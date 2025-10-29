"""
Script de teste para verificar rate limiting da Fase 1.

Testa os 4 endpoints críticos implementados:
1. Upload de foto de perfil
2. Alteração de senha
3. Envio de mensagens no chat
4. Criação de salas de chat
"""
import requests
import time
import base64
from io import BytesIO
from PIL import Image

# Configuração
BASE_URL = "http://localhost:8400"
SESSION = requests.Session()

def criar_imagem_teste_base64():
    """Cria uma imagem de teste em base64"""
    img = Image.new('RGB', (100, 100), color='red')
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    img_bytes = buffer.getvalue()
    return base64.b64encode(img_bytes).decode()

def fazer_login():
    """Faz login com usuário de teste"""
    print("\n=== FAZENDO LOGIN ===")
    response = SESSION.post(
        f"{BASE_URL}/login",
        data={
            "email": "joao@email.com",
            "senha": "Joao@123"
        },
        allow_redirects=True
    )
    # Verificar se login foi bem sucedido (seja 200, 302 ou 303)
    if response.status_code == 200 or "usuario" in SESSION.cookies.get_dict():
        print("✅ Login realizado com sucesso")
        return True
    else:
        print(f"❌ Falha no login: {response.status_code}")
        print(f"Cookies: {SESSION.cookies.get_dict()}")
        return False

def testar_rate_limit_upload_foto():
    """
    Testa rate limiting de upload de foto.
    Limite: 5 uploads / 10 minutos
    """
    print("\n" + "="*60)
    print("TESTE 1: Upload de Foto de Perfil")
    print("Limite configurado: 5 uploads / 10 minutos")
    print("="*60)

    foto_base64 = criar_imagem_teste_base64()
    tentativas_sucesso = 0
    bloqueado = False

    for i in range(7):  # Tentar 7 vezes (deve bloquear após 5)
        print(f"\nTentativa {i+1}:")
        response = SESSION.post(
            f"{BASE_URL}/usuario/perfil/atualizar-foto",
            data={"foto_base64": foto_base64},
            allow_redirects=False
        )

        if response.status_code in [302, 303]:
            tentativas_sucesso += 1
            print(f"  ✅ Upload aceito (Status: {response.status_code})")
        elif response.status_code == 429:
            bloqueado = True
            print(f"  🛑 RATE LIMIT ATIVADO (Status: {response.status_code})")
            break
        else:
            print(f"  ⚠️  Resposta inesperada: {response.status_code}")

        time.sleep(0.5)  # Pequeno delay entre requisições

    print(f"\n📊 Resultado:")
    print(f"   Tentativas bem-sucedidas: {tentativas_sucesso}")
    print(f"   Rate limit ativou: {'✅ SIM' if bloqueado else '❌ NÃO'}")
    print(f"   Status: {'✅ PASSOU' if tentativas_sucesso == 5 and bloqueado else '❌ FALHOU'}")

    return tentativas_sucesso == 5 and bloqueado

def testar_rate_limit_alterar_senha():
    """
    Testa rate limiting de alteração de senha.
    Limite: 5 tentativas / 15 minutos
    """
    print("\n" + "="*60)
    print("TESTE 2: Alteração de Senha")
    print("Limite configurado: 5 tentativas / 15 minutos")
    print("="*60)

    tentativas_sucesso = 0
    bloqueado = False

    for i in range(7):  # Tentar 7 vezes (deve bloquear após 5)
        print(f"\nTentativa {i+1}:")
        response = SESSION.post(
            f"{BASE_URL}/usuario/perfil/alterar-senha",
            data={
                "senha_atual": "SenhaErrada123!",  # Senha errada de propósito
                "senha_nova": "NovaSenha123!",
                "confirmar_senha": "NovaSenha123!"
            },
            allow_redirects=False
        )

        # Resposta esperada: 200 com erro de senha incorreta OU rate limit
        if response.status_code == 200:
            tentativas_sucesso += 1
            print(f"  ✅ Tentativa processada (Status: {response.status_code})")
        elif "Muitas tentativas" in response.text or "rate limit" in response.text.lower():
            bloqueado = True
            print(f"  🛑 RATE LIMIT ATIVADO")
            break
        else:
            print(f"  ⚠️  Resposta inesperada: {response.status_code}")

        time.sleep(0.5)

    print(f"\n📊 Resultado:")
    print(f"   Tentativas processadas: {tentativas_sucesso}")
    print(f"   Rate limit ativou: {'✅ SIM' if bloqueado else '❌ NÃO'}")
    print(f"   Status: {'✅ PASSOU' if tentativas_sucesso >= 5 and bloqueado else '❌ FALHOU'}")

    return tentativas_sucesso >= 5 and bloqueado

