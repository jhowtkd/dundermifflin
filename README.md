# 🏢 Dunder Mifflin + Jules Agents

Sistema de Gerenciamento de Agentes AI com interface estilo Windows 95. Integra **52 agentes Jules** organizados em 9 departamentos, com um painel de controle visual inspirado no design retro de terminais dos anos 90.

## 🎯 Visão Geral

O Dunder Mifflin é um **painel de controle central** para gerenciar agentes de IA especializados. A interface combina a nostalgia do Windows 95 com funcionalidades modernas de gerenciamento de tarefas.

### Features Principais

- **52 Agentes Jules** - Agentes AI especializados em diferentes áreas
- **9 Departamentos** - Organização lógica das especialidades
- **8 Personas The Office** - Personagens mapeados para agentes (easter egg!)
- **Sistema de Missões** - Criar, aprovar e monitorar tarefas
- **Interface Win95** - Design retro com efeito CRT

## 🤖 Agentes Jules

### Departamentos

| Emoji | Departamento | Agentes | Descrição |
|-------|--------------|---------|-----------|
| 🤖 | **autonomous** | 7 | Agentes autônomos (bolt, sentinel, janitor...) |
| 💻 | **development** | 9 | Desenvolvimento (fullstack, code-reviewer...) |
| 🎨 | **design** | 8 | Design e UX (ui-designer, ux-writer...) |
| 📢 | **marketing** | 7 | Marketing (growth-hacker, content-creator...) |
| 📦 | **product** | 4 | Produto (researcher, sprint-prioritizer...) |
| 📋 | **project-mgmt** | 3 | Gestão (studio-producer, project-shipper...) |
| ⚙️ | **studio-ops** | 5 | Operações (analytics, finance-tracker...) |
| 🧪 | **testing** | 7 | Testes (tester, mocker, api-tester...) |
| 🎁 | **bonus** | 2 | Especiais (joker, studio-coach) |

### Personas The Office

| Emoji | Persona | Agente Mapeado |
|-------|---------|----------------|
| 👔 | Michael Scott | studio-producer |
| 👓 | Dwight Schrute | sentinel |
| 😐 | Jim Halpert | joker |
| 🎨 | Pam Beesly | ux-writer |
| 🥨 | Stanley Hudson | tester |
| 🐈 | Angela Martin | legal-compliance-checker |
| 🍲 | Kevin Malone | finance-tracker |
| 📊 | Oscar Martinez | analytics-specialist |

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    Dunder Mifflin                           │
├─────────────────────────────────────────────────────────────┤
│  Frontend Win95 (HTML/JS)                                   │
│    ├── index.html      (Dashboard)                          │
│    ├── agents.html     (Grid de Agentes)                    │
│    ├── missions.html   (Lista de Missões)                   │
│    ├── proposals.html  (Criar/Aprovar Propostas)            │
│    └── files.html      (Arquivos Gerados)                   │
├─────────────────────────────────────────────────────────────┤
│  API REST (Flask)                Porta 3003                 │
│    └── SQLite (dunder_mifflin.db)                           │
├─────────────────────────────────────────────────────────────┤
│  Worker Python (Processa missões em background)             │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/jhowtkd/dundermifflin.git
cd dundermifflin
```

### 2. Configure o ambiente Python

```bash
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors
```

### 3. Inicialize o banco de dados

```bash
# Criar schema
sqlite3 dunder_mifflin.db < schema.sql

# Importar agentes Jules (requer pasta Jules/agents/)
python3 import_jules.py
```

### 4. Inicie o servidor

```bash
python3 api_flask.py
```

Acesse: **http://localhost:3003**

### 5. (Opcional) Worker para processar missões

```bash
python3 worker_v2.py
```

## 📡 API Endpoints

### Endpoints Principais

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/health` | GET | Status da API |
| `/api/stats` | GET | Estatísticas do dashboard |

