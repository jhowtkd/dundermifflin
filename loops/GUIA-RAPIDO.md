# Ralph Loop - Guia Rápido

Sistema de iteração contínua para os Super Agentes do Dunder Mifflin.

---

## 🌐 Acesso

| Rede | URL |
|------|-----|
| **Local** | http://clawd-b450mhp:8888/ralph-start.html |
| **Tailscale** | http://100.94.223.52:8888/ralph-start.html |

---

## 🚀 3 Formas Simplificadas de Usar

### 1. **Alias Ultra-Curto (Terminal)**

```bash
# Carregar aliases (adicione ao ~/.bashrc)
source ~/.openclaw/workspace/projects/dunder-mifflin/loops/aliases.sh

# Comandos disponíveis:
ralph dev "Criar API de autenticação JWT"
ralph marketeiro "Escrever 5 headlines para anúncio"
ralph executivo "Analisar métricas do mês"

# Ainda mais curto:
ralph-dev "Criar função de validar CPF"
ralph-mkt "Copy para email marketing"
ralph-exec "Relatório de ROI"

# Monitoramento:
ralph-status      # Ver loops ativos
ralph-history     # Últimos loops
ralph-cost        # Resumo de custos
ralph-help        # Ajuda completa
```

---

### 2. **Dashboard (Clique Simples)**

Acesse: **http://100.94.223.52:8888/ralph-start.html** (Tailscale)

**Passos:**
1. Escolha o agente (Dev, Marketeiro ou Executivo)
2. Clique em uma tarefa pré-definida ou digite a sua
3. Ajuste máximo de iterações (padrão: 20)
4. Clique em "🚀 Iniciar Loop"

**Pronto!** O loop começa e você é redirecionado para o dashboard.

---

### 3. **Via Telegram**

**Comando:**
```
/ralph <agente> <tarefa>
```

**Exemplos:**
```
/ralph dev criar API REST com Flask
/ralph marketeiro escrever copy para landing page
/ralph executivo analisar custos do projeto
```

**Aliases aceitos:**
- `dev`, `developer`, `desenvolvedor`, `code`, `codigo` → O Dev
- `mkt`, `marketeiro`, `marketing`, `copy` → O Marketeiro
- `exec`, `executivo`, `gestao`, `manager` → O Executivo

**Resposta:**
```
🚀 Ralph Loop Iniciado!

Código: RALPH-A7B3D9E2F1
Agente: 👨‍💻 O Dev
Tarefa: Criar API REST com Flask

📊 Ver no Dashboard

⏳ O loop está rodando em background...
```

---

## 📊 Monitoramento

**Dashboard:** http://100.94.223.52:8888/ralph-dashboard.html

- Loops ativos em tempo real
- Histórico completo
- Custo acumulado
- Métricas por agente
- 🔔 Notificações de loops completados

---

## 💰 Custo Estimado

| Iterações | Custo Aproximado |
|-----------|-----------------|
| 5         | ~$0.025         |
| 10        | ~$0.050         |
| 20        | ~$0.100         |
| 30        | ~$0.150         |
| 50        | ~$0.250         |

Baseado em ~2K tokens in + 1K tokens out por iteração (Kimi K2).

---

## 🔄 Como Funciona

1. **Você solicita** → 2. **Sistema cria loop** → 3. **Iterações** → 4. **Resultado**

```
Iteração 1: Analisa tarefa
Iteração 2: Planeja abordagem
Iteração 3: Executa primeira parte
...
Iteração N: Output RALPH_COMPLETE → Finaliza!
```

---

## 🆘 Precisa de Ajuda?

- Digite `ralph-help` no terminal
- Acesse o dashboard e clique nos botões de preset
- Use `/ralph` no Telegram sem parâmetros para ver ajuda

---

**Pronto para começar?** Escolha sua forma favorita acima! 🚀
