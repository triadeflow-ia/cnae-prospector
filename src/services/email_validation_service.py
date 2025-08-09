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
        self._cache: dict[str, tuple[dict, float]] = {}
        self._cache_ttl_seconds: int = 24 * 3600
        self._last_request_ts: float | None = None
        self._min_interval_seconds: float = 0.2  # ~5 QPS máx

    def validate(self, email: Optional[str]) -> Dict[str, str]:
        if not email:
            return {}
        # Simple offline format check
        if "@" not in email:
            return {"email_validacao": "inválido (formato)"}

        if not self.enabled:
            return {"email_validacao": "offline"}

        try:
            # Cache first
            import time
            now = time.time()
            cached = self._cache.get(email)
            if cached and (now - cached[1] < self._cache_ttl_seconds):
                return cached[0]

            # Basic QPS throttle
            if self._last_request_ts is not None:
                elapsed = now - self._last_request_ts
                if elapsed < self._min_interval_seconds:
                    time.sleep(self._min_interval_seconds - elapsed)
            self._last_request_ts = time.time()

            url = (
                "https://emailvalidation.abstractapi.com/v1/?api_key="
                f"{self.settings.EMAIL_VALIDATION_API_KEY}&email={email}"
            )
            # Retry/backoff on 429/5xx
            for attempt in range(3):
                r = self.session.get(url, timeout=self.settings.REQUEST_TIMEOUT)
                if r.status_code not in (429, 500, 502, 503, 504):
                    break
                backoff = (2 ** attempt) * 0.5
                time.sleep(backoff)
            if r.status_code != 200:
                result = {"email_validacao": f"erro http {r.status_code}"}
                self._cache[email] = (result, time.time())
                return result
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
            self._cache[email] = (res, time.time())
            return res
        except Exception as e:
            logger.error(f"Email validation error: {e}")
            return {"email_validacao": "erro"}


