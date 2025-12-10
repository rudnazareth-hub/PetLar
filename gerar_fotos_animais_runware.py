#!/usr/bin/env python3
"""
Script para gerar fotos de animais usando Runware MCP.
Este script consulta o banco de dados e temos que usar Claude Code para gerar as imagens.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime


def get_animals_from_db():
    """Consulta todos os animais do banco de dados com todas as informações."""
    conn = sqlite3.connect('dados.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
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
            e.nome as especie_nome
        FROM animal a
        LEFT JOIN raca r ON a.id_raca = r.id
        LEFT JOIN especie e ON r.id_especie = e.id
        ORDER BY a.id
    ''')

    animals = cursor.fetchall()
    conn.close()
    return [dict(animal) for animal in animals]


def create_animal_description(animal):
    """Cria uma descrição completa e detalhada do animal para gerar a imagem."""
    nome = animal['nome']
    raca = animal['raca_nome'] or 'Raça desconhecida'
    especie = animal['especie_nome'] or 'Espécie desconhecida'
    sexo = animal['sexo']
    observacoes = animal['observacoes'] or ''

    # Criar descrição detalhada em português para imagem realista
    descricao = f"Professional photograph of a {raca} ({especie}), {sexo.lower()}, "
    descricao += f"named {nome}. "

    # Adicionar observações se existirem
    if observacoes and len(observacoes.strip()) > 0:
        # Limitar a 100 caracteres
        obs_limited = observacoes[:100]
        descricao += f"Details: {obs_limited}. "

    # Adicionar instruções de qualidade
    descricao += "High quality professional pet photograph, 512x512 pixels, "
    descricao += "well-lit, neutral background, perfect for pet adoption website, "
    descricao += "realistic, sharp focus, professional photo quality."

    return descricao


def get_image_filename(animal_id, animal_name):
    """Gera um nome de arquivo válido para a imagem."""
    safe_name = animal_name.lower().replace(' ', '_')
    safe_name = ''.join(c for c in safe_name if c.isalnum() or c == '_')
    return f"{animal_id:03d}_{safe_name}.jpg"


def main():
    """Função principal."""
    # Obter animais do banco de dados
    animals = get_animals_from_db()
    print(f"Total de animais encontrados: {len(animals)}\n")

    # Criar arquivo JSON com informações de todos os animais
    img_dir = Path('/home/maroquio/Projects/PetLar/static/img/animais')
    img_dir.mkdir(parents=True, exist_ok=True)

    # Preparar dados para geração de imagens
    animals_data = []

    for animal in animals:
        animal_id = animal['id']
        animal_name = animal['nome']
        raca_name = animal['raca_nome'] or 'Unknown'

        description = create_animal_description(animal)
        filename = get_image_filename(animal_id, animal_name)

        animals_data.append({
            'id': animal_id,
            'nome': animal_name,
            'raca': raca_name,
            'descricao': description,
            'filename': filename,
            'filepath': f'/static/img/animais/{filename}',
            'db_path': f'/img/animais/{filename}'
        })

        print(f"[{animal_id:3d}] {animal_name:30s} ({raca_name:30s})")
        print(f"      → {filename}")
        print(f"      → Prompt: {description[:80]}...\n")

    # Salvar JSON com dados dos animais
    animals_json_path = Path('/home/maroquio/Projects/PetLar/animals_to_generate.json')
    with open(animals_json_path, 'w', encoding='utf-8') as f:
        json.dump(animals_data, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"Arquivo de configuração salvo em: {animals_json_path}")
    print(f"Total de animais para gerar: {len(animals_data)}")
    print(f"{'='*80}\n")

    # Criar instruções para o Claude Code
    instructions = """
PRÓXIMOS PASSOS:

1. O arquivo 'animals_to_generate.json' contém todos os dados dos animais
2. Use o comando abaixo para gerar as imagens com o MCP Runware:

   Para cada animal no JSON, chame o Runware com:
   - Prompt: o valor de 'descricao'
   - Width: 512
   - Height: 512
   - Salve com o nome: valor de 'filename'
   - Atualize o banco com: valor de 'db_path'

3. Depois execute este script novamente para atualizar o banco de dados com os paths das imagens.
"""

    print(instructions)

    # Salvar instruções em arquivo
    instructions_path = Path('/home/maroquio/Projects/PetLar/GERAR_FOTOS_INSTRUCOES.txt')
    with open(instructions_path, 'w', encoding='utf-8') as f:
        f.write(instructions)
        f.write(f"\nDados dos animais salvos em: {animals_json_path}\n")

    return animals_data


if __name__ == '__main__':
    main()
