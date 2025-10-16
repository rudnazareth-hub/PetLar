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
    file_handler.suffix = '%Y.%m.%d'  # Formato do sufixo com pontos

    # Função para customizar o nome do arquivo rotacionado
    def namer(default_name):
        """Converte logs/app.log.2025.10.25 para logs/app.2025.10.25.log"""
        dir_name, base_name = os.path.split(default_name)
        # Remove o '.log' do meio e adiciona no final
        parts = base_name.split('.log.')
        if len(parts) == 2:
            new_name = f"app.{parts[1]}.log"
            return os.path.join(dir_name, new_name)
        return default_name

    file_handler.namer = namer
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
