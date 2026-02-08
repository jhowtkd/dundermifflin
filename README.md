# 🏢 Dunder Mifflin + Jules Agents

> *"Onde a IA encontra a eficiência... e um pouco de caos organizado."*

Sistema de Gerenciamento de Agentes AI com interface estilo Windows 95. Integra **52 agentes especializados** organizados em **9 departamentos**, com um painel de controle visual inspirado nos terminais dos anos 90.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![SQLite](https://img.shields.io/badge/SQLite-3-orange.svg)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

![Dunder Mifflin Dashboard](https://img.shields.io/badge/Dashboard-Win95%20Style-9cf?style=for-the-badge)

---

## 🎯 Visão Geral

O **Dunder Mifflin** é um **Sistema Multi-Agente** para gerenciamento de tarefas de IA. Cada agente tem especialidade única — desde escrever conteúdo até revisar código, criar designs ou analisar dados.

### Por que "Dunder Mifflin"?
Porque assim como a empresa de papel de *The Office*, aqui também temos:
- Um **Michael Scott** (studio-producer) tentando coordenar tudo
- Um **Dwight** (sentinel) vigiando a qualidade
- Um **Jim** (joker) com suas pegadinhas
- E 49 outros agentes trabalhando (ou fingindo que trabalham)

---

## ✨ Features

### 🤖 52 Agentes Jules Organizados
| Departamento | Emoji | Agentes | Descrição |
|--------------|-------|---------|-----------|
| **Autonomous** | 🤖 | 7 | bolt, sentinel, janitor, migrator, optimizer, a11y-specialist, i18n-specialist |
| **Development** | 💻 | 9 | fullstack-dev, code-reviewer, architect, debugger, ai-engineer, cicd-engineer, database-engineer, rapid-prototyper, api-designer |
| **Design** | 🎨 | 8 | ui-designer, ux-writer, ux-researcher, brand-guardian, visual-storyteller, palette, polish, whimsy-injector |
| **Marketing** | 📢 | 7 | growth-hacker, content-creator, twitter-engager, instagram-curator, reddit-community-builder, tiktok-strategist, app-store-optimizer |
| **Product** | 📦 | 4 | researcher, sprint-prioritizer, trend-researcher, feedback-synthesizer |
| **Project Management** | 📋 | 3 | studio-producer, project-shipper, experiment-tracker |
| **Studio Operations** | ⚙️ | 5 | analytics-specialist, finance-tracker, legal-compliance-checker, support-responder, infrastructure-maintainer |
| **Testing** | 🧪 | 7 | tester, mocker, api-tester, workflow-optimizer, test-results-analyzer, performance-benchmarker, tool-evaluator |
| **Bonus** | 🎁 | 2 | joker, studio-coach |

### 🎭 Personagens The Office
Cada persona tem um agente mapeado (e uma catch phrase):

| Persona | Agente | Catch Phrase |
|---------|--------|--------------|
| 👔 Michael Scott | studio-producer | "That's what she said!" |
| 👓 Dwight Schrute | sentinel | "Bears. Beets. Battlestar Galactica." |
| 😐 Jim Halpert | joker | *looks at camera* |
| 🎨 Pam Beesly | ux-writer | "I feel God in this Chili's" |
| 🥨 Stanley Hudson | tester | "Did I stutter?" |
| 🐈 Angela Martin | legal-compliance-checker | "I know everything." |
| 🍲 Kevin Malone | finance-tracker | "Why waste time say lot word when few word do trick?" |
| 📊 Oscar Martinez | analytics-specialist | "Actually..." |

---

## 🚀 Quick Start

### 1. Clone o Repositório
```bash
git clone https://github.com/jhowtkd/dundermifflin.git
cd dundermifflin
```

### 2. Instale as Dependências
```bash
pip install flask flask-cors
```

### 3. Configure o Banco de Dados
```bash
# Cria o banco SQLite
sqlite3 dunder_mifflin.db < schema.sql

# Importa os 52 agentes Jules
python3 import_jules.py
```

### 4. Inicie os Serviços
```bash
# Terminal 1 - API Flask
python3 api_flask.py

# Terminal 2 - Dashboard (servidor estático)
cd frontend && python3 -m http.server 8888

# Terminal 3 - Worker (processa missões)
python3 worker_v2.py
```

### 5. Acesse
- 🌐 **Dashboard:** http://localhost:8888
- 🔌 **API:** http://localhost:3003
- 📊 **Health Check:** http://localhost:3003/api/health

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    DUNDER MIFFLIN                          │
├─────────────────────────────────────────────────────────────┤
│  Frontend Win95 (HTML/CSS/JS)                              │
│  ├── index.html          → Dashboard Principal             │
│  ├── agents.html         → Grid de Agentes                 │
│  ├── missions.html       → Lista de Missões                │
│  ├── proposals.html      → Criar/Aprovar Propostas         │
│  ├── mission-detail.html → Detalhes da Missão              │
│  └── files.html          → Arquivos Gerados                │
├─────────────────────────────────────────────────────────────┤
│  API REST (Flask) - Porta 3003                             │
│  ├── /api/health         → Status do sistema               │
│  ├── /api/agents         → Lista de agentes                │
│  ├── /api/missions       → CRUD de missões                 │
│  ├── /api/proposals      → Propostas pendentes             │
│  └── /api/files          → Arquivos gerados                │
├─────────────────────────────────────────────────────────────┤
│  Worker Python (Background)                                │
│  ├── Processa missões em fila                              │
│  ├── Gera conteúdo (social, carrossel, etc)               │
│  └── Salva arquivos em ~/.openclaw/workspace/studio/...   │
├─────────────────────────────────────────────────────────────┤
│  SQLite (dunder_mifflin.db)                                │
│  ├── agents, departments, personas                         │
│  ├── missions, proposals, steps                            │
│  └── events, memories, commands                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📖 API Documentation

### Agentes
```bash
# Listar todos os agentes
GET /api/agents

# Listar por departamento
GET /api/agents?dept=marketing

# Detalhes de um agente
GET /api/agents/sentinel
```

### Missões
```bash
# Listar missões
GET /api/missions
GET /api/missions?status=running
GET /api/missions?status=succeeded

# Detalhes de uma missão
GET /api/missions/MS-xxx
```

### Propostas
```bash
# Listar propostas pendentes
GET /api/proposals

# Aceitar proposta (cria missão)
POST /api/proposals/PROP-xxx/accept

# Rejeitar proposta
POST /api/proposals/PROP-xxx/reject
```

### Arquivos
```bash
# Listar arquivos gerados
GET /api/files

# Baixar arquivo
GET /api/files/carousels/xxx.html
```

---

## 🎮 Como Usar

### 1. Criar uma Missão
1. Acesse **Propostas** (`/proposals.html`)
2. Preencha o formulário:
   - **Título:** Descrição da tarefa
   - **Tipo:** social, carousel, content, research
   - **Prioridade:** 1-10
   - **Descrição:** Contexto detalhado
3. Clique em **"CRIAR PROPOSTA"**

### 2. Aprovar e Executar
1. A proposta aparece em **Missões** (`/missions.html`)
2. O Worker processa automaticamente (status: `running`)
3. Quando completo, status muda para `succeeded`
4. Clique **"VER DETALHES"** para ver o resultado

### 3. Ver Resultados
O resultado da missão inclui:
- **Social:** 5 posts com legendas, hashtags, horários
- **Carousel:** Estrutura de slides com conteúdo e design notes
- **Content:** Texto completo gerado
- **Research:** Análise e insights

---

## 🛠️ Sistema de Missões

### Tipos de Missão Suportados

| Tipo | Descrição | Exemplo de Resultado |
|------|-----------|---------------------|
| `social` | Planejamento semanal Instagram | 5 posts com legendas, hashtags, CTAs |
| `carousel` | Carrossel LinkedIn | 5-7 slides com títulos e conteúdo |
| `content` | Post LinkedIn | Texto completo com storytelling |
| `research` | Análise/Pesquisa | Relatório estruturado |
| `general` | Tarefa genérica | Confirmação de execução |

### Status das Missões
- `pending` → Aguardando aprovação
- `approved` → Aprovada, na fila
- `running` → Em execução
- `succeeded` → Completada com sucesso
- `failed` → Falhou (ver mensagem de erro)
- `cancelled` → Cancelada

---

## 🖥️ Deploy com Systemd

Para rodar como serviço no Linux:

```bash
# Copiar os arquivos de serviço
sudo cp dunder-mifflin-*.service /etc/systemd/system/

# Recarregar systemd
sudo systemctl daemon-reload

# Iniciar serviços
sudo systemctl start dunder-mifflin-api
sudo systemctl start dunder-mifflin-dashboard
sudo systemctl start dunder-mifflin-worker

# Habilitar para iniciar no boot
sudo systemctl enable dunder-mifflin-api
sudo systemctl enable dunder-mifflin-dashboard
sudo systemctl enable dunder-mifflin-worker
```

---

## 🎨 Interface Win95

O design segue a estética Windows 95 com:
- **Bordas 3D** (raised/inset)
- **Título de janela** com gradiente azul
- **Fontes pixeladas** (VT323, Press Start 2P)
- **Efeito CRT** (scanlines leves)
- **Cores clássicas:** cinza #c0c0c0, azul #000080

---

## 📝 Estrutura do Projeto

```
dunder-mifflin/
├── agents/                    # 52 agentes Jules (.md)
│   ├── autonomous/
│   ├── development/
│   ├── design/
│   ├── marketing/
│   ├── product/
│   ├── project-management/
│   ├── studio-operations/
│   ├── testing/
│   └── bonus/
├── frontend/                  # Dashboard HTML/JS
│   ├── index.html
│   ├── agents.html
│   ├── missions.html
│   ├── mission-detail.html
│   ├── proposals.html
│   ├── files.html
│   └── js/
│       ├── api.js
│       └── app.js
├── api_flask.py              # API REST
├── worker_v2.py              # Worker de missões
├── db.py                     # Funções de banco
├── import_jules.py           # Importa agentes
├── schema.sql                # Schema SQLite
├── seed_agents.py            # Seed de agentes
└── dunder-mifflin-*.service  # Systemd services
```

---

## 🧪 Testando a API

```bash
# Health check
curl http://localhost:3003/api/health

# Listar agentes
curl http://localhost:3003/api/agents | jq '.agents[:3]'

# Criar missão (via script)
python3 test_social_mission3.py

# Ver missões
curl http://localhost:3003/api/missions | jq '.missions[0]'
```

---

## 🐛 Troubleshooting

### API retorna 404
```bash
# Verificar se API está rodando
curl http://localhost:3003/api/health

# Verificar porta
tail -f /var/log/syslog | grep dunder-mifflin-api
```

### Frontend não carrega
```bash
# Verificar servidor estático
netstat -tlnp | grep 8888

# Verificar se arquivos existem
ls -la frontend/
```

### Worker não processa missões
```bash
# Verificar logs do worker
sudo journalctl -u dunder-mifflin-worker -f

# Verificar se há missões pendentes
sqlite3 dunder_mifflin.db "SELECT * FROM missions WHERE status='approved';"
```

---

## 🚧 Roadmap

- [x] 52 agentes Jules integrados
- [x] Interface Win95 completa
- [x] Sistema de missões com worker
- [x] API REST funcional
- [x] Deploy com systemd
- [ ] Autenticação JWT
- [ ] WebSocket para updates em tempo real
- [ ] Export de relatórios (PDF)
- [ ] Integração com OpenAI/Claude
- [ ] Mobile app

---

## 📜 Licença

MIT License - Veja [LICENSE](LICENSE) para detalhes.

---

## 🙏 Créditos

- **Agentes Jules:** Baseados no projeto [google-labs-jules](https://github.com/google-labs/jules)
- **The Office:** Personagens da série da NBC
- **Win95 UI:** Inspirado na interface clássica do Windows 95

---

> *"That's what she said!"* — Michael Scott, probably
