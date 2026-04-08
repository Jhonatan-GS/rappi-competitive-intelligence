"""Test del parser de DiDi sobre el HTML ya descargado de Portal Centro."""
from pathlib import Path
from src.scrapers.didi import DidiScraper

html = Path("data/raw/didi/sample_mcdonalds.html").read_text(encoding="utf-8")
scraper = DidiScraper()
result = scraper.parse_store(html)

print(f"Store: {result['store_name']}")
print(f"Address: {result['address']}")
print(f"\nProductos encontrados: {len(result['products'])}")
print("\nPrimeros 15 productos:")
for p in result["products"][:15]:
    print(f"  {p['name']:50s} ${p['price']:>7.2f}")

# Filtra Big Mac específicamente
print("\n=== Productos con 'Big Mac' ===")
for p in result["products"]:
    if "big mac" in p["name"].lower():
        print(f"  {p['name']:50s} ${p['price']:>7.2f}")