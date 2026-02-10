"""
Ralph Loop Integration Module
Integra o sistema Ralph Loop com o Worker V3
"""

import os
import sys
import json
import uuid
import sqlite3
import logging
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Optional

logger = logging.getLogger("ralph-loop")

DB_PATH = Path(__file__).parent / "dunder_mifflin.db"
RESULTS_DIR = Path(__file__).parent / "loops" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Preços aproximados por 1K tokens (ajustar conforme modelo usado)
TOKEN_PRICING = {
    "kimi-k2": {"input": 0.001, "output": 0.003},  # $ por 1K tokens
    "claude-sonnet": {"input": 0.003, "output": 0.015},
    "gemini-flash": {"input": 0.0001, "output": 0.0004},
}

def get_db():
    """Retorna conexão com o banco"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_loop(agent_slug: str, task_description: str, max_iterations: int = 20,
                completion_promise: str = "RALPH_COMPLETE") -> str:
    """Cria um novo Ralph Loop"""
    loop_code = f"RALPH-{uuid.uuid4().hex[:12].upper()}"
    
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO ralph_loops (loop_code, agent_slug, task_description, 
                                 max_iterations, completion_promise, status)
        VALUES (?, ?, ?, ?, ?, 'running')
    """, (loop_code, agent_slug, task_description, max_iterations, completion_promise))
    
    conn.commit()
    conn.close()
    
    logger.info(f"🔄 Ralph Loop criado: {loop_code} para {agent_slug}")
    return loop_code

def log_iteration(loop_code: str, iteration: int, prompt_summary: str,
                  response_summary: str, tokens_in: int = 0, tokens_out: int = 0,
                  model: str = "kimi-k2") -> bool:
    """Registra uma iteração do loop"""
    try:
        # Calcular custo
        pricing = TOKEN_PRICING.get(model, TOKEN_PRICING["kimi-k2"])
        cost_usd = (tokens_in / 1000 * pricing["input"]) + (tokens_out / 1000 * pricing["output"])
        
        conn = get_db()
        cur = conn.cursor()
        
        # Buscar log atual
        cur.execute("""
            SELECT iterations_log, total_tokens_in, total_tokens_out, total_cost_usd 
            FROM ralph_loops WHERE loop_code = ?
        """, (loop_code,))
        row = cur.fetchone()
        
        if not row:
            logger.error(f"Loop {loop_code} não encontrado")
            return False
        
        # Parse log existente
        iterations_log = json.loads(row["iterations_log"] or "[]")
        total_in = row["total_tokens_in"] or 0
        total_out = row["total_tokens_out"] or 0
        total_cost = row["total_cost_usd"] or 0
        
        # Adicionar nova iteração
        iterations_log.append({
            "iteration": iteration,
            "prompt_summary": prompt_summary[:200],  # Truncar
            "response_summary": response_summary[:500],  # Truncar
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cost_usd": round(cost_usd, 6),
            "model": model,
            "timestamp": datetime.now().isoformat()
        })
        
        # Atualizar totais
        total_in += tokens_in
        total_out += tokens_out
        total_cost += cost_usd
        
        cur.execute("""
            UPDATE ralph_loops 
            SET current_iteration = ?,
                iterations_log = ?,
                total_tokens_in = ?,
                total_tokens_out = ?,
                total_cost_usd = ?
            WHERE loop_code = ?
        """, (iteration, json.dumps(iterations_log), total_in, total_out, 
              round(total_cost, 6), loop_code))
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao logar iteração: {e}")
        return False

