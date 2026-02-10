#!/usr/bin/env python3
"""
Ralph Loop Executor - Worker automático (Python puro)
Processa loops pendentes e executa as iterações via OpenClaw API
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Adicionar path do projeto
sys.path.insert(0, os.path.expanduser('~/.openclaw/workspace/projects/dunder-mifflin'))

from ralph_loop import get_active_loops, get_db, log_iteration, complete_loop

LOOPS_DIR = Path.home() / ".openclaw/workspace/projects/dunder-mifflin/loops"
LOGS_DIR = LOOPS_DIR / "logs"
RESULTS_DIR = LOOPS_DIR / "results"

# Mapear agentes para seus prompts
AGENT_PROMPTS = {
    'o-dev': LOOPS_DIR / "prompts" / "dev-prompt.md",
    'o-marketeiro': LOOPS_DIR / "prompts" / "marketeiro-prompt.md",
    'o-executivo': LOOPS_DIR / "prompts" / "executivo-prompt.md",
}

def load_agent_prompt(agent_slug: str) -> str:
    """Carrega o prompt do agente"""
    prompt_file = AGENT_PROMPTS.get(agent_slug)
    if prompt_file and prompt_file.exists():
        return prompt_file.read_text()
    return f"# Agente {agent_slug}\nVocê é um assistente especializado."

def build_prompt(agent_slug: str, task: str, history: str = "", iteration: int = 1) -> str:
    """Constrói o prompt completo para o agente"""
    agent_prompt = load_agent_prompt(agent_slug)
    
    prompt = f"""{agent_prompt}

## Tarefa Específica
{task}

## Instruções de Iteração
1. Analise o que já foi feito (se houver histórico abaixo)
2. Execute o próximo passo lógico da tarefa
3. Documente o que foi feito nesta iteração
4. Avalie se a tarefa está completa
5. Se completa, output: <RALPH_COMPLETE>
6. Se incompleta, liste os próximos passos

## Progresso Anterior
{history}

## Regras Importantes
- Não reinvente o que já foi feito
- Se encontrar erro, corrija e continue
- Se travar por mais de 3 iterações, documente o bloqueio
- Sempre mantenha o foco na tarefa original
- Output <RALPH_COMPLETE> apenas quando REALMENTE completo

## Métricas desta Iteração
Ao final, inclua:
- TOKENS_IN: [estimativa]
- TOKENS_OUT: [estimativa]

