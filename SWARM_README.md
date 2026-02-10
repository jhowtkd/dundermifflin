# 🐝 Ralph Swarm v4.1 - Sistema Completo

Implementação do **Agent Swarm System** baseado no blueprint de Discord - com canais como database, agent-chat em tempo real, e síntese inteligente.

## 🎯 Filosofia

```
Discord Channels = Database
Agent-Chat = Coordenação real
Synthesis = Um resultado limpo
Live Feed = Visibilidade total
```

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                      VOCÊ (Jeff)                            │
│              Tarefa em linguagem natural                    │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                     #orders                                 │
│              Canal de entrada de tarefas                    │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                  🎩 RALPH (Coordinator)                     │
│  - Analisa tarefa                                           │
│  - Quebra em subtarefas                                     │
│  - Spawna agents em paralelo                                │
│  - Síntese final                                            │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
              ┌────────────┼────────────┐
              ↓            ↓            ↓
┌─────────────────┐ ┌──────────┐ ┌──────────────┐
│   🔍 SCOUT      │ │  🛠️ MAX   │ │   📝 MAYA    │
│   (Find)        │ │  (Build)  │ │  (Create)    │
├─────────────────┤ ├──────────┤ ├──────────────┤
│ #find-output    │ │#build-   │ │ #create-     │
│ #find-logs      │ │ output    │ │ output       │
│ #find-memory    │ │ #build-   │ │ #create-     │
│                 │ │ logs      │ │ logs         │
│                 │ │ #build-   │ │ #create-     │
│                 │ │ memory    │ │ memory       │
└────────┬────────┘ └─────┬────┘ └──────┬───────┘
         │                │             │
         └────────────────┴─────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    #agent-chat                              │
│  "Scout: Encontrei 15 concorrentes, handing to Maya"       │
│  "Maya: Recebido, escrevendo copy agora"                   │
│  "Max: Preciso do conteúdo antes de buildar LP"            │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                  🎯 SYNTHESIS (Ralph)                       │
│  Consolida tudo em UM resultado limpo e polido              │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              📦 ENTREGA FINAL em #orders                    │
│  "Landing page completa com research e copy entregues"     │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Estrutura de Canais

### Canais por Agente (3 canais cada)

| Canal | Propósito | Exemplo |
|-------|-----------|---------|
| `#find-output` | Resultados de research | Lista de concorrentes |
| `#find-logs` | Debug, thought process | Erros, raciocínio |
| `#find-memory` | Conhecimento persistente | Sites confiáveis |

### Canais de Coordenação

| Canal | Função |
|-------|--------|
| `#orders` | Entrada de tarefas do usuário |
| `#agent-chat` | Agents conversam entre si |
| `#drop-links` | Links para research automático |
| `#live-feed` | Atividade em tempo real |

## 🧠 Sistema de Memória

### Dois Layers

```
1. Discord Channels (shared team memory)
   - Todos agents leem/ escrevem
   - Persistente, pesquisável
   
2. Local .md files (private agent memory)
   - Cada agent tem seu memory.json
   - Aprende com cada execução
```

### Exemplo de Memória

```json
{
  "scout": {
    "trusted_sources": ["g2.com", "capterra.com"],
    "avoid_sites": ["spam-site.com"],
    "last_research": "AI tools - 2024-02-10"
  },
  "maya": {
    "writing_style": "direto, persuasivo",
    "best_headlines": ["Transforme...", "Pare de..."]
  }
}
```

## 🔄 Fluxo de Execução

### 1. Entrada (#orders)
```
Jeff: "Crie landing page para SaaS de produtividade"
```

### 2. Coordenação (#agent-chat)
```
Ralph: 📋 Plano de execução:
  • Scout (find) - Research concorrentes
  • Max (build) - Criar LP
  • Maya (create) - Escrever copy
```

### 3. Execução Paralela
```
Scout: 🚀 Começando research...
Max: 🚀 Começando build...
Maya: 🚀 Começando copy...
```

### 4. Handoff Natural
```
Scout: ✅ Research completo
       Encontrei 15 concorrentes
       handing to Maya

Maya: Recebido! Usando dados do Scout
```