def complete_loop(loop_code: str, result_content: str, success: bool = True) -> bool:
    """Completa um Ralph Loop"""
    try:
        # Salvar resultado em arquivo
        result_filename = f"{loop_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        result_path = RESULTS_DIR / result_filename
        
        with open(result_path, 'w', encoding='utf-8') as f:
            f.write(f"# Resultado: {loop_code}\n\n")
            f.write(f"**Status:** {'✅ Completo' if success else '❌ Falhou'}\n")
            f.write(f"**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            f.write("---\n\n")
            f.write(result_content)
        
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE ralph_loops 
            SET status = ?,
                result_path = ?,
                completed_at = ?
            WHERE loop_code = ?
        """, ('completed' if success else 'failed', str(result_path), 
              datetime.now().isoformat(), loop_code))
        
        conn.commit()
        conn.close()
        
        # Atualizar métricas do dia
        update_daily_metrics(loop_code)
        
        # Preparar notificação
        try:
            prepare_notification(loop_code)
        except Exception as e:
            logger.warning(f"Não foi possível preparar notificação: {e}")
        
        logger.info(f"✅ Ralph Loop {loop_code} completado: {result_path}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao completar loop: {e}")
        return False


def prepare_notification(loop_code: str):
    """Prepara notificação para envio"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM ralph_loops WHERE loop_code = ?", (loop_code,))
    loop = dict(cur.fetchone())
    conn.close()
    
    if not loop:
        return
    
    agent_names = {
        'o-dev': '👨‍💻 O Dev',
        'o-marketeiro': '📢 O Marketeiro',
        'o-executivo': '💼 O Executivo'
    }
    
    agent_name = agent_names.get(loop['agent_slug'], loop['agent_slug'])
    status_icon = '✅' if loop['status'] == 'completed' else '❌'
    status_text = 'Completado' if loop['status'] == 'completed' else 'Falhou'
    
    # Calcular duração
    duration_str = "N/A"
    if loop.get('started_at') and loop.get('completed_at'):
        try:
            start = datetime.fromisoformat(loop['started_at'])
            end = datetime.fromisoformat(loop['completed_at'])
            duration = (end - start).total_seconds()
            if duration < 60:
                duration_str = f"{int(duration)}s"
            else:
                duration_str = f"{int(duration/60)}m {int(duration%60)}s"
        except:
            pass
    
    cost = loop.get('total_cost_usd', 0)
    
    # Criar arquivo de notificação
    notifications_dir = Path(__file__).parent / "loops" / "notifications"
    notifications_dir.mkdir(parents=True, exist_ok=True)
    
    notification_file = notifications_dir / f"{loop_code}.json"
    
    # URLs acessíveis
    dashboard_urls = {
        'tailscale': f"http://100.94.223.52:8888/ralph-dashboard.html?loop={loop_code}",
        'local': f"http://clawd-b450mhp:8888/ralph-dashboard.html?loop={loop_code}",
        'hostname': f"http://{os.uname().nodename}:8888/ralph-dashboard.html?loop={loop_code}"
    }
    
    notification_data = {
        'loop_code': loop_code,
        'agent': agent_name,
        'status': loop['status'],
        'status_text': status_text,
        'status_icon': status_icon,
        'task': loop['task_description'],
        'iterations': loop['current_iteration'],
        'max_iterations': loop['max_iterations'],
        'duration': duration_str,
        'cost': round(cost, 4),
        'dashboard_urls': dashboard_urls,
        'timestamp': datetime.now().isoformat(),
        'status_notification': 'pending'
    }
    
    with open(notification_file, 'w', encoding='utf-8') as f:
        json.dump(notification_data, f, indent=2)
    
    logger.info(f"📨 Notificação preparada: {loop_code}")

def update_daily_metrics(loop_code: str):
    """Atualiza métricas agregadas do dia"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Buscar dados do loop
        cur.execute("""
            SELECT agent_slug, status, current_iteration, total_tokens_in, 
                   total_tokens_out, total_cost_usd
            FROM ralph_loops WHERE loop_code = ?
        """, (loop_code,))
        row = cur.fetchone()
        
        if not row:
            return
        
        agent_slug = row["agent_slug"]
        today = date.today().isoformat()
        
        # Verificar se já existe registro para hoje
        cur.execute("""
            SELECT * FROM ralph_metrics 
            WHERE agent_slug = ? AND date = ?
        """, (agent_slug, today))
        
        metrics_row = cur.fetchone()
        
        if metrics_row:
            # Atualizar existente
            loops_completed = metrics_row["loops_completed"] + (1 if row["status"] == "completed" else 0)
            loops_failed = metrics_row["loops_failed"] + (1 if row["status"] == "failed" else 0)
            total_iterations = metrics_row["total_iterations"] + row["current_iteration"]
            total_cost = metrics_row["total_cost_usd"] + row["total_cost_usd"]
            
            total_loops = loops_completed + loops_failed
            avg_iterations = total_iterations / max(total_loops, 1)
            avg_cost = total_cost / max(total_loops, 1)
            success_rate = loops_completed / max(total_loops, 1)
            
            cur.execute("""
                UPDATE ralph_metrics SET
                    loops_completed = ?,
                    loops_failed = ?,
                    total_iterations = ?,
                    total_tokens_in = total_tokens_in + ?,
                    total_tokens_out = total_tokens_out + ?,
                    total_cost_usd = ?,
                    avg_iterations_per_loop = ?,
                    avg_cost_per_loop = ?,
                    success_rate = ?,
                    updated_at = ?
                WHERE agent_slug = ? AND date = ?
            """, (loops_completed, loops_failed, total_iterations,
                  row["total_tokens_in"], row["total_tokens_out"],
                  total_cost, avg_iterations, avg_cost, success_rate,
                  datetime.now().isoformat(), agent_slug, today))
        else:
            # Criar novo
            is_completed = row["status"] == "completed"
            cur.execute("""
                INSERT INTO ralph_metrics 
                (agent_slug, date, loops_started, loops_completed, loops_failed,
                 total_iterations, avg_iterations_per_loop, total_tokens_in,
                 total_tokens_out, total_cost_usd, avg_cost_per_loop, success_rate)
                VALUES (?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (agent_slug, today, 1 if is_completed else 0, 0 if is_completed else 1,
                  row["current_iteration"], row["current_iteration"],
                  row["total_tokens_in"], row["total_tokens_out"],
                  row["total_cost_usd"], row["total_cost_usd"],
                  1.0 if is_completed else 0.0))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"Erro ao atualizar métricas: {e}")

