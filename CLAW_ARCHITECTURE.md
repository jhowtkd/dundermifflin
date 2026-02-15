# 🤖 Claw Coordinator - Nova Arquitetura

## Overview

Jeff fala comigo (Claw), eu decido, eu executo ou coordeno subagentes. **Ralph foi desativado.**

## Arquitetura Flattening

```
Jeff (Usuário)
    ↓ (fala comigo)
Claw (Eu - PM + Tech Lead + Executor quando necessário)
    ├─ Simples: Faço direto
    ├─ Médio: Spawno 1 especialista
    └─ Complexo: Coordeno múltiplos especialistas em paralelo
        ├─ Max (🛠️ Builder)
        ├─ Scout (🔍 Research)  
        ├─ Maya (📝 Copywriter)
        ├─ Tracker (📊 Analytics)
        └─ Watcher (👁️ Monitor)
    ↓
Jeff (Recebe resultado final, sem ver intermediários)
```

## Comandos

### Modo Pergunta Antes (padrão)
```
!ralph claw cria uma função de login
🤔 Análise:
   Complexidade: medium
   Ação: Spawno Max (Builder)
   Tempo estimado: ~15 min
   
Quer que eu prossiga? (sim/não/ajustar)
```

### Outros comandos
```
!ralph claw              # Status do coordinator
!ralph modo              # Ver modo atual
!ralph modo execute_report  # Mudar modo
!ralph deploy dashboard  # Deploy (sistema antigo, ainda funciona)
!ralph projects          # Listar projetos
```

## Modos de Operação

| Modo | Descrição | Quando usar |
|------|-----------|-------------|
| `ask_first` | Pergunto antes de executar | **Padrão** - Você quer controle total |
| `execute_report` | Executo e reporto resultado | Você quer agilidade, mas ser informado |
| `silent` | Executo silenciosamente | Você só quer ser perturbado se for importante |

## Como funciona a triagem

**Simples** (eu faço):
- Perguntas, status, verificações
- Respostas rápidas
- Edições pequenas

**Médio** (1 especialista):
- Criar função/componente
- Debug específico
- Pesquisa focada

**Complexo** (múltiplos especialistas):
- Feature completa
- Sistema novo
- Arquitetura

## Configuração

Arquivo: `swarm/.env`
```bash
RALPH_DISABLED=true
CLAW_MODE=ask_first  # ask_first | execute_report | silent
CLAW_ENABLED=true
```

## Arquivos novos

- `swarm/claw_coordinator.py` - Motor de decisão e coordenação
- `swarm/discord_bridge.py` - Atualizado com comandos do Claw
- `swarm/.env` - Configuração de modo

## Arquivos modificados

- `ralph_loop.py` - Agora retorna erro se tentar usar Ralph
- `discord_bridge.py` - Comandos `claw` e `modo` adicionados
- `loop_commands.py` - Desativado, redireciona pro Claw

## Exemplos de uso

```
Jeff: "Preciso de um dashboard novo"
Claw: 🟡 Complexo. Vou coordenar Scout (research) + Max (build) + Maya (docs).
      ~30 min. Quer que eu prossiga?

Jeff: "sim"
Claw: ✅ Iniciando... (mostra progresso)
...
Claw: ✅ Dashboard entregue em http://localhost:3000
      Scout: Pesquisou 5 alternativas
      Max: Implementou com Next.js + Convex
      Maya: Documentou integração

Jeff: "Show, obrigado"
```

## Diferença do modelo antigo (Ralph)

**Antes:**
- Jeff → Ralph → criava tasks → delegava → reportava → Jeff
- Múltiplas camadas de comunicação
- Custo alto em tokens de coordenação

**Agora:**
- Jeff → Claw → analisa → executa/coordena → Jeff
- Uma camada só
- Decisão rápida baseada em contexto direto
- Custo menor

## Próximos passos

1. Testar comandos básicos: `!ralph claw status`
2. Testar tarefa simples: `!ralph claw qual é o status do sistema?`
3. Testar tarefa média: `!ralph claw cria uma função de login`
4. Testar aprovação: ver se o "sim" funciona

## Troubleshooting

**"Claw Coordinator não disponível"**
- Verificar se `claw_coordinator.py` existe
- Verificar logs: `tail -f /tmp/discord_bridge.log`

**"Ralph está desativado"**
- Normal, é o comportamento esperado
- Use `!ralph claw` em vez de loops

**Quer reativar o Ralph?**
- Mudar no `.env`: `RALPH_DISABLED=false`
- Restartar o bridge

---

## 🆕 Integração com Telegram (Novo!)

Agora você pode falar comigo **diretamente aqui no Telegram**, sem precisar ir no Discord.

### Como funciona:

**Eu detecto automaticamente quando você quer algo:**

```
Jeff: "Preciso de uma função de login"
      ↑ Detecto: TASK
Claw: 🤔 Análise: médio, vou chamar Max. ~15 min. Quer que eu prossiga?

Jeff: "sim"
Claw: ✅ Max completou. [resultado aqui no Telegram]
```

### O que eu entendo como tarefa:

Frases que ativam o Claw:
- "Preciso...", "Quero..."
- "Cria...", "Faz...", "Implementa..."
- "Adiciona...", "Ajusta...", "Corrige..."
- "Verifica...", "Analisa...", "Pesquisa..."
- "Deploya...", "Publica...", "Sobe..."
- "Remove...", "Deleta...", "Exclui..."

Também funciona em inglês: "Create...", "Build...", "Implement...", etc.

### Aprovação rápida:

Quando eu pergunto se pode prosseguir:
- `sim`, `s`, `yes`, `ok` → **Aprova** ✅
- `não`, `nao`, `n`, `no`, `cancela` → **Cancela** ❌

### O que eu ignoro (conversa normal):

- "Obrigado", "Valeu", "Thanks"
- "Tá bom", "Beleza", "Entendi", "kkkk"
- Perguntas: "Qual é...", "Como está..."
- Saudações: "Oi", "Bom dia"

### Arquivos da integração:

- `swarm/claw_intent_handler.py` - Detecta intenções
- `swarm/claw_telegram.py` - Interface Telegram

### Teste agora:

Tenta: **"Cria uma função de exemplo"**

Eu vou detectar como task, analisar, e perguntar se pode executar.
