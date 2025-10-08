import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

def configurar_logger():
    """Configura sistema de logging profissional"""
    # Criar pasta de logs se não existir
    Path("logs").mkdir(exist_ok=True)

    # Configurar formato
    formato = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler para arquivo com rotação
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formato)

    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formato)

    # Configurar logger raiz
    logger = logging.getLogger()
    nivel = os.getenv('LOG_LEVEL', 'INFO')
    logger.setLevel(getattr(logging, nivel))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Logger global para importação
logger = configurar_logger()
