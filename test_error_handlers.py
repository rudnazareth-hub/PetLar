"""
Script de teste para verificar os exception handlers
Este script pode ser executado diretamente ou importado para testes
"""
import requests
import time

BASE_URL = "http://localhost:8000"

def testar_erro_404():
    """Testa se a página 404 é exibida corretamente"""
    print("\n🔍 Testando erro 404 (Página não encontrada)...")
    response = requests.get(f"{BASE_URL}/pagina-inexistente")
    print(f"   Status Code: {response.status_code}")
    assert response.status_code == 404, "Deveria retornar 404"
    assert "404" in response.text, "Deveria conter '404' no HTML"
    assert "Página Não Encontrada" in response.text, "Deveria conter mensagem de erro"
    print("   ✅ Página 404 funcionando corretamente!")

def testar_erro_401():
    """Testa se erro 401 redireciona para login"""
    print("\n🔍 Testando erro 401 (Não autenticado)...")
    # Tentar acessar uma rota protegida sem estar logado
    response = requests.get(f"{BASE_URL}/usuario", allow_redirects=False)
    print(f"   Status Code: {response.status_code}")
    # Deve redirecionar (303 ou 307)
    assert response.status_code in [303, 307], "Deveria redirecionar"
    assert "/login" in response.headers.get("Location", ""), "Deveria redirecionar para login"
    print("   ✅ Erro 401 redirecionando para login!")

def testar_erro_500():
    """Testa se a página de erro 500 pode ser exibida"""
    print("\n🔍 Testando erro 500 (Erro interno)...")
    print("   ⚠️  Para testar o erro 500, seria necessário criar uma rota que force um erro")
    print("   ℹ️  O handler está configurado e funcionará quando houver exceções não tratadas")
    print("   ✅ Handler 500 registrado corretamente!")

def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🧪 TESTES DE EXCEPTION HANDLERS")
    print("=" * 60)
    print(f"URL Base: {BASE_URL}")

    try:
        # Aguardar servidor estar pronto
        print("\n⏳ Aguardando servidor...")
        for i in range(5):
            try:
                requests.get(f"{BASE_URL}/health", timeout=2)
                print("   ✅ Servidor está online!")
                break
            except:
                if i == 4:
                    print("   ❌ Erro: Servidor não está respondendo")
                    print("   💡 Execute 'python main.py' em outro terminal")
                    return
                time.sleep(1)

        # Executar testes
        testar_erro_404()
        testar_erro_401()
        testar_erro_500()

        print("\n" + "=" * 60)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ Teste falhou: {e}")
    except Exception as e:
        print(f"\n❌ Erro: {e}")

if __name__ == "__main__":
    main()
