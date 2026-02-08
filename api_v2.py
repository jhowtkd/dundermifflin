#!/usr/bin/env python3
"""
Dunder Mifflin V2 API - Sistema de Squads, Serviços e Orquestração
API REST para gerenciamento de agentes em grupos com mestres orquestradores
"""

import os
import json
import sqlite3
import time
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__, static_folder='frontend/v2', static_url_path='')
CORS(app)

DB_PATH = Path(__file__).parent / "dunder_mifflin.db"

# ============================================================
# UTILS
# ============================================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def generate_code(prefix):
    import uuid
    return f"{prefix}-{uuid.uuid4().hex[:12]}"

# ============================================================
# HEALTH
# ============================================================

@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "service": "dunder-mifflin-v2", "version": "2.0.0"})


# ============================================================
# SQUADS
# ============================================================

@app.route('/api/v2/squads', methods=['GET'])
def get_squads():
    """Lista todos os squads com seus mestres e membros"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT s.*, a.name as master_name, a.avatar_emoji as master_emoji,
               a.slug as master_slug, a.role as master_role
        FROM squads s
        JOIN agents a ON s.master_agent_id = a.id
        WHERE s.is_active = 1
        ORDER BY s.name
    """)
    
    squads = []
    for row in cur.fetchall():
        squad = dict(row)
        
        # Busca membros do squad
        cur.execute("""
            SELECT sm.*, a.name, a.slug, a.avatar_emoji, a.role, a.description
            FROM squad_members sm
            JOIN agents a ON sm.agent_id = a.id
            WHERE sm.squad_id = ?
            ORDER BY sm.order_index, a.name
        """, (squad['id'],))
        
        squad['members'] = [dict(m) for m in cur.fetchall()]
        squads.append(squad)
    
    conn.close()
    return jsonify({"squads": squads})


@app.route('/api/v2/squads/<slug>', methods=['GET'])
def get_squad(slug):
    """Busca um squad específico com detalhes"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT s.*, a.name as master_name, a.avatar_emoji as master_emoji,
               a.slug as master_slug, a.role as master_role, a.description as master_description
        FROM squads s
        JOIN agents a ON s.master_agent_id = a.id
        WHERE s.slug = ? AND s.is_active = 1
    """, (slug,))
    
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Squad not found"}), 404
    
    squad = dict(row)
    
    # Busca membros
    cur.execute("""
        SELECT sm.*, a.id as agent_id, a.name, a.slug, a.avatar_emoji, a.role, 
               a.description, a.capabilities
        FROM squad_members sm
        JOIN agents a ON sm.agent_id = a.id
        WHERE sm.squad_id = ?
        ORDER BY sm.order_index, a.name
    """, (squad['id'],))
    
    squad['members'] = [dict(m) for m in cur.fetchall()]
    
    # Busca serviços do squad
    cur.execute("""
        SELECT id, slug, name, emoji, description, is_active
        FROM services
        WHERE squad_id = ? AND is_active = 1
        ORDER BY name
    """, (squad['id'],))
    
    squad['services'] = [dict(s) for s in cur.fetchall()]
    
    conn.close()
    return jsonify({"squad": squad})


@app.route('/api/v2/squads', methods=['POST'])
def create_squad():
    """Cria um novo squad"""
    data = request.get_json() or {}
    
    slug = data.get('slug')
    name = data.get('name')
    description = data.get('description', '')
    master_agent_id = data.get('master_agent_id')
    emoji = data.get('emoji', '👥')
    color = data.get('color', '#3B82F6')
    capabilities = json.dumps(data.get('capabilities', []))
    
    if not all([slug, name, master_agent_id]):
        return jsonify({"error": "slug, name and master_agent_id required"}), 400
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO squads (slug, name, description, emoji, color, master_agent_id, capabilities)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (slug, name, description, emoji, color, master_agent_id, capabilities))
        
        squad_id = cur.lastrowid
        
        # Adiciona membros se fornecidos
        members = data.get('members', [])
        for idx, member in enumerate(members):
            cur.execute("""
                INSERT INTO squad_members (squad_id, agent_id, role_in_squad, order_index, can_loop)
                VALUES (?, ?, ?, ?, ?)
            """, (squad_id, member['agent_id'], member.get('role', 'member'), 
                  idx, member.get('can_loop', 0)))
        
        conn.commit()
        conn.close()
        
        return jsonify({"id": squad_id, "slug": slug, "status": "created"}), 201
        
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({"error": f"Squad with this slug already exists: {e}"}), 409


