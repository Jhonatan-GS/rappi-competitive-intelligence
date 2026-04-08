"""Genera los Top 5 insights accionables usando un LLM sobre el dataset master."""
import json
from pathlib import Path

import pandas as pd
from loguru import logger

from src.llm_provider import generate

PROCESSED = Path("data/processed")
OUT = PROCESSED / "insights.json"


SYSTEM_PROMPT = """Eres un analista senior de Competitive Intelligence reportando al VP de Pricing de Rappi.
Rappi es TU cliente. Tu trabajo es proteger y crecer su posición competitiva, NO ayudar a la competencia.

REGLAS DE NEGOCIO CRÍTICAS:
1. Cuando Rappi tiene precio MÁS BAJO que la competencia, eso es una VENTAJA. NUNCA recomiendes subir precios para "igualar" — eso borra ventaja competitiva. La recomendación correcta es: mantener el precio bajo, amplificarlo en marketing, capturar share.
2. Cuando un competidor tiene precio MÁS BAJO que Rappi, evalúa si es subsidio temporal de penetración (probable amenaza) o estructural. Recomienda match defensivo solo en zonas estratégicas.
3. Cuando Rappi tiene COBERTURA EXCLUSIVA en una zona donde competencia no llega, eso es una ventaja estructural — recomienda explotarla con marketing local, no neutralizarla.
4. Cuando Rappi tiene precio IGUAL a competencia en la mayoría de zonas, busca dimensiones de diferenciación: ETA, delivery fee, cobertura, promociones.
5. Diferencia entre "promo dinámica de competencia" (reaccionar) vs "ventaja estructural de Rappi" (defender y amplificar).

FORMATO de cada insight:
- finding: hallazgo concreto con números (qué dicen los datos)
- impact: por qué importa para Rappi (riesgo u oportunidad)
- recommendation: acción ESPECÍFICA, accionable, que CRECE o DEFIENDE la posición de Rappi (nunca que la regala)

Sé directo, basado en datos, sin generalidades. Habla como reportarías al VP de Pricing en un Slack."""

def build_data_summary(master: pd.DataFrame) -> str:
    """Resume el dataset en texto compacto que cabe en el prompt."""
    big_mac = master[master["product_label"] == "big_mac"].pivot_table(
        index="zone", columns="platform", values="price", aggfunc="first"
    )
    mctrio = master[master["product_label"] == "mctrio_big_mac"].pivot_table(
        index="zone", columns="platform", values="price", aggfunc="first"
    )
    nuggets = master[master["product_label"] == "mcnuggets_10"].pivot_table(
        index="zone", columns="platform", values="price", aggfunc="first"
    )
    coca = master[master["product_label"] == "coca_cola"].pivot_table(
        index="zone", columns="platform", values="price", aggfunc="first"
    )

    rappi_only = master[master["platform"] == "rappi"]
    fees = rappi_only.groupby("zone")[["delivery_fee", "eta_minutes"]].first()

    return f"""DATASET: McDonald's en 8 zonas de CDMX (Polanco, Santa Fe, Roma Norte, Del Valle, Coyoacán, Centro Histórico, Iztapalapa, Ecatepec).
Plataformas: Rappi, Uber Eats, DiDi Food.

BIG MAC TOCINO (precio MXN):
{big_mac.to_string()}

MCTRÍO BIG MAC (precio MXN):
{mctrio.to_string()}

MCNUGGETS 10 PIEZAS (precio MXN):
{nuggets.to_string()}

COCA-COLA 600ML (precio MXN):
{coca.to_string()}

DELIVERY FEE Y ETA (Rappi - únicos datos disponibles):
{fees.to_string()}

NOTAS CRÍTICAS DEL DATASET:
- Rappi tiene service_fee = 0% en McDonald's MX (no cobra comisión visible).
- Uber Eats no expone delivery_fee ni service_fee en datos públicos sin login.
- DiDi Food no expone fees en su versión pública.
- Rappi delivery fee es uniforme: $9.90 MXN en TODAS las 8 zonas.
- Cobertura: Rappi = 8/8 zonas, DiDi = 8/8, Uber Eats = 8/8.
"""


def main():
    master = pd.read_csv(PROCESSED / "master.csv")
    summary = build_data_summary(master)

    prompt = f"""{summary}

GENERA EXACTAMENTE 5 INSIGHTS ACCIONABLES priorizados por impacto de negocio.

Devuelve SOLO un JSON válido con esta estructura, sin texto antes ni después:
{{
  "insights": [
    {{
      "rank": 1,
      "title": "Título corto del insight",
      "finding": "Hallazgo concreto con datos numéricos",
      "impact": "Por qué importa para Rappi",
      "recommendation": "Acción específica recomendada",
      "priority": "alta|media|baja"
    }},
    ...
  ]
}}"""

    logger.info("Generando insights con LLM...")
    raw = generate(prompt, system=SYSTEM_PROMPT, temperature=0.4)

    # Limpia posibles fences
    cleaned = raw.strip().replace("```json", "").replace("```", "").strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        logger.error(f"Raw output:\n{raw}")
        return

    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.success(f"💾 Insights guardados: {OUT}")

    print("\n=== TOP 5 INSIGHTS ===\n")
    for ins in data["insights"]:
        print(f"#{ins['rank']} [{ins['priority'].upper()}] {ins['title']}")
        print(f"  Finding: {ins['finding']}")
        print(f"  Impact: {ins['impact']}")
        print(f"  Recommendation: {ins['recommendation']}")
        print()


if __name__ == "__main__":
    main()