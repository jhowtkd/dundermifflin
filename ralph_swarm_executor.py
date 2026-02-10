#!/usr/bin/env python3
"""
Ralph Swarm Executor v4.0
Executor paralelo de swarms com suporte a interns
"""

import os
import sys
import subprocess
import concurrent.futures
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.expanduser('~/.openclaw/workspace/projects/dunder-mifflin'))

LOOPS_DIR = Path.home() / ".openclaw/workspace/projects/dunder-mifflin/loops"
RESULTS_DIR = LOOPS_DIR / "results"

def call_llm(prompt: str, model: str = "google-antigravity/gemini-3-flash", timeout: int = 60) -> str:
    """Chama LLM via kimi CLI"""
    try:
        cmd = ["kimi", "--print", "--quiet", "--prompt", prompt]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout
    except Exception as e:
        return f"Erro: {e}"

def execute_intern_task(task: str, intern_type: str) -> dict:
    """Executa uma tarefa de intern e retorna resultado estruturado"""
    
    prompt = f"""Você é um Intern de {intern_type.upper()}. Sua função é executar tarefas específicas de forma rápida e eficiente.

TAREFA: {task}

INSTRUÇÕES:
- Seja direto e objetivo
- Forneça apenas o resultado, sem explicações longas
- Se precisar de múltiplos itens, use bullet points
- Inclua <RALPH_COMPLETE> quando terminar

Execute agora:"""
    
    response = call_llm(prompt, model="google-antigravity/gemini-3-flash")
    
    return {
        'task': task,
        'type': intern_type,
        'result': response,
        'completed': '<RALPH_COMPLETE>' in response,
        'tokens': len(prompt) + len(response)
    }

def run_parallel_interns(tasks: list) -> list:
    """Executa múltiplos interns em paralelo"""
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_task = {
            executor.submit(execute_intern_task, t['task'], t['type']): t 
            for t in tasks
        }
        
        for future in concurrent.futures.as_completed(future_to_task):
            task = future_to_task[future]
            try:
                result = future.result()
                results.append(result)
                print(f"   ✅ Intern ({task['type']}) completado")
            except Exception as e:
                print(f"   ❌ Intern falhou: {e}")
                results.append({'task': task['task'], 'type': task['type'], 'error': str(e)})
    
    return results

def main():
    """Teste simples do executor de swarm"""
    print("🐝 Ralph Swarm Executor v4.0")
    print("=" * 50)
    
    # Tarefas de teste para interns
    tasks = [
        {'type': 'research', 'task': 'Liste 5 concorrentes de SaaS de produtividade com preços'},
        {'type': 'research', 'task': 'Encontre 3 benchmarks de landing pages de SaaS B2B'},
        {'type': 'analyze', 'task': 'Analise quais cores funcionam melhor para landing pages de produtividade'},
    ]
    
    print(f"\nExecutando {len(tasks)} interns em paralelo...")
    results = run_parallel_interns(tasks)
    
    print("\n" + "=" * 50)
    print("RESULTADOS:")
    for r in results:
        print(f"\n[{r['type'].upper()}]")
        print(r.get('result', r.get('error', 'Sem resultado'))[:200] + "...")

if __name__ == '__main__':
    main()
