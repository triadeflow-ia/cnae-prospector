"""
Configuração de logging para o sistema
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

# Importar configurações
from src.config.settings import Settings


def setup_logger(
    name: str = "cnae_prospector",
    level: Optional[str] = None,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Configura e retorna um logger
    
    Args:
        name: Nome do logger
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Caminho do arquivo de log
        
    Returns:
        Logger configurado
    """
    settings = Settings()
    
    # Configurar nível de log
    if not level:
        level = settings.LOG_LEVEL
    
    # Configurar arquivo de log
    if not log_file:
        log_file = settings.LOG_FILE
    
    # Criar logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Evitar duplicação de handlers
    if logger.handlers:
        return logger
    
    # Formato do log
    formatter = logging.Formatter(settings.LOG_FORMAT)
    
    # Handler para arquivo com rotação
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, level.upper()))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Formato mais simples para console
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


# Logger padrão do módulo
logger = setup_logger(__name__)