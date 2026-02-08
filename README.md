# 🏢 Dunder Mifflin Multi-Agent System

Sistema multi-agente de IA inspirado na série The Office. 7 agentes especializados trabalhando juntos para executar missões de conteúdo, pesquisa e automação.

## 🎯 Visão Geral

O Dunder Mifflin é um sistema de IA multi-agente que simula uma empresa com diferentes especialistas. Cada agente tem habilidades, prioridades e quota diária de tarefas.

## 🤖 Agentes

| Agente | Função | Prioridade | Capacidades |
|--------|--------|------------|-------------|
| **Michael Scott** | Regional Manager | 10 | strategy, planning, coordination |
| **Dwight Schrute** | Assistant Regional Manager | 9 | execution, analysis, optimization |
| **Jim Halpert** | Sales & Relations | 8 | creative, communication, empathy |
| **Quill** | Content Writer | 7 | writing, linkedin, content, seo |
| **Pam Beesly** | Reception & Support | 6 | organization, support, documentation |
| **Ryan Howard** | Temp & Initiatives | 5 | growth, experiments, innovation |
| **Creed Bratton** | QA & Edge Cases | 4 | testing, edge_cases, unconventional |

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    Dunder Mifflin                        │
├─────────────────────────────────────────────────────────┤
│  Dashboard (HTML/JS) ──▶ API REST (Flask) ──▶ SQLite    │
│       Porta 8888              Porta 3003                 │
├─────────────────────────────────────────────────────────┤
│  Worker Python (Processa missões em background)         │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/jhowtkd/dunder-mifflin.git
cd dunder-mifflin
```

### 2. Configure o ambiente Python

```bash
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors
```

### 3. Inicialize o banco de dados

```bash
python3 db.py reset
```

### 4. Inicie os serviços

```bash
# Terminal 1: API REST
python3 api_flask.py

# Terminal 2: Dashboard
python3 -m http.server 8888

# Terminal 3: Worker (processa missões)
python3 worker_v2.py
```

Ou use os systemd services (Linux):

```bash
sudo cp dunder-mifflin-*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable dunder-mifflin-api dunder-mifflin-dashboard dunder-mifflin-worker
sudo systemctl start dunder-mifflin-api dunder-mifflin-dashboard dunder-mifflin-worker
```

## 🌐 Acesso

- **Dashboard**: http://localhost:8888/dashboard.html
- **API**: http://localhost:3003
- **API Docs**: http://localhost:3003/api/health

## 📡 API Endpoints

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/health` | GET | Status da API |
| `/api/stats` | GET | Estatísticas do sistema |
| `/api/agents` | GET | Lista agentes |
| `/api/missions` | GET | Lista missões |
| `/api/proposals` | GET | Lista propostas |
| `/api/proposals` | POST | Criar proposta |
| `/api/proposals/<id>/approve` | POST | Aprovar proposta |
| `/api/files` | GET | Lista arquivos |
| `/api/files/<path>` | GET | Baixar arquivo |

## 📝 Fluxo de Trabalho

1. **Criar Proposta**: Uma ideia de tarefa é criada e atribuída a um agente
2. **Aprovação**: Você aprova a proposta no dashboard
3. **Execução**: O Worker executa a missão automaticamente
4. **Entrega**: Arquivos são gerados e ficam disponíveis para download

## 🎨 Exemplo de Missão

Criar carrossel sobre a Era Vargas:

```bash
curl -X POST http://localhost:3003/api/proposals \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": 7,
    "title": "Criar carrossel sobre a Era Vargas",
    "description": "Conteúdo educativo sobre o período 1930-1945",
    "missionType": "carousel",
    "priority": 8
  }'
```

Depois aprove no dashboard e o Quill vai gerar o carrossel!

## 📁 Estrutura de Arquivos

```
dunder-mifflin/
├── api_flask.py              # API REST (Flask)
├── worker_v2.py              # Worker de missões
├── db.py                     # Gerenciamento do banco
├── dashboard.html            # Interface web
├── schema.sql                # Schema SQLite
├── dunder_mifflin.db         # Banco de dados
├── carousels/                # Arquivos gerados
├── *.service                 # Systemd services
└── README.md                 # Este arquivo
```

## 🔧 Tecnologias

- **Backend**: Python + Flask + SQLite
- **Frontend**: HTML5 + Vanilla JS
- **Worker**: Python puro
- **Deploy**: Systemd (Linux)

## 🎓 Inspiração

Este projeto é uma homenagem à série [The Office (US)](https://www.imdb.com/title/tt0386676/), criada por Greg Daniels. O Dunder Mifflin Paper Company é a empresa fictícia onde a série se passa.

## 📄 Licença

MIT License - Sinta-se livre para usar e modificar!

---

🏢 *"Dunder Mifflin - People Person's Paper People"*
