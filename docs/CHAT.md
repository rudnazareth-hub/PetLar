# Sistema de Chat em Tempo Real com SSE

## 📋 Visão Geral

Este documento fornece um guia completo e detalhado para implementar um sistema de **chat em tempo real** no DefaultWebApp usando **Server-Sent Events (SSE)** para recebimento de mensagens e **HTTP POST** para envio.

### Por que SSE + HTTP POST?

**Server-Sent Events (SSE)** é uma tecnologia nativa do navegador que permite ao servidor enviar atualizações em tempo real para o cliente através de uma conexão HTTP de longa duração. É ideal para o DefaultWebApp porque:

- ✅ **Simplicidade**: Usa HTTP padrão, integração direta com FastAPI
- ✅ **Compatibilidade**: 98% de suporte em navegadores, funciona com firewalls corporativos
- ✅ **Arquitetura HTTP**: Funciona perfeitamente com session-based auth existente
- ✅ **Reconexão Automática**: EventSource reconecta automaticamente se cair
- ✅ **Debugging**: Mensagens visíveis no Network tab do DevTools
- ✅ **Infraestrutura**: Não requer configuração especial de load balancer

**Limitação**: SSE é unidirecional (servidor → cliente). Por isso, usamos **HTTP POST** padrão para enviar mensagens (cliente → servidor). Esta combinação é perfeita para chat.

### Arquitetura de Alto Nível

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Navegador)                      │
│  ┌──────────────────┐              ┌─────────────────────────┐  │
│  │  EventSource     │              │   fetch() POST          │  │
│  │  /chat/stream    │◄─────────────┤   /chat/enviar          │  │
│  │  (recebe msgs)   │              │   (envia msgs)          │  │
│  └────────┬─────────┘              └───────────┬─────────────┘  │
│           │                                     │                │
│           │ SSE (Server → Client)               │ HTTP POST      │
│           │                                     │                │
└───────────┼─────────────────────────────────────┼────────────────┘
            │                                     │
            ▼                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                           │
│  ┌──────────────────┐              ┌─────────────────────────┐  │
│  │  GET /stream     │              │   POST /enviar          │  │
│  │  yield mensagens │              │   salva + notifica      │  │
│  │  (SSE endpoint)  │◄─────────────┤   todas as conexões     │  │
│  └────────┬─────────┘              └───────────┬─────────────┘  │
│           │                                     │                │
│           │                                     │                │
│           ▼                                     ▼                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            ChatManager (util/chat_manager.py)             │   │
│  │  - Gerencia conexões SSE ativas (Queue por usuário)      │   │
│  │  - Notifica novas mensagens para conexões ativas          │   │
│  │  - Controla timeouts e cleanup                            │   │
│  └────────────────────┬──────────────────────────────────────┘   │
│                       │                                          │
│                       ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         Repository (repo/chat_mensagem_repo.py)           │   │
│  │  - inserir(), obter_mensagens_sala(), marcar_lida()      │   │
│  └────────────────────┬──────────────────────────────────────┘   │
│                       │                                          │
│                       ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                SQLite Database (database.db)              │   │
│  │  Tabela: chat_mensagem                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Fluxo de Dados

**1. Conexão SSE (Receber Mensagens)**
```
Usuário acessa sala → EventSource conecta em /chat/stream?sala_id=X
→ Backend registra conexão no ChatManager
→ Enquanto conectado, servidor envia novas mensagens via SSE
→ Frontend recebe eventos e atualiza UI
```

**2. Envio de Mensagem (HTTP POST)**
```
Usuário digita mensagem → fetch POST /chat/enviar
→ Backend valida com DTO → Salva no banco via Repository
→ ChatManager notifica TODAS as conexões ativas da sala
→ EventSource de todos recebe a mensagem
→ UI atualiza em tempo real
```

---

## 🗄️ Camada 1: Banco de Dados

### SQL Schema (`sql/chat_mensagem_sql.py`)

```python
"""
Queries SQL para o sistema de chat em tempo real.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS chat_mensagem (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sala_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    mensagem TEXT NOT NULL,
    data_envio TIMESTAMP NOT NULL,
    lida INTEGER DEFAULT 0,

    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
)
"""

# Índices para otimização de queries
CRIAR_INDICES = """
CREATE INDEX IF NOT EXISTS idx_chat_sala_data
ON chat_mensagem(sala_id, data_envio DESC);

CREATE INDEX IF NOT EXISTS idx_chat_usuario
ON chat_mensagem(usuario_id);

CREATE INDEX IF NOT EXISTS idx_chat_lida
ON chat_mensagem(sala_id, lida);
"""

INSERIR = """
INSERT INTO chat_mensagem (sala_id, usuario_id, mensagem, data_envio)
VALUES (?, ?, ?, ?)
"""

OBTER_MENSAGENS_SALA = """
SELECT
    cm.id,
    cm.sala_id,
    cm.usuario_id,
    cm.mensagem,
    cm.data_envio as "data_envio [timestamp]",
    cm.lida,
    u.nome as usuario_nome,
    u.email as usuario_email
FROM chat_mensagem cm
INNER JOIN usuario u ON cm.usuario_id = u.id
WHERE cm.sala_id = ?
ORDER BY cm.data_envio ASC
LIMIT ? OFFSET ?
"""

OBTER_MENSAGENS_APOS_ID = """
SELECT
    cm.id,
    cm.sala_id,
    cm.usuario_id,
    cm.mensagem,
    cm.data_envio as "data_envio [timestamp]",
    cm.lida,
    u.nome as usuario_nome,
    u.email as usuario_email
FROM chat_mensagem cm
INNER JOIN usuario u ON cm.usuario_id = u.id
WHERE cm.sala_id = ? AND cm.id > ?
ORDER BY cm.data_envio ASC
"""

MARCAR_COMO_LIDA = """
UPDATE chat_mensagem
SET lida = 1
WHERE sala_id = ? AND usuario_id != ? AND lida = 0
"""

CONTAR_NAO_LIDAS = """
SELECT COUNT(*) as total
FROM chat_mensagem
WHERE sala_id = ? AND usuario_id != ? AND lida = 0
"""

OBTER_ULTIMAS_MENSAGENS_SALA = """
SELECT
    cm.id,
    cm.sala_id,
    cm.usuario_id,
    cm.mensagem,
    cm.data_envio as "data_envio [timestamp]",
    cm.lida,
    u.nome as usuario_nome,
    u.email as usuario_email
FROM chat_mensagem cm
INNER JOIN usuario u ON cm.usuario_id = u.id
WHERE cm.sala_id = ?
ORDER BY cm.data_envio DESC
LIMIT ?
"""

EXCLUIR_MENSAGEM = """
DELETE FROM chat_mensagem WHERE id = ?
"""

EXCLUIR_MENSAGENS_SALA = """
DELETE FROM chat_mensagem WHERE sala_id = ?
"""
```

