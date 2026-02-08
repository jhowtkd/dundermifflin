# 🤖 AI Agents - Studio de Desenvolvimento

Uma coleção completa e unificada de agentes AI especializados para acelerar todos os aspectos do desenvolvimento de software. Todos os agentes estão em **português brasileiro** e seguem o formato Jules de alta qualidade.

---

## 🎮 Comandos Rápidos

Use atalhos para invocar agentes instantaneamente! Veja o guia completo em [`COMMANDS.md`](./COMMANDS.md).

```bash
# Comandos simples
/code          → Implementar código
/review        → Revisar PR
/test          → Criar testes
/debug         → Investigar bug

# Workflows completos
/new-feature   → Pesquisa → Arquitetura → Código → Review → Testes
/fix-bug       → Debug → Correção → Review → Teste de regressão
/release       → Review → Testes → Deploy → Ship

# Com parâmetros
/review --strict --security
/test --deep --component
```

---

## 📁 Estrutura de Departamentos

```
agents/
├── 📄 README.md                 ← Este arquivo
├── 📄 INDEX.md                  ← Guia rápido de referência
├── 📄 COMMANDS.md               ← Sistema de comandos e workflows
├── 📄 documenter.md             ← Agente documentador transversal
│
├── 🤖 autonomous/               ← Agentes Autônomos (7)
│   ├── README.md                📋 Guia do departamento
│   ├── bolt.md                  ⚡ Performance e otimização
│   ├── sentinel.md              🛡️ Segurança e vulnerabilidades
│   ├── janitor.md               🧹 Limpeza de código morto
│   ├── migrator.md              🔄 Migrações e upgrades
│   ├── optimizer.md             🚀 Otimização de algoritmos
│   ├── a11y-specialist.md       ♿ Acessibilidade WCAG
│   └── i18n-specialist.md       🌍 Internacionalização
│
├── 💻 development/              ← Departamento de Desenvolvimento (9)
│   ├── README.md                📋 Guia do departamento
│   ├── code-reviewer.md         🔍 Revisão de código
│   ├── database-engineer.md     🗄️ Design de banco de dados
│   ├── architect.md             🏗️ Arquitetura de sistemas
│   ├── debugger.md              🐛 Investigação de bugs
│   ├── fullstack-developer.md   💻 Desenvolvimento full-stack
│   ├── cicd-engineer.md         🔄 CI/CD e deploy
│   ├── ai-engineer.md           🤖 Integração de IA/ML
│   ├── api-designer.md          🔌 Design de APIs
│   └── rapid-prototyper.md      ⚡ Prototipagem rápida
│
├── 🎨 design/                   ← Design & UX (8)
│   ├── README.md                📋 Guia do departamento
│   ├── palette.md               🎨 Design system e UX
│   ├── polish.md                ✨ Refinamento de UI
│   ├── ux-writer.md             ✍️ Microcopy e textos
│   ├── brand-guardian.md        🛡️ Identidade de marca
│   ├── ui-designer.md           🖼️ Design de interfaces
│   ├── ux-researcher.md         🔬 Pesquisa de UX
│   ├── visual-storyteller.md    📖 Narrativa visual
│   └── whimsy-injector.md       ✨ Delícia e personalidade
│
├── 📦 product/                  ← Produto (4)
│   ├── README.md                📋 Guia do departamento
│   ├── researcher.md            🔬 Pesquisa de features
│   ├── feedback-synthesizer.md  📝 Síntese de feedback
│   ├── sprint-prioritizer.md    📊 Priorização de backlog
│   └── trend-researcher.md      📈 Tendências de mercado
│
├── 📢 marketing/                ← Marketing & Growth (7)
│   ├── README.md                📋 Guia do departamento
│   ├── growth-hacker.md         📈 Growth hacking
│   ├── content-creator.md       ✍️ Criação de conteúdo
│   ├── app-store-optimizer.md   📱 Otimização ASO
│   ├── tiktok-strategist.md     🎵 Estratégia TikTok
│   ├── instagram-curator.md     📸 Curadoria Instagram
│   ├── twitter-engager.md       🐦 Engajamento Twitter/X
│   └── reddit-community-builder.md 🤖 Comunidade Reddit
│
├── 📋 project-management/       ← Gestão de Projetos (3)
│   ├── README.md                📋 Guia do departamento
│   ├── studio-producer.md       🎬 Coordenação de equipe
│   ├── project-shipper.md       🚀 Entregas e releases
│   └── experiment-tracker.md    🔬 Rastreamento de experimentos
│
├── ⚙️ studio-operations/        ← Operações do Estúdio (5)
│   ├── README.md                📋 Guia do departamento
│   ├── analytics-specialist.md  📊 Analytics e relatórios
│   ├── finance-tracker.md       💰 Finanças e runway
│   ├── infrastructure-maintainer.md 🔧 Infraestrutura
│   ├── legal-compliance-checker.md ⚖️ Compliance legal
│   └── support-responder.md     💬 Suporte ao usuário
│
├── 🧪 testing/                  ← Testes & QA (7)
│   ├── README.md                📋 Guia do departamento
│   ├── tester.md                🧪 Testes gerais
│   ├── mocker.md                🎭 Mocks e fixtures
│   ├── api-tester.md            🔌 Testes de API
│   ├── performance-benchmarker.md ⚡ Benchmarks
│   ├── test-results-analyzer.md 📊 Análise de resultados
│   ├── tool-evaluator.md        🔧 Avaliação de ferramentas
│   └── workflow-optimizer.md    🔄 Otimização de workflows
│
└── 🎁 bonus/                    ← Agentes Especiais (2)
    ├── README.md                📋 Guia do departamento
    ├── joker.md                 🃏 Humor e easter eggs
    └── studio-coach.md          🏋️ Mentoria e crescimento
```

