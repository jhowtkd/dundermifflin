#!/usr/bin/env python3
"""
OpenClaw Task Executor - Para ser usado com sessions_spawn
Este script atualiza o banco com o resultado da execução.
"""

import sys
import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "dunder_mifflin.db"

def update_task_result(task_id: int, status: str, result: str = None, error: str = None):
    """Atualiza resultado da tarefa no banco"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.now().isoformat()
    
    if status == 'completed_by_openclaw':
        cur.execute("""
            UPDATE agent_tasks_queue 
            SET status = ?, result = ?, completed_at = ?
            WHERE id = ?
        """, (status, result, now, task_id))
    elif status == 'failed_by_openclaw':
        cur.execute("""
            UPDATE agent_tasks_queue 
            SET status = ?, error_message = ?, completed_at = ?
            WHERE id = ?
        """, (status, error, now, task_id))
    
    conn.commit()
    conn.close()
    print(f"✅ Tarefa {task_id} atualizada: {status}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python update_task_result.py <task_id> <status> [result_or_error]")
        sys.exit(1)
    
    task_id = int(sys.argv[1])
    status = sys.argv[2]
    message = sys.argv[3] if len(sys.argv) > 3 else None
    
    if status == 'completed_by_openclaw':
        update_task_result(task_id, status, result=message)
    elif status == 'failed_by_openclaw':
        update_task_result(task_id, status, error=message)
    else:
        print(f"Status desconhecido: {status}")
        sys.exit(1)
