#!/usr/bin/env python3
"""
Script de migração do banco Dunder Mifflin
Migra da versão antiga para o novo schema com Jules Agents
"""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "dunder_mifflin.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Backup dos dados antigos
    print("📦 Fazendo backup dos dados...")
    cur.execute("SELECT * FROM agents")
    old_agents = cur.fetchall()
    cur.execute("PRAGMA table_info(agents)")
    old_columns = [col[1] for col in cur.fetchall()]
    
    cur.execute("SELECT * FROM missions")
    old_missions = cur.fetchall()
    
    cur.execute("SELECT * FROM proposals")
    old_proposals = cur.fetchall()
    
    print(f"   {len(old_agents)} agentes, {len(old_missions)} missões, {len(old_proposals)} propostas")
    
    # Dropar tabelas antigas
    print("🗑️  Removendo tabelas antigas...")
    tables = ['memories', 'events', 'steps', 'missions', 'proposals', 'agents', 'personas', 'commands', 'departments']
    for table in tables:
        cur.execute(f"DROP TABLE IF EXISTS {table}")
    
    # Criar novo schema
    print("🏗️  Criando novo schema...")
    schema_sql = '''
-- Departments
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    emoji TEXT NOT NULL DEFAULT '📁',
    description TEXT,
    agent_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Agents
CREATE TABLE IF NOT EXISTS agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    department TEXT NOT NULL DEFAULT 'general',
    role TEXT,
    description TEXT,
    capabilities TEXT,
    avatar_emoji TEXT DEFAULT '🤖',
    file_path TEXT,
    is_active BOOLEAN DEFAULT 1,
    priority INTEGER DEFAULT 5,
    daily_quota INTEGER DEFAULT 10,
    quota_used INTEGER DEFAULT 0,
    missions_completed INTEGER DEFAULT 0,
    last_active_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department) REFERENCES departments(slug)
);

-- Personas
CREATE TABLE IF NOT EXISTS personas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    avatar_emoji TEXT NOT NULL,
    agent_id INTEGER,
    catch_phrase TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);

-- Commands
CREATE TABLE IF NOT EXISTS commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    command_type TEXT DEFAULT 'simple',
    agents TEXT,
    parameters TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Proposals
CREATE TABLE IF NOT EXISTS proposals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proposal_code TEXT UNIQUE NOT NULL,
    agent_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    mission_type TEXT DEFAULT 'general',
    priority INTEGER DEFAULT 5,
    parameters TEXT,
    status TEXT DEFAULT 'pending',
    proposed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reviewed_at DATETIME,
    reviewed_by TEXT,
    review_notes TEXT,
    auto_approved BOOLEAN DEFAULT 0,
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);

-- Missions
CREATE TABLE IF NOT EXISTS missions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_code TEXT UNIQUE NOT NULL,
    proposal_id INTEGER,
    agent_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    mission_type TEXT DEFAULT 'general',
    priority INTEGER DEFAULT 5,
    status TEXT DEFAULT 'approved',
    started_at DATETIME,
    completed_at DATETIME,
    result TEXT,
    error_message TEXT,
    parent_mission_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (proposal_id) REFERENCES proposals(id),
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);

-- Steps
CREATE TABLE IF NOT EXISTS steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,
    step_number INTEGER NOT NULL,
    step_code TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    action_type TEXT,
    action_config TEXT,
    status TEXT DEFAULT 'queued',
    started_at DATETIME,
    completed_at DATETIME,
    input_data TEXT,
    output_data TEXT,
    error_details TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    FOREIGN KEY (mission_id) REFERENCES missions(id)
);

-- Events
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_code TEXT UNIQUE NOT NULL,
    event_type TEXT NOT NULL,
    severity TEXT DEFAULT 'info',
    agent_id INTEGER,
    mission_id INTEGER,
    step_id INTEGER,
    proposal_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    payload TEXT,
    occurred_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id),
    FOREIGN KEY (mission_id) REFERENCES missions(id)
);

-- Memories
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_code TEXT UNIQUE NOT NULL,
    agent_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    memory_type TEXT DEFAULT 'short_term',
    context TEXT,
    tags TEXT,
    importance INTEGER DEFAULT 5,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_missions_status ON missions(status);
CREATE INDEX IF NOT EXISTS idx_missions_agent ON missions(agent_id);
CREATE INDEX IF NOT EXISTS idx_proposals_status ON proposals(status);
CREATE INDEX IF NOT EXISTS idx_steps_mission ON steps(mission_id);
CREATE INDEX IF NOT EXISTS idx_events_occurred ON events(occurred_at);

-- Seed Departments
INSERT OR IGNORE INTO departments (slug, name, emoji, description) VALUES
    ('autonomous', 'Autônomos', '🤖', 'Agentes de qualidade de código'),
    ('development', 'Desenvolvimento', '💻', 'Construção de features'),
    ('design', 'Design', '🎨', 'Visual e UX'),
    ('marketing', 'Marketing', '📢', 'Growth e conteúdo'),
    ('product', 'Produto', '📦', 'Pesquisa e priorização'),
    ('project-management', 'Gestão', '📋', 'Coordenação'),
    ('studio-operations', 'Operações', '⚙️', 'Analytics e finanças'),
    ('testing', 'Testes', '🧪', 'QA e qualidade'),
    ('bonus', 'Bonus', '🎁', 'Especiais');
'''
    
    cur.executescript(schema_sql)
    
    # Inserir agentes antigos
    print("🤖 Migrando agentes existentes...")
    agent_map = {}
    for agent in old_agents:
        # Mapeia colunas antigas
        agent_dict = dict(zip(old_columns, agent))
        
        cur.execute('''
            INSERT INTO agents (slug, name, department, role, description, capabilities, 
                              avatar_emoji, is_active, priority, daily_quota, quota_used)
            VALUES (?, ?, 'general', ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            agent_dict.get('slug'),
            agent_dict.get('name'),
            agent_dict.get('role', 'Agent'),
            agent_dict.get('description', ''),
            agent_dict.get('capabilities', '[]'),
            agent_dict.get('avatar_url', '🤖'),
            agent_dict.get('is_active', 1),
            agent_dict.get('priority', 5),
            agent_dict.get('daily_quota', 10),
            agent_dict.get('quota_used', 0)
        ))
        agent_map[agent_dict.get('id')] = cur.lastrowid
    
    # Inserir personas do The Office
    print("🎭 Criando personas...")
    cur.execute('''
        INSERT INTO personas (slug, name, avatar_emoji, catch_phrase) VALUES
        ('michael', 'Michael Scott', '👔', 'That''s what she said!'),
        ('dwight', 'Dwight Schrute', '👓', 'Bears. Beets. Battlestar Galactica.'),
        ('jim', 'Jim Halpert', '😐', '*looks at camera*'),
        ('pam', 'Pam Beesly', '🎨', 'I feel God in this Chili''s'),
        ('stanley', 'Stanley Hudson', '🥨', 'Did I stutter?'),
        ('angela', 'Angela Martin', '🐈', 'I know everything.'),
        ('kevin', 'Kevin Malone', '🍲', 'Why waste time say lot word when few word do trick?'),
        ('oscar', 'Oscar Martinez', '📊', 'Actually...')
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ Migração concluída!")
    print("   Agora execute: python3 import_jules.py (se tiver os arquivos .md)")

if __name__ == '__main__':
    migrate()
