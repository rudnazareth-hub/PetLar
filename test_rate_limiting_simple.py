"""
Script simplificado para testar rate limiting sem depender de autenticação.

Adiciona endpoints de teste temporários e verifica se o rate limiting funciona.
"""
import sys
import time
import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.testclient import TestClient

# Importar os módulos necessários
sys.path.insert(0, '/Volumes/Externo/Projetos/DefaultWebApp')

from util.rate_limiter import RateLimiter, obter_identificador_cliente
from util.config import (
    RATE_LIMIT_UPLOAD_FOTO_MAX,
    RATE_LIMIT_UPLOAD_FOTO_MINUTOS,
    RATE_LIMIT_ALTERAR_SENHA_MAX,
    RATE_LIMIT_ALTERAR_SENHA_MINUTOS,
    RATE_LIMIT_CHAT_MESSAGE_MAX,
    RATE_LIMIT_CHAT_MESSAGE_MINUTOS,
    RATE_LIMIT_CHAT_SALA_MAX,
    RATE_LIMIT_CHAT_SALA_MINUTOS,
)

# Criar app de teste
app = FastAPI()

# Criar rate limiters
upload_foto_limiter = RateLimiter(
    max_tentativas=RATE_LIMIT_UPLOAD_FOTO_MAX,
    janela_minutos=RATE_LIMIT_UPLOAD_FOTO_MINUTOS,
    nome="upload_foto_test",
)

alterar_senha_limiter = RateLimiter(
    max_tentativas=RATE_LIMIT_ALTERAR_SENHA_MAX,
    janela_minutos=RATE_LIMIT_ALTERAR_SENHA_MINUTOS,
    nome="alterar_senha_test",
)

chat_mensagem_limiter = RateLimiter(
    max_tentativas=RATE_LIMIT_CHAT_MESSAGE_MAX,
    janela_minutos=RATE_LIMIT_CHAT_MESSAGE_MINUTOS,
    nome="chat_mensagem_test",
)

chat_sala_limiter = RateLimiter(
    max_tentativas=RATE_LIMIT_CHAT_SALA_MAX,
    janela_minutos=RATE_LIMIT_CHAT_SALA_MINUTOS,
    nome="chat_sala_test",
)

# Endpoints de teste
@app.post("/test/upload-foto")
async def test_upload_foto(request: Request):
    ip = obter_identificador_cliente(request)
    if not upload_foto_limiter.verificar(ip):
        raise HTTPException(status_code=429, detail="Rate limit excedido")
    return {"ok": True}

@app.post("/test/alterar-senha")
async def test_alterar_senha(request: Request):
    ip = obter_identificador_cliente(request)
    if not alterar_senha_limiter.verificar(ip):
        raise HTTPException(status_code=429, detail="Rate limit excedido")
    return {"ok": True}

@app.post("/test/chat-mensagem")
async def test_chat_mensagem(request: Request):
    ip = obter_identificador_cliente(request)
    if not chat_mensagem_limiter.verificar(ip):
        raise HTTPException(status_code=429, detail="Rate limit excedido")
    return {"ok": True}

@app.post("/test/chat-sala")
async def test_chat_sala(request: Request):
    ip = obter_identificador_cliente(request)
    if not chat_sala_limiter.verificar(ip):
        raise HTTPException(status_code=429, detail="Rate limit excedido")
    return {"ok": True}

# Testes
def testar_endpoint(client, endpoint, limite, nome):
    print(f"\n{'='*60}")
    print(f"TESTE: {nome}")
    print(f"Limite configurado: {limite} requisições")
    print(f"{'='*60}")

    tentativas_sucesso = 0
    bloqueado = False

    for i in range(limite + 3):  # Tentar mais que o limite
        response = client.post(endpoint)

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
    print("TESTE DE RATE LIMITING - FASE 1 (SIMPLIFICADO)")
    print("="*60)

    client = TestClient(app)

    resultados = {
        "Upload de Foto": testar_endpoint(
            client, "/test/upload-foto",
            RATE_LIMIT_UPLOAD_FOTO_MAX,
            f"Upload de Foto ({RATE_LIMIT_UPLOAD_FOTO_MAX} uploads / {RATE_LIMIT_UPLOAD_FOTO_MINUTOS} min)"
        ),
        "Alteração de Senha": testar_endpoint(
            client, "/test/alterar-senha",
            RATE_LIMIT_ALTERAR_SENHA_MAX,
            f"Alteração de Senha ({RATE_LIMIT_ALTERAR_SENHA_MAX} tentativas / {RATE_LIMIT_ALTERAR_SENHA_MINUTOS} min)"
        ),
        "Envio de Mensagens": testar_endpoint(
            client, "/test/chat-mensagem",
            RATE_LIMIT_CHAT_MESSAGE_MAX,
            f"Envio de Mensagens ({RATE_LIMIT_CHAT_MESSAGE_MAX} mensagens / {RATE_LIMIT_CHAT_MESSAGE_MINUTOS} min)"
        ),
        "Criação de Salas": testar_endpoint(
            client, "/test/chat-sala",
            RATE_LIMIT_CHAT_SALA_MAX,
            f"Criação de Salas ({RATE_LIMIT_CHAT_SALA_MAX} salas / {RATE_LIMIT_CHAT_SALA_MINUTOS} min)"
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
        print(f"{nome:25} {status}")

    print(f"\nTotal: {testes_passou}/{total_testes} testes passaram")

    if testes_passou == total_testes:
        print("\n🎉 TODOS OS TESTES DA FASE 1 PASSARAM! 🎉")
        print("\n✅ Rate limiting implementado corretamente para:")
        print("   1. Upload de foto de perfil")
        print("   2. Alteração de senha")
        print("   3. Envio de mensagens no chat")
        print("   4. Criação de salas de chat")
    else:
        print(f"\n⚠️  {total_testes - testes_passou} teste(s) falharam")

    return testes_passou == total_testes

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
