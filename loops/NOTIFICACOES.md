# Ralph Loop - Notificações

Quando um loop completa, você recebe notificações automáticas!

---

## 🔔 Onde aparecem:

### 1. **Dashboard** (http://100.94.223.52:8888/ralph-dashboard.html)
- Banner verde/vermelho no topo
- Mostra: Agente, tarefa, iterações, duração, custo
- Atualiza a cada 10 segundos

### 2. **Em breve: Telegram**
- Mensagem automática quando loop termina
- Preview do resultado
- Link direto para o dashboard

---

## 📊 O que é mostrado:

```
✅ Completado
O Dev • 5 iterações • 2m 30s • $0.0523
Criar função de validar CPF...
```

Ou se falhar:
```
❌ Falhou
O Marketeiro • 20/20 iterações • $0.2100
Escrever copy para campanha...
```

---

## 🛠️ Como funciona:

1. Loop termina (completa ou falha)
2. Sistema cria arquivo de notificação
3. Dashboard detecta e mostra banner
4. Você clica para ver detalhes ou limpar

---

## 📝 Para implementar notificação Telegram:

Adicione ao `ralph_loop.py` na função `prepare_notification`:

```python
# Enviar notificação Telegram
message = f"""
🔄 *Ralph Loop {status_text}*

{status_icon} *Código:* `{loop_code}`
🤖 *Agente:* {agent_name}
📋 *Tarefa:* {task[:100]}...

📊 *Resumo:*
• Iterações: {iterations}
• Duração: {duration}
• Custo: ${cost:.4f}

🔗 [Ver no Dashboard](http://100.94.223.52:8888/ralph-dashboard.html?loop={loop_code})
"""

# Usar tool do OpenClaw
openclaw_message_send(message)
```

---

## 🎯 URLs de Acesso

| Rede | Dashboard | Novo Loop |
|------|-----------|-----------|
| Local | http://clawd-b450mhp:8888/ralph-dashboard.html | http://clawd-b450mhp:8888/ralph-start.html |
| Tailscale | http://100.94.223.52:8888/ralph-dashboard.html | http://100.94.223.52:8888/ralph-start.html |

---

## 🎯 Resumo

| Onde | Quando | O que vê |
|------|--------|----------|
| Dashboard | Loop termina | Banner com resumo |
| Dashboard | A qualquer momento | Lista de loops completados |
| Terminal | Comando `ralph-status` | Loops ativos |

---

**Pronto! Agora você sabe quando seus loops terminam! 🎉**