**Explicação dos Campos:**
- `id`: Identificador único da mensagem
- `sala_id`: ID da sala/chat (permite múltiplas salas)
- `usuario_id`: Quem enviou a mensagem (FK para tabela usuario)
- `mensagem`: Conteúdo textual da mensagem
- `data_envio`: Timestamp do envio (gerenciado pelo sistema de timezone)
- `lida`: Flag booleana (0/1) para controle de mensagens não lidas

**Índices para Performance:**
- `idx_chat_sala_data`: Acelera consulta de mensagens por sala ordenadas por data
- `idx_chat_usuario`: Acelera filtros por usuário
- `idx_chat_lida`: Acelera contagem de não lidas

---

## 📦 Camada 2: Model

### Model (`model/chat_mensagem_model.py`)

```python
"""
Model para mensagens de chat.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ChatMensagem:
    """
    Representa uma mensagem de chat no sistema.

    Attributes:
        id: Identificador único da mensagem
        sala_id: ID da sala onde a mensagem foi enviada
        usuario_id: ID do usuário que enviou
        mensagem: Conteúdo textual da mensagem
        data_envio: Data e hora do envio
        lida: Se a mensagem já foi visualizada
        usuario_nome: Nome do remetente (campo de JOIN)
        usuario_email: Email do remetente (campo de JOIN)
    """
    id: int
    sala_id: int
    usuario_id: int
    mensagem: str
    data_envio: datetime
    lida: bool = False
    # Campos do JOIN (opcionais - para exibição)
    usuario_nome: Optional[str] = None
    usuario_email: Optional[str] = None

    def to_dict(self) -> dict:
        """
        Converte a mensagem para dicionário (útil para JSON/SSE).

        Returns:
            Dicionário com dados da mensagem
        """
        return {
            "id": self.id,
            "sala_id": self.sala_id,
            "usuario_id": self.usuario_id,
            "mensagem": self.mensagem,
            "data_envio": self.data_envio.isoformat(),
            "lida": self.lida,
            "usuario_nome": self.usuario_nome,
            "usuario_email": self.usuario_email
        }
```

**Por que `to_dict()`?**
SSE envia dados como texto (JSON). O método facilita serialização para enviar via EventSource.

---

## 🗃️ Camada 3: Repository

### Repository (`repo/chat_mensagem_repo.py`)

```python
"""
Repository para operações de banco de dados de mensagens de chat.
"""
from datetime import datetime
from typing import Optional, List
from model.chat_mensagem_model import ChatMensagem
from sql.chat_mensagem_sql import *
from util.db_util import get_connection
from util.datetime_util import agora


def _row_to_chat_mensagem(row) -> ChatMensagem:
    """
    Converte uma linha do banco de dados em objeto ChatMensagem.

    Args:
        row: Linha do cursor SQLite (sqlite3.Row)

    Returns:
        Objeto ChatMensagem populado
    """
    # Campos do JOIN (opcionais)
    usuario_nome = row["usuario_nome"] if "usuario_nome" in row.keys() else None
    usuario_email = row["usuario_email"] if "usuario_email" in row.keys() else None

    return ChatMensagem(
        id=row["id"],
        sala_id=row["sala_id"],
        usuario_id=row["usuario_id"],
        mensagem=row["mensagem"],
        data_envio=row["data_envio"],  # Automaticamente convertido pelo db_util
        lida=bool(row["lida"]),
        usuario_nome=usuario_nome,
        usuario_email=usuario_email
    )


def criar_tabela() -> bool:
    """
    Cria a tabela de mensagens de chat e índices.

    Returns:
        True se criado com sucesso
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        cursor.execute(CRIAR_INDICES)
        return True


def inserir(mensagem: ChatMensagem) -> Optional[int]:
    """
    Insere uma nova mensagem no banco.

    Args:
        mensagem: Objeto ChatMensagem a ser inserido

    Returns:
        ID da mensagem inserida, ou None se falhar
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        # IMPORTANTE: Usar agora() do datetime_util, NÃO datetime.now()
        # E passar objeto datetime diretamente, NÃO usar strftime()
        cursor.execute(INSERIR, (
            mensagem.sala_id,
            mensagem.usuario_id,
            mensagem.mensagem,
            agora()  # Sistema de timezone automático
        ))
        return cursor.lastrowid


def obter_mensagens_sala(
    sala_id: int,
    limit: int = 50,
    offset: int = 0
) -> List[ChatMensagem]:
    """
    Obtém mensagens de uma sala com paginação.

    Args:
        sala_id: ID da sala
        limit: Número máximo de mensagens a retornar
        offset: Deslocamento para paginação

    Returns:
        Lista de ChatMensagem ordenadas por data (mais antigas primeiro)
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_MENSAGENS_SALA, (sala_id, limit, offset))
        rows = cursor.fetchall()
        return [_row_to_chat_mensagem(row) for row in rows]


def obter_mensagens_apos_id(sala_id: int, ultimo_id: int) -> List[ChatMensagem]:
    """
    Obtém mensagens enviadas após um determinado ID.
    Útil para SSE incremental.

    Args:
        sala_id: ID da sala
        ultimo_id: ID da última mensagem conhecida

    Returns:
        Lista de ChatMensagem novas (id > ultimo_id)
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_MENSAGENS_APOS_ID, (sala_id, ultimo_id))
        rows = cursor.fetchall()
        return [_row_to_chat_mensagem(row) for row in rows]


def obter_ultimas_mensagens(sala_id: int, limit: int = 100) -> List[ChatMensagem]:
    """
    Obtém as últimas N mensagens de uma sala.
    Retorna em ordem decrescente (mais recentes primeiro).

    Args:
        sala_id: ID da sala
        limit: Número de mensagens a retornar

    Returns:
        Lista de ChatMensagem (mais recentes primeiro)
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_ULTIMAS_MENSAGENS_SALA, (sala_id, limit))
        rows = cursor.fetchall()
        return [_row_to_chat_mensagem(row) for row in rows]


def marcar_como_lida(sala_id: int, usuario_id: int) -> bool:
    """
    Marca todas as mensagens da sala como lidas,
    exceto as do próprio usuário.

    Args:
        sala_id: ID da sala
        usuario_id: ID do usuário que está lendo

    Returns:
        True se marcou com sucesso
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(MARCAR_COMO_LIDA, (sala_id, usuario_id))
        return True


def contar_nao_lidas(sala_id: int, usuario_id: int) -> int:
    """
    Conta mensagens não lidas na sala para um usuário.

    Args:
        sala_id: ID da sala
        usuario_id: ID do usuário

    Returns:
        Número de mensagens não lidas
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_NAO_LIDAS, (sala_id, usuario_id))
        row = cursor.fetchone()
        return row["total"] if row else 0


def excluir_mensagem(id: int) -> bool:
    """
    Exclui uma mensagem específica.

    Args:
        id: ID da mensagem

    Returns:
        True se excluiu com sucesso
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR_MENSAGEM, (id,))
        return cursor.rowcount > 0


def excluir_mensagens_sala(sala_id: int) -> bool:
    """
    Exclui todas as mensagens de uma sala.

    Args:
        sala_id: ID da sala

    Returns:
        True se excluiu com sucesso
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR_MENSAGENS_SALA, (sala_id,))
        return True
```

