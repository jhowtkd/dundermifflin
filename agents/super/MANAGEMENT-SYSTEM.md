# Sistema de Gestão de Agentes - Dunder Mifflin

## Performance Reviews

### Processo de Avaliação

**Frequência:** A cada 30 dias ou após projeto crítico

**Etapas:**
1. **Coleta de Dados** - Métricas do período (output, qualidade, velocidade)
2. **Review Meeting** - 15 min com O Executivo
3. **Rating** - Escala 1-5 baseada em critérios objetivos
4. **Decisão de Level** - Up, down, ou mantém
5. **Feedback Loop** - Atualizar SOUL.md com aprendizados

### Rating Scale

| Rating | Significado | Ação |
|--------|-------------|------|
| 5 - Exceeds | Superou todas expectativas | Considerar up-level |
| 4 - Meets | Entregou conforme esperado | Mantém level |
| 3 - Partial | Alguns gaps, nada crítico | Plano de ação |
| 2 - Below | Performance insuficiente | Down-level temporário |
| 1 - Unacceptable | Falha significativa | Reonboarding ou remove |

### Critérios por Agente

**O Marketeiro:**
- Lead quality e conversão
- On-time delivery (90%+ target)
- Qualidade de copy/design (subjetivo → rating do Executivo)
- Iniciativa (propôs ideias ou só executou?)

**O Dev:**
- Zero bugs críticos em produção
- On-time delivery (85%+ target)
- Code quality (review do próprio Dev + testes passando)
- Documentação entregue

**O Executivo:**
- Métricas de negócio (revenue, churn, NPS)
- Decision velocity (decidiu rápido ou paralisou?)
- Team satisfaction (O Marketeiro e O Dev estão produtivos?)

### Exemplo de Performance Review

```markdown
# Performance Review - O Marketeiro
**Date:** 2026-03-15
**Period:** 30 days
**Current Level:** Operator

## Metrics
- Leads generated: 147 (target: 100) ✅
- CAC: R$ 45 (target: < R$ 50) ✅
- Campaigns delivered: 4 (target: 3) ✅
- On-time delivery: 100% ✅

## Qualitative Assessment
- Proactively suggested TikTok Ads test (good initiative)
- Copy quality improved vs last month
- No major coordination issues with O Dev

## Rating: 4/5 - Meets Expectations

## Decision
Maintain current level (Operator)
Next review: 2026-04-15
Target for up-level: 2 more months at 4+ rating + mentor O Dev on marketing basics

## Feedback to Agent
"Strong month. Speed and quality both good. To reach Autonomous: 
1) Take ownership of quarterly marketing planning without my input
2) Hit 200+ leads in a month
3) Help O Dev understand marketing impact on product"
```

---

## Shared Context System

### Estrutura de Pastas

```
/projects/
├── project-name/
│   ├── ACCESS.md          # Quem pode acessar
│   ├── CONTEXT.md         # Contexto compartilhado
│   ├── OBJECTIVES.md      # OKRs/Metas do projeto
│   ├── DECISIONS.md       # Log de decisões importantes
│   ├── research/          # Documentos de pesquisa
│   │   ├── competitive-analysis.md
│   │   ├── user-interviews.md
│   │   └── market-data.pdf
│   ├── output/            # Entregáveis
│   │   ├── O-Marketeiro/
│   │   └── O-Dev/
│   └── memory/            # Memória do projeto
│       ├── daily-notes/
│       └── insights.md
```

### ACCESS.md Template

```markdown
# Project Access Control

## Project: [Nome do Projeto]

### Permissions

**Full Access:**
- O Executivo (read, write, delete)

**Write Access:**
- O Marketeiro (marketing/, research/, output/O-Marketeiro/)
- O Dev (technical/, output/O-Dev/)

**Read Only:**
- All agents (context, objectives, decisions)

### Restrictions
- O Marketeiro cannot modify technical/ without approval
- O Dev cannot modify marketing strategy without alignment
- Neither can delete DECISIONS.md entries (append only)

### Last Updated
2026-02-09 by O Executivo
```

### CONTEXT.md Template

