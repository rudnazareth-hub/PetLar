import logging
from logging.handlers import TimedRotatingFileHandler
import os
from pathlib import Path

def configurar_logger():
    """Configura sistema de logging profissional com rotação diária"""
    # Criar pasta de logs se não existir
    Path("logs").mkdir(exist_ok=True)

    # Configurar formato
    formato = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Obter configuração de retenção de logs (padrão: 30 dias)
    retention_days = int(os.getenv('LOG_RETENTION_DAYS', '30'))

    # Handler para arquivo com rotação diária
    file_handler = TimedRotatingFileHandler(
        'logs/app.log',
        when='midnight',           # Rotaciona à meia-noite
        interval=1,                # A cada 1 dia
        backupCount=retention_days # Mantém N dias de histórico
    )
    file_handler.suffix = '%Y-%m-%d'  # Formato do sufixo: app.log.2025-10-15
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
