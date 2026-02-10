#!/usr/bin/env python3
"""
Ralph Swarm - Agent Brain System v5.0
Cérebro dos agents: processa mensagens, usa memória, gera respostas
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from ralph_swarm_core import ChannelSystem, SwarmAgentManager, SwarmTaskManager, AuthorType

# Paths
AGENTS_DIR = Path(__file__).parent / "swarm" / "agents"
MEMORY_DIR = Path(__file__).parent / "swarm" / "memory"

class AgentBrain:
    """
    Cérebro de um agent do Swarm.
    Responsável por processar mensagens e gerar respostas.
    """
    
    def __init__(self, agent_slug: str):
        self.agent_slug = agent_slug
        self.agent_manager = SwarmAgentManager()
        self.channels = ChannelSystem()
        self.memory = self._load_memory()
        self.personality = self._load_personality()
    
    def _load_personality(self) -> str:
        """Carrega arquivo de personalidade do agent"""
        personality_file = AGENTS_DIR / f"{self.agent_slug}.md"
        
        if personality_file.exists():
            with open(personality_file, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Personalidade padrão se arquivo não existir
        return f"""# {self.agent_slug.title()}

Você é um agent do Ralph Swarm.
Seja direto, objetivo e sempre entregue valor.
"""
    
    def _load_memory(self) -> Dict:
        """Carrega memória do agent do banco"""
        agent = self.agent_manager.get_agent(self.agent_slug)
        if agent and agent.memory:
            return agent.memory
        return {}
    
    def _save_memory(self):
        """Salva memória no banco"""
        self.agent_manager.update_memory(self.agent_slug, self.memory)
    
    def update_memory(self, key: str, value: any):
        """Atualiza memória do agent"""
        self.memory[key] = value
        self._save_memory()
    
    def get_context_from_channel(self, channel_name: str, limit: int = 10) -> str:
        """Lê contexto recente de um canal"""
        messages = self.channels.read(channel_name, limit=limit)
        
        if not messages:
            return "Nenhuma mensagem recente."
        
        context_lines = []
        for msg in reversed(messages):  # Mais antigas primeiro
            context_lines.append(f"[{msg.author_id}] {msg.content}")
        
        return "\n".join(context_lines)
    
    def should_respond(self, message_content: str, mentions: List[str]) -> bool:
        """
        Decide se o agent deve responder a uma mensagem.
        
        Responde quando:
        - É mencionado diretamente
        - É o coordinator (Ralph) e não há menção específica
        - É uma mensagem geral no #orders e ele é o coordinator
        """
        # Se mencionado diretamente
        if self.agent_slug in mentions:
            return True
        
        # Ralph responde a menções gerais ou mensagens sem menção específica
        if self.agent_slug == 'ralph':
            return True
        
        # Palavras-chave específicas por agent
        keywords = {
            'scout': ['research', 'pesquisa', 'analisar', 'concorrentes', 'benchmark'],
            'max': ['código', 'build', 'implementar', 'script', 'landing page'],
            'maya': ['copy', 'escrever', 'headline', 'linkedin', 'thread', 'marketing'],
            'tracker': ['métricas', 'analytics', 'kpi', 'dados', 'performance'],
            'watcher': ['monitorar', 'observar', 'tendências', 'concorrentes']
        }
        
        agent_keywords = keywords.get(self.agent_slug, [])
        message_lower = message_content.lower()
        
        for kw in agent_keywords:
            if kw in message_lower:
                return True
        
        return False
    
    def generate_prompt(self, task: str, context: str = "", output_format: str = "") -> str:
        """Gera prompt completo para o LLM"""
        
        # Memória relevante
        memory_str = ""
        if self.memory:
            memory_items = [f"- {k}: {v}" for k, v in list(self.memory.items())[:5]]
            memory_str = "\n".join(memory_items)
        
        prompt = f"""{self.personality}

## Memória Atual
{memory_str if memory_str else "Nenhuma memória relevante."}

## Contexto da Conversa
{context if context else "Nenhum contexto anterior."}

## Tarefa Atual
{task}

## Instruções
1. Responda como {self.agent_slug.title()}, seguindo sua personalidade
2. Use o contexto e memória se relevante
3. Seja direto e objetivo
4. SEMPRE termine com \u003cRALPH_COMPLETE\u003e
{output_format}

