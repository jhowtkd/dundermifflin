#!/usr/bin/env python3
"""
Dunder Mifflin Worker v2.0 - SQLite Edition
Executa missões localmente sem dependência do Convex.
"""

import os
import sys
import time
import json
import uuid
import logging
import random
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Constantes
KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")
WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"
STUDIO_DIR = WORKSPACE_DIR / "studio" / "projects"
DB_PATH = Path(__file__).parent / "dunder_mifflin.db"

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("dm-worker-v2")

# Mock data compartilhada para conteúdo
def _get_mock_carousel_data():
    """Retorna dados mockados de carrossel - extraído para reutilização"""
    return {
        "slides": [
            {"number": 1, "title": "A Era Vargas", "content": "Período de 1930-1945 que transformou o Brasil\n• Revolução de 1930\n• Estado Novo\n• Nacionalismo", "design_notes": "Bandeira do Brasil, cores verde e amarelo"},
            {"number": 2, "title": "Revolução de 1930", "content": "Fim da República Velha\n• Getúlio Vargas no poder\n• Mudança política profunda\n• Urbanização acelerada", "design_notes": "Ícone de revolução, cores fortes"},
            {"number": 3, "title": "Estado Novo (1937-1945)", "content": "Regime autoritário\n• Censura à imprensa\n• CLT criada\n• Industrialização", "design_notes": "Ícone de fábrica, trabalhadores"},
            {"number": 4, "title": "Legado Econômico", "content": "• Nacionalização do petróleo\n• Siderurgia (CSN)\n• Eletrobrás\n• Bases da indústria", "design_notes": "Ícones industriais, gráficos"},
            {"number": 5, "title": "Legado Social", "content": "• CLT e direitos trabalhistas\n• Férias pagas\n• 13º salário\n• Proteção ao trabalhador", "design_notes": "Ícone de família, trabalhadores"},
            {"number": 6, "title": "Lições para Hoje", "content": "• Nacionalismo estratégico\n• Investimento em infra\n• Direitos trabalhistas\n• Educação e cultura", "design_notes": "Ícone de livro, futuro"},
            {"number": 7, "title": "O Fim da Era", "content": "1945: Ditadura cai\n• Vargas volta democraticamente (1951)\n• Suicídio em 1954\n• Legado controverso", "design_notes": "Ponto final, reflexão"}
        ],
        "hashtags": ["#EraVargas", "#HistóriaBrasil", "#GetúlioVargas", "#História"],
        "cta": "Qual aspecto da Era Vargas você acha mais relevante hoje? Comente! 👇"
    }

# Import local db module
sys.path.insert(0, str(Path(__file__).parent))
from db import (
    init_db, seed_agents, get_agent_by_slug, list_missions, 
    get_mission, start_mission, complete_mission, add_event,
    create_proposal, approve_proposal, get_dashboard_stats
)

# Import orchestrator
from orchestrator import (
    MasterAgent, OrchestrationSession,
    get_pending_plans, get_approved_plans,
    approve_plan, reject_plan
)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("dm-worker-v2")

