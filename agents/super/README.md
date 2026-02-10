# Sistema de Gestão de Agentes - Dunder Mifflin Super Agents

Sistema completo para gerenciar 3 super-agentes (O Marketeiro, O Dev, O Executivo) com:
- Performance reviews
- Shared context
- Agent coordination
- Persistent memory

---

## 📁 Estrutura

```
agents/super/
├── SOUL-the-marketeiro.md      # Personalidade + capacidades
├── SOUL-the-dev.md
├── SOUL-the-executivo.md
├── MIGRATION-GUIDE.md          # Como fundir 47 → 3 agentes
├── MANAGEMENT-SYSTEM.md        # Documentação completa
├── agent_dashboard.py          # Dashboard de monitoramento
├── handoff_system.py           # Coordenação entre agentes
├── memory_system.py            # Persistência de memória
├── templates/
│   ├── ACCESS.md               # Template de controle de acesso
│   └── CONTEXT.md              # Template de contexto
├── logs/                       # Logs de atividade
├── handoffs/                   # Handoffs entre agentes
└── memory/                     # Memória dos agentes
    ├── o-marketeiro/
    ├── o-dev/
    └── o-executivo/
```

---

## 🚀 Quick Start

### 1. Dashboard (Ver status)

```bash
cd agents/super
python3 agent_dashboard.py
```

Output:
```
============================================================
  DUNDER MIFFLIN - Agent Dashboard
============================================================

┌─ Active Agents ───────────────────────────────────────────┐
│                                                           │
│ 🟢 O Marketeiro    Level: Operator                        │
│    Load: [███████░░░] 75%                                 │
│    Task: Campaign X                                       │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### 2. Criar Handoff (Coordenação)

```python
from handoff_system import request_help

# O Marketeiro precisa de landing page
handoff_id = request_help(
    from_agent="O Marketeiro",
    to_agent="O Dev",
    task_description="Landing page para campanha X",
    task_type="landing-page",
    deliverables=["HTML/CSS", "Formulário", "Integração CRM"],
    timeline="48 hours",
    priority="High"
)
```

### 3. Gerenciar Memória

```python
from memory_system import memory_system

# Adiciona daily note
memory_system.add_daily_note("O Marketeiro", "Completed blog post")

# Atualiza long-term memory
memory_system.update_longterm_memory(
    "O Marketeiro", 
    "What Works", 
    "TikTok hooks perform 3x better"
)

# Backup
memory_system.backup()
```

### 4. Performance Review

```python
from agent_dashboard import dashboard

# Gera review do último período
dashboard.performance_review("O Marketeiro", period_days=30)
```

Output:
```
============================================================
  PERFORMANCE REVIEW - O Marketeiro
============================================================
Period: Last 30 days
Total Activities: 45
Tasks Completed: 38
Performance Rating: 4.2/5.0
Status: MEETS EXPECTATIONS - Maintain level
```

---

## 📋 Workflows Comuns

### Iniciar Novo Projeto

1. **O Executivo cria pasta do projeto:**
   ```bash
   mkdir projects/nome-do-projeto
   cp templates/ACCESS.md projects/nome-do-projeto/
   cp templates/CONTEXT.md projects/nome-do-projeto/
   ```

2. **Preenche ACCESS.md** (quem pode o quê)

3. **Preenche CONTEXT.md** (objetivos, restrições, contexto)

4. **O Executivo atribui tarefas** para O Marketeiro e/ou O Dev

### Handoff entre Agentes

**Cenário:** O Marketeiro precisa de landing page

```python
# O Marketeiro cria handoff
handoff_id = request_help(
    from_agent="O Marketeiro",
    to_agent="O Dev",
    task_description="...",
    deliverables=["..."],
    timeline="48h"
)

# O Dev completa
from handoff_system import handoff_system
handoff_system.complete_handoff(
    handoff_id,
    output="Landing page entregue em: link",
    quality_rating=5
)
```

### Daily Standup (Async)

Cada agente atualiza no início do dia:

```python
# O Marketeiro
memory_system.add_daily_note("O Marketeiro", """
## Today
- [ ] Finalizar copy para campanha X
- [ ] Revisar métricas da semana
- [ ] Handoff para O Dev (landing page)

## Blockers
- Aguardando aprovação de orçamento
""")
```

### Performance Review Mensal

```bash
# Review de todos os agentes
python3 -c "
from agent_dashboard import dashboard
for agent in ['O Marketeiro', 'O Dev', 'O Executivo']:
    dashboard.performance_review(agent, period_days=30)
"
```

---

## 🔄 Sistema de Memória

### 3 Camadas

1. **Daily Notes** - Raw logs de cada dia
   - Local: `memory/{agent}/daily-notes/YYYY-MM-DD.md`
   - Conteúdo: Atividades, blockers, decisões do dia

2. **Long-Term Memory** - Insights curados
   - Local: `memory/{agent}/long-term-memory.md`
   - Conteúdo: O que funciona, o que não funciona, preferências

3. **Project Context** - Memória específica de projeto
   - Local: `memory/{agent}/projects/{project}/insights.md`
   - Conteúdo: Aprendizados, decisões, assets do projeto

### Backup & Recovery

```python
# Backup diário
memory_system.backup()

# Restaurar agente
memory_system.import_for_agent("O Marketeiro", "backup-file.json")
```

---

## 📊 Métricas de Sucesso

### O Marketeiro
- Leads gerados (mensal)
- CAC (Customer Acquisition Cost)
- ROAS de campanhas
- On-time delivery (%)

### O Dev
- Zero bugs críticos em produção
- Lead time (idea → production)
- Deploy frequency
- Uptime (99.9%+)

### O Executivo
- Revenue (MRR/ARR)
- Churn rate
- Team satisfaction
- Decision velocity

---

## 🎯 Princípios do Sistema

1. **Trust but verify** - Autonomia com accountability
2. **Context is king** - Memória compartilhada elimina cold starts
3. **Feedback loops** - Performance reviews contínuos
4. **Coordination over control** - Agents se ajudam, não precisam de microgerenciamento
5. **Memory persists** - Se recriar um agente, ele tem memória desde o dia 1

---

## 🛠️ Comandos Úteis

```bash
# Ver dashboard
python3 agent_dashboard.py

# Listar handoffs pendentes
python3 -c "
from handoff_system import handoff_system
pending = handoff_system.list_pending(for_agent='O Dev')
for p in pending:
    print(f'{p[\"id\"]}: {p[\"task_type\"]} ({p[\"priority\"]})')
"

# Backup de todas as memórias
python3 -c "
from memory_system import memory_system
memory_system.backup()
"

# Exportar memória de agente (para recriação)
python3 -c "
from memory_system import memory_system
memory_system.export_for_agent('O Marketeiro')
"
```

---

## 📚 Documentação Relacionada

- `SOUL-the-*.md` - Personalidade e capacidades de cada agente
- `MIGRATION-GUIDE.md` - Como migrar dos 47 agentes antigos
- `MANAGEMENT-SYSTEM.md` - Documentação detalhada de gestão

---

*Sistema inspirado em "My Complete Guide to Managing OpenClaw Agent Teams"*
