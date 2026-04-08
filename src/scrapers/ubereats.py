"""Scraper de Uber Eats México vía HTML embebido (__REDUX_STATE__)."""
import json
import re
from pathlib import Path
from typing import Optional
from typing import Optional, List

import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

BASE_URL = "https://www.ubereats.com"

DEFAULT_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "es-MX,es;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Brave";v="146"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
    ),
}

# Regex para capturar el blob JSON de Redux. Uber lo mete así:
# window.__REDUX_STATE__ = JSON.parse("...escaped...")
# o:  window.__REDUX_STATE__ = {...}
REDUX_PATTERN = re.compile(
    r'<script[^>]*id="__REDUX_STATE__"[^>]*>\s*(\{.+?\})\s*</script>',
    re.DOTALL,
)


class UberEatsScraper:
    def __init__(self, raw_dir: str = "data/raw/ubereats"):
        self.client = httpx.Client(
            headers=DEFAULT_HEADERS,
            timeout=30.0,
            follow_redirects=True,
        )
        self.raw_dir = Path(raw_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    def fetch_store_html(self, store_path: str) -> str:
        """Fetcha el HTML de un store. store_path = '/mx/store/<slug>/<uuid>'."""
        url = f"{BASE_URL}{store_path}"
        logger.info(f"GET {url}")
        r = self.client.get(url)
        r.raise_for_status()
        return r.text

    def extract_redux_state(self, html: str) -> Optional[dict]:
        """Extrae el JSON de Redux del <script id='__REDUX_STATE__'>."""
        m = REDUX_PATTERN.search(html)
        if not m:
            return None
        raw = m.group(1)
        # El JSON viene con escapes unicode tipo \u0022 en lugar de "
        try:
            decoded = raw.encode("utf-8").decode("unicode_escape")
            return json.loads(decoded)
        except Exception as e:
            logger.error(f"Decode error: {e}")
            return None

    def save_raw_html(self, html: str, filename: str) -> Path:
        path = self.raw_dir / filename
        path.write_text(html, encoding="utf-8")
        logger.info(f"Saved HTML {path} ({len(html)} chars)")
        return path

    def save_redux(self, data: dict, filename: str) -> Path:
        path = self.raw_dir / filename
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info(f"Saved Redux {path}")
        return path
    
    def extract_jsonld_menu(self, html: str) -> Optional[dict]:
        """Extrae el bloque JSON-LD que contiene el menú del restaurante."""
        # Encuentra todos los <script type="application/ld+json">
        pattern = re.compile(
            r'<script[^>]*type="application/ld\+json"[^>]*>(.+?)</script>',
            re.DOTALL,
        )
        for m in pattern.finditer(html):
            raw = m.group(1).strip()
            try:
                obj = json.loads(raw)
            except Exception:
                continue
            # Puede ser un dict o una lista
            candidates = obj if isinstance(obj, list) else [obj]
            for c in candidates:
                if not isinstance(c, dict):
                    continue
                t = c.get("@type")
                if t in ("Restaurant", "FoodEstablishment") or "hasMenu" in c or "menu" in c:
                    return c
        return None

    def close(self):
        self.client.close()