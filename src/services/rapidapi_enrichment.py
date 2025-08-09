"""
Serviço de enriquecimento opcional via RapidAPI

Tenta consultar detalhes por CNPJ na API configurada para validar/completar
dados vindos da Nuvem Fiscal. É best-effort e nunca interrompe o fluxo.
"""

from __future__ import annotations

import re
from typing import Optional, Tuple

import requests

from src.config.settings import Settings
from src.models.empresa import Empresa, Endereco, CNAE
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class RapidAPIEnrichmentService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update(settings.get_api_headers())

    def enrich_empresa_by_cnpj(self, empresa: Empresa) -> Empresa:
        """Complementa campos faltantes da empresa via RapidAPI (best-effort)."""
        try:
            cnpj_num = re.sub(r"\D", "", empresa.cnpj)
            payload = self._fetch_by_cnpj(cnpj_num)
            if not payload:
                return empresa

            # Extrair objeto empresa da resposta genérica
            data = self._extract_company_object(payload, cnpj_num)
            if not data:
                return empresa

            # Endereço
            if not empresa.endereco or not (
                empresa.endereco.logradouro or empresa.endereco.cidade or empresa.endereco.cep
            ):
                endereco = Endereco(
                    logradouro=data.get("logradouro") or data.get("rua"),
                    numero=str(data.get("numero")) if data.get("numero") is not None else None,
                    bairro=data.get("bairro"),
                    cidade=data.get("municipio") or data.get("cidade"),
                    uf=data.get("uf") or data.get("estado") or data.get("estado_sigla"),
                    cep=(data.get("cep") or "").replace("-", "") or None,
                )
                # Só atualiza se algo vier preenchido
                if any([endereco.logradouro, endereco.cidade, endereco.cep]):
                    empresa.endereco = endereco

            # Email/Telefone
            if not empresa.email:
                empresa.email = data.get("email") or data.get("email_contato")
            if not empresa.telefone:
                empresa.telefone = (
                    data.get("telefone")
                    or data.get("telefone1")
                    or data.get("ddd_telefone_1")
                    or data.get("ddd_telefone_2")
                )

            # CNAE principal
            if not empresa.cnae_principal:
                cnae_codigo, cnae_desc = self._extract_cnae(data)
                if cnae_codigo:
                    empresa.cnae_principal = CNAE(codigo=cnae_codigo, descricao=cnae_desc or "", principal=True)

            return empresa

        except Exception as exc:
            logger.warning(f"Enriquecimento RapidAPI falhou para CNPJ {empresa.cnpj}: {exc}")
            return empresa

    def _fetch_by_cnpj(self, cnpj: str) -> Optional[dict]:
        """Tenta diferentes formatos de endpoint para buscar por CNPJ."""
        base = self.settings.RAPIDAPI_BASE_URL.rstrip("/")

        # 1) Se base aparenta já ser um endpoint .php (ex.: buscar-base.php)
        #    tentar com ?cnpj= e fallback com ?campo=cnpj&q=
        if base.endswith(".php"):
            for params in ( {"cnpj": cnpj}, {"campo": "cnpj", "q": cnpj} ):
                try:
                    resp = self.session.get(base, params=params, timeout=self.settings.REQUEST_TIMEOUT)
                    if resp.status_code == 200:
                        return resp.json()
                except Exception:
                    continue

        # 2) Padrão REST: /empresa/{cnpj}
        try:
            resp = self.session.get(f"{base}/empresa/{cnpj}", timeout=self.settings.REQUEST_TIMEOUT)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass

        # 3) Padrão query: ?cnpj=... na raiz
        try:
            resp = self.session.get(base, params={"cnpj": cnpj}, timeout=self.settings.REQUEST_TIMEOUT)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass

        return None

    def _extract_company_object(self, payload: dict, cnpj: str) -> Optional[dict]:
        """Normaliza payloads diferentes para obter um dicionário de empresa."""
        if not isinstance(payload, dict):
            return None

        # casos comuns
        if "empresa" in payload and isinstance(payload["empresa"], dict):
            return payload["empresa"]
        if "data" in payload and isinstance(payload["data"], dict):
            return payload["data"]
        if "empresas" in payload and isinstance(payload["empresas"], list):
            for item in payload["empresas"]:
                cnpj_item = re.sub(r"\D", "", str(item.get("cnpj", "")))
                if cnpj_item == cnpj:
                    return item

        return payload if payload.get("cnpj") else None

    def _extract_cnae(self, data: dict) -> Tuple[Optional[str], Optional[str]]:
        # Possíveis formatos
        if data.get("cnae"):
            c = data["cnae"]
            if isinstance(c, dict):
                return c.get("codigo") or c.get("code"), c.get("descricao") or c.get("text")
            if isinstance(c, str):
                return c, None
        if data.get("atividade_principal"):
            ap = data["atividade_principal"]
            if isinstance(ap, list) and ap:
                return ap[0].get("code") or ap[0].get("codigo"), ap[0].get("text") or ap[0].get("descricao")
            if isinstance(ap, dict):
                return ap.get("code") or ap.get("codigo"), ap.get("text") or ap.get("descricao")
        return None, None


