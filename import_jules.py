#!/usr/bin/env python3
"""
Import Jules Agents - Importa os 52 agentes Jules para o banco SQLite

Este script lê os arquivos .md dos agentes Jules e popula o banco de dados
com as informações extraídas, incluindo nome, role, capabilities, etc.
"""

import os
import re
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configuração
JULES_AGENTS_DIR = "/Users/jhonatan/Downloads/Jules/agents"
DB_PATH = "dunder_mifflin.db"

# Mapeamento de personas DM para agentes Jules
PERSONA_AGENT_MAP = {
    'michael': 'studio-producer',
    'dwight': 'sentinel',
    'jim': 'joker',
    'pam': 'ux-writer',
    'stanley': 'tester',
    'angela': 'legal-compliance-checker',
    'kevin': 'finance-tracker',
    'oscar': 'analytics-specialist',
}

# Emojis padrão por departamento
DEPT_EMOJIS = {
    'autonomous': '🤖',
    'development': '💻',
    'design': '🎨',
    'marketing': '📢',
    'product': '📦',
    'project-management': '📋',
    'studio-operations': '⚙️',
    'testing': '🧪',
    'bonus': '🎁',
}


def extract_emoji_from_title(content: str) -> str:
    """Extrai emoji do título do agente"""
    # Procura por emoji no início do título
    emoji_pattern = r'^#\s*(.+?)\s*[🔍🛡️⚡🧹🔄🚀♿🌍💻🔌🏗️🐛🤖🎨✨✍️📖🛡️🔬📈📊🧪🎭🔌📊📝🎉💪📢📱📸🐦🎵💬📦🔬🚀🏢⚙️📊💰⚖️🗂️💬🧪📐🔍📊📈🔧🎮🎁]'
    match = re.search(emoji_pattern, content, re.MULTILINE)
    if match:
        # Procura emoji no texto capturado
        emoji_match = re.search(r'[\U0001F300-\U0001F9FF]', match.group(1))
        if emoji_match:
            return emoji_match.group(0)
    return '🤖'


