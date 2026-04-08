"""Parser: convierte los JSON-LD de Uber Eats a un DataFrame normalizado."""
import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
from loguru import logger

from src.config import ZONES, UBEREATS_STORE_PATHS

RAW_DIR = Path("data/raw/ubereats")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

PRODUCT_PATTERNS = {
    "big_mac": re.compile(r"^big mac(\s+tocino)?$", re.I),
    "mctrio_big_mac": re.compile(r"mctr[íi]o.*big mac", re.I),
    "mcnuggets_10": re.compile(r"mcnuggets?\s*10|10\s*mcnuggets?", re.I),
    "coca_cola": re.compile(r"coca[\s-]?cola", re.I),
}

# Regex para sacar delivery fee y ETA del HTML (best-effort)
DELIVERY_FEE_RE = re.compile(r'"deliveryFee"\s*:\s*\{[^}]*"feeValue"\s*:\s*([\d.]+)', re.I)
ETA_RE = re.compile(r'"etaRange"\s*:\s*\{[^}]*"min"\s*:\s*(\d+)[^}]*"max"\s*:\s*(\d+)', re.I)


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


def extract_fees_eta_from_html(html: str) -> dict:
    """Best-effort extraction de delivery fee y ETA desde el HTML crudo."""
    out = {"delivery_fee": None, "eta_min": None, "eta_max": None}
    m = DELIVERY_FEE_RE.search(html)
    if m:
        try:
            out["delivery_fee"] = round(float(m.group(1)) / 100, 2)  # micros a MXN si aplica
        except Exception:
            pass
    m = ETA_RE.search(html)
    if m:
        out["eta_min"] = int(m.group(1))
        out["eta_max"] = int(m.group(2))
    return out


def parse_zone(zone: dict) -> list[dict]:
    zname = zone["name"]
    if not UBEREATS_STORE_PATHS.get(zname):
        return []  # sin cobertura

    menu_file = RAW_DIR / f"{slug(zname)}_menu.json"
    html_file = RAW_DIR / f"{slug(zname)}.html"
    if not menu_file.exists():
        logger.warning(f"  Falta: {menu_file}")
        return []

    menu = json.loads(menu_file.read_text(encoding="utf-8"))
    html = html_file.read_text(encoding="utf-8") if html_file.exists() else ""
    fees_eta = extract_fees_eta_from_html(html)

    base = {
        "platform": "ubereats",
        "country": "MX",
        "city": "CDMX",
        "zone": zname,
        "zone_tier": zone["tier"],
        "lat": zone["lat"],
        "lng": zone["lng"],
        "scraped_at": datetime.now().isoformat(timespec="seconds"),
        "store_name": menu.get("name"),
        "store_address": (menu.get("address") or {}).get("streetAddress") if isinstance(menu.get("address"), dict) else None,
        "delivery_fee": fees_eta["delivery_fee"],
        "service_fee_pct": None,  # Uber Eats no lo expone en JSON-LD
        "eta_minutes": fees_eta["eta_min"],
        "eta_max_minutes": fees_eta["eta_max"],
        "rating": (menu.get("aggregateRating") or {}).get("ratingValue") if isinstance(menu.get("aggregateRating"), dict) else None,
    }

    rows = []
    has_menu = menu.get("hasMenu") or {}
    sections = has_menu.get("hasMenuSection") or []

    for section in sections:
        section_name = section.get("name", "")
        items = section.get("hasMenuItem") or []
        for item in items:
            name = item.get("name") or ""
            label = classify_product(name)
            if not label:
                continue

            offer = item.get("offers") or {}
            try:
                price = float(offer.get("price") or 0)
            except (ValueError, TypeError):
                price = 0.0

            rows.append({
                **base,
                "product_label": label,
                "product_name": name,
                "price": price,
                "real_price": price,  # Uber JSON-LD trae solo el precio "list"
                "discount_pct": 0.0,
                "currency": offer.get("priceCurrency"),
                "is_product_available": True,
                "corridor": section_name,
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
    out_csv = OUT_DIR / "ubereats_mcdonalds.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8")
    logger.success(f"\n💾 Guardado: {out_csv} ({len(df)} filas)")

    print("\n=== RESUMEN UBER EATS ===")
    print(df.groupby(["zone", "product_label"])[["price"]].first().to_string())
    return df


if __name__ == "__main__":
    parse_all()