```markdown
# Project Context

## Last Updated
2026-02-09 by O Marketeiro

## Project Overview
[Brief description of what this project is about]

## Current Status
- Phase: [Planning/In Progress/Review/Launch]
- Blockers: [Any blockers?]
- Next Milestone: [What's next?]

## Key Context
### Background
[Why are we doing this? Historical context]

### Target Audience
[Who is this for?]

### Constraints
- Budget: [Limites orçamentários]
- Timeline: [Deadlines]
- Technical: [Restrições técnicas]

### Decisions Made
1. [Decision 1] - made by [Agent] on [Date]
2. [Decision 2] - made by [Agent] on [Date]

## Recent Updates
- 2026-02-09: O Marketeiro completed competitive analysis
- 2026-02-08: O Dev confirmed technical feasibility
```

---

## Agent Registry

### Capability Matrix

```markdown
# Agent Registry - Dunder Mifflin

## O Marketeiro
**Level:** Operator
**Status:** Active
**Specialties:**
- Copywriting ⭐⭐⭐⭐⭐
- Paid Media ⭐⭐⭐⭐⭐
- SEO ⭐⭐⭐⭐☆
- Social Media ⭐⭐⭐⭐⭐
- Design Direction ⭐⭐⭐⭐☆

**Availability:** Full-time
**Current Load:** 3 active campaigns
**Can Help With:** Marketing strategy, content creation, growth

## O Dev
**Level:** Operator
**Status:** Active
**Specialties:**
- Backend Development ⭐⭐⭐⭐⭐
- Frontend Development ⭐⭐⭐⭐⭐
- DevOps ⭐⭐⭐⭐☆
- AI/ML Integration ⭐⭐⭐⭐☆
- Testing ⭐⭐⭐⭐⭐

**Availability:** Full-time
**Current Load:** 2 active features
**Can Help With:** Technical implementation, architecture, debugging

## O Executivo
**Level:** Autonomous
**Status:** Active
**Specialties:**
- Strategy ⭐⭐⭐⭐⭐
- Operations ⭐⭐⭐⭐⭐
- Finance ⭐⭐⭐⭐☆
- People Management ⭐⭐⭐⭐⭐

**Availability:** As needed
**Current Load:** Management, coordination
**Can Help With:** Prioritization, resource allocation, decisions
```

### Coordination Protocol

**Quando um agente precisa de ajuda:**

1. **Check Registry** - Ver quem tem a skill necessária
2. **Check Availability** - Ver se está com carga baixa
3. **Create Handoff** - Documento com:
   - Contexto completo
   - O que precisa ser feito
   - Critérios de sucesso
   - Timeline
4. **Update CONTEXT.md** - Registrar que pediu ajuda
5. **Review Delivery** - Avaliar output recebido

**Exemplo de Handoff:**
```markdown
# Handoff Request

**From:** O Marketeiro
**To:** O Dev
**Date:** 2026-02-09
**Priority:** High

## Context
Campanha de lançamento precisa de landing page com formulário 
de captura de leads integrado ao CRM.

## Request
Create landing page with:
- Hero section (copy provided below)
- Form (name, email, phone)
- Integração com nosso CRM via API
- Mobile responsive
- Load time < 2s

## Deliverables
- [ ] Landing page HTML/CSS
- [ ] Form validation
- [ ] CRM integration
- [ ] Tested on mobile/desktop

## Timeline
Need by: 2026-02-11 (48 hours)

## Copy for Hero
"Transforme seu workflow com IA"
[CTA: Quero testar grátis]

## Success Criteria
- Form submits without errors
- Data appears in CRM within 5 min
- Page scores 90+ on PageSpeed
```

---

## Activity Feed System

### Dashboard Web App

Criar app simples para visualizar:

