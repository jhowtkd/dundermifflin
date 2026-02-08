#!/usr/bin/env python3
"""
Script para criar uma missão de teste no Dunder Mifflin
"""

import requests
import json

CONVEX_URL = "https://cautious-puffin-441.convex.cloud"

def create_test_mission():
    """Cria uma proposta de missão de teste"""
    
    # Primeiro, busca o agente Quill
    print("🔍 Buscando agentes...")
    resp = requests.post(
        f"{CONVEX_URL}/api/agents/listAgents",
        json={"args": {}},
        headers={"Content-Type": "application/json"}
    )
    
    if resp.status_code != 200:
        print(f"❌ Erro ao buscar agentes: {resp.status_code}")
        return
    
    agents = resp.json()
    
    # Encontra o Quill
    quill = None
    for agent in agents:
        if agent.get("slug") == "quill":
            quill = agent
            break
    
    if not quill:
        print("❌ Agente Quill não encontrado")
        return
    
    quill_id = quill.get("_id")
    print(f"✅ Encontrado Quill: {quill.get('name')} ({quill_id})")
    
    # Cria proposta
    print("\n📝 Criando proposta de missão...")
    proposal_data = {
        "args": {
            "agentId": quill_id,
            "title": "🚀 Missão de Teste - Primeiro Post",
            "description": "Criar um post para LinkedIn sobre como agentes de IA podem aumentar a produtividade no trabalho remoto. O post deve ter 150-200 palavras e incluir hashtags relevantes.",
            "missionType": "content",
            "priority": 8
        }
    }
    
    resp = requests.post(
        f"{CONVEX_URL}/api/agents/createProposal",
        json=proposal_data,
        headers={"Content-Type": "application/json"}
    )
    
    if resp.status_code == 200:
        result = resp.json()
        print(f"✅ Proposta criada com sucesso!")
        print(f"🆔 ID: {result}")
        
        # Aprova a proposta automaticamente
        print("\n✅ Aprovando proposta...")
        approve_data = {
            "args": {
                "id": result,
                "status": "accepted",
                "notes": "Aprovada automaticamente para teste"
            }
        }
        
        resp2 = requests.post(
            f"{CONVEX_URL}/api/agents/reviewProposal",
            json=approve_data,
            headers={"Content-Type": "application/json"}
        )
        
        if resp2.status_code == 200:
            print("✅ Proposta aprovada! Missão criada!")
            print("\n📊 Próximos passos:")
            print("   1. Acesse: https://dunder-mifflin-three.vercel.app")
            print("   2. Clique na tab 'Proposals' para ver a proposta")
            print("   3. Clique na tab 'Missions' para ver a missão")
            print("   4. O worker vai processar automaticamente")
        else:
            print(f"❌ Erro ao aprovar: {resp2.status_code}")
    else:
        print(f"❌ Erro ao criar proposta: {resp2.status_code}")
        print(resp.text)

if __name__ == "__main__":
    create_test_mission()
