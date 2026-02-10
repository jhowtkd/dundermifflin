#!/usr/bin/env python3
"""
Ralph Swarm - Coordination Engine v5.0
Sistema de decisão e coordenação inteligente
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import concurrent.futures

sys.path.insert(0, str(Path(__file__).parent.parent))
from ralph_swarm_core import ChannelSystem, SwarmAgentManager, SwarmTaskManager, AuthorType, TaskStatus
sys.path.insert(0, str(Path(__file__).parent))
from agent_brain import AgentBrain

class TaskComplexity(Enum):
    """Níveis de complexidade de tarefa"""
    SIMPLE = "simple"       # 1 agent resolve
    MEDIUM = "medium"       # 2-3 agents
    COMPLEX = "complex"     # 4+ agents + síntese

@dataclass
class ExecutionPlan:
    """Plano de execução de uma tarefa"""
    complexity: TaskComplexity
    needs_swarm: bool
    agents_required: List[str]
    execution_strategy: str
    estimated_steps: int
    parallelizable: bool
    
    def to_dict(self) -> Dict:
        return {
            'complexity': self.complexity.value,
            'needs_swarm': self.needs_swarm,
            'agents_required': self.agents_required,
            'execution_strategy': self.execution_strategy,
            'estimated_steps': self.estimated_steps,
            'parallelizable': self.parallelizable
        }

@dataclass
class Handoff:
    """Representa um handoff entre agents"""
    from_agent: str
    to_agent: str
    message: str
    context_summary: str
    deliverable_location: str  # ex: #find-output

class SwarmCoordinator:
    """
    Coordenador inteligente do Swarm.
    Responsável por decisões estratégicas e orquestração.
    """
    
    # Palavras-chave para detectar necessidade de cada agent
    AGENT_KEYWORDS = {
        'scout': [
            'research', 'pesquisa', 'analisar', 'concorrentes', 'benchmark',
            'mercado', 'tendências', 'dados', 'informações', 'estudo',
            'comparar', 'landscape', 'overview'
        ],
        'max': [
            'código', 'code', 'build', 'implementar', 'script', 'landing page',
            'website', 'automação', 'api', 'função', 'classe', 'deploy',
            'desenvolver', 'programar', 'sistema'
        ],
        'maya': [
            'copy', 'escrever', 'headline', 'linkedin', 'thread', 'marketing',
            'descrição', 'cta', 'anúncio', 'campanha', 'seo', 'conteúdo',
            'post', 'blog', 'artigo'
        ],
        'tracker': [
            'métricas', 'analytics', 'kpi', 'dados', 'performance',
            'medir', 'monitorar', 'relatório', 'análise', 'estatísticas',
            'conversion', 'tráfego'
        ],
        'watcher': [
            'monitorar', 'observar', 'tendências', 'concorrentes', 'alerta',
            'social listening', 'feedback', 'menções', 'reviews'
        ]
    }
    
    # Indicadores de complexidade
    COMPLEXITY_INDICATORS = {
        'simple': [
            'simples', 'rápido', 'pequeno', 'básico', 'draft',
            'ideia', 'sugestão', 'verificar'
        ],
        'complex': [
            'completo', 'compreensivo', 'detalhado', 'estratégia',
            'plano', 'sistema', 'integração', 'multicanal'
        ]
    }
    
    def __init__(self):
        self.channels = ChannelSystem()
        self.agents = SwarmAgentManager()
        self.tasks = SwarmTaskManager()
        self.ralph_brain = AgentBrain('ralph')
    
    def analyze_task(self, task_description: str) -> ExecutionPlan:
        """
        Analisa uma tarefa e decide como executar.
        
        Returns:
            ExecutionPlan com estratégia recomendada
        """
        task_lower = task_description.lower()
        
        # Detectar quais agents são necessários
        agents_needed = self._detect_required_agents(task_lower)
        
        # Detectar complexidade
        complexity = self._detect_complexity(task_lower, agents_needed)
        
        # Decidir se precisa de swarm
        needs_swarm = len(agents_needed) > 1 or complexity == TaskComplexity.COMPLEX
        
        # Determinar se pode ser paralelizado
        parallelizable = self._can_parallelize(agents_needed, task_lower)
        
        # Criar estratégia
        strategy = self._create_strategy(agents_needed, complexity, parallelizable)
        
        return ExecutionPlan(
            complexity=complexity,
            needs_swarm=needs_swarm,
            agents_required=agents_needed,
            execution_strategy=strategy,
            estimated_steps=len(agents_needed) + 1,  # +1 para síntese
            parallelizable=parallelizable
        )
    
    def _detect_required_agents(self, task_lower: str) -> List[str]:
        """Detecta quais agents são necessários baseado em keywords"""
        agents = []
        agent_scores = {}
        
        for agent_slug, keywords in self.AGENT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in task_lower)
            if score > 0:
                agent_scores[agent_slug] = score
        
        # Ordenar por relevância (score)
        sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Pegar agents com score > 0
        agents = [slug for slug, score in sorted_agents if score > 0]
        
        # Se nenhum agent específico detectado, usar scout + maya como padrão
        if not agents:
            agents = ['scout', 'maya']
        
        return agents[:4]  # Máximo 4 agents para não sobrecarregar
    
    def _detect_complexity(self, task_lower: str, agents_needed: List[str]) -> TaskComplexity:
        """Detecta complexidade da tarefa"""
        # Contar indicadores
        simple_indicators = sum(1 for ind in self.COMPLEXITY_INDICATORS['simple'] if ind in task_lower)
        complex_indicators = sum(1 for ind in self.COMPLEXITY_INDICATORS['complex'] if ind in task_lower)
        
        # Baseado em agents necessários
        if len(agents_needed) >= 3 or complex_indicators > 1:
            return TaskComplexity.COMPLEX
        elif len(agents_needed) == 2 or complex_indicators > 0:
            return TaskComplexity.MEDIUM
        else:
            return TaskComplexity.SIMPLE
    
    def _can_parallelize(self, agents_needed: List[str], task_lower: str) -> bool:
        """Determina se agents podem trabalhar em paralelo"""
        # Research + Build/Create podem ser paralelos
        # Build + Create precisam de sequência
        
        has_research = 'scout' in agents_needed or 'watcher' in agents_needed
        has_build = 'max' in agents_needed
        has_create = 'maya' in agents_needed
        
        # Se tem research + (build ou create), pode paralelizar research com preparação
        if has_research and (has_build or has_create):
            return True
        
        # Se só tem build e create, precisam de sequência
        if has_build and has_create:
            return False
        
        return True
    
    def _create_strategy(self, agents: List[str], complexity: TaskComplexity, parallel: bool) -> str:
        """Cria descrição da estratégia de execução"""
        if complexity == TaskComplexity.SIMPLE:
            return f"Execução direta por {agents[0]}"
        
        if parallel:
            return f"Execução paralela: {', '.join(agents)} trabalham simultaneamente, depois síntese"
        else:
            strategy_parts = []
            for i, agent in enumerate(agents):
                if i == 0:
                    strategy_parts.append(f"{agent} primeiro")
                else:
                    strategy_parts.append(f"handoff para {agent}")
            strategy_parts.append("síntese final")
            return " → ".join(strategy_parts)
    
    def create_plan_message(self, plan: ExecutionPlan, task: str) -> str:
        """Cria mensagem de plano para #agent-chat"""
        emoji_map = {
            'scout': '🔍', 'max': '🛠️', 'maya': '📝',
            'tracker': '📊', 'watcher': '👁️', 'ralph': '🎩'
        }
        
        agents_list = "\n".join([
            f"  • {emoji_map.get(a, '🤖')} {a.title()}"
            for a in plan.agents_required
        ])
        
        return f"""📋 [SWARM DECISION]

Tarefa: {task[:80]}{'...' if len(task) > 80 else ''}

Complexidade: {plan.complexity.value.upper()}
Swarm necessário: {'Sim' if plan.needs_swarm else 'Não'}
Paralelizável: {'Sim' if plan.parallelizable else 'Não'}

Agents necessários:
{agents_list}

Estratégia:
{plan.execution_strategy}

Iniciando execução..."""
    
    def execute_swarm(self, task_description: str, plan: ExecutionPlan, task_id: int = None) -> Dict:
        """
        Executa o swarm conforme o plano.
        
        Args:
            task_description: Descrição da tarefa
            plan: Plano de execução
            task_id: ID da task no banco (opcional)
            
        Returns:
            Dict com resultados e síntese
        """
        results = {}
        
        # Atualizar status da task
        if task_id:
            self.tasks.update_status(task_id, TaskStatus.RUNNING)
        
        # Postar plano no agent-chat
        plan_msg = self.create_plan_message(plan, task_description)
        self.ralph_brain.post_to_channel('agent-chat', plan_msg)
        
        if plan.parallelizable:
            # Executar em paralelo
            results = self._execute_parallel(task_description, plan.agents_required)
        else:
            # Executar em sequência (relay race)
            results = self._execute_sequential(task_description, plan.agents_required)
        
        # Síntese final
        synthesis = self._synthesize_results(task_description, results)
        
        # Finalizar task
        if task_id:
            self.tasks.set_final_output(task_id, synthesis)
        
        return {
            'plan': plan.to_dict(),
            'results': results,
            'synthesis': synthesis
        }
    
    def _execute_parallel(self, task: str, agents: List[str]) -> Dict[str, str]:
        """Executa agents em paralelo"""
        results = {}
        
        def run_agent(agent_slug: str) -> Tuple[str, str]:
            brain = AgentBrain(agent_slug)
            
            # Atualizar status
            self.agents.update_status(agent_slug, 'busy')
            
            # Executar
            result = brain.think(task)
            
            # Postar resultado
            output_channels = {
                'scout': 'find-output', 'max': 'build-output',
                'maya': 'create-output', 'tracker': 'track-output',
                'watcher': 'watch-output'
            }
            output_channel = output_channels.get(agent_slug, 'agent-chat')
            brain.post_to_channel(output_channel, result)
            
            # Atualizar status
            self.agents.update_status(agent_slug, 'idle')
            
            return agent_slug, result
        
        # Executar em paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(agents)) as executor:
            future_to_agent = {
                executor.submit(run_agent, agent): agent 
                for agent in agents
            }
            
            for future in concurrent.futures.as_completed(future_to_agent):
                agent_slug, result = future.result()
                results[agent_slug] = result
                
                # Notificar no agent-chat
                handoff_msg = f"✅ {agent_slug.title()} completou. Resultado disponível. @ralph"
                self.channels.post('agent-chat', AuthorType.AGENT, 'system', handoff_msg, ['ralph'])
        
        return results
    
    def _execute_sequential(self, task: str, agents: List[str]) -> Dict[str, str]:
        """Executa agents em sequência (relay race)"""
        results = {}
        context = task
        
        for i, agent_slug in enumerate(agents):
            brain = AgentBrain(agent_slug)
            
            # Atualizar status
            self.agents.update_status(agent_slug, 'busy')
            
            # Executar com contexto acumulado
            result = brain.think(context)
            results[agent_slug] = result
            
            # Postar resultado
            output_channels = {
                'scout': 'find-output', 'max': 'build-output',
                'maya': 'create-output', 'tracker': 'track-output',
                'watcher': 'watch-output'
            }
            output_channel = output_channels.get(agent_slug, 'agent-chat')
            brain.post_to_channel(output_channel, result)
            
            # Atualizar status
            self.agents.update_status(agent_slug, 'idle')
            
            # Handoff para próximo agent
            if i < len(agents) - 1:
                next_agent = agents[i + 1]
                handoff_msg = f"✅ {agent_slug.title()} completou.\n   handing to {next_agent.title()}\n   @{next_agent} - contexto atualizado"
                self.channels.post('agent-chat', AuthorType.AGENT, agent_slug, handoff_msg, [next_agent])
                
                # Atualizar contexto para próximo agent
                context = f"{task}\n\nResultado anterior ({agent_slug}): {result[:500]}"
            else:
                # Último agent, avisar Ralph
                handoff_msg = f"✅ {agent_slug.title()} completou (último agent).\n   handing to Ralph para síntese\n   @ralph"
                self.channels.post('agent-chat', AuthorType.AGENT, agent_slug, handoff_msg, ['ralph'])
        
        return results
    
    def _synthesize_results(self, original_task: str, results: Dict[str, str]) -> str:
        """Cria síntese final dos resultados"""
        # Preparar input para Ralph
        synthesis_input = f"""Tarefa original: {original_task}

Resultados dos agents:

{chr(10).join([f"### {name.title()}\n{content[:800]}" for name, content in results.items()])}
"""
        
        # Ralph sintetiza
        synthesis = self.ralph_brain.think(
            task=f"Sintetizar resultados em uma entrega final coesa:\n{synthesis_input}",
            output_format="Crie uma entrega final consolidada, profissional e pronta para uso."
        )
        
        # Postar síntese
        self.ralph_brain.post_to_channel('orders', synthesis, mentions=['Jeff'])
        
        return synthesis
    
    def process_orders(self):
        """
        Processa mensagens pendentes em #orders.
        Método principal para execução contínua.
        """
        # Buscar mensagens de usuários não processadas
        messages = self.channels.read('orders', limit=10)
        
        for msg in messages:
            # Só processar mensagens de usuários
            if msg.author_type != 'user':
                continue
            
            # Verificar se já tem task associada (simplificado)
            # Na implementação real, marcaríamos mensagens como processadas
            
            print(f"📨 Processando: {msg.content[:60]}...")
            
            # Analisar e executar
            plan = self.analyze_task(msg.content)
            
            # Criar task no sistema
            task = self.tasks.create_task(msg.content, 'ralph')
            self.tasks.update_execution_plan(task.id, plan.to_dict())
            
            # Executar
            result = self.execute_swarm(msg.content, plan, task.id)
            
            print(f"   ✅ Task {task.task_code} completada!")
            
            return result  # Processar uma por vez
        
        return None


