# Rate Limiting - Fase 2 (Implementado)

## Resumo

Implementação bem-sucedida de rate limiting para os 4 endpoints de **alta prioridade** da aplicação, conforme Fase 2 do plano de implementação.

## Endpoints Protegidos

### 5. Criação de Chamados ✅
- **Endpoint**: `POST /chamados/cadastrar`
- **Arquivo**: `routes/chamados_routes.py:76-146`
- **Limite**: 5 chamados / 30 minutos
- **Proteção contra**: Spam de tickets de suporte, poluição do banco
- **Variáveis de ambiente**:
  - `RATE_LIMIT_CHAMADO_CRIAR_MAX` (padrão: 5)
  - `RATE_LIMIT_CHAMADO_CRIAR_MINUTOS` (padrão: 30)

### 6. Respostas em Chamados (Usuário) ✅
- **Endpoint**: `POST /chamados/{id}/responder`
- **Arquivo**: `routes/chamados_routes.py:187-243`
- **Limite**: 10 respostas / 10 minutos
- **Proteção contra**: Spam de mensagens em tickets
- **Variáveis de ambiente**:
  - `RATE_LIMIT_CHAMADO_RESPONDER_MAX` (padrão: 10)
  - `RATE_LIMIT_CHAMADO_RESPONDER_MINUTOS` (padrão: 10)

### 7. Respostas em Chamados (Admin) ✅
- **Endpoint**: `POST /admin/chamados/{id}/responder`
- **Arquivo**: `routes/admin_chamados_routes.py:82-157`
- **Limite**: 20 respostas / 5 minutos
- **Proteção contra**: Respostas acidentais duplicadas
- **Variáveis de ambiente**:
  - `RATE_LIMIT_ADMIN_CHAMADO_RESPONDER_MAX` (padrão: 20)
  - `RATE_LIMIT_ADMIN_CHAMADO_RESPONDER_MINUTOS` (padrão: 5)

### 8. Busca de Usuários no Chat ✅
- **Endpoint**: `GET /chat/usuarios/buscar`
- **Arquivo**: `routes/chat_routes.py:388-440`
- **Limite**: 30 buscas / 1 minuto
- **Proteção contra**: Enumeração de usuários, queries LIKE excessivas
- **Variáveis de ambiente**:
  - `RATE_LIMIT_BUSCA_USUARIOS_MAX` (padrão: 30)
  - `RATE_LIMIT_BUSCA_USUARIOS_MINUTOS` (padrão: 1)

## Arquivos Modificados

### 1. `util/config.py`
Adicionadas configurações de rate limiting:
```python
# Chat - Busca de Usuários
RATE_LIMIT_BUSCA_USUARIOS_MAX = int(os.getenv("RATE_LIMIT_BUSCA_USUARIOS_MAX", "30"))
RATE_LIMIT_BUSCA_USUARIOS_MINUTOS = int(os.getenv("RATE_LIMIT_BUSCA_USUARIOS_MINUTOS", "1"))

# Chamados - Criação
RATE_LIMIT_CHAMADO_CRIAR_MAX = int(os.getenv("RATE_LIMIT_CHAMADO_CRIAR_MAX", "5"))
RATE_LIMIT_CHAMADO_CRIAR_MINUTOS = int(os.getenv("RATE_LIMIT_CHAMADO_CRIAR_MINUTOS", "30"))

# Chamados - Respostas (Usuário)
RATE_LIMIT_CHAMADO_RESPONDER_MAX = int(os.getenv("RATE_LIMIT_CHAMADO_RESPONDER_MAX", "10"))
RATE_LIMIT_CHAMADO_RESPONDER_MINUTOS = int(os.getenv("RATE_LIMIT_CHAMADO_RESPONDER_MINUTOS", "10"))

# Chamados - Respostas (Admin)
RATE_LIMIT_ADMIN_CHAMADO_RESPONDER_MAX = int(os.getenv("RATE_LIMIT_ADMIN_CHAMADO_RESPONDER_MAX", "20"))
RATE_LIMIT_ADMIN_CHAMADO_RESPONDER_MINUTOS = int(os.getenv("RATE_LIMIT_ADMIN_CHAMADO_RESPONDER_MINUTOS", "5"))
```

### 2. `routes/chamados_routes.py`
- Importadas configurações de rate limiting
- Criados rate limiters globais (`chamado_criar_limiter`, `chamado_responder_limiter`)
- Aplicada verificação de rate limiting nos endpoints POST

### 3. `routes/admin_chamados_routes.py`
- Importadas configurações de rate limiting
- Criado rate limiter global (`admin_chamado_responder_limiter`)
- Aplicada verificação de rate limiting no endpoint de responder

### 4. `routes/chat_routes.py`
- Importada configuração adicional de rate limiting
- Criado rate limiter global (`busca_usuarios_limiter`)
- Aplicada verificação de rate limiting no endpoint GET de busca

## Testes

