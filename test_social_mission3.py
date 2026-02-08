#!/usr/bin/env python3
"""Cria uma missão de teste de social media"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path.home() / ".openclaw" / "workspace" / "projects" / "dunder-mifflin" / "dunder_mifflin.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Encontra agente de marketing
agent = cur.execute("SELECT id FROM agents WHERE department = 'marketing' LIMIT 1").fetchone()
agent_id = agent[0] if agent else 1

# Cria a missão
cur.execute("""
    INSERT INTO missions (mission_code, agent_id, title, description, mission_type, status, priority, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", (
    f"MS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
    agent_id,
    "Planejamento Semanal Instagram - Biomecânica",
    "Criar planejamento de 5 posts para Instagram sobre biomecânica, movimento humano e saúde.",
    "social",
    "approved",
    5,
    datetime.now().isoformat()
))

mission_id = cur.lastrowid
conn.commit()
conn.close()

print(f"✅ Missão criada: ID {mission_id}")
print("Aguarde 5-10 segundos para o worker processar...")