### 5. Síntese
```
Ralph: 📦 ENTREGA FINAL
       Consolida outputs de todos agents
       Um documento limpo e polido
```

## 💰 Modelo de Custo (Tier Trick)

| Agente | Modelo | Custo | Uso |
|--------|--------|-------|-----|
| **Ralph** (Coordinator) | Kimi K2 | $$$ | Decisões, síntese |
| **Max** (Build) | Claude Sonnet | $$ | Código complexo |
| **Scout** (Find) | Gemini Flash | $ | Research |
| **Maya** (Create) | Gemini Flash | $ | Copy/escrita |

**Economia:** ~80% em models baratos

## 📊 Dashboard

Acesse: `http://localhost:8888/ralph-swarm-dashboard.html`

Mostra:
- **Today's Summary**: Tasks, threads, snippets
- **Agent Activity**: Progress bars por agent
- **Live Feed**: Atividade em tempo real
- **Channels**: Mensagens por canal

## ⚡ Always On

### Heartbeats (30 min)
```
"Found 5 new competitors while you slept"
"Your thread got 50 replies, themes analyzed"
"Server metrics normal"
```

### Auto-Research (#drop-links)
```
Jeff: drop link em #drop-links
Sistema: Auto-summarize → Extract → Archive
```

## 🚀 Uso

### Python
```python
from ralph_swarm_v4_1 import RalphSwarmSystem

swarm = RalphSwarmSystem()

# Submeter tarefa
task = swarm.submit_task(
    "Research concorrentes e criar landing page"
)

# Coordenar
swarm.coordinate(task)

# Executar
swarm.execute_parallel(task)

# Síntese
result = swarm.synthesize(task)
```

### API (em breve)
```bash
curl -X POST http://localhost:3003/api/swarm \
  -d '{"task": "...", "agents": ["scout", "max", "maya"]}'
```

## 📁 Arquivos

```
dunder-mifflin/
├── ralph_swarm_v4_1.py          # Sistema completo
├── ralph-swarm-dashboard.html   # Dashboard visual
├── swarm/                       # Canais e memória
│   ├── channels/               # #orders, #agent-chat, etc
│   │   ├── #orders.jsonl
│   │   ├── #agent-chat.jsonl
│   │   └── ...
│   └── memory/                 # Memória dos agents
│       ├── scout.json
│       ├── max.json
│       └── maya.json
├── loops/prompts/
│   └── executivo-prompt.md     # Atualizado com swarm
└── SWARM_README.md             # Este arquivo
```

## 🎭 Agents Nomeados

| Nome | Role | Personalidade |
|------|------|---------------|
| **Ralph** | Coordinator | Gestor estratégico, focado em resultados |
| **Scout** | Find | Researcher rápido, curioso |
| **Max** | Build | Builder pragmático, entrega código |
| **Maya** | Create | Copywriter persuasiva, entende marketing |

## ✨ Diferenciais vs Outros Sistemas

| Feature | Outros | Ralph Swarm |
|---------|--------|-------------|
| Comunicação | Via coordinator | **Direct agent-chat** |
| Persistência | Banco de dados | **Canais como DB** |
| Coordenação | Scriptada | **Natural/handoffs** |
| Visibilidade | Logs técnicos | **Live feed visual** |
| Memória | Global | **Per-agent + shared** |

## 📝 TODO

- [ ] Integrar com API Flask (endpoints REST)
- [ ] WebSocket para live feed real-time
- [ ] Sistema de interns temporários
- [ ] Auto-research de links dropados
- [ ] Heartbeats automatizados
- [ ] Integração Telegram para notificações

## 🤝 Integração com Dunder Mifflin

O Swarm evolui o Ralph Loop v3, não substitui:

- **Mesmos agentes**: Dev → Max, Marketeiro → Maya
- **Mesmo executor**: ralph_executor_v3.py reutilizado
- **Mesma API**: Endpoints extendidos
- **Mesmo banco**: SQLite + JSONL channels

---

**Status**: ✅ Core implementado
**Próximo**: Integração API + Dashboard real-time

*Built with 🐝 by Ralph Swarm*
