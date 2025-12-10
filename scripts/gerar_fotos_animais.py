#!/usr/bin/env python3
"""
Script para gerar fotos de animais usando MCP Runware via Claude Code.
Cria imagens quadradas 512x512 com base nas informações do animal.
"""

import sqlite3
import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
import subprocess
import base64


def get_animals_from_db(limit=None):
    """Consulta todos os animais do banco de dados."""
    conn = sqlite3.connect('dados.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = '''
        SELECT
            a.id,
            a.nome,
            a.sexo,
            a.data_nascimento,
            a.data_entrada,
            a.observacoes,
            a.status,
            a.foto,
            r.nome as raca_nome,
            e.nome as especie_nome,
            ab.id_abrigo,
            ab.responsavel as abrigo_nome
        FROM animal a
        LEFT JOIN raca r ON a.id_raca = r.id
        LEFT JOIN especie e ON r.id_especie = e.id
        LEFT JOIN abrigo ab ON a.id_abrigo = ab.id_abrigo
        ORDER BY a.id
    '''

    if limit:
        query += f' LIMIT {limit}'

    cursor.execute(query)
    animals = cursor.fetchall()
    conn.close()
    return [dict(animal) for animal in animals]


def create_animal_description(animal):
    """Cria uma descrição completa e detalhada do animal para gerar a imagem."""
    nome = animal['nome']
    raca = animal['raca_nome'] or 'Raça desconhecida'
    especie = animal['especie_nome'] or 'Espécie desconhecida'
    sexo = animal['sexo']
    status = animal['status']
    observacoes = animal['observacoes'] or ''

    # Criar descrição detalhada em português
    descricao = f"Fotografia profissional de um(a) {raca} ({especie}), {sexo.lower()}, "
    descricao += f"chamado(a) {nome}. "

    # Adicionar status
    if status and status != 'Disponível':
        descricao += f"Status: {status}. "

    # Adicionar observações se existirem
    if observacoes and len(observacoes.strip()) > 0:
        descricao += f"Características: {observacoes}. "

    # Adicionar instruções de qualidade
    descricao += "Imagem quadrada 512x512 pixels, de alta qualidade, bem iluminada, "
    descricao += "fundo neutro branco ou cinzento suave, foto profissional de animal de estimação. "
    descricao += "Foto realista e de boa qualidade para website de adoção de animais."

    return descricao


def generate_prompt_for_claude(description):
    """Cria um prompt para Claude gerar a imagem via Runware."""
    prompt = f"""
You are an image generation assistant. Generate an image using the Runware MCP tool with these specifications:

PROMPT (Portuguese description of the animal):
{description}

SPECIFICATIONS:
- Width: 512
- Height: 512
- Model: "runware:100@1" (latest high quality model)
- Num_inference_steps: 30
- Use high quality settings
- Output format: jpg

Please call the runware generate_image tool with these parameters and return the image.
"""
    return prompt


def get_image_filename(animal_id, animal_name):
    """Gera um nome de arquivo válido para a imagem."""
    # Sanitizar nome do animal
    safe_name = animal_name.lower().replace(' ', '_')
    safe_name = ''.join(c for c in safe_name if c.isalnum() or c == '_')
    return f"{animal_id:03d}_{safe_name}.jpg"


def save_image_from_base64(image_base64, filepath):
    """Salva imagem decodificada de base64."""
    try:
        # Se é uma string base64, decodificar
        if isinstance(image_base64, str):
            image_data = base64.b64decode(image_base64)
        else:
            image_data = image_base64

        with open(filepath, 'wb') as f:
            f.write(image_data)
        return True
    except Exception as e:
        print(f"Erro ao salvar imagem: {e}")
        return False


def update_animal_photo_in_db(animal_id, photo_path):
    """Atualiza o path da foto no banco de dados."""
    conn = sqlite3.connect('dados.db')
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


def main():
    """Função principal."""
    # Diretório das imagens
    img_dir = Path('/home/maroquio/Projects/PetLar/static/img/animais')
    img_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("GERADOR DE FOTOS DE ANIMAIS - MCP Runware")
    print("=" * 80)

    # Obter animais do banco de dados
    # Para testes, vamos processar os primeiros 5 animais
    test_limit = 5
    animals = get_animals_from_db(limit=test_limit)
    print(f"\nAnimais para processar: {len(animals)} (teste com {test_limit})")

    # Criar arquivo de log
    log_file = Path('/home/maroquio/Projects/PetLar/gerar_fotos_log.txt')
    with open(log_file, 'w') as log:
        log.write(f"Log de geração de fotos\n")
        log.write(f"Data: {datetime.now()}\n")
        log.write("=" * 80 + "\n\n")

        # Processar cada animal
        for idx, animal in enumerate(animals, 1):
            animal_id = animal['id']
            animal_name = animal['nome']
            raca_name = animal['raca_nome'] or 'Unknown'

            msg = f"\n[{idx:3d}/{len(animals)}] Processando: {animal_name} ({raca_name}) - ID: {animal_id}"
            print(msg)
            log.write(msg + "\n")

            # Criar descrição detalhada
            description = create_animal_description(animal)
            log.write(f"Descrição: {description}\n")

            # Gerar nome do arquivo
            filename = get_image_filename(animal_id, animal_name)
            filepath = img_dir / filename
            photo_path = f"/img/animais/{filename}"

            log.write(f"Caminho de saída: {filepath}\n")
            log.write(f"Path do banco de dados: {photo_path}\n")

    print("\nScript preparado para gerar fotos.")
    print(f"Descrições geradas para {len(animals)} animais.")
    print(f"Log salvo em: {log_file}")
    print("\nNota: Execute este script via Claude Code para gerar as imagens com Runware.")


if __name__ == '__main__':
    main()