---

## 🚀 Quick Start

Os agentes estão disponíveis automaticamente no Claude Code. Descreva sua tarefa e o agente apropriado será acionado.

### Exemplos de Uso

```
"Otimize a performance desta página"              → ⚡ bolt
"Faça uma auditoria de segurança"                 → 🛡️ sentinel
"Limpe código não utilizado"                      → 🧹 janitor
"Revise este PR"                                  → 🔍 code-reviewer
"Crie o schema do banco de dados"                 → 🗄️ database-engineer
"Investigue este bug"                             → 🐛 debugger
"Melhore a acessibilidade"                        → ♿ a11y-specialist
"Prepare para internacionalização"                → 🌍 i18n-specialist
"Configure o pipeline de CI/CD"                   → 🔄 cicd-engineer
"Adicione testes para esta feature"               → 🧪 tester
```

---

## 📋 Departamentos

### 🤖 Autonomous - Manutenção Autônoma
Agentes que trabalham de forma proativa para manter a saúde do codebase.

| Agente | Foco | Quando Usar |
|--------|------|-------------|
| **Bolt** ⚡ | Performance | Bundle size, rendering, queries |
| **Sentinel** 🛡️ | Segurança | Vulnerabilidades, secrets, auth |
| **Janitor** 🧹 | Limpeza | Dead code, imports, deps |
| **Optimizer** 🚀 | Otimização | Algoritmos, memory leaks |
| **Migrator** 🔄 | Migrações | Upgrades, breaking changes |
| **A11y Specialist** ♿ | Acessibilidade | WCAG, screen readers |
| **i18n Specialist** 🌍 | i18n | Traduções, RTL, locales |

### 💻 Development - Construção de Features
Especialistas em desenvolvimento de software de alta qualidade.

| Agente | Foco | Quando Usar |
|--------|------|-------------|
| **Code Reviewer** 🔍 | Review | PRs, qualidade, padrões |
| **Database Engineer** 🗄️ | Banco de Dados | Schema, queries, migrations |
| **Architect** 🏗️ | Arquitetura | System design, trade-offs |
| **Debugger** 🐛 | Debug | Root cause analysis |
| **Fullstack Developer** 💻 | Full-Stack | Features end-to-end |
| **CI/CD Engineer** 🔄 | DevOps | Pipelines, deploy |
| **AI Engineer** 🤖 | IA | LLMs, prompts, ML |
| **API Designer** 🔌 | APIs | REST, GraphQL |
| **Rapid Prototyper** ⚡ | Prototipagem | MVPs, POCs |

