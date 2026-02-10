#!/usr/bin/env python3
"""
Dunder Mifflin + Jules Agents API REST - Flask Edition
Sistema de Gerenciamento de Agentes AI
"""

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

# Constantes
DB_PATH = Path(__file__).parent / "dunder_mifflin.db"
FILES_BASE = Path.home() / ".openclaw" / "workspace" / "studio" / "projects" / "dunder_mifflin"
JULES_AGENTS_DIR = Path("/Users/jhonatan/Downloads/Jules/agents")
DEFAULT_API_PORT = 3003
MAX_MISSIONS_PER_BATCH = 2
HEARTBEAT_INTERVAL = 12  # iterações
SLEEP_INTERVAL = 5  # segundos

def generate_code(prefix):
    """Gera código único com prefixo"""
    import uuid
    return f"{prefix}-{uuid.uuid4().hex[:12]}"

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

DB_PATH = Path(__file__).parent / "dunder_mifflin.db"
FILES_BASE = Path.home() / ".openclaw" / "workspace" / "studio" / "projects" / "dunder_mifflin"
JULES_AGENTS_DIR = Path("/Users/jhonatan/Downloads/Jules/agents")

def get_db():
    """Obtém conexão com o banco de dados configurada"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _fetch_all_as_dict(cur):
    """Helper: converte resultados da query para lista de dicts"""
    return [dict(row) for row in cur.fetchall()]

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

    result = _fetch_all_as_dict(cur)
    conn.close()
    return jsonify({"agents": result, "count": len(result)})


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
    
    result = _fetch_all_as_dict(cur)
    conn.close()
    return jsonify({"missions": result})

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
    
    result = _fetch_all_as_dict(cur)
    conn.close()
    return jsonify({"proposals": result})

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
    result = _fetch_all_as_dict(cur)
    conn.close()
    return jsonify({"events": result})

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

# === ENDPOINTS DE FEEDBACK ===

@app.route('/api/feedbacks', methods=['GET'])
def get_feedbacks():
    """Lista feedbacks com filtros opcionais"""
    feedback_type = request.args.get('type')
    plan_id = request.args.get('plan_id')
    session_id = request.args.get('session_id')
    agent_id = request.args.get('agent_id')
    
    conn = get_db()
    cur = conn.cursor()
    
    query = """
        SELECT f.*, 
               p.title as plan_title, p.plan_code,
               s.session_code,
               a.name as agent_name, a.avatar_emoji as agent_emoji
        FROM feedbacks f
        LEFT JOIN execution_plans p ON f.plan_id = p.id
        LEFT JOIN orchestration_sessions s ON f.session_id = s.id
        LEFT JOIN agents a ON f.agent_id = a.id
        WHERE 1=1
    """
    params = []
    
    if feedback_type:
        query += " AND f.feedback_type = ?"
        params.append(feedback_type)
    if plan_id:
        query += " AND f.plan_id = ?"
        params.append(plan_id)
    if session_id:
        query += " AND f.session_id = ?"
        params.append(session_id)
    if agent_id:
        query += " AND f.agent_id = ?"
        params.append(agent_id)
    
    query += " ORDER BY f.created_at DESC"
    
    cur.execute(query, params)
    feedbacks = [dict(row) for row in cur.fetchall()]
    
    for fb in feedbacks:
        fb['tags'] = json.loads(fb.get('tags', '[]') or '[]')
    
    conn.close()
    return jsonify({"feedbacks": feedbacks, "count": len(feedbacks)})


@app.route('/api/feedbacks/<feedback_code>', methods=['GET'])
def get_feedback(feedback_code):
    """Busca um feedback específico"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT f.*, 
               p.title as plan_title, p.plan_code,
               s.session_code,
               a.name as agent_name, a.avatar_emoji as agent_emoji
        FROM feedbacks f
        LEFT JOIN execution_plans p ON f.plan_id = p.id
        LEFT JOIN orchestration_sessions s ON f.session_id = s.id
        LEFT JOIN agents a ON f.agent_id = a.id
        WHERE f.feedback_code = ?
    """, (feedback_code,))
    
    row = cur.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"error": "Feedback not found"}), 404
    
    feedback = dict(row)
    feedback['tags'] = json.loads(feedback.get('tags', '[]') or '[]')
    return jsonify({"feedback": feedback})


@app.route('/api/feedbacks', methods=['POST'])
def create_feedback():
    """Cria um novo feedback"""
    data = request.get_json() or {}
    
    plan_id = data.get('plan_id')
    session_id = data.get('session_id')
    agent_id = data.get('agent_id')
    user_name = data.get('user_name', 'Usuário')
    feedback_type = data.get('feedback_type', 'general')
    rating = data.get('rating')
    content = data.get('content')
    tags = json.dumps(data.get('tags', []))
    
    if not content:
        return jsonify({"error": "content is required"}), 400
    
    feedback_code = generate_code('FB')
    
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO feedbacks 
        (feedback_code, plan_id, session_id, agent_id, user_name, 
         feedback_type, rating, content, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (feedback_code, plan_id, session_id, agent_id, user_name,
          feedback_type, rating, content, tags))
    
    # Se tem agent_id e rating, também salva em agent_ratings
    if agent_id and rating:
        cur.execute("""
            INSERT INTO agent_ratings (agent_id, session_id, plan_id, rating, feedback)
            VALUES (?, ?, ?, ?, ?)
        """, (agent_id, session_id, plan_id, rating, content))
    
    conn.commit()
    conn.close()
    
    return jsonify({"feedback_code": feedback_code, "status": "created"}), 201


@app.route('/api/feedbacks/<feedback_code>/respond', methods=['POST'])
def respond_to_feedback(feedback_code):
    """Responde a um feedback (admin)"""
    data = request.get_json() or {}
    response = data.get('response')
    
    if not response:
        return jsonify({"error": "response is required"}), 400
    
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE feedbacks 
        SET admin_response = ?, is_resolved = 1, updated_at = ?
        WHERE feedback_code = ?
    """, (response, datetime.now().isoformat(), feedback_code))
    
    success = cur.rowcount > 0
    conn.commit()
    conn.close()
    
    if success:
        return jsonify({"feedback_code": feedback_code, "status": "responded"})
    else:
        return jsonify({"error": "Feedback not found"}), 404


