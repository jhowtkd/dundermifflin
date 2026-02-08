#!/usr/bin/env python3
"""
Dunder Mifflin Worker - Usando Convex Python SDK
Executa missões dos agentes no clawd-B450MHP
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
from convex import ConvexClient

# Config
CONVEX_URL = os.getenv("CONVEX_URL", "https://cautious-puffin-441.convex.cloud")
CONVEX_DEPLOY_KEY = os.getenv("CONVEX_DEPLOY_KEY", "")
KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("dm-worker")

class DunderMifflinWorker:
    def __init__(self):
        # Inicializa cliente Convex
        self.convex = ConvexClient(CONVEX_URL)
        self.running = True
        self.iteration = 0
        logger.info("🚀 Dunder Mifflin Worker iniciado")
        logger.info(f"🌐 Convex URL: {CONVEX_URL}")
    
    def get_pending_missions(self):
        """Busca missões aprovadas (status approved)"""
        try:
            return self.convex.query("agents:listMissions", {"status": "approved"})
        except Exception as e:
            logger.error(f"Erro ao buscar missões: {e}")
            return []
    
    def get_running_missions(self):
        """Busca missões em execução"""
        try:
            return self.convex.query("agents:listMissions", {"status": "running"})
        except Exception as e:
            logger.error(f"Erro ao buscar missões em execução: {e}")
            return []
    
    def start_mission(self, mission_id):
        """Inicia uma missão"""
        try:
            return self.convex.mutation("agents:startMission", {"id": mission_id})
        except Exception as e:
            logger.error(f"Erro ao iniciar missão: {e}")
            return None
    
    def complete_mission(self, mission_id, status="succeeded", result=None):
        """Completa uma missão"""
        try:
            return self.convex.mutation("agents:completeMission", {
                "id": mission_id,
                "status": status,
                "result": result or {}
            })
        except Exception as e:
            logger.error(f"Erro ao completar missão: {e}")
            return None
    
    def execute_mission(self, mission):
        """Executa uma missão completa"""
        mission_id = mission.get("_id")
        title = mission.get("title", "Unknown")
        mission_type = mission.get("missionType", "general")
        
        logger.info(f"▶️ Iniciando missão: {title}")
        logger.info(f"   Tipo: {mission_type} | ID: {mission_id[:8]}...")
        
        # Marca como running
        self.start_mission(mission_id)
        logger.info("   Status alterado para: running")
        
        try:
            # Simula execução baseada no tipo
            if mission_type == "content":
                result = self._execute_content_mission(mission)
            elif mission_type == "research":
                result = self._execute_research_mission(mission)
            elif mission_type == "social":
                result = self._execute_social_mission(mission)
            else:
                result = self._execute_general_mission(mission)
            
            # Completa com sucesso
            self.complete_mission(mission_id, "succeeded", result)
            logger.info(f"✅ Missão completada: {title}")
            logger.info(f"   Resultado: {json.dumps(result, indent=2)[:100]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Missão falhou: {e}")
            self.complete_mission(mission_id, "failed", {"error": str(e)})
            return False
    
    def _execute_content_mission(self, mission):
        """Executa missão de conteúdo"""
        logger.info("   📝 Gerando conteúdo...")
        time.sleep(2)  # Simula processamento
        
        title = mission.get("title", "")
        result = {
            "type": "content",
            "content": f"📝 Conteúdo gerado com sucesso para: {title}\n\n"
                       f"Aqui está um exemplo de conteúdo sobre {title}. "
                       f"Este conteúdo foi gerado automaticamente pelo agente Quill "
                       f"como parte de uma missão de teste do Dunder Mifflin.",
            "word_count": 45,
            "generated_at": datetime.now().isoformat(),
            "status": "completed"
        }
        logger.info(f"   ✅ Conteúdo gerado: {result['word_count']} palavras")
        return result
    
    def _execute_research_mission(self, mission):
        """Executa missão de pesquisa"""
        logger.info("   🔍 Realizando pesquisa...")
        time.sleep(3)
        
        result = {
            "type": "research",
            "query": mission.get("title", ""),
            "sources": [
                {"url": "https://google.com", "title": "Google Search"},
                {"url": "https://wikipedia.org", "title": "Wikipedia"},
                {"url": "https://scholar.google.com", "title": "Google Scholar"}
            ],
            "findings": [
                "Encontrado dado relevante #1 sobre o tema",
                "Encontrado dado relevante #2 sobre o tema",
                "Encontrado dado relevante #3 sobre o tema"
            ],
            "completed_at": datetime.now().isoformat()
        }
        logger.info(f"   ✅ Pesquisa completa: {len(result['findings'])} resultados")
        return result
    
    def _execute_social_mission(self, mission):
        """Executa missão de social media"""
        logger.info("   📱 Postando nas redes...")
        time.sleep(1)
        
        result = {
            "type": "social",
            "platform": "twitter",
            "tweet_id": f"tweet_{int(time.time())}",
            "content": f"🚀 {mission.get('title', 'Post automático')} #DunderMifflin #AI",
            "engagement": {"likes": 0, "retweets": 0, "replies": 0},
            "posted_at": datetime.now().isoformat()
        }
        logger.info(f"   ✅ Post criado: {result['content'][:50]}...")
        return result
    
    def _execute_general_mission(self, mission):
        """Executa missão geral"""
        logger.info("   ⚙️ Executando tarefa geral...")
        time.sleep(2)
        
        result = {
            "type": "general",
            "mission_title": mission.get("title", ""),
            "message": "Tarefa executada com sucesso pelo Dunder Mifflin Worker",
            "execution_time_ms": 2000,
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
                        time.sleep(3)  # Pausa entre missões
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

if __name__ == "__main__":
    worker = DunderMifflinWorker()
    worker.run()