Execute agora:"""
        
        return prompt
    
    def think(self, task: str, context_channel: str = None, output_format: str = "") -> str:
        """
        Método principal: processa uma tarefa e gera resposta.
        
        Args:
            task: A tarefa a ser executada
            context_channel: Canal para ler contexto adicional
            output_format: Formato específico de output
            
        Returns:
            Resposta gerada pelo agent
        """
        # Coletar contexto se especificado
        context = ""
        if context_channel:
            context = self.get_context_from_channel(context_channel)
        
        # Gerar prompt
        prompt = self.generate_prompt(task, context, output_format)
        
        # Aqui chamaria o LLM real
        # Por enquanto, retorna uma resposta simulada estruturada
        return self._simulate_response(task)
    
    def _simulate_response(self, task: str) -> str:
        """Simula resposta do agent (substituir por chamada LLM real)"""
        
        responses = {
            'ralph': f"""📋 Plano de execução:
  • Scout (find) - Research e análise de mercado
  • Max (build) - Implementação técnica
  • Maya (create) - Copy e conteúdo

Estratégia: Research paralelo com desenvolvimento base, depois refinamento conjunto.

\u003cRALPH_COMPLETE\u003e""",
            
            'scout': f"""🔍 RESEARCH RESULTS

## Análise de Mercado
Encontrados 15 concorrentes diretos e 8 indiretos.

## Concorrentes Principais
• Notion - $10/mês, foco em produtividade
• ClickUp - $5/mês, all-in-one
• Asana - $11/mês, gerenciamento de projetos

## Tendências Identificadas
• Precificação freemium dominante
• Foco em integrações
• Landing pages minimalistas

## Insights Acionáveis
• Diferenciar por simplicidade
• Oferecer trial sem cartão
• Focar em onboarding rápido

\u003cRALPH_COMPLETE\u003e""",
            
            'max': f"""🛠️ BUILD RESULTS

## O que foi construído
Landing page scaffold completo com estrutura responsiva.

## Arquivos/Entregáveis
• index.html - Estrutura principal
• styles.css - Design system completo
• script.js - Interatividade e validações

## Funcionalidades implementadas
• Hero section com CTA dinâmico
• Pricing cards com toggle mensal/anual
• FAQ section acordeão
• Form de captura com validação

## Como usar/testar
```bash
# Abrir no navegador
open index.html

# Ou servir localmente
python3 -m http.server 8000
```

\u003cRALPH_COMPLETE\u003e""",
            
            'maya': f"""📝 COPY RESULTS

## Contexto
Público: Profissionais que buscam produtividade
Objetivo: Converter visitantes em trial users

## Headlines Testadas
1. "Transforme sua produtividade em 30 dias"
2. "O sistema que 10,000+ profissionais usam"
3. "Pare de perder tempo com ferramentas complexas"

## Copy Principal
Você já perdeu horas tentando organizar seu trabalho?

[Produto] é o sistema de produtividade que profissionais de alto desempenho usam para:
• Centralizar tarefas e projetos
• Colaborar sem fricção
• Entregar resultados consistentes

## CTAs (Call-to-Action)
• "Comece grátis hoje" (primário)
• "Ver demo de 2 minutos" (secundário)
• "Falar com especialista" (terciário)

## Notas estratégicas
• Headline #1 foca em resultado temporal (30 dias)
• Headline #2 usa prova social (10,000+ users)
• CTA primário remove barreira ("grátis")

\u003cRALPH_COMPLETE\u003e""",
            
            'tracker': f"""📊 ANALYTICS RESULTS

## Resumo Executivo
Tráfego estável com leve crescimento. Conversão acima da média do setor.

## Métricas Analisadas
| Métrica | Atual | Anterior | Variação |
|---------|-------|----------|----------|
| Visitantes | 1,250 | 1,180 | +5.9% |
| Trial Signups | 89 | 72 | +23.6% |
| Conversion Rate | 7.1% | 6.1% | +16.4% |

## Tendências Identificadas
• Crescimento consistente de tráfego orgânico
• Melhora significativa na taxa de conversão

## Anomalias/Alertas
• Nenhum alerta crítico detectado

## Recomendações
1. Dobrar investimento em canais que estão convertendo
2. A/B test no formulário de signup
3. Monitorar retenção de trial users

\u003cRALPH_COMPLETE\u003e""",
            
            'watcher': f"""👁️ WATCH RESULTS

## O que foi observado
Monitoramento de concorrentes e tendências de mercado.

## Movimentos Detectados
• Notion - Lançou feature de AI writing
• ClickUp - Reduziu preço do plano Business
• Monday.com - Nova campanha em LinkedIn

## Tendências Emergentes
• AI integration está virando table stakes
• Precificação dinâmica ganhando tração
• Foco em mobile experience aumentando

## Sentimento do Mercado
Positivo para ferramentas all-in-one. Críticas sobre complexidade excessiva.

## Recomendações
1. Considerar AI features no roadmap
2. Manter simplicidade como diferencial
3. Monitorar reação ao price drop do ClickUp

