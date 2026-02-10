#!/usr/bin/env python3
"""
Agent Queue Consumer V2
Apenas gerencia a fila - não executa tarefas!
Execução real é feita pelo OpenClaw via cron.
"""

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

# Configuração
DB_PATH = Path(__file__).parent / "dunder_mifflin.db"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("agent-queue-consumer")

def get_db_connection():
    """Retorna conexão com o banco"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_tasks_by_status(status: str, limit: int = 5) -> list:
    """Busca tarefas por status"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM agent_tasks_queue 
        WHERE status = ?
        ORDER BY created_at ASC
        LIMIT ?
    """, (status, limit))
    
    tasks = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    return tasks

def update_task_status(task_id: int, status: str, result: str = None, error: str = None):
    """Atualiza status da tarefa"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    now = datetime.now().isoformat()
    
    if status == 'running':
        cur.execute("""
            UPDATE agent_tasks_queue 
            SET status = ?, started_at = ?
            WHERE id = ?
        """, (status, now, task_id))
    elif status in ('completed', 'failed'):
        cur.execute("""
            UPDATE agent_tasks_queue 
            SET status = ?, result = ?, error_message = ?, completed_at = ?
            WHERE id = ?
        """, (status, result, error, now, task_id))
    else:
        cur.execute("""
            UPDATE agent_tasks_queue 
            SET status = ?
            WHERE id = ?
        """, (status, task_id))
    
    conn.commit()
    conn.close()

def queue_tasks_for_openclaw():
    """
    Marca tarefas pendentes como 'queued_for_openclaw'.
    O OpenClaw (via cron) vai pegar estas e executar.
    """
    tasks = get_tasks_by_status('pending', limit=3)
    
    if not tasks:
        return 0
    
    logger.info(f"📋 {len(tasks)} tarefa(s) pendentes → marcando para OpenClaw")
    
    queued_count = 0
    for task in tasks:
        try:
            # Marca como 'queued_for_openclaw' - pronta para OpenClaw executar
            update_task_status(task['id'], 'queued_for_openclaw')
            logger.info(f"   📤 {task['task_code']} ({task['agent_slug']}) → queued_for_openclaw")
            queued_count += 1
        except Exception as e:
            logger.error(f"   ❌ Erro ao enfileirar {task['task_code']}: {e}")
    
    return queued_count

def process_completed_tasks():
    """
    Processa tarefas que o OpenClaw completou.
    Atualiza sessões e notifica worker (via banco).
    """
    # Busca tarefas que OpenClaw marcou como 'executing_by_openclaw' 
    # e já tem resultado (completed_by_openclaw)
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM agent_tasks_queue 
        WHERE status = 'completed_by_openclaw'
        ORDER BY completed_at ASC
        LIMIT 5
    """)
    
    tasks = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    if not tasks:
        return 0
    
    logger.info(f"✅ {len(tasks)} tarefa(s) completadas pelo OpenClaw")
    
    processed = 0
    for task in tasks:
        try:
            # Move para 'completed' final
            update_task_status(task['id'], 'completed', result=task.get('result'))
            logger.info(f"   ✓ {task['task_code']} finalizada")
            processed += 1
        except Exception as e:
            logger.error(f"   ❌ Erro ao processar {task['task_code']}: {e}")
    
    return processed

def cleanup_old_tasks():
    """Limpa tarefas muito antigas"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        DELETE FROM agent_tasks_queue 
        WHERE completed_at < datetime('now', '-7 days')
    """)
    
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    
    if deleted > 0:
        logger.info(f"🧹 {deleted} tarefa(s) antigas removidas")
    
    return deleted

def main():
    """Função principal - gerencia a fila"""
    logger.info("🚀 Agent Queue Consumer V2 iniciado")
    
    # 1. Enfileira tarefas pendentes para OpenClaw
    queued = queue_tasks_for_openclaw()
    
    # 2. Processa tarefas que OpenClaw completou
    processed = process_completed_tasks()
    
    # 3. Limpa tarefas antigas
    cleaned = cleanup_old_tasks()
    
    logger.info(f"✅ Consumer finalizado: {queued} enfileiradas, {processed} processadas, {cleaned} limpas")

if __name__ == "__main__":
    main()
