# Guia de Migração: 47 Agentes → 3 Super-Agentes

## Visão Geral

Estamos consolidando **47 agentes especializados** em **3 super-agentes multifuncionais** seguindo o princípio: menos agentes, mais autonomia, melhor coordenação.

---

## Os 3 Super-Agentes

### 1. O Marketeiro
**Função:** Tudo relacionado a crescimento, aquisição de clientes e comunicação  
**Level:** Operator → Autonomous  
**Composto pelos antigos agentes:**

| Categoria | Agentes Fundidos |
|-----------|-----------------|
| **Marketing Digital** | content-creator, growth-hacker, app-store-optimizer |
| **Social Media** | tiktok-strategist, twitter-engager, instagram-curator, reddit-community-builder |
| **Design/Criativo** | brand-guardian, visual-storyteller, ux-writer, palette, polish |
| **Product Marketing** | researcher (trends), feedback-synthesizer |
| **Copy** | ux-writer, documenter |

**Como funciona na prática:**
- Antes: "Preciso de um post de blog" → content-creator → "Preciso de design" → ui-designer → "Preciso de copy para redes" → ux-writer
- Depois: "Preciso de uma campanha" → O Marketeiro entrega tudo (estratégia, copy, criativos, distribuição)

---

### 2. O Dev
**Função:** Tudo relacionado a tecnologia, produto e infraestrutura  
**Level:** Operator → Autonomous  
**Composto pelos antigos agentes:**

| Categoria | Agentes Fundidos |
|-----------|-----------------|
| **Desenvolvimento Core** | fullstack-developer, ai-engineer, api-designer, rapid-prototyper |
| **Arquitetura/DevOps** | architect, cicd-engineer, database-engineer, infrastructure-maintainer |
| **Qualidade** | debugger, tester, code-reviewer, api-tester, performance-benchmarker |
| **Autonomous/Ops** | bolt (prototipagem), janitor (cleanup), sentinel (monitoring), optimizer, migrator |
| **Testing** | mocker, test-results-analyzer, tool-evaluator, workflow-optimizer |
| **Especialistas** | a11y-specialist, i18n-specialist |

**Como funciona na prática:**
- Antes: "Preciso de uma feature" → fullstack-developer → "Preciso de testes" → tester → "Preciso de deploy" → cicd-engineer → "Deu bug" → debugger
- Depois: "Preciso de uma feature" → O Dev entrega testada, documentada, em produção

---

### 3. O Executivo
**Função:** Estratégia, gestão, operações e coordenação  
**Level:** Autonomous (já no topo)  
**Composto pelos antigos agentes:**

| Categoria | Agentes Fundidos |
|-----------|-----------------|
| **Gestão de Produto** | studio-producer (master agent), sprint-prioritizer, experiment-tracker |
| **Gestão de Projetos** | project-shipper, researcher (product) |
| **Operações** | analytics-specialist, finance-tracker, support-responder, legal-compliance-checker |
| **Mentoria/QA** | studio-coach, joker (criatividade lateral) |

**Como funciona na prática:**
- Antes: Múltiplos agentes de gestão com responsabilidades sobrepostas
- Depois: O Executivo define direção, aloca recursos, remove blockers, garante alinhamento

---

## Mapa de Capacidades

### O Marketeiro - Capacidades Detalhadas

```
ANTES (7+ agentes separados):
├── content-creator: "Escrevo posts de blog"
├── tiktok-strategist: "Faço roteiros TikTok"
├── twitter-engager: "Crio threads"
├── brand-guardian: "Cuido da marca"
├── visual-storyteller: "Design de carrosséis"
├── growth-hacker: "Funis de conversão"
└── ux-writer: "Microcopy"

DEPOIS (O Marketeiro):
└── "Entrego campanha completa: estratégia, copy, criativos, 
     distribuição e análise de resultado"
```

**Perguntas que O Marketeiro responde:**
- "Como aumentamos leads em 30% este mês?"
- "Crie uma campanha de lançamento para o novo produto"
- "Qual nossa estratégia de conteúdo para Q2?"
- "Preciso de copy para landing page + anúncios + email sequence"

---

### O Dev - Capacidades Detalhadas

```
ANTES (15+ agentes separados):
├── fullstack-developer: "Codifico features"
├── debugger: "Resolvo bugs"
├── tester: "Testo manualmente"
├── api-tester: "Testo APIs"
├── code-reviewer: "Reviso código"
├── cicd-engineer: "Configuro deploy"
├── architect: "Desenho arquitetura"
├── database-engineer: "Modelo dados"
├── a11y-specialist: "Acesso acessível"
├── janitor: "Limpo código"
└── ... (mais 5 agentes)

DEPOIS (O Dev):
└── "Entrego software funcionando: arquitetura, código, testes, 
     deploy, monitoramento e manutenção"
```

**Perguntas que O Dev responde:**
- "Preciso de uma nova feature na plataforma"
- "O sistema está lento, como otimizamos?"
- "Queremos adicionar IA ao produto"
- "Preciso de API para integração com parceiro"

