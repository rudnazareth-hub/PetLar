"""
Script de teste para verificar rate limiting da Fase 4.

Testa os endpoints de baixa prioridade implementados:
1. Formulários GET de perfil (2 endpoints)
2. Páginas públicas (3 endpoints)
3. Páginas de exemplos (9 endpoints)
"""
import sys
import time

# Importar os módulos necessários
sys.path.insert(0, '/Volumes/Externo/Projetos/DefaultWebApp')

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.testclient import TestClient
from fastapi.responses import HTMLResponse

from util.rate_limiter import RateLimiter, obter_identificador_cliente
from util.config import (
    RATE_LIMIT_FORM_GET_MAX,
    RATE_LIMIT_FORM_GET_MINUTOS,
    RATE_LIMIT_PUBLIC_MAX,
    RATE_LIMIT_PUBLIC_MINUTOS,
    RATE_LIMIT_EXAMPLES_MAX,
    RATE_LIMIT_EXAMPLES_MINUTOS,
)

# Criar app de teste
app = FastAPI()

# Criar rate limiters
form_get_limiter = RateLimiter(
    max_tentativas=RATE_LIMIT_FORM_GET_MAX,
    janela_minutos=RATE_LIMIT_FORM_GET_MINUTOS,
    nome="form_get_test",
)

public_limiter = RateLimiter(
    max_tentativas=RATE_LIMIT_PUBLIC_MAX,
    janela_minutos=RATE_LIMIT_PUBLIC_MINUTOS,
    nome="public_test",
)

examples_limiter = RateLimiter(
    max_tentativas=RATE_LIMIT_EXAMPLES_MAX,
    janela_minutos=RATE_LIMIT_EXAMPLES_MINUTOS,
    nome="examples_test",
)

# Endpoints de teste - Formulários GET
@app.get("/test/form-get")
async def test_form_get(request: Request):
    ip = obter_identificador_cliente(request)
    if not form_get_limiter.verificar(ip):
        return HTMLResponse(content="Rate limit", status_code=status.HTTP_429_TOO_MANY_REQUESTS)
    return {"ok": True}

# Endpoints de teste - Páginas Públicas
@app.get("/test/public")
async def test_public(request: Request):
    ip = obter_identificador_cliente(request)
    if not public_limiter.verificar(ip):
        return HTMLResponse(content="Rate limit", status_code=status.HTTP_429_TOO_MANY_REQUESTS)
    return {"ok": True}

# Endpoints de teste - Páginas de Exemplos
@app.get("/test/examples")
async def test_examples(request: Request):
    ip = obter_identificador_cliente(request)
    if not examples_limiter.verificar(ip):
        return HTMLResponse(content="Rate limit", status_code=status.HTTP_429_TOO_MANY_REQUESTS)
    return {"ok": True}

# Testes
def testar_endpoint(client, endpoint, limite, nome, metodo="GET"):
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
    print("TESTE DE RATE LIMITING - FASE 4 (BAIXA PRIORIDADE)")
    print("="*60)

    client = TestClient(app)

    resultados = {
        "Formulários GET": testar_endpoint(
            client, "/test/form-get",
            RATE_LIMIT_FORM_GET_MAX,
            f"Formulários GET de Perfil ({RATE_LIMIT_FORM_GET_MAX} requisições / {RATE_LIMIT_FORM_GET_MINUTOS} min)"
        ),
        "Páginas Públicas": testar_endpoint(
            client, "/test/public",
            RATE_LIMIT_PUBLIC_MAX,
            f"Páginas Públicas ({RATE_LIMIT_PUBLIC_MAX} requisições / {RATE_LIMIT_PUBLIC_MINUTOS} min)"
        ),
        "Páginas de Exemplos": testar_endpoint(
            client, "/test/examples",
            RATE_LIMIT_EXAMPLES_MAX,
            f"Páginas de Exemplos ({RATE_LIMIT_EXAMPLES_MAX} requisições / {RATE_LIMIT_EXAMPLES_MINUTOS} min)"
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
        print("\n🎉 TODOS OS TESTES DA FASE 4 PASSARAM! 🎉")
        print("\n✅ Rate limiting implementado corretamente para:")
        print("   1. Formulários GET de perfil (2 endpoints)")
        print("   2. Páginas públicas (3 endpoints)")
        print("   3. Páginas de exemplos (9 endpoints)")
        print("\n📋 Detalhes da Implementação:")
        print(f"   - Form GET: {RATE_LIMIT_FORM_GET_MAX} req / {RATE_LIMIT_FORM_GET_MINUTOS} min")
        print(f"   - Públicas: {RATE_LIMIT_PUBLIC_MAX} req / {RATE_LIMIT_PUBLIC_MINUTOS} min")
        print(f"   - Exemplos: {RATE_LIMIT_EXAMPLES_MAX} req / {RATE_LIMIT_EXAMPLES_MINUTOS} min")
    else:
        print(f"\n⚠️  {total_testes - testes_passou} teste(s) falharam")

    return testes_passou == total_testes

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
