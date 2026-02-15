#!/usr/bin/env python3
"""
Integração Forum Handlers → Discord Bridge v5.1

Este arquivo mostra como modificar o discord_bridge.py existente
para adicionar suporte a fóruns.
"""

"""
INSTRUÇÕES DE INTEGRAÇÃO:

1. No topo do discord_bridge.py, adicione:
   
   from swarm.forum_handlers import setup_forum_handlers, FORUM_CHANNEL_IDS

2. No __init__ do RalphSwarmBot, adicione:
   
   self.forum = setup_forum_handlers(self)

3. Adicione os event handlers ao bot:

   @bot.event
   async def on_thread_create(thread):
       await bot.forum.on_thread_create(thread)

   @bot.event  
   async def on_raw_reaction_add(payload):
       # Processa reações de planos primeiro
       await bot.forum.on_raw_reaction_add(payload)
       # Depois continua com processamento normal...

4. Modifique o on_message existente para verificar menções:

   No início do on_message, adicione:
   
   if bot.user in message.mentions and isinstance(message.channel, discord.Thread):
       await bot.forum.on_message(message)
       return  # Não processa como mensagem normal

5. Configure os canais de fórum no início do arquivo:

   FORUM_CHANNEL_IDS = [123456789, 987654321]  # IDs dos fóruns

"""

# Exemplo de como fica o código integrado:

EXEMPLO_INTEGRACAO = '''
import discord
from swarm.forum_handlers import setup_forum_handlers, FORUM_CHANNEL_IDS

class RalphSwarmBot(discord.Client):
    def __init__(self):
        super().__init__()
        self.forum = setup_forum_handlers(self)
    
    async def on_thread_create(self, thread):
        """Novo thread no fórum"""
        await self.forum.on_thread_create(thread)
    
    async def on_message(self, message):
        """Mensagem no Discord"""
        # Ignora mensagens do próprio bot
        if message.author.bot:
            return
        
        # Verifica se é menção no fórum
        if self.user in message.mentions and isinstance(message.channel, discord.Thread):
            await self.forum.on_message(message)
            return  # Não processa como comando normal
        
        # Processa comandos normais (!ralph, etc)
        await self._process_commands(message)
    
    async def on_raw_reaction_add(self, payload):
        """Reação adicionada"""
        # Processa reações de planos do fórum primeiro
        await self.forum.on_raw_reaction_add(payload)
        
        # Depois processa outras reações normalmente...
'''

# SQL para rodar antes de iniciar:
SQL_SETUP = """
-- Rode isso no banco antes de usar:
-- cat migrations/001_forum_integration.sql | sqlite3 dunder_mifflin.db
-- Ou execute via Python:

from swarm.forum_handlers import ForumTaskManager
from pathlib import Path

db = ForumTaskManager(Path("dunder_mifflin.db"))
# Isso cria as tabelas automaticamente
"""

# Como testar:
TESTE = """
1. Configure FORUM_CHANNEL_IDS em forum_handlers.py
2. Rode a migration: python3 -c "from swarm.forum_handlers import ForumTaskManager; from pathlib import Path; ForumTaskManager(Path('dunder_mifflin.db'))"
3. Modifique discord_bridge.py conforme exemplo acima
4. Reinicie a bridge: ./discord_bridge.sh restart
5. Crie um post no fórum e mencione @Ralph
"""

if __name__ == "__main__":
    print("=" * 60)
    print("INTEGRAÇÃO RALPH + FORUM DISCORD")
    print("=" * 60)
    print("\n📋 Passos para integrar:\n")
    print("1. Execute a migration SQL:")
    print("   sqlite3 dunder_mifflin.db < migrations/001_forum_integration.sql")
    print("\n2. Configure os IDs dos fóruns em swarm/forum_handlers.py:")
    print("   FORUM_CHANNEL_IDS = [123456789, 987654321]")
    print("\n3. Modifique discord_bridge.py conforme o exemplo acima")
    print("\n4. Reinicie a bridge:")
    print("   ./discord_bridge.sh restart")
    print("\n" + "=" * 60)
    print(EXEMPLO_INTEGRACAO)
    print("=" * 60)
