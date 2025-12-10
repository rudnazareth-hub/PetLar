#!/usr/bin/env python3
"""
Script para gerar fotos de animais chamando a API Runware diretamente.
"""

import json
import sqlite3
import base64
import time
import urllib.request
import urllib.error
import uuid
from pathlib import Path
import os

# Instalar requests se necessário
try:
    import requests
except ImportError:
    print("Instalando requests...")
    os.system("pip install requests -q")
    import requests

# Chave da API Runware
RUNWARE_API_KEY = "Q6SBxRqeiPTgCleUq2bjjjwvzE5vu1Az"

def load_animals_data():
    """Carrega dados dos animais do JSON."""
    json_path = Path('/home/maroquio/Projects/PetLar/animals_to_generate.json')
    if not json_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {json_path}")

    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_image_with_runware_api(prompt: str, animal_name: str) -> str:
    """
    Gera uma imagem chamando a API Runware diretamente.
    Retorna a URL da imagem gerada.
    """
    print(f"    ⏳ Chamando API Runware...", end=" ", flush=True)

    try:
        # Preparar requisição para API Runware
        url = "https://api.runware.ai/v1/images/generate"
        task_uuid = str(uuid.uuid4())

        # A API Runware requer um array de objetos com taskType e taskUUID
        payload = [
            {
                "taskType": "imageInference",
                "taskUUID": task_uuid,
                "positivePrompt": prompt,
                "width": 512,
                "height": 512,
                "model": "runware:100@1",
                "numInferenceSteps": 30
            }
        ]

        headers = {
            "Authorization": f"Bearer {RUNWARE_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers, timeout=180)

        if response.status_code == 200:
            result = response.json()

            # Extrair URL da imagem da resposta
            # A resposta vem em formato: {"data": [{...}]}
            data = result.get('data', []) if isinstance(result, dict) else result
            if isinstance(data, list) and len(data) > 0:
                image_url = data[0].get('imageURL')
                if image_url:
                    print(f"✓")
                    return image_url

            print(f"⚠")
            return None
        else:
            print(f"❌ HTTP {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        print(f"❌ Timeout (>180s)")
        return None
    except Exception as e:
        print(f"❌ {str(e)[:40]}")
        return None


def download_image(url: str, filepath: Path) -> bool:
    """
    Baixa uma imagem de URL.
    """
    try:
        print(f"    ⏳ Baixando imagem...", end=" ", flush=True)
        # Usar requests para melhor controle de timeout
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"✓")
            return True
        else:
            print(f"❌ HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {str(e)[:40]}")
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
        print(f"      ❌ Erro BD: {str(e)[:40]}")
        return False


def main():
    """Função principal."""
    print("=" * 80)
    print("🐾 GERADOR DE FOTOS DE ANIMAIS COM RUNWARE API")
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
        image_url = generate_image_with_runware_api(description, animal_name)

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

        # Delay para não sobrecarregar a API
        time.sleep(3)

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