**Observações Importantes:**
- `_row_to_chat_mensagem()`: Função privada para conversão, padrão do projeto
- Sistema de timezone automático via `agora()` e conversão do `db_util`
- Paginação suportada para salas com muitas mensagens
- `obter_mensagens_apos_id()`: Crucial para SSE incremental (evita reenviar tudo)

---

## ✅ Camada 4: DTOs e Validação

### DTOs (`dtos/chat_dto.py`)

```python
"""
DTOs para validação de dados do sistema de chat.
"""
from pydantic import BaseModel, field_validator
from dtos.validators import validar_string_obrigatoria, validar_comprimento


class EnviarMensagemDTO(BaseModel):
    """
    DTO para validação ao enviar uma mensagem de chat.

    Attributes:
        sala_id: ID da sala de chat
        mensagem: Conteúdo da mensagem
    """
    sala_id: int
    mensagem: str

    @field_validator("sala_id")
    @classmethod
    def validar_sala_id(cls, v):
        """Valida que sala_id é positivo."""
        if v <= 0:
            raise ValueError("ID da sala deve ser positivo")
        return v

    _validar_mensagem = field_validator("mensagem")(
        validar_string_obrigatoria(
            nome_campo="Mensagem",
            tamanho_minimo=1,
            tamanho_maximo=1000,
            truncar=False
        )
    )

    @field_validator("mensagem")
    @classmethod
    def validar_mensagem_nao_vazia(cls, v):
        """Valida que mensagem não é apenas espaços."""
        if not v.strip():
            raise ValueError("Mensagem não pode estar vazia")
        return v.strip()


class CarregarMensagensDTO(BaseModel):
    """
    DTO para validação ao carregar mensagens de uma sala.

    Attributes:
        sala_id: ID da sala de chat
        limit: Número máximo de mensagens a retornar
        offset: Deslocamento para paginação
    """
    sala_id: int
    limit: int = 50
    offset: int = 0

    @field_validator("sala_id")
    @classmethod
    def validar_sala_id(cls, v):
        """Valida que sala_id é positivo."""
        if v <= 0:
            raise ValueError("ID da sala deve ser positivo")
        return v

    @field_validator("limit")
    @classmethod
    def validar_limit(cls, v):
        """Valida que limit está entre 1 e 200."""
        if v < 1 or v > 200:
            raise ValueError("Limite deve estar entre 1 e 200 mensagens")
        return v

    @field_validator("offset")
    @classmethod
    def validar_offset(cls, v):
        """Valida que offset não é negativo."""
        if v < 0:
            raise ValueError("Offset não pode ser negativo")
        return v
```

**Por que esses validators?**
- `sala_id`: Previne IDs inválidos (negativos, zero)
- `mensagem`: Previne mensagens vazias ou muito longas (limite 1000 chars)
- `limit/offset`: Previne paginação maliciosa (ex: limit=999999)

---

## ⚙️ Camada 5: Gerenciador de Conexões SSE

### Chat Manager (`util/chat_manager.py`)

Este é o **coração do sistema SSE**. Gerencia conexões ativas, notificações e cleanup.

```python
"""
Gerenciador de conexões SSE para o sistema de chat em tempo real.

Este módulo é responsável por:
- Gerenciar conexões EventSource ativas por sala
- Notificar novas mensagens para todas as conexões de uma sala
- Controlar timeouts e cleanup de conexões inativas
"""
import asyncio
from typing import Dict, Set
from collections import defaultdict
from util.logger_config import logger


class ChatManager:
    """
    Gerenciador singleton de conexões SSE do chat.

    Estrutura interna:
    {
        sala_id: {
            usuario_id: asyncio.Queue,
            usuario_id: asyncio.Queue,
            ...
        }
    }

    Cada Queue armazena mensagens pendentes para um usuário específico.
    """

    def __init__(self):
        """Inicializa o gerenciador com dicionários vazios."""
        # Dicionário: sala_id -> {usuario_id -> Queue}
        self._connections: Dict[int, Dict[int, asyncio.Queue]] = defaultdict(dict)
        # Controle de conexões ativas
        self._active_connections: Set[tuple] = set()

    async def connect(self, sala_id: int, usuario_id: int) -> asyncio.Queue:
        """
        Registra uma nova conexão SSE.

        Args:
            sala_id: ID da sala de chat
            usuario_id: ID do usuário conectando

        Returns:
            Queue para receber mensagens
        """
        # Cria uma Queue para este usuário nesta sala
        queue = asyncio.Queue()

        # Registra a conexão
        self._connections[sala_id][usuario_id] = queue
        self._active_connections.add((sala_id, usuario_id))

        logger.info(
            f"Usuário {usuario_id} conectou na sala {sala_id}. "
            f"Total na sala: {len(self._connections[sala_id])}"
        )

        return queue

    async def disconnect(self, sala_id: int, usuario_id: int):
        """
        Remove uma conexão SSE.

        Args:
            sala_id: ID da sala de chat
            usuario_id: ID do usuário desconectando
        """
        try:
            # Remove a queue do dicionário
            if sala_id in self._connections:
                if usuario_id in self._connections[sala_id]:
                    del self._connections[sala_id][usuario_id]

                # Se a sala ficou vazia, remove ela também
                if not self._connections[sala_id]:
                    del self._connections[sala_id]

            # Remove do set de conexões ativas
            self._active_connections.discard((sala_id, usuario_id))

            logger.info(
                f"Usuário {usuario_id} desconectou da sala {sala_id}"
            )
        except Exception as e:
            logger.error(f"Erro ao desconectar usuário: {e}")

    async def broadcast(self, sala_id: int, mensagem_dict: dict):
        """
        Envia uma mensagem para TODAS as conexões ativas de uma sala.

        Args:
            sala_id: ID da sala
            mensagem_dict: Dicionário com dados da mensagem (será convertido para JSON)
        """
        if sala_id not in self._connections:
            logger.debug(f"Nenhuma conexão ativa na sala {sala_id}")
            return

        # Percorre todas as queues da sala
        desconectados = []
        for usuario_id, queue in self._connections[sala_id].items():
            try:
                # Adiciona mensagem na queue (não bloqueia)
                await queue.put(mensagem_dict)
                logger.debug(
                    f"Mensagem enviada para usuário {usuario_id} na sala {sala_id}"
                )
            except Exception as e:
                logger.error(
                    f"Erro ao enviar para usuário {usuario_id}: {e}"
                )
                desconectados.append(usuario_id)

        # Remove conexões que falharam
        for usuario_id in desconectados:
            await self.disconnect(sala_id, usuario_id)

    def get_users_in_room(self, sala_id: int) -> list:
        """
        Retorna lista de IDs de usuários conectados em uma sala.

        Args:
            sala_id: ID da sala

        Returns:
            Lista de IDs de usuários
        """
        if sala_id not in self._connections:
            return []
        return list(self._connections[sala_id].keys())

    def get_connection_count(self, sala_id: int) -> int:
        """
        Retorna número de conexões ativas em uma sala.

        Args:
            sala_id: ID da sala

        Returns:
            Número de conexões
        """
        if sala_id not in self._connections:
            return 0
        return len(self._connections[sala_id])

    def get_total_connections(self) -> int:
        """
        Retorna número total de conexões ativas em todas as salas.

        Returns:
            Número total de conexões
        """
        return len(self._active_connections)


# Instância singleton global
chat_manager = ChatManager()
```