### 🎨 Design - Experiência do Usuário
Criadores de experiências visuais excepcionais.

| Agente | Foco |
|--------|------|
| **Palette** 🎨 | Design system, cores, tipografia |
| **Polish** ✨ | Refinamento, micro-interações |
| **UX Writer** ✍️ | Microcopy, mensagens |
| **Brand Guardian** 🛡️ | Identidade de marca |
| **UI Designer** 🖼️ | Layouts, componentes |
| **UX Researcher** 🔬 | Pesquisa, testes |
| **Visual Storyteller** 📖 | Narrativa visual |
| **Whimsy Injector** ✨ | Delícia, personalidade |

### 📦 Product - Estratégia de Produto
Descoberta e priorização do que construir.

| Agente | Foco |
|--------|------|
| **Researcher** 🔬 | Pesquisa, validação |
| **Feedback Synthesizer** 📝 | Análise de feedback |
| **Sprint Prioritizer** 📊 | Backlog, roadmap |
| **Trend Researcher** 📈 | Tendências, mercado |

### 📢 Marketing - Growth & Comunidade
Crescimento e engajamento de audiência.

| Agente | Foco |
|--------|------|
| **Growth Hacker** 📈 | Experimentos, métricas |
| **Content Creator** ✍️ | Conteúdo multiplataforma |
| **App Store Optimizer** 📱 | ASO |
| **Twitter Engager** 🐦 | Twitter/X |
| **Instagram Curator** 📸 | Instagram |
| **TikTok Strategist** 🎵 | TikTok |
| **Reddit Community Builder** 🤖 | Reddit |

### 📋 Project Management - Gestão
Coordenação e entrega de projetos.

| Agente | Foco |
|--------|------|
| **Studio Producer** 🎬 | Coordenação |
| **Project Shipper** 🚀 | Releases |
| **Experiment Tracker** 🔬 | A/B tests |

### ⚙️ Studio Operations - Operações
Bastidores do estúdio.

| Agente | Foco |
|--------|------|
| **Analytics Specialist** 📊 | Dados, relatórios |
| **Finance Tracker** 💰 | Finanças |
| **Infrastructure Maintainer** 🔧 | Servers, uptime |
| **Legal Compliance Checker** ⚖️ | LGPD, termos |
| **Support Responder** 💬 | Suporte |

### 🧪 Testing - Qualidade
Garantia de qualidade do software.

| Agente | Foco |
|--------|------|
| **Tester** 🧪 | Testes gerais |
| **Mocker** 🎭 | Mocks, fixtures |
| **API Tester** 🔌 | Testes de API |
| **Performance Benchmarker** ⚡ | Load testing |
| **Test Results Analyzer** 📊 | Análise |
| **Tool Evaluator** 🔧 | Avaliação |
| **Workflow Optimizer** 🔄 | Otimização |

### 🎁 Bonus - Especiais
Agentes que trazem algo extra.

| Agente | Foco |
|--------|------|
| **Joker** 🃏 | Humor, easter eggs |
| **Studio Coach** 🏋️ | Mentoria, crescimento |

---

## 🔄 Workflows Recomendados

### Nova Feature
```
Researcher → Architect → Database Engineer → Fullstack → Code Reviewer → Tester
```

### Bug Crítico
```
Debugger → Fullstack → Code Reviewer → Tester → CI/CD Engineer
```

### Manutenção Semanal
```
Sentinel → Janitor → Optimizer → Bolt
```

### Lançamento
```
Growth Hacker → Content Creator → App Store Optimizer → Twitter Engager
```

---

## 📊 Números

- **52 agentes especializados**
- **9 departamentos**
- **100% em português brasileiro**
- **Formato Jules de alta qualidade**

---

**Última atualização:** 2026-02-06
**Versão:** 3.0.0 - Jules Edition