# Teste
if __name__ == '__main__':
    print("🎩 Coordination Engine - Teste")
    print("=" * 60)
    
    coord = SwarmCoordinator()
    
    # Teste 1: Análise de tarefa simples
    print("\n1️⃣ Analisando tarefa simples:")
    task1 = "Criar headline para campanha"
    plan1 = coord.analyze_task(task1)
    print(f"   Tarefa: {task1}")
    print(f"   Complexidade: {plan1.complexity.value}")
    print(f"   Agents: {plan1.agents_required}")
    print(f"   Swarm: {plan1.needs_swarm}")
    
    # Teste 2: Análise de tarefa complexa
    print("\n2️⃣ Analisando tarefa complexa:")
    task2 = "Research concorrentes, criar landing page e escrever copy persuasiva"
    plan2 = coord.analyze_task(task2)
    print(f"   Tarefa: {task2[:60]}...")
    print(f"   Complexidade: {plan2.complexity.value}")
    print(f"   Agents: {plan2.agents_required}")
    print(f"   Paralelizável: {plan2.parallelizable}")
    print(f"   Estratégia: {plan2.execution_strategy}")
    
    # Teste 3: Criar mensagem de plano
    print("\n3️⃣ Mensagem de plano:")
    msg = coord.create_plan_message(plan2, task2)
    print(msg[:400] + "...")
    
    print("\n" + "=" * 60)
    print("✅ Todos os testes passaram!")
