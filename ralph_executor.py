#!/usr/bin/env python3
"""
Ralph Loop Executor - Worker automático
Processa loops pendentes e executa as iterações
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Adicionar path do projeto
sys.path.insert(0, os.path.expanduser('~/.openclaw/workspace/projects/dunder-mifflin'))

from ralph_loop import get_active_loops, get_db

LOOPS_DIR = Path.home() / ".openclaw/workspace/projects/dunder-mifflin/loops"
LOGS_DIR = LOOPS_DIR / "logs"

def is_loop_running(loop_code: str) -> bool:
    """Verifica se um loop já está sendo executado por outro processo"""
    # Verificar no banco se current_iteration mudou recentemente
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT current_iteration, iterations_log FROM ralph_loops 
        WHERE loop_code = ?
    """, (loop_code,))
    row = cur.fetchone()
    conn.close()
    
    if row and row['current_iteration'] > 0:
        return True
    return False

def execute_loop(loop_code: str, agent_slug: str, task: str, max_iterations: int = 20):
    """Executa um loop via CLI em background desanexado"""
    
    # Mapear slug do agente para nome curto
    agent_map = {
        'o-dev': 'dev',
        'o-marketeiro': 'marketeiro',
        'o-executivo': 'executivo'
    }
    agent = agent_map.get(agent_slug, agent_slug)
    
    # Arquivo de log para capturar saída
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stdout_log = LOGS_DIR / f"{loop_code}_{timestamp}.out.log"
    stderr_log = LOGS_DIR / f"{loop_code}_{timestamp}.err.log"
    
    # Construir comando
    cmd = [
        str(LOOPS_DIR / "ralph-loop.sh"),
        agent,
        "--task", task,
        "--max-iterations", str(max_iterations),
        "--loop-code", loop_code
    ]
    
    print(f"🚀 Executando loop {loop_code}...")
    print(f"   Agente: {agent}")
    print(f"   Tarefa: {task[:50]}...")
    print(f"   Logs: {stdout_log.name}")
    
    # Abrir arquivos de log
    with open(stdout_log, 'w') as out_f, open(stderr_log, 'w') as err_f:
        # Executar em background desanexado do pai
        # start_new_session=True cria um novo grupo de processos (daemon)
        process = subprocess.Popen(
            cmd,
            stdout=out_f,
            stderr=err_f,
            cwd=str(LOOPS_DIR),
            start_new_session=True,  # Desanexa do processo pai
            close_fds=True  # Fecha file descriptors herdados
        )
    
    return process, stdout_log, stderr_log

def main():
    """Worker principal - verifica e executa loops pendentes"""
    
    print("🔍 Verificando loops pendentes...")
    
    # Buscar loops ativos (running mas sem iterações)
    loops = get_active_loops()
    
    if not loops:
        print("✅ Nenhum loop pendente")
        return
    
    print(f"📋 {len(loops)} loop(s) encontrado(s)")
    
    started_count = 0
    
    for loop in loops:
        loop_code = loop['loop_code']
        current_iter = loop.get('current_iteration', 0)
        
        # Se ainda está na iteração 0, precisa ser executado
        if current_iter == 0:
            # Verificar se já não está rodando (evitar duplicatas)
            if is_loop_running(loop_code):
                print(f"\n⏭️  Loop {loop_code} já foi iniciado por outro processo")
                continue
            
            print(f"\n⏳ Loop {loop_code} precisa ser iniciado")
            
            try:
                # Executar
                process, out_log, err_log = execute_loop(
                    loop_code=loop_code,
                    agent_slug=loop['agent_slug'],
                    task=loop['task_description'],
                    max_iterations=loop.get('max_iterations', 20)
                )
                
                print(f"   PID: {process.pid}")
                print(f"   Status: Iniciado em background (daemon)")
                print(f"   Log stdout: {out_log}")
                print(f"   Log stderr: {err_log}")
                started_count += 1
                
                # Pequena pausa entre loops para não sobrecarregar
                time.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Erro ao iniciar loop: {e}")
        else:
            print(f"\n✅ Loop {loop_code} já está em execução (iteração {current_iter})")
    
    print(f"\n🏁 Worker concluído - {started_count} loop(s) iniciado(s)")

if __name__ == '__main__':
    main()
