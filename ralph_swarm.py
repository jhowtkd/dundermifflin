#!/usr/bin/env python3
"""
Ralph Swarm v4.0 - Sistema de Agent Swarms
Orquestrador que gerencia tríade + interns paralelos
"""

import os
import sys
import json
import time
import uuid
import concurrent.futures
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

sys.path.insert(0, os.path.expanduser('~/.openclaw/workspace/projects/dunder-mifflin'))
from ralph_loop import get_db, log_iteration, complete_loop, create_loop

# Diretórios
SWARMS_DIR = Path.home() / ".openclaw/workspace/projects/dunder-mifflin/swarm"
SWARMS_DIR.mkdir(exist_ok=True)

class InternType(Enum):
    """Tipos de interns especializados"""
    RESEARCH = "research"      # Pesquisa, análise de dados
    SCRAPE = "scrape"          # Web scraping
    ANALYZE = "analyze"        # Análise de conteúdo
    DRAFT = "draft"            # Rascunhos, primeiras versões
    
class SwarmStatus(Enum):
    """Status do swarm"""
    PLANNING = "planning"      # Executivo planejando
    SPAWNING = "spawning"      # Criando interns
    RUNNING = "running"        # Executando em paralelo
    CONSOLIDATING = "consolidating"  # Consolidando resultados
    REVIEWING = "reviewing"    # Dev/Marketeiro revisando
    COMPLETED = "completed"    # Finalizado
    FAILED = "failed"          # Falhou

