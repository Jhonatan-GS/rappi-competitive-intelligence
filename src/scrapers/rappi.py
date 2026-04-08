"""Scraper de Rappi México vía API reversa."""
import json
import os
import time
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

BASE_URL = "https://services.mxgrability.rappi.com"
BRAND_ENDPOINT = f"{BASE_URL}/api/restaurant-bus/store/brand/id"
STORE_ENDPOINT = f"{BASE_URL}/api/web-gateway/web/restaurants-bus/store/id"

AUTH_TOKEN = os.getenv("RAPPI_AUTH_TOKEN")
DEVICE_ID = os.getenv("RAPPI_DEVICE_ID")

DEFAULT_HEADERS = {
    "accept": "application/json",
    "accept-language": "es-MX",
    "app-version": "1.161.2",
    "app-version-name": "1.161.2",
    "authorization": f"Bearer {AUTH_TOKEN}",
    "content-type": "application/json; charset=UTF-8",
    "deviceid": DEVICE_ID,
    "needappsflyerid": "false",
    "origin": "https://www.rappi.com.mx",
    "referer": "https://www.rappi.com.mx/",
    "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Brave";v="146"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
    ),
}


class RappiScraper:
    def __init__(self, raw_dir: str = "data/raw/rappi"):
        self.client = httpx.Client(headers=DEFAULT_HEADERS, timeout=30.0)
        self.raw_dir = Path(raw_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    def get_brand_stores(self, brand_id: int, lat: float, lng: float) -> dict:
        """Lista de stores de una marca cerca de unas coordenadas."""
        payload = {
            "is_prime": False,
            "lat": lat,
            "lng": lng,
            "store_type": "restaurant",
            "prime_config": {"unlimited_shipping": False},
        }
        url = f"{BRAND_ENDPOINT}/{brand_id}"
        logger.info(f"GET brand {brand_id} @ ({lat}, {lng})")
        r = self.client.post(url, json=payload)
        r.raise_for_status()
        return r.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    def get_store_detail(self, store_id: int, lat: float, lng: float) -> dict:
        """Menú completo y precios de un store específico."""
        payload = {
            "lat": lat,
            "lng": lng,
            "store_type": "restaurant",
            "is_prime": False,
            "prime_config": {"unlimited_shipping": False},
        }
        url = f"{STORE_ENDPOINT}/{store_id}/"
        logger.info(f"GET store {store_id} @ ({lat}, {lng})")
        r = self.client.post(url, json=payload)
        r.raise_for_status()
        return r.json()

    def save_raw(self, data: dict, filename: str) -> Path:
        path = self.raw_dir / filename
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info(f"Saved {path} ({path.stat().st_size} bytes)")
        return path

    def close(self):
        self.client.close()