# 🎮 Sistema de Comandos Jules

> Atalhos rápidos para invocar agentes e workflows. Use no chat para ativar especialistas instantaneamente.

---

## 📋 Índice

- [Comandos Rápidos](#-comandos-rápidos)
- [Workflows Completos](#-workflows-completos)
- [Composições](#-composições)
- [Parâmetros](#-parâmetros)
- [Exemplos de Uso](#-exemplos-de-uso)

---

## ⚡ Comandos Rápidos

### 💻 Desenvolvimento

| Comando | Agente | Descrição |
|---------|--------|-----------|
| `/code` | fullstack-developer | Implementa funcionalidade completa |
| `/review` | code-reviewer | Revisa código (segurança, performance, boas práticas) |
| `/debug` | debugger | Investiga e resolve bugs |
| `/arch` | architect | Propõe arquitetura e decisões técnicas |
| `/api` | api-designer | Design de APIs RESTful/GraphQL |
| `/db` | database-engineer | Schema, queries, migrations |
| `/cicd` | cicd-engineer | Pipelines, deploy, infraestrutura |
| `/ai` | ai-engineer | Integração com LLMs e AI |
| `/proto` | rapid-prototyper | MVP rápido para validação |

### 🤖 Automação

| Comando | Agente | Descrição |
|---------|--------|-----------|
| `/bolt` | bolt | Otimização extrema de performance |
| `/secure` | sentinel | Auditoria de segurança |
| `/clean` | janitor | Limpeza de código e dependências |
| `/optimize` | optimizer | Melhoria geral de performance |
| `/migrate` | migrator | Migração de versões/frameworks |
| `/a11y` | a11y-specialist | Acessibilidade WCAG |
| `/i18n` | i18n-specialist | Internacionalização |

### 🎨 Design

| Comando | Agente | Descrição |
|---------|--------|-----------|
| `/ui` | ui-designer | Interface e componentes |
| `/ux` | ux-researcher | Pesquisa de experiência |
| `/write` | ux-writer | Microcopy e conteúdo UX |
| `/polish` | polish | Refinamento visual |
| `/brand` | brand-guardian | Consistência de marca |
| `/colors` | palette | Sistema de cores |
| `/story` | visual-storyteller | Narrativa visual |
| `/fun` | whimsy-injector | Easter eggs e delighters |

### 🧪 Testes

| Comando | Agente | Descrição |
|---------|--------|-----------|
| `/test` | tester | Testes unitários e integração |
| `/mock` | mocker | Mocks e fixtures |
| `/e2e` | api-tester | Testes de API end-to-end |
| `/perf` | performance-benchmarker | Benchmarks de performance |
| `/analyze` | test-results-analyzer | Análise de resultados |
| `/eval` | tool-evaluator | Avaliação de ferramentas |
| `/flow` | workflow-optimizer | Otimização de workflows |

### 📦 Produto

| Comando | Agente | Descrição |
|---------|--------|-----------|
| `/research` | researcher | Pesquisa de mercado/usuário |
| `/feedback` | feedback-synthesizer | Síntese de feedback |
| `/sprint` | sprint-prioritizer | Priorização de backlog |
| `/trends` | trend-researcher | Tendências de mercado |

### 📢 Marketing

| Comando | Agente | Descrição |
|---------|--------|-----------|
| `/grow` | growth-hacker | Estratégias de crescimento |
| `/content` | content-creator | Criação de conteúdo |
| `/aso` | app-store-optimizer | Otimização de app stores |
| `/tiktok` | tiktok-strategist | Conteúdo TikTok |
| `/insta` | instagram-curator | Curadoria Instagram |
| `/twitter` | twitter-engager | Engajamento Twitter/X |
| `/reddit` | reddit-community-builder | Comunidade Reddit |

### 📋 Gestão

| Comando | Agente | Descrição |
|---------|--------|-----------|
| `/ship` | project-shipper | Gerenciamento de releases |
| `/produce` | studio-producer | Coordenação geral |
| `/experiment` | experiment-tracker | Testes A/B e experimentos |

### ⚙️ Operações

| Comando | Agente | Descrição |
|---------|--------|-----------|
| `/analytics` | analytics-specialist | Dados e métricas |
| `/finance` | finance-tracker | Financeiro e custos |
| `/infra` | infrastructure-maintainer | Infraestrutura e uptime |
| `/legal` | legal-compliance-checker | Compliance e LGPD |
| `/support` | support-responder | Suporte ao cliente |

### 🎁 Bonus

| Comando | Agente | Descrição |
|---------|--------|-----------|
| `/joke` | joker | Humor e descontração |
| `/coach` | studio-coach | Mentoria e crescimento |

---

## 🔄 Workflows Completos

Workflows são sequências de agentes que trabalham em cadeia para completar tarefas complexas.

### 🚀 `/new-feature` - Nova Funcionalidade
```
researcher → architect → db → code → review → test
```
**Uso:** `/new-feature autenticação com Google`

**Passos:**
1. 🔬 **researcher** - Pesquisa melhores práticas e soluções existentes
2. 🏗️ **architect** - Propõe arquitetura e decisões técnicas
3. 🗄️ **database-engineer** - Define schema e migrations necessárias
4. 💻 **fullstack-developer** - Implementa a funcionalidade
5. 👀 **code-reviewer** - Revisa código e sugere melhorias
6. 🧪 **tester** - Cria testes unitários e integração

---

### 🐛 `/fix-bug` - Correção de Bug
```
debugger → code → review → test
```
**Uso:** `/fix-bug login não funciona no Safari`

**Passos:**
1. 🔍 **debugger** - Investiga causa raiz do problema
2. 💻 **fullstack-developer** - Implementa a correção
3. 👀 **code-reviewer** - Valida a solução
4. 🧪 **tester** - Adiciona teste de regressão

---

### 🚢 `/release` - Preparar Release
```
review → test → analyze → cicd → ship
```
**Uso:** `/release v2.5.0`

**Passos:**
1. 👀 **code-reviewer** - Review final do código
2. 🧪 **tester** - Executa suite completa de testes
3. 📊 **test-results-analyzer** - Analisa cobertura e qualidade
4. ⚙️ **cicd-engineer** - Prepara pipeline de deploy
5. 🚀 **project-shipper** - Coordena o lançamento

---

### 📱 `/launch-app` - Lançamento de App
```
aso → content → grow → twitter → insta → tiktok
```
**Uso:** `/launch-app novo app de meditação`

**Passos:**
1. 📱 **app-store-optimizer** - Otimiza listing nas stores
2. ✍️ **content-creator** - Cria conteúdo de lançamento
3. 📈 **growth-hacker** - Define estratégia de aquisição
4. 🐦 **twitter-engager** - Campanha no Twitter/X
5. 📸 **instagram-curator** - Conteúdo visual pro Instagram
6. 🎵 **tiktok-strategist** - Vídeos virais pro TikTok

---

### 🎨 `/redesign` - Redesign de Interface
```
ux → research → ui → colors → polish → write → a11y
```
**Uso:** `/redesign página de checkout`

**Passos:**
1. 🔬 **ux-researcher** - Pesquisa problemas atuais
2. 🔍 **researcher** - Benchmarks e referências
3. 🎨 **ui-designer** - Novo design de interface
4. 🎨 **palette** - Sistema de cores atualizado
5. ✨ **polish** - Refinamento e micro-interações
6. ✍️ **ux-writer** - Microcopy e mensagens
7. ♿ **a11y-specialist** - Garante acessibilidade

---

### ⚡ `/performance` - Otimização de Performance
```
perf → bolt → optimize → review → test
```
**Uso:** `/performance página inicial muito lenta`

**Passos:**
1. 📊 **performance-benchmarker** - Mede performance atual
2. ⚡ **bolt** - Otimizações agressivas
3. 🔧 **optimizer** - Melhorias gerais
4. 👀 **code-reviewer** - Valida mudanças
5. 🧪 **tester** - Testes de regressão

---

### 🔒 `/security-audit` - Auditoria de Segurança
```
secure → review → legal → test
```
**Uso:** `/security-audit antes do lançamento`

**Passos:**
1. 🔒 **sentinel** - Scan completo de vulnerabilidades
2. 👀 **code-reviewer** - Review focado em segurança
3. ⚖️ **legal-compliance-checker** - Verifica LGPD/compliance
4. 🧪 **tester** - Testes de segurança

---

### 📊 `/analyze-metrics` - Análise de Métricas
```
analytics → feedback → trends → research
```
**Uso:** `/analyze-metrics último trimestre`

**Passos:**
1. 📊 **analytics-specialist** - Coleta e analisa dados
2. 💬 **feedback-synthesizer** - Sintetiza feedback de usuários
3. 📈 **trend-researcher** - Identifica tendências
4. 🔬 **researcher** - Recomendações baseadas em dados

---

### 🛠️ `/refactor` - Refatoração de Código
```
arch → review → code → clean → test
```
**Uso:** `/refactor módulo de pagamentos`

**Passos:**
1. 🏗️ **architect** - Define nova estrutura
2. 👀 **code-reviewer** - Identifica problemas atuais
3. 💻 **fullstack-developer** - Executa refatoração
4. 🧹 **janitor** - Limpa código morto
5. 🧪 **tester** - Garante que nada quebrou

---

### 🌍 `/go-global` - Internacionalização
```
i18n → a11y → write → test
```
**Uso:** `/go-global suporte a espanhol e francês`

**Passos:**
1. 🌍 **i18n-specialist** - Setup de internacionalização
2. ♿ **a11y-specialist** - RTL e acessibilidade global
3. ✍️ **ux-writer** - Adapta copy para culturas
4. 🧪 **tester** - Testes de localização

---

### 📦 `/mvp` - Criar MVP Rápido
```
research → proto → ui → code → test
```
**Uso:** `/mvp app de lista de tarefas`

**Passos:**
1. 🔬 **researcher** - Valida ideia e mercado
2. ⚡ **rapid-prototyper** - Protótipo funcional
3. 🎨 **ui-designer** - Interface mínima
4. 💻 **fullstack-developer** - Código de produção
5. 🧪 **tester** - Testes essenciais

---

### 🔄 `/upgrade` - Migração de Stack
```
migrate → arch → code → test → cicd
```
**Uso:** `/upgrade React 17 para React 19`

**Passos:**
1. 🔄 **migrator** - Planeja migração passo-a-passo
2. 🏗️ **architect** - Adapta arquitetura se necessário
3. 💻 **fullstack-developer** - Executa mudanças
4. 🧪 **tester** - Valida compatibilidade
5. ⚙️ **cicd-engineer** - Atualiza pipelines

---

## 🎭 Composições

Composições são agentes que trabalham **juntos simultaneamente** em vez de sequencialmente.

### 👥 `/pair` - Pair Programming
```
code + review (simultâneo)
```
**Uso:** `/pair implementar sistema de cache`

O fullstack implementa enquanto o reviewer comenta em tempo real.

---

### 🎨 `/design-dev` - Design + Dev
```
ui + code (simultâneo)
```
**Uso:** `/design-dev novo componente de cards`

Designer e dev trabalham juntos no componente.

---

### 📊 `/data-driven` - Decisão por Dados
```
analytics + research + feedback (simultâneo)
```
**Uso:** `/data-driven devemos adicionar dark mode?`

Três perspectivas de dados para embasar decisão.

---

### 🔒 `/secure-code` - Código Seguro
```
code + secure (simultâneo)
```
**Uso:** `/secure-code endpoint de pagamento`

Implementa já pensando em segurança desde o início.

---

### 🧪 `/tdd` - Test-Driven Development
```
test + code (alternado)
```
**Uso:** `/tdd função de validação de CPF`

Escreve teste, implementa, repete.

---

## 🎛️ Parâmetros

Modifique o comportamento dos comandos com flags.

### Níveis de Rigor

| Flag | Descrição |
|------|-----------|
| `--strict` | Modo rigoroso, sem exceções |
| `--relaxed` | Modo flexível, pragmático |
| `--quick` | Modo rápido, essencial apenas |
| `--deep` | Modo profundo, análise completa |

**Exemplos:**
```
/review --strict      → Review rigoroso, bloqueia qualquer issue
/review --relaxed     → Review pragmático, foca no crítico
/test --quick         → Apenas testes essenciais
/test --deep          → Cobertura completa com edge cases
```

---

### Foco Específico

| Flag | Descrição |
|------|-----------|
| `--security` | Foco em segurança |
| `--performance` | Foco em performance |
| `--accessibility` | Foco em acessibilidade |
| `--mobile` | Foco em mobile |
| `--seo` | Foco em SEO |

**Exemplos:**
```
/review --security    → Review focado em vulnerabilidades
/code --mobile        → Implementação mobile-first
/polish --accessibility → Refinamento focado em a11y
```

---

### Escopo

| Flag | Descrição |
|------|-----------|
| `--file` | Apenas arquivo atual |
| `--component` | Apenas componente |
| `--module` | Módulo inteiro |
| `--project` | Projeto completo |

**Exemplos:**
```
/clean --file         → Limpa apenas arquivo atual
/secure --project     → Audit de segurança do projeto todo
/test --component     → Testes do componente atual
```

---

### Output

| Flag | Descrição |
|------|-----------|
| `--verbose` | Saída detalhada com explicações |
| `--quiet` | Apenas resultado, sem explicações |
| `--json` | Saída em formato JSON |
| `--markdown` | Saída formatada em Markdown |

**Exemplos:**
```
/analyze --verbose    → Análise detalhada com contexto
/test --json          → Resultados em JSON para CI
/review --markdown    → Review formatado pra PR
```

---

### Combinações

Você pode combinar múltiplos parâmetros:

```
/review --strict --security --verbose
/test --deep --component --json
/code --mobile --performance --quick
```

---

## 💡 Exemplos de Uso

### Dia-a-dia de Desenvolvimento

```bash
# Começando feature nova
/new-feature sistema de notificações push

# Bug reportado pelo QA
/fix-bug notificação não aparece no iOS

# PR pronto para review
/review --strict

# Preparando release
/release v1.2.0
```

---

### Melhorando Qualidade

```bash
# Código legado precisa de amor
/refactor módulo de autenticação

# App tá lento
/performance --deep

# Auditoria antes do lançamento
/security-audit --project --verbose
```

---

### Lançamento de Produto

```bash
# Validar ideia
/research viabilidade de app de meditação

# Criar MVP rápido
/mvp --quick

# Preparar marketing
/launch-app

# Analisar resultados
/analyze-metrics primeira semana
```

---

### Design e UX

```bash
# Redesenhar fluxo
/redesign checkout

# Melhorar textos
/write --component botões e mensagens de erro

# Adicionar diversão
/fun easter eggs sutis
```

---

## 🔧 Criando Seus Próprios Comandos

Você pode criar aliases personalizados combinando comandos existentes:

```bash
# Meu workflow de PR
/my-pr = /review --strict + /test --quick + /secure

# Meu check diário
/daily = /clean + /test + /analyze

# Minha pipeline de conteúdo
/my-content = /content + /twitter + /insta
```

---

## 📝 Referência Rápida

```
┌─────────────────────────────────────────────────────────────┐
│                    COMANDOS MAIS USADOS                     │
├─────────────────────────────────────────────────────────────┤
│  /code        Implementar código                            │
│  /review      Revisar código                                │
│  /test        Criar testes                                  │
│  /debug       Investigar bug                                │
│  /fix-bug     Workflow completo de correção                 │
│  /new-feature Workflow completo de feature                  │
│  /ship        Preparar release                              │
├─────────────────────────────────────────────────────────────┤
│                      FLAGS COMUNS                           │
├─────────────────────────────────────────────────────────────┤
│  --strict     Modo rigoroso                                 │
│  --quick      Modo rápido                                   │
│  --deep       Análise profunda                              │
│  --security   Foco em segurança                             │
│  --verbose    Saída detalhada                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Dicas

1. **Comece simples** - Use comandos básicos como `/code`, `/review`, `/test`
2. **Workflows para tarefas grandes** - Use `/new-feature`, `/fix-bug` para tarefas complexas
3. **Flags para personalizar** - Adicione `--strict` ou `--quick` conforme necessário
4. **Combine quando fizer sentido** - `/review --security --strict` para PRs críticos
5. **Crie seus próprios** - Defina aliases para seus workflows frequentes

---

## 🚀 Comece Agora!

```
/coach me ajuda a começar com os comandos
```

O **studio-coach** vai te guiar pelos comandos mais úteis para seu contexto!

---

*Sistema de Comandos Jules v1.0 - 52 agentes, infinitas possibilidades* 🎮