@app.route('/api/agents/<int:agent_id>/ratings', methods=['GET'])
def get_agent_ratings(agent_id):
    """Busca ratings e estatísticas de um agente"""
    conn = get_db()
    cur = conn.cursor()
    
    # Busca ratings
    cur.execute("""
        SELECT ar.*, p.title as plan_title, s.session_code
        FROM agent_ratings ar
        LEFT JOIN execution_plans p ON ar.plan_id = p.id
        LEFT JOIN orchestration_sessions s ON ar.session_id = s.id
        WHERE ar.agent_id = ?
        ORDER BY ar.created_at DESC
    """, (agent_id,))
    
    ratings = [dict(row) for row in cur.fetchall()]
    
    # Calcula estatísticas
    cur.execute("""
        SELECT 
            COUNT(*) as total_ratings,
            AVG(rating) as avg_rating,
            COUNT(CASE WHEN rating = 5 THEN 1 END) as five_stars,
            COUNT(CASE WHEN rating = 4 THEN 1 END) as four_stars,
            COUNT(CASE WHEN rating = 3 THEN 1 END) as three_stars,
            COUNT(CASE WHEN rating = 2 THEN 1 END) as two_stars,
            COUNT(CASE WHEN rating = 1 THEN 1 END) as one_star
        FROM agent_ratings
        WHERE agent_id = ?
    """, (agent_id,))
    
    stats = dict(cur.fetchone())
    conn.close()
    
    return jsonify({
        "ratings": ratings,
        "stats": stats
    })


# === ENDPOINTS DE EXECUTION PLANS ===

@app.route('/api/execution-plans/<int:plan_id>')
def get_execution_plan(plan_id):
    """Busca execution plan por ID com resultado"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, plan_code, title, objective, status, 
                   final_result, created_at, completed_at
            FROM execution_plans
            WHERE id = ?
        """, (plan_id,))
        
        row = cur.fetchone()
        conn.close()
        
        if not row:
            return jsonify({"error": "Execution plan not found"}), 404
        
        plan = dict(row)
        return jsonify(plan)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# === ENDPOINTS DE ARQUIVOS ===

@app.route('/api/files')
def list_files():
    """Lista todos os arquivos criados pelas missões"""
    try:
        files = []
        
        # Pastas a serem listadas
        folders = ["carousels", "social_plans", "blog_posts", "tiktok_scripts", "repurposed_content"]
        
        for folder in folders:
            folder_dir = FILES_BASE / folder
            if folder_dir.exists():
                for f in folder_dir.iterdir():
                    if f.is_file():
                        files.append({
                            "name": f.name,
                            "path": str(f.relative_to(FILES_BASE)),
                            "folder": folder,
                            "size": f.stat().st_size,
                            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                        })
        
        # Ordena por data de modificação (mais recentes primeiro)
        files.sort(key=lambda x: x["modified"], reverse=True)
        
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
    result = _fetch_all_as_dict(cur)
    conn.close()
    return jsonify({"departments": result, "count": len(result)})


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
    dept['agents'] = _fetch_all_as_dict(cur)

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
    result = _fetch_all_as_dict(cur)
    conn.close()
    return jsonify({"personas": result, "count": len(result)})


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

    result = _fetch_all_as_dict(cur)
    conn.close()
    return jsonify({"commands": result, "count": len(result)})


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
# ORCHESTRATION V2 - NOVOS ENDPOINTS
# ============================================================

@app.route('/api/services', methods=['GET'])
def get_services():
    """Lista todos os serviços disponíveis"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, service_code, name, slug, description, icon_emoji, 
               agent_sequence, loop_config, requires_approval
        FROM services WHERE is_active = 1 ORDER BY name
    """)
    services = _fetch_all_as_dict(cur)
    
    for svc in services:
        svc['agent_sequence'] = json.loads(svc.get('agent_sequence', '[]') or '[]')
        svc['loop_config'] = json.loads(svc.get('loop_config', '{}') or '{}')
    
    conn.close()
    return jsonify({"services": services, "count": len(services)})


