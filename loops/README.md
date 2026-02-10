# Ralph Wiggum Loop System

Sistema de iteração contínua para os Super Agentes do Dunder Mifflin, inspirado na técnica [Ralph Wiggum](https://awesomeclaude.ai/ralph-wiggum).

## Como Funciona

Um **Ralph Loop** é um ciclo de iteração onde um agente trabalha em uma tarefa repetidamente até:
1. Completar a tarefa (output `<RALPH_COMPLETE>`)
2. Atingir o número máximo de iterações

Cada iteração recebe o histórico do que foi feito anteriormente, permitindo progresso incremental.

## Uso

### Comando Básico
```bash
cd ~/.openclaw/workspace/projects/dunder-mifflin/loops
./ralph-loop.sh <agente> --task "descrição da tarefa"
```

### Agentes Disponíveis

| Agente | Descrição | Melhor Para |
|--------|-----------|-------------|
| `dev` | O Dev - Desenvolvedor pragmático | Código, arquitetura, debugging, TDD |
| `marketeiro` | O Marketeiro - Estrategista de marketing | Copy, criativos, campanhas, análise de mercado |
| `executivo` | O Executivo - Gestor estratégico | Análise de métricas, planejamento, decisões, relatórios |

### Exemplos

**Desenvolvimento:**
```bash
./ralph-loop.sh dev --task "Criar API REST de autenticação com JWT"
./ralph-loop.sh dev --task "Refatorar módulo de pagamentos para usar TDD" -m 30
```

**Marketing:**
```bash
./ralph-loop.sh marketeiro --task "Escrever copy para campanha de vestibular 2026"
./ralph-loop.sh marketeiro --task "Criar 5 variações de headline para anúncio Facebook"
```

**Gestão:**
```bash
./ralph-loop.sh executivo --task "Analisar métricas de conversão do último trimestre"
./ralph-loop.sh executivo --task "Criar relatório de ROI das campanhas ativas"
```

### Opções

```bash
./ralph-loop.sh <agente> [opções]

  --task, -t           Descrição específica da tarefa (obrigatório)
  --max-iterations, -m Número máximo de iterações (padrão: 20)
  --completion, -c     String de completion (padrão: RALPH_COMPLETE)
  --dry-run            Mostrar o prompt sem executar
  --help, -h           Mostrar ajuda
```

## Estrutura

```
loops/
├── ralph-loop.sh              # Script principal
├── README.md                  # Esta documentação
├── prompts/                   # Prompts base dos agentes
│   ├── dev-prompt.md         # Identidade do O Dev
│   ├── marketeiro-prompt.md  # Identidade do O Marketeiro
│   └── executivo-prompt.md   # Identidade do O Executivo
├── logs/                      # Logs de execução (auto-gerado)
└── results/                   # Resultados finais (auto-gerado)
```

## Como Funciona Internamente

1. **Geração do Prompt**: Combina o prompt base do agente + tarefa específica + histórico de iterações
2. **Execução**: Chama o agente (kimi/claude CLI) com o prompt
3. **Verificação**: Procura pela string de completion na resposta
4. **Iteração**: Se não completou, atualiza o histórico e repete
5. **Finalização**: Salva o resultado quando completo ou atinge max iterations

## Personalização

### Adicionar Novo Agente

1. Crie um arquivo em `prompts/{nome}-prompt.md` com a identidade do agente
2. O sistema automaticamente reconhece o novo agente

### Ajustar Prompts Base

Edite os arquivos em `prompts/` para ajustar:
- Princípios fundamentais
- Frameworks preferidos
- Regras de ouro
- Tom de comunicação

## Dicas

### Escreva Bons Prompts de Tarefa

**Ruim:**
```bash
./ralph-loop.sh dev --task "Fazer uma API"
```

**Bom:**
```bash
./ralph-loop.sh dev --task "Criar API REST para autenticação JWT com endpoints: POST /login, POST /register, POST /refresh. Usar TDD, cobertura >80%. Incluir README com exemplos de uso."
```

### Use --dry-run Primeiro

Verifique o prompt antes de executar:
```bash
./ralph-loop.sh marketeiro --task "Criar campanha" --dry-run
```

### Ajuste Max Iterations

Tarefas complexas precisam de mais iterações:
```bash
./ralph-loop.sh dev --task "Refatorar sistema inteiro" -m 50
```

## Integração com o Studio

Os resultados do Ralph Loop podem ser automaticamente:
- Salvos no sistema de arquivos do Studio
- Convertidos em tasks para o Worker V3
- Registrados no banco de dados do Dunder Mifflin

Para integração automática, configure o webhook no script `ralph-loop.sh`.

## Filosofia

> "Ralph is a Bash loop" - Iteration > Perfection

Não espere acertar de primeira. Deixe o loop refinar o trabalho.
