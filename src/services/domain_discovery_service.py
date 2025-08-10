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
        self.enabled = bool(settings.ENABLE_DOMAIN_DISCOVERY and (settings.SERPAPI_KEY or settings.BING_API_KEY))
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
        # Fallback: Bing
        if self.settings.BING_API_KEY:
            try:
                headers = {"Ocp-Apim-Subscription-Key": self.settings.BING_API_KEY}
                params = {"q": query, "mkt": "pt-BR", "count": 3}
                r = self.session.get("https://api.bing.microsoft.com/v7.0/search", headers=headers, params=params, timeout=self.settings.REQUEST_TIMEOUT)
                if r.status_code == 200:
                    js = r.json()
                    for res in (js.get("webPages", {}).get("value", [])):
                        url = res.get("url") or ""
                        if url:
                            domain = url.replace("https://", "").replace("http://", "").split("/")[0]
                            if domain and not domain.endswith("bing.com"):
                                return domain
            except Exception as e:
                logger.warning(f"Bing domain discovery error: {e}")
        return None


