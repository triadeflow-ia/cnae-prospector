from __future__ import annotations

"""
Email validation service (AbstractAPI)
"""

import requests
from typing import Optional, Dict

from src.config.settings import Settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class EmailValidationService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.enabled = bool(settings.ENABLE_EMAIL_VALIDATION and settings.EMAIL_VALIDATION_API_KEY)
        self.session = requests.Session()

    def validate(self, email: Optional[str]) -> Dict[str, str]:
        if not email:
            return {}
        # Simple offline format check
        if "@" not in email:
            return {"email_validacao": "inválido (formato)"}

        if not self.enabled:
            return {"email_validacao": "offline"}

        try:
            url = (
                "https://emailvalidation.abstractapi.com/v1/?api_key="
                f"{self.settings.EMAIL_VALIDATION_API_KEY}&email={email}"
            )
            r = self.session.get(url, timeout=self.settings.REQUEST_TIMEOUT)
            if r.status_code != 200:
                return {"email_validacao": f"erro http {r.status_code}"}
            data = r.json()
            # deliverability: DELIVERABLE / UNDELIVERABLE / RISKY / UNKNOWN
            deliver = (data.get("deliverability") or "").lower()
            is_valid_format = data.get("is_valid_format", {}).get("value")
            is_mx_found = data.get("is_mx_found", {}).get("value")
            suggestion = data.get("suggestion") or ""
            status = deliver or ("válido" if is_valid_format and is_mx_found else "inválido")
            res = {"email_validacao": status}
            if suggestion:
                res["email_sugestao"] = suggestion
            return res
        except Exception as e:
            logger.error(f"Email validation error: {e}")
            return {"email_validacao": "erro"}


