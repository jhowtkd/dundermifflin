#!/usr/bin/env python3
"""
Ralph Loop Executor V3 - Usa OpenClaw sessions_spawn
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.expanduser('~/.openclaw/workspace/projects/dunder-mifflin'))
from ralph_loop import get_active_loops, log_iteration, complete_loop

LOOPS_DIR = Path.home() / ".openclaw/workspace/projects/dunder-mifflin/loops"
LOGS_DIR = LOOPS_DIR / "logs"
RESULTS_DIR = LOOPS_DIR / "results"

def load_prompt(agent_slug: str) -> str:
    prompt_file = LOOPS_DIR / "prompts" / f"{agent_slug.replace('o-', '')}-prompt.md"
    if prompt_file.exists():
        return prompt_file.read_text()
    return f"# Agente {agent_slug}\nVocê é um assistente especializado."

def build_iteration_task(agent_slug: str, task: str, history: str) -> str:
    agent_prompt = load_prompt(agent_slug)
    
    return f"""{agent_prompt}

## Tarefa Específica
{task}

## Progresso Anterior
{history}

## Instruções
1. Execute o próximo passo da tarefa
2. Se estiver COMPLETAMENTE PRONTO, inclua <RALPH_COMPLETE> na resposta
3. Se não estiver pronto, liste os próximos passos

Responda agora:"""

def validate_completion(response: str) -> tuple:
    """Valida se a resposta está completa e contém RALPH_COMPLETE"""
    
    # Verificar se contém RALPH_COMPLETE
    has_complete_tag = "<RALPH_COMPLETE>" in response
    
    # Verificar se a resposta parece truncada
    lines = response.strip().split('\n')
    last_line = lines[-1] if lines else ""
    
    # Contar blocos de código abertos vs fechados
    code_blocks_open = response.count("```") % 2
    
    # Verificar se termina abruptamente
    ends_abruptly = False
    if response.rstrip().endswith(('...', '-', '>', '[', '(')):
        ends_abruptly = True
    elif code_blocks_open == 1:
        ends_abruptly = True
    elif len(last_line) > 3:
        last_char = last_line[-1]
        if last_char not in '.!?`:)]>)}':
            ends_abruptly = True
    
    # Só considerar completo se tem a tag e não parece truncado
    is_valid_complete = has_complete_tag and not ends_abruptly
    
    return is_valid_complete, has_complete_tag, ends_abruptly

def run_iteration(loop_code: str, agent_slug: str, task: str, history: str, iteration: int) -> tuple:
    """Executa uma iteração via OpenClaw sessions_spawn"""
    
    iteration_task = build_iteration_task(agent_slug, task, history)
    
    # Salvar task em arquivo temporário
    temp_file = LOGS_DIR / f"{loop_code}_iter_{iteration}_task.txt"
    temp_file.write_text(iteration_task)
    
    try:
        # Chamar kimi CLI diretamente
        import subprocess
        
        cmd = ["kimi", "--print", "--quiet", "--prompt", iteration_task]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        response = result.stdout
        tokens_in = len(iteration_task) // 4
        tokens_out = len(response) // 4
        
        # Validar completion com regras mais rigorosas
        is_valid_complete, has_tag, is_truncated = validate_completion(response)
        
        if has_tag and is_truncated:
            print(f"⚠️  Resposta parece truncada mesmo com RALPH_COMPLETE")
            is_valid_complete = False
        
        return response, tokens_in, tokens_out, is_valid_complete
        
    except Exception as e:
        return f"Erro: {e}", 0, 0, False
    finally:
        if temp_file.exists():
            temp_file.unlink()

def execute_loop(loop_code: str, agent_slug: str, task: str, max_iterations: int):
    """Executa o loop completo"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_DIR / f"{loop_code}_{timestamp}.py.log"
    
    print(f"\n🚀 Loop {loop_code}")
    print(f"   Agente: {agent_slug}")
    print(f"   Tarefa: {task[:50]}...")
    
    iteration = 0
    history = "Primeira iteração - nada feito ainda"
    completed = False
    total_in = 0
    total_out = 0
    
    with open(log_file, 'w') as log_f:
        log_f.write(f"Loop: {loop_code}\nAgente: {agent_slug}\nTarefa: {task}\n\n")
        
        while iteration < max_iterations and not completed:
            iteration += 1
            print(f"   🔄 Iteração {iteration}/{max_iterations}...", end=" ", flush=True)
            
            response, tokens_in, tokens_out, is_complete = run_iteration(
                loop_code, agent_slug, task, history, iteration
            )
            
            total_in += tokens_in
            total_out += tokens_out
            
            # Logar no banco
            log_iteration(loop_code, iteration, task[:200], response[:500], tokens_in, tokens_out)
            
            log_f.write(f"\n--- Iteração {iteration} ---\n")
            log_f.write(response[:800] + "\n")
            log_f.write(f"Tokens: {tokens_in} in / {tokens_out} out\n")
            
            if is_complete:
                print(f"✅ COMPLETADO!")
                completed = True
                
                result_path = RESULTS_DIR / f"{loop_code}_{timestamp}_COMPLETED.md"
                result_path.write_text(f"# {loop_code} - COMPLETED\n\n{response}")
                complete_loop(loop_code, response, True)
                
            else:
                print(f"⏳ continuando...")
                history = f"Iteração {iteration}: {response[:200]}..."
        
        if not completed:
            print(f"   ⏹️  Max iterations atingido")
            result_path = RESULTS_DIR / f"{loop_code}_{timestamp}_INCOMPLETE.md"
            result_path.write_text(f"# {loop_code} - INCOMPLETE\n\nMax iterations atingido.")
            complete_loop(loop_code, "Max iterations atingido", False)
    
    print(f"   💾 Log: {log_file}")

def main():
    print("🔍 Verificando loops pendentes...")
    
    loops = get_active_loops()
    
    # Filtrar apenas loops na iteração 0
    pending = [l for l in loops if l.get('current_iteration', 0) == 0]
    
    if not pending:
        print("✅ Nenhum loop pendente")
        return
    
    print(f"📋 {len(pending)} loop(s) para executar\n")
    
    for loop in pending:
        try:
            execute_loop(
                loop_code=loop['loop_code'],
                agent_slug=loop['agent_slug'],
                task=loop['task_description'],
                max_iterations=loop.get('max_iterations', 10)
            )
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    print(f"\n🏁 Concluído!")

if __name__ == '__main__':
    main()