@app.route('/api/services/<slug>', methods=['GET'])
def get_service(slug):
    """Busca um serviço com seus steps"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM services WHERE slug = ? AND is_active = 1
    """, (slug,))
    row = cur.fetchone()
    
    if not row:
        conn.close()
        return jsonify({"error": "Service not found"}), 404
    
    service = dict(row)
    service['agent_sequence'] = json.loads(service.get('agent_sequence', '[]') or '[]')
    service['loop_config'] = json.loads(service.get('loop_config', '{}') or '{}')
    
    # Busca steps
    cur.execute("""
        SELECT * FROM service_steps WHERE service_id = ? ORDER BY step_order
    """, (service['id'],))
    service['steps'] = [dict(row) for row in cur.fetchall()]
    
    conn.close()
    return jsonify({"service": service})


@app.route('/api/services', methods=['POST'])
def create_service():
    """Cria um novo serviço"""
    data = request.get_json() or {}
    
    service_code = f"SVC-{int(time.time() * 1000):x}"
    name = data.get('name')
    slug = data.get('slug')
    description = data.get('description', '')
    icon_emoji = data.get('icon_emoji', '⚙️')
    agent_sequence = json.dumps(data.get('agent_sequence', []))
    loop_config = json.dumps(data.get('loop_config')) if data.get('loop_config') else None
    execution_type = data.get('execution_type', 'single')
    variation_contexts = json.dumps(data.get('variation_contexts')) if data.get('variation_contexts') else None
    
    if not name or not slug:
        return jsonify({"error": "name and slug required"}), 400
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO services 
            (service_code, name, slug, description, icon_emoji, agent_sequence, loop_config, execution_type, variation_contexts)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (service_code, name, slug, description, icon_emoji, agent_sequence, loop_config, execution_type, variation_contexts))
        
        service_id = cur.lastrowid
        
        # Insere steps
        for idx, step in enumerate(data.get('steps', []), 1):
            cur.execute("""
                INSERT INTO service_steps 
                (service_id, step_order, agent_slug, step_name, action_type)
                VALUES (?, ?, ?, ?, ?)
            """, (service_id, idx, step['agent_slug'], step['step_name'], step.get('action_type', 'execute')))
        
        conn.commit()
        conn.close()
        
        return jsonify({"id": service_id, "service_code": service_code, "status": "created"}), 201
        
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Service with this slug already exists"}), 409


@app.route('/api/plans', methods=['GET'])
def get_plans():
    """Lista planos com filtro opcional por status"""
    status = request.args.get('status')
    
    conn = get_db()
    cur = conn.cursor()
    
    if status:
        cur.execute("""
            SELECT ep.*, s.name as service_name, s.icon_emoji
            FROM execution_plans ep
            JOIN services s ON ep.service_id = s.id
            WHERE ep.status = ?
            ORDER BY ep.created_at DESC
        """, (status,))
    else:
        cur.execute("""
            SELECT ep.*, s.name as service_name, s.icon_emoji
            FROM execution_plans ep
            JOIN services s ON ep.service_id = s.id
            ORDER BY ep.created_at DESC
        """)
    
    plans = _fetch_all_as_dict(cur)
    
    for plan in plans:
        plan['planned_steps'] = json.loads(plan.get('planned_steps', '[]') or '[]')
    
    conn.close()
    return jsonify({"plans": plans, "count": len(plans)})


@app.route('/api/plans/<plan_code>', methods=['GET'])
def get_plan(plan_code):
    """Busca um plano específico com detalhes"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT ep.*, s.name as service_name, s.icon_emoji, s.agent_sequence
        FROM execution_plans ep
        JOIN services s ON ep.service_id = s.id
        WHERE ep.plan_code = ?
    """, (plan_code,))
    row = cur.fetchone()
    
    if not row:
        conn.close()
        return jsonify({"error": "Plan not found"}), 404
    
    plan = dict(row)
    plan['planned_steps'] = json.loads(plan.get('planned_steps', '[]') or '[]')
    plan['agent_sequence'] = json.loads(plan.get('agent_sequence', '[]') or '[]')
    
    conn.close()
    return jsonify({"plan": plan})


@app.route('/api/plans', methods=['POST'])
def create_plan():
    """Cria um novo plano via Master Agent"""
    data = request.get_json() or {}
    
    service_id = data.get('service_id')
    title = data.get('title')
    objective = data.get('objective', title)
    input_data = data.get('input_data', {})
    
    if not service_id or not title:
        return jsonify({"error": "service_id and title required"}), 400
    
    # Importa e usa o MasterAgent
    from orchestrator import MasterAgent
    master = MasterAgent()
    
    try:
        plan = master.create_plan(
            service_id=service_id,
            title=title,
            objective=objective,
            input_data=input_data
        )
        
        return jsonify(plan), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/plans/<plan_code>/approve', methods=['POST'])
def approve_plan_endpoint(plan_code):
    """Aprova um plano"""
    from orchestrator import approve_plan
    
    data = request.get_json() or {}
    approved_by = data.get('approved_by', 'user')
    
    if approve_plan(plan_code, approved_by):
        return jsonify({"plan_code": plan_code, "status": "approved"})
    else:
        return jsonify({"error": "Plan not found or already processed"}), 404


