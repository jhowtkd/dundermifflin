# ⚙️ Departamento Studio Operations

> **Missão:** Manter as operações do estúdio funcionando de forma eficiente, segura e em conformidade.

## Visão Geral

O departamento **Studio Operations** é responsável por toda a infraestrutura operacional do estúdio. De finanças a suporte, estes agentes garantem que tudo funcione nos bastidores.

## Agentes

| Agente | Emoji | Foco | Quando Usar |
|--------|-------|------|-------------|
| [Analytics Specialist](./analytics-specialist.md) | 📊 | Analytics | Eventos, relatórios, dashboards |
| [Finance Tracker](./finance-tracker.md) | 💰 | Finanças | Receitas, despesas, runway |
| [Infrastructure Maintainer](./infrastructure-maintainer.md) | 🔧 | Infraestrutura | Servers, uptime, monitoring |
| [Legal Compliance Checker](./legal-compliance-checker.md) | ⚖️ | Compliance | LGPD, termos, contratos |
| [Support Responder](./support-responder.md) | 💬 | Suporte | Tickets, usuários, resolução |

## Matriz de Prioridade

```
CRITICIDADE
   ↑
   │  ┌─────────────┐ ┌─────────────┐
   │  │Infrastructure│ │    Legal    │
   │  │ Maintainer  │ │ Compliance  │
   │  └─────────────┘ └─────────────┘
   │  ┌─────────────┐ ┌─────────────┐
   │  │   Support   │ │   Finance   │
   │  │  Responder  │ │   Tracker   │
   │  └─────────────┘ └─────────────┘
   │  ┌─────────────┐
   │  │  Analytics  │
   │  │ Specialist  │
   │  └─────────────┘
   └──────────────────────────────────────────────────→ FREQUÊNCIA
```

## Fluxos Recomendados

### Operações Diárias
1. **Infrastructure Maintainer** → Verificar health checks
2. **Support Responder** → Responder tickets
3. **Analytics Specialist** → Atualizar dashboards

### Fechamento Mensal
1. **Finance Tracker** → Consolidar números
2. **Analytics Specialist** → Relatório de métricas
3. **Legal Compliance Checker** → Verificar conformidade

### Incidente
1. **Infrastructure Maintainer** → Resolver problema
2. **Support Responder** → Comunicar usuários
3. **Analytics Specialist** → Analisar impacto

## Composições

| Cenário | Agentes | Ordem |
|---------|---------|-------|
| Novo Mercado | Legal → Finance → Analytics | Compliance → Custos → Métricas |
| Downtime | Infra → Support → Analytics | Resolver → Comunicar → Medir |
| Auditoria | Legal → Finance → Analytics | Compliance → Finanças → Dados |
| Fundraising | Finance → Analytics | Números → Métricas |

## SLAs e Métricas

### Infraestrutura
- Uptime: 99.9% (8.76h downtime/ano)
- Response time: < 200ms p95
- Error rate: < 0.1%

### Suporte
- First response: < 4h
- Resolution time: < 24h (P1), < 72h (P2)
- CSAT: > 90%

### Finanças
- Runway: > 12 meses
- Burn rate: monitorado semanalmente
- MRR growth: positivo

## Ferramentas

| Tipo | Recomendadas |
|------|--------------|
| Infra | AWS, GCP, Vercel |
| Monitoring | DataDog, Sentry, PagerDuty |
| Support | Intercom, Zendesk, Crisp |
| Analytics | Amplitude, Mixpanel, Metabase |
| Finance | QuickBooks, Stripe Dashboard |
| Legal | DocuSign, Termly |

## Compliance Checklist

### LGPD/GDPR
- [ ] Política de privacidade atualizada
- [ ] Consentimento de cookies
- [ ] Data Processing Agreement
- [ ] Direito ao esquecimento implementado

### Termos de Serviço
- [ ] ToS revisados por advogado
- [ ] Changelog de versões
- [ ] Aceitação trackada

### Segurança
- [ ] SOC 2 compliance
- [ ] Penetration testing anual
- [ ] Backup e disaster recovery

## Diários

Todos os agentes deste departamento registram suas atividades em:
```
.jules/studio-operations/
├── analytics-specialist.md
├── finance-tracker.md
├── infrastructure-maintainer.md
├── legal-compliance-checker.md
└── support-responder.md
```

---

*Departamento Studio Operations - Os bastidores que fazem tudo funcionar.*