# ============================================================
# SERVIÇOS
# ============================================================

@app.route('/api/v2/services', methods=['GET'])
def get_services():
    """Lista todos os serviços disponíveis"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT s.*, sq.name as squad_name, sq.emoji as squad_emoji
        FROM services s
        LEFT JOIN squads sq ON s.squad_id = sq.id
        WHERE s.is_active = 1
        ORDER BY s.name
    """)
    
    services = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({"services": services})


@app.route('/api/v2/services/<slug>', methods=['GET'])
def get_service(slug):
    """Busca um serviço com seu fluxo completo"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT s.*, sq.name as squad_name, sq.emoji as squad_emoji, 
               sq.master_agent_id, a.name as master_name
        FROM services s
        LEFT JOIN squads sq ON s.squad_id = sq.id
        LEFT JOIN agents a ON sq.master_agent_id = a.id
        WHERE s.slug = ? AND s.is_active = 1
    """, (slug,))
    
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Service not found"}), 404
    
    service = dict(row)
    
    # Busca steps do serviço
    cur.execute("""
        SELECT ss.*, a.name as agent_name, a.slug as agent_slug, 
               a.avatar_emoji, a.role
        FROM service_steps ss
        JOIN agents a ON ss.agent_id = a.id
        WHERE ss.service_id = ?
        ORDER BY ss.step_number
    """, (service['id'],))
    
    service['steps'] = [dict(s) for s in cur.fetchall()]
    
    conn.close()
    return jsonify({"service": service})


@app.route('/api/v2/services', methods=['POST'])
def create_service():
    """Cria um novo serviço com seu fluxo"""
    data = request.get_json() or {}
    
    slug = data.get('slug')
    name = data.get('name')
    description = data.get('description', '')
    squad_id = data.get('squad_id')
    emoji = data.get('emoji', '⚙️')
    input_schema = json.dumps(data.get('input_schema', {}))
    output_schema = json.dumps(data.get('output_schema', {}))
    
    if not all([slug, name]):
        return jsonify({"error": "slug and name required"}), 400
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO services (slug, name, description, squad_id, emoji, input_schema, output_schema)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (slug, name, description, squad_id, emoji, input_schema, output_schema))
        
        service_id = cur.lastrowid
        
        # Cria os steps
        steps = data.get('steps', [])
        for idx, step in enumerate(steps, 1):
            cur.execute("""
                INSERT INTO service_steps 
                (service_id, step_number, agent_id, title, description, instructions,
                 is_loop_enabled, loop_condition, max_loops, on_failure)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (service_id, idx, step['agent_id'], step['title'], 
                  step.get('description', ''), step.get('instructions', ''),
                  step.get('is_loop_enabled', 0), step.get('loop_condition', ''),
                  step.get('max_loops', 1), step.get('on_failure', 'stop')))
        
        conn.commit()
        conn.close()
        
        return jsonify({"id": service_id, "slug": slug, "status": "created"}), 201
        
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Service with this slug already exists"}), 409


@app.route('/api/v2/services/<slug>/steps', methods=['POST'])
def add_service_step(slug):
    """Adiciona um step a um serviço existente"""
    data = request.get_json() or {}
    
    conn = get_db()
    cur = conn.cursor()
    
    # Busca o serviço
    cur.execute("SELECT id FROM services WHERE slug = ?", (slug,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Service not found"}), 404
    
    service_id = row[0]
    
    # Busca o maior step_number atual
    cur.execute("SELECT MAX(step_number) FROM service_steps WHERE service_id = ?", (service_id,))
    max_step = cur.fetchone()[0] or 0
    
    cur.execute("""
        INSERT INTO service_steps 
        (service_id, step_number, agent_id, title, description, instructions,
         is_loop_enabled, loop_condition, max_loops, on_failure)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (service_id, max_step + 1, data['agent_id'], data['title'],
          data.get('description', ''), data.get('instructions', ''),
          data.get('is_loop_enabled', 0), data.get('loop_condition', ''),
          data.get('max_loops', 1), data.get('on_failure', 'stop')))
    
    conn.commit()
    conn.close()
    
    return jsonify({"status": "step added"})


