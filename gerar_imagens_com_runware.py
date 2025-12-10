#!/usr/bin/env python3
"""
Script para gerar imagens de animais usando o MCP Runware via Anthropic API.
"""

import json
import sqlite3
import base64
from pathlib import Path
from datetime import datetime
import os
import sys

# Tentar importar anthropic
try:
    import anthropic
except ImportError:
    print("Erro: anthropic não está instalado.")
    print("Instale com: pip install anthropic")
    sys.exit(1)


def read_animals_json():
    """Lê o arquivo JSON com dados dos animais."""
    json_path = Path('/home/maroquio/Projects/PetLar/animals_to_generate.json')
    if not json_path.exists():
        print(f"Erro: Arquivo não encontrado: {json_path}")
        sys.exit(1)

    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_image_from_base64(image_base64_data, filepath):
    """Salva uma imagem de dados base64."""
    try:
        # Se tiver 'data:image' prefix, remover
        if isinstance(image_base64_data, str) and image_base64_data.startswith('data:'):
            image_base64_data = image_base64_data.split(',')[1]

        # Decodificar
        image_bytes = base64.b64decode(image_base64_data)

        # Criar diretório
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Salvar
        with open(filepath, 'wb') as f:
            f.write(image_bytes)

        return True
    except Exception as e:
        print(f"Erro ao salvar imagem: {e}")
        return False


def save_image_from_url(image_url, filepath):
    """Baixa e salva uma imagem a partir de URL."""
    try:
        import urllib.request

        filepath.parent.mkdir(parents=True, exist_ok=True)

        with urllib.request.urlopen(image_url) as response:
            image_data = response.read()

        with open(filepath, 'wb') as f:
            f.write(image_data)

        return True
    except Exception as e:
        print(f"Erro ao baixar imagem: {e}")
        return False


def update_animal_photo_in_db(animal_id, photo_path):
    """Atualiza o path da foto no banco de dados."""
    conn = sqlite3.connect('/home/maroquio/Projects/PetLar/dados.db')
    cursor = conn.cursor()

    try:
        cursor.execute(
            'UPDATE animal SET foto = ?, data_atualizacao = CURRENT_TIMESTAMP WHERE id = ?',
            (photo_path, animal_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao atualizar banco de dados: {e}")
        return False
    finally:
        conn.close()


def generate_image_with_runware_mcp(animal_data, index, total):
    """
    Gera uma imagem usando o MCP Runware via Anthropic API.
    """
    animal_id = animal_data['id']
    animal_name = animal_data['nome']
    raca = animal_data['raca']
    description = animal_data['descricao']
    filename = animal_data['filename']
    filepath = Path('/home/maroquio/Projects/PetLar/static/img/animais') / filename
    db_path = animal_data['db_path']

    print(f"\n[{index:3d}/{total}] {animal_name} ({raca})")
    print(f"  Arquivo: {filename}")
    print(f"  Prompt: {description[:70]}...")

    try:
        # Inicializar cliente Anthropic
        client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

        # Chamar o Claude com ferramenta MCP Runware
        prompt_text = f"""Generate an image with the following specifications using the Runware image generation tool:

Prompt: {description}

Image specifications:
- Width: 512
- Height: 512
- Model: runware:100@1
- Steps: 30
- Format: jpg

Please generate this image and provide it in the response."""

        print(f"  Chamando API Anthropic com MCP Runware...")

        # Fazer a requisição
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            tools=[
                {
                    "type": "mcp",
                    "mcp": "runware",
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": prompt_text
                }
            ]
        )

        print(f"  Status: {message.stop_reason}")

        # Processar resposta
        image_saved = False
        for block in message.content:
            if hasattr(block, 'type'):
                if block.type == 'image':
                    # Salvar imagem
                    if hasattr(block, 'source') and hasattr(block.source, 'data'):
                        if save_image_from_base64(block.source.data, filepath):
                            print(f"  ✓ Imagem salva: {filepath}")
                            image_saved = True
                elif block.type == 'text':
                    # Verificar se há URL de imagem no texto
                    if hasattr(block, 'text') and 'http' in block.text:
                        # Tentar extrair URL
                        import re
                        urls = re.findall(r'https?://[^\s\)]+', block.text)
                        if urls:
                            print(f"  URL encontrada: {urls[0][:50]}...")
                            if save_image_from_url(urls[0], filepath):
                                print(f"  ✓ Imagem baixada e salva")
                                image_saved = True

        if image_saved:
            # Atualizar banco de dados
            if update_animal_photo_in_db(animal_id, db_path):
                print(f"  ✓ Banco de dados atualizado")
                return True

        print(f"  ✗ Não foi possível salvar a imagem")
        return False

    except Exception as e:
        print(f"  ✗ Erro ao gerar imagem: {str(e)[:100]}")
        return False


def main():
    """Função principal."""
    print("=" * 80)
    print("GERADOR DE IMAGENS DE ANIMAIS - MCP Runware")
    print("=" * 80)

    # Verificar chave API
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("Erro: ANTHROPIC_API_KEY não está configurada")
        print("Configure com: export ANTHROPIC_API_KEY='sua-chave-aqui'")
        sys.exit(1)

    # Ler arquivo JSON
    animals = read_animals_json()
    print(f"\nTotal de animais para gerar: {len(animals)}")

    # Processar alguns animais de teste
    test_count = 3
    animals_to_process = animals[:test_count]

    print(f"Processando {len(animals_to_process)} animais de teste...\n")

    success_count = 0
    error_count = 0

    for idx, animal in enumerate(animals_to_process, 1):
        try:
            if generate_image_with_runware_mcp(animal, idx, len(animals_to_process)):
                success_count += 1
            else:
                error_count += 1
        except Exception as e:
            print(f"  ✗ Erro: {e}")
            error_count += 1

    # Resumo
    print(f"\n{'='*80}")
    print("RESUMO")
    print(f"{'='*80}")
    print(f"Sucesso: {success_count}")
    print(f"Erros: {error_count}")
    print()


if __name__ == '__main__':
    main()
