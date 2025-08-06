"""
Configurações do sistema
Carrega variáveis de ambiente e define configurações padrão
"""

import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


class Settings:
    """Classe de configurações do sistema"""
    
    def __init__(self):
        # Diretórios
        self.BASE_DIR = Path(__file__).resolve().parent.parent.parent
        self.DATA_DIR = self.BASE_DIR / "data"
        self.RAW_DATA_DIR = self.DATA_DIR / "raw"
        self.PROCESSED_DATA_DIR = self.DATA_DIR / "processed"
        self.EXPORTS_DIR = self.DATA_DIR / "exports"
        self.LOGS_DIR = self.BASE_DIR / "logs"
        self.CONFIG_DIR = self.BASE_DIR / "config"
        
        # Criar diretórios se não existirem
        for directory in [self.DATA_DIR, self.RAW_DATA_DIR, self.PROCESSED_DATA_DIR, 
                         self.EXPORTS_DIR, self.LOGS_DIR, self.CONFIG_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # API Configuration
        self.RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
        self.RAPIDAPI_HOST = "cnpj-busca-empresa.p.rapidapi.com"
        self.RAPIDAPI_BASE_URL = "https://cnpj-busca-empresa.p.rapidapi.com"
        
        # Google Sheets (opcional)
        self.GOOGLE_SHEETS_CREDENTIALS_PATH = os.getenv(
            "GOOGLE_SHEETS_CREDENTIALS_PATH",
            str(self.CONFIG_DIR / "google_sheets.json")
        )
        self.GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID", "")
        
        # Nuvem Fiscal API
        self.NUVEM_FISCAL_CLIENT_ID = os.getenv("NUVEM_FISCAL_CLIENT_ID", "")
        self.NUVEM_FISCAL_CLIENT_SECRET = os.getenv("NUVEM_FISCAL_CLIENT_SECRET", "")
        self.NUVEM_FISCAL_BASE_URL = os.getenv("NUVEM_FISCAL_BASE_URL", "https://api.nuvemfiscal.com.br")
        
        # Logging
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.LOG_FILE = self.LOGS_DIR / "cnae_prospector.log"
        
        # Cache
        self.CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        self.CACHE_DIR = self.BASE_DIR / ".cache"
        self.CACHE_TTL = 3600  # 1 hora em segundos
        
        if self.CACHE_ENABLED:
            self.CACHE_DIR.mkdir(exist_ok=True)
        
        # Rate Limiting
        self.RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
        self.RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "1"))  # em segundos
        
        # Request Configuration
        self.REQUEST_TIMEOUT = 30  # segundos
        self.MAX_RETRIES = 3
        self.RETRY_DELAY = 1  # segundos
        
        # Export Configuration
        self.DEFAULT_EXPORT_FORMAT = "excel"
        self.EXCEL_MAX_ROWS = 1048576  # Limite do Excel
        self.CSV_ENCODING = "utf-8-sig"  # UTF-8 with BOM para Excel
        
        # Validação
        self.validate()
    
    def validate(self):
        """Valida as configurações essenciais"""
        # Validação mais flexível - não falha se as variáveis não estiverem configuradas
        warnings = []
        
        if not self.RAPIDAPI_KEY:
            warnings.append("RAPIDAPI_KEY não configurada - usando dados demonstrativos")
        
        if self.RAPIDAPI_KEY == "sua_chave_aqui":
            warnings.append("RAPIDAPI_KEY ainda está com o valor padrão - usando dados demonstrativos")
        
        # Apenas mostra warnings, não falha
        if warnings:
            print("⚠️ Configurações:")
            for warning in warnings:
                print(f"   {warning}")
            print("   O sistema funcionará com dados demonstrativos")
    
    def get_api_headers(self) -> dict:
        """Retorna os headers para requisições à API"""
        return {
            "X-RapidAPI-Key": self.RAPIDAPI_KEY,
            "X-RapidAPI-Host": self.RAPIDAPI_HOST
        }
    
    def get_export_path(self, filename: str, formato: str = "excel") -> Path:
        """
        Retorna o caminho completo para exportação de arquivo
        
        Args:
            filename: Nome do arquivo (sem extensão)
            formato: Formato do arquivo (excel ou csv)
            
        Returns:
            Caminho completo do arquivo
        """
        extension = ".xlsx" if formato.lower() == "excel" else ".csv"
        
        # Remover extensão se já estiver no nome
        if filename.endswith((".xlsx", ".csv", ".xls")):
            filename = Path(filename).stem
        
        return self.EXPORTS_DIR / f"{filename}{extension}"
    
    def __repr__(self):
        return (
            f"Settings(\n"
            f"  BASE_DIR={self.BASE_DIR}\n"
            f"  RAPIDAPI_KEY={'***' if self.RAPIDAPI_KEY else 'Not Set'}\n"
            f"  LOG_LEVEL={self.LOG_LEVEL}\n"
            f"  CACHE_ENABLED={self.CACHE_ENABLED}\n"
            f")"
        )