# ============================================================
# PLANOS
# ============================================================

@app.route('/api/v2/plans', methods=['GET'])
def get_plans():
    """Lista planos com filtro opcional por status"""
    status = request.args.get('status')
    
    conn = get_db()
    cur = conn.cursor()
    
    if status:
        cur.execute("""
            SELECT p.*, s.name as service_name, s.emoji as service_emoji,
                   sq.name as squad_name, a.name as master_name, a.avatar_emoji as master_emoji
            FROM plans p
            LEFT JOIN services s ON p.service_id = s.id
            LEFT JOIN squads sq ON p.squad_id = sq.id
            JOIN agents a ON p.master_agent_id = a.id
            WHERE p.status = ?
            ORDER BY p.created_at DESC
        """, (status,))
    else:
        cur.execute("""
            SELECT p.*, s.name as service_name, s.emoji as service_emoji,
                   sq.name as squad_name, a.name as master_name, a.avatar_emoji as master_emoji
            FROM plans p
            LEFT JOIN services s ON p.service_id = s.id
            LEFT JOIN squads sq ON p.squad_id = sq.id
            JOIN agents a ON p.master_agent_id = a.id
            ORDER BY p.created_at DESC
        """)
    
    plans = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({"plans": plans})


@app.route('/api/v2/plans/<plan_code>', methods=['GET'])
def get_plan(plan_code):
    """Busca um plano específico com detalhes completos"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT p.*, s.name as service_name, s.description as service_description,
               s.emoji as service_emoji, sq.name as squad_name, sq.emoji as squad_emoji,
               a.name as master_name, a.avatar_emoji as master_emoji, a.slug as master_slug
        FROM plans p
        LEFT JOIN services s ON p.service_id = s.id
        LEFT JOIN squads sq ON p.squad_id = sq.id
        JOIN agents a ON p.master_agent_id = a.id
        WHERE p.plan_code = ?
    """, (plan_code,))
    
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Plan not found"}), 404
    
    plan = dict(row)
    plan['planned_steps'] = json.loads(plan.get('planned_steps', '[]') or '[]')
    plan['input_data'] = json.loads(plan.get('input_data', '{}') or '{}')
    
    # Busca mensagens relacionadas
    cur.execute("""
        SELECT m.*, fa.name as from_name, fa.avatar_emoji as from_emoji,
               ta.name as to_name, ta.avatar_emoji as to_emoji
        FROM agent_messages m
        JOIN agents fa ON m.from_agent_id = fa.id
        LEFT JOIN agents ta ON m.to_agent_id = ta.id
        WHERE m.plan_id = ?
        ORDER BY m.created_at
    """, (plan['id'],))
    
    plan['messages'] = [dict(m) for m in cur.fetchall()]
    
    conn.close()
    return jsonify({"plan": plan})


