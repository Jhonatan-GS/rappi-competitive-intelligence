"""Corre el scraper de Rappi sobre todas las zonas configuradas."""
import time
from pathlib import Path

from loguru import logger

from src.config import MCDONALDS_BRAND_ID, ZONES
from src.scrapers.rappi import RappiScraper


def run_all_zones(delay_seconds: float = 2.0):
    scraper = RappiScraper()
    results = []

    for i, zone in enumerate(ZONES, start=1):
        zone_slug = zone["name"].lower().replace(" ", "_").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
        logger.info(f"[{i}/{len(ZONES)}] Zona: {zone['name']} ({zone['tier']})")
        try:
            data = scraper.get_brand_stores(MCDONALDS_BRAND_ID, zone["lat"], zone["lng"])
            scraper.save_raw(data, f"brand_706_{zone_slug}.json")
            results.append({"zone": zone["name"], "ok": True, "store": data.get("name")})
            logger.success(f"  ✅ {data.get('name')} | delivery=${data.get('delivery_price'):.2f} | eta={data.get('eta')}")
        except Exception as e:
            logger.error(f"  ❌ {zone['name']}: {e}")
            results.append({"zone": zone["name"], "ok": False, "error": str(e)})

        if i < len(ZONES):
            time.sleep(delay_seconds)  # rate limiting amable

    scraper.close()
    logger.info(f"\n=== Resumen: {sum(1 for r in results if r['ok'])}/{len(results)} zonas OK ===")
    return results


if __name__ == "__main__":
    run_all_zones()