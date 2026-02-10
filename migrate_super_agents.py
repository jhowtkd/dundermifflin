#!/usr/bin/env python3
"""
Migração: 47 Agentes → 3 Super-Agentes
Atualiza o banco de dados do Dunder Mifflin
"""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "dunder_mifflin.db"

def migrate_to_super_agents():
    """Migra o banco para usar apenas 3 super-agentes"""
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("🚀 Iniciando migração: 47 agentes → 3 super-agentes")
    print()
    
    # 1. Desativa todos os agentes antigos (não deleta para manter histórico)
    print("1️⃣ Desativando agentes antigos...")
    cur.execute("UPDATE agents SET is_active = 0, daily_quota = 0")
    old_count = cur.rowcount
    print(f"   ✅ {old_count} agentes desativados")
    print()
    
    # 2. Cria/atualiza departamentos
    print("2️⃣ Configurando departamentos...")
    departments = [
        ("marketing", "Marketing", "📈", "Growth e aquisição de clientes"),
        ("engineering", "Engineering", "💻", "Tecnologia e produto"),
        ("executive", "Executive", "👔", "Estratégia e gestão")
    ]
    
    for slug, name, emoji, desc in departments:
        cur.execute("""
            INSERT OR REPLACE INTO departments (slug, name, emoji, description)
            VALUES (?, ?, ?, ?)
        """, (slug, name, emoji, desc))
    print("   ✅ 3 departamentos configurados")
    print()
    
    # 3. Insere os 3 super-agentes
    print("3️⃣ Criando super-agentes...")
    
    super_agents = [
        {
            "slug": "o-marketeiro",
            "name": "O Marketeiro",
            "department": "marketing",
            "role": "Growth Lead",
            "description": "Especialista em marketing digital, copywriting, paid media, social media e growth hacking. Fusão de 12 agentes especializados.",
            "capabilities": json.dumps([
                "copywriting", "paid_media", "seo", "social_media", 
                "growth_hacking", "content_strategy", "email_marketing",
                "brand_strategy", "conversion_optimization"
            ]),
            "avatar_emoji": "📈",
            "priority": 10,
            "daily_quota": 20,
            "file_path": "agents/super/SOUL-the-marketeiro.md",
            "level": "Operator"
        },
        {
            "slug": "o-dev",
            "name": "O Dev",
            "department": "engineering",
            "role": "Tech Lead",
            "description": "Fullstack developer, DevOps, arquiteto de sistemas e especialista em IA. Fusão de 15+ agentes de desenvolvimento.",
            "capabilities": json.dumps([
                "fullstack_development", "devops", "system_architecture",
                "ai_integration", "testing", "database_design",
                "api_design", "security", "performance_optimization"
            ]),
            "avatar_emoji": "💻",
            "priority": 10,
            "daily_quota": 15,
            "file_path": "agents/super/SOUL-the-dev.md",
            "level": "Operator"
        },
        {
            "slug": "o-executivo",
            "name": "O Executivo",
            "department": "executive",
            "role": "Chief Operator",
            "description": "Estrategista, gestor de operações e coordenador dos outros agentes. Autonomous level com autoridade total.",
            "capabilities": json.dumps([
                "strategic_planning", "operations", "financial_management",
                "team_coordination", "decision_making", "risk_management",
                "stakeholder_management", "performance_review"
            ]),
            "avatar_emoji": "👔",
            "priority": 10,
            "daily_quota": 10,
            "file_path": "agents/super/SOUL-the-executivo.md",
            "level": "Autonomous"
        }
    ]
    
    for agent in super_agents:
        # Verifica se já existe
        cur.execute("SELECT id FROM agents WHERE slug = ?", (agent["slug"],))
        existing = cur.fetchone()
        
        if existing:
            # Atualiza
            cur.execute("""
                UPDATE agents SET
                    name = ?,
                    department = ?,
                    role = ?,
                    description = ?,
                    capabilities = ?,
                    avatar_emoji = ?,
                    priority = ?,
                    daily_quota = ?,
                    file_path = ?,
                    is_active = 1,
                    quota_used = 0
                WHERE slug = ?
            """, (
                agent["name"], agent["department"], agent["role"],
                agent["description"], agent["capabilities"], agent["avatar_emoji"],
                agent["priority"], agent["daily_quota"], agent["file_path"],
                agent["slug"]
            ))
            print(f"   🔄 {agent['name']} atualizado")
        else:
            # Insere novo
            cur.execute("""
                INSERT INTO agents 
                (slug, name, department, role, description, capabilities, 
                 avatar_emoji, priority, daily_quota, file_path, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                agent["slug"], agent["name"], agent["department"],
                agent["role"], agent["description"], agent["capabilities"],
                agent["avatar_emoji"], agent["priority"], agent["daily_quota"],
                agent["file_path"]
            ))
            print(f"   ✅ {agent['name']} criado (Level: {agent['level']})")
    
    print()
    
    # 4. Cria tabela de handoffs se não existir
    print("4️⃣ Configurando sistema de handoffs...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS agent_handoffs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            handoff_code TEXT UNIQUE NOT NULL,
            from_agent TEXT NOT NULL,
            to_agent TEXT NOT NULL,
            task_type TEXT NOT NULL,
            context TEXT NOT NULL,
            deliverables TEXT,
            timeline TEXT,
            priority TEXT DEFAULT 'Medium',
            success_criteria TEXT,
            status TEXT DEFAULT 'pending',
            output TEXT,
            quality_rating INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME,
            FOREIGN KEY (from_agent) REFERENCES agents(slug),
            FOREIGN KEY (to_agent) REFERENCES agents(slug)
        )
    """)
    print("   ✅ Tabela agent_handoffs criada")
    print()
    
    # 5. Cria tabela de memórias se não existir
    print("5️⃣ Configurando sistema de memória...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS agent_memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_slug TEXT NOT NULL,
            memory_type TEXT NOT NULL, -- 'daily', 'longterm', 'project'
            project_slug TEXT,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_slug) REFERENCES agents(slug)
        )
    """)
    print("   ✅ Tabela agent_memories criada")
    print()
    
    # 6. Cria tabela de performance reviews
    print("6️⃣ Configurando sistema de performance reviews...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS agent_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_slug TEXT NOT NULL,
            review_date DATE NOT NULL,
            period_days INTEGER DEFAULT 30,
            rating REAL NOT NULL, -- 1-5
            status TEXT NOT NULL, -- 'exceeds', 'meets', 'partial', 'below'
            activities_count INTEGER,
            tasks_completed INTEGER,
            feedback TEXT,
            next_level_target TEXT,
            reviewed_by TEXT DEFAULT 'O Executivo',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_slug) REFERENCES agents(slug)
        )
    """)
    print("   ✅ Tabela agent_reviews criada")
    print()
    
    conn.commit()
    conn.close()
    
    print("=" * 60)
    print("✅ MIGRAÇÃO CONCLUÍDA!")
    print("=" * 60)
    print()
    print("Resumo:")
    print(f"  • {old_count} agentes antigos desativados")
    print(f"  • 3 super-agentes ativados:")
    print(f"    - O Marketeiro (Level: Operator)")
    print(f"    - O Dev (Level: Operator)")
    print(f"    - O Executivo (Level: Autonomous)")
    print()
    print("Sistemas implementados:")
    print("  ✅ Handoff coordination")
    print("  ✅ Memory persistence")
    print("  ✅ Performance reviews")
    print()
    print("Próximos passos:")
    print("  1. Atualizar worker_v2.py para usar super-agentes")
    print("  2. Implementar sistema de handoffs no worker")
    print("  3. Criar dashboard integrado")

if __name__ == "__main__":
    migrate_to_super_agents()
