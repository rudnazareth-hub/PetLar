#!/usr/bin/env python3
"""
Script para gerar imagens em batch usando o MCP Runware.
Este script cria as instruções para o Claude Code gerar as imagens.
"""

import json
import sqlite3
from pathlib import Path


def gerar_batch_imagens():
    """Gera um arquivo com instruções para gerar imagens em batch."""

    # Ler animais_to_generate.json
    json_path = Path('animals_to_generate.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        animals = json.load(f)

    print(f"Total de animais: {len(animals)}\n")

    # Criar um arquivo com instruções detalhadas para cada animal
    img_dir = Path('static/img/animais')
    img_dir.mkdir(parents=True, exist_ok=True)

    # Para cada animal, gerar uma imagem temporária como placeholder
    # enquanto aguardamos a geração via MCP Runware

    print("Criando placeholders e registrando paths no banco de dados...\n")

    conn = sqlite3.connect('dados.db')
    cursor = conn.cursor()

    # Primeiramente, criar placeholder images (1x1 pixel PNG)
    placeholder_png = bytes([
        137, 80, 78, 71, 13, 10, 26, 10,  # PNG signature
        0, 0, 0, 13,  # IHDR chunk size
        73, 72, 68, 82,  # IHDR
        0, 0, 0, 1, 0, 0, 0, 1,  # 1x1
        8, 2, 0, 0, 0,  # bit depth, color, compression, filter, interlace
        144, 119, 83, 222,  # CRC
        0, 0, 0, 12,  # IDAT chunk size
        73, 68, 65, 84,  # IDAT
        120, 156, 99, 0, 1, 0, 0, 5, 0, 1,  # data
        13, 10, 45, 181,  # CRC
        0, 0, 0, 0,  # IEND chunk size
        73, 69, 78, 68,  # IEND
        174, 66, 96, 130  # CRC
    ])

    for idx, animal in enumerate(animals, 1):
        animal_id = animal['id']
        filename = animal['filename']
        filepath = img_dir / filename
        db_path = animal['db_path']

        # Criar placeholder (imagem vazia)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(filepath, 'wb') as f:
                # Criar um arquivo JPG mínimo
                f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9')

            # Atualizar banco de dados com o path da foto
            cursor.execute(
                'UPDATE animal SET foto = ?, data_atualizacao = CURRENT_TIMESTAMP WHERE id = ?',
                (db_path, animal_id)
            )

            if (idx - 1) % 10 == 0:
                print(f"[{idx:3d}/{len(animals)}] {animal['nome']:30s} - {filename}")

        except Exception as e:
            print(f"Erro ao processar {animal['nome']}: {e}")

    conn.commit()
    conn.close()

    print(f"\nDone! {len(animals)} animais registrados no banco de dados.")
    print("As imagens precisam ser geradas via MCP Runware.\n")

    # Criar arquivo de instruções para gerar as imagens
    instructions = """
# INSTRUÇÕES PARA GERAR IMAGENS COM RUNWARE MCP

Para gerar as imagens de todos os 98 animais, execute o seguinte:

## Usando Claude Code com MCP Runware:

Para cada animal em animals_to_generate.json:
1. Use o prompt em 'descricao'
2. Gere uma imagem com Runware:
   - Width: 512
   - Height: 512
   - Modelo: runware:100@1
3. Salve em static/img/animais/{filename}

## Exemplo de uso:

```python
import json
from pathlib import Path

animals = json.load(open('animals_to_generate.json'))

for animal in animals[:5]:  # Testar com 5 primeiros
    prompt = animal['descricao']
    filename = animal['filename']
    filepath = f"static/img/animais/{filename}"
    # Usar MCP Runware para gerar imagem com 'prompt'
    # Salvar em filepath
```

## Status:

- Total de animais: 98
- Animais com placeholder: 98
- Animais com imagem real: 0 (aguardando geração)
"""

    with open('RUNWARE_INSTRUCTIONS.md', 'w', encoding='utf-8') as f:
        f.write(instructions)

    print("Arquivo RUNWARE_INSTRUCTIONS.md criado.")


if __name__ == '__main__':
    gerar_batch_imagens()
