#!/usr/bin/env python3
"""
Cliente LLM unificado - Antigravity API (OpenClaw)
Suporta: Gemini 3 Flash, Kimi K2.5, Claude via Antigravity
"""

import os
import json
import requests
import subprocess
from typing import Optional

class LLMClient:
    """Cliente unificado para LLMs - Antigravity API (OpenClaw)"""
    
    def __init__(self):
        # ✅ ANTIGRAVITY - Modelos disponíveis
        self.model = "gemini-3-flash"  # ou "kimi-k2.5", "claude-opus-4-5"
        self.provider = "google-antigravity"
        
    def generate(self, prompt: str, agent_slug: str = "agent") -> str:
        """Gera conteúdo usando Antigravity via OpenClaw sessions spawn"""
        return self._call_antigravity(prompt, agent_slug)
    
    def _call_antigravity(self, prompt: str, agent_slug: str) -> str:
        """Chama Antigravity via OpenClaw CLI"""
        try:
            print(f"[BOT] Chamando Antigravity ({self.model}) para: {agent_slug}")
            
            # Usa sessions spawn com Antigravity
            cmd = [
                "openclaw", "sessions", "spawn",
                "--model", f"{self.provider}/{self.model}",
                "--task", prompt,
                "--timeout", "120"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=130
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                
                # Parse para extrair apenas o conteúdo gerado
                content = self._parse_antigravity_output(output)
                
                if len(content) > 100:
                    print(f"[OK] Antigravity respondeu ({len(content)} chars)")
                    return content
                else:
                    print(f"[AVISO] Resposta muito curta, usando demo")
                    return self._demo_content(prompt, agent_slug)
            else:
                error = result.stderr.strip()[:200] if result.stderr else "Erro"
                print(f"[ERRO] Antigravity: {error}")
                return self._demo_content(prompt, agent_slug)
                
        except subprocess.TimeoutExpired:
            print("[ERRO] Antigravity timeout")
            return self._demo_content(prompt, agent_slug)
        except Exception as e:
            print(f"[ERRO] Antigravity exception: {e}")
            return self._demo_content(prompt, agent_slug)
    
    def _parse_antigravity_output(self, output: str) -> str:
        """Extrai conteúdo relevante da saída do OpenClaw"""
        lines = output.split('\n')
        
        # Procura por linhas que parecem conteúdo real (não logs)
        content_lines = []
        in_content = False
        
        for line in lines:
            stripped = line.strip()
            
            # Pula linhas de log/decoração
            if any(marker in stripped for marker in [
                'Doctor warnings', 'Session store:', 'State dir',
                'Hook registry', 'Sessions listed:', 'Kind', 'Key',
                'Age', 'Model', '◇', '╭', '╮', '╯', '─', '│',
                'agent:', 'group', 'main', 'direct'
            ]):
                continue
            
            # Pula linhas que são só caracteres de decoração
            if set(stripped).issubset(set('│─┼┤├┌┐└┘┬┴┼═║╔╗╚╝╠╣╦╩╬')):
                continue
            
            # Se a linha tem conteúdo substancial, adiciona
            if len(stripped) > 20 and not stripped.startswith('Config'):
                content_lines.append(line)
        
        content = '\n'.join(content_lines).strip()
        return content
    
    def _demo_content(self, prompt: str, agent_slug: str) -> str:
        """Gera conteúdo de demonstração quando API falha"""
        print(f"[BOT] Modo DEMO para: {agent_slug}")
        
        if "twitter" in prompt.lower() or "tweet" in prompt.lower():
            return self._generate_twitter_thread()
        elif "linkedin" in prompt.lower():
            return self._generate_linkedin_post()
        elif "email" in prompt.lower() or "newsletter" in prompt.lower():
            return self._generate_email()
        elif "tiktok" in prompt.lower() or "roteiro" in prompt.lower():
            return self._generate_tiktok_script()
        else:
            return self._generate_blog_post()
    
    def _generate_blog_post(self) -> str:
        return """# 5 Dicas de Produtividade para Trabalho Remoto

## Introdução

O trabalho remoto trouxe liberdade, mas também desafios de produtividade. Neste post, compartilho 5 estratégias práticas que transformaram minha rotina.

## 1. 🎯 Ritual de Início

Crie um ritual que seu cérebro associe ao "modo trabalho":
- Vista-se (mesmo em casa)
- Prepare uma bebida
- Revise suas prioridades do dia

## 2. ⏰ Blocos de Tempo

Use a técnica Pomodoro:
- 25 minutos focado
- 5 minutos de pausa
- Repita 4x, depois pausa maior

## 3. 🏠 Espaço Dedicado

Tenha um local específico para trabalhar:
- Mesmo que seja uma mesa pequena
- Iluminação boa
- Poucos distratores

## 4. 📱 Modo Foco

Silencie notificações:
- Use modo avião em apps de mensagem
- Comunique horários de resposta
- Foco profundo = qualidade

## 5. 🛑 Ritual de Fim

Desligue-se de verdade:
- Liste conquistas do dia
- Defina prioridades para amanhã
- Feche o laptop e "saia" do escritório

## Conclusão

A produtividade no home office é um hábito construído dia a dia. Qual dessas dicas você vai experimentar primeiro?

---
*Conteúdo gerado por Dunder Mifflin Studio*"""

    def _generate_twitter_thread(self) -> str:
        return """🧵 Thread: 5 Mitos sobre Produtividade no Trabalho Remoto

1/ 🏠 "Trabalhar de casa é mais fácil"

FALSO! Requer mais disciplina. Sem estrutura do escritório, você precisa criar seus próprios sistemas de produtividade.

---

2/ ⏰ "Posso trabalhar a qualquer hora"

FALSO! Horários irregulares queimam sua energia. Ritmo consistente = sustentabilidade.

---

3/ 💬 "Vou ficar desconectado da equipe"

FALSO! Comunicação proativa > presença física. Updates claros mantêm todos alinhados.

---

4/ 🎯 "Faço mais em menos tempo"

FALSO! Distrações domésticas são reais. Sem fronteiras, trabalho invade vida pessoal.

---

5/ 😴 "Não preciso de pausas"

FALSO! Home office exige mais pausas ativas. Levante-se, estique-se, respire.

---

Qual desses mitos você já ouviu? Compartilhe nos comentários! 👇

#HomeOffice #Produtividade #TrabalhoRemoto"""

    def _generate_linkedin_post(self) -> str:
        return """💼 Case de Sucesso: Como aumentamos Produtividade em 40%

**O Desafio:**
Nossa equipe remota tinha dificuldade com entregas e comunicação. Reuniões sem fim, pouco foco, burnout crescente.

**A Solução:**
Implementamos 3 mudanças simples:

✅ Reuniões só às terças e quintas (meio-dia)
✅ Documentação > reuniões de alinhamento
✅ Métricas de resultado, não de horas online

**Os Resultados:**
📈 40% mais entregas no prazo
📈 60% menos reuniões
📈 NPS interno: 7.2 → 8.9

**A Lição:**
Produtividade remota não é sobre ferramentas. É sobre cultura de confiança e clareza de propósito.

---

Sua empresa já repensou processos para o remoto? Qual foi o maior aprendizado?

#Gestão #Liderança #HomeOffice #Resultados"""

    def _generate_email(self) -> str:
        return """**Assunto:** 🚀 Lançamento: Curso de Produtividade para Profissionais Busy

Oi [Nome],

Você já se sentiu sobrecarregado com tantas tarefas e pouco tempo?

Eu também. Até descobrir que produtividade não é sobre fazer mais. É sobre fazer o que importa.

Por isso criei o **Curso Produtividade Master**.

**O que você vai aprender:**

✅ Sistema de priorização que reduziu minha lista de 50 para 3 tarefas diárias
✅ Técnica de foco profundo que dobrou minha velocidade de entrega
✅ Rituais de início/fim que protegem minha sanidade mental

**Prova social:**

💬 "Mudei minha rotina em 2 semanas. Nunca me senti tão no controle." — Ana, Gerente de Produto

💬 "Parei de trabalhar fins de semana. Meu chefe nem notou, só viu as entregas melhorarem." — Carlos, Dev Senior

**Oferta de lançamento (válida por 48h):**

De R$ 497 por R$ 197
ou 12x de R$ 19,70

**Garantia:** 7 dias. Se não gostar, devolvo 100%. Sem perguntas.

👉 [QUERO ME INSCREVER AGORA]

Dúvidas? Responda este email.

Abraço,

[Seu nome]

P.S.: As vagas são limitadas porque quero dar atenção individual aos alunos. Não deixe para depois.

---
*Você recebeu este email porque se inscreveu na nossa lista de espera.*"""

    def _generate_tiktok_script(self) -> str:
        return """# 🎵 3 Roteiros TikTok: Dicas de Produtividade

---

## Roteiro 1: "O Erro que Me Custou 2 Horas"

**[0-3s] Gancho:**
"Esse erro me fazia perder 2h todo dia sem perceber"

**[3-15s] Conteúdo:**
"Abrir email de manhã. Parece inocente, né? Mas cada notificação rouba 23 min do seu foco. Solução: só abra depois das 11h"

**[15-30s] Call-to-action:**
"Salva pra não esquecer! Qual seu maior vilão da produtividade? 👇"

---

## Roteiro 2: "Técnica do Pomodoro Explicada em 30s"

**[0-3s] Gancho:**
"25 min = 1 Pomodoro. Vou te ensinar a usar"

**[3-20s] Conteúdo:**
"Trabalhe 25 minutos focado. Pare por 5 minutos. Repita 4 vezes. Descanse 15 min. Simples e funciona!"

**[20-30s] Call-to-action:**
"Já usa Pomodoro? Comenta quantos consegue fazer por dia! ⏱️"

---

## Roteiro 3: "Minha Manhã Produtiva em 3 Passos"

**[0-3s] Gancho:**
"3 coisas que faço antes das 9h"

**[3-25s] Conteúdo:**
"1. Acordo, não olho celular. 2. Tomo café enquanto planejo o dia. 3. Faço a tarefa mais importante primeiro. Só depois abro emails."

**[25-30s] Call-to-action:**
"Qual dessas você vai testar amanhã? Me conta! 💪"

---
*Roteiros gerados por Dunder Mifflin Studio*"""

# Singleton para reutilização
_llm_client = None

def get_llm_client() -> LLMClient:
    """Retorna singleton do cliente LLM"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client

def generate_content(prompt: str, agent_slug: str = "agent") -> str:
    """Função convenience para gerar conteúdo"""
    client = get_llm_client()
    return client.generate(prompt, agent_slug)

if __name__ == "__main__":
    # Teste
    result = generate_content("Escreva um post de blog sobre produtividade.", "test")
    print(f"\nResultado ({len(result)} chars):\n{result[:500]}...")
