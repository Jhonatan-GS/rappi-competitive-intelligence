"""Parser: convierte los JSONs crudos de Rappi a un DataFrame normalizado."""
import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
from loguru import logger

from src.config import ZONES

RAW_DIR = Path("data/raw/rappi")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Patrones para identificar productos de referencia (case-insensitive)
PRODUCT_PATTERNS = {
    "big_mac": re.compile(r"^big mac(\s+tocino)?$", re.I),  # solo el sandwich, no combos
    "mctrio_big_mac": re.compile(r"mctr[íi]o.*big mac", re.I),
    "mcnuggets_10": re.compile(r"mcnuggets?\s*10|10\s*mcnuggets?", re.I),
    "coca_cola": re.compile(r"coca[\s-]?cola", re.I),
}


def slug(name: str) -> str:
    s = name.lower().replace(" ", "_")
    for a, b in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u")]:
        s = s.replace(a, b)
    return s


def classify_product(name: str) -> str | None:
    for label, pat in PRODUCT_PATTERNS.items():
        if pat.search(name):
            return label
    return None


def parse_zone_file(zone: dict) -> list[dict]:
    """Lee un JSON de zona y extrae filas planas (una por producto de referencia)."""
    file = RAW_DIR / f"brand_706_{slug(zone['name'])}.json"
    if not file.exists():
        logger.warning(f"  Falta archivo: {file}")
        return []

    data = json.loads(file.read_text(encoding="utf-8"))
    rows = []

    base = {
        "platform": "rappi",
        "country": "MX",
        "city": "CDMX",
        "zone": zone["name"],
        "zone_tier": zone["tier"],
        "lat": zone["lat"],
        "lng": zone["lng"],
        "scraped_at": datetime.now().isoformat(timespec="seconds"),
        "store_id": data.get("store_id"),
        "store_name": data.get("name"),
        "store_address": data.get("address"),
        "delivery_fee": round(float(data.get("delivery_price") or 0), 2),
        "service_fee_pct": float(data.get("percentage_service_fee") or 0),
        "eta_text": data.get("eta"),
        "eta_minutes": data.get("eta_value"),
        "is_available": data.get("is_currently_available"),
        "rating": data.get("rating"),
    }

    # Recorre corridors → products
    for corridor in data.get("corridors", []) or []:
        for product in corridor.get("products", []) or []:
            name = product.get("name") or ""
            label = classify_product(name)
            if not label:
                continue

            rows.append({
                **base,
                "product_label": label,
                "product_name": name,
                "product_id": product.get("id"),
                "price": float(product.get("price") or 0),
                "real_price": float(product.get("real_price") or 0),
                "discount_pct": round(
                    100 * (1 - (product.get("price") or 0) / (product.get("real_price") or 1))
                    if product.get("real_price") else 0,
                    1,
                ),
                "is_product_available": product.get("is_available"),
                "corridor": corridor.get("name"),
            })

    if not rows:
        logger.warning(f"  ⚠️  {zone['name']}: 0 productos de referencia encontrados")
    else:
        logger.info(f"  ✅ {zone['name']}: {len(rows)} productos extraídos")
    return rows


def parse_all() -> pd.DataFrame:
    all_rows = []
    for zone in ZONES:
        all_rows.extend(parse_zone_file(zone))

    if not all_rows:
        logger.error("Sin datos. Corre primero el scraper.")
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)
    out_csv = OUT_DIR / "rappi_mcdonalds.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8")
    logger.success(f"\n💾 Guardado: {out_csv} ({len(df)} filas)")

    # Resumen rápido
    print("\n=== RESUMEN ===")
    print(df.groupby(["zone", "product_label"])[["price", "real_price", "delivery_fee"]].first().to_string())
    return df


if __name__ == "__main__":
    parse_all()