Execute agora:"""
    
    return prompt

def call_agent(prompt: str, model: str = "kimi-coding/k2p5") -> tuple:
    """Chama o agente via OpenClaw sessions_spawn"""
    
    # Criar um arquivo temporário com o prompt
    temp_prompt = LOGS_DIR / f"temp_prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    temp_prompt.write_text(prompt)
    
    try:
        # Usar kimi CLI diretamente com o arquivo de prompt
        # Mas de forma que ele entenda que é o prompt, não um arquivo pra analisar
        cmd = [
            "kimi",
            "--print",
            "--quiet",
            "--prompt", prompt
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        response = result.stdout
        tokens_in = len(prompt) // 4
        tokens_out = len(response) // 4
        
        return response, tokens_in, tokens_out
        
    except subprocess.TimeoutExpired:
        return "Erro: Timeout ao chamar agente", len(prompt)//4, 0
    except Exception as e:
        return f"Erro: {e}", len(prompt)//4, 0
    finally:
        if temp_prompt.exists():
            temp_prompt.unlink()

def execute_loop_python(loop_code: str, agent_slug: str, task: str, max_iterations: int = 20):
    """Executa um loop usando Python puro ao invés do bash script"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_DIR / f"{loop_code}_{timestamp}.log"
    
    print(f"🚀 Executando loop {loop_code} (Python)...")
    print(f"   Agente: {agent_slug}")
    print(f"   Tarefa: {task[:50]}...")
    
    iteration = 0
    history = "[Nenhuma iteração anterior - primeira execução]"
    completed = False
    total_tokens_in = 0
    total_tokens_out = 0
    
    with open(log_file, 'w') as log_f:
        log_f.write(f"# Ralph Loop - {loop_code}\n")
        log_f.write(f"Agente: {agent_slug}\n")
        log_f.write(f"Tarefa: {task}\n")
        log_f.write(f"Iniciado: {datetime.now().isoformat()}\n\n")
        
        while iteration < max_iterations and not completed:
            iteration += 1
            print(f"\n🔄 Iteração {iteration}/{max_iterations}")
            
            # Construir prompt
            prompt = build_prompt(agent_slug, task, history, iteration)
            
            # Logar prompt
            log_f.write(f"\n{'='*60}\n")
            log_f.write(f"ITERAÇÃO {iteration}\n")
            log_f.write(f"{'='*60}\n\n")
            log_f.write("PROMPT:\n")
            log_f.write(prompt[:500] + "...\n\n")
            
            # Chamar agente
            start_time = time.time()
            response, tokens_in, tokens_out = call_agent(prompt)
            duration = time.time() - start_time
            
            total_tokens_in += tokens_in
            total_tokens_out += tokens_out
            
            # Logar resposta
            log_f.write("RESPOSTA:\n")
            log_f.write(response[:1000] + "...\n\n")
            log_f.write(f"Duração: {duration:.1f}s | Tokens: {tokens_in} in / {tokens_out} out\n\n")
            
            # Logar no banco
            log_iteration(
                loop_code=loop_code,
                iteration=iteration,
                prompt_summary=prompt[:200],
                response_summary=response[:500],
                tokens_in=tokens_in,
                tokens_out=tokens_out
            )
            
            print(f"   ✅ Iteração {iteration} completa em {duration:.1f}s")
            print(f"   📊 Tokens: {tokens_in} in / {tokens_out} out")
            
            # Verificar se completou
            if "<RALPH_COMPLETE>" in response:
                print(f"   🎉 TAREFA COMPLETADA!")
                completed = True
                
                # Salvar resultado
                result_path = RESULTS_DIR / f"{loop_code}_{timestamp}_COMPLETED.md"
                result_path.write_text(f"""# Resultado Ralph Loop - {loop_code}

**Status:** ✅ COMPLETED
**Agente:** {agent_slug}
**Tarefa:** {task}
**Iterações:** {iteration}/{max_iterations}
**Duração:** {duration:.1f}s

## Resumo
- Total tokens in: {total_tokens_in}
- Total tokens out: {total_tokens_out}

## Resposta Final

{response}
""")
                
                # Completar no banco
                complete_loop(loop_code, response, success=True)
                
            else:
                # Atualizar histórico
                history = f"Iteração {iteration} ({duration:.1f}s, {tokens_in}/{tokens_out} tokens): {response[:150]}..."
        
        if not completed:
            print(f"\n⏹️  MAX ITERATIONS ({max_iterations}) atingido sem completion")
            
            # Salvar resultado incompleto
            result_path = RESULTS_DIR / f"{loop_code}_{timestamp}_INCOMPLETE.md"
            result_path.write_text(f"# Loop Incompleto - {loop_code}\n\nMáximo de iterações atingido.")
            
            # Completar no banco como falha
            complete_loop(loop_code, "Máximo de iterações atingido", success=False)
    
    print(f"\n🏁 Loop {loop_code} finalizado")
    print(f"   Log: {log_file}")

def main():
    """Worker principal - verifica e executa loops pendentes"""
    
    print("🔍 Verificando loops pendentes...")
    
    # Buscar loops ativos (running mas sem iterações)
    loops = get_active_loops()
    
    if not loops:
        print("✅ Nenhum loop pendente")
        return
    
    print(f"📋 {len(loops)} loop(s) encontrado(s)")
    
    for loop in loops:
        loop_code = loop['loop_code']
        current_iter = loop.get('current_iteration', 0)
        
        # Se ainda está na iteração 0, executar diretamente
        if current_iter == 0:
            print(f"\n⏳ Loop {loop_code} precisa ser iniciado")
            
            try:
                execute_loop_python(
                    loop_code=loop_code,
                    agent_slug=loop['agent_slug'],
                    task=loop['task_description'],
                    max_iterations=loop.get('max_iterations', 20)
                )
                
            except Exception as e:
                print(f"   ❌ Erro ao executar loop: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"\n✅ Loop {loop_code} já está em execução (iteração {current_iter})")
    
    print(f"\n🏁 Worker concluído")

if __name__ == '__main__':
    main()
