#!/usr/bin/env python3
"""
Claw Coordinator System
Arquitetura flattening - eu sou o único ponto de contato
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

# Paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

# Import Skill Dispatcher
try:
    from claw_skill_dispatcher import get_skill_dispatcher
    HAS_SKILL_DISPATCHER = True
except ImportError:
    HAS_SKILL_DISPATCHER = False

class ComplexityLevel(Enum):
    SIMPLE = "simple"      # Eu faço direto
    MEDIUM = "medium"      # Spawno 1 subagente
    COMPLEX = "complex"    # Spawno múltiplos subagentes

class ActionType(Enum):
    DIRECT = "direct"           # Eu executo
    SPAWN_SINGLE = "spawn_single"   # Um subagente
    SPAWN_PARALLEL = "spawn_parallel"  # Múltiplos subagentes
    ASK_FIRST = "ask_first"     # Pergunto antes

@dataclass
class TaskAnalysis:
    complexity: ComplexityLevel
    action: ActionType
    agents_needed: List[str]
    estimated_time: int  # minutos
    description: str
    reason: str

@dataclass
class ClawDecision:
    timestamp: str
    user_request: str
    analysis: TaskAnalysis
    executed: bool = False
    result: Optional[str] = None
    user_approved: Optional[bool] = None

class ClawCoordinator:
    """
    Eu sou o coordinator. Jeff fala comigo, eu decido, eu executo ou spawno.
    """
    
    # Keywords para classificação de complexidade
    COMPLEX_KEYWORDS = [
        "sistema", "arquitetura", "implementar", "criar projeto", 
        "nova funcionalidade", "refatorar", "migrar", "integrar",
        "pesquisar e implementar", "analisar e criar"
    ]
    
    MEDIUM_KEYWORDS = [
        "criar função", "adicionar endpoint", "modificar", "atualizar",
        "corrigir bug", "otimizar", "documentar"
    ]
    
    SIMPLE_KEYWORDS = [
        "verificar", "mostrar", "listar", "qual", "quando", "onde",
        "como está", "status de", "resuma", "explique"
    ]
    
    AGENT_ROLES = {
        "max": {
            "name": "Max",
            "role": "Builder",
            "emoji": "🛠️",
            "skills": ["coding", "implementação", "debug", "arquitetura"],
            "for": ["build", "code", "implement", "fix"]
        },
        "scout": {
            "name": "Scout", 
            "role": "Research",
            "emoji": "🔍",
            "skills": ["pesquisa", "análise", "benchmark", "investigação"],
            "for": ["research", "analyze", "investigate", "compare"]
        },
        "maya": {
            "name": "Maya",
            "role": "Copywriter",
            "emoji": "📝",
            "skills": ["copy", "conteúdo", "docs", "UX writing"],
            "for": ["write", "copy", "content", "docs"]
        },
        "tracker": {
            "name": "Tracker",
            "role": "Analytics",
            "emoji": "📊",
            "skills": ["métricas", "relatórios", "análise de dados"],
            "for": ["metrics", "report", "analytics", "data"]
        },
        "watcher": {
            "name": "Watcher",
            "role": "Monitor",
            "emoji": "👁️",
            "skills": ["monitoramento", "alerts", "health check"],
            "for": ["monitor", "check", "watch", "alert"]
        }
    }
    
    def __init__(self, mode: str = "ask_first"):
        self.mode = mode  # "ask_first", "execute_report", "silent"
        self.decision_history: List[ClawDecision] = []
        self.current_context: Dict[str, Any] = {}
        self.pending_heartbeat: Optional[Dict] = None
        
        # Skill dispatcher
        self.skill_dispatcher = get_skill_dispatcher() if HAS_SKILL_DISPATCHER else None
        
    def analyze_request(self, request: str) -> TaskAnalysis:
        """
        Analisa a request e decide complexidade e ação
        """
        request_lower = request.lower()
        
        # Detecta complexidade
        if any(kw in request_lower for kw in self.COMPLEX_KEYWORDS):
            complexity = ComplexityLevel.COMPLEX
            agents = self._select_agents(request)
            action = ActionType.SPAWN_PARALLEL
            time_estimate = 30
            reason = "Múltiplas etapas necessárias"
            
        elif any(kw in request_lower for kw in self.MEDIUM_KEYWORDS):
            complexity = ComplexityLevel.MEDIUM
            agents = self._select_agents(request)[:1]  # Só o principal
            action = ActionType.SPAWN_SINGLE
            time_estimate = 15
            reason = "Tarefa focada, um especialista resolve"
            
        else:
            complexity = ComplexityLevel.SIMPLE
            agents = []
            action = ActionType.DIRECT
            time_estimate = 5
            reason = "Posso resolver diretamente"
        
        return TaskAnalysis(
            complexity=complexity,
            action=action,
            agents_needed=agents,
            estimated_time=time_estimate,
            description=self._generate_description(request, complexity),
            reason=reason
        )
    
    def _select_agents(self, request: str) -> List[str]:
        """Seleciona quais agentes são necessários"""
        request_lower = request.lower()
        selected = []
        
        for slug, config in self.AGENT_ROLES.items():
            score = 0
            for keyword in config["for"]:
                if keyword in request_lower:
                    score += 1
            if score > 0:
                selected.append((slug, score))
        
        # Ordena por relevância
        selected.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in selected] if selected else ["max"]
    
    def _generate_description(self, request: str, complexity: ComplexityLevel) -> str:
        """Gera descrição da ação proposta"""
        if complexity == ComplexityLevel.SIMPLE:
            return f"Vou resolver isso diretamente: {request[:100]}"
        elif complexity == ComplexityLevel.MEDIUM:
            return f"Vou chamar um especialista para: {request[:100]}"
        else:
            return f"Vou coordenar múltiplos especialistas para: {request[:100]}"
    
    async def process_request(self, request: str, context: Dict = None) -> str:
        """
        Processo principal: analiso, pergunto (se necessário), executo
        """
        # Analisa
        analysis = self.analyze_request(request)
        
        # Cria decisão
        decision = ClawDecision(
            timestamp=datetime.now().isoformat(),
            user_request=request,
            analysis=analysis
        )
        self.decision_history.append(decision)
        
        # Se modo é "ask_first", pergunta antes
        if self.mode == "ask_first" and analysis.action != ActionType.DIRECT:
            return self._format_ask_message(analysis)
        
        # Senão, executa
        return await self._execute(decision)
    
    def _format_ask_message(self, analysis: TaskAnalysis) -> str:
        """Formata mensagem perguntando pro usuário"""
        agents_str = ", ".join([self.AGENT_ROLES[a]["emoji"] + " " + self.AGENT_ROLES[a]["name"] 
                                for a in analysis.agents_needed])
        
        msg = f"🤔 **Análise da sua request:**\n\n"
        msg += f"**Complexidade:** {analysis.complexity.value}\n"
        msg += f"**Ação proposta:** {analysis.description}\n"
        msg += f"**Agentes necessários:** {agents_str}\n"
        msg += f"**Tempo estimado:** ~{analysis.estimated_time} min\n"
        msg += f"**Motivo:** {analysis.reason}\n\n"
        msg += f"**Quer que eu prossiga?** (sim/não/ajustar)"
        
        return msg
    
    async def _execute(self, decision: ClawDecision) -> str:
        """Executa a ação decidida"""
        analysis = decision.analysis
        
        # Tenta usar skill primeiro (se disponível)
        if self.skill_dispatcher:
            skill_result = await self._try_skill_execution(decision.user_request)
            if skill_result:
                decision.executed = True
                decision.result = skill_result
                return skill_result
        
        if analysis.action == ActionType.DIRECT:
            # Eu faço diretamente
            decision.executed = True
            decision.result = f"✅ Resolvi diretamente: {decision.user_request[:50]}..."
            return decision.result
            
        elif analysis.action == ActionType.SPAWN_SINGLE:
            # Spawno UM agente real do swarm
            agent = analysis.agents_needed[0]
            result = await self._spawn_swarm_agent(agent, decision.user_request)
            decision.result = result
            return result
            
        else:  # SPAWN_PARALLEL - Coordeno múltiplos agentes reais
            results = await self._spawn_swarm_parallel(analysis.agents_needed, decision.user_request)
            decision.result = self._synthesize_results(results)
            return decision.result
    
    async def _spawn_swarm_agent(self, agent_slug: str, task: str) -> str:
        """
        Spawna um agente REAL do swarm via AgentBrain
        """
        try:
            from agent_brain import AgentBrain
            
            agent_info = self.AGENT_ROLES.get(agent_slug, {})
            agent_name = agent_info.get('name', agent_slug)
            emoji = agent_info.get('emoji', '🤖')
            
            print(f"🚀 Spawning {agent_name}...")
            
            # Cria brain do agente
            brain = AgentBrain(agent_slug, use_real_llm=True)
            
            # Executa task
            result = brain.think(task)
            
            # Extrai resultado limpo (remove logs de debug)
            clean_result = self._extract_clean_output(result)
            
            return f"{emoji} **{agent_name}** completou:\n{clean_result[:800]}"
            
        except Exception as e:
            return f"❌ Erro ao spawnar {agent_slug}: {str(e)}"
    
    async def _spawn_swarm_parallel(self, agents: List[str], task: str) -> Dict[str, str]:
        """
        Spawna múltiplos agentes do swarm EM PARALELO
        """
        import concurrent.futures
        
        results = {}
        
        def run_agent(agent_slug: str) -> Tuple[str, str]:
            try:
                from agent_brain import AgentBrain
                
                brain = AgentBrain(agent_slug, use_real_llm=True)
                result = brain.think(task)
                clean_result = self._extract_clean_output(result)
                
                return agent_slug, clean_result
            except Exception as e:
                return agent_slug, f"❌ Erro: {str(e)}"
        
        # Executa em paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(agents)) as executor:
            futures = {executor.submit(run_agent, agent): agent for agent in agents}
            
            for future in concurrent.futures.as_completed(futures):
                agent, result = future.result()
                results[agent] = result
        
        return results
    
    def _extract_clean_output(self, raw_output: str) -> str:
        """
        Extrai apenas o resultado útil do output do agente
        Remove logs de debug (ThinkPart, StatusUpdate, etc)
        """
        import re
        
        # Procura por TextPart ou conteúdo após marcadores
        patterns = [
            r"TextPart\([^)]*text=['\"](.+?)['\"]",
            r"<RALPH_COMPLETE>(.*?)(?:</RALPH_COMPLETE>|$)",
            r"## Resposta Final\s*\n(.+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, raw_output, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        # Se não achou padrão, retorna últimas linhas (resultado geralmente no final)
        lines = raw_output.strip().split('\n')
        # Remove linhas de log óbvias
        clean_lines = [
            l for l in lines 
            if not any(x in l for x in ['TurnBegin', 'StepBegin', 'ThinkPart', 'StatusUpdate', 'TurnEnd', 'TextPart'])
        ]
        
        return '\n'.join(clean_lines[-20:])  # Últimas 20 linhas
    
    async def _try_skill_execution(self, task: str) -> Optional[str]:
        """Tenta executar via skill dispatcher"""
        if not self.skill_dispatcher:
            return None
        
        # Detecta se tem skill adequada
        skill_id = self.skill_dispatcher.detect_skill(task)
        if skill_id:
            result = await self.skill_dispatcher.execute_with_skill(task)
            if result.get('success'):
                return f"✅ Executado via skill **{skill_id}**:\n{result.get('result', 'Concluído')}"
        return None
    
    def _synthesize_results(self, results: Dict[str, str]) -> str:
        """Sintetiza resultados de múltiplos agentes"""
        msg = "🎯 **Resultado da coordenação:**\n\n"
        for agent, result in results.items():
            agent_info = self.AGENT_ROLES.get(agent, {})
            msg += f"{agent_info.get('emoji', '🤖')} **{agent_info.get('name', agent)}:** {result}\n\n"
        return msg
    
    def approve_and_execute(self, decision_index: int = -1) -> str:
        """Usuário aprovou, executa a decisão"""
        if not self.decision_history:
            return "❌ Nenhuma decisão pendente"
        
        decision = self.decision_history[decision_index]
        decision.user_approved = True
        
        # Executa (síncrono por simplicidade, pode ser async)
        return asyncio.run(self._execute(decision))
    
    def get_status(self) -> str:
        """Retorna status do coordinator"""
        pending = len([d for d in self.decision_history if d.user_approved is None])
        executed = len([d for d in self.decision_history if d.executed])
        
        return f"📊 **Claw Coordinator Status:**\n- Modo: {self.mode}\n- Decisões pendentes: {pending}\n- Executadas: {executed}\n- Total: {len(self.decision_history)}"


# Singleton global
coordinator = ClawCoordinator(mode="ask_first")

def get_coordinator() -> ClawCoordinator:
    """Retorna instância global"""
    return coordinator


# Funções de conveniência
async def claw_process(request: str, context: Dict = None) -> str:
    """Processa request pelo Claw"""
    return await coordinator.process_request(request, context)

def claw_status() -> str:
    """Retorna status"""
    return coordinator.get_status()


def claw_approve() -> str:
    """Aprova última decisão pendente"""
    return coordinator.approve_and_execute()


if __name__ == "__main__":
    # Teste
    async def test():
        c = ClawCoordinator()
        
        # Teste simples
        result = await c.process_request("Qual é o status do sistema?")
        print(f"Simples: {result}\n")
        
        # Teste médio
        result = await c.process_request("Cria uma função de login")
        print(f"Médio: {result}\n")
        
        # Teste complexo
        result = await c.process_request("Implementa um sistema de autenticação completo")
        print(f"Complexo: {result}\n")
    
    asyncio.run(test())