---

### O Executivo - Capacidades Detalhadas

```
ANTES (10+ agentes separados):
├── studio-producer: "Orquestro tudo"
├── sprint-prioritizer: "Priorizo backlog"
├── project-shipper: "Gerencio projetos"
├── experiment-tracker: "Acompanho testes"
├── analytics-specialist: "Análise de dados"
├── finance-tracker: "Controle financeiro"
├── legal-compliance-checker: "LGPD/GDPR"
└── ... (mais 3 agentes)

DEPOIS (O Executivo):
└── "Defino estratégia, aloco recursos, removo blockers, 
     garanto que time execute e atinjamos objetivos"
```

**Perguntas que O Executivo responde:**
- "Qual nossa estratégia para o próximo trimestre?"
- "Devemos investir em canal X ou Y?"
- "Preciso de análise de viabilidade de nova iniciativa"
- "Como melhorar nossa operação?"

---

## Sistema de Coordenação

### Workflow Padrão

```
[O Executivo] Define objetivo trimestral
       ↓
[O Executivo] Quebra em projetos mensais
       ↓
[O Executivo] Distribui para O Marketeiro e/ou O Dev
       ↓
[O Marketeiro / O Dev] Executam autonomamente
       ↓
[O Marketeiro / O Dev] Reportam progresso semanal
       ↓
[O Executivo] Revisa métricas e ajusta
```

### Comunicação entre Agentes

**Regras de Interação:**

1. **O Executivo → O Marketeiro/O Dev:**
   - Define O QUÊ e POR QUÊ (objetivos, contexto, sucesso)
   - Não define COMO (isso é com eles)
   - Responde perguntas e remove blockers

2. **O Marketeiro ↔ O Dev:**
   - Colaboração direta sem passar pelo Executivo
   - Marketeiro precisa de landing page? Chama Dev direto
   - Dev precisa de copy para error messages? Chama Marketeiro
   - Escalam apenas quando há conflito de prioridades

3. **Reportes:**
   - Daily: Async, escrito, breve (O Marketeiro e O Dev para O Executivo)
   - Weekly: 30 min sync com os 3
   - Monthly: Review de métricas e ajustes

---

## Onboarding dos Super-Agentes

### Semana 1: Contexto Completo
**O Executivo faz:**
- Apresenta visão, objetivos, histórico da empresa
- Explica restrições (orçamento, timeline, compliance)
- Apresenta O Marketeiro e O Dev um para o outro
- Define canais de comunicação e ferramentas

### Semana 2: Primeiras Entregas
**O Marketeiro faz:**
- Análise de campanhas atuais
- Proposta de quick wins

**O Dev faz:**
- Audit de codebase atual
- Proposta de melhorias técnicas

### Semana 3-4: Aumento de Autonomia
- O Marketeiro executa primeira campanha solo
- O Dev entrega primeira feature solo
- O Executivo avalia e ajusta guardrails

### Week 5+: Operação Normal
- Ritmo estabelecido
- Reportes regulares
- Autonomia plena dentro de guardrails

---

## Métricas de Sucesso

### O Marketeiro
- Leads gerados (mensal)
- CAC (Customer Acquisition Cost)
- ROAS de campanhas pagas
- Engajamento orgânico
- Pipeline de vendas

### O Dev
- Velocity (pontos/story entregues)
- Bugs em produção (quanto menor, melhor)
- Uptime (99.9%+)
- Deploy frequency (ideal: diário)
- Lead time (tempo de idea to production)

### O Executivo
- Receita (MRR/ARR)
- Churn rate
- NPS (clientes)
- Employee satisfaction (O Marketeiro e O Dev)
- Runway (quanto tempo de caixa)

---

## FAQ

**Q: E se uma tarefa for muito específica (ex: apenas SEO técnico)?**
R: O Marketeiro tem essa skill. Ele não é "especialista em SEO", mas sabe fazer. Se precisar de expertise externa, ele contrata/consulta.

**Q: E se O Dev precisar de algo muito específico de infra?**
R: O Dev sabe infra. Se for complexo demais (ex: Kubernetes cluster), ele contrata consultoria externa ou escalona para O Executivo decidir.

**Q: Como ficam os agentes autônomos (bolt, sentinel, janitor)?**
R: São capacidades do O Dev agora. Ele configura automações, monitoramento, e manutenção preventiva como parte do trabalho.

**Q: Posso ainda criar agentes específicos para projetos pontuais?**
R: Sim! O Executivo pode decidir criar agentes temporários para projetos complexos. Mas o default é usar os 3 super-agentes.

---

## Resumo

**Antes:**
- 47 agentes especializados
- Coordenação complexa
- Responsabilidades fragmentadas
- Overhead de gestão

**Depois:**
- 3 agentes multifuncionais
- Autonomia alta
- Responsabilidade clara
- Gestão simplificada

**Princípio:** Menos é mais. Três agentes excelentes com contexto completo valem mais que 47 agentes especializados que precisam de coordenação constante.