# ============================================================================
# API FUNCTIONS (para dashboard)
# ============================================================================

def get_active_loops() -> List[Dict]:
    """Retorna loops atualmente em execução"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM ralph_loops 
        WHERE status = 'running'
        ORDER BY started_at DESC
    """)
    
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows

def get_loop_history(limit: int = 50) -> List[Dict]:
    """Retorna histórico de loops (completos/falhos)"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM ralph_loops 
        WHERE status IN ('completed', 'failed')
        ORDER BY completed_at DESC
        LIMIT ?
    """, (limit,))
    
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows

def get_loop_details(loop_code: str) -> Optional[Dict]:
    """Retorna detalhes de um loop específico"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM ralph_loops WHERE loop_code = ?", (loop_code,))
    row = cur.fetchone()
    
    if row:
        result = dict(row)
        # Parse iterations_log
        if result.get("iterations_log"):
            result["iterations"] = json.loads(result["iterations_log"])
        else:
            result["iterations"] = []
        return result
    
    conn.close()
    return None

def get_cost_summary(days: int = 30) -> Dict:
    """Retorna resumo de custos dos últimos N dias"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            SUM(total_cost_usd) as total_cost,
            SUM(total_tokens_in) as total_in,
            SUM(total_tokens_out) as total_out,
            SUM(loops_completed) as total_completed,
            SUM(loops_failed) as total_failed
        FROM ralph_metrics
        WHERE date >= date('now', '-{} days')
    """.format(days))
    
    row = cur.fetchone()
    conn.close()
    
    if row:
        return {
            "total_cost_usd": round(row["total_cost"] or 0, 4),
            "total_tokens_in": row["total_in"] or 0,
            "total_tokens_out": row["total_out"] or 0,
            "total_loops": (row["total_completed"] or 0) + (row["total_failed"] or 0),
            "completed": row["total_completed"] or 0,
            "failed": row["total_failed"] or 0,
            "success_rate": round((row["total_completed"] or 0) / max((row["total_completed"] or 0) + (row["total_failed"] or 0), 1), 2)
        }
    
    return {"total_cost_usd": 0, "total_tokens_in": 0, "total_tokens_out": 0, 
            "total_loops": 0, "completed": 0, "failed": 0, "success_rate": 0}

def get_agent_metrics(agent_slug: str = None, days: int = 7) -> List[Dict]:
    """Retorna métricas por agente"""
    conn = get_db()
    cur = conn.cursor()
    
    if agent_slug:
        cur.execute("""
            SELECT * FROM ralph_metrics
            WHERE agent_slug = ? AND date >= date('now', '-{} days')
            ORDER BY date DESC
        """.format(days), (agent_slug,))
    else:
        # Agregado por agente
        cur.execute("""
            SELECT 
                agent_slug,
                SUM(loops_started) as total_started,
                SUM(loops_completed) as total_completed,
                SUM(loops_failed) as total_failed,
                SUM(total_cost_usd) as total_cost,
                AVG(success_rate) as avg_success_rate
            FROM ralph_metrics
            WHERE date >= date('now', '-{} days')
            GROUP BY agent_slug
        """.format(days))
    
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows

# Exportar funções para uso no worker
__all__ = [
    'create_loop', 'log_iteration', 'complete_loop',
    'get_active_loops', 'get_loop_history', 'get_loop_details',
    'get_cost_summary', 'get_agent_metrics'
]
