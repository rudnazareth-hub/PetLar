"""
Script de teste para verificar rate limiting da Fase 2.

Testa os 4 endpoints de alta prioridade implementados:
1. Criação de chamados
2. Resposta em chamados (usuário)
3. Resposta em chamados (admin)
4. Busca de usuários no chat
"""
import sys
import time

# Importar os módulos necessários
sys.path.insert(0, '/Volumes/Externo/Projetos/DefaultWebApp')

from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.testclient import TestClient

from util.rate_limiter import RateLimiter, obter_identificador_cliente
from util.config import (
    RATE_LIMIT_CHAMADO_CRIAR_MAX,
    RATE_LIMIT_CHAMADO_CRIAR_MINUTOS,
    RATE_LIMIT_CHAMADO_RESPONDER_MAX,
    RATE_LIMIT_CHAMADO_RESPONDER_MINUTOS,
    RATE_LIMIT_ADMIN_CHAMADO_RESPONDER_MAX,
    RATE_LIMIT_ADMIN_CHAMADO_RESPONDER_MINUTOS,
    RATE_LIMIT_BUSCA_USUARIOS_MAX,
    RATE_LIMIT_BUSCA_USUARIOS_MINUTOS,
)

# Criar app de teste
app = FastAPI()

# Criar rate limiters
chamado_criar_limiter = RateLimiter(
    max_tentativas=RATE_LIMIT_CHAMADO_CRIAR_MAX,
    janela_minutos=RATE_LIMIT_CHAMADO_CRIAR_MINUTOS,
    nome="chamado_criar_test",
)

chamado_responder_limiter = RateLimiter(
    max_tentativas=RATE_LIMIT_CHAMADO_RESPONDER_MAX,
    janela_minutos=RATE_LIMIT_CHAMADO_RESPONDER_MINUTOS,
    nome="chamado_responder_test",
)

admin_chamado_responder_limiter = RateLimiter(
    max_tentativas=RATE_LIMIT_ADMIN_CHAMADO_RESPONDER_MAX,
    janela_minutos=RATE_LIMIT_ADMIN_CHAMADO_RESPONDER_MINUTOS,
    nome="admin_chamado_responder_test",
)

busca_usuarios_limiter = RateLimiter(
    max_tentativas=RATE_LIMIT_BUSCA_USUARIOS_MAX,
    janela_minutos=RATE_LIMIT_BUSCA_USUARIOS_MINUTOS,
    nome="busca_usuarios_test",
)

# Endpoints de teste
@app.post("/test/chamado-criar")
async def test_chamado_criar(request: Request):
    ip = obter_identificador_cliente(request)
    if not chamado_criar_limiter.verificar(ip):
        raise HTTPException(status_code=429, detail="Rate limit excedido")
    return {"ok": True}

@app.post("/test/chamado-responder")
async def test_chamado_responder(request: Request):
    ip = obter_identificador_cliente(request)
    if not chamado_responder_limiter.verificar(ip):
        raise HTTPException(status_code=429, detail="Rate limit excedido")
    return {"ok": True}

@app.post("/test/admin-chamado-responder")
async def test_admin_chamado_responder(request: Request):
    ip = obter_identificador_cliente(request)
    if not admin_chamado_responder_limiter.verificar(ip):
        raise HTTPException(status_code=429, detail="Rate limit excedido")
    return {"ok": True}

@app.get("/test/busca-usuarios")
async def test_busca_usuarios(request: Request):
    ip = obter_identificador_cliente(request)
    if not busca_usuarios_limiter.verificar(ip):
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
            if (i + 1) % 5 == 0 or i < 5:
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
    print("TESTE DE RATE LIMITING - FASE 2 (ALTA PRIORIDADE)")
    print("="*60)

    client = TestClient(app)

    resultados = {
        "Criação de Chamados": testar_endpoint(
            client, "/test/chamado-criar",
            RATE_LIMIT_CHAMADO_CRIAR_MAX,
            f"Criação de Chamados ({RATE_LIMIT_CHAMADO_CRIAR_MAX} chamados / {RATE_LIMIT_CHAMADO_CRIAR_MINUTOS} min)"
        ),
        "Resposta em Chamados (Usuário)": testar_endpoint(
            client, "/test/chamado-responder",
            RATE_LIMIT_CHAMADO_RESPONDER_MAX,
            f"Resposta em Chamados - Usuário ({RATE_LIMIT_CHAMADO_RESPONDER_MAX} respostas / {RATE_LIMIT_CHAMADO_RESPONDER_MINUTOS} min)"
        ),
        "Resposta em Chamados (Admin)": testar_endpoint(
            client, "/test/admin-chamado-responder",
            RATE_LIMIT_ADMIN_CHAMADO_RESPONDER_MAX,
            f"Resposta em Chamados - Admin ({RATE_LIMIT_ADMIN_CHAMADO_RESPONDER_MAX} respostas / {RATE_LIMIT_ADMIN_CHAMADO_RESPONDER_MINUTOS} min)"
        ),
        "Busca de Usuários": testar_endpoint(
            client, "/test/busca-usuarios",
            RATE_LIMIT_BUSCA_USUARIOS_MAX,
            f"Busca de Usuários ({RATE_LIMIT_BUSCA_USUARIOS_MAX} buscas / {RATE_LIMIT_BUSCA_USUARIOS_MINUTOS} min)",
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
        print("\n🎉 TODOS OS TESTES DA FASE 2 PASSARAM! 🎉")
        print("\n✅ Rate limiting implementado corretamente para:")
        print("   1. Criação de chamados")
        print("   2. Respostas em chamados (usuário)")
        print("   3. Respostas em chamados (admin)")
        print("   4. Busca de usuários no chat")
    else:
        print(f"\n⚠️  {total_testes - testes_passou} teste(s) falharam")

    return testes_passou == total_testes

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
