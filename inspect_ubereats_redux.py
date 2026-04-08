"""Encuentra dónde viven menú/precios/fees en el Redux state de Uber Eats."""
import json
from pathlib import Path

data = json.loads(Path("data/raw/ubereats/polanco_mcdonalds_redux.json").read_text(encoding="utf-8"))

print(f"=== TOP-LEVEL KEYS ({len(data)}) ===")
for k in sorted(data.keys()):
    v = data[k]
    t = type(v).__name__
    size = len(v) if hasattr(v, "__len__") else "?"
    print(f"  {k}: {t} (len={size})")

# Candidatos probables
for key in ["marketplace", "store", "stores", "storeV2", "menu", "catalog", "feed"]:
    if key in data:
        print(f"\n=== {key} ===")
        v = data[key]
        if isinstance(v, dict):
            print(f"  keys: {list(v.keys())[:30]}")

# Búsqueda recursiva: dónde aparece "Big Mac"
def find_paths(obj, target, path="", results=None, max_results=8):
    if results is None:
        results = []
    if len(results) >= max_results:
        return results
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and target.lower() in v.lower():
                results.append(f"{path}.{k} = {v[:80]}")
                if len(results) >= max_results:
                    return results
            else:
                find_paths(v, target, f"{path}.{k}", results, max_results)
    elif isinstance(obj, list):
        for i, item in enumerate(obj[:50]):
            find_paths(item, target, f"{path}[{i}]", results, max_results)
    return results

print("\n=== Paths donde aparece 'Big Mac' ===")
for p in find_paths(data, "Big Mac"):
    print(f"  {p}")

print("\n=== Paths donde aparece 'deliveryFee' o 'delivery_fee' ===")
for p in find_paths(data, "deliveryFee", max_results=5):
    print(f"  {p}")
for p in find_paths(data, "delivery_fee", max_results=5):
    print(f"  {p}")