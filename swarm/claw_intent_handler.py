#!/usr/bin/env python3
"""
Claw Intent Handler - Detecta intenções de tarefa no Telegram
"""

import re
from typing import Optional, Tuple
from enum import Enum

class IntentType(Enum):
    TASK = "task"           # Pedido de execução
    QUESTION = "question"   # Pergunta simples
    CONVERSATION = "chat"   # Conversa normal
    COMMAND = "command"     # Comando direto

class ClawIntentHandler:
    """Detecta se mensagem é uma tarefa pra executar"""
    
    # Patterns de TASK (quando você quer que eu faça algo)
    TASK_PATTERNS = [
        # Português
        r'^preciso (?:que|de) (.+)',
        r'^quero (?:que|de) (.+)',
        r'^cria\s+(.+)',
        r'^faz\s+(.+)',
        r'^faz\s+pra\s+mim\s+(.+)',
        r'^implementa\s+(.+)',
        r'^adiciona\s+(.+)',
        r'^adiciona\s+uma?\s+(.+)',
        r'^cria\s+uma?\s+(.+)',
        r'^faz\s+uma?\s+(.+)',
        r'^ajusta\s+(.+)',
        r'^corrige\s+(.+)',
        r'^atualiza\s+(.+)',
        r'^remove\s+(.+)',
        r'^exclui\s+(.+)',
        r'^deleta\s+(.+)',
        r'^verifica\s+(.+)',
        r'^analisa\s+(.+)',
        r'^pesquisa\s+(.+)',
        r'^busca\s+(.+)',
        r'^encontra\s+(.+)',
        r'^gera\s+(.+)',
        r'^produz\s+(.+)',
        r'^escreve\s+(.+)',
        r'^documenta\s+(.+)',
        r'^testa\s+(.+)',
        r'^roda\s+(.+)',
        r'^executa\s+(.+)',
        r'^deploya\s+(.+)',
        r'^publica\s+(.+)',
        r'^sobe\s+(.+)',
        r'^coloca\s+(.+)',
        r'^configura\s+(.+)',
        r'^instala\s+(.+)',
        r'^atualiza\s+o\s+(.+)',
        r'^melhora\s+(.+)',
        r'^otimiza\s+(.+)',
        r'^refatora\s+(.+)',
        r'^migra\s+(.+)',
        r'^integra\s+(.+)',
        r'^conecta\s+(.+)',
        # Imperativos diretos
        r'^me\s+(?:mostra|dá|envia|manda)\s+(.+)',
        r'^quero\s+ver\s+(.+)',
        r'^preciso\s+ver\s+(.+)',
        # Inglês
        r'^create\s+(.+)',
        r'^make\s+(.+)',
        r'^build\s+(.+)',
        r'^implement\s+(.+)',
        r'^add\s+(.+)',
        r'^fix\s+(.+)',
        r'^update\s+(.+)',
        r'^check\s+(.+)',
        r'^analyze\s+(.+)',
        r'^research\s+(.+)',
        r'^find\s+(.+)',
        r'^generate\s+(.+)',
        r'^write\s+(.+)',
        r'^document\s+(.+)',
        r'^test\s+(.+)',
        r'^run\s+(.+)',
        r'^deploy\s+(.+)',
        r'^install\s+(.+)',
        r'^configure\s+(.+)',
        r'^optimize\s+(.+)',
        r'^refactor\s+(.+)',
        r'^migrate\s+(.+)',
        r'^integrate\s+(.+)',
        r'^setup\s+(.+)',
        r'^improve\s+(.+)',
        r'^enhance\s+(.+)',
        r'^debug\s+(.+)',
    ]
    
    # Patterns de QUESTION (perguntas que eu respondo direto)
    QUESTION_PATTERNS = [
        r'^(?:qual|quais|quem|onde|quando|como|por que|porquê)\s+',
        r'^(?:o que|o que é|o que são)\s+',
        r'^(?:me explique|me fala|me diz)\s+',
        r'^(?:você sabe|sabe me dizer)\s+',
        r'^(?:tem como|tem algum|tem alguma)\s+',
        r'^(?:pode me|consegue me)\s+',
        r'^(?:what|who|where|when|how|why)\s+',
        r'^(?:is there|are there|can you|do you)\s+',
        r'^(?:explain|tell me|show me)\s+',
    ]
    
    # Patterns de COMMAND (comandos diretos do sistema)
    COMMAND_PATTERNS = [
        r'^/\w+',  # /status, /help, etc
        r'^!\w+',  # !ralph, etc
        r'^claw[:\s]',
        r'^status\s*$',
        r'^modo\s+',
        r'^deploy\s+',
        r'^aprova',
        r'^sim$',
        r'^não$',
        r'^nao$',
        r'^ok$',
        r'^cancela',
    ]
    
    # Frases que indicam que NÃO é task (só conversa)
    CHAT_INDICATORS = [
        'obrigado', 'valeu', 'thanks', 'thank you',
        'boa noite', 'bom dia', 'boa tarde',
        'kkk', 'haha', 'hehe', 'lol',
        'tá bom', 'tá certo', 'okay', 'beleza',
        'entendi', 'compreendi', 'saquei', 'captei',
        'show', 'top', 'massa', 'legal', 'nice',
        'interessante', 'faz sentido',
        'tchau', 'até logo', 'bye',
        'como você está', 'tudo bem', 'tudo bom',
        'oi', 'olá', 'hello', 'hey',
    ]
    
    def __init__(self):
        self.pending_tasks = {}  # Para tracking de aprovações
        
    def detect_intent(self, message: str) -> Tuple[IntentType, Optional[str]]:
        """
        Detecta a intenção da mensagem
        Retorna: (tipo_da_intenção, conteúdo_extraído_ou_none)
        """
        msg_lower = message.lower().strip()
        
        # 1. Verifica se é comando direto
        for pattern in self.COMMAND_PATTERNS:
            if re.match(pattern, msg_lower, re.IGNORECASE):
                return IntentType.COMMAND, None
        
        # 2. Verifica se é só conversa
        for indicator in self.CHAT_INDICATORS:
            if indicator in msg_lower and len(msg_lower) < 50:
                return IntentType.CONVERSATION, None
        
        # 3. Verifica se é pergunta
        for pattern in self.QUESTION_PATTERNS:
            if re.match(pattern, msg_lower, re.IGNORECASE):
                # Mas pode ser pergunta disfarçada de task
                # "Como faz para criar X?" → conversa
                # "Como está o sistema?" → conversa
                if any(kw in msg_lower for kw in ['faz', 'criar', 'implementar', 'build']):
                    return IntentType.TASK, message
                return IntentType.QUESTION, None
        
        # 4. Verifica se é task
        for pattern in self.TASK_PATTERNS:
            match = re.match(pattern, message, re.IGNORECASE)
            if match:
                task_content = match.group(1) if match.groups() else message
                return IntentType.TASK, task_content
        
        # 5. Padrão: conversa
        return IntentType.CONVERSATION, None
    
    def is_task(self, message: str) -> bool:
        """Shortcut: é uma tarefa pra executar?"""
        intent, _ = self.detect_intent(message)
        return intent == IntentType.TASK
    
    def format_for_claw(self, message: str) -> str:
        """Extrai a parte relevante pra enviar pro Claw"""
        intent, content = self.detect_intent(message)
        if intent == IntentType.TASK and content:
            return content
        return message
    
    def should_ask_before(self, message: str) -> bool:
        """Decide se deve perguntar antes de executar"""
        intent, _ = self.detect_intent(message)
        if intent != IntentType.TASK:
            return False
        
        # Se parece destrutivo, sempre pergunta
        destructive = ['deleta', 'exclui', 'remove', 'apaga', 'drop', 'delete', 'remove']
        msg_lower = message.lower()
        if any(d in msg_lower for d in destructive):
            return True
        
        # Se parece crítico, pergunta
        critical = ['produção', 'production', 'main', 'master', 'principal']
        if any(c in msg_lower for c in critical):
            return True
        
        # Padrão: pergunta (modo ask_first)
        return True


# Singleton
_handler = None

def get_intent_handler() -> ClawIntentHandler:
    """Retorna instância global"""
    global _handler
    if _handler is None:
        _handler = ClawIntentHandler()
    return _handler


if __name__ == "__main__":
    # Testes
    handler = ClawIntentHandler()
    
    test_messages = [
        "Preciso de uma função de login",
        "Cria um dashboard novo",
        "Faz pra mim um relatório",
        "Qual é o status do sistema?",
        "Obrigado!",
        "kkkkkk",
        "/status",
        "Deploya o dashboard",
        "Implementa autenticação JWT",
        "Como está o tempo hoje?",
        "Adiciona testes unitários",
        "Remove aquele arquivo antigo",
        "Tá bom",
        "Beleza, entendi",
    ]
    
    for msg in test_messages:
        intent, content = handler.detect_intent(msg)
        print(f"'{msg[:40]}...' → {intent.value} | {content[:30] if content else 'None'}...")
