#!/usr/bin/env python3
"""
Dunder Mifflin Worker v2.0 - SQLite Local Edition
Sem dependência do Convex, roda 100% local.
"""


import os
import sys
import time
import json
import sqlite3
from datetime import datetime
from pathlib import Path

# Constantes
DB_PATH = Path(__file__).parent / "dunder_mifflin.db"
KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")


def init_db():
    """Inicializa o banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    with open(Path(__file__).parent / "schema.sql") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print(f"✅ Banco inicializado: {DB_PATH}")

def seed_agents():
    """Cria os 6 agentes do Dunder Mifflin"""
    agents = [
        {
            "slug": "michael",
            "name": "Michael Scott",
            "role": "Regional Manager",
            "description": "Gerente geral, coordena visão estratégica",
            "capabilities": json.dumps(["strategy", "planning", "coordination"]),
            "priority": 10
        },
        {
            "slug": "dwight",
            "name": "Dwight Schrute",
            "role": "Assistant Regional Manager",
            "description": "Executor eficiente, garante execução impecável",
            "capabilities": json.dumps(["execution", "analysis", "optimization"]),
            "priority": 9
        },
        {
            "slug": "jim",
            "name": "Jim Halpert",
            "role": "Sales & Relations",
            "description": "Criativo, humano, constrói relacionamentos",
            "capabilities": json.dumps(["creative", "communication", "empathy"]),
            "priority": 8
        },
        {
            "slug": "pam",
            "name": "Pam Beesly",
            "role": "Reception & Support",
            "description": "Suporte administrativo e organizacional",
            "capabilities": json.dumps(["organization", "support", "documentation"]),
            "priority": 6
        },
        {
            "slug": "ryan",
            "name": "Ryan Howard",
            "role": "Temp & Initiatives",
            "description": "Novas iniciativas, growth, experimentação",
            "capabilities": json.dumps(["growth", "experiments", "innovation"]),
            "priority": 5
        },
        {
            "slug": "creed",
            "name": "Creed Bratton",
            "role": "QA & Edge Cases",
            "description": "Testa limites, encontra falhas, thinking outside the box",
            "capabilities": json.dumps(["testing", "edge_cases", "unconventional"]),
            "priority": 4
        },
        {
            "slug": "quill",
            "name": "Quill",
            "role": "Content Writer",
            "description": "Escritor de conteúdo especializado em LinkedIn e posts",
            "capabilities": json.dumps(["writing", "linkedin", "content", "seo"]),
            "priority": 7
        }
    ]
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    for agent in agents:
        cur.execute("""
            INSERT OR IGNORE INTO agents (slug, name, role, description, capabilities, priority, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (agent["slug"], agent["name"], agent["role"], 
              agent["description"], agent["capabilities"], agent["priority"]))
    
    conn.commit()
    conn.close()
    print(f"✅ {len(agents)} agentes criados")

def list_agents():
    """Lista todos os agentes"""
    conn = _get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM agents ORDER BY priority DESC")
    result = _fetch_all_as_dict(cur)
    conn.close()
    return result

def get_agent_by_slug(slug):
    """Busca agente por slug"""
    conn = _get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM agents WHERE slug = ?", (slug,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def create_proposal(agent_id, title, description, mission_type="general", priority=5, parameters=None):
    """Cria uma proposta de missão"""
    code = f"PROP-{int(time.time() * 1000):x}"
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO proposals (proposal_code, agent_id, title, description, mission_type, priority, parameters, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
    """, (code, agent_id, title, description, mission_type, priority, json.dumps(parameters or {})))
    proposal_id = cur.lastrowid
    conn.commit()
    conn.close()
    
    print(f"✅ Proposta criada: {code} - {title}")
    return proposal_id

def approve_proposal(proposal_id, notes=""):
    """Aprova uma proposta e cria a missão"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Busca proposta
    cur.execute("SELECT * FROM proposals WHERE id = ?", (proposal_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    
    proposal = dict(zip([col[0] for col in cur.description], row))
    
    # Atualiza proposta
    cur.execute("""
        UPDATE proposals SET status = 'accepted', reviewed_at = ?, review_notes = ?
        WHERE id = ?
    """, (datetime.now().isoformat(), notes, proposal_id))
    
    # Cria missão
    mission_code = f"MS-{int(time.time() * 1000):x}"
    cur.execute("""
        INSERT INTO missions (mission_code, proposal_id, agent_id, title, description, mission_type, priority, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'approved')
    """, (mission_code, proposal_id, proposal["agent_id"], proposal["title"], 
          proposal["description"], proposal["mission_type"], proposal["priority"]))
    
    mission_id = cur.lastrowid
    conn.commit()
    conn.close()
    
    print(f"✅ Missão criada: {mission_code} - {proposal['title']}")
    return mission_id

def _fetch_all_as_dict(cur):
    """Helper: converte resultados da query para lista de dicts"""
    return [dict(row) for row in cur.fetchall()]


def _get_db_connection():
    """Helper: cria conexão com row_factory configurado"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def list_missions(status=None, limit=50):
    """Lista missões"""
    conn = _get_db_connection()
    cur = conn.cursor()
    
    base_query = """
        SELECT m.*, a.name as agent_name, a.slug as agent_slug 
        FROM missions m 
        JOIN agents a ON m.agent_id = a.id 
    """
    
    if status:
        cur.execute(base_query + "WHERE m.status = ? ORDER BY m.created_at DESC LIMIT ?", (status, limit))
    else:
        cur.execute(base_query + "ORDER BY m.created_at DESC LIMIT ?", (limit,))
    
    result = _fetch_all_as_dict(cur)
    conn.close()
    return result

def get_mission(mission_id):
    """Busca missão por ID"""
    conn = _get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.*, a.name as agent_name, a.slug as agent_slug 
        FROM missions m 
        JOIN agents a ON m.agent_id = a.id 
        WHERE m.id = ?
    """, (mission_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def start_mission(mission_id):
    """Marca missão como running"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        UPDATE missions SET status = 'running', started_at = ? WHERE id = ?
    """, (datetime.now().isoformat(), mission_id))
    conn.commit()
    conn.close()

def complete_mission(mission_id, status="succeeded", result=None, error_message=None):
    """Completa uma missão"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        UPDATE missions 
        SET status = ?, completed_at = ?, result = ?, error_message = ?
        WHERE id = ?
    """, (status, datetime.now().isoformat(), json.dumps(result or {}), error_message, mission_id))
    conn.commit()
    conn.close()

def get_dashboard_stats():
    """Retorna estatísticas do dashboard"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    stats = {}
    
    cur.execute("SELECT COUNT(*) FROM agents WHERE is_active = 1")
    stats["active_agents"] = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM agents")
    stats["total_agents"] = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM missions WHERE status = 'running'")
    stats["running_missions"] = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM missions WHERE status = 'succeeded'")
    stats["completed_missions"] = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM missions WHERE status = 'failed'")
    stats["failed_missions"] = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM proposals WHERE status = 'pending'")
    stats["pending_proposals"] = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM events WHERE occurred_at > datetime('now', '-24 hours')")
    stats["events_24h"] = cur.fetchone()[0]
    
    conn.close()
    return stats

def add_event(event_type, title, description=None, payload=None, severity="info", agent_id=None, mission_id=None):
    """Adiciona evento ao log"""
    code = f"EVT-{int(time.time() * 1000):x}"

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO events (event_code, event_type, title, description, payload, severity, agent_id, mission_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (code, event_type, title, description, json.dumps(payload or {}), severity, agent_id, mission_id))
    conn.commit()
    conn.close()


# ============================================================
# NOVAS FUNÇÕES PARA JULES AGENTS
# ============================================================

def list_departments():
    """Lista todos os departamentos"""
    conn = _get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT d.*, COUNT(a.id) as agent_count
        FROM departments d
        LEFT JOIN agents a ON a.department = d.slug
        GROUP BY d.id
        ORDER BY d.name
    """)
    result = _fetch_all_as_dict(cur)
    conn.close()
    return result


def get_department(slug):
    """Busca departamento por slug com seus agentes"""
    conn = _get_db_connection()
    cur = conn.cursor()

    # Busca departamento
    cur.execute("SELECT * FROM departments WHERE slug = ?", (slug,))
    dept_row = cur.fetchone()
    if not dept_row:
        conn.close()
        return None

    dept = dict(dept_row)

    # Busca agentes do departamento
    cur.execute("""
        SELECT id, slug, name, role, avatar_emoji, is_active
        FROM agents
        WHERE department = ?
        ORDER BY priority DESC, name
    """, (slug,))
    dept['agents'] = _fetch_all_as_dict(cur)

    conn.close()
    return dept


def list_agents_by_department(department=None):
    """Lista agentes, opcionalmente filtrado por departamento"""
    conn = _get_db_connection()
    cur = conn.cursor()

    base_query = """
        SELECT a.*, d.name as department_name, d.emoji as department_emoji
        FROM agents a
        LEFT JOIN departments d ON a.department = d.slug
    """

    if department:
        cur.execute(base_query + "WHERE a.department = ? ORDER BY a.priority DESC, a.name", (department,))
    else:
        cur.execute(base_query + "ORDER BY a.department, a.priority DESC, a.name")

    result = _fetch_all_as_dict(cur)
    conn.close()
    return result


def get_agent_content(slug):
    """Busca agente com conteúdo completo do arquivo .md"""
    agent = get_agent_by_slug(slug)
    if not agent:
        return None

    # Lê o arquivo .md se existir
    if agent.get('file_path') and os.path.exists(agent['file_path']):
        with open(agent['file_path'], 'r', encoding='utf-8') as f:
            agent['content'] = f.read()
    else:
        agent['content'] = None

    return agent


def list_personas():
    """Lista todas as personas com seus agentes mapeados"""
    conn = _get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.*, a.name as agent_name, a.slug as agent_slug, a.department
        FROM personas p
        LEFT JOIN agents a ON p.agent_id = a.id
        ORDER BY p.name
    """)
    result = _fetch_all_as_dict(cur)
    conn.close()
    return result


def get_persona(slug):
    """Busca persona por slug"""
    conn = _get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.*, a.name as agent_name, a.slug as agent_slug,
               a.department, a.role as agent_role, a.description as agent_description
        FROM personas p
        LEFT JOIN agents a ON p.agent_id = a.id
        WHERE p.slug = ?
    """, (slug,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def list_commands(command_type=None):
    """Lista todos os comandos"""
    conn = _get_db_connection()
    cur = conn.cursor()

    if command_type:
        cur.execute("SELECT * FROM commands WHERE command_type = ? ORDER BY slug", (command_type,))
    else:
        cur.execute("SELECT * FROM commands ORDER BY command_type, slug")

    result = _fetch_all_as_dict(cur)
    conn.close()
    return result


def get_command(slug):
    """Busca comando por slug"""
    conn = _get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM commands WHERE slug = ?", (slug,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_events(limit=50):
    """Lista eventos recentes"""
    conn = _get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT e.*, a.name as agent_name, m.title as mission_title
        FROM events e
        LEFT JOIN agents a ON e.agent_id = a.id
        LEFT JOIN missions m ON e.mission_id = m.id
        ORDER BY e.occurred_at DESC
        LIMIT ?
    """, (limit,))
    result = _fetch_all_as_dict(cur)
    conn.close()
    return result


def list_proposals(status=None, limit=50):
    """Lista propostas"""
    conn = _get_db_connection()
    cur = conn.cursor()

    base_query = """
        SELECT p.*, a.name as agent_name, a.slug as agent_slug, a.avatar_emoji
        FROM proposals p
        JOIN agents a ON p.agent_id = a.id
    """

    if status:
        cur.execute(base_query + "WHERE p.status = ? ORDER BY p.proposed_at DESC LIMIT ?", (status, limit))
    else:
        cur.execute(base_query + "ORDER BY p.proposed_at DESC LIMIT ?", (limit,))

    result = _fetch_all_as_dict(cur)
    conn.close()
    return result


def get_dashboard_stats_extended():
    """Retorna estatísticas estendidas do dashboard"""
    stats = get_dashboard_stats()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Contagens adicionais
    cur.execute("SELECT COUNT(*) FROM departments")
    stats["total_departments"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM personas")
    stats["total_personas"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM commands")
    stats["total_commands"] = cur.fetchone()[0]

    # Missões por status
    cur.execute("SELECT COUNT(*) FROM missions WHERE status = 'approved'")
    stats["approved_missions"] = cur.fetchone()[0]

    # Agentes por departamento
    cur.execute("""
        SELECT department, COUNT(*) as count
        FROM agents
        GROUP BY department
        ORDER BY count DESC
    """)
    stats["agents_by_department"] = {row[0]: row[1] for row in cur.fetchall()}

    conn.close()
    return stats


if __name__ == "__main__":
    print("🚀 Dunder Mifflin Database Manager")
    
    if len(sys.argv) < 2:
        print("""
Uso: python db.py <comando> [args]

Comandos:
  init              - Inicializa banco e cria schema
  seed              - Popula com agentes
  reset             - Recria tudo do zero
  agents            - Lista agentes
  proposals         - Lista propostas
  missions [status] - Lista missões (opcional: status)
  stats             - Mostra estatísticas
        """)
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "init":
        init_db()
    elif cmd == "seed":
        seed_agents()
    elif cmd == "reset":
        if DB_PATH.exists():
            DB_PATH.unlink()
        init_db()
        seed_agents()
        print("🔄 Banco resetado e populado")
    elif cmd == "agents":
        for a in list_agents():
            print(f"[{a['slug']}] {a['name']} - {a['role']} (prio: {a['priority']})")
    elif cmd == "missions":
        status = sys.argv[2] if len(sys.argv) > 2 else None
        for m in list_missions(status):
            print(f"[{m['status']}] {m['mission_code']} - {m['title']} ({m['agent_name']})")
    elif cmd == "stats":
        stats = get_dashboard_stats()
        for k, v in stats.items():
            print(f"{k}: {v}")
    else:
        print(f"Comando desconhecido: {cmd}")
