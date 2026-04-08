"""Unifica los 3 CSVs (Rappi, Uber Eats, DiDi) en un dataset master."""
from pathlib import Path
import pandas as pd
from loguru import logger

PROCESSED = Path("data/processed")
OUT = PROCESSED / "master.csv"

CANONICAL_COLS = [
    "platform", "country", "city", "zone", "zone_tier", "lat", "lng",
    "scraped_at", "store_name", "store_address",
    "product_label", "product_name", "price", "real_price", "discount_pct",
    "delivery_fee", "service_fee_pct", "eta_minutes",
    "is_product_available", "corridor",
]


def load_and_normalize(path: Path) -> pd.DataFrame:
    if not path.exists():
        logger.warning(f"Falta: {path}")
        return pd.DataFrame()
    df = pd.read_csv(path)
    # Asegurar columnas faltantes
    for col in CANONICAL_COLS:
        if col not in df.columns:
            df[col] = None
    return df[CANONICAL_COLS]


def main():
    parts = []
    for name in ["rappi_mcdonalds.csv", "ubereats_mcdonalds.csv", "didi_mcdonalds.csv"]:
        df = load_and_normalize(PROCESSED / name)
        logger.info(f"  {name}: {len(df)} filas")
        parts.append(df)

    master = pd.concat(parts, ignore_index=True)
    master["price"] = pd.to_numeric(master["price"], errors="coerce")
    master["real_price"] = pd.to_numeric(master["real_price"], errors="coerce")
    master["discount_pct"] = pd.to_numeric(master["discount_pct"], errors="coerce").fillna(0)
    master["delivery_fee"] = pd.to_numeric(master["delivery_fee"], errors="coerce")
    master["eta_minutes"] = pd.to_numeric(master["eta_minutes"], errors="coerce")

    master.to_csv(OUT, index=False, encoding="utf-8")
    master.to_json(PROCESSED / "master.json", orient="records", force_ascii=False, indent=2)
    logger.success(f"\n💾 Master: {OUT} ({len(master)} filas)")

    print("\n=== COBERTURA ===")
    print(master.groupby(["platform", "zone"]).size().unstack(fill_value=0))

    print("\n=== PRECIO BIG MAC POR ZONA Y PLATAFORMA ===")
    big_mac = master[master["product_label"] == "big_mac"]
    pivot = big_mac.pivot_table(
        index="zone", columns="platform", values="price", aggfunc="first"
    )
    print(pivot.to_string())


if __name__ == "__main__":
    main()