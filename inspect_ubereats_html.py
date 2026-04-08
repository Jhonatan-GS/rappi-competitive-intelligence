"""Encuentra dónde vive 'Big Mac' en el HTML de Uber Eats."""
import re
from pathlib import Path

html = Path("data/raw/ubereats/polanco_mcdonalds.html").read_text(encoding="utf-8")

# Todas las posiciones de "Big Mac"
positions = [m.start() for m in re.finditer(r"Big Mac", html)]
print(f"Total ocurrencias: {len(positions)}\n")

# Mira los primeros 3 contextos
for i, pos in enumerate(positions[:3]):
    print(f"--- Ocurrencia {i+1} (pos {pos}) ---")
    print(html[max(0,pos-80):pos+120])
    print()

# Lista todos los <script id="..."> que hay
print("\n=== <script> tags con id ===")
for m in re.finditer(r'<script[^>]*id="([^"]+)"[^>]*>', html):
    print(f"  id={m.group(1)} @ pos {m.start()}")

# ¿Aparece __NEXT_DATA__?
print(f"\n__NEXT_DATA__ presente: {'__NEXT_DATA__' in html}")
print(f"application/ld+json presente: {'application/ld+json' in html}")