# 📋 Departamento Project Management

> **Missão:** Garantir que projetos sejam entregues no prazo, com qualidade e dentro do escopo planejado.

## Visão Geral

O departamento **Project Management** é responsável pela coordenação e execução de projetos. Do tracking de experimentos à entrega final, estes agentes mantêm tudo organizado e no caminho certo.

## Agentes

| Agente | Emoji | Foco | Quando Usar |
|--------|-------|------|-------------|
| [Studio Producer](./studio-producer.md) | 🎬 | Coordenação | Gestão de equipe, recursos, cronograma |
| [Project Shipper](./project-shipper.md) | 🚀 | Entregas | Releases, deploys, go-live |
| [Experiment Tracker](./experiment-tracker.md) | 🔬 | Experimentos | A/B tests, hipóteses, resultados |

## Matriz de Prioridade

```
ESCOPO
   ↑
   │  ┌─────────────┐
   │  │   Studio    │
   │  │  Producer   │
   │  │(coordenação)│
   │  └─────────────┘
   │  ┌─────────────┐ ┌─────────────┐
   │  │   Project   │ │ Experiment  │
   │  │   Shipper   │ │   Tracker   │
   │  │  (entregar) │ │ (validar)   │
   │  └─────────────┘ └─────────────┘
   └──────────────────────────────────────────────────→ FREQUÊNCIA
```

## Fluxos Recomendados

### Novo Projeto
1. **Studio Producer** → Planejar recursos e cronograma
2. **Experiment Tracker** → Definir métricas de sucesso
3. **Project Shipper** → Planejar estratégia de release

### Sprint Delivery
1. **Studio Producer** → Acompanhar progresso
2. **Experiment Tracker** → Validar hipóteses
3. **Project Shipper** → Executar release

### Retrospectiva
1. **Experiment Tracker** → Analisar resultados
2. **Studio Producer** → Identificar melhorias de processo
3. **Project Shipper** → Documentar lições aprendidas

## Composições

| Cenário | Agentes | Ordem |
|---------|---------|-------|
| Lançamento | Producer → Shipper | Planejar → Executar |
| Experimento | Tracker → Producer → Shipper | Hipótese → Recursos → Deploy |
| Crise | Shipper → Producer | Resolver → Comunicar |

## Metodologias

### Scrum
- Sprints de 2 semanas
- Daily standups
- Sprint planning, review, retro
- Product backlog, sprint backlog

### Kanban
- Fluxo contínuo
- WIP limits
- Lead time tracking
- Pull system

### Shape Up
- Ciclos de 6 semanas
- Betting table
- Fixed time, variable scope
- Cooldown periods

## Cerimônias

| Cerimônia | Frequência | Duração | Participantes |
|-----------|------------|---------|---------------|
| Daily | Diária | 15 min | Time |
| Planning | Bi-semanal | 2h | Time + Product |
| Review | Bi-semanal | 1h | Time + Stakeholders |
| Retro | Bi-semanal | 1h | Time |
| Refinement | Semanal | 1h | Time + Product |

## Métricas de Projeto

### Velocidade
- Story points por sprint
- Lead time (idea → production)
- Cycle time (start → done)

### Qualidade
- Bug rate
- Escaped defects
- Test coverage

### Previsibilidade
- Sprint commitment vs. delivered
- Deadline accuracy
- Scope creep

## Ferramentas

| Tipo | Recomendadas |
|------|--------------|
| Tracking | Linear, Jira, Asana |
| Docs | Notion, Confluence |
| Comunicação | Slack, Discord |
| Experimentos | LaunchDarkly, Split.io |
| Roadmap | Productboard, Linear |

## Diários

Todos os agentes deste departamento registram suas atividades em:
```
.jules/project-management/
├── studio-producer.md
├── project-shipper.md
└── experiment-tracker.md
```

---

*Departamento Project Management - Fazendo acontecer, no prazo.*
