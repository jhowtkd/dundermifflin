#!/usr/bin/env python3
"""
Seed Squads V2 - Popula os 6 squads com agentes reais como mestres
"""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "dunder_mifflin.db"

# Definição dos 6 squads com agentes reais como mestres
SQUADS_CONFIG = [
    {
        "slug": "content-factory",
        "name": "Fábrica de Conteúdo",
        "description": "Criação de conteúdo para redes sociais, blogs e materiais de marketing",
        "emoji": "✍️",
        "color": "#10B981",
        "master_slug": "content-creator",
        "capabilities": ["writing", "seo", "social_media", "content_strategy", "copywriting"],
        "members": [
            {"slug": "ux-writer", "role": "specialist", "can_loop": True},
            {"slug": "brand-guardian", "role": "reviewer", "can_loop": True},
            {"slug": "polish", "role": "specialist", "can_loop": False},
            {"slug": "visual-storyteller", "role": "specialist", "can_loop": False},
            {"slug": "instagram-curator", "role": "specialist", "can_loop": False},
            {"slug": "twitter-engager", "role": "specialist", "can_loop": False},
        ]
    },
    {
        "slug": "code-guardians",
        "name": "Guardiões do Código",
        "description": "Code review, refatoração, otimização e segurança de código",
        "emoji": "🛡️",
        "color": "#3B82F6",
        "master_slug": "code-reviewer",
        "capabilities": ["code_review", "refactoring", "optimization", "security", "debugging"],
        "members": [
            {"slug": "sentinel", "role": "specialist", "can_loop": True},
            {"slug": "optimizer", "role": "specialist", "can_loop": True},
            {"slug": "janitor", "role": "specialist", "can_loop": False},
            {"slug": "debugger", "role": "specialist", "can_loop": True},
            {"slug": "architect", "role": "reviewer", "can_loop": False},
            {"slug": "fullstack-developer", "role": "specialist", "can_loop": False},
        ]
    },
    {
        "slug": "ux-squad",
        "name": "Esquadrão UX",
        "description": "Pesquisa de usuários, design de interfaces, UX writing e acessibilidade",
        "emoji": "🎨",
        "color": "#8B5CF6",
        "master_slug": "ux-researcher",
        "capabilities": ["ux_research", "ui_design", "ux_writing", "accessibility", "prototyping"],
        "members": [
            {"slug": "ui-designer", "role": "specialist", "can_loop": True},
            {"slug": "ux-writer", "role": "specialist", "can_loop": True},
            {"slug": "palette", "role": "specialist", "can_loop": False},
            {"slug": "polish", "role": "specialist", "can_loop": True},
            {"slug": "a11y-specialist", "role": "specialist", "can_loop": False},
            {"slug": "whimsy-injector", "role": "specialist", "can_loop": False},
        ]
    },
    {
        "slug": "growth-team",
        "name": "Time de Growth",
        "description": "Growth hacking, marketing digital, analytics e experimentos",
        "emoji": "📈",
        "color": "#F59E0B",
        "master_slug": "growth-hacker",
        "capabilities": ["growth", "analytics", "experiments", "conversion", "viral_marketing"],
        "members": [
            {"slug": "analytics-specialist", "role": "specialist", "can_loop": False},
            {"slug": "content-creator", "role": "specialist", "can_loop": True},
            {"slug": "app-store-optimizer", "role": "specialist", "can_loop": False},
            {"slug": "tiktok-strategist", "role": "specialist", "can_loop": False},
            {"slug": "reddit-community-builder", "role": "specialist", "can_loop": False},
            {"slug": "trend-researcher", "role": "specialist", "can_loop": False},
        ]
    },
    {
        "slug": "qa-squad",
        "name": "Esquadrão QA",
        "description": "Testes manuais, automação, performance e qualidade de software",
        "emoji": "🧪",
        "color": "#EF4444",
        "master_slug": "tester",
        "capabilities": ["testing", "automation", "performance", "security_testing", "qa_strategy"],
        "members": [
            {"slug": "api-tester", "role": "specialist", "can_loop": True},
            {"slug": "performance-benchmarker", "role": "specialist", "can_loop": True},
            {"slug": "mocker", "role": "specialist", "can_loop": False},
            {"slug": "test-results-analyzer", "role": "specialist", "can_loop": True},
            {"slug": "tool-evaluator", "role": "specialist", "can_loop": False},
            {"slug": "workflow-optimizer", "role": "specialist", "can_loop": False},
        ]
    },
    {
        "slug": "devops-crew",
        "name": "Crew DevOps",
        "description": "Infraestrutura, CI/CD, monitoramento e operações",
        "emoji": "⚙️",
        "color": "#6B7280",
        "master_slug": "cicd-engineer",
        "capabilities": ["infrastructure", "cicd", "monitoring", "deployment", "cloud"],
        "members": [
            {"slug": "infrastructure-maintainer", "role": "specialist", "can_loop": False},
            {"slug": "database-engineer", "role": "specialist", "can_loop": True},
            {"slug": "migrator", "role": "specialist", "can_loop": False},
            {"slug": "sentinel", "role": "specialist", "can_loop": True},
            {"slug": "analytics-specialist", "role": "specialist", "can_loop": False},
            {"slug": "finance-tracker", "role": "specialist", "can_loop": False},
        ]
    }
]

