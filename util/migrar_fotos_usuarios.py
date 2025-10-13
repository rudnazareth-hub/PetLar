"""
Script para migrar caminhos de fotos de /static/uploads/fotos/ para /static/img/usuarios/
Execute uma única vez após atualizar o código.
"""

from repo import usuario_repo
from util.logger_config import logger

def migrar_caminhos_fotos():
    """Atualiza todos os caminhos de fotos no banco de dados"""
    try:
        # Buscar todos os usuários
        usuarios = usuario_repo.obter_todos()

        contador = 0
        for usuario in usuarios:
            if usuario.foto and usuario.foto.startswith("/static/uploads/fotos/"):
                # Novo caminho
                novo_caminho = usuario.foto.replace("/static/uploads/fotos/", "/static/img/usuarios/")

                # Atualizar no banco
                if usuario_repo.atualizar_foto(usuario.id, novo_caminho):
                    logger.info(f"Foto atualizada para usuário {usuario.email}: {novo_caminho}")
                    contador += 1
                else:
                    logger.error(f"Erro ao atualizar foto do usuário {usuario.email}")

        print(f"\n✅ Migração concluída!")
        print(f"📊 Total de fotos atualizadas: {contador}")

        return True

    except Exception as e:
        logger.error(f"Erro durante migração: {e}")
        print(f"\n❌ Erro durante migração: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Iniciando migração de caminhos de fotos...")
    print("=" * 60)
    migrar_caminhos_fotos()
