"""
CNAE Prospector - Sistema de Prospecção de Empresas por CNAE
Fonte principal: Nuvem Fiscal (fallback: BrasilAPI para enriquecer endereço)
"""

import os
import sys
from typing import List, Optional
from datetime import datetime
import argparse

# Adiciona o diretório pai ao path para importações
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.settings import Settings
from src.services.cnae_service import CNAEService
from src.services.empresa_service import EmpresaService
from src.exporters.excel_exporter import ExcelExporter
from src.exporters.csv_exporter import CSVExporter
from src.exporters.sheets_exporter import GoogleSheetsExporter
from src.utils.logger import setup_logger
from src.models.empresa import Empresa

# Configurar logger
logger = setup_logger(__name__)


class CNAEProspector:
    """Classe principal do sistema de prospecção"""
    
    def __init__(self):
        self.settings = Settings()
        self.cnae_service = CNAEService(self.settings)
        self.empresa_service = EmpresaService(self.settings)
        self.excel_exporter = ExcelExporter()
        self.csv_exporter = CSVExporter()
        self.sheets_exporter = GoogleSheetsExporter()
        
    def buscar_empresas_por_cnae(
        self, 
        cnae_codigo: str,
        uf: Optional[str] = None,
        cidade: Optional[str] = None,
        limite: int = 100
    ) -> List[Empresa]:
        """
        Busca empresas por código CNAE
        
        Args:
            cnae_codigo: Código CNAE para busca
            uf: Estado (opcional)
            cidade: Cidade (opcional)
            limite: Número máximo de resultados
            
        Returns:
            Lista de empresas encontradas
        """
        try:
            logger.info(f"Iniciando busca por CNAE: {cnae_codigo}")
            
            # Validar CNAE
            if not self.cnae_service.validar_cnae(cnae_codigo):
                logger.error(f"CNAE inválido: {cnae_codigo}")
                raise ValueError(f"Código CNAE inválido: {cnae_codigo}")
            
            # Buscar empresas
            empresas = self.empresa_service.buscar_por_cnae(
                cnae_codigo=cnae_codigo,
                uf=uf,
                cidade=cidade,
                limite=limite
            )
            
            logger.info(f"Encontradas {len(empresas)} empresas")
            return empresas
            
        except Exception as e:
            logger.error(f"Erro ao buscar empresas: {e}")
            raise
    
    def exportar_resultados(
        self, 
        empresas: List[Empresa], 
        formato: str = "excel",
        nome_arquivo: Optional[str] = None,
        exportar_sheets: bool = False
    ) -> str:
        """
        Exporta resultados para arquivo e/ou Google Sheets
        
        Args:
            empresas: Lista de empresas para exportar
            formato: Formato do arquivo (excel ou csv)
            nome_arquivo: Nome do arquivo (opcional)
            exportar_sheets: Se deve exportar para Google Sheets também
            
        Returns:
            Caminho do arquivo gerado ou URL do Google Sheets
        """
        try:
            caminho_arquivo = ""
            
            # Exportar para arquivo local
            if not nome_arquivo:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_arquivo = f"empresas_{timestamp}"
            
            if formato.lower() == "excel":
                caminho_arquivo = self.excel_exporter.exportar(empresas, nome_arquivo)
            elif formato.lower() == "csv":
                caminho_arquivo = self.csv_exporter.exportar(empresas, nome_arquivo)
            else:
                raise ValueError(f"Formato não suportado: {formato}")
            
            logger.info(f"Resultados exportados para: {caminho_arquivo}")
            
            # Exportar para Google Sheets se solicitado
            if exportar_sheets:
                try:
                    url_sheets = self.sheets_exporter.export_to_specific_sheet(empresas)
                    if url_sheets:
                        logger.info(f"Dados também exportados para Google Sheets: {url_sheets}")
                        return url_sheets
                    else:
                        logger.warning("Falha ao exportar para Google Sheets, retornando arquivo local")
                except Exception as e:
                    logger.error(f"Erro ao exportar para Google Sheets: {e}")
                    logger.info("Continuando com exportação local apenas")
            
            return caminho_arquivo
            
        except Exception as e:
            logger.error(f"Erro ao exportar resultados: {e}")
            raise
    
    def listar_cnaes_disponiveis(self, setor: Optional[str] = None) -> List[dict]:
        """
        Lista CNAEs disponíveis para consulta
        
        Args:
            setor: Filtrar por setor (opcional)
            
        Returns:
            Lista de CNAEs com descrições
        """
        try:
            cnaes = self.cnae_service.listar_cnaes(setor)
            logger.info(f"Listados {len(cnaes)} CNAEs")
            return cnaes
        except Exception as e:
            logger.error(f"Erro ao listar CNAEs: {e}")
            raise


def main():
    """Função principal - Interface CLI"""
    parser = argparse.ArgumentParser(
        description="CNAE Prospector - Busca empresas por CNAE"
    )
    
    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponíveis")
    
    # Comando: buscar
    buscar_parser = subparsers.add_parser("buscar", help="Buscar empresas por CNAE")
    buscar_parser.add_argument("cnae", help="Código CNAE")
    buscar_parser.add_argument("--uf", help="Filtrar por estado")
    buscar_parser.add_argument("--cidade", help="Filtrar por cidade")
    buscar_parser.add_argument("--limite", type=int, default=100, help="Limite de resultados")
    buscar_parser.add_argument("--formato", choices=["excel", "csv"], default="excel", 
                              help="Formato de exportação")
    buscar_parser.add_argument("--output", help="Nome do arquivo de saída")
    buscar_parser.add_argument("--sheets", action="store_true", 
                              help="Exportar também para Google Sheets")
    
    # Comando: listar
    listar_parser = subparsers.add_parser("listar", help="Listar CNAEs disponíveis")
    listar_parser.add_argument("--setor", help="Filtrar por setor")
    
    args = parser.parse_args()
    
    if not args.comando:
        parser.print_help()
        return
    
    # Inicializar sistema
    prospector = CNAEProspector()
    
    try:
        if args.comando == "buscar":
            # Buscar empresas
            print(f"\n🔍 Buscando empresas com CNAE {args.cnae}...")
            empresas = prospector.buscar_empresas_por_cnae(
                cnae_codigo=args.cnae,
                uf=args.uf,
                cidade=args.cidade,
                limite=args.limite
            )
            
            if empresas:
                # Exportar resultados
                print(f"✅ Encontradas {len(empresas)} empresas")
                print(f"📁 Exportando para {args.formato}...")
                
                arquivo = prospector.exportar_resultados(
                    empresas=empresas,
                    formato=args.formato,
                    nome_arquivo=args.output,
                    exportar_sheets=args.sheets
                )
                
                print(f"✅ Arquivo salvo em: {arquivo}")
            else:
                print("❌ Nenhuma empresa encontrada")
                
        elif args.comando == "listar":
            # Listar CNAEs
            print("\n📋 CNAEs disponíveis:")
            cnaes = prospector.listar_cnaes_disponiveis(args.setor)
            
            for cnae in cnaes:
                print(f"  • {cnae['codigo']} - {cnae['descricao']}")
            
            print(f"\nTotal: {len(cnaes)} CNAEs")
            
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        logger.error(f"Erro na execução: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()