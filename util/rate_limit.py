"""
Sistema de Rate Limiting
Controla a taxa de requisições para prevenir abusos
"""

from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List
from fastapi import HTTPException, status


class RateLimiter:
    """
    Classe para controlar taxa de requisições

    Exemplo de uso:
        login_limiter = RateLimiter(max_requests=5, window_seconds=300)

        # Em uma rota:
        login_limiter.verificar(request.client.host)
    """

    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        """
        Inicializa o rate limiter

        Args:
            max_requests: Número máximo de requisições permitidas
            window_seconds: Janela de tempo em segundos
        """
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self.requests: Dict[str, List[datetime]] = defaultdict(list)

    def verificar(self, identificador: str) -> None:
        """
        Verifica se o identificador está dentro do limite de requisições

        Args:
            identificador: IP, email ou outro identificador único

        Raises:
            HTTPException: Se o limite for excedido (HTTP 429)
        """
        agora = datetime.now()

        # Limpar requisições antigas (fora da janela de tempo)
        self.requests[identificador] = [
            req_time for req_time in self.requests[identificador]
            if agora - req_time < self.window
        ]

        # Verificar se atingiu o limite
        if len(self.requests[identificador]) >= self.max_requests:
            tempo_restante = int((self.requests[identificador][0] + self.window - agora).total_seconds())

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Muitas requisições. Tente novamente em {tempo_restante} segundos."
            )

        # Adicionar requisição atual ao histórico
        self.requests[identificador].append(agora)

    def limpar(self, identificador: str) -> None:
        """
        Limpa o histórico de requisições de um identificador
        Útil após login bem-sucedido

        Args:
            identificador: IP, email ou outro identificador único
        """
        if identificador in self.requests:
            del self.requests[identificador]

    def obter_tentativas_restantes(self, identificador: str) -> int:
        """
        Retorna o número de tentativas restantes

        Args:
            identificador: IP, email ou outro identificador único

        Returns:
            Número de tentativas restantes
        """
        agora = datetime.now()

        # Limpar requisições antigas
        self.requests[identificador] = [
            req_time for req_time in self.requests[identificador]
            if agora - req_time < self.window
        ]

        return max(0, self.max_requests - len(self.requests[identificador]))


# Instâncias globais de rate limiters para diferentes casos de uso

# Rate limiter para login: 5 tentativas por 5 minutos
login_limiter = RateLimiter(max_requests=5, window_seconds=300)

# Rate limiter para cadastro: 3 tentativas por 10 minutos
cadastro_limiter = RateLimiter(max_requests=3, window_seconds=600)

# Rate limiter para recuperação de senha: 3 tentativas por 15 minutos
recuperacao_senha_limiter = RateLimiter(max_requests=3, window_seconds=900)

# Rate limiter genérico para APIs: 60 requisições por minuto
api_limiter = RateLimiter(max_requests=60, window_seconds=60)