**Conceitos-Chave:**

1. **Singleton Pattern**: Uma única instância gerencia TODAS as conexões
2. **asyncio.Queue**: Estrutura thread-safe para passar mensagens entre coroutines
3. **defaultdict**: Facilita criação automática de dicionários aninhados
4. **Broadcast**: Quando uma mensagem chega, notifica TODOS os conectados na sala
5. **Cleanup**: Remove conexões que falharam para evitar memory leak

---

## 🌐 Camada 6: Routes e SSE Endpoint

### Routes (`routes/chat_routes.py`)

```python
"""
Routes para o sistema de chat em tempo real com SSE.
"""
import json
import asyncio
from typing import Optional
from fastapi import APIRouter, Form, Request, Query
from fastapi.responses import StreamingResponse
from pydantic import ValidationError

from dtos.chat_dto import EnviarMensagemDTO
from model.chat_mensagem_model import ChatMensagem
from repo import chat_mensagem_repo
from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro
from util.logger_config import logger
from util.chat_manager import chat_manager
from util.datetime_util import agora

router = APIRouter(prefix="/chat")
templates = criar_templates("templates")


@router.get("/sala/{sala_id}")
@requer_autenticacao()
async def sala(
    request: Request,
    sala_id: int,
    usuario_logado: Optional[dict] = None
):
    """
    Exibe a interface da sala de chat.

    Args:
        request: Requisição HTTP
        sala_id: ID da sala de chat
        usuario_logado: Dados do usuário logado (injetado pelo decorator)
    """
    assert usuario_logado is not None

    # Carrega últimas 100 mensagens da sala
    mensagens = chat_mensagem_repo.obter_ultimas_mensagens(sala_id, limit=100)

    # Inverte para exibir cronologicamente (mais antigas primeiro)
    mensagens.reverse()

    # Marca mensagens como lidas
    chat_mensagem_repo.marcar_como_lida(sala_id, usuario_logado["id"])

    # Conta usuários online
    usuarios_online = chat_manager.get_users_in_room(sala_id)

    return templates.TemplateResponse(
        "chat/sala.html",
        {
            "request": request,
            "sala_id": sala_id,
            "mensagens": mensagens,
            "usuarios_online_count": len(usuarios_online)
        }
    )


@router.get("/stream")
@requer_autenticacao()
async def stream_mensagens(
    request: Request,
    sala_id: int = Query(...),
    usuario_logado: Optional[dict] = None
):
    """
    Endpoint SSE que mantém conexão aberta e envia novas mensagens.

    Este endpoint:
    1. Registra a conexão no ChatManager
    2. Mantém conexão aberta indefinidamente
    3. Envia eventos SSE quando novas mensagens chegam
    4. Desconecta automaticamente se cliente fechar

    Args:
        request: Requisição HTTP
        sala_id: ID da sala de chat (query param)
        usuario_logado: Dados do usuário logado

    Returns:
        StreamingResponse com eventos SSE
    """
    assert usuario_logado is not None

    async def event_generator():
        """
        Generator que produz eventos SSE.

        Formato SSE:
        data: {"mensagem": "conteúdo"}\n\n

        O navegador reconhece automaticamente este formato.
        """
        # Registra conexão
        queue = await chat_manager.connect(sala_id, usuario_logado["id"])

        try:
            logger.info(
                f"SSE stream iniciado: usuário={usuario_logado['id']}, sala={sala_id}"
            )

            # Loop infinito: enquanto cliente estiver conectado
            while True:
                # Aguarda próxima mensagem na queue (bloqueia até ter uma)
                mensagem_dict = await queue.get()

                # Formata como evento SSE
                # IMPORTANTE: formato SSE é "data: JSON\n\n"
                sse_data = f"data: {json.dumps(mensagem_dict)}\n\n"

                yield sse_data

                # Pequeno delay para evitar sobrecarga
                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            # Cliente desconectou (normal)
            logger.info(
                f"SSE stream cancelado: usuário={usuario_logado['id']}, sala={sala_id}"
            )
        except Exception as e:
            # Erro inesperado
            logger.error(f"Erro no SSE stream: {e}")
        finally:
            # Sempre desconecta ao final
            await chat_manager.disconnect(sala_id, usuario_logado["id"])

    # Retorna StreamingResponse com headers SSE
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Para NGINX
        }
    )


@router.post("/enviar")
@requer_autenticacao()
async def enviar_mensagem(
    request: Request,
    sala_id: int = Form(...),
    mensagem: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """
    Envia uma nova mensagem para a sala.

    Fluxo:
    1. Valida com DTO
    2. Salva no banco
    3. Notifica TODAS as conexões SSE ativas via ChatManager

    Args:
        request: Requisição HTTP
        sala_id: ID da sala (form data)
        mensagem: Texto da mensagem (form data)
        usuario_logado: Dados do usuário logado

    Returns:
        JSON com sucesso ou erro
    """
    assert usuario_logado is not None

    try:
        # Validação com DTO
        dto = EnviarMensagemDTO(sala_id=sala_id, mensagem=mensagem)

        # Cria objeto de mensagem
        nova_mensagem = ChatMensagem(
            id=0,  # Será preenchido pelo banco
            sala_id=dto.sala_id,
            usuario_id=usuario_logado["id"],
            mensagem=dto.mensagem,
            data_envio=agora(),  # Timezone-aware
            lida=False,
            usuario_nome=usuario_logado.get("nome"),
            usuario_email=usuario_logado.get("email")
        )

        # Salva no banco
        mensagem_id = chat_mensagem_repo.inserir(nova_mensagem)

        if not mensagem_id:
            return {"success": False, "erro": "Erro ao salvar mensagem"}

        # Atualiza ID da mensagem
        nova_mensagem.id = mensagem_id

        # CRITICAL: Notifica TODAS as conexões SSE ativas da sala
        await chat_manager.broadcast(sala_id, nova_mensagem.to_dict())

        logger.info(
            f"Mensagem enviada: sala={sala_id}, usuario={usuario_logado['id']}, id={mensagem_id}"
        )

        return {
            "success": True,
            "mensagem_id": mensagem_id,
            "data_envio": nova_mensagem.data_envio.isoformat()
        }

    except ValidationError as e:
        # Retorna erros de validação como JSON
        erros = {}
        for erro in e.errors():
            campo = erro["loc"][0] if erro["loc"] else "geral"
            erros[campo] = erro["msg"]

        return {"success": False, "erros": erros}

    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {e}")
        return {"success": False, "erro": "Erro interno do servidor"}


@router.get("/listar-salas")
@requer_autenticacao()
async def listar_salas(request: Request, usuario_logado: Optional[dict] = None):
    """
    Lista todas as salas de chat disponíveis.

    NOTA: Por simplicidade, este exemplo usa uma lista hardcoded.
    Em produção, você teria uma tabela 'chat_sala' no banco.
    """
    assert usuario_logado is not None

    # Exemplo de salas (em produção, viria do banco)
    salas = [
        {
            "id": 1,
            "nome": "Sala Geral",
            "descricao": "Conversa aberta para todos",
            "usuarios_online": chat_manager.get_connection_count(1)
        },
        {
            "id": 2,
            "nome": "Suporte Técnico",
            "descricao": "Tire suas dúvidas técnicas",
            "usuarios_online": chat_manager.get_connection_count(2)
        },
        {
            "id": 3,
            "nome": "Vendas",
            "descricao": "Discussões sobre vendas e negócios",
            "usuarios_online": chat_manager.get_connection_count(3)
        }
    ]

    return templates.TemplateResponse(
        "chat/listar_salas.html",
        {"request": request, "salas": salas}
    )
```

