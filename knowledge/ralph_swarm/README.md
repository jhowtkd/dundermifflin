# 📚 Ralph Swarm Knowledge Base

Documentação completa das skills e expertises do Ralph Swarm.

## Arquivos

| Arquivo | Descrição | Tamanho |
|---------|-----------|---------|
| `ralph_swarm_skills_mapping.json` | Mapeamento completo em JSON | 50 KB |
| `ralph_swarm_skills_mapping.md` | Documentação Markdown | 33 KB |
| `ralph_swarm_documentacao_completa_rag.md` | Doc otimizada para RAG | 79 KB |
| `ralph_swarm_agentes_documentacao.md` | Docs individuais dos 6 agentes | 31 KB |
| `ralph_swarm_quick_reference.md` | Referência rápida | 5 KB |
| `ralph_swarm_mapping_summary.txt` | Resumo estatístico | 10 KB |
| `ralph_swarm_rag_summary.json` | Resumo otimizado para busca | 4 KB |
| `ralph_swarm_skills_visualization.png` | Gráficos de distribuição | 181 KB |

## Estrutura do Sistema

**52 skills** mapeadas em **4 categorias**:
- 🔧 Técnica (15 skills)
- 📊 Analítica (24 skills)  
- 🎨 Criativa (11 skills)
- 🎯 Estratégica (15 skills)

**6 Agentes**:
- Ralph (10 skills) - Coordenador
- Maya (11 skills) - Copywriter
- Tracker (9 skills) - Analista
- Scout (8 skills) - Researcher
- Max (7 skills) - Builder
- Watcher (7 skills) - Observador

## Uso

Para buscar skills:
```python
from ralph_swarm_loader import load_skills, find_by_tag, find_by_agent

skills = load_skills()  # Carrega skills_mapping.json
maya_skills = find_by_agent('Maya')  # Skills da Maya
research_skills = find_by_tag('research')  # Skills de pesquisa
```

---
*Integrado em 2026-02-13*
