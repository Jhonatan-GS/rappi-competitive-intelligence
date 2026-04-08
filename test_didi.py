"""Sondeo: qué trae la página pública de un restaurante DiDi sin login."""
import httpx
import re
from pathlib import Path

URL = "https://web.didiglobal.com/mx/food/ciudad-de-mexico-cdmx/mcdonalds-portal-centro/5764607547986935864/"

HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "es-MX,es;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
}

r = httpx.get(URL, headers=HEADERS, timeout=30, follow_redirects=True)
print(f"Status: {r.status_code}")
print(f"Final URL: {r.url}")
print(f"HTML size: {len(r.text):,}")

Path("data/raw/didi").mkdir(parents=True, exist_ok=True)
Path("data/raw/didi/sample_mcdonalds.html").write_text(r.text, encoding="utf-8")

html = r.text
print(f"\nContiene 'Big Mac': {'Big Mac' in html} ({html.count('Big Mac')} veces)")
print(f"Contiene 'McDonald': {'McDonald' in html}")
print(f"Contiene 'price': {html.lower().count(chr(34) + 'price' + chr(34))}")
print(f"Contiene '__NEXT_DATA__': {'__NEXT_DATA__' in html}")
print(f"Contiene 'application/ld+json': {'application/ld+json' in html}")
print(f"Contiene 'window.__': {'window.__' in html}")

# Lista <script id=...>
print("\n=== <script> tags con id ===")
for m in re.finditer(r'<script[^>]*id="([^"]+)"', html):
    print(f"  id={m.group(1)}")

# Si hay JSON-LD, mira qué tipos contiene
ld_pat = re.compile(r'<script[^>]*type="application/ld\+json"[^>]*>(.+?)</script>', re.DOTALL)
print(f"\n=== JSON-LD blocks: {len(ld_pat.findall(html))} ===")
for i, block in enumerate(ld_pat.findall(html)[:3]):
    print(f"--- block {i+1} (primeros 300 chars) ---")
    print(block.strip()[:300])