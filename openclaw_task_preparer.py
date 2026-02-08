#!/usr/bin/env python3
"""
OpenClaw Agent Executor
Este script é chamado pelo OpenClaw (via cron) para executar tarefas.
NÃO é executado diretamente - é chamado como sub-agent.
"""

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "dunder_mifflin.db"
AGENTS_DIR = Path(__file__).parent / "agents"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("openclaw-executor")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def load_agent_prompt(agent_slug: str) -> str:
    """Carrega o prompt do agente"""
    agent_paths = {
        "debugger": "development/debugger.md",
        "tester": "testing/tester.md",
        "researcher": "product/researcher.md",
        "code-reviewer": "development/code-reviewer.md",
        "architect": "development/architect.md",
        "fullstack-developer": "development/fullstack-developer.md",
        "ai-engineer": "development/ai-engineer.md",
        "database-engineer": "development/database-engineer.md",
        "twitter-engager": "social-media/twitter-engager.md",
        "linkedin-storyteller": "social-media/linkedin-storyteller.md",
        "instagram-visual": "social-media/instagram-visual.md",
        "copywriter": "marketing/copywriter.md",
        "content-strategist": "marketing/content-strategist.md",
        "bolt": "autonomous/bolt.md",
        "sentinel": "autonomous/sentinel.md",
        "janitor": "autonomous/janitor.md",
    }
    
    if agent_slug in agent_paths:
        file_path = AGENTS_DIR / agent_paths[agent_slug]
    else:
        file_path = AGENTS_DIR / f"{agent_slug}.md"
    
    if file_path.exists():
        with open(file_path) as f:
            return f.read()
    
    return f"Você é um agente especialista chamado {agent_slug}. Execute a tarefa solicitada."

def get_tasks_for_execution(limit: int = 2) -> list:
    """Busca tarefas prontas para execução pelo OpenClaw"""
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

def mark_task_running(task_id: int):
    """Marca tarefa como em execução"""
    conn = get_db_connection()
    cur = conn.cursor()
    now = datetime.now().isoformat()
    
    cur.execute("""
        UPDATE agent_tasks_queue 
        SET status = 'executing_by_openclaw', started_at = ?
        WHERE id = ?
    """, (now, task_id))
    
    conn.commit()
    conn.close()

def mark_task_completed(task_id: int, result: str):
    """Marca tarefa como completada"""
    conn = get_db_connection()
    cur = conn.cursor()
    now = datetime.now().isoformat()
    
    cur.execute("""
        UPDATE agent_tasks_queue 
        SET status = 'completed_by_openclaw', result = ?, completed_at = ?
        WHERE id = ?
    """, (result, now, task_id))
    
    conn.commit()
    conn.close()

def mark_task_failed(task_id: int, error: str):
    """Marca tarefa como falha"""
    conn = get_db_connection()
    cur = conn.cursor()
    now = datetime.now().isoformat()
    
    cur.execute("""
        UPDATE agent_tasks_queue 
        SET status = 'failed_by_openclaw', error_message = ?, completed_at = ?
        WHERE id = ?
    """, (error, now, task_id))
    
    conn.commit()
    conn.close()

def execute_task(task: dict) -> dict:
    """
    Executa uma tarefa usando OpenClaw sessions_spawn.
    ESTA FUNÇÃO É CHAMADA PELO OPENCLAW - NÃO EXECUTAR DIRETAMENTE!
    """
    agent_slug = task['agent_slug']
    task_desc = task['task_description']
    
    # Carrega prompt do agente
    prompt = load_agent_prompt(agent_slug)
    
    # Monta a mensagem completa para o agente
    full_task = f"""{prompt}

---

## TAREFA ATUAL

{task_desc}

---

## INSTRUÇÕES

1. Execute esta tarefa completamente
2. Retorne o resultado detalhado do trabalho realizado
3. Se criar arquivos, liste-os
4. Se houver código, inclua-o na resposta

## FORMATO DA RESPOSTA

```
## Resumo
[Breve descrição do que foi feito]

## Detalhes
[Detalhes completos, análises, descobertas]

## Arquivos/Código (se houver)
[Lista de arquivos criados/modificados ou código gerado]

## Próximos Passos (se aplicável)
[Recomendações para continuar o trabalho]
```
"""
    
    # Retorna estrutura para o OpenClaw usar sessions_spawn
    return {
        "task_id": task['id'],
        "task_code": task['task_code'],
        "agent_slug": agent_slug,
        "message": full_task,
        "model": "kimi-coding/k2p5",
        "timeout_seconds": 300
    }

def main():
    """
    Função principal - prepara tarefas para execução.
    O OpenClaw vai chamar sessions_spawn para cada tarefa.
    """
    logger.info("🔍 Buscando tarefas para execução...")
    
    tasks = get_tasks_for_execution(limit=2)
    
    if not tasks:
        logger.info("📭 Nenhuma tarefa pendente")
        return []
    
    logger.info(f"📋 {len(tasks)} tarefa(s) encontradas")
    
    prepared_tasks = []
    for task in tasks:
        try:
            # Marca como em execução
            mark_task_running(task['id'])
            
            # Prepara a tarefa
            prepared = execute_task(task)
            prepared_tasks.append(prepared)
            
            logger.info(f"   🎯 {task['task_code']} ({task['agent_slug']}) preparada")
            
        except Exception as e:
            logger.error(f"   ❌ Erro ao preparar {task['task_code']}: {e}")
            mark_task_failed(task['id'], str(e))
    
    return prepared_tasks

if __name__ == "__main__":
    # Quando executado diretamente, apenas mostra tarefas preparadas
    tasks = main()
    if tasks:
        print(json.dumps(tasks, indent=2, ensure_ascii=False))
    else:
        print("[]")
