"""
Cliente para a API Lista de Empresas por Segmento via RapidAPI
"""

import os
import time
import requests
from typing import Dict, List, Optional, Any
from loguru import logger

from ..config.settings import get_settings
from ..models.empresa import Empresa, Endereco, CNAE


class EmpresasBrasilAPI:
    """Cliente para a API Lista de Empresas por Segmento"""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = "https://lista-de-empresas-por-segmento.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": self.settings.rapidapi_key,
            "X-RapidAPI-Host": "lista-de-empresas-por-segmento.p.rapidapi.com"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Faz uma requisição para a API com retry e rate limiting"""
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.settings.api_max_retries):
            try:
                logger.debug(f"Fazendo requisição para {url} (tentativa {attempt + 1})")
                response = self.session.get(url, params=params, timeout=self.settings.api_timeout)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    logger.warning("Rate limit atingido, aguardando...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    logger.error(f"Erro na API: {response.status_code} - {response.text}")
                    return {}
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro na requisição: {e}")
                if attempt < self.settings.api_max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return {}
        
        return {}
    
    def buscar_por_cnae(self, cnae: str, uf: str = None, cidade: str = None, 
                        limit: int = 100) -> List[Empresa]:
        """Busca empresas por CNAE usando a nova API"""
        logger.info(f"Buscando empresas com CNAE {cnae}")
        
        # Usar a nova API de busca por segmento
        params = {
            "campo": "cnae",
            "q": cnae,
            "situacao": "Ativa"
        }
        
        if uf:
            params["uf"] = uf
        if cidade:
            params["cidade"] = cidade
            
        data = self._make_request("buscar-por-segmento.php", params)
        
        empresas = []
        if data and "empresas" in data:
            for emp_data in data["empresas"]:
                empresa = self._parse_empresa(emp_data)
                if empresa:
                    empresas.append(empresa)
        
        logger.info(f"Encontradas {len(empresas)} empresas")
        return empresas
    
    def buscar_por_cep(self, cep: str, limit: int = 100) -> List[Empresa]:
        """Busca empresas por CEP"""
        logger.info(f"Buscando empresas com CEP {cep}")
        
        params = {
            "campo": "cep",
            "q": cep,
            "situacao": "Ativa"
        }
            
        data = self._make_request("buscar-por-segmento.php", params)
        
        empresas = []
        if data and "empresas" in data:
            for emp_data in data["empresas"]:
                empresa = self._parse_empresa(emp_data)
                if empresa:
                    empresas.append(empresa)
        
        logger.info(f"Encontradas {len(empresas)} empresas")
        return empresas
    
    def buscar_por_cnpj(self, cnpj: str) -> Optional[Empresa]:
        """Busca uma empresa específica por CNPJ"""
        logger.info(f"Buscando empresa com CNPJ {cnpj}")
        
        params = {
            "campo": "cnpj",
            "q": cnpj
        }
        data = self._make_request("buscar-por-segmento.php", params)
        
        if data and "empresas" in data and len(data["empresas"]) > 0:
            return self._parse_empresa(data["empresas"][0])
        
        return None
    
    def buscar_por_nome(self, nome: str, uf: str = None, limit: int = 100) -> List[Empresa]:
        """Busca empresas por nome"""
        logger.info(f"Buscando empresas com nome '{nome}'")
        
        params = {
            "campo": "nome",
            "q": nome,
            "situacao": "Ativa"
        }
        
        if uf:
            params["uf"] = uf
            
        data = self._make_request("buscar-por-segmento.php", params)
        
        empresas = []
        if data and "empresas" in data:
            for emp_data in data["empresas"]:
                empresa = self._parse_empresa(emp_data)
                if empresa:
                    empresas.append(empresa)
        
        logger.info(f"Encontradas {len(empresas)} empresas")
        return empresas
    
    def _parse_empresa(self, data: Dict[str, Any]) -> Optional[Empresa]:
        """Converte dados da API para objeto Empresa"""
        try:
            # Parse endereço
            endereco = None
            if "endereco" in data:
                end_data = data["endereco"]
                endereco = Endereco(
                    logradouro=end_data.get("logradouro", ""),
                    numero=end_data.get("numero", ""),
                    complemento=end_data.get("complemento", ""),
                    bairro=end_data.get("bairro", ""),
                    cidade=end_data.get("cidade", ""),
                    uf=end_data.get("uf", ""),
                    cep=end_data.get("cep", ""),
                    municipio=end_data.get("municipio", "")
                )
            
            # Parse CNAE
            cnae = None
            if "cnae" in data:
                cnae_data = data["cnae"]
                cnae = CNAE(
                    codigo=cnae_data.get("codigo", ""),
                    descricao=cnae_data.get("descricao", "")
                )
            
            empresa = Empresa(
                cnpj=data.get("cnpj", ""),
                razao_social=data.get("razao_social", ""),
                nome_fantasia=data.get("nome_fantasia", ""),
                data_abertura=data.get("data_abertura", ""),
                situacao=data.get("situacao", ""),
                tipo=data.get("tipo", ""),
                porte=data.get("porte", ""),
                natureza_juridica=data.get("natureza_juridica", ""),
                capital_social=data.get("capital_social", 0.0),
                endereco=endereco,
                cnae=cnae,
                telefone=data.get("telefone", ""),
                email=data.get("email", ""),
                site=data.get("site", ""),
                data_ultima_atualizacao=data.get("data_ultima_atualizacao", "")
            )
            
            return empresa
            
        except Exception as e:
            logger.error(f"Erro ao parsear empresa: {e}")
            return None
    
    def testar_conexao(self) -> bool:
        """Testa se a conexão com a API está funcionando"""
        try:
            data = self._make_request("buscar-por-segmento.php", {"campo": "cnae", "q": "5611-2/01", "situacao": "Ativa"})
            return "empresas" in data
        except Exception as e:
            logger.error(f"Erro ao testar conexão: {e}")
            return False


# Instância global do cliente
api_client = EmpresasBrasilAPI() 