@app.route('/api/v2/plans', methods=['POST'])
def create_plan():
    """
    Cria um novo plano. 
    Se service_id for fornecido, usa o fluxo do serviço.
    Senão, cria um plano genérico.
    """
    data = request.get_json() or {}
    
    title = data.get('title')
    description = data.get('description', '')
    service_id = data.get('service_id')
    squad_id = data.get('squad_id')
    master_agent_id = data.get('master_agent_id')
    input_data = json.dumps(data.get('input_data', {}))
    
    if not title:
        return jsonify({"error": "title required"}), 400
    
    conn = get_db()
    cur = conn.cursor()
    
    # Se tem service_id, busca o fluxo do serviço
    planned_steps = '[]'
    if service_id:
        cur.execute("""
            SELECT ss.*, a.name as agent_name, a.slug as agent_slug
            FROM service_steps ss
            JOIN agents a ON ss.agent_id = a.id
            WHERE ss.service_id = ?
            ORDER BY ss.step_number
        """, (service_id,))
        
        steps = [dict(s) for s in cur.fetchall()]
        for step in steps:
            step['input_mapping'] = json.loads(step.get('input_mapping', '{}') or '{}')
            step['output_mapping'] = json.loads(step.get('output_mapping', '{}') or '{}')
        
        planned_steps = json.dumps(steps)
        
        # Se não tem squad_id, pega do serviço
        if not squad_id:
            cur.execute("SELECT squad_id FROM services WHERE id = ?", (service_id,))
            row = cur.fetchone()
            if row:
                squad_id = row[0]
        
        # Se não tem master_agent_id, pega do squad
        if not master_agent_id and squad_id:
            cur.execute("SELECT master_agent_id FROM squads WHERE id = ?", (squad_id,))
            row = cur.fetchone()
            if row:
                master_agent_id = row[0]
    
    plan_code = generate_code('PLAN')
    
    cur.execute("""
        INSERT INTO plans (plan_code, title, description, service_id, squad_id, 
                          master_agent_id, input_data, planned_steps, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'draft')
    """, (plan_code, title, description, service_id, squad_id, 
          master_agent_id, input_data, planned_steps))
    
    plan_id = cur.lastrowid
    
    # Cria mensagem do master sobre o plano
    if master_agent_id:
        msg_code = generate_code('MSG')
        cur.execute("""
            INSERT INTO agent_messages (message_code, from_agent_id, plan_id, 
                                       message_type, content)
            VALUES (?, ?, ?, 'plan_created', ?)
        """, (msg_code, master_agent_id, plan_id, 
              f"📋 Plano criado: {title}\n\nAnalisando requisitos e preparando estratégia..."))
    
    conn.commit()
    conn.close()
    
    return jsonify({"id": plan_id, "plan_code": plan_code, "status": "draft"}), 201