**Pontos Críticos:**

1. **`StreamingResponse`**: Tipo especial de resposta do FastAPI para SSE
2. **`media_type="text/event-stream"`**: Header que identifica SSE
3. **`X-Accel-Buffering: no`**: Desabilita buffer do NGINX (crítico!)
4. **`yield` no generator**: Envia dados incrementalmente sem fechar conexão
5. **`await queue.get()`**: Bloqueia até ter mensagem (não desperdiça CPU)
6. **`finally` block**: Garante cleanup mesmo com erro/desconexão

---

## 🎨 Camada 7: Frontend (Templates e JavaScript)

### Template da Sala (`templates/chat/sala.html`)

```html
{% extends 'base_privada.html' %}

{% block titulo %}Chat - Sala {{ sala_id }}{% endblock %}

{% block styles %}
<style>
    /* Container do chat com altura fixa e scroll */
    #chat-messages {
        height: 500px;
        overflow-y: auto;
        border: 1px solid #dee2e6;
        border-radius: 0.375rem;
        padding: 1rem;
        background-color: #f8f9fa;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }

    /* Bolha de mensagem */
    .message {
        max-width: 70%;
        padding: 0.75rem 1rem;
        border-radius: 1rem;
        position: relative;
        word-wrap: break-word;
    }

    /* Mensagem do próprio usuário (direita, azul) */
    .message.own {
        align-self: flex-end;
        background-color: #0d6efd;
        color: white;
    }

    /* Mensagem de outros usuários (esquerda, cinza) */
    .message.other {
        align-self: flex-start;
        background-color: white;
        border: 1px solid #dee2e6;
    }

    /* Nome do remetente */
    .message-sender {
        font-weight: 600;
        font-size: 0.875rem;
        margin-bottom: 0.25rem;
    }

    /* Texto da mensagem */
    .message-text {
        margin-bottom: 0.25rem;
    }

    /* Timestamp */
    .message-time {
        font-size: 0.75rem;
        opacity: 0.7;
        text-align: right;
    }

    /* Campo de input fixo no fundo */
    #chat-input-container {
        position: sticky;
        bottom: 0;
        background: white;
        padding-top: 1rem;
        border-top: 1px solid #dee2e6;
    }

    /* Indicador de conexão */
    .connection-status {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 5px;
    }

    .connection-status.connected {
        background-color: #28a745;
    }

    .connection-status.disconnected {
        background-color: #dc3545;
    }
</style>
{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-12">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h2>
                <i class="bi bi-chat-dots"></i> Sala de Chat #{{ sala_id }}
            </h2>
            <div>
                <span class="connection-status connected" id="connection-indicator"></span>
                <span id="connection-text">Conectado</span>
                <span class="badge bg-primary ms-2">
                    <i class="bi bi-people"></i> {{ usuarios_online_count }} online
                </span>
            </div>
        </div>

        <!-- Container de mensagens -->
        <div id="chat-messages">
            {% for msg in mensagens %}
            <div class="message {% if msg.usuario_id == usuario_logado.id %}own{% else %}other{% endif %}"
                 data-message-id="{{ msg.id }}">
                {% if msg.usuario_id != usuario_logado.id %}
                <div class="message-sender">{{ msg.usuario_nome }}</div>
                {% endif %}
                <div class="message-text">{{ msg.mensagem }}</div>
                <div class="message-time">{{ msg.data_envio|format_data_hora }}</div>
            </div>
            {% endfor %}
        </div>

        <!-- Formulário de envio -->
        <div id="chat-input-container">
            <form id="chat-form" class="d-flex gap-2">
                <input type="hidden" name="sala_id" value="{{ sala_id }}">
                <input
                    type="text"
                    id="mensagem-input"
                    name="mensagem"
                    class="form-control"
                    placeholder="Digite sua mensagem..."
                    autocomplete="off"
                    maxlength="1000"
                    required
                >
                <button type="submit" class="btn btn-primary">
                    <i class="bi bi-send"></i> Enviar
                </button>
            </form>
            <small class="text-muted">
                Pressione Enter para enviar
            </small>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script src="/static/js/chat.js"></script>
<script>
    // Inicializa o chat quando a página carregar
    document.addEventListener('DOMContentLoaded', () => {
        const salaId = {{ sala_id }};
        const usuarioId = {{ usuario_logado.id }};
        const usuarioNome = "{{ usuario_logado.nome }}";

        // Inicializa módulo de chat
        window.chatModule.init(salaId, usuarioId, usuarioNome);
    });
</script>
{% endblock %}
```

### JavaScript Module (`static/js/chat.js`)

