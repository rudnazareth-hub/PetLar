import os
import requests
from typing import Optional
from util.logger_config import logger

class EmailService:
    def __init__(self):
        self.api_key = os.getenv('MAILERSEND_API_KEY')
        self.from_email = os.getenv('MAILERSEND_FROM_EMAIL', 'noreply@seudominio.com')
        self.from_name = os.getenv('MAILERSEND_FROM_NAME', 'Sistema')
        self.base_url = "https://api.mailersend.com/v1/email"

    def enviar_email(
        self,
        para_email: str,
        para_nome: str,
        assunto: str,
        html: str,
        texto: Optional[str] = None
    ) -> bool:
        """Envia e-mail via MailerSend"""
        if not self.api_key:
            logger.warning("MAILERSEND_API_KEY não configurada")
            return False

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "from": {
                "email": self.from_email,
                "name": self.from_name
            },
            "to": [
                {
                    "email": para_email,
                    "name": para_nome
                }
            ],
            "subject": assunto,
            "html": html,
            "text": texto or assunto
        }

        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info(f"E-mail enviado para {para_email}")
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail: {e}")
            return False

    def enviar_recuperacao_senha(self, para_email: str, para_nome: str, token: str) -> bool:
        """Envia e-mail de recuperação de senha"""
        url_recuperacao = f"{os.getenv('BASE_URL', 'http://localhost:8000')}/redefinir-senha?token={token}"

        html = f"""
        <html>
        <body>
            <h2>Recuperação de Senha</h2>
            <p>Olá {para_nome},</p>
            <p>Você solicitou a recuperação de senha.</p>
            <p>Clique no link abaixo para redefinir sua senha:</p>
            <a href="{url_recuperacao}">Redefinir Senha</a>
            <p>Este link expira em 1 hora.</p>
            <p>Se você não solicitou esta recuperação, ignore este e-mail.</p>
        </body>
        </html>
        """

        return self.enviar_email(
            para_email=para_email,
            para_nome=para_nome,
            assunto="Recuperação de Senha",
            html=html
        )

    def enviar_boas_vindas(self, para_email: str, para_nome: str) -> bool:
        """Envia e-mail de boas-vindas"""
        html = f"""
        <html>
        <body>
            <h2>Bem-vindo(a)!</h2>
            <p>Olá {para_nome},</p>
            <p>Seu cadastro foi realizado com sucesso!</p>
            <p>Agora você pode acessar o sistema com seu e-mail e senha.</p>
        </body>
        </html>
        """

        return self.enviar_email(
            para_email=para_email,
            para_nome=para_nome,
            assunto="Bem-vindo ao Sistema",
            html=html
        )

# Instância global
email_service = EmailService()
