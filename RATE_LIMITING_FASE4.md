# Rate Limiting - Fase 4 (Implementado)

## Resumo

Implementação bem-sucedida de rate limiting para os **14 endpoints de baixa prioridade** da aplicação, conforme Fase 4 do plano de implementação.

Esta fase protege contra uso excessivo de formulários GET e ataques DDoS em páginas públicas e de exemplos.

## Endpoints Protegidos

### 14-15. Formulários GET de Perfil ✅
- **Endpoints**:
  - `GET /usuario/perfil/editar`
  - `GET /usuario/perfil/alterar-senha`
- **Arquivo**: `routes/usuario_routes.py:92-100, 195-207`
- **Limite**: 60 requisições / 1 minuto
- **Proteção contra**: Enumeração de usuários, scraping de dados
- **Variáveis de ambiente**:
  - `RATE_LIMIT_FORM_GET_MAX` (padrão: 60)
  - `RATE_LIMIT_FORM_GET_MINUTOS` (padrão: 1)

### 16-18. Páginas Públicas ✅
- **Endpoints**:
  - `GET /` (landing page)
  - `GET /index`
  - `GET /sobre`
- **Arquivo**: `routes/public_routes.py:25-89`
- **Limite**: 100 requisições / 1 minuto (compartilhado entre todos endpoints)
- **Proteção contra**: Ataques DDoS, sobrecarga do servidor
- **Variáveis de ambiente**:
  - `RATE_LIMIT_PUBLIC_MAX` (padrão: 100)
  - `RATE_LIMIT_PUBLIC_MINUTOS` (padrão: 1)

### 19-27. Páginas de Exemplos ✅
- **Endpoints**:
  - `GET /exemplos/` (índice)
  - `GET /exemplos/campos-formulario`
  - `GET /exemplos/grade-cartoes`
  - `GET /exemplos/bootswatch`
  - `GET /exemplos/detalhes-produto`
  - `GET /exemplos/detalhes-servico`
  - `GET /exemplos/detalhes-perfil`
  - `GET /exemplos/detalhes-imovel`
  - `GET /exemplos/lista-tabela`
- **Arquivo**: `routes/examples_routes.py:23-232`
- **Limite**: 100 requisições / 1 minuto (compartilhado entre todos endpoints)
- **Proteção contra**: Ataques DDoS, sobrecarga do servidor
- **Variáveis de ambiente**:
  - `RATE_LIMIT_EXAMPLES_MAX` (padrão: 100)
  - `RATE_LIMIT_EXAMPLES_MINUTOS` (padrão: 1)

## Arquivos Modificados

### 1. `util/config.py`
Adicionadas configurações de rate limiting:
```python
# Formulários GET (Edição de Perfil)
RATE_LIMIT_FORM_GET_MAX = int(os.getenv("RATE_LIMIT_FORM_GET_MAX", "60"))
RATE_LIMIT_FORM_GET_MINUTOS = int(os.getenv("RATE_LIMIT_FORM_GET_MINUTOS", "1"))

# Páginas Públicas
RATE_LIMIT_PUBLIC_MAX = int(os.getenv("RATE_LIMIT_PUBLIC_MAX", "100"))
RATE_LIMIT_PUBLIC_MINUTOS = int(os.getenv("RATE_LIMIT_PUBLIC_MINUTOS", "1"))

# Páginas de Exemplos
RATE_LIMIT_EXAMPLES_MAX = int(os.getenv("RATE_LIMIT_EXAMPLES_MAX", "100"))
RATE_LIMIT_EXAMPLES_MINUTOS = int(os.getenv("RATE_LIMIT_EXAMPLES_MINUTOS", "1"))
```

### 2. `routes/usuario_routes.py`
- Importadas configurações adicionais de rate limiting
- Criado rate limiter global (`form_get_limiter`)
- Aplicada verificação de rate limiting nos endpoints GET de formulários
- Resposta em caso de limite: redirect para `/usuario` com mensagem de erro

### 3. `routes/public_routes.py`
- Importadas configurações de rate limiting
- Importado status HTTP e RedirectResponse
- Criado rate limiter global compartilhado (`public_limiter`)
- Aplicada verificação de rate limiting nos 3 endpoints GET
- Resposta em caso de limite: template `errors/429.html` com status 429

### 4. `routes/examples_routes.py`
- Importadas configurações de rate limiting
- Criado rate limiter global compartilhado (`examples_limiter`)
- Aplicada verificação de rate limiting nos 9 endpoints GET
- Resposta em caso de limite: template `errors/429.html` com status 429

### 5. `templates/errors/429.html` (NOVO)
- Criado template de erro para HTTP 429 (Too Many Requests)
- Design consistente com outros templates de erro (404, 500)
- Mensagem amigável explicando rate limiting
- Botões de navegação para home e dashboard/login

## Testes

### Script de Testes
Criado `test_rate_limiting_fase4.py` que valida:
- ✅ Rate limiter aceita exatamente `max_tentativas` requisições
- ✅ Rate limiter bloqueia requisições após atingir o limite
- ✅ Status HTTP 429 (Too Many Requests) é retornado
- ✅ Logging adequado de tentativas bloqueadas
- ✅ Rate limiters compartilhados funcionam corretamente

### Resultados dos Testes
```
============================================================
RESUMO FINAL
============================================================
Formulários GET                     ✅ PASSOU
Páginas Públicas                    ✅ PASSOU
Páginas de Exemplos                 ✅ PASSOU

Total: 3/3 testes passaram
```

