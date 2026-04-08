"""Test: fetcha el McDonald's Plaza Galerías de Uber Eats y extrae menú JSON-LD."""
import json
from src.scrapers.ubereats import UberEatsScraper

STORE_PATH = "/mx/store/mcdonalds-plaza-galerias/oIEI4FlNTJ6ioOOpC-lxsQ"

def main():
    scraper = UberEatsScraper()
    html = scraper.fetch_store_html(STORE_PATH)
    scraper.save_raw_html(html, "polanco_mcdonalds.html")

    print(f"\nHTML size: {len(html):,} chars")

    menu = scraper.extract_jsonld_menu(html)
    if menu is None:
        print("❌ No se encontró JSON-LD de menú")
        scraper.close()
        return

    scraper.save_redux(menu, "polanco_mcdonalds_menu.json")
    print(f"\n✅ Menú JSON-LD extraído.")
    print(f"  Restaurante: {menu.get('name')}")
    print(f"  Tipo: {menu.get('@type')}")
    print(f"  Top-level keys: {list(menu.keys())}")

    # Busca productos
    has_menu = menu.get("hasMenu") or menu.get("menu")
    if has_menu:
        print(f"\n  hasMenu type: {type(has_menu).__name__}")
        if isinstance(has_menu, dict):
            sections = has_menu.get("hasMenuSection", [])
            print(f"  Secciones: {len(sections) if isinstance(sections, list) else 'N/A'}")
            if isinstance(sections, list) and sections:
                first = sections[0]
                items = first.get("hasMenuItem", [])
                print(f"  Primera sección: '{first.get('name')}' con {len(items)} items")
                if items:
                    sample = items[0]
                    print(f"  Sample item: {json.dumps(sample, ensure_ascii=False)[:200]}")

    # Cuenta cuántos "Big Mac" aparecen en el menú
    text = json.dumps(menu, ensure_ascii=False)
    print(f"\n  'Big Mac' menciones en JSON-LD: {text.count('Big Mac')}")

    scraper.close()

if __name__ == "__main__":
    main()