# 🤖 Departamento Autonomous

> **Missão:** Manter a qualidade, segurança e saúde do codebase através de agentes que operam de forma autônoma e proativa.

## Visão Geral

O departamento **Autonomous** é responsável pela manutenção contínua e melhoria incremental do código. Estes agentes trabalham de forma independente, identificando e resolvendo problemas antes que se tornem críticos.

## Agentes

| Agente | Emoji | Foco | Quando Usar |
|--------|-------|------|-------------|
| [Bolt](./bolt.md) | ⚡ | Performance | Otimização de velocidade, bundle size, rendering |
| [Sentinel](./sentinel.md) | 🛡️ | Segurança | Vulnerabilidades, OWASP, secrets, auth |
| [Janitor](./janitor.md) | 🧹 | Limpeza | Dead code, imports, dependências não usadas |
| [Optimizer](./optimizer.md) | 🚀 | Otimização | Algoritmos, queries, memory leaks |
| [Migrator](./migrator.md) | 🔄 | Migrações | Upgrades de dependências, breaking changes |
| [A11y Specialist](./a11y-specialist.md) | ♿ | Acessibilidade | WCAG, screen readers, navegação por teclado |
| [i18n Specialist](./i18n-specialist.md) | 🌍 | Internacionalização | Traduções, formatação locale, RTL |

## Matriz de Prioridade

```
URGÊNCIA
   ↑
   │  ┌─────────────┐ ┌─────────────┐
   │  │  Sentinel   │ │    Bolt     │
   │  │ (segurança) │ │(performance)│
   │  └─────────────┘ └─────────────┘
   │  ┌─────────────┐ ┌─────────────┐
   │  │  Migrator   │ │  Optimizer  │
   │  │  (updates)  │ │  (otimiza)  │
   │  └─────────────┘ └─────────────┘
   │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
   │  │   Janitor   │ │ A11y Spec.  │ │ i18n Spec.  │
   │  │  (limpeza)  │ │(acessibil.) │ │  (tradução) │
   │  └─────────────┘ └─────────────┘ └─────────────┘
   └──────────────────────────────────────────────────→ IMPACTO
```

## Fluxos Recomendados

### Manutenção Semanal
1. **Sentinel** → Scan de segurança
2. **Janitor** → Limpeza de código morto
3. **Migrator** → Verificar dependências desatualizadas

### Antes de Release
1. **Bolt** → Verificar performance
2. **A11y Specialist** → Auditoria de acessibilidade
3. **Sentinel** → Scan final de segurança

### Novo Mercado/Idioma
1. **i18n Specialist** → Preparar internacionalização
2. **A11y Specialist** → Verificar requisitos locais

## Composições

| Cenário | Agentes | Ordem |
|---------|---------|-------|
| Saúde do Código | Janitor → Optimizer → Bolt | Limpar, otimizar, medir |
| Segurança Total | Sentinel → Migrator | Vulnerabilidades → Updates |
| Globalização | i18n → A11y | Tradução → Acessibilidade |

## Integração com CI/CD

```yaml
# .github/workflows/autonomous-agents.yml
name: Autonomous Agents

on:
  schedule:
    - cron: '0 6 * * 1'  # Segunda às 6h

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Sentinel Scan
        run: npm audit && npm run security:scan

  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Bolt Performance Check
        run: npm run build && npm run lighthouse
```

## Diários

Todos os agentes deste departamento registram suas atividades em:
```
.jules/autonomous/
├── bolt.md
├── sentinel.md
├── janitor.md
├── optimizer.md
├── migrator.md
├── a11y-specialist.md
└── i18n-specialist.md
```

---

*Departamento Autonomous - Cuidando do código enquanto você dorme.*
