# 🎯 Ralph Swarm - Referência Rápida de Skills

## Estrutura do Sistema
```
┌─────────────────────────────────────────────────────────────┐
│                    RALPH (Coordenador)                      │
│              Tier: Expensive | Skills: 10                   │
│         Função: Orquestração, Decisão, Síntese              │
└──────────────────────┬──────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┬───────────────┐
       │               │               │               │
       ▼               ▼               ▼               ▼
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  SCOUT   │    │   MAX    │    │   MAYA   │    │  TRACKER │
│Researcher│    │ Builder  │    │Copywriter│    │ Analista │
│Cheap: 8  │    │Medium: 7 │    │Cheap: 11 │    │Cheap: 9  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
       │                                               │
       └───────────────────┬───────────────────────────┘
                           │
                    ┌──────────┐
                    │ WATCHER  │
                    │Observador│
                    │Cheap: 7  │
                    └──────────┘
```

## Mapeamento de Categorias

| Categoria | Skills | Agentes Principais | Foco |
|-----------|--------|-------------------|------|
| 🔧 Técnica | 15 | Max, Ralph | Desenvolvimento, Debugging, Segurança |
| 📊 Analítica | 24 | Todos | Análise, Métricas, Frameworks |
| 🎨 Criativa | 11 | Maya | Copywriting, Storytelling |
| 🎯 Estratégica | 15 | Ralph, Scout, Watcher | Orquestração, Inteligência |

## Frameworks Principais

### Ralph (Coordenação)
- **RAL-001**: Análise de Tarefas (Chain-of-Thought)
- **RAL-002**: Decisão Swarm vs Single
- **RAL-007**: Síntese em 4 Camadas

### Scout (Research)
- **SCO-001**: Framework ESTRATEGIC
- **SCO-003**: Níveis de Profundidade (1/2/3)

### Max (Build)
- **MAX-001**: Processo em 5 Fases
- **MAX-002**: Metodologia DEBUG

### Maya (Copy)
- **MAY-002**: Framework AIDA
- **MAY-003**: Framework PAS

### Tracker (Analytics)
- **TRA-001**: Processo de Análise Estruturado
- **TRA-005**: Sistema de Alertas (🔴🟡🟢)

### Watcher (Monitor)
- **WAT-004**: Competitor Tracking (4 dimensões)
- **WAT-005**: Trend Detection (5 sinais)

## Tags para Busca RAG

### Por Função
- `#coordination` - Ralph
- `#research` - Scout
- `#development` - Max
- `#copywriting` - Maya
- `#analytics` - Tracker
- `#monitoring` - Watcher

### Por Atividade
- `#analysis` - Análise de dados/padrões
- `#synthesis` - Consolidação de informações
- `#framework` - Metodologias estruturadas
- `#prioritization` - Priorização de ações
- `#debugging` - Resolução de problemas
- `#security` - Segurança e proteção

## Níveis de Complexidade

| Nível | Skills | Tempo Est. | Automação |
|-------|--------|------------|-----------|
| 🟢 Baixa | 3 | 15-30min | Alta |
| 🟡 Média | 32 | 30-60min | Média |
| 🔴 Alta | 17 | 60+min | Baixa |

## Exemplos de Consultas RAG

```python
# Buscar todas as skills de um agente
query = "agent == 'Maya' AND category == 'criativa'"

# Buscar skills por tag
query = "'analytics' in tags"

# Buscar skills sem pré-requisitos (fundamentais)
query = "prerequisites == []"

# Buscar caminho de dependências
path = get_skill_path("RAL-007")  # Retorna: [RAL-001, RAL-002, RAL-003, RAL-004, RAL-005, RAL-007]

# Buscar skills complementares
related = get_complementary("MAY-002")  # Retorna: [MAY-003]
```

## Contratos de Interface (SLAs)

| Agent | Entregável Mínimo | SLA |
|-------|------------------|-----|
| Scout | 3+ fontes, 2+ benchmarks, insights | 15 min |
| Max | Código funcional, README, testes | 30 min |
| Maya | 3 variações de copy, justificativa | 15 min |
| Tracker | Análise de métricas, recomendações | 10 min |

---
*Documento para uso em sistemas RAG - Ralph Swarm Skills Mapping v1.0*
