#!/usr/bin/env python3
"""
Agent Task Queue Consumer
Consome tarefas da fila e executa agentes via OpenClaw sessions_spawn
"""

import os
import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

# Configuração
DB_PATH = Path(__file__).parent / "dunder_mifflin.db"
AGENTS_DIR = Path(__file__).parent / "agents"

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

def load_agent_prompt(agent_slug: str) -> str:
    """Carrega o prompt do agente do arquivo markdown"""
    
    # Mapeamento completo de agentes
    agent_paths = {
        "debugger": "development/debugger.md",
        "tester": "testing/tester.md",
        "researcher": "product/researcher.md",
        "code-reviewer": "development/code-reviewer.md",
        "architect": "development/architect.md",
        "fullstack-developer": "development/fullstack-developer.md",
        "ai-engineer": "development/ai-engineer.md",
        "database-engineer": "development/database-engineer.md",
        "cicd-engineer": "development/cicd-engineer.md",
        "api-designer": "development/api-designer.md",
        "rapid-prototyper": "development/rapid-prototyper.md",
        "bolt": "autonomous/bolt.md",
        "sentinel": "autonomous/sentinel.md",
        "janitor": "autonomous/janitor.md",
        "migrator": "autonomous/migrator.md",
        "optimizer": "autonomous/optimizer.md",
        "a11y-specialist": "autonomous/a11y-specialist.md",
        "i18n-specialist": "autonomous/i18n-specialist.md",
        "ui-designer": "design/ui-designer.md",
        "ux-researcher": "design/ux-researcher.md",
        "ux-writer": "design/ux-writer.md",
        "palette": "design/palette.md",
        "polish": "design/polish.md",
        "brand-guardian": "design/brand-guardian.md",
        "visual-storyteller": "design/visual-storyteller.md",
        "whimsy-injector": "design/whimsy-injector.md",
        "feedback-synthesizer": "product/feedback-synthesizer.md",
        "sprint-prioritizer": "product/sprint-prioritizer.md",
        "trend-researcher": "product/trend-researcher.md",
        "social-media-manager": "marketing/social-media-manager.md",
        "copywriter": "marketing/copywriter.md",
        "seo-specialist": "marketing/seo-specialist.md",
        "content-strategist": "marketing/content-strategist.md",
        "growth-hacker": "marketing/growth-hacker.md",
        "email-marketing": "marketing/email-marketing.md",
        "community-manager": "marketing/community-manager.md",
        "jira-manager": "project-management/jira-manager.md",
        "notion-manager": "project-management/notion-manager.md",
        "github-manager": "project-management/github-manager.md",
        "sprint-master": "project-management/sprint-master.md",
        "risk-manager": "project-management/risk-manager.md",
        "stakeholder-liaison": "project-management/stakeholder-liaison.md",
        "release-coordinator": "project-management/release-coordinator.md",
        "twitter-engager": "social-media/twitter-engager.md",
        "linkedin-storyteller": "social-media/linkedin-storyteller.md",
        "instagram-visual": "social-media/instagram-visual.md",
        "youtube-scriptwriter": "social-media/youtube-scriptwriter.md",
        "tiktok-creator": "social-media/tiktok-creator.md",
        "mermaid-architect": "tools/mermaid-architect.md",
        "regex-wizard": "tools/regex-wizard.md",
        "sql-analyzer": "tools/sql-analyzer.md",
        "bash-automator": "tools/bash-automator.md",
        "dockerfile-optimizer": "tools/dockerfile-optimizer.md",
        "git-sherpa": "tools/git-sherpa.md",
        "json-wrangler": "tools/json-wrangler.md",
        "csv-magician": "tools/csv-magician.md",
    }
    
    if agent_slug in agent_paths:
        file_path = AGENTS_DIR / agent_paths[agent_slug]
    else:
        # Tenta encontrar em qualquer lugar
        file_path = AGENTS_DIR / f"{agent_slug}.md"
    
    if file_path.exists():
        with open(file_path) as f:
            return f.read()
    
    # Fallback
    return f"""Você é um agente especialista chamado {agent_slug}.
Sua tarefa é ajudar com o objetivo fornecido.
Seja completo e detalhado em sua resposta."""

def get_pending_tasks(limit: int = 3) -> list:
    """Busca tarefas pendentes na fila"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM agent_tasks_queue 
        WHERE status = 'pending'
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
    elif status in ('completed', 'failed'):
        cur.execute("""
            UPDATE agent_tasks_queue 
            SET status = ?, result = ?, error_message = ?, completed_at = ?
            WHERE id = ?
        """, (status, result, error, now, task_id))
    
    conn.commit()
    conn.close()

def execute_task_local(task: dict) -> dict:
    """Executa tarefa localmente (simulação por enquanto)"""
    agent_slug = task['agent_slug']
    task_desc = task['task_description']
    
    # Carrega prompt do agente
    prompt = load_agent_prompt(agent_slug)
    
    # Simula execução (em breve: chamar OpenClaw sessions_spawn)
    result = f"""✅ Agente {agent_slug} executou com sucesso!

## Prompt Utilizado:
{prompt[:500]}...

## Tarefa:
{task_desc}

## Resultado:
Tarefa processada. Integração com OpenClaw sessions_spawn em desenvolvimento.
Para execução real, configure o gateway OpenClaw.
"""
    
    return {
        "status": "completed",
        "output": result,
        "agent_slug": agent_slug
    }

def process_tasks():
    """Processa tarefas pendentes"""
    tasks = get_pending_tasks(limit=2)
    
    if not tasks:
        logger.info("Nenhuma tarefa pendente")
        return
    
    logger.info(f"Processando {len(tasks)} tarefa(s)...")
    
    for task in tasks:
        task_code = task['task_code']
        agent_slug = task['agent_slug']
        
        logger.info(f"▶️ Executando {task_code} ({agent_slug})")
        
        try:
            # Marca como running
            update_task_status(task['id'], 'running')
            
            # Executa tarefa
            result = execute_task_local(task)
            
            # Marca como completed
            update_task_status(task['id'], 'completed', result=json.dumps(result))
            
            logger.info(f"✅ {task_code} completado")
            
        except Exception as e:
            logger.error(f"❌ {task_code} falhou: {e}")
            update_task_status(task['id'], 'failed', error=str(e))

def main():
    """Função principal"""
    logger.info("🚀 Agent Queue Consumer iniciado")
    process_tasks()
    logger.info("✅ Consumer finalizado")

if __name__ == "__main__":
    main()
