#!/usr/bin/env python3
"""
Re-executa planos 19-23 para gerar arquivos com conteúdo completo (não truncado)
"""

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

DB_PATH = Path(__file__).parent / "dunder_mifflin.db"

def reset_plans_for_reexecution():
    """Reseta planos para re-execução"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Busca planos 19-23
    cur.execute("""
        SELECT id, title, status FROM execution_plans 
        WHERE id BETWEEN 19 AND 23
        ORDER BY id
    """)
    
    plans = cur.fetchall()
    print(f"📋 Encontrados {len(plans)} planos para re-executar:\n")
    
    for plan_id, title, status in plans:
        print(f"  • Plano #{plan_id}: {title[:50]}... (status: {status})")
    
    # Reset status para 'approved' para re-execução
    cur.execute("""
        UPDATE execution_plans 
        SET status = 'approved', final_result = NULL, completed_at = NULL
        WHERE id BETWEEN 19 AND 23
    """)
    
    # Limpa sessões antigas desses planos
    cur.execute("""
        DELETE FROM orchestration_sessions 
        WHERE execution_plan_id BETWEEN 19 AND 23
    """)
    
    # Limpa tasks antigas
    cur.execute("""
        DELETE FROM agent_tasks_queue 
        WHERE session_id IN (
            SELECT id FROM orchestration_sessions 
            WHERE execution_plan_id BETWEEN 19 AND 23
        )
    """)
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Planos 19-23 resetados para 'approved'")
    print("🚀 O Worker V2 vai re-executá-los automaticamente")
    print("⏱️ Tempo estimado: 15-20 minutos para todos")

if __name__ == "__main__":
    reset_plans_for_reexecution()
