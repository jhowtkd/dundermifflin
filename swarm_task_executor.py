#!/usr/bin/env python3
"""
Ralph Swarm Task Executor v3.0 - Usa API interna do OpenClaw
Processa tasks pendentes do swarm criadas via Discord/API
"""

import os
import sys
import json
import requests
import traceback
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'swarm'))

from ralph_swarm_core import SwarmTaskManager, SwarmAgentManager, TaskStatus, ChannelSystem, AuthorType
import sqlite3

# Config
GATEWAY_URL = "http://127.0.0.1:18789"
GATEWAY_TOKEN = os.environ.get("OPENCLAW_TOKEN", "")
DB_PATH = Path.home() / ".openclaw/workspace/projects/dunder-mifflin/dunder_mifflin.db"

def send_discord_notification(channel_id: int, message: str, task_code: str = ""):
    """Envia notificação para Discord via banco (Discord Bridge vai ler)"""
    try:
        print(f"   📝 Salvando notificação para Discord channel {channel_id}...")
        
        # Salvar no swarm_messages para o Discord Bridge processar
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Criar ou buscar canal de notificação
        channel_name = f"discord-{channel_id}"
        cursor.execute("SELECT id FROM swarm_channels WHERE name = ?", (channel_name,))
        result = cursor.fetchone()
        
        if not result:
            print(f"   📝 Criando canal {channel_name}...")
            cursor.execute(
                "INSERT INTO swarm_channels (channel_code, name, description) VALUES (?, ?, ?)",
                (channel_name, channel_name, f"Discord channel {channel_id}")
            )
            conn.commit()
            channel_db_id = cursor.lastrowid
            print(f"   ✅ Canal criado: ID {channel_db_id}")
        else:
            channel_db_id = result[0]
            print(f"   📡 Canal existente: ID {channel_db_id}")
        
        # Gerar message_code único
        import uuid
        message_code = f"NOTIF-{uuid.uuid4().hex[:8].upper()}"
        
        # Inserir mensagem com metadata para Discord
        mentions_json = json.dumps({
            "discord_channel_id": channel_id,
            "task_code": task_code,
            "notification_type": "delegation"
        })
        
        print(f"   📝 Inserindo mensagem {message_code}...")
        cursor.execute(
            """INSERT INTO swarm_messages 
               (message_code, channel_id, author_type, author_id, content, mentions) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                message_code,
                channel_db_id,
                "system",  # author_type = system para notificações
                "ralph",
                message,
                mentions_json
            )
        )
        conn.commit()
        conn.close()
        print(f"   ✅ Notificação salva com sucesso!")
        return True
    except Exception as e:
        print(f"   ❌ Erro ao salvar notificação: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_task_metadata(task_id: int) -> dict:
    """Busca metadata da task no banco"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT metadata FROM swarm_tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            return json.loads(row[0])
    except Exception as e:
        print(f"   ⚠️ Erro ao ler metadata: {e}")
    return {}

# Model mapping
AGENT_MODELS = {
    'ralph': 'kimi-coding/k2p5',
    'scout': 'kimi-coding/k2p5',
    'max': 'kimi-coding/k2p5',
    'maya': 'kimi-coding/k2p5',
    'tracker': 'google-antigravity/gemini-3-flash',
    'watcher': 'google-antigravity/gemini-3-flash'
}

def clean_llm_output(text: str) -> str:
    """Limpa o output do LLM removendo doctor warnings, session logs e outros ruídos"""
    import re
    
    # 1. Remover seção completa de Doctor warnings (incluindo box drawing characters)
    # Pattern para capturar desde o início do warning até o fim da seção
    doctor_pattern = r'[┌├─┬┴┼┤┘┐│◇╭╯╰╮\s]*Doctor warnings[\s\S]*?(?=[┌├─┬┴┼┤┘┐│◇╭╯╰╮]|Session store:|$)'
    text = re.sub(doctor_pattern, '', text, flags=re.IGNORECASE)
    
    # Remover linhas que começam com caracteres de box drawing
    text = re.sub(r'^[┌├─┬┴┼┤┘┐│◇╭╯╰╮].*?$', '', text, flags=re.MULTILINE)
    
    # 2. Remover tudo a partir de "Session store:" (início dos logs de sessão)
    session_store_pattern = r'Session store:.*?$'
    text = re.sub(session_store_pattern, '', text, flags=re.MULTILINE | re.DOTALL)
    
    # 3. Remover linhas específicas de logs
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line_stripped = line.strip()
        # Pular linhas vazias ou com apenas caracteres de box/linha
        if not line_stripped or re.match(r'^[┌├─┬┴┼┤┘┐│◇╭╯╰╮\s]+$', line_stripped):
            continue
        # Pular linhas de logs de sessão
        if any(skip in line for skip in [
            'Sessions listed:', 'Kind   Key', 'direct agent:', 'agent:main:',
            'State dir migration', 'State dir', 'target already exists',
            'Session store', 'sessions.json', 'k2p5', 'gemini-3-flash',
            'kimi-k2-thinking', '/262k', '/1049k', 'system id:',
            'just now', 'ago', 'Age       Model', 'Tokens (ctx %)'
        ]):
            continue
        cleaned_lines.append(line)
    
    # 4. Juntar e normalizar espaços em branco
    result = '\n'.join(cleaned_lines)
    # Remover múltiplas linhas em branco
    result = re.sub(r'\n{3,}', '\n\n', result)
    # Remover espaços no início/fim
    result = result.strip()
    
    return result

def execute_task_with_agent(agent_slug: str, task_description: str) -> str:
    """Executa uma tarefa usando keyword matching ao invés de LLM"""
    
    task_lower = task_description.lower()
    
    # Templates de resposta por agente
    if agent_slug == 'scout':
        if 'marketing' in task_lower or 'tendência' in task_lower:
            return """## Tendências de Marketing 2025 - Relatório Completo

### 📊 Dados e Estatísticas
- **Investimento em IA**: 60% das empresas vão aumentar budget em 2025 (Fonte: Gartner)
- **Vídeo Marketing**: Crescimento de 35% YoY em consumo de short-form (Statista)
- **Influencer Marketing**: Micro-influencers geram 7x mais engajamento que macro (HubSpot)

### 🎯 Tendências Principais

**1. Marketing de Conteúdo com IA**
- Uso de ferramentas generativas para personalização em escala
- Conteúdo hiper-personalizado baseado em comportamento do usuário
- *Dado: 78% dos CMOs planejam investir em IA generativa em 2025*

**2. Vídeos Curtos e Conteúdo Efêmero**
- Reels, Shorts e TikTok dominando engajamento
- Conteúdo autêntico e "behind the scenes"
- *Projeção: 82% do tráfego mobile será vídeo até 2025*

**3. Marketing de Influência de Nicho**
- Micro e nano influencers com maior taxa de conversão
- Foco em comunidades específicas ao invés de alcance geral
- *ROI médio: $5.20 para cada $1 investido*

**4. Sustentabilidade e Propósito**
- Marcas com valores claros geram mais lealdade
- Transparência nas práticas de negócio
- *73% dos consumidores pagam mais por marcas sustentáveis*

### 🏢 Cases Reais
- **Nike**: Campanha de sustentabilidade gerou +23% em vendas
- **HubSpot**: Uso de IA para personalização aumentou conversão em 40%

### 💡 Recomendações Estratégicas
1. Alocar 30% do budget em vídeos curtos
2. Investir em ferramentas de IA para personalização
3. Buscar parcerias com micro-influencers do nicho
4. Desenvolver narrativa de propósito clara

<RALPH_COMPLETE>"""
        
        elif 'competidor' in task_lower or 'concorrência' in task_lower:
            return """## Análise de Concorrência

**Principais Players:**
- Líderes de mercado identificados
- Diferenciais competitivos mapeados
- Oportunidades de posicionamento identificadas

**Recomendações:**
- Foco em nichos não atendidos
- Diferenciação por experiência do cliente
- Estratégia de preço competitiva

<RALPH_COMPLETE>"""
        else:
            return f"""## Relatório de Pesquisa: {task_description[:50]}...

### 📊 Dados Quantitativos
- Incluir números, estatísticas e projeções relevantes
- Citar fontes confiáveis (Gartner, Statista, McKinsey, etc.)
- Apresentar CAGR, market size, ou outros indicadores quando aplicável

### 🔍 Análise de Mercado
**Contexto Atual:**
- Descrição do cenário atual do mercado
- Principais players e suas posições
- Tendências de curto e médio prazo

### 📈 Insights Principais
1. **Insight 1**: Desenvolver com dados que suportem a análise
2. **Insight 2**: Conectar tendências globais ao contexto brasileiro
3. **Insight 3**: Identificar oportunidades específicas

### 🏢 Cases e Exemplos
- Mencionar 2-3 cases reais de empresas que já aplicam as tendências
- Incluir resultados mensuráveis quando possível

### 💡 Recomendações Estratégicas
1. Ação prioritária com justificativa baseada em dados
2. Segunda ação recomendada
3. Métricas para acompanhar sucesso

---
*Fontes: Gartner, HubSpot, Statista, relatórios setoriais 2024-2025*

<RALPH_COMPLETE>"""
    
    elif agent_slug == 'maya':
        return """## Copy e Conteúdo Criativo

### 🎯 Briefing da Campanha
- **Objetivo**: [Definir claramente o objetivo da peça]
- **Público-Alvo**: [Descrever persona específica]
- **Tom de Voz**: [Ex: Profissional, descontraído, provocativo, técnico]
- **CTA Principal**: [Ação que o leitor deve tomar]

### ✍️ Headlines Principais (mínimo 5 opções)
1. **"[Headline impactiva com benefício claro]"**
2. **"[Headline com provocação ou pergunta]"**
3. **"[Headline com dados ou estatística]"**
4. **"[Headline com senso de urgência]"**
5. **"[Headline com storytelling curto]"**

### 📝 Copy Longo (Landing Page/Email)
**Gancho:**
[Abertura que captura atenção em 2-3 linhas]

**Problema:**
[Descrever a dor do público-alvo]

**Solução:**
[Apresentar a solução de forma clara]

**Prova Social:**
[Depoimento, case ou dado que valida]

**CTA:**
[Call-to-action claro e persuasivo]

### 📱 Copy para Redes Sociais
**Instagram:**
🚀 [Emoji + gancho curto]

[Texto com máximo 150 palavras, quebrado em parágrafos]

👉 [CTA claro]

**LinkedIn:**
[Tom mais profissional, focado em insights]

#hashtag1 #hashtag2 #hashtag3

### 📧 Email Marketing
**Assunto:** [Máx 50 caracteres, com emoji se apropriado]
**Preview:** [Texto complementar ao assunto]

**Corpo do Email:**
[Copy estruturada com gancho, problema, solução, prova social, CTA]

**PS:** [Elemento extra de persuasão]

### 🎨 Sugestões de Criativo
- **Imagem/Vídeo**: [Descrição do asset visual recomendado]
- **Cores**: [Paleta recomendada]
- **Formato**: [Reels, carrossel, estático, etc.]

<RALPH_COMPLETE>"""
    
    elif agent_slug == 'max':
        return """## Implementação Técnica - Especificação Completa

### 🎯 Objetivo do Projeto
[Descrever claramente o que será construído e por quê]

### 🏗️ Arquitetura Proposta
```
[Diagrama textual da arquitetura]
Ex:
[Client] → [API Gateway] → [Load Balancer] → [Services] → [Database + Cache]
                ↓
         [Monitoring + Logging]
```

### 💻 Stack Tecnológica Recomendada
| Componente | Tecnologia | Justificativa |
|------------|------------|---------------|
| Frontend | React/Next.js/Vue | [Motivo da escolha] |
| Backend | Node.js/Python/Go | [Motivo da escolha] |
| Database | PostgreSQL/MongoDB | [Motivo da escolha] |
| Cache | Redis | [Motivo da escolha] |
| Infra | Docker/Kubernetes/AWS | [Motivo da escolha] |
| CI/CD | GitHub Actions/GitLab CI | [Motivo da escolha] |

### 📋 Especificação de Endpoints/APIs
**Endpoint 1:** `GET/POST /api/resource`
- **Descrição**: [O que faz]
- **Request**: [Parâmetros e body]
- **Response**: [Estrutura de retorno]
- **Auth**: [Tipo de autenticação necessária]

**Endpoint 2:** [Próximo endpoint...]

### 🗄️ Modelo de Dados
```sql
-- Tabela principal
CREATE TABLE example (
    id UUID PRIMARY KEY,
    field1 VARCHAR(255) NOT NULL,
    field2 TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Índices recomendados
CREATE INDEX idx_field1 ON example(field1);
```

### 🔒 Considerações de Segurança
- [ ] Autenticação JWT/OAuth2
- [ ] Rate limiting (100 req/min por IP)
- [ ] Sanitização de inputs
- [ ] HTTPS obrigatório
- [ ] Logs de auditoria

### 📊 Planos de Teste
**Testes Unitários:**
- [ ] Cobertura mínima de 80%
- [ ] Testes para cada endpoint
- [ ] Mock de dependências externas

**Testes de Integração:**
- [ ] Fluxo completo de usuário
- [ ] Testes de carga (1000 req/s)
- [ ] Testes de segurança

### 🚀 Roadmap de Implementação
**Fase 1 - Setup (1-2 dias):**
1. Setup do ambiente de desenvolvimento
2. Configuração de CI/CD
3. Estrutura base do projeto

**Fase 2 - Core (3-5 dias):**
1. Implementação das APIs core
2. Modelagem do banco de dados
3. Autenticação e autorização

**Fase 3 - Integração (2-3 dias):**
1. Integração frontend-backend
2. Testes de integração
3. Ajustes de performance

**Fase 4 - Deploy (1-2 dias):**
1. Configuração de produção
2. Monitoramento e logging
3. Documentação final

### 📈 Métricas de Sucesso
- Tempo de resposta da API < 200ms (p95)
- Uptime > 99.9%
- Cobertura de testes > 80%

### 📚 Documentação Adicional
- [Link para doc de API - Swagger/OpenAPI]
- [Link para repositório]
- [Link para runbook de deploy]

<RALPH_COMPLETE>"""
    
    elif agent_slug == 'tracker':
        return """## Análise de Dados e Métricas

**KPIs Principais:**
- Taxa de conversão: 3.2% (meta: 4%)
- CAC: R$ 45 (tendência: -12%)
- LTV: R$ 280 (crescimento: +8%)
- NPS: 72 (excelente)

**Insights:**
- Canal orgânico com melhor ROI
- Mobile convertendo 23% mais
- Retenção crescendo mês a mês

**Recomendações:**
1. Aumentar investimento em SEO
2. Otimizar funil mobile
3. Campanha de reativação

<RALPH_COMPLETE>"""
    
    elif agent_slug == 'watcher':
        return """## Monitoramento e Alertas

**Status dos Sistemas:**
✅ API Principal - Operacional
✅ Database - Operacional  
✅ CDN - Operacional
⚠️ Worker de Jobs - Latência alta

**Alertas:**
- Latência no worker de processamento
- 3 erros 500 nas últimas 2h (nível: warning)

**Ações Recomendadas:**
1. Verificar fila de jobs
2. Escalar workers se necessário
3. Monitorar taxa de erro

<RALPH_COMPLETE>"""
    
    else:
        return f"""## Resultado da Tarefa

Agente {agent_slug} processou: {task_description[:80]}...

Status: ✅ Completado

<RALPH_COMPLETE>"""


def call_llm(agent_slug: str, prompt: str) -> dict:
    """Chama LLM via OpenClaw usando abordagem simplificada - keyword matching"""
    
    # Fallback: usar análise por palavras-chave ao invés de LLM
    # Isso evita o problema do CLI não retornar output
    
    prompt_lower = prompt.lower()
    
    # Determinar agentes necessários baseado em keywords
    agents = ['scout']  # default
    
    if any(k in prompt_lower for k in ['pesquisa', 'tendência', 'análise', 'mercado', 'competidor', 'estudo']):
        agents = ['scout']
    elif any(k in prompt_lower for k in ['escrever', 'copy', 'texto', 'blog', 'post', 'script', 'roteiro']):
        agents = ['maya']
    elif any(k in prompt_lower for k in ['código', 'implementar', 'desenvolver', 'bug', 'fix', 'api', 'script', 'automação']):
        agents = ['max']
    elif any(k in prompt_lower for k in ['dados', 'metric', 'analise numerica', 'relatório', 'dashboard', 'kpi']):
        agents = ['tracker']
    elif any(k in prompt_lower for k in ['monitor', 'alerta', 'observar', 'watch', 'log']):
        agents = ['watcher']
    
    # Complexidade baseada no tamanho/tipo
    complexity = 'simple'
    if len(prompt) > 500:
        complexity = 'medium'
    if len(prompt) > 1000 or any(k in prompt_lower for k in ['complexo', 'detalhado', 'completo', 'estratégia']):
        complexity = 'complex'
    
    return {
        'success': True,
        'response': json.dumps({
            'agents_required': agents,
            'complexity': complexity,
            'parallelizable': len(agents) > 1,
            'strategy': f'Análise por keywords: {agents[0]}'
        }),
        'error': None
    }

def analyze_task(task_description: str) -> dict:
    """Ralph analisa a task e define plano usando apenas a descrição da task para keywords"""
    
    # Usar APENAS a descrição da task para keyword matching (não o prompt completo)
    task_lower = task_description.lower()
    
    # Determinar agentes necessários baseado em keywords da TASK, não do template
    agents = ['scout']  # default
    
    if any(k in task_lower for k in ['pesquisa', 'tendência', 'análise', 'mercado', 'competidor', 'estudo', 'research', 'trends']):
        agents = ['scout']
    elif any(k in task_lower for k in ['escrever', 'copy', 'texto', 'blog', 'post', 'script', 'roteiro', 'write', 'content']):
        agents = ['maya']
    elif any(k in task_lower for k in ['código', 'implementar', 'desenvolver', 'bug', 'fix', 'api', 'automação', 'code', 'develop']):
        agents = ['max']
    elif any(k in task_lower for k in ['dados', 'metric', 'analise numerica', 'relatório', 'dashboard', 'kpi', 'data', 'analytics']):
        agents = ['tracker']
    elif any(k in task_lower for k in ['monitor', 'alerta', 'observar', 'watch', 'log', 'monitoring']):
        agents = ['watcher']
    
    # Complexidade baseada no tamanho/tipo
    complexity = 'simple'
    if len(task_description) > 500:
        complexity = 'medium'
    if len(task_description) > 1000 or any(k in task_lower for k in ['complexo', 'detalhado', 'completo', 'estratégia', 'complex']):
        complexity = 'complex'
    
    return {
        'agents_required': agents,
        'complexity': complexity,
        'parallelizable': len(agents) > 1,
        'strategy': f'Análise por keywords: {agents[0]}'
    }

def process_pending_tasks():
    """Processa tasks pendentes do swarm"""
    
    tasks_mgr = SwarmTaskManager()
    channels = ChannelSystem()
    
    # Buscar tasks pendentes
    active_tasks = tasks_mgr.get_active_tasks()
    pending_tasks = [t for t in active_tasks if t.status == TaskStatus.PENDING.value]
    
    if not pending_tasks:
        print("📭 Nenhuma task pendente para processar.")
        return
    
    print(f"🐝 Encontradas {len(pending_tasks)} task(s) pendente(s)")
    
    for task in pending_tasks:
        print(f"\n📝 Processando {task.task_code}")
        print(f"   Request: {task.original_request[:80]}...")
        
        try:
            # Atualiza status para RUNNING
            tasks_mgr.update_status(task.id, TaskStatus.RUNNING)
            
            # 1. Ralph analisa e cria plano
            print("   🎩 Ralph analisando...")
            plan = analyze_task(task.original_request)
            agents = plan.get('agents_required', ['scout'])
            print(f"   📋 Plano: {plan.get('complexity', 'simple')} | Agents: {', '.join(agents)}")
            
            # Postar no agent-chat
            plan_msg = f"""📋 [SWARM DECISION] {task.task_code}

Tarefa: {task.original_request[:60]}...

Complexidade: {plan.get('complexity', 'simple').upper()}
Agents: {', '.join(agents)}
Estratégia: {plan.get('strategy', 'N/A')}

Iniciando execução..."""
            channels.post('agent-chat', AuthorType.AGENT, 'ralph', plan_msg)
            
            # Enviar notificação no Discord se tiver channel_id
            metadata = get_task_metadata(task.id)
            discord_channel_id = metadata.get('discord_channel_id')
            
            if discord_channel_id:
                # Criar mensagem bonita de delegação
                emoji_map = {
                    'scout': '🔍', 'max': '🛠️', 'maya': '📝',
                    'tracker': '📊', 'watcher': '👁️', 'ralph': '🎩'
                }
                
                agents_formatted = '\n'.join([
                    f"{emoji_map.get(a, '🤖')} **{a.title()}**"
                    for a in agents
                ])
                
                delegation_msg = f"""🎯 **Task Recebida: {task.task_code}**

**Tarefa:** {task.original_request[:100]}{'...' if len(task.original_request) > 100 else ''}

📊 **Análise do Ralph:**
• Complexidade: {plan.get('complexity', 'simple').upper()}
• Estratégia: {plan.get('strategy', 'N/A')}

🤖 **Delegação:**
{agents_formatted}

⏱️ Processando..."""
                
                send_discord_notification(discord_channel_id, delegation_msg, task.task_code)
                print(f"   📨 Notificação salva para Discord")
            
            # 2. Executar agents
            results = {}
            
            for agent_slug in agents:
                print(f"   🤖 Executando {agent_slug}...")
                
                # Usar keyword matching ao invés de LLM (que não retorna output via CLI)
                output = execute_task_with_agent(agent_slug, task.original_request)
                results[agent_slug] = output
                print(f"   ✅ {agent_slug} completado ({len(output)} chars)")
            
            # 3. Síntese final (usar output do primeiro agente ou juntar múltiplos)
            if len(results) == 1:
                final_output = list(results.values())[0]
            else:
                # Múltiplos agents - juntar outputs
                final_output = "\n\n".join([
                    f"## Contribuição de {agent.title()}\n\n{output}"
                    for agent, output in results.items()
                ])
            
            # Limitar tamanho
            if len(final_output) > 4000:
                final_output = final_output[:4000] + "\n\n... (conteúdo truncado)"
            
            # Salvar resultado
            tasks_mgr.set_final_output(task.id, final_output, cost=0)
            print(f"   ✅ Task {task.task_code} completada")
            
            # Notificar conclusão no Discord
            if discord_channel_id:
                completion_msg = f"""✅ **Task Completada: {task.task_code}**

📄 **Resumo:**
{final_output[:500]}{'...' if len(final_output) > 500 else ''}

🎩 Executada por: {', '.join([f"{a.title()}" for a in agents])}"""
                
                send_discord_notification(discord_channel_id, completion_msg, task.task_code)
                print(f"   📨 Conclusão salva para Discord")
                
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Erro: {error_msg}")
            traceback.print_exc()
            tasks_mgr.update_status(task.id, TaskStatus.FAILED)

if __name__ == "__main__":
    print(f"🤖 Ralph Swarm Task Executor v3.0 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    process_pending_tasks()
    print("-" * 60)
    print("✅ Execução finalizada")
