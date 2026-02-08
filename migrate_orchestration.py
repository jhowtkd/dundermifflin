#!/usr/bin/env python3
"""
Migração para Orquestração V2
Adiciona as 5 tabelas de serviços, planos e sessões
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "dunder_mifflin.db"

def migrate():
    print("🔄 Migração: Orquestração V2")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Verifica se tabelas já existem
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='services'")
    if cur.fetchone():
        print("✅ Tabelas de orquestração já existem")
    else:
        print("📦 Criando tabelas...")
        
        # Lê o schema e executa apenas as partes novas
        with open('schema.sql', 'r') as f:
            schema = f.read()
        
        # Executa o schema completo (SQLite ignora IF NOT EXISTS)
        conn.executescript(schema)
        print("✅ Tabelas criadas")
    
    # Verifica se já temos serviços seed
    cur.execute("SELECT COUNT(*) FROM services")
    if cur.fetchone()[0] > 0:
        print("✅ Serviços seed já existem")
    else:
        print("🌱 Criando serviços de exemplo...")
        seed_services(cur, conn)
    
    conn.close()
    print("\n✅ Migração completa!")
    print("=" * 60)


def seed_services(cur, conn):
    """Cria 5 serviços de exemplo"""
    
    services = [
        {
            "code": "SVC-linkedin",
            "name": "Criar Post LinkedIn",
            "slug": "criar-post-linkedin",
            "desc": "Pesquisa tema, redige post profissional e revisa qualidade",
            "emoji": "📝",
            "agents": ["researcher", "content-creator", "ux-writer"],
            "loop": {"enabled": True, "max_iterations": 2, "until_score": 8},
            "steps": [
                {"agent": "researcher", "name": "Pesquisar tema", "action": "execute"},
                {"agent": "content-creator", "name": "Redigir post", "action": "execute"},
                {"agent": "ux-writer", "name": "Revisar qualidade", "action": "review"}
            ]
        },
        {
            "code": "SVC-carousel",
            "name": "Gerar Carrossel",
            "slug": "gerar-carrossel",
            "desc": "Cria carrossel visual com slides e copy",
            "emoji": "🎠",
            "agents": ["researcher", "visual-storyteller", "ux-writer"],
            "loop": None,
            "steps": [
                {"agent": "researcher", "name": "Pesquisar conteúdo", "action": "execute"},
                {"agent": "visual-storyteller", "name": "Criar slides", "action": "execute"},
                {"agent": "ux-writer", "name": "Escrever copy", "action": "execute"}
            ]
        },
        {
            "code": "SVC-social",
            "name": "Planejamento Social",
            "slug": "planejamento-social",
            "desc": "Planeja semana de conteúdo para redes sociais",
            "emoji": "📱",
            "agents": ["trend-researcher", "content-creator", "instagram-curator"],
            "loop": None,
            "steps": [
                {"agent": "trend-researcher", "name": "Analisar tendências", "action": "execute"},
                {"agent": "content-creator", "name": "Criar conteúdo", "action": "execute"},
                {"agent": "instagram-curator", "name": "Organizar feed", "action": "review"}
            ]
        },
        {
            "code": "SVC-review",
            "name": "Code Review",
            "slug": "code-review",
            "desc": "Revisão completa de código com testes",
            "emoji": "🔍",
            "agents": ["code-reviewer", "tester", "debugger"],
            "loop": {"enabled": True, "max_iterations": 3, "until_score": 9},
            "steps": [
                {"agent": "code-reviewer", "name": "Revisar código", "action": "review"},
                {"agent": "tester", "name": "Executar testes", "action": "execute"},
                {"agent": "debugger", "name": "Corrigir issues", "action": "execute"}
            ]
        },
        {
            "code": "SVC-docs",
            "name": "Documentar Feature",
            "slug": "documentar-feature",
            "desc": "Cria documentação técnica e guia de uso",
            "emoji": "📚",
            "agents": ["architect", "documenter", "ux-writer"],
            "loop": None,
            "steps": [
                {"agent": "architect", "name": "Definir estrutura", "action": "execute"},
                {"agent": "documenter", "name": "Escrever docs", "action": "execute"},
                {"agent": "ux-writer", "name": "Revisar clareza", "action": "review"}
            ]
        }
    ]
    
    for svc in services:
        # Insere serviço
        cur.execute("""
            INSERT INTO services (service_code, name, slug, description, icon_emoji, 
                                 agent_sequence, loop_config, requires_approval)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            svc["code"],
            svc["name"],
            svc["slug"],
            svc["desc"],
            svc["emoji"],
            json.dumps(svc["agents"]),
            json.dumps(svc["loop"]) if svc["loop"] else None,
            1
        ))
        
        service_id = cur.lastrowid
        
        # Insere steps
        for idx, step in enumerate(svc["steps"], 1):
            cur.execute("""
                INSERT INTO service_steps (service_id, step_order, agent_slug, step_name, action_type)
                VALUES (?, ?, ?, ?, ?)
            """, (service_id, idx, step["agent"], step["name"], step["action"]))
        
        print(f"  ✅ {svc['emoji']} {svc['name']}")
    
    conn.commit()


if __name__ == "__main__":
    migrate()
