# 🚀 Dunder Mifflin V2 - Execução Local

## Iniciar o Sistema

### Opção 1: Script Automático (Recomendado)

```bash
python3 start_local.py
```

Isso vai:
- Verificar dependências
- Verificar banco de dados
- Iniciar o servidor
- Abrir o navegador automaticamente

### Opção 2: Manual

```bash
# Instalar dependências (se necessário)
pip3 install flask flask-cors

# Iniciar API
python3 api_flask.py
```

---

## Acessar o Sistema

Após iniciar, acesse:

| URL | Descrição |
|-----|-----------|
| http://localhost:3003 | **Dashboard** - Menu principal |
| http://localhost:3003/services.html | **Hub de Serviços** - Criar/executar workflows |
| http://localhost:3003/history.html | **Histórico** - Missões e execuções |

---

## Fluxo de Uso

### 1. Criar um Plano

1. Acesse **Serviços** (http://localhost:3003/services.html)
2. Clique em um serviço existente (ex: "Post LinkedIn")
3. Preencha título e objetivo
4. Clique em "Criar Plano"

### 2. Aprovar o Plano

1. Vá para a aba **Planos**
2. Veja o plano criado pelo Master (Michael Scott)
3. Reveja a estratégia e sequência de agentes
4. Clique em **Aprovar** ou **Rejeitar**

### 3. Acompanhar Execução

1. Acesse a aba **Execução**
2. Veja o progresso em tempo real
3. Acompanhe a conversa entre os agentes
4. Veja o resultado final

---

## Serviços Disponíveis

| Serviço | Emoji | Descrição |
|---------|-------|-----------|
| Post LinkedIn | 📝 | Pesquisa → Redação → Revisão |
| Code Review | 🔍 | Análise → Testes → Debug |
| Landing Page | 🎨 | UX → Copy → Design → Polimento |
| Experimento Growth | 🚀 | Hipótese → Analytics → Assets |
| Suíte QA | 🧪 | Testes → API → Performance |
| Pipeline Deploy | ⚙️ | CI/CD → Check → Deploy |

---

## API Endpoints

```
GET  /api/services                 # Lista serviços
POST /api/services                 # Cria serviço
GET  /api/plans                    # Lista planos
POST /api/plans                    # Cria plano
POST /api/plans/:code/approve      # Aprova plano
POST /api/plans/:code/reject       # Rejeita plano
GET  /api/orchestration/sessions   # Lista execuções
GET  /api/agents                   # Lista agentes
```

---

## Solução de Problemas

### Erro "Banco de dados não encontrado"
```bash
python3 import_jules.py
```

### Erro "Tabelas não encontradas"
```bash
python3 migrate_orchestration.py
```

### Porta 3003 em uso
```bash
# Usar outra porta
DM_API_PORT=3004 python3 start_local.py
```

---

## Estrutura do Sistema

```
dundermifflin/
├── api_flask.py          # API REST
├── orchestrator.py       # Master Agent + Orquestração
├── worker_v2.py          # Worker de execução
├── dunder_mifflin.db     # Banco SQLite
└── frontend/
    ├── index.html        # Dashboard
    ├── services.html     # Hub principal
    └── history.html      # Histórico
```

---

## Master Agent

O **studio-producer** (Michael Scott) atua como orquestrador:
- Analisa sua solicitação
- Cria plano estruturado
- Seleciona agentes adequados
- Coordena execução sequencial

Você sempre aprova o plano antes da execução!

---

**Pronto para usar!** 🎉

Execute `python3 start_local.py` e acesse http://localhost:3003