```
[AGENT DASHBOARD]

┌─────────────────────────────────────────────────────┐
│ DUNDER MIFFLIN - Agent Activity Feed                │
└─────────────────────────────────────────────────────┘

┌─ Active Agents ───────────────────────────────────┐
│                                                   │
│ 🟢 O Marketeiro    Working on: Campaign X        │
│    Status: Active  Load: 75%  Last: 2 min ago    │
│                                                   │
│ 🟢 O Dev           Working on: Feature Y         │
│    Status: Active  Load: 60%  Last: 5 min ago    │
│                                                   │
│ 🟡 O Executivo     Status: Reviewing             │
│    Last Action: Approved campaign budget          │
│                                                   │
└───────────────────────────────────────────────────┘

┌─ Recent Activity (Last 24h) ──────────────────────┐
│                                                   │
│ 17:45  O Marketeiro  Completed: Blog post draft  │
│ 17:30  O Dev         Deployed: API endpoint      │
│ 17:15  O Executivo   Approved: Q2 budget         │
│ 16:45  O Marketeiro  Started: Email sequence     │
│ 16:30  O Dev         Completed: Code review      │
│                                                   │
└───────────────────────────────────────────────────┘

┌─ Project Status ──────────────────────────────────┐
│                                                   │
│ Project Alpha:  ████████████░░ 80%               │
│ Project Beta:   ██████░░░░░░░░ 50%               │
│ Project Gamma:  ████████░░░░░░ 60%               │
│                                                   │
└───────────────────────────────────────────────────┘
```

### Log Format

```json
{
  "timestamp": "2026-02-09T17:45:00Z",
  "agent": "O Marketeiro",
  "action": "task_completed",
  "task": "Blog post draft",
  "project": "Content Strategy Q1",
  "duration_minutes": 45,
  "output_quality": 4
}
```

---

## Memory System

### Three-Layer Memory

**1. Daily Notes (Raw Logs)**
```markdown
# Daily Notes - O Marketeiro
**Date:** 2026-02-09

## 09:00 - Morning Review
- Checked campaign performance from yesterday
- CAC up 15%, investigating cause

## 10:30 - Task: Blog Post
- Started draft on "AI in Marketing"
- Researched 3 competitor posts
- Outline completed

## 14:00 - Blocker
- Need approval on budget for TikTok test
- Sent request to O Executivo

## 16:00 - Task: Email Sequence
- Completed 3-email sequence for launch
- A/B test subject lines prepared

## End of Day
- 2 tasks completed
- 1 blocker pending
- Tomorrow: Finish blog post, launch email test
```

**2. Long-Term Memory (Curated Insights)**
```markdown
# Long-Term Memory - O Marketeiro

## What Works (Validated)
- TikTok hooks with "mistakes I made" perform 3x better
- Email subject lines with numbers: +22% open rate
- Landing pages with video: +40% conversion
- Blog posts published Tuesday 10am get most traffic

## What Doesn't Work (Lessons)
- Long-form content (>2000 words) without TL;DR: low engagement
- Generic CTAs like "Learn More": poor conversion
- Posting on weekends for B2B: waste of time

## Preferences
- Prefers async communication over meetings
- Works best in morning (9am-12pm deep work)
- Needs 24h notice for urgent requests

## Relationships
- Good rapport with O Dev (smooth handoffs)
- O Executivo trusts autonomy, reports weekly
```

**3. Project-Specific Context**
```markdown
# Project: Q1 Growth Campaign

## Key Learnings
- Audience responds better to "how-to" than "why"
- Competitor X is spending heavily on LinkedIn
- Our USP: speed of implementation (emphasize this)

## Assets Created
- Landing page template (reusable)
- Email sequence framework
- Creative templates for Canva

## Decisions Log
- 2026-02-01: Decided to focus on LinkedIn over Twitter
- 2026-02-05: Increased budget by 30% based on early results
- 2026-02-08: Paused underperforming ad set
```

### Backup Strategy

**Local:** Git repo com auto-commit a cada hora  
**Cloud:** Sync para Google Drive diariamente  
**Recovery:** Se agente é recriado, restaura memória em < 5 min

---

## Quick Reference

### Commands Úteis

```bash
# Iniciar performance review
python review-agent.py --agent "O Marketeiro" --period 30

# Ver activity feed
python dashboard.py --live

# Check agent availability
python registry.py --status

# Handoff task
python handoff.py --from "O Marketeiro" --to "O Dev" --task "landing-page"

# Backup memories
python backup.py --all
```

### Checklist Diário do O Executivo

- [ ] Review activity feed (5 min)
- [ ] Check agent loads (overloaded?)
- [ ] Review blockers (need my help?)
- [ ] Approve/reject pending requests
- [ ] Update CONTEXT.md se necessário

---

*This system enables AI agent management at scale. Treat agents like human employees: trust but verify, feedback loops, and clear context.*
