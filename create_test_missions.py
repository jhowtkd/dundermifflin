#!/usr/bin/env python3
"""
Cria missões de teste para todos os serviços do Dunder Mifflin
"""

import requests
import json

API_BASE = "http://100.94.223.52:3003/api"

def get_agent_id_by_slug(slug):
    """Busca o ID do agente pelo slug"""
    try:
        res = requests.get(f"{API_BASE}/agents", timeout=10)
        if res.status_code == 200:
            agents = res.json().get("agents", [])
            for agent in agents:
                if agent.get("slug") == slug:
                    return agent.get("id")
    except Exception as e:
        print(f"⚠️  Erro ao buscar agente {slug}: {e}")
    return None

def create_test_missions():
    """Cria 5 missões de teste - uma para cada tipo de conteúdo"""
    
    missions = [
        {
            "title": "📝 TESTE: Post de Blog - Automação com IA",
            "description": "Criar um post de blog completo e bem formatado sobre automação de marketing usando agentes de IA. O post deve ter introdução, 3 seções principais com exemplos práticos, e conclusão com call-to-action.",
            "agent_slug": "content-creator",
            "content_type": "blog_post"
        },
        {
            "title": "🐦 TESTE: Thread Twitter - 5 Mitos sobre IA",
            "description": "Criar uma thread de 5 tweets sobre os mitos mais comuns sobre Inteligência Artificial no trabalho. Cada tweet deve ser engajante, com hashtag relevante, e se conectar ao próximo.",
            "agent_slug": "twitter-engager",
            "content_type": "twitter_thread"
        },
        {
            "title": "🎵 TESTE: Roteiro TikTok - Dicas de Produtividade",
            "description": "Criar 3 roteiros curtos para TikTok sobre produtividade no trabalho remoto. Cada roteiro deve ter: gancho nos primeiros 3 segundos, dica prática, call-to-action. Tom jovem e descontraído.",
            "agent_slug": "tiktok-strategist",
            "content_type": "tiktok_script"
        },
        {
            "title": "💼 TESTE: LinkedIn Post - Case de Sucesso",
            "description": "Criar um post profissional para LinkedIn sobre um case de sucesso de implementação de automação. Estrutura: problema → solução → resultados (com números) → lição aprendida. Tom consultivo e autoridade.",
            "agent_slug": "content-creator",
            "content_type": "linkedin_post"
        },
        {
            "title": "📧 TESTE: Email Newsletter - Lançamento de Curso",
            "description": "Criar um email de newsletter para lançamento de um curso sobre Agentes AI. Estrutura: assunto chamativo, saudação personalizada, história de origem, benefícios do curso (bullet points), prova social, oferta com urgência, call-to-action claro.",
            "agent_slug": "content-creator",
            "content_type": "email_newsletter"
        }
    ]
    
    created = []
    for i, mission in enumerate(missions, 1):
        try:
            # Busca o ID do agente
            agent_id = get_agent_id_by_slug(mission["agent_slug"])
            if not agent_id:
                print(f"⚠️  Agente {mission['agent_slug']} não encontrado, pulando...")
                continue
            
            # Criar proposta de missão
            proposal_data = {
                "agentId": agent_id,
                "title": mission["title"],
                "description": mission["description"],
                "missionType": mission["content_type"],
                "priority": 5
            }
            
            res = requests.post(f"{API_BASE}/proposals", json=proposal_data, timeout=30)
            if res.status_code == 201 or res.status_code == 200:
                data = res.json()
                proposal_id = data.get("id") or data.get("proposal_id")
                
                # Aprovar automaticamente
                approve_res = requests.post(
                    f"{API_BASE}/proposals/{proposal_id}/approve",
                    json={},
                    timeout=30
                )
                
                if approve_res.status_code == 200:
                    print(f"✅ Missão {i}/5 criada e aprovada: {mission['title'][:40]}...")
                    created.append({
                        "id": proposal_id,
                        "title": mission["title"],
                        "agent": mission["agent_slug"]
                    })
                else:
                    print(f"⚠️  Missão {i} criada mas falhou ao aprovar: {approve_res.status_code}")
            else:
                print(f"❌ Falha ao criar missão {i}: {res.status_code} - {res.text[:100]}")
                
        except Exception as e:
            print(f"❌ Erro na missão {i}: {e}")
    
    print(f"\n🎉 {len(created)}/5 missões de teste criadas com sucesso!")
    return created

if __name__ == "__main__":
    print("🚀 Criando missões de teste para todos os serviços...\n")
    missions = create_test_missions()
    
    print("\n📋 Resumo:")
    for m in missions:
        print(f"  • {m['title'][:50]}... (Agente: {m['agent']})")
    
    print("\n⏳ As missões serão processadas automaticamente pelo Worker.")
    print("📊 Acompanhe em: http://100.94.223.52:8889/history.html")
