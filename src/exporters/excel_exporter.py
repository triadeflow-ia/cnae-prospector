"""
Exportador para Excel
"""

import pandas as pd
from typing import List, Optional
from pathlib import Path
from datetime import datetime

try:
    import xlsxwriter  # noqa: F401
    DEFAULT_EXCEL_ENGINE = 'xlsxwriter'
except Exception:
    # Fallback: openpyxl (sem formatação avançada)
    DEFAULT_EXCEL_ENGINE = 'openpyxl'

from src.config.settings import Settings
from src.models.empresa import Empresa
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ExcelExporter:
    """Exportador de dados para Excel"""
    
    def __init__(self):
        self.settings = Settings()
    
    def exportar(
        self,
        empresas: List[Empresa],
        nome_arquivo: Optional[str] = None,
        incluir_socios: bool = False
    ) -> str:
        """
        Exporta lista de empresas para Excel
        
        Args:
            empresas: Lista de empresas para exportar
            nome_arquivo: Nome do arquivo (opcional)
            incluir_socios: Se deve incluir aba com sócios
            
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
                nome_arquivo = f"empresas_{timestamp}"
            
            # Obter caminho completo
            arquivo_path = self.settings.get_export_path(nome_arquivo, "excel")
            
            logger.info(f"Exportando {len(empresas)} empresas para Excel")
            
            # Criar writer do Excel (tenta xlsxwriter, senão openpyxl)
            engine = DEFAULT_EXCEL_ENGINE
            with pd.ExcelWriter(arquivo_path, engine=engine) as writer:
                # Aba principal com dados das empresas
                self._exportar_empresas(empresas, writer)
                
                # Aba com CNAEs secundários (se houver)
                self._exportar_cnaes_secundarios(empresas, writer)
                
                # Aba com sócios (se solicitado)
                if incluir_socios:
                    self._exportar_socios(empresas, writer)
                
                # Adicionar formatação (somente quando usar xlsxwriter)
                self._aplicar_formatacao(writer, engine)
            
            logger.info(f"Arquivo Excel criado: {arquivo_path}")
            return str(arquivo_path)
            
        except Exception as e:
            logger.error(f"Erro ao exportar para Excel: {e}")
            raise
    
    def _exportar_empresas(self, empresas: List[Empresa], writer):
        """Exporta dados principais das empresas"""
        # Converter empresas para lista de dicionários
        dados = [empresa.to_excel_row() for empresa in empresas]
        
        # Criar DataFrame
        df = pd.DataFrame(dados)
        
        # Reordenar colunas se necessário
        colunas_ordem = [
            "CNPJ", "Razão Social", "Nome Fantasia", "Situação",
            "Data Abertura", "Porte", "Capital Social", "CNAE Principal",
            "Telefone", "Email", "Logradouro", "Número", "Complemento",
            "Bairro", "Cidade", "UF", "CEP"
        ]
        
        # Garantir que todas as colunas existam
        for col in colunas_ordem:
            if col not in df.columns:
                df[col] = ""
        
        # Reordenar
        df = df[colunas_ordem]
        
        # Escrever no Excel
        df.to_excel(writer, sheet_name="Empresas", index=False)
        
        logger.debug(f"Exportadas {len(df)} linhas na aba 'Empresas'")
    
    def _exportar_cnaes_secundarios(self, empresas: List[Empresa], writer):
        """Exporta CNAEs secundários das empresas"""
        dados_cnaes = []
        
        for empresa in empresas:
            for cnae in empresa.cnaes_secundarios:
                dados_cnaes.append({
                    "CNPJ": empresa.cnpj_formatado,
                    "Razão Social": empresa.razao_social,
                    "CNAE Código": cnae.codigo,
                    "CNAE Descrição": cnae.descricao
                })
        
        if dados_cnaes:
            df_cnaes = pd.DataFrame(dados_cnaes)
            df_cnaes.to_excel(writer, sheet_name="CNAEs Secundários", index=False)
            logger.debug(f"Exportados {len(df_cnaes)} CNAEs secundários")
    
    def _exportar_socios(self, empresas: List[Empresa], writer):
        """Exporta sócios das empresas"""
        dados_socios = []
        
        for empresa in empresas:
            for socio in empresa.socios:
                dados_socios.append({
                    "CNPJ Empresa": empresa.cnpj_formatado,
                    "Razão Social": empresa.razao_social,
                    "Nome Sócio": socio.get("nome", ""),
                    "Qualificação": socio.get("qual", ""),
                    "País Origem": socio.get("pais_origem", ""),
                    "Nome Representante": socio.get("nome_rep_legal", ""),
                    "Qualificação Representante": socio.get("qual_rep_legal", "")
                })
        
        if dados_socios:
            df_socios = pd.DataFrame(dados_socios)
            df_socios.to_excel(writer, sheet_name="Sócios", index=False)
            logger.debug(f"Exportados {len(df_socios)} sócios")
    
    def _aplicar_formatacao(self, writer, engine: str):
        """Aplica formatação ao arquivo Excel"""
        # Somente xlsxwriter suporta as formatações abaixo
        if engine != 'xlsxwriter':
            return
        try:
            workbook = writer.book
            
            # Formato para cabeçalho
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BD',
                'border': 1
            })
            
            # Formato para moeda
            money_format = workbook.add_format({
                'num_format': 'R$ #,##0.00'
            })
            
            # Formato para data
            date_format = workbook.add_format({
                'num_format': 'dd/mm/yyyy'
            })
            
            # Aplicar formatação em cada aba
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                
                # Ajustar largura das colunas
                worksheet.set_column('A:A', 20)  # CNPJ
                worksheet.set_column('B:B', 40)  # Razão Social
                worksheet.set_column('C:C', 30)  # Nome Fantasia
                worksheet.set_column('D:D', 15)  # Situação
                worksheet.set_column('E:E', 12)  # Data
                worksheet.set_column('F:F', 15)  # Porte
                worksheet.set_column('G:G', 18)  # Capital Social
                worksheet.set_column('H:H', 50)  # CNAE
                worksheet.set_column('I:I', 15)  # Telefone
                worksheet.set_column('J:J', 30)  # Email
                worksheet.set_column('K:Q', 20)  # Endereço
                
                # Congelar primeira linha
                worksheet.freeze_panes(1, 0)
                
                # Adicionar filtros
                worksheet.autofilter(0, 0, 1000, 20)
                
        except Exception as e:
            logger.warning(f"Erro ao aplicar formatação: {e}")
    
    def exportar_resumo(
        self,
        empresas: List[Empresa],
        nome_arquivo: Optional[str] = None
    ) -> str:
        """
        Exporta resumo estatístico das empresas
        
        Args:
            empresas: Lista de empresas
            nome_arquivo: Nome do arquivo
            
        Returns:
            Caminho do arquivo gerado
        """
        try:
            if not nome_arquivo:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_arquivo = f"resumo_empresas_{timestamp}"
            
            arquivo_path = self.settings.get_export_path(nome_arquivo, "excel")
            
            engine = DEFAULT_EXCEL_ENGINE
            with pd.ExcelWriter(arquivo_path, engine=engine) as writer:
                # Estatísticas por UF
                self._exportar_estatisticas_uf(empresas, writer)
                
                # Estatísticas por porte
                self._exportar_estatisticas_porte(empresas, writer)
                
                # Estatísticas por CNAE
                self._exportar_estatisticas_cnae(empresas, writer)
            
            logger.info(f"Resumo exportado: {arquivo_path}")
            return str(arquivo_path)
            
        except Exception as e:
            logger.error(f"Erro ao exportar resumo: {e}")
            raise
    
    def _exportar_estatisticas_uf(self, empresas: List[Empresa], writer):
        """Exporta estatísticas por UF"""
        stats = {}
        
        for empresa in empresas:
            if empresa.endereco and empresa.endereco.uf:
                uf = empresa.endereco.uf
                if uf not in stats:
                    stats[uf] = 0
                stats[uf] += 1
        
        if stats:
            df = pd.DataFrame(
                list(stats.items()),
                columns=["UF", "Quantidade"]
            ).sort_values("Quantidade", ascending=False)
            
            df.to_excel(writer, sheet_name="Por UF", index=False)
    
    def _exportar_estatisticas_porte(self, empresas: List[Empresa], writer):
        """Exporta estatísticas por porte"""
        stats = {}
        
        for empresa in empresas:
            porte = empresa.porte or "Não informado"
            if porte not in stats:
                stats[porte] = 0
            stats[porte] += 1
        
        if stats:
            df = pd.DataFrame(
                list(stats.items()),
                columns=["Porte", "Quantidade"]
            ).sort_values("Quantidade", ascending=False)
            
            df.to_excel(writer, sheet_name="Por Porte", index=False)
    
    def _exportar_estatisticas_cnae(self, empresas: List[Empresa], writer):
        """Exporta estatísticas por CNAE"""
        stats = {}
        
        for empresa in empresas:
            if empresa.cnae_principal:
                cnae = f"{empresa.cnae_principal.codigo} - {empresa.cnae_principal.descricao}"
                if cnae not in stats:
                    stats[cnae] = 0
                stats[cnae] += 1
        
        if stats:
            df = pd.DataFrame(
                list(stats.items()),
                columns=["CNAE", "Quantidade"]
            ).sort_values("Quantidade", ascending=False)
            
            df.to_excel(writer, sheet_name="Por CNAE", index=False)