@dataclass
class Intern:
    """Representa um intern temporário"""
    intern_id: str
    intern_type: InternType
    model: str  # Modelo barato: gemini-flash, kimi-flash
    task: str
    parent_swarm_id: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    status: str = "pending"
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    
    def to_dict(self):
        data = asdict(self)
        data['intern_type'] = self.intern_type.value
        data['created_at'] = self.created_at.isoformat()
        data['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        return data

@dataclass
class Swarm:
    """Representa um swarm de execução"""
    swarm_id: str
    original_task: str
    coordinator_agent: str  # sempre 'o-executivo'
    primary_agents: List[str]  # ['o-dev', 'o-marketeiro'] ou só um
    status: SwarmStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    # Planejamento
    execution_plan: Optional[Dict] = None
    needs_interns: bool = False
    
    # Interns
    interns: List[Intern] = None
    
    # Resultados
    intern_results: Optional[Dict] = None
    final_result: Optional[str] = None
    total_cost: float = 0.0
    
    def __post_init__(self):
        if self.interns is None:
            self.interns = []
    
    def to_dict(self):
        return {
            'swarm_id': self.swarm_id,
            'original_task': self.original_task,
            'coordinator_agent': self.coordinator_agent,
            'primary_agents': self.primary_agents,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'execution_plan': self.execution_plan,
            'needs_interns': self.needs_interns,
            'interns': [i.to_dict() for i in self.interns],
            'intern_results': self.intern_results,
            'final_result': self.final_result,
            'total_cost': self.total_cost
        }

class RalphSwarm:
    """Orquestrador principal de swarms"""
    
    # Modelos por tier de custo
    MODELS = {
        'cheap': 'google-antigravity/gemini-3-flash',      # Interns
        'medium': 'google-antigravity/gemini-3-pro',       # Dev/Marketeiro
        'expensive': 'kimi-coding/k2p5'                     # Executivo
    }
    
    def __init__(self):
        self.active_swarms: Dict[str, Swarm] = {}
        self.load_active_swarms()
    
    def load_active_swarms(self):
        """Carrega swarms ativos do disco"""
        swarm_file = SWARMS_DIR / "active_swarms.json"
        if swarm_file.exists():
            try:
                with open(swarm_file) as f:
                    data = json.load(f)
                    # Reconstruir objetos Swarm
                    for swarm_id, swarm_data in data.items():
                        # TODO: Reconstruir objeto completo
                        pass
            except Exception as e:
                print(f"Erro ao carregar swarms: {e}")
    
    def save_active_swarms(self):
        """Salva swarms ativos no disco"""
        swarm_file = SWARMS_DIR / "active_swarms.json"
        data = {sid: s.to_dict() for sid, s in self.active_swarms.items()}
        with open(swarm_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_swarm(self, task: str, coordinator: str = "o-executivo") -> Swarm:
        """Cria um novo swarm a partir de uma tarefa"""
        swarm_id = f"SWARM-{uuid.uuid4().hex[:8].upper()}"
        
        # Determinar primary agents baseado na tarefa
        primary_agents = self._detect_primary_agents(task)
        
        swarm = Swarm(
            swarm_id=swarm_id,
            original_task=task,
            coordinator_agent=coordinator,
            primary_agents=primary_agents,
            status=SwarmStatus.PLANNING,
            created_at=datetime.now()
        )
        
        self.active_swarms[swarm_id] = swarm
        self.save_active_swarms()
        
        print(f"🐝 Swarm criado: {swarm_id}")
        print(f"   Tarefa: {task[:60]}...")
        print(f"   Agentes primários: {', '.join(primary_agents)}")
        
        return swarm
    
    def _detect_primary_agents(self, task: str) -> List[str]:
        """Detecta quais agentes primários são necessários"""
        task_lower = task.lower()
        agents = []
        
        # Palavras-chave para Dev
        dev_keywords = ['código', 'programar', 'função', 'classe', 'api', 'script', 
                       'python', 'javascript', 'bug', 'debug', 'deploy', 'landing page']
        # Palavras-chave para Marketeiro
        marketing_keywords = ['copy', 'headline', 'marketing', 'linkedin', 'post',
                             'descrição', 'cta', 'anúncio', 'campanha', 'seo']
        
        if any(kw in task_lower for kw in dev_keywords):
            agents.append('o-dev')
        
        if any(kw in task_lower for kw in marketing_keywords):
            agents.append('o-marketeiro')
        
        # Se não detectou, usa ambos por padrão
        if not agents:
            agents = ['o-dev', 'o-marketeiro']
        
        return agents
    
    def plan_execution(self, swarm: Swarm) -> Dict:
        """Fase 1: Executivo planeja a execução"""
        print(f"\n🧠 [{swarm.swarm_id}] Fase 1: Planejamento")
        
        # Criar prompt para o Executivo analisar a tarefa
        plan_prompt = f"""Você é o Executivo Coordenador. Analise esta tarefa e determine:

TAREFA: {swarm.original_task}

Agentes primários disponíveis: {', '.join(swarm.primary_agents)}

DECISÕES A TOMAR:
1. A tarefa é simples (1 agente resolve) ou complexa (precisa de swarm)?
2. Se complexa, quantos e quais interns são necessários?
3. Que tipo de research/análise paralela agilizaria o trabalho?

Responda em formato JSON:
{{
  "complexity": "simple|complex",
  "needs_interns": true|false,
  "interns_required": [
    {{"type": "research|scrape|analyze|draft", "count": N, "task": "descrição"}}
  ],
  "execution_strategy": "descrição do plano",
  "estimated_iterations": N
}}

IMPORTANTE: Seja pragmático. Só use interns se realmente acelerar o trabalho."""
        
        # TODO: Chamar LLM para planejamento
        # Por enquanto, simulamos uma decisão
        plan = {
            "complexity": "complex",
            "needs_interns": True,
            "interns_required": [
                {"type": "research", "count": 2, "task": "Pesquisar concorrentes e benchmarks"},
                {"type": "analyze", "count": 1, "task": "Analisar melhores práticas do mercado"}
            ],
            "execution_strategy": "Interns fazem research paralelo enquanto agentes primários começam estrutura base",
            "estimated_iterations": 3
        }
        
        swarm.execution_plan = plan
        swarm.needs_interns = plan["needs_interns"]
        
        print(f"   Complexidade: {plan['complexity']}")
        print(f"   Precisa de interns: {plan['needs_interns']}")
        if plan['needs_interns']:
            total_interns = sum(i['count'] for i in plan['interns_required'])
            print(f"   Interns: {total_interns}")
        
        return plan
    
    def spawn_interns(self, swarm: Swarm) -> List[Intern]:
        """Fase 2: Criar interns temporários"""
        if not swarm.needs_interns or not swarm.execution_plan:
            return []
        
        print(f"\n👶 [{swarm.swarm_id}] Fase 2: Spawning Interns")
        
        interns = []
        for intern_spec in swarm.execution_plan['interns_required']:
            for i in range(intern_spec['count']):
                intern_id = f"INTERN-{uuid.uuid4().hex[:6].upper()}"
                intern = Intern(
                    intern_id=intern_id,
                    intern_type=InternType(intern_spec['type']),
                    model=self.MODELS['cheap'],
                    task=intern_spec['task'],
                    parent_swarm_id=swarm.swarm_id,
                    created_at=datetime.now()
                )
                interns.append(intern)
                print(f"   + {intern_id} ({intern.intern_type.value})")
        
        swarm.interns = interns
        swarm.status = SwarmStatus.SPAWNING
        self.save_active_swarms()
        
        return interns
    
    def execute_intern(self, intern: Intern) -> str:
        """Executa um único intern (será chamado em paralelo)"""
        print(f"   🔄 Executando {intern.intern_id}...")
        
        # Criar loop no banco para tracking
        loop_code = create_loop(
            agent_slug='o-dev',  # Simplificado - idealmente teríamos agentes especializados por tipo
            task=f"[INTERN {intern.intern_type.value.upper()}] {intern.task}",
            max_iterations=2,
            completion_promise='RALPH_COMPLETE'
        )
        
        # Aqui chamaria o executor real
        # Por enquanto simulamos
        time.sleep(1)  # Simula execução
        
        result = f"Resultado simulado do intern {intern.intern_id}"
        intern.result = result
        intern.status = "completed"
        intern.completed_at = datetime.now()
        intern.tokens_in = 500
        intern.tokens_out = 300
        intern.cost_usd = 0.0005
        
        return result
    
    def run_swarm_parallel(self, swarm: Swarm) -> Dict[str, str]:
        """Fase 3: Executar todos os interns em paralelo"""
        if not swarm.interns:
            return {}
        
        print(f"\n⚡ [{swarm.swarm_id}] Fase 3: Execução Paralela")
        print(f"   {len(swarm.interns)} interns executando simultaneamente...")
        
        swarm.status = SwarmStatus.RUNNING
        self.save_active_swarms()
        
        results = {}
        
        # Usar ThreadPoolExecutor para paralelismo real
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_intern = {
                executor.submit(self.execute_intern, intern): intern 
                for intern in swarm.interns
            }
            
            for future in concurrent.futures.as_completed(future_to_intern):
                intern = future_to_intern[future]
                try:
                    result = future.result()
                    results[intern.intern_id] = result
                    print(f"   ✅ {intern.intern_id} completado")
                except Exception as e:
                    print(f"   ❌ {intern.intern_id} falhou: {e}")
                    results[intern.intern_id] = f"Erro: {e}"
        
        swarm.intern_results = results
        swarm.status = SwarmStatus.CONSOLIDATING
        self.save_active_swarms()
        
        return results
    
    def consolidate_results(self, swarm: Swarm) -> str:
        """Fase 4: Consolidar resultados dos interns"""
        print(f"\n📦 [{swarm.swarm_id}] Fase 4: Consolidação")
        
        if not swarm.intern_results:
            return "Nenhum resultado de interns"
        
        # Aqui o Executivo consolidaria os resultados
        # Por enquanto, juntamos simplesmente
        consolidated = "\n\n".join([
            f"### {intern_id}\n{result}"
            for intern_id, result in swarm.intern_results.items()
        ])
        
        print(f"   Resultados consolidados: {len(consolidated)} chars")
        
        return consolidated
    
    def handoff_to_primary(self, swarm: Swarm, consolidated_results: str):
        """Fase 5: Entregar para agentes primários refinarem"""
        print(f"\n🎯 [{swarm.swarm_id}] Fase 5: Handoff para Agentes Primários")
        
        for agent in swarm.primary_agents:
            print(f"   📨 Entregando para {agent}...")
            # Criar loop para o agente primário
            # TODO: Implementar integração real
        
        swarm.status = SwarmStatus.REVIEWING
        self.save_active_swarms()
    
    def execute_swarm(self, swarm_id: str):
        """Executa o fluxo completo de um swarm"""
        swarm = self.active_swarms.get(swarm_id)
        if not swarm:
            print(f"Swarm {swarm_id} não encontrado")
            return
        
        try:
            # Fase 1: Planejamento
            self.plan_execution(swarm)
            
            # Fase 2: Spawning (se necessário)
            if swarm.needs_interns:
                self.spawn_interns(swarm)
                
                # Fase 3: Execução paralela
                self.run_swarm_parallel(swarm)
                
                # Fase 4: Consolidação
                consolidated = self.consolidate_results(swarm)
            else:
                consolidated = "Tarefa simples - sem interns necessários"
            
            # Fase 5: Handoff
            self.handoff_to_primary(swarm, consolidated)
            
            # Finalizar
            swarm.status = SwarmStatus.COMPLETED
            swarm.completed_at = datetime.now()
            
            # Calcular custo total
            swarm.total_cost = sum(i.cost_usd for i in swarm.interns)
            
            print(f"\n✅ [{swarm_id}] Swarm completado!")
            print(f"   Custo total: ${swarm.total_cost:.4f}")
            
        except Exception as e:
            print(f"\n❌ [{swarm_id}] Erro: {e}")
            swarm.status = SwarmStatus.FAILED
        
        self.save_active_swarms()
    
    def list_active_swarms(self) -> List[Swarm]:
        """Lista swarms ativos"""
        return [s for s in self.active_swarms.values() 
                if s.status not in [SwarmStatus.COMPLETED, SwarmStatus.FAILED]]
    
    def get_swarm_status(self, swarm_id: str) -> Optional[Dict]:
        """Retorna status de um swarm"""
        swarm = self.active_swarms.get(swarm_id)
        return swarm.to_dict() if swarm else None


def main():
    """Teste do sistema"""
    print("🐝 Ralph Swarm v4.0 - Teste")
    print("=" * 60)
    
    swarm_system = RalphSwarm()
    
    # Criar swarm de teste
    task = "Criar landing page para SaaS de produtividade com research de concorrentes e copy persuasiva"
    swarm = swarm_system.create_swarm(task)
    
    # Executar
    swarm_system.execute_swarm(swarm.swarm_id)
    
    print("\n" + "=" * 60)
    print("✅ Teste concluído!")


if __name__ == '__main__':
    main()