### Script de Testes
Criado `test_rate_limiting_fase2.py` que valida:
- ✅ Rate limiter aceita exatamente `max_tentativas` requisições
- ✅ Rate limiter bloqueia requisições após atingir o limite
- ✅ Status HTTP 429 (Too Many Requests) é retornado
- ✅ Logging adequado de tentativas bloqueadas

### Resultados dos Testes
```
============================================================
RESUMO FINAL
============================================================
Criação de Chamados                 ✅ PASSOU
Resposta em Chamados (Usuário)      ✅ PASSOU
Resposta em Chamados (Admin)        ✅ PASSOU
Busca de Usuários                   ✅ PASSOU

Total: 4/4 testes passaram

🎉 TODOS OS TESTES DA FASE 2 PASSARAM! 🎉
```

## Configuração (Opcional)

Para ajustar os limites de rate limiting, adicione ao arquivo `.env`:

```bash
# Chat - Busca de Usuários
RATE_LIMIT_BUSCA_USUARIOS_MAX=30
RATE_LIMIT_BUSCA_USUARIOS_MINUTOS=1

# Chamados - Criação
RATE_LIMIT_CHAMADO_CRIAR_MAX=5
RATE_LIMIT_CHAMADO_CRIAR_MINUTOS=30

# Chamados - Respostas (Usuário)
RATE_LIMIT_CHAMADO_RESPONDER_MAX=10
RATE_LIMIT_CHAMADO_RESPONDER_MINUTOS=10

# Chamados - Respostas (Admin)
RATE_LIMIT_ADMIN_CHAMADO_RESPONDER_MAX=20
RATE_LIMIT_ADMIN_CHAMADO_RESPONDER_MINUTOS=5
```

## Padrão de Implementação

Todos os endpoints seguem o mesmo padrão da Fase 1:

### Para endpoints que retornam templates (HTML):
```python
# Rate limiting por IP
ip = obter_identificador_cliente(request)
if not xxx_limiter.verificar(ip):
    informar_erro(request, f"Muitas tentativas. Aguarde {RATE_LIMIT_XXX_MINUTOS} minuto(s).")
    logger.warning(f"Rate limit excedido - IP: {ip}")
    return templates.TemplateResponse(...)
```

### Para endpoints API (JSON):
```python
# Rate limiting por IP
ip = obter_identificador_cliente(request)
if not xxx_limiter.verificar(ip):
    logger.warning(f"Rate limit excedido - IP: {ip}")
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=f"Muitas tentativas. Aguarde {RATE_LIMIT_XXX_MINUTOS} minuto(s)."
    )
```

## Logs

Quando o rate limiting é ativado, são gerados logs no formato:

```
2025-10-28 21:12:54 - root - WARNING - Rate limit excedido [chamado_criar] - Identificador: 127.0.0.1, Tentativas: 5/5
2025-10-28 21:12:54 - root - WARNING - Rate limit excedido [chamado_responder] - Identificador: 127.0.0.1, Tentativas: 10/10
2025-10-28 21:12:55 - root - WARNING - Rate limit excedido [admin_chamado_responder] - Identificador: 127.0.0.1, Tentativas: 20/20
2025-10-28 21:12:57 - root - WARNING - Rate limit excedido [busca_usuarios] - Identificador: 127.0.0.1, Tentativas: 30/30
```

## Endpoints Protegidos até Agora

### Fase 1 (Crítico) - 4 endpoints:
1. ✅ Upload de foto de perfil (5 uploads / 10 min)
2. ✅ Alteração de senha (5 tentativas / 15 min)
3. ✅ Envio de mensagens no chat (30 mensagens / 1 min)
4. ✅ Criação de salas de chat (10 salas / 10 min)

### Fase 2 (Alta Prioridade) - 4 endpoints:
5. ✅ Criação de chamados (5 chamados / 30 min)
6. ✅ Respostas em chamados - usuário (10 respostas / 10 min)
7. ✅ Respostas em chamados - admin (20 respostas / 5 min)
8. ✅ Busca de usuários no chat (30 buscas / 1 min)

**Total de Endpoints Protegidos**: **8 de 24** (33% de cobertura)

## Próximas Fases

### Fase 3 - Média Prioridade (Próximas 2 Semanas)
- Criação de tarefas (`/tarefas/cadastrar`)
- Operações em tarefas - concluir/excluir (`/tarefas/{id}/concluir`, `/tarefas/{id}/excluir`)
- Listagem de conversas do chat (`/chat/conversas`)
- Histórico de mensagens (`/chat/mensagens/{sala_id}`)
- Download de backups (`/admin/backups/download/{nome_arquivo}`)

### Fase 4 - Opcional
- Formulários de edição de perfil (GET)
- Páginas públicas (proteção DDoS)
- Páginas de exemplos

## Status

✅ **Fase 2 Completa e Testada** (28/10/2025)

Todos os 4 endpoints de alta prioridade estão protegidos e funcionando corretamente.
