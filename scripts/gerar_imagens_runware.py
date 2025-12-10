#!/usr/bin/env python3
"""
Script para gerar fotos de animais usando Runware MCP via Anthropic API.
Lê dados de animals_to_generate.json e gera imagens 512x512 para cada animal.
"""

import json
import sqlite3
import base64
import time
import urllib.request
from pathlib import Path
from anthropic import Anthropic

# Inicializar cliente Anthropic
client = Anthropic()

def load_animals_data():
    """Carrega dados dos animais do JSON."""
    json_path = Path('/home/maroquio/Projects/PetLar/animals_to_generate.json')
    if not json_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {json_path}")

    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_image_with_runware(prompt: str, animal_name: str) -> str:
    """
    Gera uma imagem usando o MCP Runware via Anthropic API.
    Retorna a URL da imagem gerada.
    """
    print(f"    ⏳ Chamando Runware MCP...", end=" ", flush=True)

    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            tools=[
                {
                    "type": "mcp",
                    "mcp": "runware"
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": f"""Generate a professional pet photograph image with EXACTLY these specifications:
Width: 512 pixels
Height: 512 pixels
Format: JPEG
Quality: High

Pet description: {prompt}

Use the runware tool to generate this image. Return the image URL."""
                }
            ]
        )

        # Extrair a resposta
        for block in message.content:
            if hasattr(block, 'text'):
                response_text = block.text
                # Procurar por URL na resposta
                if "http" in response_text:
                    import re
                    urls = re.findall(r'https?://[^\s\'"<>]+', response_text)
                    if urls:
                        print(f"✓")
                        return urls[0]

        print(f"⚠")
        return None

    except Exception as e:
        print(f"❌ Erro: {str(e)[:50]}")
        return None


def download_image(url: str, filepath: Path) -> bool:
    """
    Baixa uma imagem de URL.
    """
    try:
        print(f"    ⏳ Baixando imagem...", end=" ", flush=True)
        urllib.request.urlretrieve(url, filepath)
        print(f"✓")
        return True
    except Exception as e:
        print(f"❌ Erro: {str(e)[:50]}")
        return False


def update_animal_photo_in_db(animal_id: int, photo_path: str) -> bool:
    """
    Atualiza o caminho da foto no banco de dados.
    """
    try:
        conn = sqlite3.connect('/home/maroquio/Projects/PetLar/dados.db')
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE animal SET foto = ?, data_atualizacao = CURRENT_TIMESTAMP WHERE id = ?',
            (photo_path, animal_id)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"      ❌ Erro BD: {str(e)[:50]}")
        return False


def main():
    """Função principal."""
    print("=" * 80)
    print("🐾 GERADOR DE FOTOS DE ANIMAIS COM RUNWARE MCP")
    print("=" * 80)
    print()

    # Carregar dados dos animais
    print("📋 Carregando dados dos animais...")
    try:
        animals = load_animals_data()
        print(f"   ✓ {len(animals)} animais carregados\n")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return

    # Criar diretório de imagens
    img_dir = Path('/home/maroquio/Projects/PetLar/static/img/animais')
    img_dir.mkdir(parents=True, exist_ok=True)

    # Gerar imagens
    generated_count = 0
    failed_count = 0
    skipped_count = 0

    for idx, animal in enumerate(animals, 1):
        animal_id = animal['id']
        animal_name = animal['nome']
        animal_raca = animal['raca']
        description = animal['descricao']
        filename = animal['filename']
        filepath = img_dir / filename
        db_path = animal['db_path']

        # Se já existe, pular
        if filepath.exists():
            print(f"[{idx:3d}/{len(animals)}] ⏭️  {animal_name:25s} ({animal_raca:20s}) - já existe")
            skipped_count += 1
            continue

        print(f"[{idx:3d}/{len(animals)}] 🎨 {animal_name:25s} ({animal_raca:20s})")

        # Gerar imagem
        image_url = generate_image_with_runware(description, animal_name)

        if image_url:
            if download_image(image_url, filepath):
                # Atualizar BD
                if update_animal_photo_in_db(animal_id, db_path):
                    print(f"    ✅ BD atualizado: {db_path}")
                    generated_count += 1
                else:
                    print(f"    ⚠️  Arquivo salvo mas BD não atualizado")
                    generated_count += 1
            else:
                failed_count += 1
        else:
            failed_count += 1

        # Pequeno delay para não sobrecarregar a API
        time.sleep(2)

    # Resumo
    print()
    print("=" * 80)
    print(f"📊 RESUMO:")
    print(f"   ✅ Geradas com sucesso: {generated_count}")
    print(f"   ❌ Falhadas: {failed_count}")
    print(f"   ⏭️  Já existentes: {skipped_count}")
    print(f"   📁 Total de animais: {len(animals)}")
    print("=" * 80)
    print()


if __name__ == '__main__':
    main()
