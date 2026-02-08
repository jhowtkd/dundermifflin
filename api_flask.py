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
    
    if not name or not slug:
        return jsonify({"error": "name and slug required"}), 400
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO services 
            (service_code, name, slug, description, icon_emoji, agent_sequence, loop_config)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (service_code, name, slug, description, icon_emoji, agent_sequence, loop_config))
        
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


if __name__ == '__main__':
    port = int(os.getenv("DM_API_PORT", str(DEFAULT_API_PORT)))
    print(f"🚀 Dunder Mifflin API (Flask) rodando em http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
