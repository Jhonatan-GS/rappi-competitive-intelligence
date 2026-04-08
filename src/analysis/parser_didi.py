"""Parser: convierte los JSONs parseados de DiDi a un DataFrame normalizado."""
import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
from loguru import logger

from src.config import ZONES, DIDI_STORE_PATHS

RAW_DIR = Path("data/raw/didi")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

PRODUCT_PATTERNS = {
    "big_mac": re.compile(r"^big mac(\s+tocino)?$", re.I),
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


def parse_zone(zone: dict) -> list[dict]:
    zname = zone["name"]
    if not DIDI_STORE_PATHS.get(zname):
        return []

    file = RAW_DIR / f"{slug(zname)}_parsed.json"
    if not file.exists():
        logger.warning(f"  Falta: {file}")
        return []

    parsed = json.loads(file.read_text(encoding="utf-8"))

    base = {
        "platform": "didi",
        "country": "MX",
        "city": "CDMX",
        "zone": zname,
        "zone_tier": zone["tier"],
        "lat": zone["lat"],
        "lng": zone["lng"],
        "scraped_at": datetime.now().isoformat(timespec="seconds"),
        "store_name": parsed.get("store_name"),
        "store_address": parsed.get("address"),
        "delivery_fee": None,  # DiDi público no expone fees
        "service_fee_pct": None,
        "eta_minutes": None,
    }

    rows = []
    for p in parsed.get("products", []):
        label = classify_product(p["name"])
        if not label:
            continue
        rows.append({
            **base,
            "product_label": label,
            "product_name": p["name"],
            "price": float(p["price"]),
            "real_price": float(p["price"]),
            "discount_pct": 0.0,
            "is_product_available": True,
            "corridor": None,
        })

    if not rows:
        logger.warning(f"  ⚠️  {zname}: 0 productos de referencia")
    else:
        logger.info(f"  ✅ {zname}: {len(rows)} productos extraídos")
    return rows


def parse_all() -> pd.DataFrame:
    all_rows = []
    for zone in ZONES:
        all_rows.extend(parse_zone(zone))

    if not all_rows:
        logger.error("Sin datos.")
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)
    out_csv = OUT_DIR / "didi_mcdonalds.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8")
    logger.success(f"\n💾 Guardado: {out_csv} ({len(df)} filas)")

    print("\n=== RESUMEN DIDI ===")
    print(df.groupby(["zone", "product_label"])[["price"]].first().to_string())
    return df


if __name__ == "__main__":
    parse_all()