# Arquitetura Híbrida: Consumer + OpenClaw

## Visão Geral

Sistema de execução de agentes usando arquitetura híbrida:
- **Consumer (Python/Systemd)**: Gerencia a fila, faz polling
- **OpenClaw (Cron)**: Executa agentes via `sessions_spawn`

## Fluxo de Dados

```
┌─────────────────┐     ┌─────────────────────┐     ┌─────────────────┐
│   Worker V2     │────▶│  Fila SQLite        │     │   Consumer      │
│  (Orquestra)    │     │  status=pending     │────▶│   (Systemd)     │
│                 │     │       ↓             │     │                 │
│  Aguarda        │◀────│  status=completed   │◀────│  Marca como     │
│  resultado      │     │  _by_openclaw       │     │  queued_for_    │
└─────────────────┘     └─────────────────────┘     │  openclaw       │
                                                    └─────────────────┘
                                                              │
                                                              │
                              ┌───────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │   OpenClaw Cron     │
                    │  (a cada 60s)       │
                    │                     │
                    │  1. Busca queued_   │
                    │  2. sessions_spawn  │
                    │  3. Atualiza banco  │
                    └─────────────────────┘
```

## Status da Fila

| Status | Significado | Responsável |
|--------|-------------|-------------|
| `pending` | Nova tarefa, aguardando | Worker |
| `queued_for_openclaw` | Pronta para execução | Consumer |
| `executing_by_openclaw` | Em execução | OpenClaw |
| `completed_by_openclaw` | Executada, aguardando ack | OpenClaw |
| `completed` | Finalizada | Consumer |
| `failed_by_openclaw` | Falhou | OpenClaw |

## Componentes

### 1. Worker V2 (`worker_v2.py`)
- Enfileira tarefas (`_queue_agent_task()`)
- Faz polling do resultado (`_wait_for_task_result()`)
- Continua workflow quando tarefa completa

### 2. Consumer V2 (`agent_queue_consumer_v2.py`)
- **Systemd service**: `dunder-mifflin-agent-consumer`
- Roda a cada 30 segundos
- `queue_tasks_for_openclaw()`: Move pending → queued_for_openclaw
- `process_completed_tasks()`: Move completed_by_openclaw → completed
- `cleanup_old_tasks()`: Remove tarefas antigas

### 3. OpenClaw Executor (Cron Job)
- **Job**: `openclaw-agent-executor`
- **Frequência**: A cada 60 segundos
- **Ações**:
  1. Busca `status='queued_for_openclaw'`
  2. Marca como `executing_by_openclaw`
  3. Usa `sessions_spawn` com modelo `kimi-coding/k2p5`
  4. Atualiza como `completed_by_openclaw` ou `failed_by_openclaw`

## Execução de Teste

Para testar o sistema completo:

1. **Criar um plano** no dashboard e aprovar
2. **Verificar fila**:
   ```bash
   sqlite3 dunder_mifflin.db "SELECT task_code, agent_slug, status FROM agent_tasks_queue;"
   ```
3. **Aguardar Consumer** (até 30s):
   - Status muda: `pending` → `queued_for_openclaw`
4. **Aguardar OpenClaw** (até 60s):
   - Status muda: `queued_for_openclaw` → `executing_by_openclaw` → `completed_by_openclaw`
5. **Ver resultado**:
   - Consumer move para `completed`
   - Worker continua próximo step

## Logs

```bash
# Consumer (Systemd)
sudo journalctl -u dunder-mifflin-agent-consumer -f

# Worker
sudo journalctl -u dunder-mifflin-worker -f

# API
sudo journalctl -u dunder-mifflin-api -f

# Cron jobs do OpenClaw
openclaw cron list
openclaw cron runs --jobId 0584e5e5-b740-41ec-8234-464795031230
```

## Troubleshooting

### Tarefas ficam em "pending"
```bash
# Verificar se Consumer está rodando
sudo systemctl status dunder-mifflin-agent-consumer

# Restartar Consumer
sudo systemctl restart dunder-mifflin-agent-consumer
```

### Tarefas ficam em "queued_for_openclaw"
```bash
# Verificar cron job do OpenClaw
openclaw cron list

# Verificar últimas execuções
openclaw cron runs --jobId 0584e5e5-b740-41ec-8234-464795031230

# Trigger manual (se necessário)
openclaw cron run --jobId 0584e5e5-b740-41ec-8234-464795031230
```

### Limpar tarefas stuck
```bash
cd ~/.openclaw/workspace/projects/dunder-mifflin

# Resetar tarefas stuck
sqlite3 dunder_mifflin.db "
  UPDATE agent_tasks_queue 
  SET status = 'pending' 
  WHERE status IN ('queued_for_openclaw', 'executing_by_openclaw') 
  AND started_at < datetime('now', '-10 minutes');
"
```

## Próximos Passos

1. **Testar execução real**: Criar plano e verificar se todo o fluxo funciona
2. **Adicionar mais agentes**: Mapear todos os 54 agentes disponíveis
3. **Melhorar prompts**: Refinar prompts dos agentes para melhores resultados
4. **Adicionar notificações**: Enviar mensagem quando plano completar
5. **Escalar**: Permitir múltiplas execuções paralelas (aumentar limites)
