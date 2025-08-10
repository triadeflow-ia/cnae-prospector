from __future__ import annotations

"""
Domain discovery using SerpAPI (preferred) or Bing Web Search (fallback)
"""

import requests
from typing import Optional
from urllib.parse import urlencode

from src.config.settings import Settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DomainDiscoveryService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.enabled = bool(settings.ENABLE_DOMAIN_DISCOVERY and (settings.SERPAPI_KEY or (settings.GOOGLE_CSE_API_KEY and settings.GOOGLE_CSE_CX)))
        self.session = requests.Session()

    def discover(self, company_name: str, city: Optional[str], uf: Optional[str]) -> Optional[str]:
        if not self.enabled:
            return None
        if not company_name:
            return None
        query_parts = [company_name]
        if city:
            query_parts.append(city)
        if uf:
            query_parts.append(uf)
        query = " ".join(query_parts)
        # Try SerpAPI first
        if self.settings.SERPAPI_KEY:
            try:
                params = {
                    "engine": "google",
                    "q": query,
                    "api_key": self.settings.SERPAPI_KEY,
                    "num": 3,
                    "hl": "pt-BR",
                }
                r = self.session.get("https://serpapi.com/search", params=params, timeout=self.settings.REQUEST_TIMEOUT)
                if r.status_code == 200:
                    js = r.json()
                    for res in (js.get("organic_results") or [])[:3]:
                        link: str = res.get("link") or ""
                        if link:
                            domain = link.replace("https://", "").replace("http://", "").split("/")[0]
                            if domain and not domain.endswith("google.com"):
                                return domain
            except Exception as e:
                logger.warning(f"SerpAPI domain discovery error: {e}")
        # Fallback: Google Programmable Search (CSE JSON API)
        if self.settings.GOOGLE_CSE_API_KEY and self.settings.GOOGLE_CSE_CX:
            try:
                params = {
                    "key": self.settings.GOOGLE_CSE_API_KEY,
                    "cx": self.settings.GOOGLE_CSE_CX,
                    "q": query,
                    "num": 3,
                    "hl": "pt-BR",
                }
                r = self.session.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=self.settings.REQUEST_TIMEOUT)
                if r.status_code == 200:
                    js = r.json() or {}
                    for res in (js.get("items") or []):
                        url = res.get("link") or ""
                        if url:
                            domain = url.replace("https://", "").replace("http://", "").split("/")[0]
                            if domain:
                                return domain
            except Exception as e:
                logger.warning(f"Google CSE domain discovery error: {e}")
        return None


