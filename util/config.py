"""
Módulo de configurações centralizadas da aplicação.

Carrega e disponibiliza todas as variáveis de ambiente e configurações
do sistema em um único local, facilitando a manutenção e evitando duplicação.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# === Configurações da Aplicação ===
APP_NAME = os.getenv("APP_NAME", "Sistema Web")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
SECRET_KEY = os.getenv("SECRET_KEY", "sua-chave-secreta-super-segura-mude-isso-em-producao")

# === Configurações do Banco de Dados ===
DATABASE_PATH = os.getenv("DATABASE_PATH", "database.db")

# === Configurações de Logging ===
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# === Configurações de Email (Resend.com) ===
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "noreply@seudominio.com")
RESEND_FROM_NAME = os.getenv("RESEND_FROM_NAME", APP_NAME)

# === Configurações do Servidor ===
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
RELOAD = os.getenv("RELOAD", "True").lower() == "true"

# === Versão da Aplicação ===
VERSION = "1.0.0"
