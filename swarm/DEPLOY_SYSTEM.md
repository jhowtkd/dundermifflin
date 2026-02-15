# 🚀 Ralph Deploy System - Documentação

## O que foi implementado

### 1. Project Registry (`swarm/project_registry.py`)
- Escaneia automaticamente projetos em `~/projetos`, `~/workspace`, `~/dev`, etc.
- Detecta arquivos `.ralph-deploy.yml`
- Mostra status git (branch, commits ahead, modified)

### 2. Live Logger (`swarm/live_logger.py`)
- Envia logs em tempo real pro dashboard via Convex
- Steps: `started`, `running`, `completed`, `failed`
- Níveis: DEBUG, INFO, STEP, WARN, ERROR, SUCCESS

### 3. Deployer Agent (`swarm/agents/deployer.py`)
- Suporta: Vercel, Railway, Docker, GitHub Pages, Netlify
- Valida env vars necessárias
- Build + Deploy + Health Check
- Rollback automático se health check falhar

### 4. Natural Language Handler (`swarm/deploy_integration.py`)
- Entende comandos como:
  - "deploya o meu-app"
  - "deploya o dashboard pra produção"
  - "deploya o api na railway"
  - "faz deploy do frontend com Node 20"
  - "lista os projetos"

### 5. Dashboard API Fix (`dashboard/app/api/`)
- Rotas de sync e webhook agora realmente chamam mutations do Convex
- `activityLogs:create` adicionado

## Como usar

### 1. Configurar um projeto

Crie `.ralph-deploy.yml` na raiz do projeto:

```yaml
project:
  name: meu-app
  type: nextjs
  
deploy:
  platform: vercel
  build_cmd: npm run build
  output_dir: .next
  
  health_check:
    url: https://meu-app.vercel.app/api/health
    timeout: 30
```

### 2. Comandos naturais suportados

| Comando | O que faz |
|---------|-----------|
| `deploya o meu-app` | Deploy do projeto pra produção |
| `deploya o dashboard pra staging` | Deploy em ambiente específico |
| `deploya o api na railway` | Força plataforma específica |
| `faz deploy do frontend com Node 20` | Deploy com ajuste de versão |
| `lista os projetos` | Mostra projetos disponíveis |
| `status do deploy` | Link pro dashboard |

### 3. Integrar no Ralph

Adicione isso no `agent_brain.py` ou `discord_bridge.py`:

```python
from swarm.deploy_integration import handle_deploy_message

async def process_message(self, message: str):
    # Tenta processar como comando de deploy
    deploy_response = await handle_deploy_message(
        message, 
        agent_slug=self.agent_slug,
        mission_id=self.current_mission
    )
    
    if deploy_response:
        return deploy_response
    
    # Se não for deploy, processa normalmente...
```

### 4. Ver logs em tempo real

Acesse o dashboard em `http://localhost:3000` e veja:
- Status de cada step do deploy
- Logs detalhados de build/deploy
- Erros com stack trace
- URL final do deploy

## Estrutura de arquivos

```
swarm/
├── project_registry.py      # Descobre projetos
├── live_logger.py           # Logs em tempo real
├── deploy_integration.py    # Handler de comandos
├── agents/
│   └── deployer.py          # Agente de deploy
└── dashboard/
    ├── app/api/
    │   ├── sync/route.ts         # API de sync (fixado)
    │   └── webhook/[path]/       # Webhooks (novo)
    └── convex/
        └── activityLogs.ts       # Mutation de logs (novo)
```

## Próximos passos sugeridos

1. **Testar integração**: Rodar um deploy de teste
2. **Adicionar rollback manual**: Comando "ralph, reverte o deploy do meu-app"
3. **Deploy automático**: Detectar push no git e deployar sozinho
4. **Notificações**: Enviar pro Telegram quando deploy completar

## Variáveis de ambiente necessárias

```bash
# Para dashboard
CONVEX_URL=https://seu-projeto.convex.cloud

# Para deploys
VERCEL_TOKEN=xxx
RAILWAY_TOKEN=xxx
DOCKER_REGISTRY=xxx
```
