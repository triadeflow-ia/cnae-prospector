"""
Classe base para exportadores de dados
"""

import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from loguru import logger

from ..models.empresa import Empresa
from ..config.settings import get_settings


class BaseExporter(ABC):
    """Classe base para exportadores de dados"""
    
    def __init__(self):
        self.settings = get_settings()
        self.export_path = self.settings.export_path
        
        # Cria o diretório de exportação se não existir
        os.makedirs(self.export_path, exist_ok=True)
    
    @abstractmethod
    def export(self, empresas: List[Empresa], filename: str = None) -> str:
        """
        Exporta a lista de empresas para um arquivo
        
        Args:
            empresas: Lista de empresas para exportar
            filename: Nome do arquivo (opcional)
            
        Returns:
            Caminho do arquivo exportado
        """
        pass
    
    def _get_filename(self, base_name: str = None) -> str:
        """Gera um nome de arquivo único"""
        import datetime
        
        if base_name is None:
            base_name = "empresas"
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp}"
    
    def _prepare_data(self, empresas: List[Empresa]) -> List[Dict[str, Any]]:
        """Prepara os dados das empresas para exportação"""
        data = []
        
        for empresa in empresas:
            row = {
                "CNPJ": empresa.cnpj,
                "Razão Social": empresa.razao_social,
                "Nome Fantasia": empresa.nome_fantasia,
                "Data Abertura": empresa.data_abertura,
                "Situação": empresa.situacao,
                "Tipo": empresa.tipo,
                "Porte": empresa.porte,
                "Natureza Jurídica": empresa.natureza_juridica,
                "Capital Social": empresa.capital_social,
                "Telefone": empresa.telefone,
                "Email": empresa.email,
                "Site": empresa.site,
                "Data Última Atualização": empresa.data_ultima_atualizacao,
            }
            
            # Adiciona dados do endereço
            if empresa.endereco:
                row.update({
                    "Logradouro": empresa.endereco.logradouro,
                    "Número": empresa.endereco.numero,
                    "Complemento": empresa.endereco.complemento,
                    "Bairro": empresa.endereco.bairro,
                    "Cidade": empresa.endereco.cidade,
                    "UF": empresa.endereco.uf,
                    "CEP": empresa.endereco.cep,
                    "Município": empresa.endereco.municipio,
                })
            
            # Adiciona dados do CNAE
            if empresa.cnae:
                row.update({
                    "CNAE Código": empresa.cnae.codigo,
                    "CNAE Descrição": empresa.cnae.descricao,
                })
            
            data.append(row)
        
        return data
    
    def _validate_export_path(self, filepath: str) -> str:
        """Valida e cria o caminho de exportação se necessário"""
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Diretório criado: {directory}")
        
        return filepath 