@app.route('/api/plans/<plan_code>/reject', methods=['POST'])
def reject_plan_endpoint(plan_code):
    """Rejeita um plano"""
    from orchestrator import reject_plan
    
    data = request.get_json() or {}
    reason = data.get('reason', 'Rejeitado pelo usuário')
    
    if reject_plan(plan_code, reason):
        return jsonify({"plan_code": plan_code, "status": "rejected"})
    else:
        return jsonify({"error": "Plan not found or already processed"}), 404


@app.route('/api/orchestration/sessions', methods=['GET'])
def get_sessions():
    """Lista sessões de orquestração"""
    status = request.args.get('status')
    
    conn = get_db()
    cur = conn.cursor()
    
    if status:
        cur.execute("""
            SELECT os.*, ep.title as plan_title, ep.plan_code
            FROM orchestration_sessions os
            JOIN execution_plans ep ON os.execution_plan_id = ep.id
            WHERE os.status = ?
            ORDER BY os.created_at DESC
        """, (status,))
    else:
        cur.execute("""
            SELECT os.*, ep.title as plan_title, ep.plan_code
            FROM orchestration_sessions os
            JOIN execution_plans ep ON os.execution_plan_id = ep.id
            ORDER BY os.created_at DESC
        """)
    
    sessions = _fetch_all_as_dict(cur)
    conn.close()
    return jsonify({"sessions": sessions})


@app.route('/api/orchestration/sessions/<session_code>', methods=['GET'])
def get_session(session_code):
    """Busca uma sessão com mensagens"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT os.*, ep.title as plan_title, ep.plan_code, ep.objective
        FROM orchestration_sessions os
        JOIN execution_plans ep ON os.execution_plan_id = ep.id
        WHERE os.session_code = ?
    """, (session_code,))
    row = cur.fetchone()
    
    if not row:
        conn.close()
        return jsonify({"error": "Session not found"}), 404
    
    session = dict(row)
    session['shared_context'] = json.loads(session.get('shared_context', '{}') or '{}')
    session['agent_outputs'] = json.loads(session.get('agent_outputs', '[]') or '[]')
    
    # Busca mensagens
    cur.execute("""
        SELECT m.*, a.name as from_name, a.avatar_emoji as from_emoji
        FROM agent_messages_v2 m
        LEFT JOIN agents a ON m.from_agent_id = a.id
        WHERE m.session_id = ?
        ORDER BY m.created_at
    """, (session['id'],))
    session['messages'] = _fetch_all_as_dict(cur)
    
    conn.close()
    return jsonify({"session": session})


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


# ============================================================
# RALPH LOOP ENDPOINTS
# ============================================================

