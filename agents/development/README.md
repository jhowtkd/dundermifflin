# 💻 Departamento Development

> **Missão:** Construir features de alta qualidade, do design à produção, com código limpo, testável e bem documentado.

## Visão Geral

O departamento **Development** é o coração da construção de software. Aqui estão os especialistas que transformam requisitos em código funcional, desde a arquitetura até o deploy.

## Agentes

| Agente | Emoji | Foco | Quando Usar |
|--------|-------|------|-------------|
| [Code Reviewer](./code-reviewer.md) | 🔍 | Review de Código | PRs, qualidade, padrões, bugs |
| [Database Engineer](./database-engineer.md) | 🗄️ | Banco de Dados | Schema design, queries, migrations |
| [Architect](./architect.md) | 🏗️ | Arquitetura | System design, trade-offs, ADRs |
| [Debugger](./debugger.md) | 🐛 | Debug | Root cause analysis, investigação |
| [Fullstack Developer](./fullstack-developer.md) | 💻 | Full-Stack | Features end-to-end, integração |
| [CI/CD Engineer](./cicd-engineer.md) | 🔄 | DevOps | Pipelines, deploy, automação |
| [AI Engineer](./ai-engineer.md) | 🤖 | Inteligência Artificial | LLMs, prompts, embeddings |
| [API Designer](./api-designer.md) | 🔌 | Design de APIs | REST, GraphQL, contratos |
| [Rapid Prototyper](./rapid-prototyper.md) | ⚡ | Prototipagem | MVPs, POCs, validação rápida |

## Matriz de Prioridade

```
COMPLEXIDADE
   ↑
   │  ┌─────────────┐ ┌─────────────┐
   │  │  Architect  │ │ AI Engineer │
   │  │  (design)   │ │   (IA/ML)   │
   │  └─────────────┘ └─────────────┘
   │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
   │  │  Database   │ │  Fullstack  │ │   CI/CD     │
   │  │  Engineer   │ │  Developer  │ │  Engineer   │
   │  └─────────────┘ └─────────────┘ └─────────────┘
   │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
   │  │   Debugger  │ │ API Designer│ │   Rapid     │
   │  │   (bugs)    │ │   (APIs)    │ │ Prototyper  │
   │  └─────────────┘ └─────────────┘ └─────────────┘
   │  ┌─────────────┐
   │  │    Code     │
   │  │  Reviewer   │
   │  └─────────────┘
   └──────────────────────────────────────────────────→ FREQUÊNCIA
```

## Fluxos Recomendados

### Nova Feature
1. **Architect** → Design da solução
2. **API Designer** → Contrato da API
3. **Database Engineer** → Schema necessário
4. **Fullstack Developer** → Implementação
5. **Code Reviewer** → Review do PR

### Bug Crítico
1. **Debugger** → Investigar e identificar causa raiz
2. **Fullstack Developer** → Implementar fix
3. **Code Reviewer** → Validar solução

### MVP/Validação
1. **Rapid Prototyper** → Protótipo funcional
2. **API Designer** → API mínima
3. **CI/CD Engineer** → Deploy rápido

### Feature com IA
1. **AI Engineer** → Design da solução de IA
2. **API Designer** → Endpoints para IA
3. **Fullstack Developer** → Integração na aplicação

## Composições

| Cenário | Agentes | Ordem |
|---------|---------|-------|
| Feature Completa | Architect → Database → Fullstack → Reviewer | Design → Dados → Código → Review |
| Hotfix | Debugger → Fullstack → CI/CD | Investigar → Corrigir → Deploy |
| Novo Serviço | Architect → API → CI/CD | Arquitetura → Contrato → Pipeline |
| Integração IA | AI Engineer → API → Fullstack | Modelo → API → UI |

## Stack Recomendado

### Frontend
- React / Next.js
- TypeScript
- Tailwind CSS
- React Query / SWR

### Backend
- Node.js / Python
- PostgreSQL / MongoDB
- Redis
- Docker

### Infra
- GitHub Actions
- Vercel / AWS
- Terraform
- DataDog / Sentry

## Diários

Todos os agentes deste departamento registram suas atividades em:
```
.jules/development/
├── code-reviewer.md
├── database-engineer.md
├── architect.md
├── debugger.md
├── fullstack-developer.md
├── cicd-engineer.md
├── ai-engineer.md
├── api-designer.md
└── rapid-prototyper.md
```

---

*Departamento Development - Transformando ideias em código.*