# Serviços pré-configurados
SERVICES_CONFIG = [
    {
        "slug": "linkedin-post",
        "name": "Post para LinkedIn",
        "description": "Cria um post profissional para LinkedIn sobre qualquer tema",
        "emoji": "💼",
        "squad_slug": "content-factory",
        "steps": [
            {"agent_slug": "trend-researcher", "title": "Pesquisa de tendências", "desc": "Pesquisa o tema e identifica ângulos relevantes"},
            {"agent_slug": "content-creator", "title": "Rascunho do post", "desc": "Escreve o post inicial com hooks e CTA"},
            {"agent_slug": "brand-guardian", "title": "Revisão de marca", "desc": "Verifica consistência com a voz da marca"},
            {"agent_slug": "polish", "title": "Refinamento final", "desc": "Polimento e otimização do texto"},
        ]
    },
    {
        "slug": "code-review",
        "name": "Code Review Completo",
        "description": "Revisão de código com análise de segurança e performance",
        "emoji": "🔍",
        "squad_slug": "code-guardians",
        "steps": [
            {"agent_slug": "code-reviewer", "title": "Análise inicial", "desc": "Revisão geral do código e lógica"},
            {"agent_slug": "sentinel", "title": "Scan de segurança", "desc": "Identifica vulnerabilidades e issues de segurança"},
            {"agent_slug": "optimizer", "title": "Otimização", "desc": "Sugestões de performance e melhor práticas"},
            {"agent_slug": "janitor", "title": "Limpeza", "desc": "Verifica qualidade e consistência do código"},
        ]
    },
    {
        "slug": "landing-page",
        "name": "Landing Page",
        "description": "Cria uma landing page completa com copy e design",
        "emoji": "🎯",
        "squad_slug": "ux-squad",
        "steps": [
            {"agent_slug": "ux-researcher", "title": "Pesquisa de usuários", "desc": "Define persona e jornada do usuário"},
            {"agent_slug": "ux-writer", "title": "Copy estratégico", "desc": "Escreve headlines, benefícios e CTA"},
            {"agent_slug": "ui-designer", "title": "Design da página", "desc": "Cria layout e componentes visuais"},
            {"agent_slug": "polish", "title": "Polimento", "desc": "Refina detalhes visuais e microcopy"},
        ]
    },
    {
        "slug": "growth-experiment",
        "name": "Experimento de Growth",
        "description": "Planeja e executa um experimento de growth hacking",
        "emoji": "🚀",
        "squad_slug": "growth-team",
        "steps": [
            {"agent_slug": "growth-hacker", "title": "Hipótese", "desc": "Define hipótese e métricas do experimento"},
            {"agent_slug": "analytics-specialist", "title": "Setup analytics", "desc": "Configura tracking e métricas"},
            {"agent_slug": "content-creator", "title": "Assets", "desc": "Cria copy e materiais do experimento"},
            {"agent_slug": "experiment-tracker", "title": "Documentação", "desc": "Documenta o experimento para análise"},
        ]
    },
    {
        "slug": "qa-suite",
        "name": "Suíte de QA",
        "description": "Testes completos de qualidade para uma feature",
        "emoji": "🧪",
        "squad_slug": "qa-squad",
        "steps": [
            {"agent_slug": "tester", "title": "Testes manuais", "desc": "Executa casos de teste principais"},
            {"agent_slug": "api-tester", "title": "Testes de API", "desc": "Valida endpoints e integrações"},
            {"agent_slug": "performance-benchmarker", "title": "Performance", "desc": "Mede tempos de resposta e carga"},
            {"agent_slug": "test-results-analyzer", "title": "Análise", "desc": "Consolida resultados e identifica padrões"},
        ]
    },
    {
        "slug": "deploy-pipeline",
        "name": "Pipeline de Deploy",
        "description": "Configura e executa deploy com monitoramento",
        "emoji": "🚢",
        "squad_slug": "devops-crew",
        "steps": [
            {"agent_slug": "cicd-engineer", "title": "Configuração CI/CD", "desc": "Atualiza pipeline de deploy"},
            {"agent_slug": "sentinel", "title": "Pre-deploy check", "desc": "Validações de segurança pré-deploy"},
            {"agent_slug": "infrastructure-maintainer", "title": "Deploy", "desc": "Executa deploy em produção"},
            {"agent_slug": "analytics-specialist", "title": "Monitoramento", "desc": "Verifica métricas pós-deploy"},
        ]
    }
]


