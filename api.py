#!/usr/bin/env python3
"""
Dunder Mifflin API REST - SQLite Edition
Serve dados do banco local via HTTP
"""

import os
import sys
import json
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

DB_PATH = Path(__file__).parent / "dunder_mifflin.db"
PORT = int(os.getenv("DM_API_PORT", "3003"))

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class APIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silencia logs de requisição
        pass
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def do_options(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_get(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        try:
            if path == "/api/agents":
                self.get_agents()
            elif path.startswith("/api/agents/"):
                slug = path.split("/")[-1]
                self.get_agent_by_slug(slug)
            elif path == "/api/missions":
                status = query.get("status", [None])[0]
                self.get_missions(status)
            elif path.startswith("/api/missions/"):
                mission_id = path.split("/")[-1]
                self.get_mission(mission_id)
            elif path == "/api/proposals":
                status = query.get("status", [None])[0]
                self.get_proposals(status)
            elif path == "/api/events":
                limit = int(query.get("limit", ["50"])[0])
                self.get_events(limit)
            elif path == "/api/stats":
                self.get_stats()
            elif path == "/api/health":
                self.send_json({"status": "ok", "service": "dunder-mifflin-api"})
            else:
                self.send_json({"error": "Not found"}, 404)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)
    
    def do_post(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else "{}"
        
        try:
            data = json.loads(body) if body else {}
        except:
            data = {}
        
        try:
            if path == "/api/proposals":
                self.create_proposal(data)
            elif path.startswith("/api/proposals/") and path.endswith("/approve"):
                proposal_id = path.split("/")[-2]
                self.approve_proposal(proposal_id, data)
            elif path.startswith("/api/missions/") and path.endswith("/start"):
                mission_id = path.split("/")[-2]
                self.start_mission(mission_id)
            elif path.startswith("/api/missions/") and path.endswith("/complete"):
                mission_id = path.split("/")[-2]
                self.complete_mission(mission_id, data)
            else:
                self.send_json({"error": "Not found"}, 404)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)
    
    def get_agents(self):
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM agents ORDER BY priority DESC")
        rows = [dict(row) for row in cur.fetchall()]
        conn.close()
        self.send_json({"agents": rows})
    
    def get_agent_by_slug(self, slug):
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM agents WHERE slug = ?", (slug,))
        row = cur.fetchone()
        conn.close()
        if row:
            self.send_json({"agent": dict(row)})
        else:
            self.send_json({"error": "Agent not found"}, 404)
    
    def get_missions(self, status=None):
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
        self.send_json({"missions": rows})
    
    def get_mission(self, mission_id):
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
            self.send_json({"mission": dict(row)})
        else:
            self.send_json({"error": "Mission not found"}, 404)
    
    def get_proposals(self, status=None):
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
        self.send_json({"proposals": rows})
    
    def get_events(self, limit=50):
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
        self.send_json({"events": rows})
    
    def get_stats(self):
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
        self.send_json(stats)
    
    def create_proposal(self, data):
        agent_id = data.get("agentId")
        title = data.get("title")
        description = data.get("description", "")
        mission_type = data.get("missionType", "general")
        priority = data.get("priority", 5)
        
        if not agent_id or not title:
            self.send_json({"error": "agentId and title required"}, 400)
            return
        
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
        
        self.send_json({"id": proposal_id, "code": code, "status": "created"})
    
    def approve_proposal(self, proposal_id, data):
        notes = data.get("notes", "")
        
        conn = get_db()
        cur = conn.cursor()
        
        # Busca proposta
        cur.execute("SELECT * FROM proposals WHERE id = ?", (proposal_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            self.send_json({"error": "Proposal not found"}, 404)
            return
        
        proposal = dict(row)
        
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
        
        self.send_json({"missionId": mission_id, "code": mission_code, "status": "created"})
    
    def start_mission(self, mission_id):
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE missions SET status = 'running', started_at = ? WHERE id = ?
        """, (datetime.now().isoformat(), mission_id))
        conn.commit()
        conn.close()
        
        self.send_json({"id": mission_id, "status": "running"})
    
    def complete_mission(self, mission_id, data):
        status = data.get("status", "succeeded")
        result = data.get("result", {})
        error_message = data.get("errorMessage")
        
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE missions 
            SET status = ?, completed_at = ?, result = ?, error_message = ?
            WHERE id = ?
        """, (status, datetime.now().isoformat(), json.dumps(result), error_message, mission_id))
        conn.commit()
        conn.close()
        
        self.send_json({"id": mission_id, "status": status})

def run_server():
    server = HTTPServer(("0.0.0.0", PORT), APIHandler)
    print(f"🚀 Dunder Mifflin API rodando em http://localhost:{PORT}")
    print(f"📊 Endpoints disponíveis:")
    print(f"   GET  /api/agents")
    print(f"   GET  /api/missions")
    print(f"   GET  /api/proposals")
    print(f"   GET  /api/events")
    print(f"   GET  /api/stats")
    print(f"   GET  /api/health")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 API parada")
        server.shutdown()

if __name__ == "__main__":
    run_server()
