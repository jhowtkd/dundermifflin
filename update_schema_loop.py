#!/usr/bin/env python3
"""
Atualiza schema do banco para suportar tipos de execução (loop)
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "dunder_mifflin.db"

def update_schema():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Adiciona colunas na tabela services
    try:
        cur.execute("ALTER TABLE services ADD COLUMN execution_type TEXT DEFAULT 'single'")
        print("✅ Coluna execution_type adicionada")
    except sqlite3.OperationalError:
        print("⚠️ Coluna execution_type já existe")
    
    try:
        cur.execute("ALTER TABLE services ADD COLUMN loop_config TEXT")
        print("✅ Coluna loop_config adicionada")
    except sqlite3.OperationalError:
        print("⚠️ Coluna loop_config já existe")
    
    try:
        cur.execute("ALTER TABLE services ADD COLUMN variation_contexts TEXT")
        print("✅ Coluna variation_contexts adicionada")
    except sqlite3.OperationalError:
        print("⚠️ Coluna variation_contexts já existe")
    
    conn.commit()
    conn.close()
    print("\n✅ Schema atualizado com sucesso!")

if __name__ == "__main__":
    update_schema()