def get_agent_id(cur, slug):
    """Busca ID de um agente pelo slug"""
    cur.execute("SELECT id FROM agents WHERE slug = ?", (slug,))
    row = cur.fetchone()
    return row[0] if row else None


def seed_squads():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("🚀 Inicializando Squads V2...")
    print("=" * 60)
    
    for squad_config in SQUADS_CONFIG:
        print(f"\n📦 Criando squad: {squad_config['name']}")
        
        # Busca ID do master
        master_id = get_agent_id(cur, squad_config['master_slug'])
        if not master_id:
            print(f"  ⚠️  Master não encontrado: {squad_config['master_slug']}")
            continue
        
        # Cria/atualiza squad
        cur.execute("""
            INSERT INTO squads (slug, name, description, emoji, color, master_agent_id, capabilities)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(slug) DO UPDATE SET
                name = excluded.name,
                description = excluded.description,
                emoji = excluded.emoji,
                color = excluded.color,
                master_agent_id = excluded.master_agent_id,
                capabilities = excluded.capabilities
        """, (
            squad_config['slug'],
            squad_config['name'],
            squad_config['description'],
            squad_config['emoji'],
            squad_config['color'],
            master_id,
            json.dumps(squad_config['capabilities'])
        ))
        
        # Busca ID do squad
        cur.execute("SELECT id FROM squads WHERE slug = ?", (squad_config['slug'],))
        squad_id = cur.fetchone()[0]
        
        # Limpa membros antigos
        cur.execute("DELETE FROM squad_members WHERE squad_id = ?", (squad_id,))
        
        # Adiciona membros
        for idx, member in enumerate(squad_config['members']):
            agent_id = get_agent_id(cur, member['slug'])
            if not agent_id:
                print(f"  ⚠️  Membro não encontrado: {member['slug']}")
                continue
            
            cur.execute("""
                INSERT INTO squad_members (squad_id, agent_id, role_in_squad, order_index, can_loop)
                VALUES (?, ?, ?, ?, ?)
            """, (squad_id, agent_id, member['role'], idx, member['can_loop']))
            print(f"  ✅ {member['slug']} ({member['role']})")
        
        print(f"  🎯 Master: {squad_config['master_slug']}")
    
    conn.commit()
    
    # Cria serviços
    print("\n" + "=" * 60)
    print("⚙️  Criando Serviços...")
    print("=" * 60)
    
    for service_config in SERVICES_CONFIG:
        print(f"\n📋 {service_config['name']}")
        
        # Busca squad_id
        cur.execute("SELECT id FROM squads WHERE slug = ?", (service_config['squad_slug'],))
        row = cur.fetchone()
        if not row:
            print(f"  ⚠️  Squad não encontrado: {service_config['squad_slug']}")
            continue
        
        squad_id = row[0]
        
        # Cria/atualiza serviço
        cur.execute("""
            INSERT INTO services (slug, name, description, emoji, squad_id, input_schema, output_schema)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(slug) DO UPDATE SET
                name = excluded.name,
                description = excluded.description,
                emoji = excluded.emoji,
                squad_id = excluded.squad_id
        """, (
            service_config['slug'],
            service_config['name'],
            service_config['description'],
            service_config['emoji'],
            squad_id,
            json.dumps({"type": "object", "properties": {"tema": {"type": "string"}}}),
            json.dumps({"type": "object", "properties": {"resultado": {"type": "string"}}})
        ))
        
        # Busca service_id
        cur.execute("SELECT id FROM services WHERE slug = ?", (service_config['slug'],))
        service_id = cur.fetchone()[0]
        
        # Limpa steps antigos
        cur.execute("DELETE FROM service_steps WHERE service_id = ?", (service_id,))
        
        # Cria steps
        for idx, step in enumerate(service_config['steps'], 1):
            agent_id = get_agent_id(cur, step['agent_slug'])
            if not agent_id:
                print(f"  ⚠️  Agente não encontrado: {step['agent_slug']}")
                continue
            
            cur.execute("""
                INSERT INTO service_steps 
                (service_id, step_number, agent_id, title, description, instructions, is_loop_enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                service_id, idx, agent_id, step['title'], step['desc'],
                f"Execute como {step['agent_slug']}", 0
            ))
            print(f"  {idx}. {step['title']} ({step['agent_slug']})")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ Seed completo!")
    print("=" * 60)


if __name__ == "__main__":
    seed_squads()
