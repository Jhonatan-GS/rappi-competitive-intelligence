"""Corre el scraper de DiDi sobre las zonas con cobertura."""
import json
import time
from loguru import logger

from src.config import ZONES, DIDI_STORE_PATHS
from src.scrapers.didi import DidiScraper


def slug(name: str) -> str:
    s = name.lower().replace(" ", "_")
    for a, b in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u")]:
        s = s.replace(a, b)
    return s


def run_all_zones(delay_seconds: float = 3.0):
    scraper = DidiScraper()
    results = []

    for i, zone in enumerate(ZONES, start=1):
        zname = zone["name"]
        path = DIDI_STORE_PATHS.get(zname)
        if not path:
            logger.warning(f"[{i}/{len(ZONES)}] {zname}: SIN MATCH (skip)")
            results.append({"zone": zname, "ok": False, "reason": "no_match"})
            continue

        logger.info(f"[{i}/{len(ZONES)}] {zname} ({zone['tier']})")
        try:
            html = scraper.fetch_store_html(path)
            scraper.save_raw_html(html, f"{slug(zname)}.html")
            parsed = scraper.parse_store(html)
            # Guarda parseado también
            (scraper.raw_dir / f"{slug(zname)}_parsed.json").write_text(
                json.dumps(parsed, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            n = len(parsed["products"])
            logger.success(f"  ✅ {parsed['store_name']} | {n} productos")
            results.append({"zone": zname, "ok": True, "store": parsed["store_name"], "n_products": n})
        except Exception as e:
            logger.error(f"  ❌ {zname}: {e}")
            results.append({"zone": zname, "ok": False, "error": str(e)})

        if i < len(ZONES):
            time.sleep(delay_seconds)

    scraper.close()
    ok = sum(1 for r in results if r["ok"])
    logger.info(f"\n=== Resumen DiDi: {ok}/{len(results)} zonas OK ===")
    return results


if __name__ == "__main__":
    run_all_zones()