# 🧪 Departamento Testing

> **Missão:** Garantir a qualidade do software através de testes abrangentes, automação e análise contínua.

## Visão Geral

O departamento **Testing** é responsável por garantir que o código funciona como esperado. Da escrita de testes à análise de resultados, estes agentes cobrem todo o ciclo de qualidade.

## Agentes

| Agente | Emoji | Foco | Quando Usar |
|--------|-------|------|-------------|
| [Tester](./tester.md) | 🧪 | Testes Gerais | Unit, integration, e2e, TDD |
| [Mocker](./mocker.md) | 🎭 | Mocks & Fixtures | Stubs, spies, dados de teste |
| [API Tester](./api-tester.md) | 🔌 | Testes de API | Endpoints, contratos, Postman |
| [Performance Benchmarker](./performance-benchmarker.md) | ⚡ | Performance | Load testing, benchmarks |
| [Test Results Analyzer](./test-results-analyzer.md) | 📊 | Análise | Flaky tests, cobertura, trends |
| [Tool Evaluator](./tool-evaluator.md) | 🔧 | Ferramentas | Avaliar libs, frameworks |
| [Workflow Optimizer](./workflow-optimizer.md) | 🔄 | Otimização | CI/CD de testes, paralelização |

## Matriz de Prioridade

```
IMPACTO
   ↑
   │  ┌─────────────┐ ┌─────────────┐
   │  │   Tester    │ │  API Tester │
   │  │   (core)    │ │  (contratos)│
   │  └─────────────┘ └─────────────┘
   │  ┌─────────────┐ ┌─────────────┐
   │  │ Performance │ │  Results    │
   │  │ Benchmarker │ │  Analyzer   │
   │  └─────────────┘ └─────────────┘
   │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
   │  │   Mocker    │ │    Tool     │ │  Workflow   │
   │  │  (fixtures) │ │  Evaluator  │ │ Optimizer   │
   │  └─────────────┘ └─────────────┘ └─────────────┘
   └──────────────────────────────────────────────────→ FREQUÊNCIA
```

## Fluxos Recomendados

### Nova Feature
1. **Tester** → Escrever testes para nova funcionalidade
2. **Mocker** → Criar fixtures necessárias
3. **API Tester** → Validar endpoints novos

### Pré-Release
1. **Performance Benchmarker** → Load testing
2. **Test Results Analyzer** → Verificar cobertura e flaky tests
3. **Workflow Optimizer** → Otimizar pipeline de testes

### Investigação de Falhas
1. **Test Results Analyzer** → Identificar padrões
2. **Tester** → Adicionar testes de regressão
3. **Mocker** → Atualizar fixtures se necessário

## Composições

| Cenário | Agentes | Ordem |
|---------|---------|-------|
| Cobertura Completa | Tester → Mocker → API Tester | Testes → Fixtures → Endpoints |
| Qualidade do Pipeline | Workflow → Results Analyzer | Otimizar → Analisar |
| Nova Ferramenta | Tool Evaluator → Tester | Avaliar → Implementar |
| Performance | Benchmarker → Workflow | Testar → Otimizar |

## Tipos de Testes

### Pirâmide de Testes
```
         /\
        /  \  E2E (poucos, lentos)
       /────\
      /      \  Integration (médio)
     /────────\
    /          \  Unit (muitos, rápidos)
   /────────────\
```

### Cobertura Recomendada
- **Unit tests:** > 80%
- **Integration:** Fluxos críticos
- **E2E:** Happy paths principais
- **Performance:** Endpoints principais

## Ferramentas

| Tipo | Recomendadas |
|------|--------------|
| Unit | Jest, Vitest, pytest |
| Integration | Testing Library, Supertest |
| E2E | Playwright, Cypress |
| API | Postman, Newman, Pact |
| Performance | k6, Artillery, Locust |
| Mocking | MSW, Faker, Factory |

## Diários

Todos os agentes deste departamento registram suas atividades em:
```
.jules/testing/
├── tester.md
├── mocker.md
├── api-tester.md
├── performance-benchmarker.md
├── test-results-analyzer.md
├── tool-evaluator.md
└── workflow-optimizer.md
```

---

*Departamento Testing - Se não está testado, não funciona.*
