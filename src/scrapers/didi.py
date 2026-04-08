"""Scraper de DiDi Food MX vía HTML público server-side."""
import json
import re
from pathlib import Path
from typing import Optional

import httpx
from bs4 import BeautifulSoup
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

BASE_URL = "https://web.didiglobal.com"

DEFAULT_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "es-MX,es;q=0.9,en;q=0.8",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
    ),
}

PRICE_RE = re.compile(r"MX\$\s*([\d,]+\.\d{2})")


class DidiScraper:
    def __init__(self, raw_dir: str = "data/raw/didi"):
        self.client = httpx.Client(
            headers=DEFAULT_HEADERS,
            timeout=30.0,
            follow_redirects=True,
        )
        self.raw_dir = Path(raw_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    def fetch_store_html(self, store_path: str) -> str:
        """store_path = '/mx/food/ciudad-de-mexico-cdmx/<slug>/<id>/'"""
        url = f"{BASE_URL}{store_path}" if store_path.startswith("/") else store_path
        logger.info(f"GET {url}")
        r = self.client.get(url)
        r.raise_for_status()
        return r.text

    def save_raw_html(self, html: str, filename: str) -> Path:
        path = self.raw_dir / filename
        path.write_text(html, encoding="utf-8")
        logger.info(f"Saved {path} ({len(html)} chars)")
        return path

    def parse_store(self, html: str) -> dict:
        """Extrae info del store + lista de productos del HTML."""
        soup = BeautifulSoup(html, "html.parser")

        # Nombre del restaurante (h2 dentro del bloque hidden id='S:0' o h1 visible)
        store_name = None
        h2 = soup.find("h2", class_=re.compile(r"orange"))
        if h2:
            store_name = h2.get_text(strip=True)

        # Dirección: aparece en el párrafo de descripción
        address = None
        desc_p = soup.find("p", string=re.compile(r"Ubicado", re.I))
        if desc_p:
            address = desc_p.get_text(strip=True)[:200]

        # Productos: cada producto es un div con un h4 + un span de precio
        products = []
        for h4 in soup.find_all("h4", class_=re.compile(r"font-semibold")):
            name = h4.get_text(strip=True)
            # Sube al contenedor del producto y busca el span de precio
            container = h4.find_parent("div")
            price_span = None
            if container:
                price_span = container.find("span", class_=re.compile(r"green"))
            if not price_span:
                continue
            price_text = price_span.get_text(strip=True)
            m = PRICE_RE.search(price_text)
            if not m:
                continue
            price = float(m.group(1).replace(",", ""))

            # Descripción opcional
            desc_tag = container.find("p", class_=re.compile(r"gray-600"))
            description = desc_tag.get_text(strip=True) if desc_tag else None

            products.append({
                "name": name,
                "price": price,
                "description": description,
            })

        return {
            "store_name": store_name,
            "address": address,
            "products": products,
        }

    def close(self):
        self.client.close()