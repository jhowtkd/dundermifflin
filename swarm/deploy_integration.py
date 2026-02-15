#!/usr/bin/env python3
"""
Ralph Deploy Integration - Conecta comandos naturais ao DeployerAgent

Adicione isso ao agent_brain.py ou discord_bridge.py para processar
comandos de deploy.
"""

import re
import asyncio
from typing import Optional, Tuple
from swarm.agents.deployer import DeployerAgent, DeployResult
from swarm.live_logger import get_logger

class DeployCommandHandler:
    """Processa comandos de deploy em linguagem natural"""
    
    DEPLOY_PATTERNS = [
        r'deploya\s+(?:o\s+|a\s+)?(.+)',
        r'faz\s+(?:o\s+|o\s+)?deploy\s+(?:do\s+|da\s+)?(.+)',
        r'publica\s+(?:o\s+|a\s+)?(.+)',
        r'sobe\s+(?:o\s+|a\s+)?(.+)',
        r'coloca\s+(?:o\s+|a\s+)?(.+)\s+no\s+ar',
    ]
    
    STATUS_PATTERNS = [
        r'status\s+(?:do\s+)?deploy',
        r'como\s+esta\s+(?:o\s+)?deploy',
        r'onde\s+esta\s+(?:o\s+)?deploy',
    ]
    
    LIST_PATTERNS = [
        r'lista\s+(?:os\s+)?projetos',
        r'quais\s+projetos',
        r'projetos\s+disponiveis',
        r'o\s+que\s+pode\s+deployar',
    ]
    
    def __init__(self):
        self.deployer = DeployerAgent()
        self.logger = get_logger()
    
    def is_deploy_command(self, message: str) -> bool:
        """Verifica se mensagem é um comando de deploy"""
        msg_lower = message.lower()
        
        for pattern in self.DEPLOY_PATTERNS:
            if re.search(pattern, msg_lower):
                return True
        
        for pattern in self.STATUS_PATTERNS:
            if re.search(pattern, msg_lower):
                return True
                
        for pattern in self.LIST_PATTERNS:
            if re.search(pattern, msg_lower):
                return True
        
        return False
    
    async def handle(self, message: str, agent_slug: str = "ralph", 
                     mission_id: str = None) -> Optional[str]:
        """
        Processa comando de deploy e retorna resposta.
        
        Exemplos de comandos suportados:
        - "deploya o meu-app"
        - "deploya o dashboard pra produção"
        - "deploya o api na railway"
        - "faz deploy do frontend"
        - "status do deploy"
        - "lista os projetos"
        """
        msg_lower = message.lower()
        
        # Lista projetos
        for pattern in self.LIST_PATTERNS:
            if re.search(pattern, msg_lower):
                return self.deployer.list_available_projects()
        
        # Status de deploy
        for pattern in self.STATUS_PATTERNS:
            if re.search(pattern, msg_lower):
                return "📊 Para ver status, acesse o Dashboard: http://localhost:3000"
        
        # Comando de deploy
        for pattern in self.DEPLOY_PATTERNS:
            match = re.search(pattern, msg_lower)
            if match:
                # Extrai o comando completo (pode incluir ajustes)
                full_command = message[match.start():]
                
                await self.logger.info(
                    agent_slug, 
                    f"🚀 Iniciando deploy: {full_command}",
                    mission_id=mission_id
                )
                
                # Executa deploy
                result = await self.deployer.handle_command(full_command, mission_id)
                
                return self._format_result(result)
        
        return None
    
    def _format_result(self, result: DeployResult) -> str:
        """Formata resultado do deploy para resposta"""
        if result.success:
            msg = f"✅ {result.message}"
            if result.url:
                msg += f"\n🔗 URL: {result.url}"
            if result.duration:
                msg += f"\n⏱️ Duração: {result.duration:.1f}s"
            return msg
        else:
            msg = f"❌ {result.message}"
            if result.error:
                # Trunca erro longo
                error_short = result.error[:500] + "..." if len(result.error) > 500 else result.error
                msg += f"\n\n💥 Erro:\n```\n{error_short}\n```"
            return msg


# Singleton
_handler = None

def get_deploy_handler() -> DeployCommandHandler:
    """Retorna handler global"""
    global _handler
    if _handler is None:
        _handler = DeployCommandHandler()
    return _handler


# Função de conveniência para integração rápida
async def handle_deploy_message(message: str, agent_slug: str = "ralph", 
                                 mission_id: str = None) -> Optional[str]:
    """
    Função simples para integrar em qualquer lugar.
    Retorna string de resposta se for comando de deploy, None caso contrário.
    """
    handler = get_deploy_handler()
    
    if not handler.is_deploy_command(message):
        return None
    
    return await handler.handle(message, agent_slug, mission_id)


# Exemplo de uso/integração
if __name__ == "__main__":
    async def test():
        # Testa detecção de comandos
        test_messages = [
            "deploya o dashboard",
            "faz deploy do meu-app pra produção",
            "lista os projetos",
            "qualquer outra coisa",
        ]
        
        handler = DeployCommandHandler()
        
        for msg in test_messages:
            is_deploy = handler.is_deploy_command(msg)
            print(f"'{msg}' -> Deploy command: {is_deploy}")
            
            if is_deploy:
                response = await handler.handle(msg)
                print(f"  Resposta: {response[:200]}...")
    
    asyncio.run(test())