```javascript
/**
 * Módulo de Chat em Tempo Real com SSE
 *
 * Responsabilidades:
 * - Gerenciar conexão EventSource (SSE)
 * - Receber mensagens em tempo real
 * - Enviar mensagens via fetch POST
 * - Atualizar UI dinamicamente
 * - Gerenciar reconexão automática
 */

const chatModule = (() => {
    // Estado privado
    let eventSource = null;
    let salaId = null;
    let usuarioId = null;
    let usuarioNome = null;
    let reconectando = false;

    // Elementos DOM (cachear para performance)
    const elementos = {
        messagesContainer: null,
        form: null,
        input: null,
        connectionIndicator: null,
        connectionText: null
    };

    /**
     * Inicializa o módulo de chat
     * @param {number} sala - ID da sala
     * @param {number} usuario - ID do usuário logado
     * @param {string} nome - Nome do usuário logado
     */
    function init(sala, usuario, nome) {
        salaId = sala;
        usuarioId = usuario;
        usuarioNome = nome;

        // Cachear elementos DOM
        elementos.messagesContainer = document.getElementById('chat-messages');
        elementos.form = document.getElementById('chat-form');
        elementos.input = document.getElementById('mensagem-input');
        elementos.connectionIndicator = document.getElementById('connection-indicator');
        elementos.connectionText = document.getElementById('connection-text');

        // Configurar event listeners
        setupEventListeners();

        // Conectar ao SSE
        conectarSSE();

        // Scroll para o fim das mensagens
        scrollToBottom();
    }

    /**
     * Configura event listeners do formulário
     */
    function setupEventListeners() {
        // Submit do formulário
        elementos.form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await enviarMensagem();
        });

        // Enter para enviar (Shift+Enter para nova linha)
        elementos.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                elementos.form.dispatchEvent(new Event('submit'));
            }
        });
    }

    /**
     * Conecta ao endpoint SSE
     */
    function conectarSSE() {
        // Fechar conexão anterior se existir
        if (eventSource) {
            eventSource.close();
        }

        // URL do endpoint SSE
        const url = `/chat/stream?sala_id=${salaId}`;

        // Criar EventSource
        eventSource = new EventSource(url);

        // Handler: Conexão aberta
        eventSource.onopen = () => {
            console.log('[SSE] Conectado');
            atualizarStatusConexao(true);
            reconectando = false;
        };

        // Handler: Mensagem recebida
        eventSource.onmessage = (event) => {
            try {
                const mensagem = JSON.parse(event.data);
                console.log('[SSE] Mensagem recebida:', mensagem);

                // Adicionar mensagem à UI
                adicionarMensagemUI(mensagem);
            } catch (erro) {
                console.error('[SSE] Erro ao processar mensagem:', erro);
            }
        };

        // Handler: Erro de conexão
        eventSource.onerror = (erro) => {
            console.error('[SSE] Erro de conexão:', erro);
            atualizarStatusConexao(false);

            // EventSource reconecta automaticamente, mas vamos informar o usuário
            if (!reconectando) {
                reconectando = true;
                if (window.exibirToast) {
                    window.exibirToast('Conexão perdida. Reconectando...', 'warning');
                }
            }
        };
    }

    /**
     * Envia mensagem via POST
     */
    async function enviarMensagem() {
        const mensagem = elementos.input.value.trim();

        // Validar input
        if (!mensagem) {
            if (window.exibirToast) {
                window.exibirToast('Digite uma mensagem', 'warning');
            }
            return;
        }

        if (mensagem.length > 1000) {
            if (window.exibirToast) {
                window.exibirToast('Mensagem muito longa (máx. 1000 caracteres)', 'danger');
            }
            return;
        }

        try {
            // Enviar via fetch POST
            const response = await fetch('/chat/enviar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    sala_id: salaId,
                    mensagem: mensagem
                })
            });

            const resultado = await response.json();

            if (resultado.success) {
                // Limpar input
                elementos.input.value = '';

                // Focar input novamente
                elementos.input.focus();

                // Nota: NÃO adicionamos a mensagem aqui na UI
                // Ela chegará via SSE (broadcast) e será adicionada lá
            } else {
                // Exibir erros
                if (resultado.erros) {
                    const mensagensErro = Object.values(resultado.erros).join(', ');
                    if (window.exibirToast) {
                        window.exibirToast(mensagensErro, 'danger');
                    }
                } else {
                    if (window.exibirToast) {
                        window.exibirToast(resultado.erro || 'Erro ao enviar mensagem', 'danger');
                    }
                }
            }
        } catch (erro) {
            console.error('[Chat] Erro ao enviar mensagem:', erro);
            if (window.exibirToast) {
                window.exibirToast('Erro ao enviar mensagem', 'danger');
            }
        }
    }

    /**
     * Adiciona mensagem à UI
     * @param {Object} mensagem - Dados da mensagem
     */
    function adicionarMensagemUI(mensagem) {
        // Verificar se mensagem já existe (evitar duplicatas)
        const existe = document.querySelector(`[data-message-id="${mensagem.id}"]`);
        if (existe) {
            console.log('[Chat] Mensagem já existe, ignorando:', mensagem.id);
            return;
        }

        // Criar elemento da mensagem
        const messageDiv = document.createElement('div');
        messageDiv.className = mensagem.usuario_id === usuarioId ? 'message own' : 'message other';
        messageDiv.setAttribute('data-message-id', mensagem.id);

        // HTML da mensagem
        let html = '';

        // Nome do remetente (se não for próprio usuário)
        if (mensagem.usuario_id !== usuarioId) {
            html += `<div class="message-sender">${escapeHtml(mensagem.usuario_nome)}</div>`;
        }

        // Texto da mensagem (escapar HTML para segurança)
        const textoEscapado = escapeHtml(mensagem.mensagem);
        html += `<div class="message-text">${textoEscapado}</div>`;

        // Timestamp formatado
        const dataFormatada = formatarDataHora(mensagem.data_envio);
        html += `<div class="message-time">${dataFormatada}</div>`;

        messageDiv.innerHTML = html;

        // Adicionar ao container
        elementos.messagesContainer.appendChild(messageDiv);

        // Scroll para o fim
        scrollToBottom();

        // Animação de entrada
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(10px)';
        setTimeout(() => {
            messageDiv.style.transition = 'all 0.3s ease';
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        }, 10);
    }

    /**
     * Atualiza indicador visual de status da conexão
     * @param {boolean} conectado - Se está conectado
     */
    function atualizarStatusConexao(conectado) {
        if (conectado) {
            elementos.connectionIndicator.classList.remove('disconnected');
            elementos.connectionIndicator.classList.add('connected');
            elementos.connectionText.textContent = 'Conectado';
        } else {
            elementos.connectionIndicator.classList.remove('connected');
            elementos.connectionIndicator.classList.add('disconnected');
            elementos.connectionText.textContent = 'Desconectado';
        }
    }

    /**
     * Scroll suave para o fim do container de mensagens
     */
    function scrollToBottom() {
        elementos.messagesContainer.scrollTop = elementos.messagesContainer.scrollHeight;
    }

    /**
     * Escapa HTML para prevenir XSS
     * @param {string} texto - Texto a escapar
     * @returns {string} Texto escapado
     */
    function escapeHtml(texto) {
        const div = document.createElement('div');
        div.textContent = texto;
        return div.innerHTML;
    }

    /**
     * Formata data/hora ISO para exibição
     * @param {string} isoString - String ISO 8601
     * @returns {string} Data formatada
     */
    function formatarDataHora(isoString) {
        const data = new Date(isoString);
        const hoje = new Date();

        // Se for hoje, mostra apenas hora
        if (data.toDateString() === hoje.toDateString()) {
            return data.toLocaleTimeString('pt-BR', {
                hour: '2-digit',
                minute: '2-digit'
            });
        }

        // Se for outro dia, mostra data + hora
        return data.toLocaleString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    /**
     * Cleanup ao sair da página
     */
    function destruir() {
        if (eventSource) {
            eventSource.close();
            console.log('[SSE] Conexão fechada');
        }
    }

    // Cleanup automático ao sair da página
    window.addEventListener('beforeunload', destruir);

    // API pública
    return {
        init,
        destruir
    };
})();

// Expor globalmente
window.chatModule = chatModule;
```

