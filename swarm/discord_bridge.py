#!/usr/bin/env python3
"""
Ralph Swarm - Discord Bridge v5.1
Com fila persistente e auto-recovery
"""

import discord
import asyncio
import json
import sqlite3
import os
import logging
import signal
import sys
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/discord_bridge.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('discord_bridge')

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import Forum Integration
from forum_handlers import setup_forum_handlers, FORUM_CHANNEL_IDS

# Import RAG Memory
try:
    from swarm.rag_memory import get_rag_memory
    HAS_RAG = True
    rag_memory = get_rag_memory()
except ImportError:
    HAS_RAG = False
    rag_memory = None

# Import Deploy Integration
sys.path.insert(0, str(Path(__file__).parent))
try:
    from deploy_integration import DeployCommandHandler
    DEPLOY_AVAILABLE = True
    deploy_handler = DeployCommandHandler()
except ImportError as e:
    logger.warning(f"Deploy integration não disponível: {e}")
    DEPLOY_AVAILABLE = False
    deploy_handler = None

# Import Claw Coordinator
sys.path.insert(0, str(Path(__file__).parent))
try:
    from claw_coordinator import ClawCoordinator, get_coordinator
    CLAW_AVAILABLE = True
    claw = get_coordinator()
except ImportError as e:
    logger.warning(f"Claw Coordinator não disponível: {e}")
    CLAW_AVAILABLE = False
    claw = None

# Load token
env_path = os.path.join(os.path.dirname(__file__), '.env')
DISCORD_TOKEN = None
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('DISCORD_TOKEN='):
                DISCORD_TOKEN = line.strip().split('=', 1)[1]
                break

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN not found")

# Import loop commands
try:
    from loop_commands import handle_loop_command
    LOOP_COMMANDS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Loop commands não disponível: {e}")
    LOOP_COMMANDS_AVAILABLE = False

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'dunder_mifflin.db')
PENDING_MESSAGES_TABLE = "discord_pending_messages"

