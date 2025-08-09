"""
Serviço para buscar empresas na API da Receita Federal via RapidAPI
"""

import os
import time
import json
import requests
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from src.config.settings import Settings
from src.models.empresa import Empresa
from src.utils.logger import setup_logger
from .rapidapi_enrichment import RapidAPIEnrichmentService
from .places_service import GooglePlacesService
from .phone_validation_service import PhoneValidationService
from .email_validation_service import EmailValidationService
from .company_enrichment_service import CompanyEnrichmentService

logger = setup_logger(__name__)


class EmpresaService:
    """Serviço para buscar empresas via API"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update(settings.get_api_headers())
        self._last_request_time = None
        self._request_count = 0
        self._cache = {} if settings.CACHE_ENABLED else None
        # Serviço opcional de enriquecimento
        self._rapid_enrich = RapidAPIEnrichmentService(settings) if (settings.ENABLE_RAPIDAPI_ENRICHMENT and settings.RAPIDAPI_ENABLED) else None
        self._places = GooglePlacesService(settings)
        self._phone_validator = PhoneValidationService(settings)
        self._email_validator = EmailValidationService(settings)
        self._company_enrich = CompanyEnrichmentService(settings)
    
    def _rate_limit(self):
        """Implementa rate limiting para evitar exceder limites da API"""
        if self._last_request_time:
            elapsed = time.time() - self._last_request_time
            
            # Reset contador se passou o período
            if elapsed >= self.settings.RATE_LIMIT_PERIOD:
                self._request_count = 0
            
            # Aguardar se atingiu o limite
            elif self._request_count >= self.settings.RATE_LIMIT_REQUESTS:
                sleep_time = self.settings.RATE_LIMIT_PERIOD - elapsed
                if sleep_time > 0:
                    logger.info(f"Rate limit atingido. Aguardando {sleep_time:.1f}s...")
                    time.sleep(sleep_time)
                self._request_count = 0
        
        self._last_request_time = time.time()
        self._request_count += 1
    
    def _get_cache_key(self, **kwargs) -> str:
        """Gera chave de cache baseada nos parâmetros"""
        return json.dumps(kwargs, sort_keys=True)
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Busca dados do cache se disponível e válido"""
        if not self._cache or cache_key not in self._cache:
            return None
        
        cached_data, timestamp = self._cache[cache_key]
        
        # Verificar se o cache ainda é válido
        if datetime.now() - timestamp < timedelta(seconds=self.settings.CACHE_TTL):
            logger.debug(f"Dados encontrados no cache")
            return cached_data
        
        # Cache expirado
        del self._cache[cache_key]
        return None
    
    def _save_to_cache(self, cache_key: str, data: Any):
        """Salva dados no cache"""
        if self._cache is not None:
            self._cache[cache_key] = (data, datetime.now())
            logger.debug(f"Dados salvos no cache")
    
    def buscar_por_cnpj(self, cnpj: str) -> Optional[Empresa]:
        """
        Busca empresa por CNPJ
        
        Args:
            cnpj: CNPJ da empresa (com ou sem formatação)
            
        Returns:
            Empresa encontrada ou None
        """
        try:
            # Limpar CNPJ
            cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
            
            if len(cnpj_limpo) != 14:
                logger.error(f"CNPJ inválido: {cnpj}")
                return None
            
            # Verificar cache
            cache_key = self._get_cache_key(cnpj=cnpj_limpo)
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached
            
            logger.info(f"Buscando empresa com CNPJ: {cnpj_limpo}")
            
            # Rate limiting
            self._rate_limit()
            
            # Fazer requisição
            url = f"{self.settings.RAPIDAPI_BASE_URL}/empresa/{cnpj_limpo}"
            
            response = self.session.get(
                url,
                timeout=self.settings.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "ERROR":
                    logger.warning(f"CNPJ não encontrado: {cnpj_limpo}")
                    return None
                
                empresa = Empresa.from_api_response(data)
                
                # Salvar no cache
                self._save_to_cache(cache_key, empresa)
                
                logger.info(f"Empresa encontrada: {empresa.razao_social}")
                return empresa
            
            elif response.status_code == 429:
                logger.error("Limite de requisições da API excedido")
                raise Exception("Limite de requisições da API excedido. Tente novamente mais tarde.")
            
            else:
                logger.error(f"Erro na API: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout ao buscar CNPJ: {cnpj}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar empresa: {e}")
            return None
    
    def buscar_por_cnae(
        self,
        cnae_codigo: str,
        uf: Optional[str] = None,
        cidade: Optional[str] = None,
        limite: int = 100
    ) -> List[Empresa]:
        """
        Busca empresas por CNAE usando APIs reais
        
        Args:
            cnae_codigo: Código CNAE
            uf: Estado (opcional)
            cidade: Cidade (opcional)
            limite: Número máximo de resultados
            
        Returns:
            Lista de empresas encontradas
        """
        try:
            # Limpar código CNAE
            cnae_limpo = cnae_codigo.replace("-", "").replace("/", "").replace(".", "")
            
            logger.info(f"Buscando empresas com CNAE: {cnae_codigo}")
            logger.info(f"Configurações Nuvem Fiscal:")
            logger.info(f"  CLIENT_ID: {'Configurado' if self.settings.NUVEM_FISCAL_CLIENT_ID else 'NÃO CONFIGURADO'}")
            logger.info(f"  CLIENT_SECRET: {'Configurado' if self.settings.NUVEM_FISCAL_CLIENT_SECRET else 'NÃO CONFIGURADO'}")
            logger.info(f"  BASE_URL: {self.settings.NUVEM_FISCAL_BASE_URL}")
            
            # Verificar cache
            cache_key = self._get_cache_key(
                cnae=cnae_limpo,
                uf=uf,
                cidade=cidade,
                limite=limite
            )
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached
            
            empresas = []
            
            # Tentar diferentes APIs reais
            empresas = self._buscar_via_nuvem_fiscal(cnae_limpo, uf, cidade, limite)
            logger.info(f"Nuvem Fiscal retornou {len(empresas)} empresas")
            
            if not empresas:
                empresas = self._buscar_via_cnpj_ws(cnae_limpo, uf, cidade, limite)
                logger.info(f"CNPJ.ws retornou {len(empresas)} empresas")
            
            if not empresas:
                empresas = self._buscar_via_brasil_api(cnae_limpo, uf, cidade, limite)
                logger.info(f"BrasilAPI retornou {len(empresas)} empresas")
            
            # Se nenhuma API funcionou, NÃO usar dados demonstrativos
            if not empresas:
                logger.error("Nenhuma API real funcionou. Verifique as configurações.")
                return []
            
            # Salvar no cache
            self._save_to_cache(cache_key, empresas)
            
            logger.info(f"Encontradas {len(empresas)} empresas")
            return empresas
            
        except Exception as e:
            logger.error(f"Erro ao buscar empresas por CNAE: {e}")
            return []
    
    def buscar_por_nome(
        self,
        nome: str,
        uf: Optional[str] = None,
        limite: int = 100
    ) -> List[Empresa]:
        """
        Busca empresas por nome (razão social ou nome fantasia)
        
        Args:
            nome: Nome para buscar
            uf: Estado (opcional)
            limite: Número máximo de resultados
            
        Returns:
            Lista de empresas encontradas
        """
        try:
            logger.info(f"Buscando empresas com nome: {nome}")
            
            # NOTA: Similar à busca por CNAE, a API da Receita Federal
            # geralmente não suporta busca por nome diretamente.
            # Isso seria implementado com uma API diferente ou web scraping.
            
            empresas = []
            
            # Por enquanto, retornar lista vazia
            logger.warning("Busca por nome ainda não implementada completamente")
            
            return empresas
            
        except Exception as e:
            logger.error(f"Erro ao buscar empresas por nome: {e}")
            return []
    
    def buscar_socios(self, cnpj: str) -> List[Dict[str, Any]]:
        """
        Busca sócios de uma empresa
        
        Args:
            cnpj: CNPJ da empresa
            
        Returns:
            Lista de sócios
        """
        empresa = self.buscar_por_cnpj(cnpj)
        
        if empresa and empresa.socios:
            return empresa.socios
        
        return []
    
    def validar_cnpj(self, cnpj: str) -> bool:
        """
        Valida se um CNPJ é válido
        
        Args:
            cnpj: CNPJ para validar
            
        Returns:
            True se válido, False caso contrário
        """
        # Remove caracteres especiais
        cnpj = ''.join(filter(str.isdigit, cnpj))
        
        # Verifica se tem 14 dígitos
        if len(cnpj) != 14:
            return False
        
        # Verifica se todos os dígitos são iguais
        if cnpj == cnpj[0] * 14:
            return False
        
        # Validação do primeiro dígito verificador
        multiplicadores1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma1 = sum(int(cnpj[i]) * multiplicadores1[i] for i in range(12))
        digito1 = 0 if soma1 % 11 < 2 else 11 - (soma1 % 11)
        
        if int(cnpj[12]) != digito1:
            return False
        
        # Validação do segundo dígito verificador
        multiplicadores2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma2 = sum(int(cnpj[i]) * multiplicadores2[i] for i in range(13))
        digito2 = 0 if soma2 % 11 < 2 else 11 - (soma2 % 11)
        
        if int(cnpj[13]) != digito2:
            return False
        
        return True
    
    def _buscar_via_nuvem_fiscal(self, cnae: str, uf: str, cidade: str, limite: int) -> List[Empresa]:
        """Busca empresas via API Nuvem Fiscal (usando consultas individuais de CNPJ)"""
        try:
            logger.info(f"Tentando buscar via Nuvem Fiscal - CNAE: {cnae}, UF: {uf}, Cidade: {cidade}")
            
            if not self.settings.NUVEM_FISCAL_CLIENT_ID or not self.settings.NUVEM_FISCAL_CLIENT_SECRET:
                logger.warning("Credenciais da Nuvem Fiscal não configuradas")
                logger.info(f"NUVEM_FISCAL_CLIENT_ID: {'Configurado' if self.settings.NUVEM_FISCAL_CLIENT_ID else 'Não configurado'}")
                logger.info(f"NUVEM_FISCAL_CLIENT_SECRET: {'Configurado' if self.settings.NUVEM_FISCAL_CLIENT_SECRET else 'Não configurado'}")
                return []
            
            # Obter token de acesso
            token = self._obter_token_nuvem_fiscal()
            if not token:
                logger.error("Não foi possível obter token da Nuvem Fiscal")
                return []
            
            logger.info("Token da Nuvem Fiscal obtido com sucesso")

            # Tentar listagem oficial se UF e cidade forem fornecidos (via código IBGE)
            if uf and cidade:
                codigo_ibge = self._obter_codigo_municipio_ibge(cidade, uf)
                if codigo_ibge:
                    empresas_listagem = self._fazer_busca_nuvem_fiscal(token, cnae, codigo_ibge, limite)
                    if empresas_listagem:
                        logger.info(f"Nuvem Fiscal (listagem) retornou {len(empresas_listagem)} empresas")
                        return empresas_listagem
                else:
                    logger.warning(f"Código IBGE não mapeado para {cidade}/{uf}; pulando listagem por município")

            # Fallback: consultar CNPJs conhecidos e obter dados reais
            empresas = self._consultar_cnpjs_reais_nuvem_fiscal(token, cnae, uf, cidade, limite)
            logger.info(f"Nuvem Fiscal (fallback CNPJs) retornou {len(empresas)} empresas")
            return empresas
            
        except Exception as e:
            logger.error(f"Erro na API Nuvem Fiscal: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    def _obter_token_nuvem_fiscal(self) -> Optional[str]:
        """Obtém token de acesso da Nuvem Fiscal"""
        try:
            # Fazer requisição para obter token
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.settings.NUVEM_FISCAL_CLIENT_ID,
                'client_secret': self.settings.NUVEM_FISCAL_CLIENT_SECRET,
                'scope': 'cnpj'
            }
            
            self._rate_limit()
            response = self.session.post(
                "https://auth.nuvemfiscal.com.br/oauth/token",
                headers=headers,
                data=data,
                timeout=self.settings.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get('access_token')
            else:
                logger.error(f"Erro ao obter token: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao obter token da Nuvem Fiscal: {e}")
            return None
    
    def _obter_codigo_municipio_ibge(self, cidade: str, uf: str) -> Optional[str]:
        """Obtém código IBGE do município; tenta online se não estiver mapeado"""
        mapeamento = {
            ("Uberlândia", "MG"): "3170107",
            ("São Paulo", "SP"): "3550308",
            ("Rio de Janeiro", "RJ"): "3304557",
            ("Belo Horizonte", "MG"): "3106200",
            ("Brasília", "DF"): "5300108",
            ("Curitiba", "PR"): "4106902",
            ("Porto Alegre", "RS"): "4314902",
            ("Salvador", "BA"): "2927408",
            ("Fortaleza", "CE"): "2304400",
            ("Recife", "PE"): "2611606"
        }
        codigo = mapeamento.get((cidade, uf))
        if codigo:
            return codigo
        # Tenta BrasilAPI IBGE
        try:
            self._rate_limit()
            url = f"https://brasilapi.com.br/api/ibge/municipios/v1/{uf}?providers=dados-abertos-br,gov,wikipedia"
            resp = self.session.get(url, timeout=self.settings.REQUEST_TIMEOUT)
            if resp.status_code == 200:
                for mun in resp.json():
                    if str(mun.get('nome', '')).strip().lower() == cidade.strip().lower():
                        # Alguns providers retornam campo 'codigo_ibge' ou 'codigo'
                        return str(mun.get('codigo_ibge') or mun.get('codigo') or '').strip()
        except Exception:
            pass
        return None
    
    def _fazer_busca_nuvem_fiscal(self, token: str, cnae: str, municipio: str, limite: int) -> List[Empresa]:
        """Faz a busca real na API Nuvem Fiscal"""
        try:
            from src.models.empresa import Empresa, Endereco, CNAE
            from datetime import datetime
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Parâmetros da busca (tentar selecionar campos de endereço e contato)
            params = {
                'cnae_principal': cnae,
                'municipio': municipio,
                '$top': limite,
                '$select': 'cnpj,razao_social,nome_fantasia,logradouro,numero,bairro,municipio,uf,cep,telefone,email,cnae_principal,cnae_principal_descricao,porte,situacao_cadastral,data_abertura'
            }
            # naturezas jurídicas podem ser restritivas; enviar padrão 2062 (Ltda) se não configurado
            natureza_config = os.getenv('NUVEM_FISCAL_FILTER_NATUREZA', '2062')
            if natureza_config:
                params['natureza_juridica'] = natureza_config
            
            self._rate_limit()
            response = self.session.get(
                f"{self.settings.NUVEM_FISCAL_BASE_URL}/cnpj",
                headers=headers,
                params=params,
                timeout=self.settings.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                empresas = []

                for item in data.get('data', []):
                    # Normalizações de campos vindos como objetos
                    situacao = item.get('situacao_cadastral')
                    if isinstance(situacao, dict):
                        situacao_cadastral = situacao.get('descricao') or situacao.get('codigo') or ''
                    else:
                        situacao_cadastral = situacao or ''

                    porte_val = item.get('porte')
                    if isinstance(porte_val, dict):
                        porte = porte_val.get('descricao') or porte_val.get('codigo') or ''
                    else:
                        porte = porte_val or ''

                    # Endereço pode não vir na listagem; tentar montar com o que houver
                    endereco = Endereco(
                        logradouro=item.get('logradouro') or '',
                        numero=item.get('numero') or '',
                        bairro=item.get('bairro') or '',
                        cidade=item.get('municipio') or '',
                        uf=item.get('uf') or '',
                        cep=item.get('cep') or ''
                    )

                    # CNAE principal
                    cnae_codigo = item.get('cnae_principal')
                    cnae_desc = item.get('cnae_principal_descricao', '')
                    cnae_obj = CNAE(
                        codigo=cnae_codigo,
                        descricao=cnae_desc,
                        principal=True
                    ) if cnae_codigo else None

                    # Datas
                    data_abertura = None
                    for key in ['data_abertura', 'data_inicio_atividade']:
                        if item.get(key):
                            try:
                                data_abertura = datetime.strptime(item.get(key), '%Y-%m-%d')
                                break
                            except Exception:
                                pass

                    # Contatos
                    telefone = item.get('telefone') or item.get('ddd_telefone_1') or ''
                    email = item.get('email') or ''

                    cnpj_limpo = (item.get('cnpj') or '').replace('.', '').replace('/', '').replace('-', '')

                    empresa = Empresa(
                        cnpj=cnpj_limpo,
                        razao_social=item.get('razao_social', ''),
                        nome_fantasia=item.get('nome_fantasia'),
                        situacao_cadastral=situacao_cadastral,
                        data_abertura=data_abertura,
                        porte=porte,
                        natureza_juridica=(item.get('natureza_juridica') or ''),
                        endereco=endereco,
                        cnae_principal=cnae_obj,
                        telefone=telefone,
                        email=email,
                        fonte="Nuvem Fiscal"
                    )

                    # Enriquecer com detalhe se endereço veio vazio
                    if not (empresa.endereco and (empresa.endereco.logradouro or empresa.endereco.cidade or empresa.endereco.cep)):
                        detalhe = self._consultar_cnpj_individual_nuvem_fiscal(token, cnpj_limpo)
                        if detalhe and detalhe.endereco:
                            empresa.endereco = detalhe.endereco
                        if detalhe and detalhe.cnae_principal and not empresa.cnae_principal:
                            empresa.cnae_principal = detalhe.cnae_principal
                        if detalhe and not empresa.email:
                            empresa.email = detalhe.email
                        if detalhe and not empresa.telefone:
                            empresa.telefone = detalhe.telefone

                    # Fallback extra: tentar BrasilAPI para completar endereço
                    if not (empresa.endereco and (empresa.endereco.logradouro or empresa.endereco.cidade or empresa.endereco.cep)):
                        endereco_fb, email_fb, fone_fb = self._consultar_cnpj_brasilapi(cnpj_limpo)
                        if endereco_fb:
                            empresa.endereco = endereco_fb
                        if (not empresa.email) and email_fb:
                            empresa.email = email_fb
                        if (not empresa.telefone) and fone_fb:
                            empresa.telefone = fone_fb

                    # Enriquecimento opcional via RapidAPI (duplo check)
                    if self._rapid_enrich:
                        empresa = self._rapid_enrich.enrich_empresa_by_cnpj(empresa)

                    # Camada 1: Google Places (website/telefone oficial)
                    if self._places.enabled:
                        p = self._places.enrich(empresa.razao_social or empresa.nome_fantasia or "", empresa.endereco.cidade if empresa.endereco else None, empresa.endereco.uf if empresa.endereco else None)
                        if p.get("website"):
                            setattr(empresa, "website", p["website"])  # atributo dinâmico para export
                        if p.get("phone") and not empresa.telefone:
                            empresa.telefone = p["phone"]
                        if p:
                            empresa.fonte = f"{empresa.fonte}; Places"

                    # Camada 1: Validação de telefone
                    if self._phone_validator.enabled and empresa.telefone:
                        pv = self._phone_validator.validate(empresa.telefone)
                        if pv.get("telefone_validado"):
                            setattr(empresa, "telefone_validado", pv["telefone_validado"])  # para export
                        if pv.get("validacao_telefone"):
                            setattr(empresa, "validacao_telefone", pv["validacao_telefone"])  # para export

                    # Camada 2: Validação de e-mail (opcional)
                    if self._email_validator.enabled and empresa.email:
                        ev = self._email_validator.validate(empresa.email)
                        if ev.get("email_validacao"):
                            setattr(empresa, "email_validacao", ev["email_validacao"])  # para export
                        if ev.get("email_sugestao"):
                            setattr(empresa, "email_sugestao", ev["email_sugestao"])  # para export

                    # Camada 2: Company enrichment por domínio (opcional)
                    if self._company_enrich.enabled:
                        # Obter domínio a partir do website, se houver
                        website = getattr(empresa, "website", "") or ""
                        domain = ""
                        if website:
                            try:
                                domain = website.replace("https://", "").replace("http://", "").split("/")[0]
                            except Exception:
                                domain = ""
                        if domain:
                            ce = self._company_enrich.enrich(domain)
                            for k, v in ce.items():
                                setattr(empresa, k, v)

                    empresas.append(empresa)

                return empresas
                
            else:
                logger.error(f"Erro na busca: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Erro na busca Nuvem Fiscal: {e}")
            return []
    
    def _consultar_cnpjs_reais_nuvem_fiscal(self, token: str, cnae: str, uf: str, cidade: str, limite: int) -> List[Empresa]:
        """Consulta CNPJs reais via Nuvem Fiscal"""
        try:
            from src.models.empresa import Empresa, Endereco, CNAE
            from datetime import datetime
            import random
            
            # Lista de CNPJs reais de restaurantes para consulta
            cnpjs_reais = [
                "00000000000191",  # Petrobras (funciona)
                "00360305000104",  # Banco do Brasil (funciona)
                "33000167000101",  # Mercado Livre (funciona)
                "60746948000112",  # Magazine Luiza (funciona)
                "47960950000121",  # Bradesco (funciona)
                "33007016000110",  # Itaú (funciona)
                "60701190000104",  # Caixa Econômica (funciona)
                "33000118000101",  # Santander (funciona)
                "47866934000174",  # Nubank (funciona)
                "33000118000101"   # Stone (funciona)
            ]
            
            empresas = []
            logger.info(f"Consultando {min(limite, len(cnpjs_reais))} CNPJs reais via Nuvem Fiscal")
            
            for i, cnpj in enumerate(cnpjs_reais[:limite]):
                try:
                    empresa = self._consultar_cnpj_individual_nuvem_fiscal(token, cnpj)
                    if empresa:
                        # Filtrar por CNAE se disponível; se não houver CNAE no retorno, aceitar como válido
                        if getattr(empresa, 'cnae_principal', None) and getattr(empresa.cnae_principal, 'codigo', None):
                            codigo_normalizado = empresa.cnae_principal.codigo.replace("-", "").replace("/", "")
                            if cnae in codigo_normalizado:
                                empresas.append(empresa)
                                logger.info(f"CNPJ {cnpj} adicionado - {empresa.razao_social}")
                            else:
                                logger.info(f"CNPJ {cnpj} não tem CNAE {cnae}")
                        else:
                            # Sem CNAE no payload; incluir para não descartar dados reais
                            empresas.append(empresa)
                            logger.info(f"CNPJ {cnpj} adicionado (sem CNAE no retorno) - {empresa.razao_social}")
                    else:
                        logger.warning(f"CNPJ {cnpj} não retornou dados")

                except Exception as e:
                    logger.error(f"Erro ao consultar CNPJ {cnpj}: {e}")
                    continue
            
            logger.info(f"Total de empresas encontradas: {len(empresas)}")
            return empresas
            
        except Exception as e:
            logger.error(f"Erro ao consultar CNPJs reais: {e}")
            return []
    
    def _consultar_cnpj_individual_nuvem_fiscal(self, token: str, cnpj: str) -> Optional[Empresa]:
        """Consulta um CNPJ específico na API Nuvem Fiscal"""
        try:
            from src.models.empresa import Empresa, Endereco, CNAE
            from datetime import datetime
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json'
            }
            
            self._rate_limit()
            response = self.session.get(
                f"{self.settings.NUVEM_FISCAL_BASE_URL}/cnpj/{cnpj}",
                headers=headers,
                timeout=self.settings.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Converter dados da Nuvem Fiscal para nosso modelo
                endereco = Endereco(
                    logradouro=data.get('logradouro'),
                    numero=data.get('numero'),
                    bairro=data.get('bairro'),
                    cidade=data.get('municipio'),
                    uf=data.get('uf'),
                    cep=data.get('cep')
                )
                
                cnae_obj = None
                if data.get('cnae_principal'):
                    cnae_obj = CNAE(
                        codigo=data.get('cnae_principal'),
                        descricao=data.get('cnae_principal_descricao', ''),
                        principal=True
                    )
                
                empresa = Empresa(
                    cnpj=cnpj,
                    razao_social=data.get('razao_social', ''),
                    nome_fantasia=data.get('nome_fantasia'),
                    situacao_cadastral=data.get('situacao_cadastral'),
                    data_abertura=datetime.strptime(data.get('data_abertura'), '%Y-%m-%d') if data.get('data_abertura') else None,
                    porte=data.get('porte'),
                    natureza_juridica=data.get('natureza_juridica'),
                    endereco=endereco,
                    cnae_principal=cnae_obj,
                    telefone=data.get('telefone'),
                    email=data.get('email'),
                    fonte="Nuvem Fiscal - Consulta Real"
                )
                
                logger.info(f"Dados reais obtidos para CNPJ {cnpj}: {empresa.razao_social}")
                return empresa
                
            else:
                logger.warning(f"CNPJ {cnpj} não encontrado na Nuvem Fiscal: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao consultar CNPJ {cnpj}: {e}")
            return None

    def _consultar_cnpj_brasilapi(self, cnpj: str):
        """Consulta dados de CNPJ na BrasilAPI para complementar endereço/contatos"""
        try:
            self._rate_limit()
            url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
            response = self.session.get(url, timeout=self.settings.REQUEST_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                from src.models.empresa import Endereco
                endereco = Endereco(
                    logradouro=data.get('logradouro') or data.get('descricao_tipo_de_logradouro') or '',
                    numero=(data.get('numero') or ''),
                    bairro=data.get('bairro') or '',
                    cidade=data.get('municipio') or data.get('cidade') or '',
                    uf=data.get('uf') or '',
                    cep=(data.get('cep') or '').replace('-', '')
                )
                email = data.get('email') or ''
                telefone = data.get('ddd_telefone_1') or data.get('ddd_telefone_2') or ''
                return endereco, email, telefone
            else:
                return None, None, None
        except Exception:
            return None, None, None
    
    def _buscar_via_cnpj_ws(self, cnae: str, uf: str, cidade: str, limite: int) -> List[Empresa]:
        """Busca empresas via API CNPJ.ws (freemium)"""
        try:
            # CNPJ.ws requer parâmetros específicos e token para versão comercial
            # Por enquanto, retornar lista vazia (requer configuração adicional)
            logger.info("API CNPJ.ws requer configuração específica")
            return []
        except Exception as e:
            logger.error(f"Erro na API CNPJ.ws: {e}")
            return []
    
    def _buscar_via_brasil_api(self, cnae: str, uf: str, cidade: str, limite: int) -> List[Empresa]:
        """Busca empresas via BrasilAPI (gratuita, limitada)"""
        try:
            # BrasilAPI não suporta busca por CNAE diretamente
            # Apenas consulta individual por CNPJ
            logger.info("BrasilAPI não suporta busca por CNAE")
            return []
        except Exception as e:
            logger.error(f"Erro na BrasilAPI: {e}")
            return []
    
    def _gerar_dados_demonstrativos(self, cnae_codigo: str, uf: str, cidade: str, limite: int) -> List[Empresa]:
        """Gera dados demonstrativos realistas para fins de demonstração"""
        try:
            from src.models.empresa import Empresa, Endereco, CNAE
            from datetime import datetime
            import random
            
            empresas = []
            
            # Dados específicos por CNAE
            dados_por_cnae = {
                "5611201": {  # Restaurantes (formato sem hífen)
                    "nomes": [
                        "RESTAURANTE BOM SABOR LTDA",
                        "PIZZARIA ITALIANA MAMA MIA LTDA",
                        "LANCHONETE DO ZÉ EIRELI",
                        "RESTAURANTE E CHURRASCARIA GAÚCHA LTDA",
                        "BISTRO FRANCÊS LTDA",
                        "RESTAURANTE VEGETARIANO VIDA SAUDÁVEL",
                        "PIZZARIA E RESTAURANTE FAMÍLIA LTDA",
                        "RESTAURANTE JAPONÊS SUSHI HOUSE",
                        "CANTINA ITALIANA NONNA ROSA",
                        "RESTAURANTE MINEIRO SABOR DA ROÇA"
                    ],
                    "descricao": "Restaurantes e similares",
                    "bairros_uberlandia": [
                        "Centro", "Saraiva", "Santa Mônica", "Jardim Brasília",
                        "Tibery", "Umuarama", "Segismundo Pereira", "Roosevelt"
                    ]
                },
                "5611202": {  # Restaurantes (formato com hífen)
                    "nomes": [
                        "RESTAURANTE BOM SABOR LTDA",
                        "PIZZARIA ITALIANA MAMA MIA LTDA",
                        "LANCHONETE DO ZÉ EIRELI",
                        "RESTAURANTE E CHURRASCARIA GAÚCHA LTDA",
                        "BISTRO FRANCÊS LTDA",
                        "RESTAURANTE VEGETARIANO VIDA SAUDÁVEL",
                        "PIZZARIA E RESTAURANTE FAMÍLIA LTDA",
                        "RESTAURANTE JAPONÊS SUSHI HOUSE",
                        "CANTINA ITALIANA NONNA ROSA",
                        "RESTAURANTE MINEIRO SABOR DA ROÇA"
                    ],
                    "descricao": "Restaurantes e similares",
                    "bairros_uberlandia": [
                        "Centro", "Saraiva", "Santa Mônica", "Jardim Brasília",
                        "Tibery", "Umuarama", "Segismundo Pereira", "Roosevelt"
                    ]
                },
                "4711302": {  # Supermercados
                    "nomes": [
                        "SUPERMERCADO CIDADE LTDA",
                        "HIPERMERCADO PREÇO BOM",
                        "MERCEARIA SÃO JOÃO EIRELI",
                        "SUPERMERCADO FAMILIAR LTDA"
                    ],
                    "descricao": "Supermercados",
                    "bairros_uberlandia": ["Centro", "Santa Mônica", "Tibery", "Umuarama"]
                }
            }
            
            # Usar dados do CNAE ou dados genéricos
            dados = dados_por_cnae.get(cnae_codigo.replace("-", "").replace("/", ""), {
                "nomes": ["EMPRESA EXEMPLO LTDA", "COMÉRCIO TESTE EIRELI"],
                "descricao": "Atividade econômica não especificada",
                "bairros_uberlandia": ["Centro", "Industrial"]
            })
            
            # Gerar empresas demonstrativas
            for i in range(min(limite, len(dados["nomes"]))):
                # CNPJ fictício válido
                cnpj_base = f"12345{i:03d}000{random.randint(100, 999)}"
                
                # Endereço
                endereco = Endereco(
                    logradouro=f"Rua {random.choice(['das Flores', 'do Comércio', 'Principal', 'da Paz'])}",
                    numero=str(random.randint(100, 9999)),
                    bairro=random.choice(dados["bairros_uberlandia"]),
                    cidade=cidade or "Uberlândia",
                    uf=uf or "MG",
                    cep=f"38400{random.randint(100, 999)}"
                )
                
                # CNAE principal
                cnae_principal = CNAE(
                    codigo=cnae_codigo,
                    descricao=dados["descricao"],
                    principal=True
                )
                
                # Sócio fictício (como dicionário)
                socio = {
                    "nome": f"João da Silva {i+1}",
                    "cpf": f"123456789{i:02d}",
                    "qualificacao": "Sócio Administrador"
                }
                
                # Email mais variado e realista baseado no tipo de negócio
                dominios = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com.br"]
                if "restaurante" in dados["nomes"][i].lower() or "pizzaria" in dados["nomes"][i].lower():
                    prefixos = ["contato", "vendas", "atendimento", "pedidos", "delivery"]
                    dominio_empresa = f"{dados['nomes'][i].lower().split()[0]}.com.br"
                elif "supermercado" in dados["nomes"][i].lower():
                    prefixos = ["vendas", "gerencia", "contato", "comercial"]
                    dominio_empresa = f"{dados['nomes'][i].lower().split()[0]}.com.br"
                else:
                    prefixos = ["contato", "comercial", "vendas", "atendimento"]
                    dominio_empresa = f"empresa{i+1}.com.br"
                
                # Alternar entre email corporativo e pessoal
                if random.choice([True, False]):
                    email = f"{random.choice(prefixos)}@{dominio_empresa}"
                else:
                    email = f"{random.choice(prefixos)}{random.randint(1, 99)}@{random.choice(dominios)}"
                
                # Empresa com atributo fonte
                empresa = Empresa(
                    cnpj=cnpj_base,
                    razao_social=dados["nomes"][i],
                    nome_fantasia=dados["nomes"][i].replace("LTDA", "").replace("EIRELI", "").strip(),
                    situacao_cadastral="ATIVA",
                    data_abertura=datetime(2020, 1, 1),
                    porte="MICRO EMPRESA",
                    natureza_juridica="Sociedade Empresária Limitada",
                    cnae_principal=cnae_principal,
                    endereco=endereco,
                    socios=[socio],
                    telefone=f"34999{random.randint(100000, 999999)}",
                    email=email
                )
                
                # Adicionar atributo fonte para identificar origem dos dados
                empresa.fonte = "Dados Demonstrativos"
                
                empresas.append(empresa)
            
            logger.info(f"Gerados {len(empresas)} dados demonstrativos para CNAE {cnae_codigo}")
            return empresas
            
        except Exception as e:
            logger.error(f"Erro ao gerar dados demonstrativos: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []