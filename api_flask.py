#!/usr/bin/env python3
"""
Dunder Mifflin + Jules Agents API REST - Flask Edition
Sistema de Gerenciamento de Agentes AI
"""

import os
import json
import sqlite3
from pathlib import Path
from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
from datetime import datetime
import time
import mimetypes

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

DB_PATH = Path(__file__).parent / "dunder_mifflin.db"
FILES_BASE = Path.home() / ".openclaw" / "workspace" / "studio" / "projects" / "dunder_mifflin"
JULES_AGENTS_DIR = Path(__file__).parent / "agents"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "service": "dunder-mifflin-api"})

@app.route('/api/agents')
def get_agents():
    """Lista agentes com filtro opcional por departamento"""
    department = request.args.get('dept') or request.args.get('department')
    conn = get_db()
    cur = conn.cursor()

    if department:
        cur.execute("""
            SELECT a.*, d.name as department_name, d.emoji as department_emoji
            FROM agents a
            LEFT JOIN departments d ON a.department = d.slug
            WHERE a.department = ?
            ORDER BY a.priority DESC, a.name
        """, (department,))
    else:
        cur.execute("""
            SELECT a.*, d.name as department_name, d.emoji as department_emoji
            FROM agents a
            LEFT JOIN departments d ON a.department = d.slug
            ORDER BY a.department, a.priority DESC, a.name
        """)

    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({"agents": rows, "count": len(rows)})


@app.route('/api/agents/<slug>')
def get_agent(slug):
    """Busca agente por slug"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.*, d.name as department_name, d.emoji as department_emoji
        FROM agents a
        LEFT JOIN departments d ON a.department = d.slug
        WHERE a.slug = ?
    """, (slug,))
    row = cur.fetchone()
    conn.close()
    if row:
        return jsonify({"agent": dict(row)})
    return jsonify({"error": "Agent not found"}), 404


@app.route('/api/agents/<slug>/content')
def get_agent_content(slug):
    """Busca agente com conteúdo completo do arquivo .md"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM agents WHERE slug = ?", (slug,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Agent not found"}), 404

    agent = dict(row)

    # Lê o arquivo .md se existir
    if agent.get('file_path') and os.path.exists(agent['file_path']):
        with open(agent['file_path'], 'r', encoding='utf-8') as f:
            agent['content'] = f.read()
    else:
        agent['content'] = None

    return jsonify({"agent": agent})

@app.route('/api/missions')
def get_missions():
    status = request.args.get('status')
    conn = get_db()
    cur = conn.cursor()
    
    if status:
        cur.execute("""
            SELECT m.*, a.name as agent_name, a.slug as agent_slug 
            FROM missions m 
            JOIN agents a ON m.agent_id = a.id 
            WHERE m.status = ? 
            ORDER BY m.created_at DESC
        """, (status,))
    else:
        cur.execute("""
            SELECT m.*, a.name as agent_name, a.slug as agent_slug 
            FROM missions m 
            JOIN agents a ON m.agent_id = a.id 
            ORDER BY m.created_at DESC
        """)
    
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({"missions": rows})

@app.route('/api/missions/<int:mission_id>')
def get_mission(mission_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.*, a.name as agent_name, a.slug as agent_slug 
        FROM missions m 
        JOIN agents a ON m.agent_id = a.id 
        WHERE m.id = ?
    """, (mission_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return jsonify({"mission": dict(row)})
    return jsonify({"error": "Mission not found"}), 404

@app.route('/api/proposals')
def get_proposals():
    status = request.args.get('status')
    conn = get_db()
    cur = conn.cursor()
    
    if status:
        cur.execute("""
            SELECT p.*, a.name as agent_name 
            FROM proposals p 
            JOIN agents a ON p.agent_id = a.id 
            WHERE p.status = ? 
            ORDER BY p.proposed_at DESC
        """, (status,))
    else:
        cur.execute("""
            SELECT p.*, a.name as agent_name 
            FROM proposals p 
            JOIN agents a ON p.agent_id = a.id 
            ORDER BY p.proposed_at DESC
        """)
    
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({"proposals": rows})

@app.route('/api/events')
def get_events():
    limit = request.args.get('limit', 50, type=int)
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT e.*, a.name as agent_name 
        FROM events e 
        LEFT JOIN agents a ON e.agent_id = a.id 
        ORDER BY e.occurred_at DESC 
        LIMIT ?
    """, (limit,))
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({"events": rows})

@app.route('/api/proposals', methods=['POST'])
def create_proposal():
    data = request.get_json() or {}
    
    agent_id = data.get("agentId")
    title = data.get("title")
    description = data.get("description", "")
    mission_type = data.get("missionType", "general")
    priority = data.get("priority", 5)
    
    if not agent_id or not title:
        return jsonify({"error": "agentId and title required"}), 400
    
    code = f"PROP-{int(time.time() * 1000):x}"
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO proposals (proposal_code, agent_id, title, description, mission_type, priority, status)
        VALUES (?, ?, ?, ?, ?, ?, 'pending')
    """, (code, agent_id, title, description, mission_type, priority))
    proposal_id = cur.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({"id": proposal_id, "code": code, "status": "created"})

@app.route('/api/proposals/<int:proposal_id>/approve', methods=['POST'])
def approve_proposal(proposal_id):
    data = request.get_json() or {}
    notes = data.get("notes", "")
    
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM proposals WHERE id = ?", (proposal_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Proposal not found"}), 404
    
    proposal = dict(row)
    
    cur.execute("""
        UPDATE proposals SET status = 'accepted', reviewed_at = ?, review_notes = ?
        WHERE id = ?
    """, (datetime.now().isoformat(), notes, proposal_id))
    
    mission_code = f"MS-{int(time.time() * 1000):x}"
    cur.execute("""
        INSERT INTO missions (mission_code, proposal_id, agent_id, title, description, mission_type, priority, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'approved')
    """, (mission_code, proposal_id, proposal["agent_id"], proposal["title"], 
          proposal["description"], proposal["mission_type"], proposal["priority"]))
    
    mission_id = cur.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({"missionId": mission_id, "code": mission_code, "status": "created"})

# === ENDPOINTS DE ARQUIVOS ===

@app.route('/api/files')
def list_files():
    """Lista todos os arquivos criados pelas missões"""
    try:
        files = []
        carousels_dir = FILES_BASE / "carousels"
        
        if carousels_dir.exists():
            for f in carousels_dir.iterdir():
                if f.is_file():
                    files.append({
                        "name": f.name,
                        "path": str(f.relative_to(FILES_BASE)),
                        "size": f.stat().st_size,
                        "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                    })
        
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/files/<path:filepath>')
def serve_file(filepath):
    """Serve arquivos do diretório de projetos"""
    try:
        # Normaliza o path
        safe_path = Path(FILES_BASE) / filepath

        # Verifica se está dentro do diretório permitido (segurança)
        try:
            safe_path.relative_to(FILES_BASE)
        except ValueError:
            return jsonify({"error": "Acesso negado"}), 403

        if not safe_path.exists():
            return jsonify({"error": "Arquivo não encontrado"}), 404

        if safe_path.is_dir():
            return jsonify({"error": "É um diretório"}), 400

        # Detecta o MIME type
        mime_type, _ = mimetypes.guess_type(str(safe_path))
        if not mime_type:
            mime_type = 'application/octet-stream'

        return send_file(safe_path, mimetype=mime_type)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# NOVOS ENDPOINTS PARA JULES AGENTS
# ============================================================

@app.route('/api/departments')
def get_departments():
    """Lista todos os departamentos"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT d.*, COUNT(a.id) as agent_count
        FROM departments d
        LEFT JOIN agents a ON a.department = d.slug
        GROUP BY d.id
        ORDER BY d.name
    """)
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({"departments": rows, "count": len(rows)})


@app.route('/api/departments/<slug>')
def get_department(slug):
    """Busca departamento por slug com seus agentes"""
    conn = get_db()
    cur = conn.cursor()

    # Busca departamento
    cur.execute("SELECT * FROM departments WHERE slug = ?", (slug,))
    dept_row = cur.fetchone()
    if not dept_row:
        conn.close()
        return jsonify({"error": "Department not found"}), 404

    dept = dict(dept_row)

    # Busca agentes do departamento
    cur.execute("""
        SELECT id, slug, name, role, avatar_emoji, is_active, priority
        FROM agents
        WHERE department = ?
        ORDER BY priority DESC, name
    """, (slug,))
    dept['agents'] = [dict(row) for row in cur.fetchall()]

    conn.close()
    return jsonify({"department": dept})


@app.route('/api/personas')
def get_personas():
    """Lista todas as personas com seus agentes mapeados"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.*, a.name as agent_name, a.slug as agent_slug, a.department
        FROM personas p
        LEFT JOIN agents a ON p.agent_id = a.id
        ORDER BY p.name
    """)
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({"personas": rows, "count": len(rows)})


