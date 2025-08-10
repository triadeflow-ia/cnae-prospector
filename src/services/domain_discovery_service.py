from __future__ import annotations

"""
Domain discovery using SerpAPI (preferred) or Bing Web Search (fallback)
"""

import requests
from typing import Optional
from urllib.parse import urlencode
import re

from src.config.settings import Settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DomainDiscoveryService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.enabled = bool(settings.ENABLE_DOMAIN_DISCOVERY and (settings.SERPAPI_KEY or (settings.GOOGLE_CSE_API_KEY and settings.GOOGLE_CSE_CX)))
        self.session = requests.Session()

    def _is_blacklisted(self, domain: str) -> bool:
        domain = domain.lower()
        blacklist = [
            "google.com",
            "maps.google",
            "g.page",
            "facebook.com",
            "instagram.com",
            "twitter.com",
            "x.com",
            "wikipedia.org",
            "youtube.com",
            "linkedin.com",
            "ifood",
            "tripadvisor",
            "gov.br",
            ".gov.br",
            ".mg.gov.br",
            ".sp.gov.br",
        ]
        return any(b in domain for b in blacklist)

    def _score(self, company_name: str, city: Optional[str], uf: Optional[str], domain: str, title: str) -> float:
        name = company_name.lower()
        dom = domain.lower()
        ttl = (title or "").lower()
        score = 0.0
        # Basic name tokens
        tokens = [t for t in re.split(r"[^a-z0-9]+", name) if len(t) >= 4]
        if any(t in dom for t in tokens):
            score += 0.4
        if any(t in ttl for t in tokens):
            score += 0.2
        # Local signals
        if city and city.lower() in ttl:
            score += 0.1
        if uf and uf.lower() in ttl:
            score += 0.05
        # TLD preference
        if dom.endswith(".com.br"):
            score += 0.1
        # Penalties
        if self._is_blacklisted(dom):
            score -= 0.7
        # Clamp
        return max(0.0, min(1.0, score))

    def discover(self, company_name: str, city: Optional[str], uf: Optional[str]) -> Optional[dict]:
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
                    best = (None, 0.0)
                    for res in (js.get("organic_results") or [])[:5]:
                        link: str = res.get("link") or ""
                        title: str = res.get("title") or ""
                        if link:
                            domain = link.replace("https://", "").replace("http://", "").split("/")[0]
                            sc = self._score(company_name, city, uf, domain, title)
                            if sc > best[1]:
                                best = (domain, sc)
                    if best[0] and best[1] >= 0.6:
                        return {"domain": best[0], "confidence": best[1], "source": "serpapi"}
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
                    best = (None, 0.0)
                    for res in (js.get("items") or [])[:5]:
                        url = res.get("link") or ""
                        title = res.get("title") or ""
                        if url:
                            domain = url.replace("https://", "").replace("http://", "").split("/")[0]
                            sc = self._score(company_name, city, uf, domain, title)
                            if sc > best[1]:
                                best = (domain, sc)
                    if best[0] and best[1] >= 0.6:
                        return {"domain": best[0], "confidence": best[1], "source": "google_cse"}
            except Exception as e:
                logger.warning(f"Google CSE domain discovery error: {e}")
        return None


