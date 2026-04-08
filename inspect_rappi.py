"""Inspector: descubre dónde viven los productos en el JSON de Rappi."""
import json
from pathlib import Path

data = json.loads(Path("data/raw/rappi/brand_706_polanco.json").read_text(encoding="utf-8"))

print(f"\n=== TOP-LEVEL KEYS ===")
print(f"Store: {data.get('name')}")
print(f"Delivery price: ${data.get('delivery_price')}")
print(f"Service fee %: {data.get('percentage_service_fee')}")
print(f"ETA: {data.get('eta')} (value: {data.get('eta_value')})")

# Probables contenedores de productos
for key in ["corridors", "sections", "product_categories", "favourite_products"]:
    val = data.get(key)
    if val is None:
        print(f"\n{key}: None")
        continue
    print(f"\n=== {key} (type={type(val).__name__}, len={len(val) if hasattr(val, '__len__') else '?'}) ===")
    if isinstance(val, list) and val:
        first = val[0]
        if isinstance(first, dict):
            print(f"  First item keys: {list(first.keys())[:15]}")
            # Mira si hay productos anidados
            for sub_key in ["products", "items", "products_list"]:
                if sub_key in first:
                    sub = first[sub_key]
                    print(f"  -> {sub_key}: {len(sub) if isinstance(sub, list) else type(sub).__name__}")
                    if isinstance(sub, list) and sub:
                        print(f"     First product keys: {list(sub[0].keys())[:15]}")
                        print(f"     First product sample: name={sub[0].get('name')}, price={sub[0].get('price')}")
        else:
            print(f"  First item: {first}")

# Búsqueda directa de "big mac" en el JSON entero
import re
text = json.dumps(data, ensure_ascii=False).lower()
matches = re.findall(r'"name"\s*:\s*"([^"]*big mac[^"]*)"', text)
print(f"\n=== Búsqueda 'big mac' en todo el JSON ===")
print(f"Coincidencias: {matches[:10]}")