### Template de Listagem (`templates/chat/listar_salas.html`)

```html
{% extends 'base_privada.html' %}

{% block titulo %}Salas de Chat{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-12">
        <h2 class="mb-4">
            <i class="bi bi-chat-dots-fill"></i> Salas de Chat Disponíveis
        </h2>

        <div class="row g-3">
            {% for sala in salas %}
            <div class="col-md-6 col-lg-4">
                <div class="card h-100 shadow-sm">
                    <div class="card-body">
                        <h5 class="card-title">
                            <i class="bi bi-door-open"></i> {{ sala.nome }}
                        </h5>
                        <p class="card-text text-muted">
                            {{ sala.descricao }}
                        </p>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                <i class="bi bi-people-fill"></i>
                                {{ sala.usuarios_online }} online
                            </small>
                            <a href="/chat/sala/{{ sala.id }}" class="btn btn-primary btn-sm">
                                <i class="bi bi-box-arrow-in-right"></i> Entrar
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</div>
{% endblock %}
```

---

## 🧪 Camada 8: Testes

### Testes (`tests/test_chat.py`)

```python
"""
Testes para o sistema de chat em tempo real.
"""
import pytest
from model.chat_mensagem_model import ChatMensagem
from repo import chat_mensagem_repo
from util.datetime_util import agora


@pytest.mark.unit
def test_criar_tabela_chat(client):
    """Testa criação da tabela de mensagens"""
    resultado = chat_mensagem_repo.criar_tabela()
    assert resultado is True


@pytest.mark.unit
def test_inserir_mensagem(client, criar_usuario):
    """Testa inserção de mensagem"""
    # Criar usuário para teste
    usuario = criar_usuario("chatuser@test.com", "Chat@123")

    # Criar mensagem
    mensagem = ChatMensagem(
        id=0,
        sala_id=1,
        usuario_id=usuario["id"],
        mensagem="Mensagem de teste",
        data_envio=agora(),
        lida=False
    )

    # Inserir
    mensagem_id = chat_mensagem_repo.inserir(mensagem)

    assert mensagem_id is not None
    assert mensagem_id > 0


@pytest.mark.unit
def test_obter_mensagens_sala(client, criar_usuario):
    """Testa obtenção de mensagens por sala"""
    # Criar usuário
    usuario = criar_usuario("chatuser2@test.com", "Chat@123")

    # Inserir 3 mensagens na sala 1
    for i in range(3):
        mensagem = ChatMensagem(
            id=0,
            sala_id=1,
            usuario_id=usuario["id"],
            mensagem=f"Mensagem {i+1}",
            data_envio=agora(),
            lida=False
        )
        chat_mensagem_repo.inserir(mensagem)

    # Obter mensagens
    mensagens = chat_mensagem_repo.obter_mensagens_sala(sala_id=1, limit=10)

    assert len(mensagens) >= 3
    assert any(msg.mensagem == "Mensagem 1" for msg in mensagens)


@pytest.mark.unit
def test_marcar_como_lida(client, criar_usuario):
    """Testa marcação de mensagens como lidas"""
    # Criar dois usuários
    usuario1 = criar_usuario("user1@test.com", "User@123")
    usuario2 = criar_usuario("user2@test.com", "User@123")

    # Usuário 1 envia mensagem
    mensagem = ChatMensagem(
        id=0,
        sala_id=1,
        usuario_id=usuario1["id"],
        mensagem="Olá!",
        data_envio=agora(),
        lida=False
    )
    chat_mensagem_repo.inserir(mensagem)

    # Usuário 2 marca como lida
    resultado = chat_mensagem_repo.marcar_como_lida(
        sala_id=1,
        usuario_id=usuario2["id"]
    )

    assert resultado is True


@pytest.mark.integration
def test_enviar_mensagem_via_api(cliente_autenticado):
    """Testa envio de mensagem via endpoint"""
    response = cliente_autenticado.post(
        "/chat/enviar",
        data={
            "sala_id": 1,
            "mensagem": "Teste via API"
        }
    )

    assert response.status_code == 200

    dados = response.json()
    assert dados["success"] is True
    assert "mensagem_id" in dados


@pytest.mark.integration
def test_validacao_mensagem_vazia(cliente_autenticado):
    """Testa que mensagem vazia é rejeitada"""
    response = cliente_autenticado.post(
        "/chat/enviar",
        data={
            "sala_id": 1,
            "mensagem": "   "
        }
    )

    dados = response.json()
    assert dados["success"] is False
    assert "erros" in dados


@pytest.mark.integration
def test_acesso_sala_autenticado(cliente_autenticado):
    """Testa acesso à sala por usuário autenticado"""
    response = cliente_autenticado.get("/chat/sala/1")

    assert response.status_code == 200
    assert b"Sala de Chat" in response.content


@pytest.mark.integration
def test_acesso_sala_nao_autenticado(client):
    """Testa que usuário não autenticado é redirecionado"""
    response = client.get("/chat/sala/1", follow_redirects=False)

    assert response.status_code == 303
    assert "/login" in response.headers["location"]
```

---

## 📝 Checklist de Implementação

Siga esta ordem exata para implementar o sistema:

### Fase 1: Backend Básico

- [ ] **1.1** Criar `sql/chat_mensagem_sql.py` com todas as queries
- [ ] **1.2** Criar `model/chat_mensagem_model.py` com dataclass e `to_dict()`
- [ ] **1.3** Criar `repo/chat_mensagem_repo.py` com todas as funções CRUD
- [ ] **1.4** Criar `dtos/chat_dto.py` com DTOs de validação
- [ ] **1.5** Registrar criação de tabela no `main.py` startup:
  ```python
  from repo import chat_mensagem_repo

  @app.on_event("startup")
  async def startup():
      # ... outras tabelas ...
      chat_mensagem_repo.criar_tabela()
  ```

### Fase 2: Gerenciador SSE

- [ ] **2.1** Criar `util/chat_manager.py` com classe `ChatManager`
- [ ] **2.2** Testar instância singleton `chat_manager`
- [ ] **2.3** Implementar métodos `connect()`, `disconnect()`, `broadcast()`

### Fase 3: Routes e SSE

- [ ] **3.1** Criar `routes/chat_routes.py` com router básico
- [ ] **3.2** Implementar endpoint `GET /sala/{sala_id}`
- [ ] **3.3** Implementar endpoint SSE `GET /stream`
- [ ] **3.4** Implementar endpoint `POST /enviar`
- [ ] **3.5** Implementar endpoint `GET /listar-salas`
- [ ] **3.6** Registrar router no `main.py`:
  ```python
  from routes.chat_routes import router as chat_router

  app.include_router(chat_router)
  ```

