#!/usr/bin/env python3
"""
Ralph Swarm CLI - Interface de linha de comando
Uso simples: ralph-swarm "sua tarefa aqui"
"""

import sys
import json
import requests
from pathlib import Path

# Configuração
API_BASE = "http://localhost:3003/api/swarm"

def post_task(task: str, agents=None):
    """Posta uma tarefa no swarm"""
    if agents is None:
        agents = ['scout', 'max', 'maya']
    
    try:
        resp = requests.post(
            f"{API_BASE}/orchestrate",
            json={"task": task, "agents": agents},
            timeout=60
        )
        data = resp.json()
        
        if 'error' in data:
            print(f"❌ Erro: {data['error']}")
            return None
        
        return data
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return None

def list_channels():
    """Lista canais do swarm"""
    try:
        resp = requests.get(f"{API_BASE}/channels", timeout=10)
        data = resp.json()
        
        print("📺 Canais disponíveis:")
        for ch in data.get('channels', []):
            print(f"   #{ch['name']} - {ch.get('message_count', 0)} msgs")
    except Exception as e:
        print(f"❌ Erro: {e}")

def list_agents():
    """Lista agents do swarm"""
    try:
        resp = requests.get(f"{API_BASE}/agents", timeout=10)
        data = resp.json()
        
        print("🤖 Agents disponíveis:")
        for agent in data.get('agents', []):
            status_emoji = "🟢" if agent.get('status') == 'idle' else "🔴"
            print(f"   {status_emoji} {agent['avatar_emoji']} {agent['name']} ({agent['role']}) - {agent['model_tier']}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def read_channel(channel: str, limit: int = 10):
    """Lê mensagens de um canal"""
    try:
        resp = requests.get(
            f"{API_BASE}/channels/{channel}/messages?limit={limit}",
            timeout=10
        )
        data = resp.json()
        
        print(f"📨 Mensagens em #{channel}:")
        for msg in reversed(data.get('messages', [])):
            author = msg.get('author_id', 'unknown')
            content = msg.get('content', '')[:80]
            print(f"   [{author}] {content}...")
    except Exception as e:
        print(f"❌ Erro: {e}")

def show_dashboard():
    """Mostra dashboard do swarm"""
    try:
        resp = requests.get(f"{API_BASE}/dashboard", timeout=10)
        data = resp.json()
        
        print("📊 Ralph Swarm Dashboard")
        print("=" * 50)
        print(f"\n📈 Hoje:")
        print(f"   Tasks: {data.get('today', {}).get('tasks', 0)}")
        print(f"   Completadas: {data.get('today', {}).get('completed', 0)}")
        
        agents = data.get('agents', {})
        print(f"\n🤖 Agents: {agents.get('total', 0)} total")
        print(f"   🟢 Disponíveis: {agents.get('active', 0)}")
        print(f"   🔴 Ocupados: {agents.get('busy', 0)}")
        
        print(f"\n📋 Tasks: {data.get('active_tasks', 0)} ativas")
        print(f"   ⏳ Pendentes: {data.get('pending_tasks', 0)}")
        
        print(f"\n📺 Canais mais ativos:")
        for ch in data.get('channels', [])[:5]:
            print(f"   #{ch['name']}: {ch.get('message_count', 0)} msgs")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def show_help():
    """Mostra ajuda"""
    print("""🐝 Ralph Swarm CLI

Uso:
  ralph-swarm "sua tarefa aqui"     # Orquestra uma tarefa
  ralph-swarm --channels             # Lista canais
  ralph-swarm --agents               # Lista agents
  ralph-swarm --read #orders         # Lê mensagens de um canal
  ralph-swarm --dashboard            # Mostra dashboard
  ralph-swarm --help                 # Mostra esta ajuda

Exemplos:
  ralph-swarm "Research concorrentes de SaaS"
  ralph-swarm "Criar landing page para produto X"
  ralph-swarm "Escrever copy para campanha Y"
""")

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1]
    
    # Flags
    if command in ['--help', '-h']:
        show_help()
    
    elif command == '--channels':
        list_channels()
    
    elif command == '--agents':
        list_agents()
    
    elif command == '--dashboard':
        show_dashboard()
    
    elif command == '--read':
        if len(sys.argv) < 3:
            print("❌ Especifique o canal: ralph-swarm --read #orders")
            return
        channel = sys.argv[2].lstrip('#')
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        read_channel(channel, limit)
    
    else:
        # Tarefa direta
        task = ' '.join(sys.argv[1:])
        print(f"🐝 Enviando tarefa: {task}")
        print("⏳ Processando...\n")
        
        result = post_task(task)
        
        if result:
            print(f"✅ Task {result['task_code']} completada!")
            print(f"\n📋 Plano:")
            print(result['plan'][:300] + "..." if len(result['plan']) > 300 else result['plan'])
            
            print(f"\n📦 Síntese final:")
            print(result['synthesis'][:500] + "..." if len(result['synthesis']) > 500 else result['synthesis'])

if __name__ == '__main__':
    main()
