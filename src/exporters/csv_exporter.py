"""
Exportador para CSV
"""

import csv
from typing import List, Optional
from pathlib import Path
from datetime import datetime

from src.config.settings import Settings
from src.models.empresa import Empresa
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class CSVExporter:
    """Exportador de dados para CSV"""
    
    def __init__(self):
        self.settings = Settings()
    
    def exportar(
        self,
        empresas: List[Empresa],
        nome_arquivo: Optional[str] = None,
        separador: str = ",",
        encoding: Optional[str] = None
    ) -> str:
        """
        Exporta lista de empresas para CSV formatado para CRM
        
        Args:
            empresas: Lista de empresas para exportar
            nome_arquivo: Nome do arquivo (opcional)
            separador: Caractere separador (padrão vírgula)
            encoding: Encoding do arquivo (padrão UTF-8 com BOM)
            
        Returns:
            Caminho do arquivo gerado
        """
        try:
            if not empresas:
                logger.warning("Nenhuma empresa para exportar")
                raise ValueError("Lista de empresas vazia")
            
            # Definir nome do arquivo
            if not nome_arquivo:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_arquivo = f"prospeccao_cnae_{timestamp}"
            
            # Obter caminho completo
            arquivo_path = self.settings.get_export_path(nome_arquivo, "csv")
            
            # Definir encoding
            if not encoding:
                encoding = self.settings.CSV_ENCODING
            
            logger.info(f"Exportando {len(empresas)} empresas para CSV")
            
            # Escrever arquivo CSV
            with open(arquivo_path, 'w', newline='', encoding=encoding) as csvfile:
                # Definir campos organizados para CRM
                fieldnames = [
                    # Identificação da Empresa
                    "CNPJ",
                    "Razão Social", 
                    "Nome Fantasia",
                    "Status",
                    
                    # Informações Comerciais
                    "Setor (CNAE)",
                    "Atividade Principal",
                    "Porte Empresa",
                    "Data Abertura",
                    
                    # Contatos
                    "Telefone Principal",
                    "Email Contato",
                    
                    # Endereço Completo
                    "Endereço Completo",
                    "Rua",
                    "Número",
                    "Bairro",
                    "Cidade",
                    "Estado (UF)",
                    "CEP",
                    
                    # Informações Adicionais
                    "Capital Social",
                    "Website",
                    "Telefone Validado",
                    "Validação Telefone",
                    "Email Validação",
                    "Email Sugestão",
                    "Empresa Tamanho",
                    "Empresa Indústria",
                    "LinkedIn",
                    "Twitter",
                    "Facebook",
                    "Instagram",
                    "Domain Confidence",
                    "Domain Source",
                    "Fonte dos Dados",
                    "Data da Consulta",
                    
                    # Campos para CRM
                    "Lead Score",
                    "Observações",
                    "Responsável",
                    "Status Contato"
                ]
                
                writer = csv.DictWriter(
                    csvfile,
                    fieldnames=fieldnames,
                    delimiter=separador
                )
                
                # Escrever cabeçalho
                writer.writeheader()
                
                # Escrever dados
                for empresa in empresas:
                    row = self._empresa_to_crm_row(empresa)
                    writer.writerow(row)
            
            logger.info(f"Arquivo CSV criado: {arquivo_path}")
            return str(arquivo_path)
            
        except Exception as e:
            logger.error(f"Erro ao exportar para CSV: {e}")
            raise
    
    def _empresa_to_csv_row(self, empresa: Empresa) -> dict:
        """
        Converte empresa para linha CSV
        
        Args:
            empresa: Empresa para converter
            
        Returns:
            Dicionário com dados da empresa
        """
        row = {
            "CNPJ": empresa.cnpj_formatado,
            "Razão Social": empresa.razao_social,
            "Nome Fantasia": empresa.nome_fantasia or "",
            "Situação": empresa.situacao_cadastral or "",
            "Data Abertura": empresa.data_abertura.strftime("%d/%m/%Y") if empresa.data_abertura else "",
            "Porte": empresa.porte or "",
            "Capital Social": empresa.capital_social_formatado,
            "CNAE Principal": empresa.cnae_principal.codigo if empresa.cnae_principal else "",
            "CNAE Principal Descrição": empresa.cnae_principal.descricao if empresa.cnae_principal else "",
            "Telefone": empresa.telefone_formatado,
            "Email": empresa.email or "",
        }
        
        # Adicionar campos de endereço
        if empresa.endereco:
            row.update({
                "Logradouro": empresa.endereco.logradouro or "",
                "Número": empresa.endereco.numero or "",
                "Complemento": empresa.endereco.complemento or "",
                "Bairro": empresa.endereco.bairro or "",
                "Cidade": empresa.endereco.cidade or "",
                "UF": empresa.endereco.uf or "",
                "CEP": empresa.endereco.cep or ""
            })
        else:
            row.update({
                "Logradouro": "",
                "Número": "",
                "Complemento": "",
                "Bairro": "",
                "Cidade": "",
                "UF": "",
                "CEP": ""
            })
        
        return row
    
    def _empresa_to_crm_row(self, empresa: Empresa) -> dict:
        """
        Converte empresa para linha CSV formatada para CRM
        
        Args:
            empresa: Empresa para converter
            
        Returns:
            Dicionário com dados formatados para CRM
        """
        # Montar endereço completo
        endereco_completo = ""
        if empresa.endereco:
            partes_endereco = []
            if empresa.endereco.logradouro:
                partes_endereco.append(empresa.endereco.logradouro)
            if empresa.endereco.numero:
                partes_endereco.append(f"nº {empresa.endereco.numero}")
            if empresa.endereco.bairro:
                partes_endereco.append(empresa.endereco.bairro)
            if empresa.endereco.cidade and empresa.endereco.uf:
                partes_endereco.append(f"{empresa.endereco.cidade}/{empresa.endereco.uf}")
            if empresa.endereco.cep:
                partes_endereco.append(f"CEP: {empresa.endereco.cep}")
            
            endereco_completo = ", ".join(partes_endereco)
        
        # Definir lead score baseado em critérios
        lead_score = self._calcular_lead_score(empresa)
        
        row = {
            # Identificação da Empresa
            "CNPJ": empresa.cnpj_formatado,
            "Razão Social": empresa.razao_social,
            "Nome Fantasia": empresa.nome_fantasia or empresa.razao_social,
            "Status": empresa.situacao_cadastral or "ATIVA",
            
            # Informações Comerciais
            "Setor (CNAE)": empresa.cnae_principal.codigo if empresa.cnae_principal else "",
            "Atividade Principal": empresa.cnae_principal.descricao if empresa.cnae_principal else "",
            "Porte Empresa": empresa.porte or "Não informado",
            "Data Abertura": empresa.data_abertura.strftime("%d/%m/%Y") if empresa.data_abertura else "",
            
            # Contatos
            "Telefone Principal": empresa.telefone_formatado,
            "Email Contato": empresa.email or "",
            
            # Endereço Completo
            "Endereço Completo": endereco_completo,
            "Rua": empresa.endereco.logradouro if empresa.endereco else "",
            "Número": empresa.endereco.numero if empresa.endereco else "",
            "Bairro": empresa.endereco.bairro if empresa.endereco else "",
            "Cidade": empresa.endereco.cidade if empresa.endereco else "",
            "Estado (UF)": empresa.endereco.uf if empresa.endereco else "",
            "CEP": empresa.endereco.cep if empresa.endereco else "",
            
            # Informações Adicionais
            "Capital Social": empresa.capital_social_formatado,
            "Website": getattr(empresa, 'website', ''),
            "Telefone Validado": getattr(empresa, 'telefone_validado', ''),
            "Validação Telefone": getattr(empresa, 'validacao_telefone', ''),
            "Email Validação": getattr(empresa, 'email_validacao', ''),
            "Email Sugestão": getattr(empresa, 'email_sugestao', ''),
            "Empresa Tamanho": getattr(empresa, 'empresa_tamanho', ''),
            "Empresa Indústria": getattr(empresa, 'empresa_industria', ''),
            "LinkedIn": getattr(empresa, 'empresa_linkedin', ''),
            "Twitter": getattr(empresa, 'empresa_twitter', ''),
            "Facebook": getattr(empresa, 'empresa_facebook', ''),
            "Instagram": getattr(empresa, 'empresa_instagram', ''),
            "Domain Confidence": getattr(empresa, 'domain_confidence', ''),
            "Domain Source": getattr(empresa, 'domain_source', ''),
            "Fonte dos Dados": getattr(empresa, 'fonte', 'CNAE Prospector'),
            "Data da Consulta": datetime.now().strftime("%d/%m/%Y %H:%M"),
            
            # Campos para CRM (vazios para preenchimento manual)
            "Lead Score": lead_score,
            "Observações": "",
            "Responsável": "",
            "Status Contato": "Não contatado"
        }
        
        return row
    
    def _calcular_lead_score(self, empresa: Empresa) -> str:
        """
        Calcula um lead score básico para a empresa
        
        Args:
            empresa: Empresa para analisar
            
        Returns:
            Score de 1-10 com classificação
        """
        score = 5  # Score base
        
        # Critérios para aumentar o score
        if empresa.situacao_cadastral == "ATIVA":
            score += 2
        
        if empresa.email:
            score += 1
            
        if empresa.telefone:
            score += 1
            
        if empresa.porte in ["MICRO EMPRESA", "PEQUENA EMPRESA"]:
            score += 1  # Mais fáceis de abordar
            
        # Limitar entre 1 e 10
        score = max(1, min(10, score))
        
        # Classificar o score
        if score >= 8:
            return f"{score}/10 - Alto Potencial"
        elif score >= 6:
            return f"{score}/10 - Médio Potencial"
        else:
            return f"{score}/10 - Baixo Potencial"
    
    def exportar_cnaes_secundarios(
        self,
        empresas: List[Empresa],
        nome_arquivo: Optional[str] = None
    ) -> str:
        """
        Exporta CNAEs secundários para CSV
        
        Args:
            empresas: Lista de empresas
            nome_arquivo: Nome do arquivo
            
        Returns:
            Caminho do arquivo gerado
        """
        try:
            if not nome_arquivo:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_arquivo = f"cnaes_secundarios_{timestamp}"
            
            arquivo_path = self.settings.get_export_path(nome_arquivo, "csv")
            
            with open(arquivo_path, 'w', newline='', encoding=self.settings.CSV_ENCODING) as csvfile:
                fieldnames = ["CNPJ", "Razão Social", "CNAE Código", "CNAE Descrição"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                
                for empresa in empresas:
                    for cnae in empresa.cnaes_secundarios:
                        writer.writerow({
                            "CNPJ": empresa.cnpj_formatado,
                            "Razão Social": empresa.razao_social,
                            "CNAE Código": cnae.codigo,
                            "CNAE Descrição": cnae.descricao
                        })
            
            logger.info(f"CNAEs secundários exportados: {arquivo_path}")
            return str(arquivo_path)
            
        except Exception as e:
            logger.error(f"Erro ao exportar CNAEs secundários: {e}")
            raise
    
    def exportar_socios(
        self,
        empresas: List[Empresa],
        nome_arquivo: Optional[str] = None
    ) -> str:
        """
        Exporta sócios para CSV
        
        Args:
            empresas: Lista de empresas
            nome_arquivo: Nome do arquivo
            
        Returns:
            Caminho do arquivo gerado
        """
        try:
            if not nome_arquivo:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_arquivo = f"socios_{timestamp}"
            
            arquivo_path = self.settings.get_export_path(nome_arquivo, "csv")
            
            with open(arquivo_path, 'w', newline='', encoding=self.settings.CSV_ENCODING) as csvfile:
                fieldnames = [
                    "CNPJ Empresa", "Razão Social", "Nome Sócio",
                    "Qualificação", "País Origem", "Nome Representante",
                    "Qualificação Representante"
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                
                for empresa in empresas:
                    for socio in empresa.socios:
                        writer.writerow({
                            "CNPJ Empresa": empresa.cnpj_formatado,
                            "Razão Social": empresa.razao_social,
                            "Nome Sócio": socio.get("nome", ""),
                            "Qualificação": socio.get("qual", ""),
                            "País Origem": socio.get("pais_origem", ""),
                            "Nome Representante": socio.get("nome_rep_legal", ""),
                            "Qualificação Representante": socio.get("qual_rep_legal", "")
                        })
            
            logger.info(f"Sócios exportados: {arquivo_path}")
            return str(arquivo_path)
            
        except Exception as e:
            logger.error(f"Erro ao exportar sócios: {e}")
            raise
    
    def exportar_para_importacao(
        self,
        empresas: List[Empresa],
        nome_arquivo: Optional[str] = None,
        formato: str = "salesforce"
    ) -> str:
        """
        Exporta dados em formato específico para importação em outros sistemas
        
        Args:
            empresas: Lista de empresas
            nome_arquivo: Nome do arquivo
            formato: Formato de saída (salesforce, hubspot, etc)
            
        Returns:
            Caminho do arquivo gerado
        """
        try:
            if not nome_arquivo:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_arquivo = f"importacao_{formato}_{timestamp}"
            
            arquivo_path = self.settings.get_export_path(nome_arquivo, "csv")
            
            if formato.lower() == "salesforce":
                fieldnames = [
                    "Account Name", "Phone", "Website", "Industry",
                    "Billing Street", "Billing City", "Billing State",
                    "Billing Postal Code", "Description"
                ]
                
                with open(arquivo_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for empresa in empresas:
                        writer.writerow({
                            "Account Name": empresa.razao_social,
                            "Phone": empresa.telefone or "",
                            "Website": "",
                            "Industry": empresa.cnae_principal.descricao if empresa.cnae_principal else "",
                            "Billing Street": f"{empresa.endereco.logradouro}, {empresa.endereco.numero}" if empresa.endereco else "",
                            "Billing City": empresa.endereco.cidade if empresa.endereco else "",
                            "Billing State": empresa.endereco.uf if empresa.endereco else "",
                            "Billing Postal Code": empresa.endereco.cep if empresa.endereco else "",
                            "Description": f"CNPJ: {empresa.cnpj_formatado} | Porte: {empresa.porte or 'N/A'}"
                        })
            
            else:
                # Formato padrão
                return self.exportar(empresas, nome_arquivo)
            
            logger.info(f"Arquivo para importação criado: {arquivo_path}")
            return str(arquivo_path)
            
        except Exception as e:
            logger.error(f"Erro ao exportar para importação: {e}")
            raise