@app.route('/api/v2/plans/<plan_code>/submit', methods=['POST'])
def submit_plan(plan_code):
    """Submete um plano para aprovação"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT id, status, master_agent_id FROM plans WHERE plan_code = ?", (plan_code,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Plan not found"}), 404
    
    plan_id, status, master_id = row
    
    if status != 'draft':
        conn.close()
        return jsonify({"error": f"Plan already {status}"}), 400
    
    cur.execute("""
        UPDATE plans SET status = 'pending_approval', submitted_at = ?
        WHERE id = ?
    """, (datetime.now().isoformat(), plan_id))
    
    # Mensagem do master
    msg_code = generate_code('MSG')
    cur.execute("""
        INSERT INTO agent_messages (message_code, from_agent_id, plan_id, 
                                   message_type, content)
        VALUES (?, ?, ?, 'plan_submitted', ?)
    """, (msg_code, master_id, plan_id, 
          "🚀 Plano submetido para aprovação!\n\nAguardando sua revisão..."))
    
    conn.commit()
    conn.close()
    
    return jsonify({"plan_code": plan_code, "status": "pending_approval"})


@app.route('/api/v2/plans/<plan_code>/approve', methods=['POST'])
def approve_plan(plan_code):
    """Aprova um plano e inicia execução"""
    data = request.get_json() or {}
    notes = data.get('notes', '')
    
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT p.*, s.id as service_id, s.name as service_name
        FROM plans p
        LEFT JOIN services s ON p.service_id = s.id
        WHERE p.plan_code = ?
    """, (plan_code,))
    
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Plan not found"}), 404
    
    plan = dict(row)
    
    if plan['status'] not in ['draft', 'pending_approval']:
        conn.close()
        return jsonify({"error": f"Plan cannot be approved (status: {plan['status']})"}), 400
    
    now = datetime.now().isoformat()
    
    cur.execute("""
        UPDATE plans SET status = 'approved', approved_at = ?, approval_notes = ?
        WHERE id = ?
    """, (now, notes, plan['id']))
    
    # Cria execução
    execution_code = generate_code('EXEC')
    planned_steps = json.loads(plan.get('planned_steps', '[]') or '[]')
    
    cur.execute("""
        INSERT INTO service_executions 
        (execution_code, service_id, plan_id, title, input_data, status, total_steps, started_at)
        VALUES (?, ?, ?, ?, ?, 'running', ?, ?)
    """, (execution_code, plan['service_id'], plan['id'], plan['title'],
          plan['input_data'], len(planned_steps), now))
    
    execution_id = cur.lastrowid
    
    # Cria execution_steps
    for idx, step in enumerate(planned_steps, 1):
        cur.execute("""
            INSERT INTO execution_steps 
            (execution_id, service_step_id, step_number, agent_id, title, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        """, (execution_id, step.get('id', 0), idx, step.get('agent_id'), step.get('title', f'Step {idx}')))
    
    # Mensagem do master
    msg_code = generate_code('MSG')
    cur.execute("""
        INSERT INTO agent_messages (message_code, from_agent_id, execution_id, 
                                   message_type, content)
        VALUES (?, ?, ?, 'execution_started', ?)
    """, (msg_code, plan['master_agent_id'], execution_id, 
          f"✅ Plano aprovado!\n\nIniciando execução com {len(planned_steps)} passos..."))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        "plan_code": plan_code, 
        "status": "approved", 
        "execution_code": execution_code
    })


@app.route('/api/v2/plans/<plan_code>/reject', methods=['POST'])
def reject_plan(plan_code):
    """Rejeita um plano"""
    data = request.get_json() or {}
    reason = data.get('reason', '')
    
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT id, status, master_agent_id FROM plans WHERE plan_code = ?", (plan_code,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Plan not found"}), 404
    
    plan_id, status, master_id = row
    
    cur.execute("""
        UPDATE plans SET status = 'rejected', approval_notes = ?
        WHERE id = ?
    """, (reason, plan_id))
    
    # Mensagem do master
    msg_code = generate_code('MSG')
    cur.execute("""
        INSERT INTO agent_messages (message_code, from_agent_id, plan_id, 
                                   message_type, content)
        VALUES (?, ?, ?, 'plan_rejected', ?)
    """, (msg_code, master_id, plan_id, 
          f"❌ Plano rejeitado.\n\nMotivo: {reason}\n\nVou revisar e propor alternativas..."))
    
    conn.commit()
    conn.close()
    
    return jsonify({"plan_code": plan_code, "status": "rejected"})


# ============================================================
# EXECUÇÕES
# ============================================================

@app.route('/api/v2/executions', methods=['GET'])
def get_executions():
    """Lista execuções ativas e recentes"""
    status = request.args.get('status')
    
    conn = get_db()
    cur = conn.cursor()
    
    if status:
        cur.execute("""
            SELECT e.*, s.name as service_name, p.plan_code
            FROM service_executions e
            LEFT JOIN services s ON e.service_id = s.id
            LEFT JOIN plans p ON e.plan_id = p.id
            WHERE e.status = ?
            ORDER BY e.created_at DESC
        """, (status,))
    else:
        cur.execute("""
            SELECT e.*, s.name as service_name, p.plan_code
            FROM service_executions e
            LEFT JOIN services s ON e.service_id = s.id
            LEFT JOIN plans p ON e.plan_id = p.id
            ORDER BY e.created_at DESC
            LIMIT 50
        """)
    
    executions = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({"executions": executions})