class PendingMessageQueue:
    """Fila persistente de mensagens não processadas"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_table()
    
    def _init_table(self):
        """Cria tabela se não existir"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {PENDING_MESSAGES_TABLE} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_message_id TEXT NOT NULL,
                discord_channel_id TEXT NOT NULL,
                author_id TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                retry_count INTEGER DEFAULT 0,
                error TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def add(self, message_id: str, channel_id: str, author_id: str, content: str):
        """Adiciona mensagem à fila"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO {PENDING_MESSAGES_TABLE} 
                (discord_message_id, discord_channel_id, author_id, content)
                VALUES (?, ?, ?, ?)
            """, (message_id, channel_id, author_id, content))
            conn.commit()
            logger.info(f"📥 Mensagem {message_id} adicionada à fila")
        except sqlite3.OperationalError as e:
            logger.error(f"❌ Erro ao adicionar à fila: {e}")
        finally:
            if conn:
                conn.close()
    
    def get_pending(self, limit: int = 50) -> list:
        """Busca mensagens pendentes"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT id, discord_message_id, discord_channel_id, author_id, content, retry_count
            FROM {PENDING_MESSAGES_TABLE}
            WHERE processed_at IS NULL AND retry_count < 5
            ORDER BY created_at ASC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def mark_processed(self, message_id: str):
        """Marca mensagem como processada"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE {PENDING_MESSAGES_TABLE}
            SET processed_at = CURRENT_TIMESTAMP
            WHERE discord_message_id = ?
        """, (message_id,))
        conn.commit()
        conn.close()
    
    def increment_retry(self, db_id: int, error: str = None):
        """Incrementa contador de retry"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE {PENDING_MESSAGES_TABLE}
            SET retry_count = retry_count + 1, error = ?
            WHERE id = ?
        """, (error, db_id))
        conn.commit()
        conn.close()
    
    def get_stats(self) -> dict:
        """Estatísticas da fila"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT 
                COUNT(CASE WHEN processed_at IS NULL THEN 1 END) as pending,
                COUNT(CASE WHEN processed_at IS NOT NULL THEN 1 END) as processed,
                COUNT(CASE WHEN retry_count >= 5 THEN 1 END) as failed
            FROM {PENDING_MESSAGES_TABLE}
        """)
        row = cursor.fetchone()
        conn.close()
        return {
            'pending': row[0],
            'processed': row[1],
            'failed': row[2]
        }

# Instância global da fila
pending_queue = PendingMessageQueue(DB_PATH)

class RAGReviewView(discord.ui.View):
    """View com botões 👍/👎 para review"""
    
    def __init__(self, task_id: str, task_type: str, project: str,
                 task_desc: str, output: str, agent_name: str):
        super().__init__(timeout=86400)
        self.task_id = task_id
        self.task_type = task_type
        self.project = project
        self.task_desc = task_desc
        self.output = output
        self.agent_name = agent_name

    @discord.ui.button(label="👍 Aprovar", style=discord.ButtonStyle.green, custom_id="approve")
    async def approve_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not HAS_RAG:
            await interaction.response.send_message("❌ RAG não disponível", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        
        entry_id = rag_memory.save_example(
            task_type=self.task_type,
            project=self.project,
            task=self.task_desc,
            output=self.output,
            approved_by=str(interaction.user),
            quality_score=5,
            tags=[self.task_type, self.project, self.agent_name],
            agent_slug=self.agent_name,
            task_id=self.task_id
        )

        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.add_field(name="✅ Status", value=f"Aprovado por {interaction.user.mention}", inline=False)
        
        await interaction.message.edit(embed=embed, view=None)
        await interaction.followup.send(f"✅ Aprovado! ID: `{entry_id}`", ephemeral=True)

    @discord.ui.button(label="👎 Reprovar", style=discord.ButtonStyle.red, custom_id="reject")
    async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not HAS_RAG:
            await interaction.response.send_message("❌ RAG não disponível", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        
        thread = await interaction.message.create_thread(
            name=f"📝 Feedback - {self.agent_name}",
            auto_archive_duration=1440
        )
        
        await thread.send(
            f"{interaction.user.mention} **Por favor, explique o que está errado.**\n\n"
            f"Task: {self.task_desc[:100]}..."
        )

        embed = interaction.message.embeds[0]
        embed.color = discord.Color.orange()
        embed.add_field(
            name="⏳ Aguardando Feedback",
            value=f"Reprovado por {interaction.user.mention}",
            inline=False
        )

        await interaction.message.edit(embed=embed, view=None)
        await interaction.followup.send(f"📝 Thread criada", ephemeral=True)


class SwarmDiscordBridge(discord.Client):
    """Discord Bridge com fila persistente"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents)

        self.swarm_channels = {}
        self.command_prefix = "!ralph"
        self.output_channel_name = "ralph-output"
        self.processing_pending = False
        
        # Setup Forum Integration
        self.forum = setup_forum_handlers(self)

    def get_project_context(self, message: discord.Message) -> str:
        """Extrai contexto do projeto do nome do canal"""
        channel_name = message.channel.name
        if channel_name.startswith("projeto-"):
            return channel_name.replace("projeto-", "")
        return channel_name

    def load_project_brief(self, project: str) -> str:
        """Carrega PROJECT.md"""
        project_dir = os.path.join(os.path.dirname(__file__), 'projects', project)
        project_file = os.path.join(project_dir, 'PROJECT.md')

        if os.path.exists(project_file):
            try:
                with open(project_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Erro ao carregar brief: {e}")
                return ""
        return ""

    async def on_ready(self):
        """Bot pronto - inicia processamento de pendentes"""
        logger.info(f"🤖 Bot online! {self.user.name}")
        logger.info(f"   Connected to {len(self.guilds)} guild(s)")

        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="!ralph help | Fila persistente ativa"
            )
        )

        await self._init_channel_mappings()
        
        # Inicia processamento de mensagens pendentes
        self.loop.create_task(self._process_pending_messages())
        self.loop.create_task(self._notification_poller())
        
        # Status da fila
        stats = pending_queue.get_stats()
        if stats['pending'] > 0:
            logger.info(f"📥 {stats['pending']} mensagens pendentes na fila")

    async def _init_channel_mappings(self):
        """Inicializa mapeamentos de canais"""
        for guild in self.guilds:
            for channel in guild.text_channels:
                if "swarm" in channel.name.lower():
                    self.swarm_channels[channel.id] = {
                        "name": channel.name,
                        "guild": guild.name
                    }

    async def _process_pending_messages(self):
        """Processa mensagens pendentes da fila"""
        await asyncio.sleep(5)  # Espera bot ficar pronto
        
        while True:
            try:
                if not self.processing_pending:
                    pending = pending_queue.get_pending(limit=10)
                    
                    if pending:
                        logger.info(f"🔄 Processando {len(pending)} mensagens pendentes...")
                        self.processing_pending = True
                        
                        for row in pending:
                            db_id, msg_id, ch_id, author_id, content, retry_count = row
                            
                            try:
                                channel = self.get_channel(int(ch_id))
                                if channel:
                                    # Tenta buscar mensagem do Discord
                                    try:
                                        message = await channel.fetch_message(int(msg_id))
                                        
                                        # Verifica se é aprovação antes de fazer relay
                                        if 'aprovado' in message.content.lower():
                                            handled = await self._handle_approval(message)
                                            if handled:
                                                pending_queue.mark_processed(msg_id)
                                                logger.info(f"✅ Aprovação processada da fila: {msg_id}")
                                                continue
                                        
                                        await self._relay_to_swarm(message)
                                        pending_queue.mark_processed(msg_id)
                                        logger.info(f"✅ Mensagem {msg_id} processada da fila")
                                    except discord.NotFound:
                                        # Mensagem não existe mais
                                        pending_queue.mark_processed(msg_id)
                                        logger.warning(f"⚠️ Mensagem {msg_id} não encontrada no Discord")
                                else:
                                    pending_queue.increment_retry(db_id, "Canal não encontrado")
                                    
                            except Exception as e:
                                pending_queue.increment_retry(db_id, str(e))
                                logger.error(f"❌ Erro ao processar mensagem {msg_id}: {e}")
                        
                        self.processing_pending = False
                        
            except Exception as e:
                logger.error(f"❌ Erro no processamento de pendentes: {e}")
                self.processing_pending = False
                
            await asyncio.sleep(30)  # Verifica a cada 30 segundos

    async def _notification_poller(self):
        """Poll para notificações"""
        await asyncio.sleep(5)
        
        while True:
            try:
                await self._check_pending_notifications()
            except Exception as e:
                logger.error(f"Erro no poller: {e}")
            await asyncio.sleep(10)

    async def _check_pending_notifications(self):
        """Verifica notificações pendentes no banco"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT m.id, m.content, m.mentions, c.name
                FROM swarm_messages m
                JOIN swarm_channels c ON m.channel_id = c.id
                WHERE m.author_type = 'system'
                AND m.author_id = 'ralph'
                AND (m.content LIKE '🎯%' OR m.content LIKE '✅%' OR m.content LIKE '🎩%' OR m.content LIKE '📋%')
                AND m.created_at > datetime('now', '-1 hour')
                AND m.edited_at IS NULL
                ORDER BY m.created_at ASC
                LIMIT 10
            """)

            rows = cursor.fetchall()

            for row in rows:
                msg_id, content, mentions_json, channel_name = row
                try:
                    metadata = json.loads(mentions_json or '{}')
                    discord_channel_id = metadata.get('discord_channel_id')

                    if discord_channel_id:
                        channel = self.get_channel(discord_channel_id)
                        if channel:
                            if "🎩" in content and "Perguntas" in content:
                                await channel.send(content)
                            elif "📋" in content and ("Plano" in content or "plano" in content):
                                await channel.send(content)
                            else:
                                embed = discord.Embed(
                                    title="✅ Task Completada",
                                    description=content[:4000],
                                    color=0x2ecc71
                                )
                                await channel.send(embed=embed)

                            cursor.execute(
                                "UPDATE swarm_messages SET edited_at = datetime('now') WHERE id = ?",
                                (msg_id,)
                            )
                            conn.commit()

                except Exception as e:
                    logger.error(f"Erro ao enviar notificação: {e}")

            conn.close()

        except Exception as e:
            logger.error(f"Erro ao verificar notificações: {e}")

    async def on_message(self, message: discord.Message):
        """Handler de mensagens com fila persistente"""
        if message.author.bot:
            return

        # 🚀 DETECTA COMANDOS DE DEPLOY NATURAIS - PRIMEIRO!
        # Isso previne que "deploya o dashboard" vire uma task do swarm
        if DEPLOY_AVAILABLE and deploy_handler and deploy_handler.is_deploy_command(message.content):
            await self._handle_natural_deploy(message)
            return  # Não processa como mensagem normal

        # VERIFICA SE É MENÇÃO NO FÓRUM PRIMEIRO
        if isinstance(message.channel, discord.Thread):
            # Detecta automaticamente se é um fórum (ForumChannel = type 15)
            is_forum = False
            if message.channel.parent:
                # Discord.py 2.0+: ForumChannel tem type 15
                is_forum = getattr(message.channel.parent, 'type', None) and message.channel.parent.type.value == 15
            
            # Se FORUM_CHANNEL_IDS estiver vazio, aceita qualquer fórum
            # Se tiver valores, só aceita os fóruns listados
            channel_allowed = not FORUM_CHANNEL_IDS or message.channel.parent_id in FORUM_CHANNEL_IDS
            
            if is_forum and channel_allowed:
                logger.info(f"📁 Fórum detectado: {message.channel.name} (parent: {message.channel.parent_id})")
                logger.info(f"   Menciona bot? {self.user in message.mentions}")
                
                if self.user in message.mentions:
                    logger.info(f"📢 Menção no fórum detectada: {message.channel.name}")
                    await self.forum.on_message(message)
                    return  # Não processa como mensagem normal
        
        # Adiciona à fila persistente ANTES de processar
        pending_queue.add(
            str(message.id),
            str(message.channel.id),
            str(message.author),
            message.content
        )
        
        # Processa thread de feedback
        if await self._handle_thread_feedback(message):
            pending_queue.mark_processed(str(message.id))
            return
        
        # Aprovação
        if 'aprovado' in message.content.lower():
            handled = await self._handle_approval(message)
            if handled:
                pending_queue.mark_processed(str(message.id))
                return

        # Comando
        if message.content.startswith(self.command_prefix):
            await self._handle_command(message)
            pending_queue.mark_processed(str(message.id))
            return

        # Canal mapeado
        if message.channel.id in self.swarm_channels:
            await self._relay_to_swarm(message)
            pending_queue.mark_processed(str(message.id))
            return

        # Reply para bot
        if message.reference and message.reference.message_id:
            try:
                ref_msg = await message.channel.fetch_message(message.reference.message_id)
                if ref_msg.author.bot and '🎩' in ref_msg.content:
                    await self._relay_to_swarm(message, from_reply=True)
                    pending_queue.mark_processed(str(message.id))
                    return
            except:
                pass

        await self._check_and_relay_any_channel(message)
        pending_queue.mark_processed(str(message.id))

    async def _handle_natural_deploy(self, message: discord.Message):
        """Processa comandos de deploy em linguagem natural"""
        # Envia reação imediata
        await message.add_reaction("🚀")
        
        # Envia mensagem de status
        status_msg = await message.reply("🚀 Detectado comando de deploy! Iniciando...")
        
        try:
            # Executa deploy
            result = await deploy_handler.handle(
                message.content, 
                agent_slug="ralph",
                mission_id=f"discord-deploy-{message.id}"
            )
            
            if result:
                # Edita mensagem com resultado
                await status_msg.edit(content=result)
                
                # Adiciona reação de sucesso/falha
                if "✅" in result:
                    await message.add_reaction("✅")
                elif "❌" in result:
                    await message.add_reaction("❌")
            else:
                await status_msg.edit(content="❓ Não entendi o comando de deploy. Tente: `!ralph projects` para ver disponíveis.")
                await message.add_reaction("❓")
                
        except Exception as e:
            logger.error(f"Erro no deploy natural: {e}")
            await status_msg.edit(content=f"❌ Erro: {str(e)[:200]}")
            await message.add_reaction("❌")

    async def on_thread_create(self, thread: discord.Thread):
        """Novo thread criado no fórum"""
        await self.forum.on_thread_create(thread)

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Processa reações"""
        # Ignora reações do próprio bot
        if payload.user_id == self.user.id:
            return
        
        # Processa reações de planos do fórum
        await self.forum.on_raw_reaction_add(payload)

    async def _handle_thread_feedback(self, message: discord.Message):
        """Processa feedback em threads"""
        if not HAS_RAG or not isinstance(message.channel, discord.Thread):
            return False

        thread = message.channel
        if not thread.name.startswith("📝 Feedback"):
            return False

        if message.author.bot:
            return False

        try:
            parent = thread.parent
            async for msg in parent.history(limit=20):
                if msg.author.bot and len(msg.embeds) > 0:
                    # Processa feedback...
                    await thread.send("Obrigado pelo feedback!")
                    return True

        except Exception as e:
            logger.error(f"Erro no thread feedback: {e}")

        return False

    async def _handle_approval(self, message: discord.Message):
        """Handler de aprovação"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Busca task mais recente pendente de aprovação
            cursor.execute("""
                SELECT t.id, t.task_code, t.original_request, t.execution_plan
                FROM swarm_tasks t
                WHERE t.status IN ('awaiting_approval', 'awaiting_questions')
                ORDER BY t.created_at DESC
                LIMIT 1
            """)

            row = cursor.fetchone()
            if not row:
                conn.close()
                return False

            task_id, task_code, original_request, execution_plan = row

            # Atualiza status
            cursor.execute("""
                UPDATE swarm_tasks 
                SET status = 'approved', 
                    started_at = datetime('now')
                WHERE id = ?
            """, (task_id,))
            conn.commit()
            conn.close()

            # Notifica
            await message.channel.send(
                f"✅ Task `{task_code}` aprovada! Iniciando execução..."
            )

            # Inicia execução
            from coordination_engine import SwarmCoordinator
            coordinator = SwarmCoordinator()
            
            plan = coordinator.analyze_task(original_request)
            result = coordinator.execute_swarm(original_request, plan, task_id)

            return True

        except Exception as e:
            logger.error(f"Erro na aprovação: {e}")
            return False

    async def _handle_command(self, message: discord.Message):
        """Handler de comandos"""
        content = message.content[len(self.command_prefix):].strip()
        parts = content.split()
        command = parts[0] if parts else "help"

        if command == "help":
            await self._cmd_help(message)
        elif command == "status":
            await self._cmd_status(message)
        elif command == "agents":
            await self._cmd_agents(message)
        elif command == "task":
            await self._cmd_task(message, parts[1:])
        elif command == "retry":
            await self._cmd_retry(message)
        elif command == "queue":
            await self._cmd_queue(message)
        elif command == "rag":
            await self._cmd_rag(message, parts[1:])
        elif command == "loop":
            await self._cmd_loop(message, parts[1:])
        elif command == "deploy":
            await self._cmd_deploy(message, parts[1:])
        elif command == "projects":
            await self._cmd_projects(message)
        elif command == "claw":
            await self._cmd_claw(message, parts[1:])
        elif command == "modo":
            await self._cmd_modo(message, parts[1:])
        else:
            await message.reply("❓ Comando desconhecido. Use `!ralph help`")

    async def _cmd_help(self, message: discord.Message):
        """Mostra ajuda completa de todos os comandos"""
        embed = discord.Embed(
            title="🐝 Ralph Swarm - Comandos",
            description="Sistema multi-agente com fila persistente e loops iterativos",
            color=0x7289DA
        )
        
        embed.add_field(
            name="📝 Gestão de Tarefas",
            value=(
                "`!ralph task <descrição>` - Cria nova tarefa\n"
                "`!ralph retry` - Reprocessa mensagens perdidas\n"
                "`!ralph queue` - Status da fila de mensagens"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🚀 Deploy",
            value=(
                "`!ralph deploy <projeto>` - Deploya projeto\n"
                "`!ralph deploy <projeto> staging` - Deploy em staging\n"
                "`!ralph projects` - Lista projetos configurados"
            ),
            inline=False
        )
        
        # Seção de Loops (substituído pelo Claw)
        if LOOP_COMMANDS_AVAILABLE:
            embed.add_field(
                name="🔄 Loops (Legado - use Claw)",
                value="Loops foram substituídos pelo **Claw Coordinator**. Use `!ralph claw <tarefa>`",
                inline=False
            )
        
        # Seção do Claw Coordinator
        if CLAW_AVAILABLE:
            embed.add_field(
                name="🤖 Claw Coordinator (Novo)",
                value=(
                    "`!ralph claw <tarefa>` - Delega tarefa pro Claw analisar e executar\n"
                    "`!ralph claw` - Status do coordinator\n"
                    "`!ralph modo` - Ver modo atual\n"
                    "`!ralph modo <modo>` - Altera modo (ask_first/execute_report/silent)\n\n"
                    "**Como funciona:**\n"
                    "• Você fala comigo (Claw)\n"
                    "• Eu analiso a complexidade\n"
                    "• Decido: faço direto, chamo 1 especialista, ou coordeno vários\n"
                    "• No modo `ask_first`, pergunto antes de executar\n"
                    "• Entrego resultado final, sem você gerenciar quem fez o quê"
                ),
                inline=False
            )
        else:
            embed.add_field(
                name="🔄 Loops (Iteração Contínua)",
                value=loop_section + "\n⚠️ *Sistema de loops não disponível no momento*",
                inline=False
            )
        
        embed.add_field(
            name="ℹ️ Informações",
            value=(
                "`!ralph status` - Status geral do swarm\n"
                "`!ralph agents` - Lista agentes disponíveis\n"
                "`!ralph rag status` - Estatísticas de memória RAG"
            ),
            inline=False
        )
        
        embed.add_field(
            name="💡 Dicas",
            value=(
                "• Use `--max 30` para tarefas complexas (padrão: 20)\n"
                "• Agentes: `dev`, `ralf`, `max`, `maya`, `scout`, `watcher`, `tracker`\n"
                "• Responda 🎩 para interagir com perguntas do Ralph"
            ),
            inline=False
        )
        
        await message.reply(embed=embed)

    async def _cmd_retry(self, message: discord.Message):
        """Força reprocessamento de mensagens pendentes"""
        pending = pending_queue.get_pending(limit=50)
        
        if not pending:
            await message.reply("✅ Nenhuma mensagem pendente na fila.")
            return
        
        count = 0
        for row in pending:
            db_id, msg_id, ch_id, author_id, content, retry_count = row
            try:
                channel = self.get_channel(int(ch_id))
                if channel:
                    try:
                        discord_msg = await channel.fetch_message(int(msg_id))
                        await self._relay_to_swarm(discord_msg)
                        pending_queue.mark_processed(msg_id)
                        count += 1
                    except discord.NotFound:
                        pending_queue.mark_processed(msg_id)
            except Exception as e:
                logger.error(f"Erro no retry: {e}")
        
        await message.reply(f"🔄 {count} mensagens reprocessadas da fila.")

    async def _cmd_queue(self, message: discord.Message):
        """Mostra status da fila"""
        stats = pending_queue.get_stats()
        
        embed = discord.Embed(
            title="📥 Fila de Mensagens",
            color=0xFFA500
        )
        embed.add_field(name="Pendentes", value=str(stats['pending']), inline=True)
        embed.add_field(name="Processadas", value=str(stats['processed']), inline=True)
        embed.add_field(name="Falhas", value=str(stats['failed']), inline=True)
        
        if stats['pending'] > 0:
            embed.add_field(
                name="💡 Dica",
                value="Use `!ralph retry` para reprocessar",
                inline=False
            )
        
        await message.reply(embed=embed)

    async def _cmd_status(self, message: discord.Message):
        """Status do swarm"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM swarm_agents")
            agent_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM swarm_tasks")
            task_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM swarm_tasks WHERE status = 'pending'")
            pending_count = cursor.fetchone()[0]

            conn.close()

            embed = discord.Embed(
                title="🐝 Ralph Swarm - Status",
                color=0x00FF00
            )
            embed.add_field(name="Agentes", value=str(agent_count), inline=True)
            embed.add_field(name="Tasks", value=str(task_count), inline=True)
            embed.add_field(name="Pendentes", value=str(pending_count), inline=True)
            
            # Status da fila
            queue_stats = pending_queue.get_stats()
            embed.add_field(
                name="📥 Fila",
                value=f"{queue_stats['pending']} pendentes",
                inline=True
            )

            await message.reply(embed=embed)

        except Exception as e:
            await message.reply(f"❌ Erro: {e}")

    async def _cmd_agents(self, message: discord.Message):
        """Lista agentes"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT name, role, model_tier FROM swarm_agents ORDER BY id")
            agents = cursor.fetchall()
            conn.close()

            embed = discord.Embed(title="🤖 Agentes", color=0xFFA500)
            emojis = {"ralph": "🎩", "scout": "🔍", "max": "🛠️", 
                     "maya": "📝", "tracker": "📊", "watcher": "👁️"}

            for name, role, tier in agents:
                emoji = emojis.get(name.lower(), "🤖")
                tier_emoji = "$" * (3 if tier == "expensive" else 2 if tier == "medium" else 1)
                embed.add_field(name=f"{emoji} {name.title()}", 
                              value=f"{role}\n{tier_emoji}", inline=True)

            await message.reply(embed=embed)

        except Exception as e:
            await message.reply(f"❌ Erro: {e}")

    async def _cmd_task(self, message: discord.Message, args: list):
        """Cria nova task"""
        if not args:
            await message.reply("❌ Uso: `!ralph task <descrição>`")
            return

        task_description = " ".join(args)
        project = self.get_project_context(message)

        try:
            from ralph_swarm_core import SwarmTaskManager
            tasks = SwarmTaskManager()

            project_brief = self.load_project_brief(project)
            full_request = f"[{project.upper()}] {task_description}"
            
            if project_brief:
                full_request += f"\n\n[CONTEXT]:\n{project_brief[:1500]}..."

            task = tasks.create_task(
                original_request=full_request,
                coordinator_agent_slug='ralph',
                project=project,
                source='discord',
                channel_id=message.channel.id
            )

            embed = discord.Embed(
                title="✅ Tarefa Criada",
                description=f"**Projeto:** {project}\n**Descrição:** {task_description}",
                color=0x00FF00
            )
            embed.add_field(name="Task ID", value=f"`{task.task_code}`", inline=True)
            embed.set_footer(text="🎩 Ralph vai analisar e fazer perguntas")

            await message.reply(embed=embed)
            await message.add_reaction("✅")

        except Exception as e:
            await message.reply(f"❌ Erro: {e}")

    async def _cmd_rag(self, message: discord.Message, parts: list):
        """Comandos RAG"""
        if not HAS_RAG:
            await message.reply("❌ RAG não disponível")
            return

        subcommand = parts[0] if parts else "status"
        
        if subcommand == "status":
            stats = rag_memory.get_stats()
            embed = discord.Embed(title="🧠 RAG - Estatísticas", color=0x9B59B6)
            embed.add_field(name="✅ Exemplos", value=str(stats['examples']), inline=True)
            embed.add_field(name="❌ Erros", value=str(stats['mistakes']), inline=True)
            embed.add_field(name="⭐ Qualidade", value=f"{stats['avg_quality']}/5", inline=True)
            await message.reply(embed=embed)
        else:
            await message.reply("❓ Use: `!ralph rag status`")

    async def _cmd_loop(self, message: discord.Message, parts: list):
        """Comandos de loop (iteração contínua) - DESATIVADO (use claw)"""
        await message.reply("🔄 Loops foram substituídos pelo **Claw Coordinator**. Use `!ralph claw <tarefa>`")

    async def _cmd_claw(self, message: discord.Message, parts: list):
        """Claw Coordinator - processa tarefas diretamente"""
        if not CLAW_AVAILABLE or not claw:
            await message.reply("❌ Claw Coordinator não disponível. Verifique os logs.")
            return
        
        if not parts:
            # Mostra status
            status = claw.get_status()
            await message.reply(status)
            return
        
        # Junta o resto como a tarefa
        task = " ".join(parts)
        
        # Reação imediata
        await message.add_reaction("🤖")
        
        # Processa pela Claw
        try:
            result = await claw.process_request(task)
            
            # Se precisa de aprovação (modo ask_first)
            if "Quer que eu prossiga?" in result:
                await message.reply(result)
                # Salva referência da mensagem pra aprovação depois
                # (simplificado por enquanto)
            else:
                # Já executou
                await message.reply(result)
                await message.add_reaction("✅")
                
        except Exception as e:
            logger.error(f"Erro no Claw: {e}")
            await message.reply(f"❌ Erro: {str(e)[:200]}")
            await message.add_reaction("❌")

    async def _cmd_modo(self, message: discord.Message, parts: list):
        """Altera modo de operação do Claw"""
        if not CLAW_AVAILABLE or not claw:
            await message.reply("❌ Claw Coordinator não disponível.")
            return
        
        if not parts:
            await message.reply(f"Modo atual: **{claw.mode}**\n\nModos disponíveis:\n- `ask_first`: Pergunta antes de executar\n- `execute_report`: Executa e reporta\n- `silent`: Executa silenciosamente")
            return
        
        new_mode = parts[0].lower()
        if new_mode not in ["ask_first", "execute_report", "silent"]:
            await message.reply("❌ Modo inválido. Use: ask_first, execute_report, ou silent")
            return
        
        claw.mode = new_mode
        await message.reply(f"✅ Modo alterado para: **{new_mode}**")

    async def _cmd_deploy(self, message: discord.Message, parts: list):
        """Handler de deploy"""
        if not DEPLOY_AVAILABLE or not deploy_handler:
            await message.reply("❌ Sistema de deploy não disponível. Verifique os logs.")
            return
        
        if not parts:
            await message.reply("❌ Uso: `!ralph deploy <projeto> [ambiente]`\nExemplo: `!ralph deploy dashboard` ou `!ralph deploy api staging`")
            return
        
        project_name = parts[0]
        env = parts[1] if len(parts) > 1 else "production"
        
        # Monta comando natural
        deploy_command = f"deploya o {project_name}"
        if env != "production":
            deploy_command += f" pra {env}"
        
        # Envia mensagem inicial
        status_msg = await message.reply(f"🚀 Iniciando deploy de **{project_name}** ({env})...\n📊 Acompanhe em tempo real no Dashboard!")
        
        try:
            # Executa deploy
            result = await deploy_handler.handle(deploy_command, agent_slug="ralph")
            
            if result:
                # Atualiza mensagem com resultado
                if "✅" in result:
                    await status_msg.edit(content=result)
                elif "❌" in result:
                    await status_msg.edit(content=result)
                else:
                    await status_msg.edit(content=f"📋 {result}")
            else:
                await status_msg.edit(content=f"❌ Projeto '{project_name}' não encontrado. Use `!ralph projects` para ver os disponíveis.")
                
        except Exception as e:
            logger.error(f"Erro no deploy: {e}")
            await status_msg.edit(content=f"❌ Erro durante deploy: {str(e)[:200]}")

    async def _cmd_projects(self, message: discord.Message):
        """Lista projetos disponíveis"""
        if not DEPLOY_AVAILABLE or not deploy_handler:
            await message.reply("❌ Sistema de deploy não disponível.")
            return
        
        try:
            projects_list = deploy_handler.deployer.list_available_projects()
            embed = discord.Embed(
                title="📁 Projetos Configurados",
                description=projects_list[:4000] if projects_list else "Nenhum projeto encontrado.",
                color=0x3498DB
            )
            embed.set_footer(text="Crie um .ralph-deploy.yml na raiz do projeto para adicionar")
            await message.reply(embed=embed)
        except Exception as e:
            logger.error(f"Erro ao listar projetos: {e}")
            await message.reply(f"❌ Erro ao listar projetos: {e}")

    async def _relay_to_swarm(self, message: discord.Message, from_reply: bool = False):
        """Relay para swarm"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            project = self.get_project_context(message)
            channel_name = f"discord-{message.channel.id}"
            
            cursor.execute("SELECT id FROM swarm_channels WHERE name = ?", (channel_name,))
            result = cursor.fetchone()

            if not result:
                cursor.execute("""
                    INSERT INTO swarm_channels (channel_code, name, description, created_by)
                    VALUES (?, ?, ?, ?)
                """, (channel_name, channel_name, f"Discord: {message.channel.name}", "system"))
                conn.commit()
                channel_id = cursor.lastrowid
            else:
                channel_id = result[0]

            message_code = f"MSG-{uuid.uuid4().hex[:8].upper()}"
            
            cursor.execute("""
                INSERT INTO swarm_messages (message_code, channel_id, author_type, author_id, content, mentions)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                message_code, channel_id, "user", str(message.author), message.content,
                json.dumps({
                    "discord_message_id": message.id,
                    "discord_channel_id": message.channel.id,
                    "project": project,
                    "from_reply": from_reply
                })
            ))

            conn.commit()
            conn.close()

            await message.add_reaction("🐝")

        except Exception as e:
            logger.error(f"Erro no relay: {e}")

    async def _check_and_relay_any_channel(self, message: discord.Message):
        """Verifica se deve relay de qualquer canal"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            channel_name = f"discord-{message.channel.id}"
            
            cursor.execute("SELECT id FROM swarm_channels WHERE name = ?", (channel_name,))
            result = cursor.fetchone()
            conn.close()

            if result:
                await self._relay_to_swarm(message)

        except Exception as e:
            logger.error(f"Erro no check: {e}")

    async def send_task_for_review(self, channel_id: int, task_id: str, agent_name: str,
                                    project: str, task_type: str, task_desc: str, output: str):
        """Envia task para review"""
        try:
            channel = self.get_channel(channel_id)
            if not channel:
                return

            embed = discord.Embed(
                title=f"🤖 {agent_name} - Output",
                description=f"**Task:** {task_desc[:150]}{'...' if len(task_desc) > 150 else ''}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            embed.add_field(name="📁 Projeto", value=project, inline=True)
            embed.add_field(name="📋 Tipo", value=task_type, inline=True)

            output_display = output[:800] + "..." if len(output) > 800 else output
            embed.add_field(name="📤 Output", value=f"```\n{output_display}\n```", inline=False)

            view = RAGReviewView(
                task_id=task_id, task_type=task_type, project=project,
                task_desc=task_desc, output=output, agent_name=agent_name
            )

            await channel.send(embed=embed, view=view)

        except Exception as e:
            logger.error(f"Erro ao enviar review: {e}")


def main():
    """Main entry point"""
    client = SwarmDiscordBridge()
    
    # Graceful shutdown
    def signal_handler(sig, frame):
        logger.info("🛑 Sinal de shutdown recebido")
        asyncio.create_task(client.close())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run
    client.run(DISCORD_TOKEN)


if __name__ == '__main__':
    main()
