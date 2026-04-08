"""Test rápido: 1 zona, McDonald's, dump del JSON crudo."""
from src.scrapers.rappi import RappiScraper
from src.config import MCDONALDS_BRAND_ID, ZONES

def main():
    scraper = RappiScraper()
    zone = ZONES[0]  # Polanco
    print(f"\n>>> Probando zona: {zone['name']}\n")

    # Paso 1: buscar McDonald's cerca de Polanco
    brand_data = scraper.get_brand_stores(MCDONALDS_BRAND_ID, zone["lat"], zone["lng"])
    scraper.save_raw(brand_data, f"brand_706_{zone['name'].lower().replace(' ', '_')}.json")

    # Paso 2: tomar el primer store y pedir su detalle
    stores = brand_data.get("stores") or brand_data.get("data") or []
    print(f"Stores encontrados: {len(stores)}")
    if not stores:
        print("⚠️  No se encontraron stores. Mira el JSON crudo guardado.")
        print(f"Keys del response: {list(brand_data.keys())}")
        return

    first = stores[0]
    print(f"Primer store: {first.get('name', '???')} (id={first.get('store_id') or first.get('id')})")
    store_id = first.get("store_id") or first.get("id")

    detail = scraper.get_store_detail(store_id, zone["lat"], zone["lng"])
    scraper.save_raw(detail, f"store_{store_id}_{zone['name'].lower().replace(' ', '_')}.json")
    print(f"\n✅ Detalle guardado. Keys: {list(detail.keys())[:10]}")
    scraper.close()

if __name__ == "__main__":
    main()