@app.route('/api/v2/executions/<execution_code>', methods=['GET'])
def get_execution(execution_code):
    """Busca execução com steps e mensagens"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT e.*, s.name as service_name, s.emoji as service_emoji,
               p.plan_code, p.title as plan_title
        FROM service_executions e
        LEFT JOIN services s ON e.service_id = s.id
        LEFT JOIN plans p ON e.plan_id = p.id
        WHERE e.execution_code = ?
    """, (execution_code,))
    
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Execution not found"}), 404
    
    execution = dict(row)
    execution['input_data'] = json.loads(execution.get('input_data', '{}') or '{}')
    execution['output_data'] = json.loads(execution.get('output_data', '{}') or '{}')
    
    # Busca steps
    cur.execute("""
        SELECT es.*, a.name as agent_name, a.slug as agent_slug, a.avatar_emoji
        FROM execution_steps es
        JOIN agents a ON es.agent_id = a.id
        WHERE es.execution_id = ?
        ORDER BY es.step_number
    """, (execution['id'],))
    
    execution['steps'] = [dict(s) for s in cur.fetchall()]
    
    # Busca mensagens
    cur.execute("""
        SELECT m.*, fa.name as from_name, fa.avatar_emoji as from_emoji,
               ta.name as to_name, ta.avatar_emoji as to_emoji
        FROM agent_messages m
        JOIN agents fa ON m.from_agent_id = fa.id
        LEFT JOIN agents ta ON m.to_agent_id = ta.id
        WHERE m.execution_id = ?
        ORDER BY m.created_at
    """, (execution['id'],))
    
    execution['messages'] = [dict(m) for m in cur.fetchall()]
    
    conn.close()
    return jsonify({"execution": execution})


