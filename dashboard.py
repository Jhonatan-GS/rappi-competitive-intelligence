"""Dashboard Streamlit - Competitive Intelligence Rappi vs Uber Eats vs DiDi."""
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Competitive Intelligence — Rappi MX",
    page_icon="🍔",
    layout="wide",
)

PROCESSED = Path("data/processed")

# ============ DATA LOADING ============
@st.cache_data
def load_data():
    master = pd.read_csv(PROCESSED / "master.csv")
    master["price"] = pd.to_numeric(master["price"], errors="coerce")
    insights_path = PROCESSED / "insights.json"
    insights = json.loads(insights_path.read_text(encoding="utf-8")) if insights_path.exists() else {"insights": []}
    return master, insights

master, insights = load_data()

PLATFORM_COLORS = {
    "rappi": "#FF441F",
    "ubereats": "#06C167",
    "didi": "#FF7A1F",
}

PRODUCT_LABELS = {
    "big_mac": "Big Mac Tocino",
    "mctrio_big_mac": "McTrío Big Mac",
    "mcnuggets_10": "McNuggets 10pz",
    "coca_cola": "Coca-Cola",
}

# ============ HEADER ============
st.title("🍔 Competitive Intelligence — Rappi vs Uber Eats vs DiDi Food")
st.caption("McDonald's en CDMX · 8 zonas · 3 plataformas · scraping reproducible")

# ============ KPIs ============
col1, col2, col3, col4 = st.columns(4)
col1.metric("Plataformas", master["platform"].nunique())
col2.metric("Zonas cubiertas", master["zone"].nunique())
col3.metric("Datapoints totales", len(master))
col4.metric("Productos comparables", master["product_label"].nunique())

st.divider()

# ============ SECCIÓN 1: PRICING POR ZONA ============
st.header("1. Posicionamiento de precios por zona")

product_choice = st.selectbox(
    "Producto a comparar",
    options=list(PRODUCT_LABELS.keys()),
    format_func=lambda x: PRODUCT_LABELS[x],
)

prod_df = master[master["product_label"] == product_choice].copy()
pivot = prod_df.pivot_table(index="zone", columns="platform", values="price", aggfunc="first")

# Bar chart agrupado
fig1 = go.Figure()
for platform in pivot.columns:
    fig1.add_trace(go.Bar(
        name=platform.upper(),
        x=pivot.index,
        y=pivot[platform],
        marker_color=PLATFORM_COLORS.get(platform, "#888"),
        text=pivot[platform].apply(lambda v: f"${v:.0f}" if pd.notna(v) else ""),
        textposition="outside",
    ))
fig1.update_layout(
    title=f"{PRODUCT_LABELS[product_choice]} — precio por zona y plataforma (MXN)",
    barmode="group",
    height=450,
    yaxis_title="Precio (MXN)",
    xaxis_title="",
    legend_title="Plataforma",
)
st.plotly_chart(fig1, use_container_width=True)

# Tabla de la diferencia
st.subheader("Diferencia vs precio mínimo (por zona)")
pivot_diff = pivot.copy()
pivot_diff["min"] = pivot.min(axis=1)
for col in pivot.columns:
    pivot_diff[f"{col}_vs_min"] = pivot[col] - pivot_diff["min"]
display_cols = [col for col in pivot.columns] + [f"{col}_vs_min" for col in pivot.columns]
st.dataframe(pivot_diff[display_cols].round(0), use_container_width=True)

st.divider()

# ============ SECCIÓN 2: HEATMAP DE PRECIOS ============
st.header("2. Mapa de calor de precios — Big Mac Tocino")

big_mac = master[master["product_label"] == "big_mac"].pivot_table(
    index="zone", columns="platform", values="price", aggfunc="first"
)
fig2 = px.imshow(
    big_mac.values,
    labels=dict(x="Plataforma", y="Zona", color="Precio MXN"),
    x=[p.upper() for p in big_mac.columns],
    y=big_mac.index,
    text_auto=".0f",
    color_continuous_scale="RdYlGn_r",
    aspect="auto",
)
fig2.update_layout(height=450, title="Precio Big Mac por zona × plataforma")
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ============ SECCIÓN 3: ETA Y DELIVERY FEE (RAPPI) ============
st.header("3. Operacional — ETA y Delivery Fee (Rappi)")

rappi_ops = master[master["platform"] == "rappi"].groupby("zone").agg(
    delivery_fee=("delivery_fee", "first"),
    eta_minutes=("eta_minutes", "first"),
    zone_tier=("zone_tier", "first"),
).reset_index().sort_values("eta_minutes")

col_a, col_b = st.columns(2)
with col_a:
    fig3 = px.bar(
        rappi_ops,
        x="zone",
        y="eta_minutes",
        color="zone_tier",
        title="ETA Rappi (minutos) por zona",
        labels={"eta_minutes": "ETA (min)", "zone": ""},
        text="eta_minutes",
    )
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)

with col_b:
    fig4 = px.bar(
        rappi_ops,
        x="zone",
        y="delivery_fee",
        title="Delivery Fee Rappi (MXN) por zona",
        labels={"delivery_fee": "Delivery (MXN)", "zone": ""},
        text="delivery_fee",
    )
    fig4.update_traces(marker_color="#FF441F")
    fig4.update_layout(height=400)
    st.plotly_chart(fig4, use_container_width=True)

st.info("⚠️ Uber Eats y DiDi no exponen delivery fee ni ETA en sus endpoints públicos sin login. Documentado como limitación.")

st.divider()

# ============ SECCIÓN 4: TOP 5 INSIGHTS ============
st.header("4. Top 5 Insights Accionables")
st.caption("Generados con LLM (Llama 3.3 70B vía Groq) sobre el dataset completo")

for ins in insights.get("insights", []):
    priority_color = {"alta": "🔴", "media": "🟡", "baja": "🟢"}.get(ins.get("priority", "").lower(), "⚪")
    with st.expander(f"{priority_color} #{ins['rank']} — {ins['title']}", expanded=(ins["rank"] <= 2)):
        st.markdown(f"**Finding:** {ins['finding']}")
        st.markdown(f"**Impact:** {ins['impact']}")
        st.markdown(f"**Recommendation:** {ins['recommendation']}")

st.divider()

# ============ SECCIÓN 5: DATASET RAW ============
st.header("5. Dataset completo")
st.dataframe(master, use_container_width=True, height=400)

csv = master.to_csv(index=False).encode("utf-8")
st.download_button("📥 Descargar master.csv", csv, "master.csv", "text/csv")