### Agentes Jules

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/agents` | GET | Lista todos os 52 agentes |
| `/api/agents?dept=X` | GET | Filtro por departamento |
| `/api/agents/<slug>` | GET | Detalhes do agente |
| `/api/agents/<slug>/content` | GET | Conteúdo completo (.md) |

### Departamentos e Personas

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/departments` | GET | Lista 9 departamentos |
| `/api/personas` | GET | Lista 8 personas The Office |
| `/api/commands` | GET | Lista comandos disponíveis |

### Missões e Propostas

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/missions` | GET | Lista missões |
| `/api/missions?status=X` | GET | Filtro por status |
| `/api/proposals` | GET | Lista propostas |
| `/api/proposals` | POST | Criar proposta |
| `/api/proposals/<id>/approve` | POST | Aprovar proposta |

### Arquivos

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/files` | GET | Lista arquivos gerados |
| `/api/files/<path>` | GET | Download de arquivo |

## 🎨 Interface

### Dashboard (index.html)
- 5 Stat Cards com contadores
- Missões recentes
- Links de navegação

### Agentes (agents.html)
- Sidebar com departamentos
- Grid de agentes com cards
- Terminal de detalhes do agente selecionado
- Botões de ação

### Missões (missions.html)
- Filtros por status (Todas/Rodando/Sucesso/Falhas)
- Cards de missão com status
- Auto-refresh a cada 5 segundos

### Propostas (proposals.html)
- Formulário de nova proposta
- Select de agentes
- Lista de propostas pendentes
- Botões Aprovar/Rejeitar

### Arquivos (files.html)
- Grid de arquivos gerados
- Preview inline
- Download

## 📁 Estrutura do Projeto

```
dundermifflin/
├── api_flask.py              # API REST (Flask)
├── db.py                     # Camada de acesso ao banco
├── worker_v2.py              # Worker de missões
├── import_jules.py           # Script de importação dos agentes
├── schema.sql                # Schema SQLite
├── dunder_mifflin.db         # Banco de dados
│
├── frontend/                 # Interface Win95
│   ├── index.html            # Dashboard
│   ├── agents.html           # Grid de agentes
│   ├── missions.html         # Lista de missões
│   ├── proposals.html        # Criar/aprovar propostas
│   ├── files.html            # Arquivos gerados
│   └── js/
│       ├── api.js            # Cliente API
│       └── app.js            # Componentes e lógica
│
├── dunder-mifflin-*.service  # Systemd services
└── README.md
```

## 🔧 Tecnologias

- **Backend**: Python 3, Flask, SQLite
- **Frontend**: HTML5, Tailwind CSS (CDN), Vanilla JS
- **Fonts**: VT323, Press Start 2P (Google Fonts)
- **Icons**: Material Symbols Outlined
- **Deploy**: Systemd (Linux)

## 🎮 Como Usar

### 1. Visualizar Agentes

Acesse `/agents` e navegue pelos departamentos. Clique em um agente para ver detalhes no terminal.

### 2. Criar Missão

1. Acesse `/proposals`
2. Selecione um agente
3. Preencha título, descrição e tipo
4. Clique em "SUBMIT"

### 3. Aprovar Missão

1. Na lista de propostas pendentes
2. Clique em "APPROVE"
3. A missão será criada e processada

### 4. Monitorar Execução

Acesse `/missions` para ver o status em tempo real.

### 5. Baixar Resultados

Acesse `/files` para ver e baixar arquivos gerados.

## 🐛 Troubleshooting

### Erro "No agents found"

Execute o script de importação:
```bash
python3 import_jules.py
```

### Porta 3003 em uso

Mude a porta via variável de ambiente:
```bash
DM_API_PORT=3004 python3 api_flask.py
```

### Dark mode não funciona

O dark mode é detectado automaticamente pelo sistema operacional. Para forçar:
```javascript
document.documentElement.classList.add('dark');
```

## 📄 Licença

MIT License - Sinta-se livre para usar e modificar!

---

🏢 *"Dunder Mifflin - People Person's Paper People"*

🤖 *Powered by Jules Agents - 52 Specialists, One Mission*
