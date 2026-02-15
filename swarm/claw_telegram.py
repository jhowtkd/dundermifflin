#!/usr/bin/env python3
"""
Claw Telegram Integration
Conecta intent detection com execução via Claw Coordinator
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from claw_intent_handler import get_intent_handler, IntentType
from claw_coordinator import get_coordinator

class ClawTelegramInterface:
    """
    Interface entre Telegram e Claw Coordinator
    """
    
    def __init__(self):
        self.intent_handler = get_intent_handler()
        self.coordinator = get_coordinator()
        self.awaiting_approval = {}  # session_id -> decision
    
    async def process_message(self, message: str, session_id: str = "default") -> str:
        """
        Processa mensagem do Telegram
        """
        # 1. Detecta intenção
        intent, content = self.intent_handler.detect_intent(message)
        
        # 2. Se for comando direto
        if intent == IntentType.COMMAND:
            return await self._handle_command(message, session_id)
        
        # 3. Se for conversa, respondo normalmente
        if intent == IntentType.CONVERSATION:
            return None  # Deixa o processamento normal acontecer
        
        # 4. Se for pergunta simples
        if intent == IntentType.QUESTION:
            return None  # Respondo diretamente
        
        # 5. Se for task, processa pelo Claw
        if intent == IntentType.TASK:
            return await self._handle_task(message, session_id)
        
        return None
    
    async def _handle_command(self, message: str, session_id: str) -> str:
        """Handler de comandos diretos"""
        msg_lower = message.lower().strip()
        
        # Comandos de aprovação
        if msg_lower in ['sim', 's', 'yes', 'y', 'aprova', 'aprovar', 'ok']:
            return await self._approve_pending(session_id)
        
        if msg_lower in ['não', 'nao', 'n', 'no', 'cancela', 'cancelar']:
            return await self._reject_pending(session_id)
        
        # Comando status
        if msg_lower in ['status', 'claw', 'modo']:
            return self.coordinator.get_status()
        
        return None
    
    async def _handle_task(self, message: str, session_id: str) -> str:
        """Processa tarefa pelo Claw Coordinator"""
        # Extrai conteúdo da task
        task_content = self.intent_handler.format_for_claw(message)
        
        # Processa pela coordinator
        result = await self.coordinator.process_request(task_content)
        
        # Se precisa de aprovação, salva pra tracking
        if "Quer que eu prossiga?" in result:
            self.awaiting_approval[session_id] = {
                'task': task_content,
                'message': result
            }
        
        return result
    
    async def _approve_pending(self, session_id: str) -> str:
        """Usuário aprovou tarefa pendente"""
        if session_id not in self.awaiting_approval:
            return "❓ Não tenho nenhuma tarefa pendente de aprovação."
        
        pending = self.awaiting_approval.pop(session_id)
        
        # Executa tarefa
        return await self.coordinator.approve_and_execute()
    
    async def _reject_pending(self, session_id: str) -> str:
        """Usuário rejeitou tarefa pendente"""
        if session_id not in self.awaiting_approval:
            return None
        
        self.awaiting_approval.pop(session_id)
        return "✅ Cancelado. Se precisar de algo mais, é só falar."


# Singleton
_interface = None

def get_telegram_interface() -> ClawTelegramInterface:
    """Retorna instância global"""
    global _interface
    if _interface is None:
        _interface = ClawTelegramInterface()
    return _interface


# Função principal de integração
async def handle_telegram_message(message: str, session_id: str = "telegram:jeff") -> Optional[str]:
    """
    Função principal: recebe mensagem do Telegram, retorna resposta ou None
    
    Uso:
        response = await handle_telegram_message("Cria uma função de login")
        if response:
            # É uma task do Claw, enviar resposta
            send_message(response)
        else:
            # É conversa normal, processar normalmente
            pass
    """
    interface = get_telegram_interface()
    return await interface.process_message(message, session_id)


if __name__ == "__main__":
    async def test():
        # Teste
        result = await handle_telegram_message("Cria uma função de login")
        print(result)
    
    asyncio.run(test())