def testar_rate_limit_enviar_mensagem():
    """
    Testa rate limiting de envio de mensagens.
    Limite: 30 mensagens / 1 minuto
    """
    print("\n" + "="*60)
    print("TESTE 3: Envio de Mensagens no Chat")
    print("Limite configurado: 30 mensagens / 1 minuto")
    print("="*60)

    # Primeiro, criar uma sala de chat
    print("\nCriando sala de chat...")
    response = SESSION.post(
        f"{BASE_URL}/chat/salas",
        data={"outro_usuario_id": 1},  # ID do admin
        allow_redirects=False
    )

    if response.status_code != 200:
        print(f"❌ Falha ao criar sala: {response.status_code}")
        return False

    sala_data = response.json()
    sala_id = sala_data.get("sala_id")
    print(f"✅ Sala criada: {sala_id}")

    tentativas_sucesso = 0
    bloqueado = False

    for i in range(35):  # Tentar 35 vezes (deve bloquear após 30)
        if i % 10 == 0:
            print(f"\nTentativas {i+1}-{min(i+10, 35)}...")

        response = SESSION.post(
            f"{BASE_URL}/chat/mensagens",
            data={
                "sala_id": sala_id,
                "mensagem": f"Mensagem de teste {i+1}"
            }
        )

        if response.status_code == 200:
            tentativas_sucesso += 1
            if (i+1) % 10 == 0:
                print(f"  ✅ {i+1} mensagens enviadas")
        elif response.status_code == 429:
            bloqueado = True
            print(f"  🛑 RATE LIMIT ATIVADO após {tentativas_sucesso} mensagens")
            break
        else:
            print(f"  ⚠️  Resposta inesperada: {response.status_code}")

        time.sleep(0.1)

    print(f"\n📊 Resultado:")
    print(f"   Mensagens enviadas: {tentativas_sucesso}")
    print(f"   Rate limit ativou: {'✅ SIM' if bloqueado else '❌ NÃO'}")
    print(f"   Status: {'✅ PASSOU' if tentativas_sucesso == 30 and bloqueado else '❌ FALHOU'}")

    return tentativas_sucesso == 30 and bloqueado

def testar_rate_limit_criar_sala():
    """
    Testa rate limiting de criação de salas.
    Limite: 10 salas / 10 minutos
    """
    print("\n" + "="*60)
    print("TESTE 4: Criação de Salas de Chat")
    print("Limite configurado: 10 salas / 10 minutos")
    print("="*60)

    tentativas_sucesso = 0
    bloqueado = False

    # Nota: Como só temos 3 usuários no seed, não conseguiremos criar 10 salas únicas
    # Este teste verifica se o rate limiter está aplicado, mesmo que reutilize salas

    for i in range(12):  # Tentar 12 vezes
        print(f"\nTentativa {i+1}:")
        # Alterna entre usuários 1, 2, 3
        outro_usuario_id = (i % 2) + 1

        response = SESSION.post(
            f"{BASE_URL}/chat/salas",
            data={"outro_usuario_id": outro_usuario_id}
        )

        if response.status_code == 200:
            tentativas_sucesso += 1
            print(f"  ✅ Requisição aceita (Status: {response.status_code})")
        elif response.status_code == 429:
            bloqueado = True
            print(f"  🛑 RATE LIMIT ATIVADO (Status: {response.status_code})")
            break
        else:
            print(f"  ⚠️  Resposta: {response.status_code}")

        time.sleep(0.3)

    print(f"\n📊 Resultado:")
    print(f"   Requisições aceitas: {tentativas_sucesso}")
    print(f"   Rate limit ativou: {'✅ SIM' if bloqueado else '❌ NÃO'}")
    print(f"   Status: {'✅ PASSOU' if tentativas_sucesso == 10 and bloqueado else '❌ FALHOU'}")

    return tentativas_sucesso == 10 and bloqueado

def main():
    print("\n" + "="*60)
    print("TESTE DE RATE LIMITING - FASE 1")
    print("="*60)

    # Fazer login primeiro
    if not fazer_login():
        print("\n❌ Não foi possível fazer login. Abortando testes.")
        return

    # Executar todos os testes
    resultados = {
        "Upload de Foto": testar_rate_limit_upload_foto(),
        "Alteração de Senha": testar_rate_limit_alterar_senha(),
        "Envio de Mensagens": testar_rate_limit_enviar_mensagem(),
        "Criação de Salas": testar_rate_limit_criar_sala(),
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
    else:
        print(f"\n⚠️  {total_testes - testes_passou} teste(s) falharam")

if __name__ == "__main__":
    main()
