from __future__ import annotations

"""
Email pattern discovery via Hunter.io
"""

import requests
from typing import Optional, Dict

from src.config.settings import Settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class EmailPatternService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.enabled = bool(settings.ENABLE_EMAIL_PATTERN and settings.HUNTER_API_KEY)
        self.session = requests.Session()

    def enrich(self, domain: Optional[str]) -> Dict[str, str]:
        if not self.enabled or not domain:
            return {}
        try:
            url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={self.settings.HUNTER_API_KEY}&limit=10"
            r = self.session.get(url, timeout=self.settings.REQUEST_TIMEOUT)
            if r.status_code != 200:
                return {}
            data = r.json().get("data", {})
            pattern = (data.get("pattern") or "").replace("{first}", "nome").replace("{last}", "sobrenome").replace("{f}", "n").replace("{l}", "s")
            emails = [e.get("value") for e in (data.get("emails") or []) if e.get("value")]
            confs = [e.get("confidence") for e in (data.get("emails") or []) if e.get("confidence") is not None]
            avg_conf = round(sum(confs) / len(confs), 1) if confs else None
            res: Dict[str, str] = {}
            if pattern:
                res["email_padrao"] = f"{pattern}@{domain}" if "@" not in pattern else pattern
            if emails:
                res["emails_dominio"] = ", ".join(emails)
            if avg_conf is not None:
                res["emails_confianza"] = str(avg_conf)
            return res
        except Exception as e:
            logger.error(f"Hunter pattern error: {e}")
            return {}