**Observação**: Todos os testes passaram com sucesso, demonstrando que o rate limiting está funcionando corretamente para todos os grupos de endpoints.

## Configuração (Opcional)

Para ajustar os limites de rate limiting, adicione ao arquivo `.env`:

```bash
# Formulários GET (Edição de Perfil)
RATE_LIMIT_FORM_GET_MAX=60
RATE_LIMIT_FORM_GET_MINUTOS=1

# Páginas Públicas
RATE_LIMIT_PUBLIC_MAX=100
RATE_LIMIT_PUBLIC_MINUTOS=1

# Páginas de Exemplos
RATE_LIMIT_EXAMPLES_MAX=100
RATE_LIMIT_EXAMPLES_MINUTOS=1
```

## Padrão de Rate Limiters Compartilhados

Esta fase utiliza extensivamente o conceito de **rate limiters compartilhados** entre múltiplos endpoints:

### Exemplo 1: Páginas Públicas
- `GET /`
- `GET /index`
- `GET /sobre`
- **Compartilham**: `public_limiter`
- **Razão**: Todas são páginas públicas que devem ser protegidas em conjunto contra DDoS

### Exemplo 2: Páginas de Exemplos
- Todos os 9 endpoints `/exemplos/*`
- **Compartilham**: `examples_limiter`
- **Razão**: Todas são páginas de demonstração e devem compartilhar o mesmo limite

Este padrão evita que usuários contornem o rate limiting alternando entre endpoints similares.

## Tratamento de Erros

### Páginas Públicas e Exemplos
Quando o rate limiting é ativado:
1. Retorna template `errors/429.html` com status HTTP 429
2. Exibe mensagem flash de erro ao usuário
3. Gera log de warning com IP do cliente
4. Template oferece navegação para home ou login/dashboard

### Formulários GET
Quando o rate limiting é ativado:
1. Redireciona para `/usuario` com status HTTP 303
2. Exibe mensagem flash de erro ao usuário
3. Gera log de warning com IP do cliente

## Logs

Quando o rate limiting é ativado, são gerados logs no formato:

```
2025-10-28 21:26:43 - root - WARNING - Rate limit excedido [form_get] - Identificador: 127.0.0.1, Tentativas: 60/60
2025-10-28 21:26:48 - root - WARNING - Rate limit excedido [public_pages] - Identificador: 127.0.0.1, Tentativas: 100/100
2025-10-28 21:26:53 - root - WARNING - Rate limit excedido [examples_pages] - Identificador: 127.0.0.1, Tentativas: 100/100
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

### Fase 3 (Média Prioridade) - 5 endpoints:
9. ✅ Criação de tarefas (20 tarefas / 10 min)
10. ✅ Operações em tarefas - concluir/excluir (30 operações / 5 min)
11. ✅ Listagem de conversas do chat (60 requisições / 1 min)
12. ✅ Listagem de mensagens do chat (60 requisições / 1 min - compartilhado com #11)
13. ✅ Download de backups (5 downloads / 10 min)

### Fase 4 (Baixa Prioridade) - 14 endpoints:
14-15. ✅ Formulários GET de perfil (60 requisições / 1 min - 2 endpoints)
16-18. ✅ Páginas públicas (100 requisições / 1 min - 3 endpoints)
19-27. ✅ Páginas de exemplos (100 requisições / 1 min - 9 endpoints)

**Total de Endpoints Protegidos**: **27 endpoints** (100% de cobertura dos endpoints críticos)

## Benefícios da Implementação

1. **Proteção contra DDoS**: Páginas públicas e exemplos agora resistem a ataques de negação de serviço
2. **Prevenção de Scraping**: Formulários GET limitados impedem extração automatizada de dados
3. **Conservação de Recursos**: Limita uso excessivo do servidor
4. **Experiência do Usuário**: Usuários legítimos raramente atingirão os limites generosos
5. **Monitoramento**: Logs permitem identificar tentativas de abuso

## Limites Generosos

Os limites da Fase 4 são **intencionalmente generosos** (60-100 req/min):
- **60 req/min para forms GET**: Permite navegação normal sem restrições
- **100 req/min para públicas**: Permite crawlers legítimos e tráfego orgânico alto
- **100 req/min para exemplos**: Facilita exploração de demos sem frustração

Esses limites protegem contra abuso extremo sem impactar usuários normais.

## Status

✅ **Fase 4 Completa e Testada** (28/10/2025)

Todos os 14 endpoints de baixa prioridade estão protegidos e funcionando corretamente, incluindo:
- Template de erro 429 customizado
- Rate limiters compartilhados entre endpoints similares
- Tratamento diferenciado por tipo de endpoint
- Limites generosos para não impactar usuários legítimos

## Próximos Passos

Com a conclusão da Fase 4, **TODO O SISTEMA DE RATE LIMITING ESTÁ COMPLETO**:
- ✅ Fase 1 (Crítico) - 4 endpoints
- ✅ Fase 2 (Alta Prioridade) - 4 endpoints
- ✅ Fase 3 (Média Prioridade) - 5 endpoints
- ✅ Fase 4 (Baixa Prioridade) - 14 endpoints

**Total**: 27 endpoints protegidos com rate limiting configurável e testado.

Próximo passo recomendado: Criar documentação consolidada final com visão geral completa do sistema de rate limiting.
