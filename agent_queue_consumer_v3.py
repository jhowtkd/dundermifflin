#!/usr/bin/env python3
"""
Agent Queue Consumer V3 - COM EXECUÇÃO REAL
Executa tarefas usando agent_executor.py com suporte a projetos
"""

import os
import sys
import json
import sqlite3
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Configuração
DB_PATH = Path(__file__).parent / "dunder_mifflin.db"
AGENT_EXECUTOR = Path(__file__).parent / "agent_executor.py"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("agent-queue-executor")

def get_db_connection():
    """Retorna conexão com o banco"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_pending_tasks(limit: int = 2) -> list:
    """Busca tarefas prontas para execução"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM agent_tasks_queue 
        WHERE status = 'queued_for_openclaw'
        ORDER BY created_at ASC
        LIMIT ?
    """, (limit,))
    
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
    elif status in ('completed', 'failed', 'completed_by_openclaw', 'failed_by_openclaw'):
        cur.execute("""
            UPDATE agent_tasks_queue 
            SET status = ?, result = ?, error_message = ?, completed_at = ?
            WHERE id = ?
        """, (status, result, error, now, task_id))
    
    conn.commit()
    conn.close()

def execute_task_with_agent(task: dict) -> dict:
    """
    Executa uma tarefa usando o agent_executor.py
    Com suporte a projetos e Git
    """
    agent_slug = task['agent_slug']
    task_desc = task['task_description']
    task_code = task['task_code']
    project_slug = task.get('project_slug')
    
    logger.info(f"▶️ Executando {task_code}: {agent_slug}")
    
    try:
        # Monta comando com argumentos
        cmd = [
            sys.executable,
            str(AGENT_EXECUTOR),
            agent_slug,
            task_desc,
            '--json'
        ]
        
        # Adiciona projeto se existir
        if project_slug:
            cmd.extend(['--project', project_slug])
            cmd.extend(['--task-code', task_code])
        
        logger.info(f"   📝 Comando: {' '.join(cmd[:6])}...")
        
        # Executa agente
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutos timeout
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            # Parse do resultado JSON
            try:
                output_data = json.loads(result.stdout)
                logger.info(f"   ✅ {task_code} completado com sucesso")
                
                # Log de projeto/branch se existir
                if output_data.get('project'):
                    logger.info(f"   📁 Projeto: {output_data['project']}")
                if output_data.get('branch'):
                    logger.info(f"   🌿 Branch: {output_data['branch']}")
                
                return {
                    "status": "completed_by_openclaw",
                    "result": result.stdout,
                    "error": None
                }
            except json.JSONDecodeError:
                logger.warning(f"   ⚠️  Saída não é JSON válido, usando como texto")
                return {
                    "status": "completed_by_openclaw",
                    "result": json.dumps({"output": result.stdout}),
                    "error": None
                }
        else:
            logger.error(f"   ❌ {task_code} falhou: {result.stderr[:200]}")
            return {
                "status": "failed_by_openclaw",
                "result": None,
                "error": result.stderr or "Erro desconhecido"
            }
            
    except subprocess.TimeoutExpired:
        logger.error(f"   ⏱️ {task_code} timeout após 300s")
        return {
            "status": "failed_by_openclaw",
            "result": None,
            "error": "Timeout: Execução excedeu 5 minutos"
        }
    except Exception as e:
        logger.error(f"   ❌ Erro ao executar {task_code}: {e}")
        return {
            "status": "failed_by_openclaw",
            "result": None,
            "error": str(e)
        }

def process_tasks():
    """Processa tarefas pendentes - EXECUTA AGENTES"""
    tasks = get_pending_tasks(limit=2)
    
    if not tasks:
        logger.info("📭 Nenhuma tarefa pendente para execução")
        return 0
    
    logger.info(f"🎯 {len(tasks)} tarefa(s) para executar")
    
    executed = 0
    for task in tasks:
        try:
            # Marca como em execução
            update_task_status(task['id'], 'executing_by_openclaw')
            logger.info(f"   🚀 {task['task_code']} ({task['agent_slug']}) - EXECUTANDO")
            
            # EXECUTA A TAREFA
            result = execute_task_with_agent(task)
            
            # Atualiza resultado
            update_task_status(
                task['id'],
                result['status'],
                result=result.get('result'),
                error=result.get('error')
            )
            
            if result['status'] == 'completed_by_openclaw':
                executed += 1
                logger.info(f"   ✅ {task['task_code']} finalizado")
            else:
                logger.error(f"   ❌ {task['task_code']} falhou: {result.get('error', 'unknown')}")
            
        except Exception as e:
            logger.error(f"   ❌ Erro crítico em {task['task_code']}: {e}")
            update_task_status(task['id'], 'failed_by_openclaw', error=str(e))
    
    return executed

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
    """Função principal - EXECUTA TAREFAS"""
    logger.info("🚀 Agent Queue Consumer V3 (Executor) iniciado")
    logger.info("   ⚙️  Modo: EXECUÇÃO REAL com suporte a projetos")
    
    # 1. Executa tarefas pendentes
    executed = process_tasks()
    
    # 2. Limpa tarefas antigas
    cleaned = cleanup_old_tasks()
    
    logger.info(f"✅ Executor finalizado: {executed} executadas, {cleaned} limpas")

if __name__ == "__main__":
    main()
