#!/usr/bin/env python3
"""
Ralph Swarm v4.1 - Sistema Completo de Agent Swarms
Inclui: Canais como DB, Agent-Chat, Synthesis, Live Feed, Memory
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
from dataclasses import dataclass, asdict, field
from enum import Enum

sys.path.insert(0, os.path.expanduser('~/.openclaw/workspace/projects/dunder-mifflin'))

# Diretórios base
BASE_DIR = Path.home() / ".openclaw/workspace/projects/dunder-mifflin"
SWARM_DIR = BASE_DIR / "swarm"
CHANNELS_DIR = SWARM_DIR / "channels"  # Simula canais do Discord
MEMORY_DIR = SWARM_DIR / "memory"      # Memória persistente
LIVE_FEED_FILE = SWARM_DIR / "live_feed.json"

for d in [SWARM_DIR, CHANNELS_DIR, MEMORY_DIR]:
    d.mkdir(parents=True, exist_ok=True)

class ChannelType(Enum):
    """Tipos de canais (igual Discord)"""
    ORDERS = "orders"           # Entrada de tarefas
    OUTPUT = "output"           # Resultados de trabalho
    LOGS = "logs"               # Debug, erros, thought process
    MEMORY = "memory"           # Conhecimento persistente
    AGENT_CHAT = "agent-chat"   # Coordenação entre agents
    DROP_LINKS = "drop-links"   # Links para research auto
    LIVE_FEED = "live-feed"     # Atividade em tempo real

class AgentRole(Enum):
    """Papéis dos agents no swarm"""
    COORDINATOR = "coordinator"  # O Executivo
    FIND = "find"               # Research (intern)
    BUILD = "build"             # Implementação (Dev)
    CREATE = "create"           # Copy/Content (Marketeiro)
    TRACK = "track"             # Analytics
    WATCH = "watch"             # Monitoramento

@dataclass
class Agent:
    """Representa um agent no sistema"""
    agent_id: str
    name: str  # Nome amigável (Scout, Max, etc.)
    role: AgentRole
    model_tier: str  # cheap, medium, expensive
    personality: str = ""
    memory: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        # Carregar memória do agente
        memory_file = MEMORY_DIR / f"{self.agent_id}.json"
        if memory_file.exists():
            with open(memory_file) as f:
                self.memory = json.load(f)

@dataclass
class Message:
    """Mensagem em um canal (simula Discord)"""
    msg_id: str
    channel: str
    author: str
    content: str
    timestamp: datetime
    mentions: List[str] = field(default_factory=list)
    thread_id: Optional[str] = None
    
    def to_dict(self):
        return {
            'msg_id': self.msg_id,
            'channel': self.channel,
            'author': self.author,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'mentions': self.mentions,
            'thread_id': self.thread_id
        }

class ChannelSystem:
    """Sistema de canais que simula Discord"""
    
    def __init__(self):
        self.channels = {}
        self._load_channels()
    
    def _get_channel_file(self, channel_name: str) -> Path:
        return CHANNELS_DIR / f"#{channel_name}.jsonl"
    
    def _load_channels(self):
        """Carrega todos os canais existentes"""
        for f in CHANNELS_DIR.glob("#*.jsonl"):
            channel_name = f.stem[1:]  # Remove #
            self.channels[channel_name] = []
    
    def post(self, channel: str, author: str, content: str, mentions: List[str] = None):
        """Posta mensagem em um canal"""
        msg = Message(
            msg_id=str(uuid.uuid4())[:8],
            channel=channel,
            author=author,
            content=content,
            timestamp=datetime.now(),
            mentions=mentions or []
        )
        
        # Salvar no arquivo
        channel_file = self._get_channel_file(channel)
        with open(channel_file, 'a') as f:
            f.write(json.dumps(msg.to_dict()) + '\n')
        
        # Atualizar live feed
        self._update_live_feed(msg)
        
        return msg
    
    def read(self, channel: str, limit: int = 50) -> List[Message]:
        """Lê mensagens de um canal"""
        channel_file = self._get_channel_file(channel)
        if not channel_file.exists():
            return []
        
        messages = []
        with open(channel_file) as f:
            lines = f.readlines()
            for line in lines[-limit:]:
                data = json.loads(line)
                messages.append(Message(
                    msg_id=data['msg_id'],
                    channel=data['channel'],
                    author=data['author'],
                    content=data['content'],
                    timestamp=datetime.fromisoformat(data['timestamp']),
                    mentions=data.get('mentions', []),
                    thread_id=data.get('thread_id')
                ))
        
        return messages
    
    def search(self, channel: str, query: str) -> List[Message]:
        """Busca em um canal"""
        messages = self.read(channel, limit=1000)
        return [m for m in messages if query.lower() in m.content.lower()]
    
    def _update_live_feed(self, msg: Message):
        """Atualiza feed de atividade ao vivo"""
        feed_entry = {
            'time': msg.timestamp.strftime('%H:%M'),
            'agent': msg.author,
            'action': msg.content[:100] + ('...' if len(msg.content) > 100 else ''),
            'channel': msg.channel
        }
        
        # Carregar feed existente
        feed = []
        if LIVE_FEED_FILE.exists():
            with open(LIVE_FEED_FILE) as f:
                feed = json.load(f)
        
        # Adicionar no início
        feed.insert(0, feed_entry)
        feed = feed[:100]  # Manter últimas 100 entradas
        
        with open(LIVE_FEED_FILE, 'w') as f:
            json.dump(feed, f, indent=2)

@dataclass
class SwarmTask:
    """Tarefa no sistema de swarm"""
    task_id: str
    original_request: str
    coordinator: Agent
    agents: List[Agent]
    status: str = "pending"  # pending, running, synthesizing, completed
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    final_output: Optional[str] = None

class RalphSwarmSystem:
    """Sistema completo de swarms"""
    
    def __init__(self):
        self.channels = ChannelSystem()
        self.agents: Dict[str, Agent] = {}
        self.active_tasks: Dict[str, SwarmTask] = {}
        self._init_agents()
    
    def _init_agents(self):
        """Inicializa os agents do sistema"""
        # Coordinator (Executivo)
        self.agents['ralph'] = Agent(
            agent_id='ralph',
            name='Ralph',
            role=AgentRole.COORDINATOR,
            model_tier='expensive',
            personality="Gestor estratégico focado em resultados"
        )
        
        # Agents principais (nossa tríade)
        self.agents['scout'] = Agent(
            agent_id='scout',
            name='Scout',
            role=AgentRole.FIND,
            model_tier='cheap',
            personality="Researcher rápido e eficiente"
        )
        
        self.agents['max'] = Agent(
            agent_id='max',
            name='Max',
            role=AgentRole.BUILD,
            model_tier='medium',
            personality="Builder pragmático, entrega código que funciona"
        )
        
        self.agents['maya'] = Agent(
            agent_id='maya',
            name='Maya',
            role=AgentRole.CREATE,
            model_tier='medium',
            personality="Copywriter persuasiva, entende marketing"
        )
    
    def submit_task(self, request: str, user: str = "Jeff") -> SwarmTask:
        """Usuário submete tarefa no #orders"""
        task_id = f"TASK-{uuid.uuid4().hex[:6].upper()}"
        
        # Postar no canal orders
        self.channels.post(
            channel='orders',
            author=user,
            content=request,
            mentions=['ralph']
        )
        
        # Criar task
        task = SwarmTask(
            task_id=task_id,
            original_request=request,
            coordinator=self.agents['ralph'],
            agents=[self.agents['scout'], self.agents['max'], self.agents['maya']]
        )
        
        self.active_tasks[task_id] = task
        
        print(f"📝 Task submetida: {task_id}")
        print(f"   Request: {request[:60]}...")
        
        return task
    
    def coordinate(self, task: SwarmTask):
        """Coordinator analisa e delega"""
        print(f"\n🧠 [COORDINATOR] Analisando task {task.task_id}")
        
        # Analisar request
        request = task.original_request.lower()
        
        # Decidir quais agents spawnar
        agents_needed = []
        
        if any(kw in request for kw in ['research', 'pesquisar', 'analisar', 'concorrentes']):
            agents_needed.append(self.agents['scout'])
        
        if any(kw in request for kw in ['código', 'landing page', 'build', 'implementar']):
            agents_needed.append(self.agents['max'])
        
        if any(kw in request for kw in ['copy', 'escrever', 'linkedin', 'thread']):
            agents_needed.append(self.agents['maya'])
        
        if not agents_needed:
            agents_needed = [self.agents['scout'], self.agents['max'], self.agents['maya']]
        
        # Postar plano no agent-chat
        plan = f"📋 Plano de execução:\n" + \
               "\n".join([f"  • {a.name} ({a.role.value})" for a in agents_needed])
        
        self.channels.post(
            channel='agent-chat',
            author='ralph',
            content=plan,
            mentions=[a.agent_id for a in agents_needed]
        )
        
        task.agents = agents_needed
        task.status = "running"
        
        return agents_needed
    
    def execute_parallel(self, task: SwarmTask):
        """Executa agents em paralelo"""
        print(f"\n⚡ [EXECUTION] Executando {len(task.agents)} agents em paralelo")
        
        def run_agent(agent: Agent):
            """Executa um agent"""
            # Postar início
            self.channels.post(
                channel='agent-chat',
                author=agent.agent_id,
                content=f"🚀 {agent.name} começando..."
            )
            
            # Simular execução
            time.sleep(1)
            
            # Gerar resultado baseado no role
            if agent.role == AgentRole.FIND:
                result = self._simulate_find(task.original_request)
            elif agent.role == AgentRole.BUILD:
                result = self._simulate_build(task.original_request)
            elif agent.role == AgentRole.CREATE:
                result = self._simulate_create(task.original_request)
            else:
                result = f"Resultado de {agent.name}"
            
            # Postar no output
            self.channels.post(
                channel=f"{agent.role.value}-output",
                author=agent.agent_id,
                content=result
            )
            
            # Postar no agent-chat (handoff)
            self.channels.post(
                channel='agent-chat',
                author=agent.agent_id,
                content=f"✅ {agent.name} completou. Resultado em #{agent.role.value}-output",
                mentions=['ralph']
            )
            
            return result
        
        # Executar em paralelo
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(run_agent, task.agents))
        
        return results
    
    def _simulate_find(self, request: str) -> str:
        """Simula agent Find"""
        return f"""🔍 RESEARCH RESULTS

Encontrados 15 concorrentes em análise:
1. Notion - $10/mês, foco em produtividade
2. ClickUp - $5/mês, all-in-one
3. Asana - $11/mês, gerenciamento de projetos

Tendências identificadas:
- Precificação freemium dominante
- Foco em integrações
- Landing pages minimalistas

<RALPH_COMPLETE>"""
    
    def _simulate_build(self, request: str) -> str:
        """Simula agent Build"""
        return f"""🛠️ BUILD RESULTS

Landing page scaffold criado:
- index.html (estrutura base)
- styles.css (design system)
- script.js (interatividade)

Features implementadas:
- Hero section com CTA
- Pricing cards
- FAQ section
- Form de captura

<RALPH_COMPLETE>"""
    
    def _simulate_create(self, request: str) -> str:
        """Simula agent Create"""
        return f"""📝 COPY RESULTS

Headlines testadas:
"Transforme sua produtividade em 30 dias"
"O sistema que 10,000+ profissionais usam"
"Pare de perder tempo com ferramentas complexas"

CTAs:
- "Comece grátis hoje"
- "Ver demo de 2 minutos"
- "Falar com especialista"

<RALPH_COMPLETE>"""
    
    def synthesize(self, task: SwarmTask) -> str:
        """Coordinator consolida tudo em UM resultado"""
        print(f"\n🎯 [SYNTHESIS] Consolidando resultados")
        
        task.status = "synthesizing"
        
        # Ler todos os outputs
        all_outputs = []
        for agent in task.agents:
            messages = self.channels.read(f"{agent.role.value}-output", limit=5)
            for m in messages:
                all_outputs.append(f"[{agent.name}]\n{m.content}")
        
        # Simular síntese (na implementação real, chamaríamos LLM)
        synthesis = f"""# 📦 ENTREGA FINAL - {task.task_id}

## Resumo Executivo
Task: {task.original_request}
Agents envolvidos: {', '.join(a.name for a in task.agents)}
Tempo total: ~3 minutos

## Resultados Consolidados

### 🎯 Research (Scout)
{all_outputs[0] if len(all_outputs) > 0 else 'N/A'}

### 🛠️ Build (Max)
{all_outputs[1] if len(all_outputs) > 1 else 'N/A'}

### 📝 Copy (Maya)
{all_outputs[2] if len(all_outputs) > 2 else 'N/A'}

## Próximos Passos
1. Revisar entregáveis
2. Ajustar conforme feedback
3. Deploy quando aprovado

---
*Entregue por Ralph Swarm v4.1*
"""
        
        # Postar resultado final
        self.channels.post(
            channel='orders',
            author='ralph',
            content=synthesis,
            mentions=['Jeff']
        )
        
        task.final_output = synthesis
        task.status = "completed"
        task.completed_at = datetime.now()
        
        return synthesis
    
    def get_live_feed(self, limit: int = 20) -> List[Dict]:
        """Retorna feed de atividade ao vivo"""
        if LIVE_FEED_FILE.exists():
            with open(LIVE_FEED_FILE) as f:
                feed = json.load(f)
            return feed[:limit]
        return []
    
    def get_dashboard(self) -> Dict:
        """Retorna dados do dashboard"""
        # Contar tarefas de hoje
        today_tasks = [t for t in self.active_tasks.values() 
                      if t.created_at.date() == datetime.now().date()]
        
        # Contar por agent
        agent_activity = {}
        for agent in self.agents.values():
            msgs = self.channels.read(f"{agent.role.value}-output", limit=100)
            agent_activity[agent.name] = len(msgs)
        
        return {
            'today_summary': {
                'tasks': len(today_tasks),
                'completed': len([t for t in today_tasks if t.status == 'completed']),
                'agents_active': len([a for a in self.agents.values()])
            },
            'agent_activity': agent_activity,
            'pending_queue': len([t for t in self.active_tasks.values() if t.status == 'pending'])
        }