### Fase 4: Frontend

- [ ] **4.1** Criar diretório `templates/chat/`
- [ ] **4.2** Criar `templates/chat/sala.html` com HTML completo
- [ ] **4.3** Criar `templates/chat/listar_salas.html`
- [ ] **4.4** Criar `static/js/chat.js` com módulo JavaScript
- [ ] **4.5** Adicionar link no menu principal para `/chat/listar-salas`

### Fase 5: Testes

- [ ] **5.1** Criar `tests/test_chat.py` com testes unitários
- [ ] **5.2** Executar `pytest tests/test_chat.py -v`
- [ ] **5.3** Corrigir erros até todos passarem

### Fase 6: Verificação Manual

- [ ] **6.1** Iniciar aplicação: `python main.py`
- [ ] **6.2** Acessar `/chat/listar-salas` e verificar lista
- [ ] **6.3** Entrar em uma sala
- [ ] **6.4** Abrir sala em DUAS abas diferentes (simular dois usuários)
- [ ] **6.5** Enviar mensagem em uma aba
- [ ] **6.6** Verificar que aparece em TEMPO REAL na outra aba
- [ ] **6.7** Verificar indicador de conexão (bolinha verde)
- [ ] **6.8** Fechar uma aba e verificar que a outra continua funcionando

---

## 🚀 Deployment e Considerações de Produção

### 1. Configuração NGINX

SSE requer configuração especial no NGINX para não fazer buffer:

```nginx
location /chat/stream {
    proxy_pass http://localhost:8400;
    proxy_http_version 1.1;

    # CRITICAL: Desabilita buffering para SSE
    proxy_buffering off;
    proxy_cache off;

    # Headers para SSE
    proxy_set_header Connection '';
    proxy_set_header X-Accel-Buffering no;

    # Timeouts longos (conexão fica aberta)
    proxy_read_timeout 86400s;
    proxy_send_timeout 86400s;
}
```

### 2. Variáveis de Ambiente

Adicione ao `.env`:

```bash
# Configurações de Chat
CHAT_MAX_CONNECTIONS_PER_ROOM=100
CHAT_MESSAGE_MAX_LENGTH=1000
CHAT_HISTORY_LIMIT=100
CHAT_SSE_TIMEOUT=86400  # 24 horas
```

### 3. Performance

**Limites Recomendados:**
- **Máximo de 100 conexões simultâneas** por sala
- **Máximo de 1000 mensagens** no histórico (implemente paginação)
- **Timeout de 24h** para conexões SSE (reconecta automaticamente)

### 4. Segurança

**Checklist de Segurança:**
- ✅ Validação de sala_id (prevenir SQL injection)
- ✅ Escape de HTML nas mensagens (prevenir XSS)
- ✅ Autenticação obrigatória em todos os endpoints
- ✅ Limite de tamanho de mensagem (prevenir DoS)
- ✅ Rate limiting por usuário (prevenir spam)

### 5. Monitoramento

```python
# Endpoint de health check para chat
@router.get("/health")
async def chat_health():
    return {
        "total_connections": chat_manager.get_total_connections(),
        "rooms_active": len(chat_manager._connections),
        "status": "healthy"
    }
```

---

## 🎯 Melhorias Futuras (Opcional)

### 1. Indicador de "Usuário está digitando..."

```python
# Adicionar ao ChatManager
async def notify_typing(self, sala_id: int, usuario_id: int, is_typing: bool):
    await self.broadcast(sala_id, {
        "tipo": "typing",
        "usuario_id": usuario_id,
        "is_typing": is_typing
    })
```

### 2. Upload de Arquivos

```python
# Novo campo na tabela
ALTER TABLE chat_mensagem ADD COLUMN arquivo_url TEXT;
```

### 3. Reações a Mensagens (Emojis)

```sql
CREATE TABLE chat_reacao (
    id INTEGER PRIMARY KEY,
    mensagem_id INTEGER,
    usuario_id INTEGER,
    emoji TEXT,
    FOREIGN KEY (mensagem_id) REFERENCES chat_mensagem(id)
);
```

### 4. Notificações Push

```javascript
// Pedir permissão de notificações
if ('Notification' in window) {
    Notification.requestPermission();
}

// Ao receber mensagem quando página não está focada
if (document.hidden) {
    new Notification('Nova mensagem', {
        body: mensagem.mensagem
    });
}
```

### 5. Migração para WebSocket (se necessário)

**Quando migrar:**
- Mais de 500 conexões simultâneas
- Necessidade de comunicação bidirecional full-duplex
- Latência crítica (< 50ms)

---

## 🔍 Troubleshooting

### Problema: SSE não conecta

**Solução:**
1. Verificar console do navegador (F12)
2. Verificar se endpoint retorna `text/event-stream`
3. Verificar headers de CORS se frontend estiver em domínio diferente

### Problema: Mensagens duplicadas

**Solução:**
- Verificar atributo `data-message-id` único
- Checar lógica de `adicionarMensagemUI()` para prevenir duplicatas

### Problema: Conexão cai após alguns minutos

**Solução:**
- Aumentar timeout do NGINX: `proxy_read_timeout 86400s;`
- Verificar firewall/proxy intermediário

### Problema: Mensagens não aparecem em tempo real

**Solução:**
1. Verificar que `broadcast()` está sendo chamado após `inserir()`
2. Verificar logs do servidor para erros
3. Testar com `curl` direto no endpoint SSE:
   ```bash
   curl -N http://localhost:8400/chat/stream?sala_id=1
   ```

---

## 📚 Referências

### Documentação Oficial
- [MDN: EventSource](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)
- [FastAPI: Custom Response](https://fastapi.tiangolo.com/advanced/custom-response/)
- [Server-Sent Events Spec](https://html.spec.whatwg.org/multipage/server-sent-events.html)

### Artigos Recomendados
- [SSE vs WebSocket](https://ably.com/topic/server-sent-events-vs-websockets)
- [Scaling SSE with NGINX](https://www.nginx.com/blog/nginx-plus-sse-websockets/)

---

## ✅ Conclusão

Este guia fornece **tudo que você precisa** para implementar um chat em tempo real robusto e escalável no DefaultWebApp usando SSE.

**Principais Vantagens:**
- ✅ Simplicidade (sem bibliotecas extras)
- ✅ Performance (conexões leves)
- ✅ Compatibilidade (funciona em todos os navegadores modernos)
- ✅ Manutenibilidade (código limpo e bem estruturado)
- ✅ Segurança (validação e autenticação integradas)

**Próximos Passos:**
1. Siga o checklist de implementação
2. Execute os testes
3. Teste manualmente com múltiplas abas
4. Deploy em produção com configuração NGINX
5. Monitore logs e métricas
6. Implemente melhorias opcionais conforme necessário

Boa implementação! 🚀
