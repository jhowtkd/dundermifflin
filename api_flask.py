#!/usr/bin/env python3
"""
Dunder Mifflin API REST - Flask Edition
"""

import os
import json
import sqlite3
from pathlib import Path
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime
import time
import mimetypes

app = Flask(__name__)
CORS(app)

DB_PATH = Path(__file__).parent / "dunder_mifflin.db"
FILES_BASE = Path.home() / ".openclaw" / "workspace" / "studio" / "projects" / "dunder_mifflin"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "service": "dunder-mifflin-api"})

@app.route('/api/agents')
def get_agents():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM agents ORDER BY priority DESC")
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({"agents": rows})

@app.route('/api/agents/<slug>')
def get_agent(slug):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM agents WHERE slug = ?", (slug,))
    row = cur.fetchone()
    conn.close()
    if row:
        return jsonify({"agent": dict(row)})
    return jsonify({"error": "Agent not found"}), 404

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

@app.route('/api/stats')
def get_stats():
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
    
    cur.execute("SELECT COUNT(*) FROM proposals WHERE status = 'pending'")
    stats["pendingProposals"] = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM events WHERE occurred_at > datetime('now', '-24 hours')")
    stats["events24h"] = cur.fetchone()[0]
    
    conn.close()
    return jsonify(stats)

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

if __name__ == '__main__':
    port = int(os.getenv("DM_API_PORT", "3003"))
    print(f"🚀 Dunder Mifflin API (Flask) rodando em http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
