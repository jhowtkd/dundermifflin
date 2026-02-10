#!/usr/bin/env python3
"""
Ralph Loop - Integração Telegram
Permite iniciar loops via comandos do Telegram
"""

import sys
import os
import json
import re

# Adicionar path do projeto
sys.path.insert(0, os.path.expanduser('~/.openclaw/workspace/projects/dunder-mifflin'))

from ralph_loop import create_loop

# Mapeamento de agentes
AGENT_ALIASES = {
    'dev': 'o-dev',
    'developer': 'o-dev',
    'desenvolvedor': 'o-dev',
    'code': 'o-dev',
    'codigo': 'o-dev',
    'mkt': 'o-marketeiro',
    'marketeiro': 'o-marketeiro',
    'marketing': 'o-marketeiro',
    'copy': 'o-marketeiro',
    'exec': 'o-executivo',
    'executivo': 'o-executivo',
    'gestao': 'o-executivo',
    'manager': 'o-executivo'
}

def parse_command(text):
    """Parseia comando /ralph do Telegram"""
    # Padrões aceitos:
    # /ralph dev criar api
    # /ralph marketeiro "escrever copy"
    # ralph executivo analisar métricas
    
    # Remover comando /ralph ou ralph
    text = re.sub(r'^/?ralph\s+', '', text, flags=re.IGNORECASE).strip()
    
    if not text:
        return None, None
    
    # Primeira palavra é o agente
    parts = text.split(None, 1)
    agent_input = parts[0].lower()
    task = parts[1] if len(parts) > 1 else ""
    
    # Mapear agente
    agent_slug = AGENT_ALIASES.get(agent_input)
    
    if not agent_slug:
        return None, f"Agente '{agent_input}' não reconhecido. Use: dev, marketeiro ou executivo"
    
    if not task:
        return None, "Tarefa não especificada. Ex: /ralph dev criar API"
    
    return agent_slug, task

def start_loop_from_telegram(text, user_id=None):
    """Inicia um loop a partir de comando Telegram"""
    
    agent_slug, task = parse_command(text)
    
    if agent_slug is None:
        return {
            "success": False,
            "error": task  # task contém mensagem de erro
        }
    
    try:
        # Criar loop
        loop_code = create_loop(agent_slug, task, max_iterations=20)
        
        # Nome amigável do agente
        agent_names = {
            'o-dev': '👨‍💻 O Dev',
            'o-marketeiro': '📢 O Marketeiro',
            'o-executivo': '💼 O Executivo'
        }
        
        return {
            "success": True,
            "loop_code": loop_code,
            "agent": agent_names.get(agent_slug, agent_slug),
            "task": task,
            "dashboard_url": f"http://clawd-b450mhp:8888/ralph-dashboard.html?loop={loop_code}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def format_response(result):
    """Formata resposta para Telegram"""
    
    if not result["success"]:
        return f"❌ **Erro:** {result['error']}\n\n💡 **Uso:** `/ralph <agente> <tarefa>`\nEx: `/ralph dev criar API JWT`"
    
    return f"""🚀 **Ralph Loop Iniciado!**

**Código:** `{result['loop_code']}`
**Agente:** {result['agent']}
**Tarefa:** {result['task'][:100]}{'...' if len(result['task']) > 100 else ''}

📊 [Ver no Dashboard]({result['dashboard_url']})

⏳ O loop está rodando em background. Você receberá uma notificação quando completar.
"""

def main():
    """Modo CLI para testes"""
    if len(sys.argv) < 2:
        print("Uso: python ralph_telegram.py '\u003ccomando\u003e'")
        print("Ex: python ralph_telegram.py 'ralph dev criar API'")
        sys.exit(1)
    
    command = ' '.join(sys.argv[1:])
    result = start_loop_from_telegram(command)
    print(format_response(result))

if __name__ == '__main__':
    main()
