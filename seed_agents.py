#!/usr/bin/env python3
"""
Seed básico de agentes Jules - Cria alguns agentes de exemplo
para ter dados iniciais no sistema
"""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "dunder_mifflin.db"

AGENTS = [
    # Autonomous
    {'slug': 'bolt', 'name': 'Bolt', 'department': 'autonomous', 'role': 'Otimizador de Código', 'description': 'Otimiza código para performance máxima', 'capabilities': ['optimization', 'performance', 'refactoring'], 'emoji': '⚡'},
    {'slug': 'sentinel', 'name': 'Sentinel', 'department': 'autonomous', 'role': 'Guardião de Qualidade', 'description': 'Monitora e garante qualidade do código', 'capabilities': ['quality', 'monitoring', 'alerts'], 'emoji': '🛡️'},
    {'slug': 'janitor', 'name': 'Janitor', 'department': 'autonomous', 'role': 'Limpeza de Código', 'description': 'Remove código morto e limpa sujeira', 'capabilities': ['cleanup', 'dead-code', 'refactoring'], 'emoji': '🧹'},
    
    # Development
    {'slug': 'fullstack-dev', 'name': 'Fullstack Dev', 'department': 'development', 'role': 'Desenvolvedor Fullstack', 'description': 'Constrói features end-to-end', 'capabilities': ['frontend', 'backend', 'database'], 'emoji': '💻'},
    {'slug': 'code-reviewer', 'name': 'Code Reviewer', 'department': 'development', 'role': 'Revisor de Código', 'description': 'Analisa PRs e sugere melhorias', 'capabilities': ['review', 'best-practices', 'patterns'], 'emoji': '👁️'},
    {'slug': 'architect', 'name': 'Architect', 'department': 'development', 'role': 'Arquiteto de Software', 'description': 'Desenha arquitetura e padrões', 'capabilities': ['architecture', 'patterns', 'scalability'], 'emoji': '🏗️'},
    
    # Design
    {'slug': 'ui-designer', 'name': 'UI Designer', 'department': 'design', 'role': 'Designer de Interfaces', 'description': 'Cria interfaces visuais', 'capabilities': ['ui', 'visual', 'components'], 'emoji': '🎨'},
    {'slug': 'ux-writer', 'name': 'UX Writer', 'department': 'design', 'role': 'Redator UX', 'description': 'Escreve copy e microtextos', 'capabilities': ['copywriting', 'ux', 'content'], 'emoji': '✍️'},
    
    # Marketing
    {'slug': 'growth-hacker', 'name': 'Growth Hacker', 'department': 'marketing', 'role': 'Especialista em Crescimento', 'description': 'Otimiza funil de crescimento', 'capabilities': ['growth', 'analytics', 'experiments'], 'emoji': '📈'},
    {'slug': 'content-creator', 'name': 'Content Creator', 'department': 'marketing', 'role': 'Criador de Conteúdo', 'description': 'Produz conteúdo para redes', 'capabilities': ['content', 'social', 'writing'], 'emoji': '📝'},
    
    # Product
    {'slug': 'researcher', 'name': 'Researcher', 'department': 'product', 'role': 'Pesquisador de Produto', 'description': 'Pesquisa usuários e mercado', 'capabilities': ['research', 'users', 'market'], 'emoji': '🔬'},
    {'slug': 'sprint-prioritizer', 'name': 'Sprint Prioritizer', 'department': 'product', 'role': 'Priorizador de Sprint', 'description': 'Organiza e prioriza backlog', 'capabilities': ['prioritization', 'sprints', 'backlog'], 'emoji': '📊'},
    
    # Testing
    {'slug': 'tester', 'name': 'Tester', 'department': 'testing', 'role': 'QA Engineer', 'description': 'Testa funcionalidades e encontra bugs', 'capabilities': ['testing', 'qa', 'automation'], 'emoji': '🧪'},
    {'slug': 'mocker', 'name': 'Mocker', 'department': 'testing', 'role': 'Criador de Mocks', 'description': 'Cria mocks e dados de teste', 'capabilities': ['mocking', 'fixtures', 'data'], 'emoji': '🎭'},
]

def seed_agents():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("🤖 Adicionando agentes Jules de exemplo...")
    
    count = 0
    for agent in AGENTS:
        try:
            cur.execute('''
                INSERT OR IGNORE INTO agents 
                (slug, name, department, role, description, capabilities, avatar_emoji, priority, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            ''', (
                agent['slug'],
                agent['name'],
                agent['department'],
                agent['role'],
                agent['description'],
                json.dumps(agent['capabilities']),
                agent['emoji'],
                5
            ))
            if cur.rowcount > 0:
                count += 1
        except Exception as e:
            print(f"   Erro em {agent['slug']}: {e}")
    
    # Atualizar contagem de agentes por departamento
    cur.execute('''
        UPDATE departments 
        SET agent_count = (SELECT COUNT(*) FROM agents WHERE department = departments.slug)
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"✅ {count} agentes adicionados!")
    print("   Execute 'python3 db.py agents' para ver todos")

if __name__ == '__main__':
    seed_agents()