def main():
    """Demonstração do sistema"""
    print("🐝 Ralph Swarm v4.1 - Sistema Completo")
    print("=" * 60)
    
    # Inicializar sistema
    swarm = RalphSwarmSystem()
    
    # Submeter task
    task = swarm.submit_task(
        "Research concorrentes de SaaS de produtividade, "
        "criar landing page e escrever copy persuasiva"
    )
    
    # Coordenar
    agents = swarm.coordinate(task)
    
    # Executar em paralelo
    results = swarm.execute_parallel(task)
    
    # Síntese
    final = swarm.synthesize(task)
    
    # Mostrar dashboard
    print("\n" + "=" * 60)
    print("📊 DASHBOARD:")
    dashboard = swarm.get_dashboard()
    print(f"   Tasks hoje: {dashboard['today_summary']['tasks']}")
    print(f"   Completadas: {dashboard['today_summary']['completed']}")
    print(f"   Agents ativos: {dashboard['today_summary']['agents_active']}")
    
    # Mostrar live feed
    print("\n📡 LIVE FEED:")
    for entry in swarm.get_live_feed(limit=5):
        print(f"   {entry['time']} [{entry['agent']}] {entry['action'][:50]}...")
    
    print("\n" + "=" * 60)
    print("✅ Demo concluída!")
    print(f"📁 Canais salvos em: {CHANNELS_DIR}")


if __name__ == '__main__':
    main()
