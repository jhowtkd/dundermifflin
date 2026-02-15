# 🚀 Deploy pelo Discord - Guia Rápido

## Como usar

### 1. Configurar um projeto

Crie um arquivo `.ralph-deploy.yml` na raiz do projeto:

```yaml
project:
  name: meu-app
  type: nextjs  # nextjs, react, python, docker, static
  
deploy:
  platform: vercel  # vercel, railway, docker, github_pages, netlify
  build_cmd: npm run build
  output_dir: .next
  
  health_check:
    url: https://meu-app.vercel.app/api/health
    timeout: 30
```

### 2. Comandos no Discord

#### Via comando direto:
```
!ralph projects                    # Lista projetos configurados
!ralph deploy meu-app              # Deploy pra produção
!ralph deploy dashboard staging    # Deploy em staging
```

#### Via linguagem natural (o Ralph entende):
```
"deploya o meu-app"
"faz deploy do dashboard"
"deploya o api na railway"
"publica o frontend"
"sobe o backend pra produção"
```

### 3. Durante o deploy

O Ralph vai:
1. ✅ Reagir com 🚀 no seu comando
2. Enviar mensagem de status
3. Reportar cada etapa em tempo real:
   - Validação
   - Build
   - Deploy
   - Health Check
4. Resultado final com URL ✅ ou erro ❌

### 4. Acompanhar no Dashboard

Abra `http://localhost:3000` para ver logs detalhados em tempo real.

## Plataformas suportadas

| Plataforma | Detecta por | Variáveis necessárias |
|------------|-------------|----------------------|
| Vercel | `vercel.json` ou package.json | `VERCEL_TOKEN` |
| Railway | `railway.json` | `RAILWAY_TOKEN` |
| Docker | `Dockerfile` | `DOCKER_REGISTRY` |
| GitHub Pages | `.github/workflows` | `GITHUB_TOKEN` |
| Netlify | `netlify.toml` | `NETLIFY_AUTH_TOKEN` |

## Estrutura de arquivos

```
swarm/
├── discord_bridge.py          # ← Integração adicionada aqui
├── deploy_integration.py      # Handler de comandos naturais
├── agents/
│   └── deployer.py            # Agente de deploy
├── project_registry.py        # Descobre projetos
└── live_logger.py             # Logs em tempo real
```

## Troubleshooting

**"Sistema de deploy não disponível"**
- Verifique se `deploy_integration.py` existe
- Verifique os logs: `tail -f /tmp/discord_bridge.log`

**"Projeto não encontrado"**
- Verifique se `.ralph-deploy.yml` existe na raiz
- Use `!ralph projects` para ver se foi detectado

**Deploy falha**
- Verifique variáveis de ambiente no `.env`
- Veja logs detalhados no dashboard
- Verifique permissões do token da plataforma
