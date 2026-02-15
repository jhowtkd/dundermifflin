#!/usr/bin/env python3
"""
Mission Control Dashboard - Orquestração REAL com Subagentes
Executa Scout, Max, Maya, Tracker em paralelo via AgentBrain
"""

import os
import sys
import asyncio
import concurrent.futures
from datetime import datetime
from pathlib import Path

# Paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from agent_brain import AgentBrain
from live_logger import get_logger

class RealDashboardOrchestrator:
    """
    Orquestrador REAL que executa agentes do swarm em paralelo
    """
    
    def __init__(self):
        self.logger = get_logger()
        self.results = {}
        self.errors = []
        
    async def run_mission(self, mission_id: str = None) -> dict:
        """
        Executa missão completa com agentes reais
        """
        mission_id = mission_id or f"dashboard-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        print("🚀 MISSÃO REAL: Mission Control Dashboard")
        print("=" * 70)
        print(f"ID: {mission_id}")
        print(f"Agentes: Scout → Max → Maya → Tracker (paralelo)")
        print("=" * 70)
        
        # Define tasks para cada agente
        tasks = {
            'scout': {
                'name': 'Research UI Patterns',
                'prompt': '''Research best practices for mission control dashboards.
                
Focus areas:
1. Dark mode design systems (JARVIS, Bloomberg terminal aesthetics)
2. Glass morphism with Tailwind CSS
3. Real-time data visualization patterns
4. Mobile-first responsive dashboard design
5. System monitoring best practices

Deliver in Portuguese:
- 3-5 specific UI patterns with examples
- Color palette recommendations (dark mode)
- Component architecture suggestions
- Animation guidelines (Framer Motion)
- File structure recommendations for Next.js 15

Be specific and actionable.'''
            },
            'max': {
                'name': 'Technical Architecture',
                'prompt': '''Design the technical architecture for a Mission Control Dashboard.

Requirements:
- Next.js 15 with App Router
- Convex real-time backend
- Tailwind CSS v4 + Framer Motion
- 8 pages: HOME, OPS, AGENTS, CHAT, CONTENT, COMMS, KNOWLEDGE, CODE
- 15+ API routes reading from filesystem
- Dark mode, glass effects, mobile-first

Deliver in Portuguese:
- Complete folder structure
- API route specifications (what each endpoint returns)
- Convex schema for: activities, calendarEvents, tasks, contacts, contentDrafts
- Component hierarchy
- Tech stack decisions with justification
- Implementation order (priorities)

Be detailed and specific.'''
            },
            'maya': {
                'name': 'Content & Copy Strategy',
                'prompt': '''Create content strategy and UI copy for Mission Control Dashboard.

Context:
- Dashboard for OpenClaw AI agent system
- 24/7 autonomous agents on Mac Mini
- Telegram/Discord integration
- Cron jobs, sub-agents, filesystem memory
- Target: Jeff (technical user, wants efficiency)

Deliver in Portuguese:
- Navigation labels (8 items, concise)
- Page titles and descriptions
- Empty state messages for each view
- Loading states copy
- Error messages (helpful, not robotic)
- Quick command suggestions
- Onboarding text

Tone: Professional but not corporate. Direct. Premium feel.'''
            },
            'tracker': {
                'name': 'Metrics & Quality Plan',
                'prompt': '''Define metrics and quality standards for Mission Control Dashboard.

Requirements:
- Premium aesthetic (Iron Man JARVIS + Bloomberg)
- Dark mode only
- Mobile-first (320px minimum)
- Real-time updates (15s refresh)
- 8 pages, 15+ API routes

Deliver in Portuguese:
- Performance budgets (bundle size, load time)
- Code quality metrics (TypeScript strict, test coverage)
- Accessibility requirements
- Mobile responsiveness checklists
- Monitoring points (what to track)
- Success criteria for launch
- Post-launch metrics to monitor

Be specific with numbers and thresholds.'''
            }
        }
        
        # Executa em PARALELO
        print("\n🔄 Iniciando execução paralela...\n")
        
        await self.logger.step(mission_id, "orchestration", "started", {
            "agents": list(tasks.keys()),
            "mode": "parallel"
        }, mission_id)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Submete todas as tasks
            future_to_agent = {
                executor.submit(self._run_agent, agent, task['name'], task['prompt'], mission_id): agent
                for agent, task in tasks.items()
            }
            
            # Coleta resultados conforme completam
            for future in concurrent.futures.as_completed(future_to_agent):
                agent = future_to_agent[future]
                try:
                    result = future.result()
                    self.results[agent] = result
                    print(f"✅ {agent.upper()} completou ({len(result)} chars)")
                    
                    await self.logger.step(mission_id, agent, "completed", {
                        "output_length": len(result)
                    }, mission_id)
                    
                except Exception as e:
                    error_msg = str(e)
                    self.errors.append(f"{agent}: {error_msg}")
                    self.results[agent] = f"❌ ERRO: {error_msg}"
                    print(f"❌ {agent.upper()} falhou: {error_msg}")
                    
                    await self.logger.step(mission_id, agent, "failed", {
                        "error": error_msg
                    }, mission_id)
        
        # Síntese final
        print("\n" + "=" * 70)
        print("🎯 SÍNTESE FINAL")
        print("=" * 70)
        
        synthesis = await self._synthesize_results(mission_id)
        
        # Reporta status
        success_count = len([r for r in self.results.values() if not r.startswith('❌')])
        error_count = len(self.errors)
        
        print(f"\n📊 STATUS: {success_count}/4 agentes completaram")
        if error_count > 0:
            print(f"⚠️  Erros: {error_count}")
            for err in self.errors:
                print(f"   - {err}")
        
        await self.logger.step(mission_id, "orchestration", "completed", {
            "success_count": success_count,
            "error_count": error_count
        }, mission_id)
        
        return {
            "mission_id": mission_id,
            "results": self.results,
            "synthesis": synthesis,
            "errors": self.errors,
            "status": "completed" if error_count == 0 else "partial"
        }
    
    def _run_agent(self, agent_slug: str, task_name: str, prompt: str, mission_id: str) -> str:
        """
        Executa um agente individual via AgentBrain
        """
        print(f"🤖 {agent_slug.upper()} iniciando: {task_name}...")
        
        try:
            # Cria brain do agente
            brain = AgentBrain(agent_slug, use_real_llm=True)
            
            # Executa task
            result = brain.think(prompt)
            
            return result
            
        except Exception as e:
            raise Exception(f"Agent {agent_slug} failed: {str(e)}")
    
    async def _synthesize_results(self, mission_id: str) -> str:
        """
        Sintetiza resultados de todos os agentes em um plano unificado
        """
        synthesis_prompt = f"""Você é o coordenador. Sintetize os resultados dos 4 agentes em um plano unificado de implementação.

RESULTADOS DOS AGENTES:

🔍 SCOUT (Research):
{self.results.get('scout', 'N/A')}

🛠️ MAX (Arquitetura):
{self.results.get('max', 'N/A')}

📝 MAYA (Conteúdo):
{self.results.get('maya', 'N/A')}

📊 TRACKER (Métricas):
{self.results.get('tracker', 'N/A')}

INSTRUÇÕES:
Crie um plano de implementação consolidado em português:
1. Estrutura de pastas final
2. Ordem de implementação (prioridades)
3. Decisões técnicas consolidadas
4. Checklist de qualidade
5. Próximos passos imediatos

Seja prático e direto."""
        
        try:
            # Usa o próprio Claw para sintetizar
            brain = AgentBrain("ralph", use_real_llm=True)
            synthesis = brain.think(synthesis_prompt)
            
            print("\n📋 PLANO DE IMPLEMENTAÇÃO:")
            print(synthesis[:2000])  # Primeiros 2000 chars
            
            return synthesis
            
        except Exception as e:
            error_msg = f"Erro na síntese: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg


async def main():
    """Entry point"""
    orchestrator = RealDashboardOrchestrator()
    
    print("\n" + "=" * 70)
    print("🚀 ORQUESTRAÇÃO REAL INICIANDO")
    print("=" * 70)
    print("\n⚠️  Isso vai executar 4 agentes em paralelo usando LLM real.")
    print("   Custo estimado: ~$0.50-1.00 em tokens\n")
    
    # Confirmação
    import time
    print("Iniciando em 5 segundos... (Ctrl+C para cancelar)")
    time.sleep(5)
    
    # Executa
    result = await orchestrator.run_mission()
    
    # Salva resultados
    output_dir = Path(__file__).parent / "mission_outputs"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"{result['mission_id']}.json"
    import json
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: {output_file}")
    
    return result


if __name__ == "__main__":
    # Executa
    result = asyncio.run(main())
    
    print("\n" + "=" * 70)
    print("✅ MISSÃO FINALIZADA")
    print("=" * 70)
    print(f"Status: {result['status']}")
    print(f"Mission ID: {result['mission_id']}")
    print(f"Resultados salvos em: mission_outputs/")