def parse_agent_md(file_path: str) -> Dict:
    """Parseia um arquivo .md de agente e extrai informações"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extrai nome do título
    title_match = re.search(r'^#\s*(.+?)(?:\s*[-–—]\s*|\n)', content, re.MULTILINE)
    name = title_match.group(1).strip() if title_match else Path(file_path).stem

    # Remove emojis do nome para ficar limpo
    name = re.sub(r'[\U0001F300-\U0001F9FF]', '', name).strip()
    name = re.sub(r'\s+', ' ', name)

    # Extrai emoji do título
    avatar_emoji = extract_emoji_from_title(content)

    # Extrai descrição/missão
    mission_match = re.search(r'\*\*Missão:\*\*\s*(.+?)(?:\n|$)', content)
    description = mission_match.group(1).strip() if mission_match else ""

    # Se não encontrou missão, tenta pegar a primeira linha após Identidade
    if not description:
        identity_match = re.search(r'##\s*Identidade\s*\n+(.+?)(?:\n\n|$)', content, re.DOTALL)
        if identity_match:
            first_line = identity_match.group(1).strip().split('\n')[0]
            description = first_line[:200]

    # Extrai role da segunda linha ou após o nome
    role_match = re.search(r'^#.+?\n+(?:.*?\n)*?(?:Você é|You are)\s*\*\*\w+\*\*\s*[-–—]\s*(.+?)(?:\.|$)', content, re.MULTILINE)
    role = role_match.group(1).strip() if role_match else name

    # Se role é muito longo, trunca
    if len(role) > 100:
        role = role[:97] + "..."

    # Extrai capabilities da seção de Filosofia ou capabilities
    capabilities = []

    # Tenta extrair da seção Filosofia
    philosophy_match = re.search(r'##\s*Filosofia\s*\n+((?:[-*]\s*.+\n?)+)', content)
    if philosophy_match:
        items = re.findall(r'[-*]\s*\*\*(.+?)\*\*', philosophy_match.group(1))
        capabilities.extend(items[:5])

    # Tenta extrair da seção ✅ Sempre Faça
    always_match = re.search(r'###\s*✅\s*Sempre Faça\s*\n+((?:[-*]\s*.+\n?)+)', content)
    if always_match and len(capabilities) < 5:
        items = re.findall(r'[-*]\s*(.+?)(?:\n|$)', always_match.group(1))
        for item in items[:3]:
            cap = item.strip()[:50]
            if cap and cap not in capabilities:
                capabilities.append(cap)

    # Garante pelo menos uma capability
    if not capabilities:
        capabilities = [name]

    # Determina prioridade baseado no departamento
    priority = 5  # padrão

    return {
        'name': name,
        'role': role,
        'description': description,
        'capabilities': capabilities,
        'avatar_emoji': avatar_emoji,
        'file_path': file_path,
        'priority': priority,
    }


def get_agent_slug(file_path: str) -> str:
    """Gera slug a partir do nome do arquivo"""
    return Path(file_path).stem


def import_agents(conn: sqlite3.Connection, agents_dir: str) -> Tuple[int, int]:
    """Importa todos os agentes Jules para o banco"""
    cursor = conn.cursor()
    imported = 0
    skipped = 0

    departments = [
        'autonomous', 'development', 'design', 'marketing',
        'product', 'project-management', 'studio-operations',
        'testing', 'bonus'
    ]

    for dept in departments:
        dept_path = os.path.join(agents_dir, dept)
        if not os.path.exists(dept_path):
            print(f"⚠️  Departamento não encontrado: {dept}")
            continue

        agent_count = 0
        for file in os.listdir(dept_path):
            if not file.endswith('.md') or file == 'README.md':
                continue

            file_path = os.path.join(dept_path, file)
            slug = get_agent_slug(file_path)

            try:
                agent_data = parse_agent_md(file_path)

                cursor.execute('''
                    INSERT OR REPLACE INTO agents
                    (slug, name, department, role, description, capabilities,
                     avatar_emoji, file_path, priority, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                ''', (
                    slug,
                    agent_data['name'],
                    dept,
                    agent_data['role'],
                    agent_data['description'],
                    json.dumps(agent_data['capabilities'], ensure_ascii=False),
                    agent_data['avatar_emoji'],
                    agent_data['file_path'],
                    agent_data['priority'],
                ))

                imported += 1
                agent_count += 1
                print(f"  ✅ {agent_data['avatar_emoji']} {slug}")

            except Exception as e:
                print(f"  ❌ Erro ao importar {file}: {e}")
                skipped += 1

        # Atualiza contagem de agentes no departamento
        cursor.execute('''
            UPDATE departments SET agent_count = ? WHERE slug = ?
        ''', (agent_count, dept))

        print(f"\n📁 {dept}: {agent_count} agentes")

    conn.commit()
    return imported, skipped


def link_personas_to_agents(conn: sqlite3.Connection):
    """Vincula personas DM aos agentes Jules correspondentes"""
    cursor = conn.cursor()

    print("\n🎭 Vinculando personas aos agentes...")

    for persona_slug, agent_slug in PERSONA_AGENT_MAP.items():
        # Busca o agent_id
        cursor.execute('SELECT id FROM agents WHERE slug = ?', (agent_slug,))
        result = cursor.fetchone()

        if result:
            agent_id = result[0]
            cursor.execute('''
                UPDATE personas SET agent_id = ? WHERE slug = ?
            ''', (agent_id, persona_slug))
            print(f"  ✅ {persona_slug} → {agent_slug}")
        else:
            print(f"  ⚠️  Agente não encontrado: {agent_slug}")

    conn.commit()


def import_commands(conn: sqlite3.Connection, commands_file: str):
    """Importa comandos do COMMANDS.md"""
    cursor = conn.cursor()

    if not os.path.exists(commands_file):
        print(f"⚠️  COMMANDS.md não encontrado: {commands_file}")
        return

    with open(commands_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extrai comandos simples da tabela
    simple_commands = re.findall(
        r'\|\s*`(/\w+)`\s*\|\s*(\w+(?:-\w+)*)\s*\|\s*(.+?)\s*\|',
        content
    )

    print(f"\n🎮 Importando {len(simple_commands)} comandos...")

    for cmd, agent, desc in simple_commands:
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO commands
                (slug, name, description, command_type, agents)
                VALUES (?, ?, ?, 'simple', ?)
            ''', (cmd, cmd.replace('/', '').title(), desc, json.dumps([agent])))
        except Exception as e:
            print(f"  ⚠️  Erro ao importar {cmd}: {e}")

    conn.commit()
    print(f"  ✅ Comandos importados")


def main():
    """Função principal"""
    print("=" * 60)
    print("🏢 Dunder Mifflin - Import Jules Agents")
    print("=" * 60)

    # Verifica se o diretório de agentes existe
    if not os.path.exists(JULES_AGENTS_DIR):
        print(f"❌ Diretório de agentes não encontrado: {JULES_AGENTS_DIR}")
        return

    # Conecta ao banco
    conn = sqlite3.connect(DB_PATH)

    # Executa o schema para criar/atualizar tabelas
    print("\n📝 Aplicando schema...")
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    print("  ✅ Schema aplicado")

    # Importa agentes
    print("\n🤖 Importando agentes Jules...")
    imported, skipped = import_agents(conn, JULES_AGENTS_DIR)

    # Vincula personas
    link_personas_to_agents(conn)

    # Importa comandos
    commands_file = os.path.join(JULES_AGENTS_DIR, 'COMMANDS.md')
    import_commands(conn, commands_file)

    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO")
    print("=" * 60)
    print(f"  ✅ Agentes importados: {imported}")
    print(f"  ⚠️  Agentes pulados: {skipped}")

    # Estatísticas
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM agents')
    total_agents = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM departments')
    total_depts = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM personas WHERE agent_id IS NOT NULL')
    linked_personas = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM commands')
    total_commands = cursor.fetchone()[0]

    print(f"\n  📁 Departamentos: {total_depts}")
    print(f"  🤖 Agentes: {total_agents}")
    print(f"  🎭 Personas vinculadas: {linked_personas}")
    print(f"  🎮 Comandos: {total_commands}")

    conn.close()
    print("\n✅ Importação concluída!")


if __name__ == '__main__':
    main()
