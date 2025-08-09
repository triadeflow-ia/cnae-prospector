from __future__ import annotations

"""
Google Places enrichment service (Layer 1)
"""

import requests
from typing import Optional, Dict, Any
from urllib.parse import urlencode

from src.config.settings import Settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class GooglePlacesService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.api_key = settings.GOOGLE_PLACES_API_KEY
        self.enabled = bool(settings.ENABLE_PLACES and self.api_key)
        self.session = requests.Session()

    def enrich(self, razao_social: str, cidade: Optional[str], uf: Optional[str]) -> Dict[str, Any]:
        """Return website and formatted_phone_number if found"""
        if not self.enabled:
            return {}
        try:
            query_parts = [razao_social]
            if cidade:
                query_parts.append(cidade)
            if uf:
                query_parts.append(uf)
            query = " ".join(query_parts)
            params = {
                "query": query,
                "key": self.api_key,
                "language": "pt-BR",
            }
            url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?{urlencode(params)}"
            r = self.session.get(url, timeout=self.settings.REQUEST_TIMEOUT)
            if r.status_code != 200:
                logger.warning(f"Places textsearch HTTP {r.status_code}")
                return {}
            data = r.json()
            results = data.get("results") or []
            if not results:
                return {}
            place_id = results[0].get("place_id")
            if not place_id:
                return {}
            details_params = {
                "place_id": place_id,
                "fields": "formatted_phone_number,international_phone_number,website",
                "key": self.api_key,
                "language": "pt-BR",
            }
            details_url = f"https://maps.googleapis.com/maps/api/place/details/json?{urlencode(details_params)}"
            dr = self.session.get(details_url, timeout=self.settings.REQUEST_TIMEOUT)
            if dr.status_code != 200:
                return {}
            d = dr.json().get("result", {})
            phone = d.get("international_phone_number") or d.get("formatted_phone_number")
            return {
                "website": d.get("website"),
                "phone": phone,
                "fonte_places": "Google Places",
            }
        except Exception as e:
            logger.error(f"Places enrich error: {e}")
            return {}


