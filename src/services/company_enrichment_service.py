from __future__ import annotations

"""
Company enrichment via AbstractAPI Company Enrichment
"""

import requests
from typing import Optional, Dict

from src.config.settings import Settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class CompanyEnrichmentService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.enabled = bool(settings.ENABLE_COMPANY_ENRICHMENT and settings.COMPANY_ENRICHMENT_API_KEY)
        self.session = requests.Session()

    def enrich(self, domain: Optional[str]) -> Dict[str, str]:
        if not domain:
            return {}
        if not self.enabled:
            return {}
        try:
            url = (
                "https://companyenrichment.abstractapi.com/v2/?api_key="
                f"{self.settings.COMPANY_ENRICHMENT_API_KEY}&domain={domain}"
            )
            r = self.session.get(url, timeout=self.settings.REQUEST_TIMEOUT)
            if r.status_code != 200:
                return {}
            d = r.json() or {}
            res: Dict[str, str] = {}
            # Fields per AbstractAPI docs (best-effort)
            res["empresa_tamanho"] = d.get("employees_range") or ""
            res["empresa_industria"] = d.get("industry") or ""
            res["empresa_linkedin"] = (d.get("social_media") or {}).get("linkedin_url") or ""
            res["empresa_twitter"] = (d.get("social_media") or {}).get("twitter_url") or ""
            res["empresa_facebook"] = (d.get("social_media") or {}).get("facebook_url") or ""
            res["empresa_instagram"] = (d.get("social_media") or {}).get("instagram_url") or ""
            res["empresa_logo"] = d.get("logo") or ""
            return res
        except Exception as e:
            logger.error(f"Company enrichment error: {e}")
            return {}