class DunderMifflinWorkerV2:
    def __init__(self):
        self.running = True
        self.iteration = 0
        self.master_agent = MasterAgent()
        self.active_sessions = {}  # session_code -> OrchestrationSession
        logger.info("🚀 Dunder Mifflin Worker v2.0 iniciado (SQLite)")
        logger.info(f"🎬 Master Agent: {self.master_agent.AGENT_SLUG}")
        logger.info(f"   Agentes disponíveis: {len(self.master_agent.available_agents)}")
    
    def get_pending_missions(self):
        """Busca missões aprovadas (status approved)"""
        return list_missions(status="approved")
    
    def get_running_missions(self):
        """Busca missões em execução"""
        return list_missions(status="running")
    
    def execute_mission(self, mission):
        """Executa uma missão completa"""
        mission_id = mission["id"]
        title = mission["title"]
        mission_type = mission.get("mission_type", "general")
        agent_slug = mission.get("agent_slug", "unknown")
        
        logger.info(f"▶️ Iniciando missão: {title}")
        logger.info(f"   Tipo: {mission_type} | Agente: {agent_slug} | ID: {mission_id}")
        
        # Marca como running
        start_mission(mission_id)
        add_event("mission_started", f"Missão iniciada: {title}", mission_id=mission_id)
        
        try:
            # Executa baseado no tipo
            if mission_type == "content":
                result = self._execute_content_mission(mission)
            elif mission_type == "research":
                result = self._execute_research_mission(mission)
            elif mission_type == "social":
                result = self._execute_social_mission(mission)
            elif mission_type == "carousel":
                result = self._execute_carousel_mission(mission)
            else:
                result = self._execute_general_mission(mission)
            
            # Completa com sucesso
            complete_mission(mission_id, "succeeded", result)
            add_event("mission_completed", f"Missão completada: {title}", 
                     payload=result, mission_id=mission_id)
            logger.info(f"✅ Missão completada: {title}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Missão falhou: {error_msg}")
            complete_mission(mission_id, "failed", error_message=error_msg)
            add_event("mission_failed", f"Missão falhou: {title}", 
                     description=error_msg, severity="error", mission_id=mission_id)
            return False
    
    def _call_llm(self, prompt, agent_id="quill"):
        """Retorna conteúdo mockado baseado no tipo de prompt"""
        # Detecta tipo de conteúdo pelo prompt
        prompt_lower = prompt.lower()
        
        if "social" in prompt_lower or "instagram" in prompt_lower or "semana" in prompt_lower:
            # Planejamento completo de social media
            return json.dumps({
                "tema_semana": "Biomecânica do Movimento: Entenda seu corpo em ação",
                "posts": [
                    {
                        "dia": "Segunda",
                        "tipo": "carousel",
                        "titulo": "O que é Biomecânica? 🤔",
                        "legenda": "Você sabe como seu corpo se move?\n\nA biomecânica estuda as forças que atuam no corpo humano durante o movimento. É a ciência por trás de cada passo, salto e levantamento.\n\n💡 Nesta semana, vamos descomplicar a biomecânica e mostrar como ela pode melhorar sua performance e prevenir lesões.\n\n👉 Salva esse post para acompanhar a série completa!\n\nQual aspecto do movimento humano você mais se interessa? Comenta aqui! 👇",
                        "hashtags": ["#Biomecanica", "#MovimentoHumano", "#Fisioterapia", "#Performance"],
                        "conteudo_visual": "Carrossel com 5 slides: (1) Capa 'O que é Biomecânica?', (2) Definição simples com ícone de corpo humano, (3) Exemplo do dia a dia - caminhada, (4) Benefícios para atletas, (5) CTA 'Segue para mais'",
                        "hora_postagem": "19:00"
                    },
                    {
                        "dia": "Terça", 
                        "tipo": "reel",
                        "titulo": "3 Erros Biomecânicos no Agachamento ⚠️",
                        "legenda": "Agachar errado pode causar lesões sérias! 🚨\n\nNo vídeo de hoje mostro os 3 erros mais comuns que vejo na academia e como corrigi-los em segundos.\n\n✅ Joelhos cedendo para dentro\n✅ Elevação excessiva dos calcanhares\n✅ Curvatura lombar excessiva\n\nQual desses erros você comete? Me conta! 👇\n\n💾 Salva para revisar antes do próximo treino",
                        "hashtags": ["#Agachamento", "#Treino", "#Academia", "#Biomecanica"],
                        "conteudo_visual": "Vídeo curto (30s) mostrando os 3 erros com setas indicativas e depois a forma correta. Split screen comparando erro vs correto.",
                        "hora_postagem": "12:00"
                    },
                    {
                        "dia": "Quarta",
                        "tipo": "carousel", 
                        "titulo": "Cadeia Cinética: Tudo está conectado 🔗",
                        "legenda": "Dor no ombro? O problema pode estar no quadril! 🧐\n\nO corpo humano é uma cadeia de movimento. Quando um elo falha, toda a corrente sofre.\n\n📊 Neste carrossel você vai entender:\n→ O que é cadeia cinética\n→ Como o pé afeta o joelho\n→ Por que a postura importa\n→ Exercícios para integrar o corpo\n\n🧠 Conhecimento é poder! Quanto mais você entende seu corpo, melhor você treina.\n\nCompartilha com aquele amigo que precisa ver isso! 💪",
                        "hashtags": ["#CadeiaCinetica", "#CorpoIntegrado", "#Postura", "#Saude"],
                        "conteudo_visual": "Carrossel educativo com ilustrações mostrando a conexão pé-joelho-quadril-coluna. Setas indicando o fluxo de força.",
                        "hora_postagem": "19:00"
                    },
                    {
                        "dia": "Quinta",
                        "tipo": "single",
                        "titulo": "Pergunte-me qualquer coisa sobre Biomecânica! 💬",
                        "legenda": "Caixa de perguntas aberta! 📦\n\nQualquer dúvida sobre biomecânica, movimento, lesões ou performance é bem-vinda.\n\n🔥 As melhores perguntas vão virar conteúdo nos próximos dias!\n\nNão seja tímido - pode perguntar sobre:\n• Lesões específicas\n• Exercícios corretos\n• Avaliação postural\n• Performance esportiva\n• Qualquer coisa sobre movimento!\n\nBora interagir? 👇",
                        "hashtags": ["#PergunteMe", "#FAQ", "#Duvidas", "#Biomecanica"],
                        "conteudo_visual": "Imagem com fundo gradiente e texto 'Pergunte-me qualquer coisa' centralizado. Ícone de caixa de perguntas.",
                        "hora_postagem": "15:00"
                    },
                    {
                        "dia": "Sexta",
                        "tipo": "carousel",
                        "titulo": "Checklist Biomecânico da Semana ✅",
                        "legenda": "Resumo da semana + checklist para você aplicar! 📝\n\nDepois de 5 dias aprendendo sobre biomecânica, chegou a hora de colocar em prática.\n\n✅ Meu checklist biomecânico:\n1️⃣ Observo minha postura durante o dia\n2️⃣ Aqueço antes de treinar\n3️⃣ Presto atenção na técnica, não só na carga\n4️⃣ Durmo bem para recuperação\n5️⃣ Escuto meu corpo quando ele fala\n\n💪 Pequenas mudanças criam grandes resultados. Qual dessas você vai começar hoje?\n\n🎯 Comprometa-se nos comentários! 👇",
                        "hashtags": ["#Checklist", "#Habitos", "#Saude", "#BemEstar"],
                        "conteudo_visual": "Carrossel com design de checklist. Slide 1: Capa 'Checklist da Semana', Slides 2-6: Cada item do checklist com ícone ilustrativo.",
                        "hora_postagem": "19:00"
                    }
                ],
                "resumo_estrategia": "Estratégia de conteúdo educativo mixando carrosséis informativos, reel dinâmico e interação direta. Foco em engajamento através de perguntas e CTAs claros. Variação de horários para testar alcance.",
                "materiais_necessarios": [
                    "Imagens de corpo humano/anatomia",
                    "Ícones de exercícios",
                    "Vídeo do agachamento (stock ou gravado)",
                    "Templates de carrossel",
                    "Stickers e elementos gráficos"
                ]
            }, ensure_ascii=False)
        
        elif "carrossel" in prompt_lower:
            return json.dumps(_get_mock_carousel_data(), ensure_ascii=False)
        
        else:
            return f"Conteúdo gerado para: {prompt[:100]}...\n\nEste é um conteúdo de exemplo gerado pelo sistema."
    
    def _generate_mock_content(self, prompt):
        """Gera conteúdo mockado quando LLM falha"""
        if "carrossel" in prompt.lower() or "carousel" in prompt.lower():
            return json.dumps(_get_mock_carousel_data(), ensure_ascii=False)
        return f"Conteúdo gerado para: {prompt[:100]}..."
    
    def _execute_content_mission(self, mission):
        """Executa missão de conteúdo (texto/posts)"""
        logger.info("   📝 Gerando conteúdo com Quill...")
        
        title = mission.get("title", "")
        description = mission.get("description", "")
        
        prompt = f"""Você é Quill, um escritor especializado em conteúdo para LinkedIn.

Tarefa: {title}
Descrição: {description}

Gere um conteúdo profissional e envolvente. Use:
- Tom conversacional mas profissional
- Parágrafos curtos (2-3 linhas)
- Storytelling quando apropriado
- Call-to-action no final
- Hashtags relevantes

Conteúdo:"""
        
        content = self._call_llm(prompt, agent_id="quill")
        
        result = {
            "type": "content",
            "title": title,
            "content": content,
            "word_count": len(content.split()),
            "generated_at": datetime.now().isoformat()
        }
        
        logger.info(f"   ✅ Conteúdo gerado: {result['word_count']} palavras")
        return result
    
    def _execute_carousel_mission(self, mission):
        """Executa missão de carrossel LinkedIn"""
        logger.info("   🎠 Gerando carrossel...")
        
        title = mission.get("title", "")
        description = mission.get("description", "")
        
        prompt = f"""Você é um designer de conteúdo especializado em carrosséis para LinkedIn.

Tarefa: {title}
Descrição: {description}

Crie um carrossel com 5-7 slides seguindo este formato JSON:
{{
  "slides": [
    {{
      "number": 1,
      "title": "Título do slide",
      "content": "Conteúdo principal (bullet points ou texto curto)",
      "design_notes": "Sugestões visuais (cores, ícones, layout)"
    }}
  ],
  "hashtags": ["#hashtag1", "#hashtag2"],
  "cta": "Call to action final"
}}

Regras:
- Slide 1: Hook forte (problema ou curiosidade)
- Slides 2-5: Conteúdo educativo com bullets
- Slide 6: Exemplo prático ou caso
- Slide 7: CTA e hashtags
- Texto curto e direto (máx 40 palavras por slide)

Retorne APENAS o JSON válido:"""
        
        response = self._call_llm(prompt, agent_id="quill")
        
        # Extrai JSON da resposta
        try:
            # Tenta encontrar JSON entre chaves
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                carousel_data = json.loads(response[start:end])
            else:
                carousel_data = json.loads(response)
        except json.JSONDecodeError:
            # Fallback: cria estrutura simples
            carousel_data = {
                "slides": [
                    {"number": 1, "title": title, "content": response[:200] + "..."}
                ],
                "hashtags": ["#conteúdo", "#linkedin"],
                "cta": "Siga para mais conteúdo!"
            }
        
        result = {
            "type": "carousel",
            "title": title,
            "carousel": carousel_data,
            "slide_count": len(carousel_data.get("slides", [])),
            "generated_at": datetime.now().isoformat()
        }
        
        logger.info(f"   ✅ Carrossel gerado: {result['slide_count']} slides")
        
        # Salva arquivo local
        self._save_carousel_file(title, carousel_data)
        
        return result
    
    def _save_carousel_file(self, title, carousel_data):
        """Salva carrossel em arquivo HTML na pasta studio"""
        # Cria pasta se não existir
        carousel_dir = STUDIO_DIR / "dunder_mifflin" / "carousels"
        carousel_dir.mkdir(parents=True, exist_ok=True)
        
        # Nome do arquivo
        date_str = datetime.now().strftime("%Y%m%d")
        safe_title = "".join(c if c.isalnum() else "_" for c in title.lower())[:30]
        filename = f"{date_str}_carousel_{safe_title}.html"
        filepath = carousel_dir / filename
        
        # Gera HTML
        slides = carousel_data.get("slides", [])
        hashtags = carousel_data.get("hashtags", [])
        cta = carousel_data.get("cta", "")
        
        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }}
        .carousel {{ max-width: 600px; margin: 0 auto; }}
        .slide {{ background: white; border-radius: 12px; padding: 30px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .slide-number {{ color: #666; font-size: 14px; margin-bottom: 10px; }}
        .slide-title {{ font-size: 24px; font-weight: bold; color: #1a1a1a; margin-bottom: 15px; }}
        .slide-content {{ font-size: 16px; line-height: 1.6; color: #333; }}
        .slide-content ul {{ padding-left: 20px; }}
        .slide-content li {{ margin-bottom: 8px; }}
        .hashtags {{ color: #0a66c2; margin-top: 20px; }}
        .cta {{ background: #0a66c2; color: white; padding: 15px; border-radius: 8px; text-align: center; margin-top: 20px; }}
        .meta {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="carousel">
        <h1 style="text-align: center; color: #1a1a1a;">{title}</h1>
        
        {''.join([f'''
        <div class="slide">
            <div class="slide-number">Slide {s.get('number', i+1)} de {len(slides)}</div>
            <div class="slide-title">{s.get('title', '')}</div>
            <div class="slide-content">{s.get('content', '').replace(chr(10), '<br>')}</div>
        </div>
        ''' for i, s in enumerate(slides)])}
        
        <div class="cta">{cta}</div>
        <div class="hashtags">{' '.join(hashtags)}</div>
        <div class="meta">Gerado por Dunder Mifflin 🏢 | {datetime.now().strftime('%d/%m/%Y')}</div>
    </div>
</body>
</html>"""
        
        filepath.write_text(html, encoding="utf-8")
        logger.info(f"   💾 Carrossel salvo: {filepath}")
        
        return str(filepath)
    
    def _execute_research_mission(self, mission):
        """Executa missão de pesquisa"""
        logger.info("   🔍 Realizando pesquisa...")
        
        result = {
            "type": "research",
            "query": mission.get("title", ""),
            "findings": ["Research capability not fully implemented yet"],
            "completed_at": datetime.now().isoformat()
        }
        
        logger.info(f"   ✅ Pesquisa simulada")
        return result
    
    def _execute_social_mission(self, mission):
        """Executa missão de social media - Gera planejamento completo"""
        logger.info("   📱 Gerando planejamento de social media...")
        
        title = mission.get("title", "")
        description = mission.get("description", "")
        
        prompt = f"""Você é um especialista em social media e criação de conteúdo para Instagram.

TAREFA: {title}
DESCRIÇÃO: {description}

Crie um planejamento COMPLETO para uma semana de posts no Instagram.

Retorne APENAS um JSON válido seguindo este formato:
{{
  "tema_semana": "Tema principal da semana (1 frase)",
  "posts": [
    {{
      "dia": "Segunda",
      "tipo": "carousel|single|reel|story",
      "titulo": "Título do post",
      "legenda": "Legenda completa com storytelling, emojis e CTA (150-300 palavras)",
      "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#hashtag4", "#hashtag5"],
      "conteudo_visual": "Descrição do que deve ter na imagem/carrossel",
      "hora_postagem": "19:00"
    }}
  ],
  "resumo_estrategia": "Breve explicação da estratégia da semana (2-3 frases)",
  "materiais_necessarios": ["item 1", "item 2", "item 3"]
}}

REGRAS:
- Crie 5 posts (segunda a sexta)
- Varie os tipos: carrossel educativo, post único inspiracional, reel dinâmico
- Legendas devem ter storytelling e engajamento
- Hashtags devem ser estratégicas (mix de populares e nichadas)
- Horários otimizados para engajamento brasileiro
- Conteúdo alinhado com a descrição da missão"""
        
        response = self._call_llm(prompt, agent_id="quill")
        
        # Tenta extrair JSON
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                social_plan = json.loads(response[start:end])
            else:
                social_plan = json.loads(response)
            
            # Valida estrutura mínima
            if "posts" not in social_plan:
                raise ValueError("JSON não contém 'posts'")
                
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"   Erro ao parsear JSON: {e}")
            # Fallback: cria estrutura básica
            social_plan = {
                "tema_semana": title,
                "posts": [
                    {
                        "dia": "Segunda",
                        "tipo": "single",
                        "titulo": title,
                        "legenda": f"{description}\n\n{response[:500]}",
                        "hashtags": ["#instagram", "#conteudo", "#biomecanica"],
                        "conteudo_visual": "Imagem relacionada ao tema",
                        "hora_postagem": "19:00"
                    }
                ],
                "resumo_estrategia": "Planejamento gerado com conteúdo disponível",
                "materiais_necessarios": ["Imagens de apoio"]
            }
        
        # Salva o planejamento em arquivo
        self._save_social_plan_file(title, social_plan)
        
        result = {
            "type": "social",
            "tema_semana": social_plan.get("tema_semana", title),
            "total_posts": len(social_plan.get("posts", [])),
            "posts": social_plan.get("posts", []),
            "resumo_estrategia": social_plan.get("resumo_estrategia", ""),
            "materiais_necessarios": social_plan.get("materiais_necessarios", []),
            "planning_file": f"social_plans/{title.lower().replace(' ', '_')[:30]}.json",
            "generated_at": datetime.now().isoformat()
        }
        
        logger.info(f"   ✅ Planejamento gerado: {result['total_posts']} posts")
        return result
    
    def _save_social_plan_file(self, title, social_plan):
        """Salva planejamento social em arquivo"""
        # Cria pasta se não existir
        social_dir = STUDIO_DIR / "dunder_mifflin" / "social_plans"
        social_dir.mkdir(parents=True, exist_ok=True)
        
        # Nome do arquivo
        date_str = datetime.now().strftime("%Y%m%d")
        safe_title = "".join(c if c.isalnum() else "_" for c in title.lower())[:30]
        filename = f"{date_str}_social_{safe_title}.json"
        filepath = social_dir / filename
        
        # Salva JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(social_plan, f, ensure_ascii=False, indent=2)
        
        logger.info(f"   💾 Arquivo salvo: {filepath}")
    
    def _execute_general_mission(self, mission):
        """Executa missão geral"""
        logger.info("   ⚙️ Executando tarefa geral...")
        
        result = {
            "type": "general",
            "mission_title": mission.get("title", ""),
            "message": "Tarefa executada com sucesso",
            "completed_at": datetime.now().isoformat()
        }
        
        logger.info(f"   ✅ Tarefa geral completada")
        return result
    
    def run(self):
        """Loop principal"""
        logger.info("🔁 Worker iniciando loop principal")
        logger.info("⏳ Aguardando missões...")
        
        while self.running:
            try:
                self.iteration += 1
                
                # Busca missões aprovadas
                missions = self.get_pending_missions()
                
                if missions and len(missions) > 0:
                    logger.info(f"📋 {len(missions)} missão(ões) aprovada(s) encontrada(s)!")
                    
                    for mission in missions[:2]:  # Processa até 2 por vez
                        self.execute_mission(mission)
                        time.sleep(3)
                else:
                    # Heartbeat a cada 12 iterações (~1 min)
                    if self.iteration % 12 == 0:
                        logger.info("💓 Worker ativo - aguardando missões...")
                
                # Aguarda 5 segundos
                time.sleep(5)
                    
            except KeyboardInterrupt:
                logger.info("👋 Worker parado pelo usuário")
                self.running = False
            except Exception as e:
                logger.error(f"❌ Erro no loop: {e}")
                time.sleep(10)
    
    def stop(self):
        self.running = False
    
    # ============================================================
    # NOVOS MÉTODOS - ORQUESTRAÇÃO V2
    # ============================================================
    
    def check_plans_needing_creation(self):
        """Busca missões que precisam de plano (via serviço)"""
        # Por enquanto, missões do tipo 'orchestrated' precisam de plano
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT m.*, a.slug as agent_slug
            FROM missions m
            JOIN agents a ON m.agent_id = a.id
            WHERE m.status = 'approved' AND m.mission_type = 'orchestrated'
        """)
        missions = [dict(row) for row in cur.fetchall()]
        conn.close()
        return missions
    
    def create_plan_for_mission(self, mission):
        """Cria plano via Master Agent"""
        try:
            logger.info(f"📋 Criando plano para missão: {mission['title']}")
            
            # Extrai service_id dos parâmetros da missão
            params = json.loads(mission.get('parameters', '{}') or '{}')
            service_id = params.get('service_id')
            
            if not service_id:
                logger.error("   ❌ Missão sem service_id")
                return None
            
            # Cria plano via Master
            plan = self.master_agent.create_plan(
                service_id=service_id,
                title=mission['title'],
                objective=mission.get('description', mission['title']),
                input_data=params
            )
            
            logger.info(f"   ✅ Plano criado: {plan['plan_code']}")
            logger.info(f"   📊 Steps: {len(plan['steps'])}")
            logger.info(f"   ⏱️  Duração estimada: {plan['estimated_duration_minutes']} min")
            
            # Atualiza missão com plan_code
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                UPDATE missions SET parameters = ? WHERE id = ?
            """, (json.dumps({**params, 'plan_code': plan['plan_code']}), mission['id']))
            conn.commit()
            conn.close()
            
            return plan
            
        except Exception as e:
            logger.error(f"   ❌ Erro ao criar plano: {e}")
            return None
    
    def execute_approved_plans(self):
        """Executa planos aprovados"""
        # 1. Primeiro, continua planos que estão em execução
        executing_plans = self.get_executing_plans()
        if executing_plans:
            logger.info(f"🔄 {len(executing_plans)} plano(s) em execução")
            for plan in executing_plans[:1]:
                self._continue_plan_execution(plan)
            return  # Prioriza continuar execuções existentes
        
        # 2. Depois, inicia novos planos aprovados
        plans = get_approved_plans()
        if not plans:
            return
        
        logger.info(f"🎯 {len(plans)} plano(s) aprovado(s) para execução")
        
        for plan in plans[:1]:  # Executa 1 por vez
            self._start_plan_execution(plan)
    
    def get_executing_plans(self) -> List[Dict]:
        """Busca planos que estão em execução mas não completos"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # IMPORTANTE: permite converter para dict
        cur = conn.cursor()
        
        cur.execute("""
            SELECT ep.*, s.name as service_name
            FROM execution_plans ep
            JOIN services s ON ep.service_id = s.id
            WHERE ep.status = 'executing'
            AND ep.id NOT IN (
                SELECT execution_plan_id 
                FROM orchestration_sessions 
                WHERE status = 'completed'
            )
        """)
        
        plans = [dict(row) for row in cur.fetchall()]
        conn.close()
        
        for plan in plans:
            plan['planned_steps'] = json.loads(plan.get('planned_steps', '[]') or '[]')
        
        return plans
    
    def _start_plan_execution(self, plan: Dict):
        """Inicia execução de um novo plano"""
        try:
            logger.info(f"▶️ Iniciando plano: {plan['plan_code']}")
            
            # Verifica se já existe uma sessão running para esse plano
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("""
                SELECT id, session_code FROM orchestration_sessions 
                WHERE execution_plan_id = ? AND status = 'running'
                ORDER BY created_at DESC
            """, (plan['id'],))
            row = cur.fetchone()
            conn.close()
            
            if row:
                # Já existe uma sessão, carrega ela
                logger.info(f"   📂 Sessão existente encontrada: {row['session_code']}")
                from orchestrator import OrchestrationSession
                session = OrchestrationSession.load_by_id(row['id'])
            else:
                # Cria nova sessão
                session = self.master_agent.execute_approved_plan(plan['id'])
            
            self.active_sessions[session.session_code] = session
            
            # Executa steps
            self._run_session_steps(session, plan)
            
        except Exception as e:
            logger.error(f"❌ Erro ao executar plano: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def _continue_plan_execution(self, plan: Dict):
        """Continua execução de um plano em andamento"""
        try:
            logger.info(f"🔄 Continuando plano: {plan['plan_code']}")
            
            # Busca sessão existente
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("""
                SELECT id, session_code FROM orchestration_sessions 
                WHERE execution_plan_id = ? AND status = 'running'
                ORDER BY created_at DESC
            """, (plan['id'],))
            row = cur.fetchone()
            conn.close()
            
            if not row:
                logger.warning(f"   ⚠️ Sessão não encontrada para plano {plan['plan_code']}")
                # Reset status para permitir reinício
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("""
                    UPDATE execution_plans SET status = 'approved' WHERE id = ?
                """, (plan['id'],))
                conn.commit()
                conn.close()
                return
            
            # Carrega sessão existente
            from orchestrator import OrchestrationSession
            session = OrchestrationSession.load_by_id(row['id'])
            self.active_sessions[session.session_code] = session
            
            # Continua execução
            self._run_session_steps(session, plan)
            
        except Exception as e:
            logger.error(f"❌ Erro ao continuar plano: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def _run_session_steps(self, session, plan: Dict):
        """Executa os steps de uma sessão"""
        try:
            # Executa steps sequencialmente
            while not session.is_complete():
                step = session.next_step()
                if not step:
                    break
                
                logger.info(f"   ⚙️ Step {step['step_index'] + 1}/{step['total_steps']}: {step['title']}")
                
                # Simula execução do agente
                output = self._execute_agent_step(step, session)
                
                # Registra output
                quality_score = self._evaluate_quality(output)
                session.execute_step(step, output, quality_score)
                
                logger.info(f"   ✅ Output registrado (quality: {quality_score})")
                
                # Verifica loop
                if session.should_loop():
                    logger.info("   🔄 Qualidade insuficiente, repetindo step...")
                    if session.handle_loop():
                        continue
                
                time.sleep(1)  # Pausa entre steps
            
            # Finaliza
            final_output = self._aggregate_outputs(session.outputs)
            session.complete(final_output, quality_score=8)
            
            logger.info(f"✅ Plano concluído: {plan['plan_code']}")
            
            # Remove da lista ativa
            if session.session_code in self.active_sessions:
                del self.active_sessions[session.session_code]
                
        except Exception as e:
            logger.error(f"❌ Erro nos steps: {e}")
            session.fail(str(e))
            if session.session_code in self.active_sessions:
                del self.active_sessions[session.session_code]
    
    def _queue_agent_task(self, step: Dict, session: OrchestrationSession) -> str:
        """Adiciona tarefa do agente na fila com contexto de projeto"""
        agent_slug = step['agent_slug']
        context = session.get_context_for_step(step)
        
        # Gera código único para a tarefa
        task_code = f"TASK-{uuid.uuid4().hex[:12]}"
        
        # Busca informação do projeto (se houver execução plan associada)
        project_slug = self._get_project_for_session(session.session_id)
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO agent_tasks_queue 
            (task_code, session_id, step_index, agent_slug, task_description, project_slug, status)
            VALUES (?, ?, ?, ?, ?, ?, 'pending')
        """, (
            task_code,
            session.session_id,
            step['step_index'],
            agent_slug,
            context['objective'],
            project_slug
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"   📥 Tarefa enfileirada: {task_code} ({agent_slug})" + 
                   (f" [Projeto: {project_slug}]" if project_slug else ""))
        return task_code
    
    def _get_project_for_session(self, session_id: int) -> Optional[str]:
        """Busca projeto associado à sessão de execução"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            
            # Busca plano associado à sessão
            cur.execute("""
                SELECT ep.project_slug 
                FROM orchestration_sessions os
                JOIN execution_plans ep ON os.execution_plan_id = ep.id
                WHERE os.id = ?
            """, (session_id,))
            
            row = cur.fetchone()
            conn.close()
            
            return row[0] if row else None
            
        except Exception as e:
            logger.error(f"   ⚠️ Erro ao buscar projeto: {e}")
            return None
    
    def _wait_for_task_result(self, task_code: str, timeout: int = 300) -> str:
        """Aguarda resultado da tarefa (polling)"""
        start_time = time.time()
        check_interval = 2  # segundos
        
        logger.info(f"   ⏳ Aguardando resultado de {task_code}...")
        
        while time.time() - start_time < timeout:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            cur.execute("""
                SELECT status, result, error_message 
                FROM agent_tasks_queue 
                WHERE task_code = ?
            """, (task_code,))
            row = cur.fetchone()
            conn.close()
            
            if not row:
                return f"Erro: Tarefa {task_code} não encontrada"
            
            status = row['status']
            
            if status == 'completed':
                result_data = json.loads(row['result'] or '{}')
                output = result_data.get('output', 'Tarefa completada sem resultado')
                logger.info(f"   ✅ Tarefa {task_code} completada")
                return output
            
            elif status == 'failed':
                error = row['error_message'] or 'Erro desconhecido'
                logger.error(f"   ❌ Tarefa {task_code} falhou: {error}")
                return f"Erro na execução: {error}"
            
            # Ainda pendente ou running, aguarda
            time.sleep(check_interval)
        
        logger.error(f"   ⏱️ Timeout aguardando {task_code}")
        return f"Timeout: Tarefa não completou em {timeout}s"
    
    def _execute_agent_step(self, step: Dict, session: OrchestrationSession) -> str:
        """Executa um step enfileirando e aguardando resultado"""
        # 1. Enfileira tarefa
        task_code = self._queue_agent_task(step, session)
        
        # 2. Aguarda resultado
        output = self._wait_for_task_result(task_code)
        
        return output
    
    def _evaluate_quality(self, output: str) -> int:
        """Avalia qualidade do output (simulação)"""
        # Simulação: retorna score aleatório entre 7-10
        return random.randint(7, 10)
    
    def _aggregate_outputs(self, outputs: List[Dict]) -> str:
        """Agrega outputs de todos os steps"""
        aggregated = "RESULTADO FINAL:\n\n"
        for out in outputs:
            aggregated += f"\n--- {out['agent_slug']} ---\n{out['output'][:300]}...\n"
        return aggregated
    
    def _run_improvement_loop(self, session, plan: Dict, step: Dict, agent_slug: str, target_score: int, max_attempts: int):
        """Executa loop de aperfeiçoamento até atingir nota alvo"""
        attempt = 1
        best_output = None
        best_score = 0
        
        while attempt <= max_attempts:
            logger.info(f"   🔄 Aperfeiçoamento - Tentativa {attempt}/{max_attempts}")
            
            # Executa agente
            output = self._execute_agent_step(step, session)
            score = self._evaluate_quality(output)
            
            logger.info(f"   📊 Nota: {score}/{target_score}")
            
            # Guarda melhor resultado
            if score > best_score:
                best_score = score
                best_output = output
            
            # Verifica se atingiu nota alvo
            if score >= target_score:
                logger.info(f"   ✅ Nota alvo atingida! ({score} >= {target_score})")
                return best_output, best_score
            
            # Se não atingiu e ainda tem tentativas, continua
            if attempt < max_attempts:
                logger.info(f"   📝 Melhorando... (tentativa {attempt + 1})")
                # Adiciona contexto de melhoria ao step
                step['context'] = step.get('context', '') + f"\n\n[Melhoria necessária - Tentativa {attempt + 1}]\nResultado anterior nota {score}/10. Melhore focando em:\n- Clareza\n- Completude\n- Qualidade técnica"
            
            attempt += 1
            time.sleep(1)
        
        # Retorna melhor resultado mesmo se não atingiu nota alvo
        logger.info(f"   ⚠️ Máximo de tentativas atingido. Melhor nota: {best_score}")
        return best_output, best_score
    
    def _run_variations_loop(self, session, plan: Dict, step: Dict, agent_slug: str, count: int, contexts: List[str]):
        """Executa loop de variações - gera N variações do mesmo tema"""
        variations = []
        
        # Se não tiver contextos definidos, gera automaticamente
        if not contexts:
            contexts = [f"Contexto {i+1}" for i in range(count)]
        
        for i, context in enumerate(contexts[:count], 1):
            logger.info(f"   🎨 Variação {i}/{count}: {context}")
            
            # Cria step modificado com contexto específico
            variation_step = step.copy()
            variation_step['context'] = f"[Variação: {context}]\n{step.get('context', '')}"
            variation_step['title'] = f"{step['title']} ({context})"
            
            # Executa agente
            output = self._execute_agent_step(variation_step, session)
            score = self._evaluate_quality(output)
            
            variations.append({
                'context': context,
                'output': output,
                'score': score
            })
            
            logger.info(f"   ✅ Variação {i} completa (nota: {score})")
            time.sleep(1)
        
        # Agrega todas as variações
        aggregated = "## VARIAÇÕES GERADAS\n\n"
        for i, var in enumerate(variations, 1):
            aggregated += f"\n### Variação {i}: {var['context']}\n"
            aggregated += f"Nota: {var['score']}/10\n\n"
            aggregated += var['output'][:500] + "...\n\n"
        
        return aggregated, max(v['score'] for v in variations)
    
    def run_v2(self):
        """Loop principal V2 - com orquestração e suporte a loops"""
        logger.info("🔁 Worker V2 iniciando loop principal")
        logger.info("⏳ Aguardando missões e planos...")
        
        while self.running:
            try:
                self.iteration += 1
                
                # 1. PRIMEIRO: Executa planos APROVADOS
                self.execute_approved_plans()
                
                # 2. SEGUNDO: Processa missões que PRECISAM de plano
                pending_missions = self.check_plans_needing_creation()
                if pending_missions:
                    logger.info(f"📋 {len(pending_missions)} missão(ões) precisam de plano")
                    for mission in pending_missions[:2]:
                        self.create_plan_for_mission(mission)
                        time.sleep(2)
                
                # 3. TERCEIRO: Processa missões normais (compatibilidade)
                missions = self.get_pending_missions()
                if missions:
                    logger.info(f"📋 {len(missions)} missão(ões) aprovada(s)!")
                    for mission in missions[:2]:
                        self.execute_mission(mission)
                        time.sleep(3)
                
                # Heartbeat
                if self.iteration % 12 == 0:
                    logger.info("💓 Worker V2 ativo")
                
                time.sleep(5)
                    
            except KeyboardInterrupt:
                logger.info("👋 Worker V2 parado pelo usuário")
                self.running = False
            except Exception as e:
                logger.error(f"❌ Erro no loop V2: {e}")
                time.sleep(10)

def main():
    """Entry point"""
    # Inicializa banco se necessário
    init_db()
    seed_agents()
    
    # Migra orquestração se necessário
    try:
        import migrate_orchestration
        migrate_orchestration.migrate()
    except Exception as e:
        logger.warning(f"Migração já realizada ou erro: {e}")
    
    # Cria worker e roda (versão V2)
    worker = DunderMifflinWorkerV2()
    worker.run_v2()  # Usa novo loop com orquestração

if __name__ == "__main__":
    main()
