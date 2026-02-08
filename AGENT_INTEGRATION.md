# Integração Worker V2 com Agentes Reais

## Problema
O worker_v2 está simulando a execução dos agentes em vez de chamar agentes reais:

```python
def _execute_agent_step(self, step: Dict, session: OrchestrationSession) -> str:
    # Aqui você integraria com o agente real via Clawdbot
    # Por enquanto, simulamos uma resposta
    output = f"Output do agente {agent_slug} para: {step['title']}\n"
    return output
```

## Solução Proposta

### Opção 1: Chamada HTTP para OpenClaw Gateway (Recomendada)
Criar um endpoint no Gateway que permite spawnar agentes via HTTP:

```python
# worker_v2.py
import requests

def _execute_agent_step(self, step: Dict, session: OrchestrationSession) -> str:
    agent_slug = step['agent_slug']
    context = session.get_context_for_step(step)
    
    # Carrega prompt do agente
    agent_prompt = self._load_agent_prompt(agent_slug)
    
    # Chama OpenClaw Gateway
    response = requests.post(
        "http://localhost:8080/api/agents/spawn",
        json={
            "agent_slug": agent_slug,
            "task": context['objective'],
            "prompt": agent_prompt,
            "timeout": 300
        }
    )
    
    return response.json()['result']
```

### Opção 2: Sistema de Filas (Mais Robusta)
Worker salva tarefas em fila SQLite, OpenClaw consome via heartbeat:

```python
# worker_v2.py
def _execute_agent_step(self, step: Dict, session: OrchestrationSession) -> str:
    # Cria tarefa na fila
    task_id = self._queue_task(step, session)
    
    # Aguarda resultado (polling)
    return self._wait_for_result(task_id, timeout=300)
```

### Opção 3: Subprocess Direto (Mais Simples)
Chamar openclaw CLI via subprocess:

```python
# worker_v2.py
import subprocess
import json

def _execute_agent_step(self, step: Dict, session: OrchestrationSession) -> str:
    agent_slug = step['agent_slug']
    context = session.get_context_for_step(step)
    
    # Monta comando
    cmd = [
        "openclaw", "agents", "run",
        "--agent", agent_slug,
        "--task", context['objective'],
        "--json"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    return json.loads(result.stdout)['output']
```

## Mapeamento de Agentes

Mapear agent_slug para arquivos markdown:

| slug | arquivo |
|------|---------|
| debugger | agents/development/debugger.md |
| tester | agents/testing/tester.md |
| researcher | agents/product/researcher.md |
| code-reviewer | agents/development/code-reviewer.md |
| architect | agents/development/architect.md |

## Implementação

Para implementar a Opção 2 (fila + heartbeat):

1. Criar tabela `agent_tasks_queue` no banco
2. Worker insere tarefas na fila em vez de executar
3. OpenClaw heartbeat consome fila e executa agentes
4. Worker faz polling do resultado

Isso permite execução assíncrona e escalável.
