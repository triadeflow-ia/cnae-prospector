from __future__ import annotations

"""
Phone validation/normalization service (Layer 1)
Providers supported: numverify (default), abstractapi (basic)
"""

import requests
from typing import Optional, Dict

from src.config.settings import Settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class PhoneValidationService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.enabled = bool(settings.ENABLE_PHONE_VALIDATION and settings.PHONE_VALIDATION_API_KEY)
        self.provider = settings.PHONE_VALIDATION_PROVIDER
        self.session = requests.Session()

    def validate(self, raw_phone: Optional[str]) -> Dict[str, str]:
        if not raw_phone:
            return {}
        phone_digits = "".join(ch for ch in raw_phone if ch.isdigit())
        if not phone_digits:
            return {}

        # Offline normalization fallback (E.164 BR best-effort)
        digits = phone_digits
        if digits.startswith("55"):
            digits = digits[2:]
        # keep last 11 or 10 digits as local number
        if len(digits) > 11:
            digits = digits[-11:]
        e164_offline = "+55" + digits
        fallback = {
            "telefone_validado": e164_offline,
            "validacao_telefone": "offline",
            "tipo_linha": ""
        }

        # If provider not enabled, return fallback immediately
        if not self.enabled:
            return fallback

        try:
            if self.provider == "abstract":
                url = f"https://phonevalidation.abstractapi.com/v1/?api_key={self.settings.PHONE_VALIDATION_API_KEY}&phone={phone_digits}&country=BR"
            else:  # numverify
                url = f"http://apilayer.net/api/validate?access_key={self.settings.PHONE_VALIDATION_API_KEY}&number={phone_digits}&country_code=BR&format=1"
            r = self.session.get(url, timeout=self.settings.REQUEST_TIMEOUT)
            if r.status_code != 200:
                return fallback
            data = r.json()
            # Normalized E.164 might be in different fields
            e164 = data.get("international_format") or data.get("format", {}).get("e164") or data.get("e164")
            valid = data.get("valid")
            line_type = data.get("line_type") or data.get("type")
            return {
                "telefone_validado": e164 or phone_digits,
                "validacao_telefone": "válido" if valid else "inválido",
                "tipo_linha": line_type or ""
            }
        except Exception as e:
            logger.error(f"Phone validation error: {e}")
            return fallback


