# Rate Limiting - Fase 1 (Implementado)

## Resumo

Implementação bem-sucedida de rate limiting para os 4 endpoints mais críticos da aplicação, conforme Fase 1 do plano de implementação.

## Endpoints Protegidos

### 1. Upload de Foto de Perfil ✅
- **Endpoint**: `POST /usuario/perfil/atualizar-foto`
- **Arquivo**: `routes/usuario_routes.py:294-344`
- **Limite**: 5 uploads / 10 minutos
- **Proteção contra**: DoS via uploads grandes (até 10MB), esgotamento de armazenamento
- **Variáveis de ambiente**:
  - `RATE_LIMIT_UPLOAD_FOTO_MAX` (padrão: 5)
  - `RATE_LIMIT_UPLOAD_FOTO_MINUTOS` (padrão: 10)

### 2. Alteração de Senha ✅
- **Endpoint**: `POST /usuario/perfil/alterar-senha`
- **Arquivo**: `routes/usuario_routes.py:190-291`
- **Limite**: 5 tentativas / 15 minutos
- **Proteção contra**: Brute force na validação de senha atual
- **Variáveis de ambiente**:
  - `RATE_LIMIT_ALTERAR_SENHA_MAX` (padrão: 5)
  - `RATE_LIMIT_ALTERAR_SENHA_MINUTOS` (padrão: 15)

### 3. Envio de Mensagens no Chat ✅
- **Endpoint**: `POST /chat/mensagens`
- **Arquivo**: `routes/chat_routes.py:261-331`
- **Limite**: 30 mensagens / 1 minuto
- **Proteção contra**: Spam, flooding, assédio via chat
- **Variáveis de ambiente**:
  - `RATE_LIMIT_CHAT_MESSAGE_MAX` (padrão: 30)
  - `RATE_LIMIT_CHAT_MESSAGE_MINUTOS` (padrão: 1)

### 4. Criação de Salas de Chat ✅
- **Endpoint**: `POST /chat/salas`
- **Arquivo**: `routes/chat_routes.py:83-144`
- **Limite**: 10 salas / 10 minutos
- **Proteção contra**: Poluição do banco de dados, criação abusiva de salas
- **Variáveis de ambiente**:
  - `RATE_LIMIT_CHAT_SALA_MAX` (padrão: 10)
  - `RATE_LIMIT_CHAT_SALA_MINUTOS` (padrão: 10)

## Arquivos Modificados

### 1. `util/config.py`
Adicionadas configurações de rate limiting:
```python
# Upload de Foto de Perfil
RATE_LIMIT_UPLOAD_FOTO_MAX = int(os.getenv("RATE_LIMIT_UPLOAD_FOTO_MAX", "5"))
RATE_LIMIT_UPLOAD_FOTO_MINUTOS = int(os.getenv("RATE_LIMIT_UPLOAD_FOTO_MINUTOS", "10"))

# Alteração de Senha
RATE_LIMIT_ALTERAR_SENHA_MAX = int(os.getenv("RATE_LIMIT_ALTERAR_SENHA_MAX", "5"))
RATE_LIMIT_ALTERAR_SENHA_MINUTOS = int(os.getenv("RATE_LIMIT_ALTERAR_SENHA_MINUTOS", "15"))

# Chat - Mensagens
RATE_LIMIT_CHAT_MESSAGE_MAX = int(os.getenv("RATE_LIMIT_CHAT_MESSAGE_MAX", "30"))
RATE_LIMIT_CHAT_MESSAGE_MINUTOS = int(os.getenv("RATE_LIMIT_CHAT_MESSAGE_MINUTOS", "1"))

# Chat - Salas
RATE_LIMIT_CHAT_SALA_MAX = int(os.getenv("RATE_LIMIT_CHAT_SALA_MAX", "10"))
RATE_LIMIT_CHAT_SALA_MINUTOS = int(os.getenv("RATE_LIMIT_CHAT_SALA_MINUTOS", "10"))
```

### 2. `routes/usuario_routes.py`
- Importadas configurações de rate limiting
- Criados rate limiters globais (`upload_foto_limiter`, `alterar_senha_limiter`)
- Aplicada verificação de rate limiting nos endpoints POST

### 3. `routes/chat_routes.py`
- Importadas configurações de rate limiting
- Criados rate limiters globais (`chat_mensagem_limiter`, `chat_sala_limiter`)
- Aplicada verificação de rate limiting nos endpoints POST

## Padrão de Implementação

Todos os endpoints seguem o mesmo padrão de implementação:

```python
# 1. Importar configurações
from util.config import (
    RATE_LIMIT_XXX_MAX,
    RATE_LIMIT_XXX_MINUTOS,
)

# 2. Importar rate limiter
from util.rate_limiter import RateLimiter, obter_identificador_cliente

# 3. Criar instância global
xxx_limiter = RateLimiter(
    max_tentativas=RATE_LIMIT_XXX_MAX,
    janela_minutos=RATE_LIMIT_XXX_MINUTOS,
    nome="xxx",
)

# 4. Aplicar no endpoint
@router.post("/endpoint")
@requer_autenticacao()
async def endpoint(request: Request, ...):
    # Rate limiting por IP
    ip = obter_identificador_cliente(request)
    if not xxx_limiter.verificar(ip):
        # Para endpoints que retornam templates:
        informar_erro(request, f"Muitas tentativas. Aguarde {RATE_LIMIT_XXX_MINUTOS} minuto(s).")
        return templates.TemplateResponse(...)

        # Para endpoints API (JSON):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Muitas tentativas. Aguarde {RATE_LIMIT_XXX_MINUTOS} minuto(s)."
        )

    # Lógica normal do endpoint...
```

## Testes

### Script de Testes
Criado `test_rate_limiting_simple.py` que valida:
- ✅ Rate limiter aceita exatamente `max_tentativas` requisições
- ✅ Rate limiter bloqueia requisições após atingir o limite
- ✅ Status HTTP 429 (Too Many Requests) é retornado
- ✅ Logging adequado de tentativas bloqueadas

### Resultados dos Testes
```
============================================================
RESUMO FINAL
============================================================
Upload de Foto            ✅ PASSOU
Alteração de Senha        ✅ PASSOU
Envio de Mensagens        ✅ PASSOU
Criação de Salas          ✅ PASSOU

Total: 4/4 testes passaram

🎉 TODOS OS TESTES DA FASE 1 PASSARAM! 🎉
```

## Configuração (Opcional)

Para ajustar os limites de rate limiting, adicione ao arquivo `.env`:

```bash
# Upload de Foto de Perfil
RATE_LIMIT_UPLOAD_FOTO_MAX=5
RATE_LIMIT_UPLOAD_FOTO_MINUTOS=10

# Alteração de Senha
RATE_LIMIT_ALTERAR_SENHA_MAX=5
RATE_LIMIT_ALTERAR_SENHA_MINUTOS=15

# Chat - Mensagens
RATE_LIMIT_CHAT_MESSAGE_MAX=30
RATE_LIMIT_CHAT_MESSAGE_MINUTOS=1

# Chat - Salas
RATE_LIMIT_CHAT_SALA_MAX=10
RATE_LIMIT_CHAT_SALA_MINUTOS=10
```

## Características do Rate Limiter

- **Algoritmo**: Janela deslizante (sliding window)
- **Identificação**: Por endereço IP do cliente
- **Armazenamento**: Em memória (via `defaultdict`)
- **Thread-safe**: Sim
- **Logging**: Automático para tentativas bloqueadas
- **Limpeza**: Automática de tentativas antigas fora da janela

## Limitações Conhecidas

1. **Armazenamento em memória**: Os contadores resetam ao reiniciar a aplicação
2. **Múltiplos workers**: Em produção com múltiplos workers (Gunicorn/Uvicorn), cada worker mantém seu próprio contador
3. **Ambiente distribuído**: Não funciona em múltiplos servidores sem storage compartilhado

### Solução para Produção

Para ambientes de produção com múltiplos workers ou servidores, considere:
- **Redis**: Armazenamento compartilhado, rápido e distribuído
- **Database**: Persistente, mas mais lento
- **Memcached**: Rápido, mas sem persistência

## Próximas Fases

### Fase 2 - Alta Prioridade (Próxima Semana)
- Criação de chamados (`/chamados/cadastrar`)
- Respostas em chamados (usuário e admin)
- Busca de usuários no chat (`/chat/usuarios/buscar`)

### Fase 3 - Média Prioridade (Próximas 2 Semanas)
- Operações CRUD de tarefas
- Listagem de conversas e mensagens do chat
- Download de backups admin

### Fase 4 - Opcional
- Páginas públicas (proteção DDoS)
- Páginas de exemplos

## Logs

Quando o rate limiting é ativado, são gerados logs no formato:

```
2025-10-28 21:06:32 - root - WARNING - Rate limit excedido [upload_foto] - Identificador: 127.0.0.1, Tentativas: 5/5
```

Isso facilita monitoramento e detecção de possíveis ataques ou comportamento abusivo.

## Status

✅ **Fase 1 Completa e Testada** (28/10/2025)

Todos os 4 endpoints críticos estão protegidos e funcionando corretamente.
