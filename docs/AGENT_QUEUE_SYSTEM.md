# Sistema de Fila de Agentes - Documentação

## Arquitetura

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Worker V2     │────▶│  Fila SQLite     │◀────│   Consumer      │
│  (Orquestra)    │     │ agent_tasks_queue│     │  (30s loop)     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                        │
         │                       │                        │
         ▼                       ▼                        ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Polling do     │     │  Status: pending │     │  Execução Real  │
│  resultado      │◀────│  → running       │────▶│  via OpenClaw   │
│                 │     │  → completed     │     │  sessions_spawn │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## Como Funciona

### 1. Worker Enfileira
Quando um plano é aprovado, o worker:
1. Para cada step, cria uma tarefa na fila (`agent_tasks_queue`)
2. Faz polling do resultado a cada 2 segundos
3. Quando a tarefa é completada, continua para o próximo step

### 2. Consumer Processa
O consumer (`dunder-mifflin-agent-consumer.service`):
1. Roda em loop a cada 30 segundos
2. Busca tarefas com `status = 'pending'`
3. Executa o agente (atualmente simulado)
4. Atualiza status para `completed` ou `failed`

### 3. Worker Continua
Worker detecta a conclusão e prossegue com o workflow.

## Serviços Systemd

```bash
# Ver status dos serviços
sudo systemctl status dunder-mifflin-worker
sudo systemctl status dunder-mifflin-agent-consumer
sudo systemctl status dunder-mifflin-api

# Logs em tempo real
sudo journalctl -u dunder-mifflin-agent-consumer -f
sudo journalctl -u dunder-mifflin-worker -f
```

## Ativar Execução Real (Próximo Passo)

Para executar agentes reais via OpenClaw, modifique `agent_queue_consumer.py`:

```python
def execute_task_local(task: dict) -> dict:
    """Executa tarefa via OpenClaw sessions_spawn"""
    
    agent_slug = task['agent_slug']
    task_desc = task['task_description']
    prompt = load_agent_prompt(agent_slug)
    
    # Monta mensagem para o agente
    full_message = f"""{prompt}

---

## Tarefa

{task_desc}

---

Execute esta tarefa e retorne o resultado completo.
"""
    
    # Chama sessions_spawn via OpenClaw Gateway
    # (requer implementação no gateway)
    response = requests.post(
        "http://localhost:8080/api/agents/spawn",
        json={
            "task": full_message,
            "model": "kimi-coding/k2p5",
            "timeoutSeconds": 300
        }
    )
    
    return {
        "status": "completed",
        "output": response.json()['result']
    }
```

## Banco de Dados

```sql
-- Ver tarefas pendentes
SELECT * FROM agent_tasks_queue WHERE status = 'pending';

-- Ver tarefas em execução
SELECT * FROM agent_tasks_queue WHERE status = 'running';

-- Ver tarefas completadas
SELECT * FROM agent_tasks_queue WHERE status = 'completed' ORDER BY completed_at DESC;

-- Limpar tarefas antigas
DELETE FROM agent_tasks_queue WHERE completed_at < datetime('now', '-7 days');
```

## Fluxo de Execução

1. **Criar Plano** → Dashboard → `POST /api/orchestration/plans`
2. **Aprovar Plano** → Dashboard → `PATCH /api/orchestration/plans/{id}`
3. **Worker Detecta** → `get_executing_plans()` retorna plano aprovado
4. **Worker Enfileira** → `_queue_agent_task()` cria tarefa na fila
5. **Consumer Processa** → `process_tasks()` executa agente
6. **Worker Continua** → `_wait_for_task_result()` detecta conclusão
7. **Próximo Step** → Repete até completar todos os steps

## Monitoramento

### Logs do Worker
```bash
sudo journalctl -u dunder-mifflin-worker -n 50 -f
```

### Logs do Consumer
```bash
sudo journalctl -u dunder-mifflin-agent-consumer -n 50 -f
```

### Status da Fila
```bash
cd ~/.openclaw/workspace/projects/dunder-mifflin
sqlite3 dunder_mifflin.db "SELECT status, COUNT(*) FROM agent_tasks_queue GROUP BY status;"
```

## Troubleshooting

### Consumer não está processando
```bash
sudo systemctl restart dunder-mifflin-agent-consumer
sudo journalctl -u dunder-mifflin-agent-consumer --since "5 minutes ago"
```

### Worker travado em polling
```bash
# Ver se há tarefas stuck
sqlite3 dunder_mifflin.db "SELECT * FROM agent_tasks_queue WHERE status = 'running' AND started_at < datetime('now', '-10 minutes');"

# Resetar tarefas stuck
sqlite3 dunder_mifflin.db "UPDATE agent_tasks_queue SET status = 'pending', started_at = NULL WHERE status = 'running' AND started_at < datetime('now', '-10 minutes');"
```

### Limpar fila completamente
```bash
sqlite3 dunder_mifflin.db "DELETE FROM agent_tasks_queue;"
```
