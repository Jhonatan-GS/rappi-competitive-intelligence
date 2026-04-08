"""Corre el scraper de Uber Eats sobre todas las zonas configuradas."""
import time
from loguru import logger

from src.config import ZONES, UBEREATS_STORE_PATHS
from src.scrapers.ubereats import UberEatsScraper


def slug(name: str) -> str:
    s = name.lower().replace(" ", "_")
    for a, b in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u")]:
        s = s.replace(a, b)
    return s


def run_all_zones(delay_seconds: float = 3.0):
    scraper = UberEatsScraper()
    results = []

    for i, zone in enumerate(ZONES, start=1):
        zname = zone["name"]
        path = UBEREATS_STORE_PATHS.get(zname)
        if not path:
            logger.warning(f"[{i}/{len(ZONES)}] {zname}: SIN COBERTURA (skip)")
            results.append({"zone": zname, "ok": False, "reason": "no_coverage"})
            continue

        logger.info(f"[{i}/{len(ZONES)}] {zname} ({zone['tier']})")
        try:
            html = scraper.fetch_store_html(path)
            scraper.save_raw_html(html, f"{slug(zname)}.html")

            menu = scraper.extract_jsonld_menu(html)
            if menu is None:
                raise ValueError("JSON-LD no encontrado en HTML")

            scraper.save_redux(menu, f"{slug(zname)}_menu.json")
            logger.success(f"  ✅ {menu.get('name')}")
            results.append({"zone": zname, "ok": True, "store": menu.get("name")})
        except Exception as e:
            logger.error(f"  ❌ {zname}: {e}")
            results.append({"zone": zname, "ok": False, "error": str(e)})

        if i < len(ZONES):
            time.sleep(delay_seconds)

    scraper.close()
    ok = sum(1 for r in results if r["ok"])
    logger.info(f"\n=== Resumen Uber Eats: {ok}/{len(results)} zonas OK ===")
    return results


if __name__ == "__main__":
    run_all_zones()