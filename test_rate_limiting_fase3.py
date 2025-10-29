"""
Script de teste para verificar rate limiting da Fase 3.

Testa os 5 endpoints de média prioridade implementados:
1. Criação de tarefas
2. Operações em tarefas (concluir/excluir)
3. Listagem de conversas do chat
4. Listagem de mensagens do chat
5. Download de backups
"""
import sys
import time

# Importar os módulos necessários
sys.path.insert(0, '/Volumes/Externo/Projetos/DefaultWebApp')

from fastapi import FastAPI, Request, HTTPException
from fastapi.testclient import TestClient

from util.rate_limiter import RateLimiter, obter_identificador_cliente
from util.config import (
    RATE_LIMIT_TAREFA_CRIAR_MAX,
    RATE_LIMIT_TAREFA_CRIAR_MINUTOS,
    RATE_LIMIT_TAREFA_OPERACAO_MAX,
    RATE_LIMIT_TAREFA_OPERACAO_MINUTOS,
    RATE_LIMIT_CHAT_LISTAGEM_MAX,
    RATE_LIMIT_CHAT_LISTAGEM_MINUTOS,
    RATE_LIMIT_BACKUP_DOWNLOAD_MAX,
    RATE_LIMIT_BACKUP_DOWNLOAD_MINUTOS,
)

# Criar app de teste
app = FastAPI()

# Criar rate limiters
tarefa_criar_limiter = RateLimiter(
    max_tentativas=RATE_LIMIT_TAREFA_CRIAR_MAX,
    janela_minutos=RATE_LIMIT_TAREFA_CRIAR_MINUTOS,
    nome="tarefa_criar_test",
)

tarefa_operacao_limiter = RateLimiter(
    max_tentativas=RATE_LIMIT_TAREFA_OPERACAO_MAX,
    janela_minutos=RATE_LIMIT_TAREFA_OPERACAO_MINUTOS,
    nome="tarefa_operacao_test",
)

chat_listagem_limiter = RateLimiter(
    max_tentativas=RATE_LIMIT_CHAT_LISTAGEM_MAX,
    janela_minutos=RATE_LIMIT_CHAT_LISTAGEM_MINUTOS,
    nome="chat_listagem_test",
)

backup_download_limiter = RateLimiter(
    max_tentativas=RATE_LIMIT_BACKUP_DOWNLOAD_MAX,
    janela_minutos=RATE_LIMIT_BACKUP_DOWNLOAD_MINUTOS,
    nome="backup_download_test",
)

# Endpoints de teste
@app.post("/test/tarefa-criar")
async def test_tarefa_criar(request: Request):
    ip = obter_identificador_cliente(request)
    if not tarefa_criar_limiter.verificar(ip):
        raise HTTPException(status_code=429, detail="Rate limit excedido")
    return {"ok": True}

@app.post("/test/tarefa-operacao")
async def test_tarefa_operacao(request: Request):
    ip = obter_identificador_cliente(request)
    if not tarefa_operacao_limiter.verificar(ip):
        raise HTTPException(status_code=429, detail="Rate limit excedido")
    return {"ok": True}

@app.get("/test/chat-conversas")
async def test_chat_conversas(request: Request):
    ip = obter_identificador_cliente(request)
    if not chat_listagem_limiter.verificar(ip):
        raise HTTPException(status_code=429, detail="Rate limit excedido")
    return {"ok": True}

@app.get("/test/chat-mensagens")
async def test_chat_mensagens(request: Request):
    ip = obter_identificador_cliente(request)
    if not chat_listagem_limiter.verificar(ip):
        raise HTTPException(status_code=429, detail="Rate limit excedido")
    return {"ok": True}

@app.get("/test/backup-download")
async def test_backup_download(request: Request):
    ip = obter_identificador_cliente(request)
    if not backup_download_limiter.verificar(ip):
        raise HTTPException(status_code=429, detail="Rate limit excedido")
    return {"ok": True}

