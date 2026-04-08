"""Encuentra cómo está embebido __REDUX_STATE__ en el HTML."""
from pathlib import Path

html = Path("data/raw/ubereats/polanco_mcdonalds.html").read_text(encoding="utf-8")

idx = html.find("__REDUX_STATE__")
print(f"Posición: {idx}")
print(f"\n--- 300 chars desde __REDUX_STATE__ ---")
print(html[idx:idx+300])
print(f"\n--- 100 chars antes ---")
print(html[max(0,idx-100):idx])