@app.route('/api/v2/executions/<execution_code>/next', methods=['POST'])
def execute_next_step(execution_code):
    """Executa o próximo step de uma execução (simulação)"""
    data = request.get_json() or {}
    result = data.get('result', {})
    
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT id, current_step, total_steps, status FROM service_executions WHERE execution_code = ?", 
                (execution_code,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Execution not found"}), 404
    
    exec_id, current_step, total_steps, status = row
    
    if status != 'running':
        conn.close()
        return jsonify({"error": f"Execution is {status}"}), 400
    
    next_step = current_step + 1
    now = datetime.now().isoformat()
    
    if next_step > total_steps:
        # Finaliza execução
        cur.execute("""
            UPDATE service_executions 
            SET status = 'succeeded', completed_at = ?, output_data = ?
            WHERE id = ?
        """, (now, json.dumps(result), exec_id))
        
        # Atualiza plano
        cur.execute("""
            UPDATE plans SET status = 'completed', completed_at = ?, result = ?
            WHERE id = (SELECT plan_id FROM service_executions WHERE id = ?)
        """, (now, json.dumps(result), exec_id))
        
        status = 'succeeded'
    else:
        # Avança para próximo step
        cur.execute("""
            UPDATE service_executions SET current_step = ?
            WHERE id = ?
        """, (next_step, exec_id))
        
        # Atualiza step atual
        cur.execute("""
            UPDATE execution_steps 
            SET status = 'succeeded', output_data = ?, completed_at = ?
            WHERE execution_id = ? AND step_number = ?
        """, (json.dumps(result), now, exec_id, current_step))
        
        # Inicia próximo step
        cur.execute("""
            UPDATE execution_steps 
            SET status = 'running', started_at = ?
            WHERE execution_id = ? AND step_number = ?
        """, (now, exec_id, next_step))
        
        status = 'running'
    
    conn.commit()
    conn.close()
    
    return jsonify({"execution_code": execution_code, "status": status, "current_step": next_step})


# ============================================================
# MENSAGENS ENTRE AGENTES
# ============================================================

@app.route('/api/v2/messages', methods=['GET'])
def get_messages():
    """Lista mensagens com filtros opcionais"""
    squad_id = request.args.get('squad_id')
    execution_id = request.args.get('execution_id')
    plan_id = request.args.get('plan_id')
    
    conn = get_db()
    cur = conn.cursor()
    
    query = """
        SELECT m.*, fa.name as from_name, fa.avatar_emoji as from_emoji,
               ta.name as to_name, ta.avatar_emoji as to_emoji
        FROM agent_messages m
        JOIN agents fa ON m.from_agent_id = fa.id
        LEFT JOIN agents ta ON m.to_agent_id = ta.id
        WHERE 1=1
    """
    params = []
    
    if squad_id:
        query += " AND m.squad_id = ?"
        params.append(squad_id)
    if execution_id:
        query += " AND m.execution_id = ?"
        params.append(execution_id)
    if plan_id:
        query += " AND m.plan_id = ?"
        params.append(plan_id)
    
    query += " ORDER BY m.created_at"
    
    cur.execute(query, params)
    messages = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    return jsonify({"messages": messages})


@app.route('/api/v2/messages', methods=['POST'])
def create_message():
    """Cria uma mensagem entre agentes"""
    data = request.get_json() or {}
    
    from_agent_id = data.get('from_agent_id')
    to_agent_id = data.get('to_agent_id')
    squad_id = data.get('squad_id')
    execution_id = data.get('execution_id')
    plan_id = data.get('plan_id')
    message_type = data.get('message_type', 'text')
    content = data.get('content')
    context = json.dumps(data.get('context', {}))
    parent_id = data.get('parent_message_id')
    
    if not from_agent_id or not content:
        return jsonify({"error": "from_agent_id and content required"}), 400
    
    msg_code = generate_code('MSG')
    
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO agent_messages 
        (message_code, from_agent_id, to_agent_id, squad_id, execution_id, plan_id,
         message_type, content, context, parent_message_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (msg_code, from_agent_id, to_agent_id, squad_id, execution_id, plan_id,
          message_type, content, context, parent_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({"message_code": msg_code, "status": "created"}), 201


# ============================================================
# AGENTES (compatibilidade)
# ============================================================

@app.route('/api/v2/agents', methods=['GET'])
def get_agents():
    """Lista agentes disponíveis para formar squads"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT a.id, a.slug, a.name, a.role, a.avatar_emoji, a.description,
               a.department, d.name as department_name
        FROM agents a
        LEFT JOIN departments d ON a.department = d.slug
        WHERE a.is_active = 1
        ORDER BY a.department, a.name
    """)
    
    agents = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({"agents": agents})


@app.route('/api/v2/agents/<slug>', methods=['GET'])
def get_agent(slug):
    """Busca um agente específico"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT a.*, d.name as department_name
        FROM agents a
        LEFT JOIN departments d ON a.department = d.slug
        WHERE a.slug = ?
    """, (slug,))
    
    row = cur.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"error": "Agent not found"}), 404
    
    return jsonify({"agent": dict(row)})


# ============================================================
# ROTAS DO FRONTEND
# ============================================================

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    file_path = Path(app.static_folder) / path
    if file_path.exists() and file_path.is_file():
        return send_from_directory(app.static_folder, path)
    
    if '.' not in path:
        html_path = Path(app.static_folder) / f"{path}.html"
        if html_path.exists():
            return send_from_directory(app.static_folder, f"{path}.html")
    
    return send_from_directory(app.static_folder, 'index.html')


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    port = int(os.getenv("DM_API_PORT", "3003"))
    print(f"🚀 Dunder Mifflin V2 API rodando em http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
