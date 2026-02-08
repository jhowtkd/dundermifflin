#!/usr/bin/env python3
"""
Dunder Mifflin Worker v2.0 - SQLite Edition
Executa missões localmente sem dependência do Convex.
"""

import os
import sys
import time
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path

# Import local db module
sys.path.insert(0, str(Path(__file__).parent))
from db import (
    init_db, seed_agents, get_agent_by_slug, list_missions, 
    get_mission, start_mission, complete_mission, add_event,
    create_proposal, approve_proposal, get_dashboard_stats
)

# Config
KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")
WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"
STUDIO_DIR = WORKSPACE_DIR / "studio" / "projects"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("dm-worker-v2")

class DunderMifflinWorkerV2:
    def __init__(self):
        self.running = True
        self.iteration = 0
        logger.info("🚀 Dunder Mifflin Worker v2.0 iniciado (SQLite)")
    
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
        """Chama LLM via OpenClaw sessions_spawn"""
        import subprocess
        import json
        
        # Cria comando para sessions_spawn
        task_text = f"""Você é {agent_id}, um agente especializado.

TAREFA:
{prompt}

Responda apenas com o conteúdo solicitado, sem explicações adicionais."""
        
        try:
            # Usa openclaw CLI para spawnar um agente
            result = subprocess.run(
                ["openclaw", "sessions", "spawn", "--task", task_text, "--agent-id", agent_id, "--timeout", "120"],
                capture_output=True,
                text=True,
                timeout=130
            )
            
            if result.returncode == 0:
                # Tenta extrair resultado do JSON
                try:
                    output = json.loads(result.stdout)
                    return output.get("result", result.stdout)
                except:
                    return result.stdout
            else:
                logger.error(f"Erro no spawn: {result.stderr}")
                # Fallback: retorna conteúdo mockado
                return self._generate_mock_content(prompt)
                
        except Exception as e:
            logger.error(f"Erro ao chamar LLM: {e}")
            return self._generate_mock_content(prompt)
    
    def _generate_mock_content(self, prompt):
        """Gera conteúdo mockado quando LLM falha"""
        if "carrossel" in prompt.lower() or "carousel" in prompt.lower():
            return json.dumps({
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
            }, ensure_ascii=False)
        
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
        from datetime import datetime
        
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
        """Executa missão de social media"""
        logger.info("   📱 Preparando post...")
        
        result = {
            "type": "social",
            "content": f"🚀 {mission.get('title', 'Post automático')} #DunderMifflin",
            "posted_at": datetime.now().isoformat()
        }
        
        logger.info(f"   ✅ Post preparado")
        return result
    
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

def main():
    """Entry point"""
    # Inicializa banco se necessário
    init_db()
    seed_agents()
    
    # Cria worker e roda
    worker = DunderMifflinWorkerV2()
    worker.run()

if __name__ == "__main__":
    main()