@app.route('/api/personas/<slug>')
def get_persona(slug):
    """Busca persona por slug"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.*, a.name as agent_name, a.slug as agent_slug,
               a.department, a.role as agent_role, a.description as agent_description,
               a.capabilities, a.avatar_emoji as agent_emoji
        FROM personas p
        LEFT JOIN agents a ON p.agent_id = a.id
        WHERE p.slug = ?
    """, (slug,))
    row = cur.fetchone()
    conn.close()
    if row:
        return jsonify({"persona": dict(row)})
    return jsonify({"error": "Persona not found"}), 404


@app.route('/api/commands')
def get_commands():
    """Lista todos os comandos"""
    command_type = request.args.get('type')
    conn = get_db()
    cur = conn.cursor()

    if command_type:
        cur.execute("""
            SELECT * FROM commands WHERE command_type = ? ORDER BY slug
        """, (command_type,))
    else:
        cur.execute("SELECT * FROM commands ORDER BY command_type, slug")

    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({"commands": rows, "count": len(rows)})


@app.route('/api/commands/<slug>')
def get_command(slug):
    """Busca comando por slug"""
    # Normaliza slug (adiciona / se não tiver)
    if not slug.startswith('/'):
        slug = '/' + slug

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM commands WHERE slug = ?", (slug,))
    row = cur.fetchone()
    conn.close()
    if row:
        return jsonify({"command": dict(row)})
    return jsonify({"error": "Command not found"}), 404


@app.route('/api/stats')
def get_stats():
    """Retorna estatísticas estendidas do dashboard"""
    conn = get_db()
    cur = conn.cursor()

    stats = {}
    cur.execute("SELECT COUNT(*) FROM agents WHERE is_active = 1")
    stats["activeAgents"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM agents")
    stats["totalAgents"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM missions WHERE status = 'running'")
    stats["runningMissions"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM missions WHERE status = 'succeeded'")
    stats["completedMissions"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM missions WHERE status = 'failed'")
    stats["failedMissions"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM missions WHERE status = 'approved'")
    stats["approvedMissions"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM proposals WHERE status = 'pending'")
    stats["pendingProposals"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM events WHERE occurred_at > datetime('now', '-24 hours')")
    stats["events24h"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM departments")
    stats["totalDepartments"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM personas")
    stats["totalPersonas"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM commands")
    stats["totalCommands"] = cur.fetchone()[0]

    conn.close()
    return jsonify(stats)


# ============================================================
# ROTAS DO FRONTEND (servir arquivos estáticos)
# ============================================================

@app.route('/')
def serve_index():
    """Serve a página principal"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve arquivos estáticos do frontend"""
    # Verifica se é um arquivo que existe
    file_path = Path(app.static_folder) / path
    if file_path.exists() and file_path.is_file():
        return send_from_directory(app.static_folder, path)

    # Se é uma rota HTML sem extensão, adiciona .html
    if not '.' in path:
        html_path = Path(app.static_folder) / f"{path}.html"
        if html_path.exists():
            return send_from_directory(app.static_folder, f"{path}.html")

    # Fallback para index.html (SPA-like)
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    port = int(os.getenv("DM_API_PORT", "3003"))
    print(f"🚀 Dunder Mifflin API (Flask) rodando em http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
