"""Inspecciona el HTML de DiDi para ver cómo viven los precios."""
import re
from pathlib import Path

html = Path("data/raw/didi/sample_mcdonalds.html").read_text(encoding="utf-8")

# Primeros 3 contextos donde aparece "Big Mac"
print("=== Contextos de 'Big Mac' ===")
for i, m in enumerate(re.finditer(r"Big Mac", html)):
    if i >= 3: break
    pos = m.start()
    print(f"\n--- {i+1} (pos {pos}) ---")
    print(html[max(0,pos-150):pos+250])

# Busca patrones de precio: $XXX, MXN XXX, $XXX.XX
print("\n\n=== Precios detectados ===")
prices = re.findall(r'(\$\s*\d{1,4}(?:[.,]\d{2})?|MXN\s*\$?\s*\d{1,4}(?:[.,]\d{2})?)', html)
print(f"Total: {len(prices)}")
print(f"Únicos: {sorted(set(prices))[:30]}")

# Busca tags HTML que contengan "Big Mac" para entender la estructura
print("\n=== Estructura HTML alrededor de Big Mac ===")
m = re.search(r'(<[^>]+>[^<]*Big Mac[^<]*</[^>]+>)', html)
if m:
    print(m.group(1)[:300])

# Busca el ID interno de productos (data-id, sku, etc)
print("\n=== Atributos data-* alrededor de Big Mac ===")
for m in re.finditer(r'(data-\w+="[^"]*")[^>]{0,200}Big Mac', html):
    print(m.group(1))
    if len(re.findall(r'data-\w+', html)) > 5: break

# Busca el script _R_ (que vimos antes)
print("\n=== Script id=_R_ (primeros 500 chars) ===")
m = re.search(r'<script[^>]*id="_R_"[^>]*>(.+?)</script>', html, re.DOTALL)
if m:
    print(m.group(1)[:500])

