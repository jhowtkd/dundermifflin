# 🚀 Como Usar - Dunder Mifflin V2

## ⚡ Início Rápido

### No Terminal:

```bash
cd /Users/jhonatan/Repos/dundermifflin
python3 run_server.py
```

**Deixe o terminal aberto!** O servidor precisa rodar.

### Em outro terminal ou navegador:

Abra: **http://localhost:3003**

---

## 🖥️ Passo a Passo Completo

### 1. Abra um Terminal

Pressione `Cmd + Espaço`, digite "Terminal" e pressione Enter.

### 2. Navegue até a pasta

```bash
cd /Users/jhonatan/Repos/dundermifflin
```

### 3. Inicie o servidor

```bash
python3 run_server.py
```

Você verá:
```
🏢 DUNDER MIFFLIN V2 - Servidor Iniciado
==================================================
🌐 URL: http://localhost:3003
📊 API: http://localhost:3003/api
...
```

**⚠️ IMPORTANTE: Não feche esta janela do terminal!**

### 4. Acesse no navegador

Abra seu navegador e digite:
```
http://localhost:3003
```

Ou clique no link que aparece no terminal.

---

## 🎯 Teste Rápido

1. **Dashboard** → Clique em "SERVIÇOS"
2. Escolha **"Post LinkedIn"** (📝)
3. Preencha:
   - Título: `Post sobre IA`
   - Objetivo: `Criar post profissional sobre inteligência artificial`
4. Clique **"Criar Plano"**
5. Vá para aba **"PLANOS"**
6. Veja o plano criado pelo Master (Michael Scott)
7. Clique **"Aprovar"**

---

## 🛑 Como Parar

No terminal onde o servidor está rodando, pressione:
```
Ctrl + C
```

---

## 🔧 Problemas Comuns

### "Porta 3003 em uso"

```bash
# Encontre e mate o processo
lsof -ti:3003 | xargs kill -9

# Ou use outra porta
DM_API_PORT=3004 python3 run_server.py
```

### "Banco de dados não encontrado"

```bash
python3 import_jules.py
python3 migrate_orchestration.py
```

### "Connection refused"

O servidor não está rodando. Siga os passos acima para iniciar.

---

## 📁 Estrutura

```
/Users/jhonatan/Repos/dundermifflin/
├── run_server.py          # ⬅️ EXECUTE ESTE
├── api_flask.py           # API backend
├── orchestrator.py        # Master Agent
├── frontend/
│   ├── index.html         # Dashboard
│   ├── services.html      # Hub de serviços
│   └── history.html       # Histórico
└── dunder_mifflin.db      # Banco de dados
```

---

## 🌐 URLs

| URL | Descrição |
|-----|-----------|
| http://localhost:3003 | Dashboard principal |
| http://localhost:3003/services.html | Criar/gerenciar serviços |
| http://localhost:3003/history.html | Histórico de execuções |
| http://localhost:3003/api/services | API - Lista serviços |
| http://localhost:3003/api/plans | API - Lista planos |

---

**Pronto! Execute `python3 run_server.py` e acesse http://localhost:3003** 🎉