@app.route('/api/ralph/loop', methods=['POST'])
def create_ralph_loop():
    """Cria um novo Ralph Loop via API"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    agent_slug = data.get('agent') or data.get('agent_slug')
    task = data.get('task') or data.get('task_description')
    max_iterations = data.get('max_iterations', 20)
    
    if not agent_slug or not task:
        return jsonify({"error": "Missing agent or task"}), 400
    
    # Mapear nomes simplificados
    agent_map = {
        'dev': 'o-dev',
        'marketeiro': 'o-marketeiro',
        'mkt': 'o-marketeiro',
        'executivo': 'o-executivo',
        'exec': 'o-executivo'
    }
    agent_slug = agent_map.get(agent_slug, agent_slug)
    
    try:
        # Importar e criar loop
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from ralph_loop import create_loop
        
        loop_code = create_loop(agent_slug, task, max_iterations)
        
        # URLs acessíveis
        dashboard_url = f"http://100.94.223.52:8888/ralph-dashboard.html?loop={loop_code}"
        
        return jsonify({
            "success": True,
            "loop_code": loop_code,
            "agent": agent_slug,
            "task": task,
            "status": "running",
            "dashboard_url": dashboard_url
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/ralph/loops/active', methods=['GET'])
def get_ralph_loops_active():
    """Retorna loops Ralph atualmente em execução"""
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from ralph_loop import get_active_loops
        
        loops = get_active_loops()
        return jsonify(loops)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/ralph/loops/history', methods=['GET'])
def get_ralph_loops_history():
    """Retorna histórico de loops completados/falhos"""
    limit = request.args.get('limit', 50, type=int)
    
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from ralph_loop import get_loop_history
        
        loops = get_loop_history(limit=limit)
        return jsonify(loops)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/ralph/costs/summary', methods=['GET'])
def get_ralph_costs_summary():
    """Retorna resumo de custos"""
    days = request.args.get('days', 30, type=int)
    
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from ralph_loop import get_cost_summary
        
        summary = get_cost_summary(days=days)
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/ralph/metrics/agents', methods=['GET'])
def get_ralph_agent_metrics():
    """Retorna métricas por agente"""
    days = request.args.get('days', 7, type=int)
    
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from ralph_loop import get_agent_metrics
        
        metrics = get_agent_metrics(days=days)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/ralph/notifications', methods=['GET'])
def get_ralph_notifications():
    """Retorna notificações pendentes"""
    notifications_dir = Path(__file__).parent / "loops" / "notifications"
    
    if not notifications_dir.exists():
        return jsonify({"notifications": []})
    
    notifications = []
    
    for notif_file in notifications_dir.glob("*.json"):
        try:
            with open(notif_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if data.get('status_notification') == 'pending':
                notifications.append(data)
                # Marcar como lido
                data['status_notification'] = 'read'
                with open(notif_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Erro ao ler notificação {notif_file}: {e}")
    
    notifications.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return jsonify({"notifications": notifications[:10]})


@app.route('/api/ralph/notifications/clear', methods=['POST'])
def clear_ralph_notifications():
    """Limpa todas as notificações"""
    notifications_dir = Path(__file__).parent / "loops" / "notifications"
    
    if notifications_dir.exists():
        for notif_file in notifications_dir.glob("*.json"):
            try:
                notif_file.unlink()
            except Exception as e:
                print(f"Erro ao remover {notif_file}: {e}")
    
    return jsonify({"success": True, "message": "Notificações limpas"})


@app.route('/api/ralph/results/<filename>', methods=['GET'])
def get_ralph_result(filename):
    """Retorna o conteúdo de um arquivo de resultado"""
    try:
        results_dir = Path(__file__).parent / "loops" / "results"
        file_path = results_dir / filename
        
        # Verificar se o arquivo existe e está dentro do diretório de resultados
        if not file_path.exists() or not str(file_path.resolve()).startswith(str(results_dir.resolve())):
            return jsonify({"error": "Arquivo não encontrado"}), 404
        
        return send_file(file_path, mimetype='text/markdown')
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# RALPH SWARM v5.0 - Endpoints
# ============================================================

from ralph_swarm_core import ChannelSystem, SwarmAgentManager, SwarmTaskManager, AuthorType, TaskStatus

# Instanciar gerenciadores
swarm_channels = ChannelSystem()
swarm_agents = SwarmAgentManager()
swarm_tasks = SwarmTaskManager()

@app.route('/api/swarm/channels', methods=['GET'])
def get_swarm_channels():
    """Lista todos os canais do swarm"""
    try:
        channels = swarm_channels.get_channels()
        
        # Adicionar contagem de mensagens para cada canal
        for ch in channels:
            ch['message_count'] = swarm_channels.get_message_count(ch['name'])
        
        return jsonify({
            "channels": channels,
            "count": len(channels)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/swarm/channels/<channel_name>', methods=['GET'])
def get_swarm_channel(channel_name):
    """Retorna detalhes de um canal específico"""
    try:
        channel_id = swarm_channels.get_channel_id(channel_name)
        if not channel_id:
            return jsonify({"error": f"Canal '{channel_name}' não encontrado"}), 404
        
        channels = swarm_channels.get_channels()
        channel = next((c for c in channels if c['id'] == channel_id), None)
        
        if channel:
            channel['message_count'] = swarm_channels.get_message_count(channel_name)
        
        return jsonify({"channel": channel})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/swarm/channels/<channel_name>/messages', methods=['GET'])
def get_swarm_messages(channel_name):
    """Retorna mensagens de um canal"""
    try:
        limit = request.args.get('limit', 50, type=int)
        before_id = request.args.get('before_id', type=int)
        
        messages = swarm_channels.read(channel_name, limit=limit, before_id=before_id)
        
        return jsonify({
            "channel": channel_name,
            "messages": [m.to_dict() for m in messages],
            "count": len(messages)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/swarm/channels/<channel_name>/post', methods=['POST'])
def post_swarm_message(channel_name):
    """Posta mensagem em um canal"""
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({"error": "Campo 'content' é obrigatório"}), 400
        
        author_type = data.get('author_type', 'user')
        author_id = data.get('author_id', 'anonymous')
        content = data['content']
        mentions = data.get('mentions', [])
        
        # Validar author_type
        try:
            author_type_enum = AuthorType(author_type)
        except ValueError:
            return jsonify({"error": f"author_type inválido: {author_type}"}), 400
        
        message = swarm_channels.post(
            channel_name=channel_name,
            author_type=author_type_enum,
            author_id=author_id,
            content=content,
            mentions=mentions
        )
        
        return jsonify({
            "success": True,
            "message": message.to_dict()
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/swarm/channels/<channel_name>/search', methods=['GET'])
def search_swarm_messages(channel_name):
    """Busca mensagens em um canal"""
    try:
        query = request.args.get('q')
        limit = request.args.get('limit', 20, type=int)
        
        if not query:
            return jsonify({"error": "Parâmetro 'q' é obrigatório"}), 400
        
        messages = swarm_channels.search(channel_name, query, limit=limit)
        
        return jsonify({
            "channel": channel_name,
            "query": query,
            "messages": [m.to_dict() for m in messages],
            "count": len(messages)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/swarm/agents', methods=['GET'])
def get_swarm_agents():
    """Lista todos os agents do swarm"""
    try:
        agents = swarm_agents.get_all_agents()
        
        return jsonify({
            "agents": [a.to_dict() for a in agents],
            "count": len(agents)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/swarm/agents/<agent_slug>', methods=['GET'])
def get_swarm_agent(agent_slug):
    """Retorna detalhes de um agent específico"""
    try:
        agent = swarm_agents.get_agent(agent_slug)
        
        if not agent:
            return jsonify({"error": f"Agent '{agent_slug}' não encontrado"}), 404
        
        return jsonify({"agent": agent.to_dict()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/swarm/agents/<agent_slug>/status', methods=['PUT'])
def update_swarm_agent_status(agent_slug):
    """Atualiza status de um agent"""
    try:
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({"error": "Campo 'status' é obrigatório"}), 400
        
        swarm_agents.update_status(agent_slug, data['status'])
        
        return jsonify({
            "success": True,
            "message": f"Status de '{agent_slug}' atualizado para '{data['status']}'"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/swarm/tasks', methods=['GET'])
def get_swarm_tasks():
    """Lista tarefas do swarm"""
    try:
        # Por padrão, retorna apenas tarefas ativas
        active_only = request.args.get('active', 'true').lower() == 'true'
        
        if active_only:
            tasks = swarm_tasks.get_active_tasks()
        else:
            # Retornar todas (implementação simplificada)
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
                SELECT t.id FROM swarm_tasks
                ORDER BY created_at DESC LIMIT 100
            """)
            rows = cur.fetchall()
            conn.close()
            tasks = [swarm_tasks.get_task(row['id']) for row in rows]
        
        return jsonify({
            "tasks": [t.to_dict() for t in tasks if t],
            "count": len(tasks)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/swarm/tasks', methods=['POST'])
def create_swarm_task():
    """Cria nova tarefa no swarm"""
    try:
        data = request.get_json()
        
        if not data or 'request' not in data:
            return jsonify({"error": "Campo 'request' é obrigatório"}), 400
        
        original_request = data['request']
        coordinator = data.get('coordinator', 'ralph')
        
        task = swarm_tasks.create_task(
            original_request=original_request,
            coordinator_agent_slug=coordinator
        )
        
        # Postar no canal orders
        swarm_channels.post(
            channel_name='orders',
            author_type=AuthorType.USER,
            author_id='api',
            content=original_request,
            mentions=[coordinator]
        )
        
        return jsonify({
            "success": True,
            "task": task.to_dict()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/swarm/tasks/<task_code>', methods=['GET'])
def get_swarm_task(task_code):
    """Retorna detalhes de uma tarefa"""
    try:
        task = swarm_tasks.get_task_by_code(task_code)
        
        if not task:
            return jsonify({"error": f"Task '{task_code}' não encontrada"}), 404
        
        return jsonify({"task": task.to_dict()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/swarm/dashboard', methods=['GET'])
def get_swarm_dashboard():
    """Retorna dados do dashboard"""
    try:
        # Resumo do dia
        today_summary = swarm_tasks.get_today_summary()
        
        # Agents ativos
        agents = swarm_agents.get_all_agents()
        
        # Canais com atividade
        channels = swarm_channels.get_channels()
        for ch in channels:
            ch['message_count'] = swarm_channels.get_message_count(ch['name'])
        
        # Tarefas ativas
        active_tasks = swarm_tasks.get_active_tasks()
        
        return jsonify({
            "today": today_summary,
            "agents": {
                "total": len(agents),
                "active": len([a for a in agents if a.status == 'idle']),
                "busy": len([a for a in agents if a.status == 'busy'])
            },
            "channels": sorted(channels, key=lambda x: x['message_count'], reverse=True)[:10],
            "active_tasks": len(active_tasks),
            "pending_tasks": len([t for t in active_tasks if t.status == 'pending'])
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/swarm/live-feed', methods=['GET'])
def get_swarm_live_feed():
    """Retorna feed de atividade ao vivo"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        # Pegar mensagens recentes dos canais principais
        feed = []
        
        for channel_name in ['orders', 'agent-chat', 'find-output', 'build-output', 'create-output']:
            messages = swarm_channels.read(channel_name, limit=5)
            for msg in messages:
                feed.append({
                    'time': msg.created_at.strftime('%H:%M') if msg.created_at else '--:--',
                    'channel': channel_name,
                    'agent': msg.author_id,
                    'action': msg.content[:100] + ('...' if len(msg.content) > 100 else '')
                })
        
        # Ordenar por hora (mais recente primeiro)
        feed.sort(key=lambda x: x['time'], reverse=True)
        
        return jsonify({
            "feed": feed[:limit],
            "count": len(feed[:limit])
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/swarm/agents/<agent_slug>/think', methods=['POST'])
def agent_think(agent_slug):
    """Faz um agent processar uma tarefa e retornar resposta"""
    try:
        from swarm.agent_brain import AgentBrain
        
        data = request.get_json()
        if not data or 'task' not in data:
            return jsonify({"error": "Campo 'task' é obrigatório"}), 400
        
        task = data['task']
        context_channel = data.get('context_channel')
        
        # Criar cérebro do agent
        brain = AgentBrain(agent_slug)
        
        # Executar tarefa
        result = brain.think(task, context_channel)
        
        # Postar no canal apropriado
        output_channels = {
            'ralph': 'agent-chat',
            'scout': 'find-output',
            'max': 'build-output',
            'maya': 'create-output',
            'tracker': 'track-output',
            'watcher': 'watch-output'
        }
        output_channel = output_channels.get(agent_slug, 'agent-chat')
        
        message = brain.post_to_channel(output_channel, result)
        
        return jsonify({
            "success": True,
            "agent": agent_slug,
            "result": result,
            "posted_to": output_channel,
            "message_id": message.id if message else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/swarm/agents/<agent_slug>/memory', methods=['GET', 'PUT'])
def agent_memory(agent_slug):
    """GET: Lê memória do agent | PUT: Atualiza memória"""
    try:
        from swarm.agent_brain import AgentBrain
        brain = AgentBrain(agent_slug)
        
        if request.method == 'GET':
            return jsonify({
                "agent": agent_slug,
                "memory": brain.memory
            })
        
        elif request.method == 'PUT':
            data = request.get_json()
            if not data:
                return jsonify({"error": "Dados obrigatórios"}), 400
            
            for key, value in data.items():
                brain.update_memory(key, value)
            
            return jsonify({
                "success": True,
                "agent": agent_slug,
                "memory": brain.memory
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/swarm/orchestrate', methods=['POST'])
def orchestrate_task():
    """
    Orquestra uma tarefa completa com múltiplos agents.
    Ralph analisa, delega e consolida.
    """
    try:
        from swarm.agent_brain import AgentBrain
        
        data = request.get_json()
        if not data or 'task' not in data:
            return jsonify({"error": "Campo 'task' é obrigatório"}), 400
        
        task_description = data['task']
        agents_to_spawn = data.get('agents', ['scout', 'max', 'maya'])
        
        # 1. Ralph cria plano
        ralph = AgentBrain('ralph')
        plan = ralph.think(
            task=f"Criar plano para: {task_description}",
            context_channel='orders'
        )
        
        ralph.post_to_channel('agent-chat', f"📋 Novo plano criado:\n{plan}")
        
        # 2. Criar task no sistema
        task = swarm_tasks.create_task(task_description, 'ralph')
        swarm_tasks.update_execution_plan(task.id, {
            'plan': plan,
            'agents': agents_to_spawn
        })
        
        # 3. Executar agents (simulação sequencial por enquanto)
        results = {}
        for agent_slug in agents_to_spawn:
            brain = AgentBrain(agent_slug)
            agent_task = f"Executar para: {task_description}"
            result = brain.think(agent_task)
            results[agent_slug] = result
            
            # Pequeno delay para simular processamento
            import time
            time.sleep(0.5)
        
        # 4. Ralph sintetiza
        synthesis_input = "\n\n".join([
            f"### {name}\n{content}" 
            for name, content in results.items()
        ])
        
        synthesis = ralph.think(
            task=f"Sintetizar resultados:\n{synthesis_input}",
            output_format="Crie uma entrega final consolidada e polida."
        )
        
        # Postar síntese
        ralph.post_to_channel('orders', synthesis, mentions=['Jeff'])
        
        # Finalizar task
        swarm_tasks.set_final_output(task.id, synthesis)
        
        return jsonify({
            "success": True,
            "task_code": task.task_code,
            "plan": plan,
            "results": results,
            "synthesis": synthesis
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/swarm/coordinate', methods=['POST'])
def coordinate_swarm_smart():
    """
    Coordenação inteligente do swarm.
    Ralph analisa a tarefa, decide a estratégia e executa.
    """
    try:
        from swarm.coordination_engine import SwarmCoordinator
        
        data = request.get_json()
        if not data or 'task' not in data:
            return jsonify({"error": "Campo 'task' é obrigatório"}), 400
        
        task_description = data['task']
        auto_execute = data.get('auto_execute', True)
        
        # Criar coordenador
        coordinator = SwarmCoordinator()
        
        # 1. Ralph analisa a tarefa
        plan = coordinator.analyze_task(task_description)
        
        # 2. Criar task no sistema
        task = swarm_tasks.create_task(task_description, 'ralph')
        swarm_tasks.update_execution_plan(task.id, plan.to_dict())
        
        if not auto_execute:
            # Apenas retornar o plano para aprovação
            return jsonify({
                "success": True,
                "task_code": task.task_code,
                "plan": plan.to_dict(),
                "message": "Plano criado. Use auto_execute=true para executar."
            })
        
        # 3. Executar o swarm
        result = coordinator.execute_swarm(task_description, plan, task.id)
        
        return jsonify({
            "success": True,
            "task_code": task.task_code,
            "plan": plan.to_dict(),
            "execution": result
        })
        
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route('/api/swarm/process-orders', methods=['POST'])
def process_swarm_orders():
    """
    Processa mensagens pendentes em #orders.
    Endpoint para execução contínua/background.
    """
    try:
        from swarm.coordination_engine import SwarmCoordinator
        
        coordinator = SwarmCoordinator()
        result = coordinator.process_orders()
        
        if result:
            return jsonify({
                "success": True,
                "processed": True,
                "result": result
            })
        else:
            return jsonify({
                "success": True,
                "processed": False,
                "message": "Nenhuma mensagem pendente em #orders"
            })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/swarm/costs', methods=['GET'])
def get_swarm_costs():
    """Retorna tracking de custos de LLM"""
    try:
        from swarm.llm_executor import CostTracker
        
        tracker = CostTracker()
        stats = tracker.get_stats()
        
        return jsonify({
            "costs": stats,
            "models": {
                "gemini-flash": "Barato - Research/Copy",
                "gemini-pro": "Médio - Análise complexa",
                "kimi-k2": "Caro - Decisões estratégicas",
                "claude-sonnet": "Médio - Código"
            },
            "agent_models": {
                "ralph": "kimi-k2",
                "scout": "gemini-flash",
                "max": "claude-sonnet",
                "maya": "gemini-flash",
                "tracker": "gemini-flash",
                "watcher": "gemini-flash"
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/swarm/synthesize', methods=['POST'])
def synthesize_results():
    """
    Síntese avançada de resultados.
    Consolida outputs de múltiplos agents em entrega final.
    """
    try:
        from swarm.synthesis_engine import SynthesisEngine, SynthesisConfig, SynthesisQuality, AgentOutput
        
        data = request.get_json()
        if not data or 'task' not in data or 'outputs' not in data:
            return jsonify({"error": "Campos 'task' e 'outputs' são obrigatórios"}), 400
        
        task = data['task']
        outputs_data = data['outputs']
        
        # Configuração opcional
        quality_str = data.get('quality', 'standard')
        quality = SynthesisQuality(quality_str)
        
        config = SynthesisConfig(
            quality=quality,
            max_length=data.get('max_length', 2000),
            include_action_items=data.get('include_actions', True),
            include_metrics=data.get('include_metrics', True),
            tone=data.get('tone', 'professional'),
            format=data.get('format', 'markdown')
        )
        
        # Converter outputs
        outputs = [
            AgentOutput(
                agent_slug=out['agent_slug'],
                agent_name=out.get('agent_name', out['agent_slug']),
                role=out.get('role', 'unknown'),
                content=out['content'],
                tokens_used=out.get('tokens', 0),
                confidence=out.get('confidence', 1.0)
            )
            for out in outputs_data
        ]
        
        # Executar síntese
        engine = SynthesisEngine()
        result = engine.synthesize(task, outputs, config)
        
        # Formatar para entrega
        format_type = data.get('format', 'markdown')
        formatted = engine.format_for_delivery(result, format_type)
        
        return jsonify({
            "success": True,
            "result": result.to_dict(),
            "formatted": formatted,
            "format": format_type
        })
        
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


# Serve Ralph Swarm Dashboard
@app.route('/swarm')
def serve_swarm_dashboard():
    """Serve o dashboard do Ralph Swarm"""
    dashboard_path = Path(__file__).parent / 'swarm' / 'dashboard.html'
    if dashboard_path.exists():
        return send_file(dashboard_path)
    else:
        return jsonify({"error": "Dashboard not found"}), 404

@app.route('/swarm/dashboard')
def serve_swarm_dashboard_alt():
    """Serve o dashboard do Ralph Swarm (alt route)"""
    return serve_swarm_dashboard()


# Ralph Swarm Always On endpoints
always_on_manager = None

@app.route('/api/swarm/always-on/status', methods=['GET'])
def get_always_on_status():
    """Retorna status do sistema Always On"""
    try:
        from swarm.always_on import AlwaysOnManager
        
        global always_on_manager
        if always_on_manager is None:
            always_on_manager = AlwaysOnManager()
        
        status = always_on_manager.get_status()
        
        return jsonify({
            "success": True,
            "status": status
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/swarm/always-on/start', methods=['POST'])
def start_always_on():
    """Inicia o sistema Always On"""
    try:
        from swarm.always_on import AlwaysOnManager
        
        global always_on_manager
        if always_on_manager is None:
            always_on_manager = AlwaysOnManager()
        
        if always_on_manager.running:
            return jsonify({
                "success": True,
                "message": "Always On já está rodando",
                "running": True
            })
        
        always_on_manager.start()
        
        return jsonify({
            "success": True,
            "message": "Always On iniciado com sucesso",
            "running": True
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/swarm/always-on/stop', methods=['POST'])
def stop_always_on():
    """Para o sistema Always On"""
    try:
        global always_on_manager
        if always_on_manager is None or not always_on_manager.running:
            return jsonify({
                "success": True,
                "message": "Always On não está rodando",
                "running": False
            })
        
        always_on_manager.stop()
        
        return jsonify({
            "success": True,
            "message": "Always On parado",
            "running": False
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/swarm/always-on/trigger', methods=['POST'])
def trigger_always_on_job():
    """Dispara um job manualmente"""
    try:
        from swarm.always_on import AlwaysOnManager
        
        data = request.get_json()
        job_type = data.get('job_type', 'heartbeat')
        
        global always_on_manager
        if always_on_manager is None:
            always_on_manager = AlwaysOnManager()
        
        always_on_manager.trigger_now(job_type)
        
        return jsonify({
            "success": True,
            "message": f"Job {job_type} disparado"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv("DM_API_PORT", str(DEFAULT_API_PORT)))
    print(f"🚀 Dunder Mifflin API (Flask) rodando em http://localhost:{port}")
    print(f"📊 Ralph Swarm Dashboard: http://localhost:{port}/swarm")
    app.run(host='0.0.0.0', port=port, debug=False)