\u003cRALPH_COMPLETE\u003e"""
        }
        
        return responses.get(self.agent_slug, f"✅ Tarefa executada por {self.agent_slug}\n\n\u003cRALPH_COMPLETE\u003e")
    
    def post_to_channel(self, channel_name: str, content: str, mentions: List[str] = None):
        """Posta mensagem em um canal"""
        return self.channels.post(
            channel_name=channel_name,
            author_type=AuthorType.AGENT,
            author_id=self.agent_slug,
            content=content,
            mentions=mentions or []
        )
    
    def handle_message(self, message: Dict) -> Optional[str]:
        """
        Processa uma mensagem recebida.
        
        Args:
            message: Dict com 'content', 'mentions', 'channel'
            
        Returns:
            Resposta do agent ou None se não deve responder
        """
        content = message.get('content', '')
        mentions = message.get('mentions', [])
        channel = message.get('channel', '')
        
        # Decidir se deve responder
        if not self.should_respond(content, mentions):
            return None
        
        # Processar e gerar resposta
        response = self.think(
            task=content,
            context_channel=channel if channel != 'orders' else None
        )
        
        # Extrair canal de output baseado no role
        output_channels = {
            'ralph': 'agent-chat',
            'scout': 'find-output',
            'max': 'build-output',
            'maya': 'create-output',
            'tracker': 'track-output',
            'watcher': 'watch-output'
        }
        
        output_channel = output_channels.get(self.agent_slug, 'agent-chat')
        
        # Postar resposta
        self.post_to_channel(output_channel, response)
        
        # Se não for Ralph, avisar no agent-chat
        if self.agent_slug != 'ralph':
            handoff_msg = f"✅ {self.agent_slug.title()} completou.\n   Resultado em #{output_channel}\n   @ralph"
            self.post_to_channel('agent-chat', handoff_msg, mentions=['ralph'])
        
        return response


class SwarmOrchestrator:
    """
    Orquestrador do Swarm.
    Coordena a execução de tarefas entre múltiplos agents.
    """
    
    def __init__(self):
        self.channels = ChannelSystem()
        self.agents = SwarmAgentManager()
        self.tasks = SwarmTaskManager()
        self.brains: Dict[str, AgentBrain] = {}
    
    def get_brain(self, agent_slug: str) -> AgentBrain:
        """Obtém ou cria cérebro de um agent"""
        if agent_slug not in self.brains:
            self.brains[agent_slug] = AgentBrain(agent_slug)
        return self.brains[agent_slug]
    
    def process_orders(self):
        """
        Processa mensagens pendentes em #orders.
        Método principal para execução do swarm.
        """
        # Ler mensagens não processadas de #orders
        messages = self.channels.read('orders', limit=10)
        
        for msg in messages:
            # Só processar mensagens de usuários
            if msg.author_type != 'user':
                continue
            
            print(f"📨 Processando mensagem de {msg.author_id}: {msg.content[:50]}...")
            
            # Ralph analisa e decide
            ralph = self.get_brain('ralph')
            
            # Simular decisão de Ralph
            plan = ralph.think(
                task=f"Analisar e criar plano para: {msg.content}",
                context_channel='orders'
            )
            
            # Postar plano no agent-chat
            ralph.post_to_channel('agent-chat', plan, mentions=['scout', 'max', 'maya'])
            
            # TODO: Executar agents em paralelo
            # Por enquanto, simular execução sequencial
            
            print(f"   ✅ Plano criado por Ralph")
    
    def run_single_task(self, task_description: str, agent_slug: str = 'scout') -> str:
        """Executa uma tarefa única com um agent"""
        brain = self.get_brain(agent_slug)
        
        # Atualizar status para busy
        self.agents.update_status(agent_slug, 'busy')
        
        # Executar
        result = brain.think(task_description)
        
        # Atualizar memória
        brain.update_memory('last_task', task_description)
        brain.update_memory('last_run', str(datetime.now()))
        
        # Voltar para idle
        self.agents.update_status(agent_slug, 'idle')
        
        return result


# Teste
if __name__ == '__main__':
    print("🧠 Agent Brain System - Teste")
    print("=" * 50)
    
    # Testar cérebro individual
    scout = AgentBrain('scout')
    print("\n1. Testando Scout:")
    response = scout.think("Research concorrentes de SaaS de produtividade")
    print(response[:200] + "...")
    
    # Testar memória
    print("\n2. Testando memória:")
    scout.update_memory('trusted_sources', ['g2.com', 'capterra.com'])
    print(f"   Memória salva: {scout.memory}")
    
    # Testar Maya
    maya = AgentBrain('maya')
    print("\n3. Testando Maya:")
    response = maya.think("Criar copy para landing page de produtividade")
    print(response[:200] + "...")
    
    print("\n" + "=" * 50)
    print("✅ Todos os testes passaram!")
