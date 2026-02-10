#!/usr/bin/env python3
"""
Ralph Swarm - Always On System v5.0
Sistema de heartbeats e cron jobs para execução contínua
"""

import os
import sys
import json
import time
import schedule
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable

sys.path.insert(0, str(Path(__file__).parent.parent))
from ralph_swarm_core import ChannelSystem, SwarmTaskManager, AuthorType
sys.path.insert(0, str(Path(__file__).parent))
from coordination_engine import SwarmCoordinator
from agent_brain import AgentBrain

class AlwaysOnManager:
    """
    Gerenciador do sistema Always On.
    Mantém o Swarm trabalhando em background 24/7.
    """
    
    def __init__(self):
        self.channels = ChannelSystem()
        self.tasks = SwarmTaskManager()
        self.coordinator = SwarmCoordinator()
        self.running = False
        self.scheduler_thread = None
        
        # Configurações de heartbeats
        self.heartbeat_interval = 30 * 60  # 30 minutos
        self.last_heartbeat = None
        
        # Jobs agendados
        self.scheduled_jobs: List[Dict] = []
        
        # Métricas
        self.metrics = {
            'heartbeats_sent': 0,
            'tasks_auto_executed': 0,
            'alerts_triggered': 0,
            'last_activity': None
        }
    
    def start(self):
        """Inicia o sistema Always On"""
        if self.running:
            print("⚠️ Always On já está rodando")
            return
        
        self.running = True
        print("🚀 Iniciando Ralph Swarm Always On...")
        
        # Configurar jobs
        self._setup_jobs()
        
        # Iniciar scheduler em thread separada
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        print(f"✅ Always On iniciado! Heartbeat a cada {self.heartbeat_interval//60}min")
    
    def stop(self):
        """Para o sistema Always On"""
        self.running = False
        print("🛑 Always On parado")
    
    def _setup_jobs(self):
        """Configura jobs agendados"""
        
        # Heartbeat a cada 30 minutos
        schedule.every(30).minutes.do(self._send_heartbeat)
        
        # Check de #orders a cada 5 minutos
        schedule.every(5).minutes.do(self._check_orders)
        
        # Check de #drop-links a cada hora
        schedule.every(1).hours.do(self._process_drop_links)
        
        # Morning Brief às 08:00
        schedule.every().day.at("08:00").do(self._send_morning_brief)
        
        # Health check a cada 10 minutos
        schedule.every(10).minutes.do(self._health_check)
    
    def _run_scheduler(self):
        """Loop do scheduler"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def _send_heartbeat(self):
        """Envia heartbeat de status"""
        self.last_heartbeat = datetime.now()
        self.metrics['heartbeats_sent'] += 1
        
        # Postar no #live-feed
        status_msg = f"💓 Heartbeat - Sistema operacional\n   Tasks hoje: {self.metrics['tasks_auto_executed']}\n   Last activity: {self.metrics['last_activity'] or 'N/A'}"
        
        self.channels.post(
            channel_name='live-feed',
            author_type=AuthorType.SYSTEM,
            author_id='system',
            content=status_msg
        )
        
        print(f"💓 Heartbeat enviado às {datetime.now().strftime('%H:%M')}")
    
    def _check_orders(self):
        """Verifica #orders para novas tarefas"""
        print("🔍 Verificando #orders...")
        
        try:
            result = self.coordinator.process_orders()
            
            if result:
                self.metrics['tasks_auto_executed'] += 1
                self.metrics['last_activity'] = datetime.now().isoformat()
                print(f"   ✅ Task processada automaticamente")
            else:
                print("   ℹ️ Nenhuma tarefa pendente")
                
        except Exception as e:
            print(f"   ❌ Erro ao processar orders: {e}")
    
    def _process_drop_links(self):
        """Processa links em #drop-links"""
        print("🔗 Processando #drop-links...")
        
        messages = self.channels.read('drop-links', limit=10)
        
        processed = 0
        for msg in messages:
            # Verificar se é mensagem de usuário e contém URL
            if msg.author_type == 'user' and self._extract_urls(msg.content):
                urls = self._extract_urls(msg.content)
                
                for url in urls:
                    # Criar task de research para cada URL
                    task = f"Research e summarize: {url}"
                    
                    try:
                        plan = self.coordinator.analyze_task(task)
                        task_obj = self.tasks.create_task(task, 'ralph')
                        self.coordinator.execute_swarm(task, plan, task_obj.id)
                        
                        processed += 1
                        
                        # Responder no canal
                        self.channels.post(
                            channel_name='drop-links',
                            author_type=AuthorType.AGENT,
                            author_id='scout',
                            content=f"✅ Processado: {url}\n   Resumo disponível em #find-output",
                            mentions=[msg.author_id]
                        )
                        
                    except Exception as e:
                        print(f"   ❌ Erro ao processar {url}: {e}")
        
        if processed > 0:
            print(f"   ✅ {processed} links processados")
        else:
            print("   ℹ️ Nenhum link novo")
    
    def _send_morning_brief(self):
        """Envia briefing da manhã"""
        print("🌅 Enviando Morning Brief...")
        
        # Coletar dados do dia anterior
        yesterday = (datetime.now() - timedelta(days=1)).date()
        
        brief_parts = ["🌅 **MORNING BRIEF**"]
        
        # Tasks completadas
        brief_parts.append(f"\n📊 **Atividade:**")
        brief_parts.append(f"• Tasks auto-executadas: {self.metrics['tasks_auto_executed']}")
        brief_parts.append(f"• Heartbeats: {self.metrics['heartbeats_sent']}")
        
        # Alertas do Watcher
        watcher = AgentBrain('watcher')
        watch_result = watcher.think(
            task="Analisar tendências e alertas do mercado para briefing matinal",
            use_real_llm=False  # Simulação para evitar custo
        )
        
        if watch_result:
            brief_parts.append(f"\n👁️ **Observações:**")
            brief_parts.append(watch_result[:300])
        
        # Próximos passos sugeridos
        brief_parts.append(f"\n📋 **Sugestões para hoje:**")
        brief_parts.append("• Verificar #orders para novas tarefas")
        brief_parts.append("• Revisar métricas em #track-output")
        brief_parts.append("• Processar links pendentes em #drop-links")
        
        brief_msg = "\n".join(brief_parts)
        
        # Postar em #orders
        self.channels.post(
            channel_name='orders',
            author_type=AuthorType.AGENT,
            author_id='ralph',
            content=brief_msg,
            mentions=['Jeff']
        )
        
        print(f"   ✅ Morning Brief enviado")
    
    def _health_check(self):
        """Verifica saúde do sistema"""
        checks = {
            'database': self._check_database(),
            'api': self._check_api(),
            'agents': self._check_agents()
        }
        
        failed = [k for k, v in checks.items() if not v]
        
        if failed:
            alert_msg = f"🚨 **Health Check Alert**\n   Falha em: {', '.join(failed)}\n   @ralph"
            
            self.channels.post(
                channel_name='live-feed',
                author_type=AuthorType.SYSTEM,
                author_id='system',
                content=alert_msg,
                mentions=['ralph']
            )
            
            print(f"   🚨 Alerta de health check: {failed}")
        else:
            print("   ✅ Health check OK")
    
    def _check_database(self) -> bool:
        """Verifica conexão com banco"""
        try:
            self.channels.get_channels()
            return True
        except:
            return False
    
    def _check_api(self) -> bool:
        """Verifica se API está respondendo"""
        # Simplificado: sempre True se chegou aqui
        return True
    
    def _check_agents(self) -> bool:
        """Verifica se agents estão operacionais"""
        try:
            from ralph_swarm_core import SwarmAgentManager
            agents = SwarmAgentManager().get_all_agents()
            return len(agents) > 0
        except:
            return False
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extrai URLs de um texto"""
        import re
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)
    
    def get_status(self) -> Dict:
        """Retorna status do sistema Always On"""
        return {
            'running': self.running,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'metrics': self.metrics,
            'scheduled_jobs': [
                {
                    'job': str(job),
                    'next_run': job.next_run.isoformat() if hasattr(job, 'next_run') and job.next_run else None
                }
                for job in schedule.jobs
            ]
        }
    
    def trigger_now(self, job_type: str):
        """Dispara um job manualmente"""
        if job_type == 'heartbeat':
            self._send_heartbeat()
        elif job_type == 'orders':
            self._check_orders()
        elif job_type == 'drop_links':
            self._process_drop_links()
        elif job_type == 'morning_brief':
            self._send_morning_brief()
        elif job_type == 'health':
            self._health_check()
        else:
            print(f"❌ Job type desconhecido: {job_type}")


# Teste
if __name__ == '__main__':
    print("🌙 Ralph Swarm Always On - Teste")
    print("=" * 60)
    
    manager = AlwaysOnManager()
    
    print("\n1️⃣ Testando jobs individuais:")
    
    # Test heartbeat
    print("\n   Enviando heartbeat...")
    manager._send_heartbeat()
    
    # Test health check
    print("\n   Verificando saúde...")
    manager._health_check()
    
    # Test URL extraction
    print("\n   Testando extração de URLs...")
    test_text = "Check this out: https://example.com and http://test.org/path"
    urls = manager._extract_urls(test_text)
    print(f"   URLs encontradas: {urls}")
    
    # Status
    print("\n2️⃣ Status do sistema:")
    status = manager.get_status()
    print(f"   Running: {status['running']}")
    print(f"   Heartbeats: {status['metrics']['heartbeats_sent']}")
    
    print("\n" + "=" * 60)
    print("✅ Testes completados!")
    print("\nPara iniciar o sistema Always On:")
    print("  manager.start()")
    print("\nPara parar:")
    print("  manager.stop()")
