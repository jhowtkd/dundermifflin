# 🤖 Guia Rápido de Agentes

Referência rápida para escolher o agente certo para cada situação.

> 💡 **Dica:** Use comandos rápidos! Veja [`COMMANDS.md`](./COMMANDS.md) para atalhos como `/review`, `/test`, `/new-feature`.

---

## 🎯 Matriz de Decisão Rápida

```
┌─────────────────────────────────────────────────────────────────────┐
│  PROBLEMA/SITUAÇÃO                    →  AGENTE RECOMENDADO         │
├─────────────────────────────────────────────────────────────────────┤
│  App está lenta                       →  ⚡ bolt                    │
│  Bundle size grande                   →  ⚡ bolt                    │
│  Queries lentas                       →  ⚡ bolt / 🗄️ database-engineer│
├─────────────────────────────────────────────────────────────────────┤
│  Vulnerabilidade encontrada           →  🛡️ sentinel               │
│  Secret hardcoded                     →  🛡️ sentinel               │
│  SQL injection possível               →  🛡️ sentinel               │
├─────────────────────────────────────────────────────────────────────┤
│  Revisar código de PR                 →  🔍 code-reviewer           │
│  Validar padrões de código            →  🔍 code-reviewer           │
├─────────────────────────────────────────────────────────────────────┤
│  Investigar bug                       →  🐛 debugger                │
│  Root cause analysis                  →  🐛 debugger                │
├─────────────────────────────────────────────────────────────────────┤
│  Design de schema SQL                 →  🗄️ database-engineer      │
│  Otimizar queries                     →  🗄️ database-engineer      │
├─────────────────────────────────────────────────────────────────────┤
│  Arquitetura de sistema               →  🏗️ architect              │
│  Trade-offs técnicos                  →  🏗️ architect              │
├─────────────────────────────────────────────────────────────────────┤
│  Feature full-stack                   →  💻 fullstack-developer    │
│  Criar novo app/protótipo             →  ⚡ rapid-prototyper       │
├─────────────────────────────────────────────────────────────────────┤
│  Feature com AI/ML                    →  🤖 ai-engineer            │
│  Integrar LLM                         →  🤖 ai-engineer            │
├─────────────────────────────────────────────────────────────────────┤
│  Pipeline de CI/CD                    →  🔄 cicd-engineer          │
│  Docker/Deploy                        →  🔄 cicd-engineer          │
├─────────────────────────────────────────────────────────────────────┤
│  Design de API                        →  🔌 api-designer           │
│  REST/GraphQL                         →  🔌 api-designer           │
├─────────────────────────────────────────────────────────────────────┤
│  Escrever/melhorar testes             →  🧪 tester                 │
│  Mocks e fixtures                     →  🎭 mocker                 │
│  Testar APIs                          →  🔌 api-tester             │
├─────────────────────────────────────────────────────────────────────┤
│  Problemas de acessibilidade          →  ♿ a11y-specialist        │
│  Internacionalização                  →  🌍 i18n-specialist        │
├─────────────────────────────────────────────────────────────────────┤
│  Interface/UX                         →  🎨 palette                │
│  Refinamento visual                   →  ✨ polish                 │
│  Microcopy/textos                     →  ✍️ ux-writer             │
├─────────────────────────────────────────────────────────────────────┤
│  Pesquisar nova feature               →  🔬 researcher             │
│  Análise de tendências                →  📈 trend-researcher       │
│  Priorizar backlog                    →  📊 sprint-prioritizer     │
├─────────────────────────────────────────────────────────────────────┤
│  Growth/marketing                     →  📈 growth-hacker          │
│  Conteúdo social                      →  ✍️ content-creator       │
│  ASO (App Store)                      →  📱 app-store-optimizer    │
├─────────────────────────────────────────────────────────────────────┤
│  Código morto/limpeza                 →  🧹 janitor                │
│  Upgrade de dependências              →  🔄 migrator               │
│  Otimização de algoritmos             →  🚀 optimizer              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📂 Por Departamento

### 🤖 Autonomous (7 agentes)
Manutenção proativa e autônoma do codebase.

| Agente | Comando | Foco |
|--------|---------|------|
| Bolt | `@bolt` | Performance, bundle, rendering |
| Sentinel | `@sentinel` | Segurança, vulnerabilidades |
| Janitor | `@janitor` | Limpeza de código morto |
| Optimizer | `@optimizer` | Otimização de algoritmos |
| Migrator | `@migrator` | Upgrades, migrações |
| A11y Specialist | `@a11y` | Acessibilidade WCAG |
| i18n Specialist | `@i18n` | Internacionalização |

### 💻 Development (9 agentes)
Construção de features de alta qualidade.

| Agente | Comando | Foco |
|--------|---------|------|
| Code Reviewer | `@reviewer` | Revisão de PRs |
| Database Engineer | `@database` | Schema, queries |
| Architect | `@architect` | System design |
| Debugger | `@debugger` | Investigação de bugs |
| Fullstack Developer | `@fullstack` | Features end-to-end |
| CI/CD Engineer | `@cicd` | Pipelines, deploy |
| AI Engineer | `@ai` | LLMs, ML |
| API Designer | `@api` | REST, GraphQL |
| Rapid Prototyper | `@prototype` | MVPs rápidos |

### 🎨 Design (8 agentes)
Experiência visual e de usuário.

| Agente | Comando | Foco |
|--------|---------|------|
| Palette | `@palette` | Design system |
| Polish | `@polish` | Refinamento UI |
| UX Writer | `@uxwriter` | Microcopy |
| Brand Guardian | `@brand` | Identidade visual |
| UI Designer | `@ui` | Layouts, componentes |
| UX Researcher | `@uxresearch` | Pesquisa de usuário |
| Visual Storyteller | `@visual` | Narrativa visual |
| Whimsy Injector | `@whimsy` | Delícia, easter eggs |

### 📦 Product (4 agentes)
Estratégia e descoberta de produto.

| Agente | Comando | Foco |
|--------|---------|------|
| Researcher | `@research` | Pesquisa de features |
| Feedback Synthesizer | `@feedback` | Análise de feedback |
| Sprint Prioritizer | `@prioritize` | Backlog, roadmap |
| Trend Researcher | `@trends` | Tendências de mercado |

### 📢 Marketing (7 agentes)
Growth e engajamento.

| Agente | Comando | Foco |
|--------|---------|------|
| Growth Hacker | `@growth` | Experimentos, métricas |
| Content Creator | `@content` | Conteúdo multiplataforma |
| App Store Optimizer | `@aso` | ASO |
| TikTok Strategist | `@tiktok` | TikTok |
| Instagram Curator | `@instagram` | Instagram |
| Twitter Engager | `@twitter` | Twitter/X |
| Reddit Community Builder | `@reddit` | Reddit |

### 📋 Project Management (3 agentes)
Coordenação e entrega.

| Agente | Comando | Foco |
|--------|---------|------|
| Studio Producer | `@producer` | Coordenação |
| Project Shipper | `@ship` | Releases |
| Experiment Tracker | `@experiments` | A/B tests |

### ⚙️ Studio Operations (5 agentes)
Operações do estúdio.

| Agente | Comando | Foco |
|--------|---------|------|
| Analytics Specialist | `@analytics` | Dados, relatórios |
| Finance Tracker | `@finance` | Finanças |
| Infrastructure Maintainer | `@infra` | Servers, uptime |
| Legal Compliance Checker | `@legal` | LGPD, compliance |
| Support Responder | `@support` | Suporte ao usuário |

### 🧪 Testing (7 agentes)
Garantia de qualidade.

| Agente | Comando | Foco |
|--------|---------|------|
| Tester | `@tester` | Testes gerais |
| Mocker | `@mocker` | Mocks, fixtures |
| API Tester | `@apitest` | Testes de API |
| Performance Benchmarker | `@benchmark` | Load testing |
| Test Results Analyzer | `@testresults` | Análise |
| Tool Evaluator | `@tools` | Avaliação |
| Workflow Optimizer | `@workflow` | Otimização CI |

### 🎁 Bonus (2 agentes)
Agentes especiais.

| Agente | Comando | Foco |
|--------|---------|------|
| Joker | `@joker` | Humor, easter eggs |
| Studio Coach | `@coach` | Mentoria, crescimento |

---

## 🔄 Workflows Comuns

### Nova Feature
```
@research → @architect → @database → @fullstack → @reviewer → @tester
```

### Bug Crítico
```
@debugger → @fullstack → @reviewer → @tester → @cicd
```

### Manutenção Semanal
```
@sentinel → @janitor → @optimizer → @bolt
```

### Novo Mercado
```
@i18n → @a11y → @uxwriter → @content
```

### Lançamento
```
@ship → @growth → @content → @aso → @twitter
```

---

## 📊 Resumo

- **52 agentes** especializados
- **9 departamentos** organizados
- **100%** em português brasileiro
- **Formato Jules** de alta qualidade

---

**Última atualização:** 2026-02-07
