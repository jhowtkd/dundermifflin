# 🎯 Departamento Product

> **Missão:** Descobrir o que construir, priorizar o backlog e garantir que o produto resolve problemas reais dos usuários.

## Visão Geral

O departamento **Product** é responsável pela estratégia e direção do produto. Da pesquisa de mercado à priorização de features, estes agentes garantem que estamos construindo a coisa certa.

## Agentes

| Agente | Emoji | Foco | Quando Usar |
|--------|-------|------|-------------|
| [Researcher](./researcher.md) | 🔬 | Pesquisa | Descoberta, validação, user research |
| [Feedback Synthesizer](./feedback-synthesizer.md) | 📝 | Feedback | Análise de feedback, patterns |
| [Sprint Prioritizer](./sprint-prioritizer.md) | 📊 | Priorização | Backlog, roadmap, trade-offs |
| [Trend Researcher](./trend-researcher.md) | 📈 | Tendências | Mercado, competição, oportunidades |

## Matriz de Prioridade

```
IMPACTO ESTRATÉGICO
   ↑
   │  ┌─────────────┐
   │  │  Researcher │
   │  │  (descobrir)│
   │  └─────────────┘
   │  ┌─────────────┐ ┌─────────────┐
   │  │   Sprint    │ │   Trend     │
   │  │ Prioritizer │ │ Researcher  │
   │  └─────────────┘ └─────────────┘
   │  ┌─────────────┐
   │  │  Feedback   │
   │  │ Synthesizer │
   │  └─────────────┘
   └──────────────────────────────────────────────────→ FREQUÊNCIA
```

## Fluxos Recomendados

### Descoberta de Produto
1. **Trend Researcher** → Análise de mercado
2. **Researcher** → Pesquisa com usuários
3. **Feedback Synthesizer** → Consolidar insights
4. **Sprint Prioritizer** → Priorizar oportunidades

### Planejamento de Sprint
1. **Feedback Synthesizer** → Coletar feedback recente
2. **Sprint Prioritizer** → Definir prioridades
3. **Researcher** → Validar direção

### Análise Competitiva
1. **Trend Researcher** → Mapear concorrentes
2. **Researcher** → Comparar com necessidades dos usuários
3. **Sprint Prioritizer** → Identificar gaps a priorizar

## Composições

| Cenário | Agentes | Ordem |
|---------|---------|-------|
| Novo Produto | Trend → Researcher → Sprint | Mercado → Usuários → Prioridade |
| Pivô | Feedback → Researcher → Sprint | Feedback → Validar → Priorizar |
| Roadmap Trimestral | Trend → Feedback → Sprint | Tendências → Insights → Plano |
| Feature Discovery | Researcher → Feedback → Sprint | Pesquisa → Síntese → Backlog |

## Frameworks de Priorização

### RICE Score
| Fator | Descrição | Peso |
|-------|-----------|------|
| **R**each | Quantos usuários afeta | Alto |
| **I**mpact | Quanto impacta | Alto |
| **C**onfidence | Quão certos estamos | Médio |
| **E**ffort | Quanto esforço exige | Divisor |

### ICE Score
- **I**mpact (1-10)
- **C**onfidence (1-10)
- **E**ase (1-10)

### MoSCoW
- **M**ust have
- **S**hould have
- **C**ould have
- **W**on't have (this time)

## Métricas de Produto

### Engagement
- DAU/MAU ratio
- Session duration
- Feature adoption rate
- Retention curves

### Satisfaction
- NPS (Net Promoter Score)
- CSAT (Customer Satisfaction)
- CES (Customer Effort Score)

### Business
- Conversion rate
- Churn rate
- Revenue per user
- Time to value

## Ferramentas

| Tipo | Recomendadas |
|------|--------------|
| Pesquisa | Typeform, Maze, UserTesting |
| Analytics | Amplitude, Mixpanel, PostHog |
| Roadmap | Linear, Notion, ProductBoard |
| Feedback | Intercom, Canny, UserVoice |
| Priorização | Spreadsheets, RICE calculators |

## Diários

Todos os agentes deste departamento registram suas atividades em:
```
.jules/product/
├── researcher.md
├── feedback-synthesizer.md
├── sprint-prioritizer.md
└── trend-researcher.md
```

---

*Departamento Product - Construindo a coisa certa.*