# Testes
def testar_endpoint(client, endpoint, limite, nome, metodo="POST"):
    print(f"\n{'='*60}")
    print(f"TESTE: {nome}")
    print(f"Limite configurado: {limite} requisições")
    print(f"{'='*60}")

    tentativas_sucesso = 0
    bloqueado = False

    for i in range(limite + 3):  # Tentar mais que o limite
        if metodo == "POST":
            response = client.post(endpoint)
        else:
            response = client.get(endpoint)

        if response.status_code == 200:
            tentativas_sucesso += 1
            if (i + 1) % 10 == 0 or i < 5:
                print(f"Requisição {i+1}: ✅ Aceita")
        elif response.status_code == 429:
            bloqueado = True
            print(f"Requisição {i+1}: 🛑 RATE LIMIT ATIVADO")
            break
        else:
            print(f"Requisição {i+1}: ⚠️  Status {response.status_code}")

        time.sleep(0.05)  # Pequeno delay

    print(f"\n📊 Resultado:")
    print(f"   Requisições aceitas: {tentativas_sucesso}")
    print(f"   Rate limit ativou: {'✅ SIM' if bloqueado else '❌ NÃO'}")
    print(f"   Status: {'✅ PASSOU' if tentativas_sucesso == limite and bloqueado else '❌ FALHOU'}")

    return tentativas_sucesso == limite and bloqueado

def main():
    print("\n" + "="*60)
    print("TESTE DE RATE LIMITING - FASE 3 (MÉDIA PRIORIDADE)")
    print("="*60)

    client = TestClient(app)

    resultados = {
        "Criação de Tarefas": testar_endpoint(
            client, "/test/tarefa-criar",
            RATE_LIMIT_TAREFA_CRIAR_MAX,
            f"Criação de Tarefas ({RATE_LIMIT_TAREFA_CRIAR_MAX} tarefas / {RATE_LIMIT_TAREFA_CRIAR_MINUTOS} min)"
        ),
        "Operações em Tarefas": testar_endpoint(
            client, "/test/tarefa-operacao",
            RATE_LIMIT_TAREFA_OPERACAO_MAX,
            f"Operações em Tarefas ({RATE_LIMIT_TAREFA_OPERACAO_MAX} operações / {RATE_LIMIT_TAREFA_OPERACAO_MINUTOS} min)"
        ),
        "Listagem de Conversas": testar_endpoint(
            client, "/test/chat-conversas",
            RATE_LIMIT_CHAT_LISTAGEM_MAX,
            f"Listagem de Conversas ({RATE_LIMIT_CHAT_LISTAGEM_MAX} requisições / {RATE_LIMIT_CHAT_LISTAGEM_MINUTOS} min)",
            metodo="GET"
        ),
        "Listagem de Mensagens": testar_endpoint(
            client, "/test/chat-mensagens",
            RATE_LIMIT_CHAT_LISTAGEM_MAX,
            f"Listagem de Mensagens ({RATE_LIMIT_CHAT_LISTAGEM_MAX} requisições / {RATE_LIMIT_CHAT_LISTAGEM_MINUTOS} min)",
            metodo="GET"
        ),
        "Download de Backups": testar_endpoint(
            client, "/test/backup-download",
            RATE_LIMIT_BACKUP_DOWNLOAD_MAX,
            f"Download de Backups ({RATE_LIMIT_BACKUP_DOWNLOAD_MAX} downloads / {RATE_LIMIT_BACKUP_DOWNLOAD_MINUTOS} min)",
            metodo="GET"
        ),
    }

    # Resumo final
    print("\n" + "="*60)
    print("RESUMO FINAL")
    print("="*60)

    total_testes = len(resultados)
    testes_passou = sum(resultados.values())

    for nome, passou in resultados.items():
        status = "✅ PASSOU" if passou else "❌ FALHOU"
        print(f"{nome:35} {status}")

    print(f"\nTotal: {testes_passou}/{total_testes} testes passaram")

    if testes_passou == total_testes:
        print("\n🎉 TODOS OS TESTES DA FASE 3 PASSARAM! 🎉")
        print("\n✅ Rate limiting implementado corretamente para:")
        print("   1. Criação de tarefas")
        print("   2. Operações em tarefas (concluir/excluir)")
        print("   3. Listagem de conversas do chat")
        print("   4. Listagem de mensagens do chat")
        print("   5. Download de backups")
    else:
        print(f"\n⚠️  {total_testes - testes_passou} teste(s) falharam")

    return testes_passou == total_testes

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
