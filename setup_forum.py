#!/usr/bin/env python3
"""
Setup Script - Forum Integration for Ralph
Instala e configura a integração de fóruns automaticamente.
"""

import os
import sys
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "dunder_mifflin.db"
MIGRATION_PATH = BASE_DIR / "migrations" / "001_forum_integration.sql"
FORUM_HANDLERS_PATH = BASE_DIR / "swarm" / "forum_handlers.py"

def check_database():
    """Verifica se banco existe"""
    if not DB_PATH.exists():
        print(f"❌ Banco não encontrado: {DB_PATH}")
        print("   Execute primeiro: python3 db.py")
        return False
    return True

def run_migration():
    """Executa migration SQL"""
    if not MIGRATION_PATH.exists():
        print(f"❌ Migration não encontrada: {MIGRATION_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        with open(MIGRATION_PATH) as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
        print("✅ Tabelas do fórum criadas")
        return True
    except Exception as e:
        print(f"❌ Erro na migration: {e}")
        return False

def check_forum_handlers():
    """Verifica se forum_handlers.py existe"""
    if not FORUM_HANDLERS_PATH.exists():
        print(f"❌ Arquivo não encontrado: {FORUM_HANDLERS_PATH}")
        return False
    print("✅ Forum handlers encontrado")
    return True

def configure_forum_channels():
    """Guia configuração dos canais"""
    print("\n" + "=" * 50)
    print("CONFIGURAÇÃO DOS FÓRUNS")
    print("=" * 50)
    print("\nPara ativar a integração, você precisa:")
    print("\n1. Pegar os IDs dos canais de fórum no Discord:")
    print("   - Ative modo desenvolvedor: Configurações → Avançado")
    print("   - Clique direito no canal de fórum → 'Copiar ID'")
    print("\n2. Edite swarm/forum_handlers.py e adicione:")
    print("   FORUM_CHANNEL_IDS = [123456789, 987654321]")
    print("   (substitua pelos IDs reais)")

def show_integration_steps():
    """Mostra passos de integração"""
    print("\n" + "=" * 50)
    print("PRÓXIMOS PASSOS")
    print("=" * 50)
    print("""
1. Edite discord_bridge.py e adicione no topo:
   
   from swarm.forum_handlers import setup_forum_handlers

2. No __init__ do bot, adicione:
   
   self.forum = setup_forum_handlers(self)

3. Adicione o event handler:
   
   @bot.event
   async def on_thread_create(thread):
       await bot.forum.on_thread_create(thread)
   
   @bot.event
   async def on_message(message):
       # Antes de processar comandos:
       if bot.user in message.mentions and isinstance(message.channel, discord.Thread):
           await bot.forum.on_message(message)
           return
       # ... resto do código
   
   @bot.event
   async def on_raw_reaction_add(payload):
       await bot.forum.on_raw_reaction_add(payload)
       # ... resto do código

4. Reinicie a bridge:
   
   ./discord_bridge.sh restart

5. Teste:
   - Crie um post no fórum
   - Adicione várias mensagens com links/referências
   - Mencione @Ralph
   - Veja se ele registra a task
""")

def main():
    print("=" * 50)
    print("SETUP - Forum Integration for Ralph")
    print("=" * 50)
    
    # Verificações
    checks = [
        ("Banco de dados", check_database),
        ("Forum handlers", check_forum_handlers),
    ]
    
    all_passed = True
    for name, check_fn in checks:
        print(f"\n🔍 Verificando: {name}")
        if not check_fn():
            all_passed = False
    
    if not all_passed:
        print("\n❌ Verificações falharam. Corrija antes de continuar.")
        sys.exit(1)
    
    # Executa migration
    print("\n🔄 Executando migration...")
    if not run_migration():
        print("❌ Migration falhou")
        sys.exit(1)
    
    # Configuração
    configure_forum_channels()
    
    # Próximos passos
    show_integration_steps()
    
    print("\n" + "=" * 50)
    print("✅ Setup completo!")
    print("=" * 50)

if __name__ == "__main__":
    main()
