"""
Ralph Swarm Discord Bridge
Integração entre o sistema Swarm e Discord
"""
import discord
import asyncio
import json
import sqlite3
import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import sys

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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import RAG Memory
try:
    from swarm.rag_memory import get_rag_memory
    HAS_RAG = True
    rag_memory = get_rag_memory()
except ImportError:
    HAS_RAG = False
    rag_memory = None

# Load token from .env
env_path = os.path.join(os.path.dirname(__file__), '.env')
DISCORD_TOKEN = None
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('DISCORD_TOKEN='):
                DISCORD_TOKEN = line.strip().split('=', 1)[1]
                break

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN not found in .env file")

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'dunder_mifflin.db')

# 🆕 RAG Review View - Botões para aprovar/reprovar
class RAGReviewView(discord.ui.View):
    """View com botões 👍/👎 para review de outputs do swarm"""

    def __init__(self, task_id: str, task_type: str, project: str,
                 task_desc: str, output: str, agent_name: str):
        super().__init__(timeout=86400)  # 24 horas
        self.task_id = task_id
        self.task_type = task_type
        self.project = project
        self.task_desc = task_desc
        self.output = output
        self.agent_name = agent_name

    @discord.ui.button(label="👍 Aprovar", style=discord.ButtonStyle.green, custom_id="approve")
    async def approve_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not HAS_RAG:
            await interaction.response.send_message("❌ RAG não está disponível", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        # Salva como exemplo
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

        # Atualiza embed
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()
        embed.add_field(name="✅ Status", value=f"Aprovado por {interaction.user.mention}", inline=False)
        embed.set_footer(text=f"ID: {entry_id} | Este exemplo será usado como referência futura")

        await interaction.message.edit(embed=embed, view=None)
        await interaction.followup.send(f"✅ Aprovado! ID: `{entry_id}`", ephemeral=True)

    @discord.ui.button(label="👎 Reprovar", style=discord.ButtonStyle.red, custom_id="reject")
    async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not HAS_RAG:
            await interaction.response.send_message("❌ RAG não está disponível", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        # Cria thread para feedback
        thread = await interaction.message.create_thread(
            name=f"📝 Feedback - {self.agent_name}",
            auto_archive_duration=1440
        )

        await thread.send(
            f"{interaction.user.mention} **Por favor, explique o que está errado.**\n\n"
            f"Task: {self.task_desc[:100]}...\n\n"
            f"💡 *Seja específico: o que falta? O que deveria ser diferente?*"
        )

        # Atualiza embed
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.orange()
        embed.add_field(
            name="⏳ Aguardando Feedback",
            value=f"Reprovado por {interaction.user.mention}\nThread: {thread.mention}",
            inline=False
        )

        await interaction.message.edit(embed=embed, view=None)
        await interaction.followup.send(
            f"📝 Thread criada: {thread.mention}\nPor favor, explique o erro lá.",
            ephemeral=True
        )


class SwarmDiscordBridge(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents)

        self.swarm_channels = {}  # Map Discord channel ID -> Swarm channel name
        self.command_prefix = "!ralph"
        self.output_channel_name = "ralph-output"  # Canal centralizado (opcional)

    def get_project_context(self, message: discord.Message) -> str:
        """Extract project context from channel name"""
        channel_name = message.channel.name

        # If channel starts with 'projeto-', extract project name
        if channel_name.startswith("projeto-"):
            return channel_name.replace("projeto-", "")

        # Otherwise use channel name as context
        return channel_name

    def load_project_brief(self, project: str) -> str:
        """Load PROJECT.md for a given project"""
        project_dir = os.path.join(os.path.dirname(__file__), 'projects', project)
        project_file = os.path.join(project_dir, 'PROJECT.md')

        if os.path.exists(project_file):
            try:
                with open(project_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"Error loading project brief for {project}: {e}")
                return ""
        return ""

    async def get_output_channel(self, guild: discord.Guild) -> Optional[discord.TextChannel]:
        """Get output channel if exists (hybrid mode)"""
        for channel in guild.text_channels:
            if channel.name == self.output_channel_name:
                return channel
        return None

    async def on_ready(self):
        """Called when bot is ready"""
        print(f"🤖 Ralph Swarm Discord Bridge online!")
        print(f"   Logged in as: {self.user.name} ({self.user.id})")
        print(f"   Connected to {len(self.guilds)} guild(s)")

        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="swarm commands | !ralph help"
            )
        )

        # Initialize swarm channels mapping
        await self._init_channel_mappings()

        # Start background task for notifications
        self.loop.create_task(self._notification_poller())

    async def _notification_poller(self):
        """Poll for pending notifications and send to Discord"""
        await asyncio.sleep(5)  # Wait for bot to be fully ready

        while True:
            try:
                await self._check_pending_notifications()
            except Exception as e:
                logger.error(f"Error in notification poller: {e}")

            await asyncio.sleep(10)  # Check every 10 seconds

    async def _check_pending_notifications(self):
        """Check for pending notifications in database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Find messages with system notifications that haven't been sent yet
            # Use edited_at as a flag - if NULL, message hasn't been sent
            # v4.0: Also include 🎩 (questions) and 📋 (plan approval) messages
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

            if rows:
                logger.info(f"📨 {len(rows)} notificações pendentes encontradas")

            for row in rows:
                msg_id, content, mentions_json, channel_name = row
                try:
                    metadata = json.loads(mentions_json or '{}')
                    discord_channel_id = metadata.get('discord_channel_id')

                    if discord_channel_id:
                        channel = self.get_channel(discord_channel_id)
                        if channel:
                            # Check if this is a delegation or completion message
                            if "🎯 Task Recebida" in content:
                                # Delegation notification - use embed
                                embed = discord.Embed(
                                    title="🎯 Task Recebida",
                                    description=content.replace("🎯 **Task Recebida:**", "").split("\n\n")[0],
                                    color=0x3498db
                                )
                                # Extract task details
                                lines = content.split("\n")
                                for line in lines[2:]:
                                    if line.startswith("📊") or line.startswith("🤖") or line.startswith("•"):
                                        embed.add_field(name="\u200b", value=line, inline=False)
                                await channel.send(embed=embed)
                            elif "🎩" in content and "Perguntas" in content:
                                # v4.0: Questions message - send as-is (already formatted)
                                await channel.send(content)
                            elif "📋" in content and ("Plano" in content or "plano" in content):
                                # v4.0: Plan for approval - send as-is
                                await channel.send(content)
                            else:
                                # Completion notification
                                embed = discord.Embed(
                                    title="✅ Task Completada",
                                    description=content[:4000],
                                    color=0x2ecc71
                                )
                                await channel.send(embed=embed)

                            logger.info(f"📨 Notificação enviada para Discord: {channel_name}")

                            # Mark as sent by setting edited_at
                            cursor.execute(
                                "UPDATE swarm_messages SET edited_at = datetime('now') WHERE id = ?",
                                (msg_id,)
                            )
                            conn.commit()

                except Exception as e:
                    logger.error(f"⚠️ Erro ao enviar notificação: {e}")

            conn.close()

        except Exception as e:
            logger.error(f"Error checking notifications: {e}")

    async def _init_channel_mappings(self):
        """Initialize mappings between Discord and Swarm channels"""
        for guild in self.guilds:
            for channel in guild.text_channels:
                # Auto-map channels with specific names
                if "swarm" in channel.name.lower():
                    self.swarm_channels[channel.id] = {
                        "name": channel.name,
                        "guild": guild.name
                    }
                    print(f"   📡 Mapped: #{channel.name} in {guild.name}")

    async def on_message(self, message: discord.Message):
        """Handle incoming messages"""
        # Ignore bot messages
        if message.author.bot:
            return
        
        # 🆕 Primeiro: tenta processar como thread de feedback RAG
        if await self._handle_thread_feedback(message):
            return
            
        # Check if message is "aprovado" (approval for a task)
        if 'aprovado' in message.content.lower():
            handled = await self._handle_approval(message)
            if handled:
                return

        # Check for command prefix
        if message.content.startswith(self.command_prefix):
            await self._handle_command(message)
            return

        # Check if message is in a mapped swarm channel
        if message.channel.id in self.swarm_channels:
            await self._relay_to_swarm(message)
            return

        # v4.0: Also capture replies to bot messages (for task responses)
        # Check if this is a reply to a bot message (Ralph's questions)
        if message.reference and message.reference.message_id:
            try:
                # Try to fetch the referenced message
                ref_msg = await message.channel.fetch_message(message.reference.message_id)
                if ref_msg.author.bot and '🎩' in ref_msg.content:
                    # This is a reply to Ralph's questions - relay it
                    await self._relay_to_swarm(message, from_reply=True)
                    return
            except:
                pass

        # Also check if message is in a channel where we sent notifications
        # (user might be responding without using reply feature)
        await self._check_and_relay_any_channel(message)

    async def _handle_thread_feedback(self, message: discord.Message):
        """Processa feedback em threads de review RAG"""
        if not HAS_RAG or not isinstance(message.channel, discord.Thread):
            return False

        thread = message.channel
        if not thread.name.startswith("📝 Feedback"):
            return False

        # Ignora bots
        if message.author.bot:
            return False

        try:
            # Busca mensagem original (parent)
            parent = thread.parent
            async for msg in parent.history(limit=20):
                if msg.author.bot and len(msg.embeds) > 0:
                    embed = msg.embeds[0]

                    # Extrai info do embed
                    task_type = "general"
                    project = "default"
                    task_desc = ""
                    output = ""
                    agent_name = ""

                    for field in embed.fields:
                        if field.name == "📋 Tipo":
                            task_type = field.value
                        elif field.name == "📁 Projeto":
                            project = field.value
                        elif field.name == "🤖 Agent":
                            agent_name = field.value
                        elif field.name == "📤 Output":
                            output = field.value.replace("```\n", "").replace("\n```", "")

                    if embed.description:
                        task_desc = embed.description.replace("**Task:** ", "")

                    # Pede correção
                    await thread.send(
                        "Obrigado pelo feedback! Agora, por favor, forneça **como deveria ser feito** (a versão correta).\n"
                        "Ou confirme se o feedback acima já é suficiente."
                    )

                    # Salva como erro
                    entry_id = rag_memory.save_mistake(
                        task_type=task_type,
                        project=project,
                        task=task_desc,
                        rejected_output=output,
                        feedback=message.content,
                        correction="Aguardando versão correta...",
                        rejected_by=str(message.author),
                        tags=[task_type, project, agent_name, "rejected"],
                        agent_slug=agent_name
                    )

                    # Atualiza mensagem original
                    embed.color = discord.Color.red()
                    embed.add_field(
                        name="❌ Reprovado",
                        value=f"Por: {message.author.mention}\nID: `{entry_id}`",
                        inline=False
                    )
                    await msg.edit(embed=embed)

                    await thread.send(f"✅ Erro registrado! ID: `{entry_id}`")
                    return True

        except Exception as e:
            print(f"Erro ao processar thread feedback: {e}")

        return False

    async def _handle_command(self, message: discord.Message):
        """Handle !ralph commands"""
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
        elif command == "channels":
            await self._cmd_channels(message)
        elif command == "project":
            # Check for subcommand
            if len(parts) > 1 and parts[1] == "update":
                await self._cmd_project_update(message, parts[2:])
            else:
                await self._cmd_project(message)

        # 🆕 Comandos RAG
        elif command == "rag":
            if not HAS_RAG:
                await message.reply("❌ RAG não está disponível")
                return

            subcommand = parts[1] if len(parts) > 1 else "status"
            if subcommand == "status":
                await self._cmd_rag_status(message)
            elif subcommand == "examples":
                task_type = parts[2] if len(parts) > 2 else "analysis"
                await self._cmd_rag_examples(message, task_type)
            else:
                await message.reply("❓ Subcomando RAG desconhecido. Use: `!ralph rag status` ou `!ralph rag examples [tipo]`")

        else:
            await message.reply("❓ Comando desconhecido. Use `!ralph help` para ver os disponíveis.")

    async def _cmd_help(self, message: discord.Message):
        """Show help message"""
        embed = discord.Embed(
            title="🐝 Ralph Swarm - Comandos",
            description="Sistema multi-agente de coordenação",
            color=0x7289DA
        )
        embed.add_field(
            name="Comandos Gerais",
            value=(
                "`!ralph help` - Mostra esta ajuda\n"
                "`!ralph status` - Status do swarm\n"
                "`!ralph agents` - Lista agentes disponíveis\n"
                "`!ralph channels` - Lista canais do swarm"
            ),
            inline=False
        )
        embed.add_field(
            name="Gestão de Tarefas",
            value=(
                "`!ralph task <descrição>` - Cria nova tarefa\n"
                "`!ralph project` - Mostra contexto do projeto atual\n"
                "`!ralph project update <campo> <valor>` - Atualiza projeto\n"
                "Ex: `!ralph task Pesquisar concorrentes`\n"
                "Ex: `!ralph project update stack Python + Node`"
            ),
            inline=False
        )
        embed.add_field(
            name="Agentes",
            value="🎩 Ralph (Coordenador) | 🔍 Scout (Pesquisa) | 🛠️ Max (Build)\n"
                  "📝 Maya (Criação) | 📊 Tracker (Analytics) | 👁️ Watcher (Monitor)",
            inline=False
        )

        # 🆕 Comandos RAG no help
        if HAS_RAG:
            embed.add_field(
                name="🧠 RAG - Memória Compartilhada",
                value="`!ralph rag status` - Estatísticas da memória\n"
                      "`!ralph rag examples [tipo]` - Exemplos por tipo (analysis, code, content)",
                inline=False
            )

        await message.reply(embed=embed)

    async def _cmd_status(self, message: discord.Message):
        """Show swarm status"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Get counts
            cursor.execute("SELECT COUNT(*) FROM swarm_agents")
            agent_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM swarm_tasks")
            task_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM swarm_tasks WHERE status = 'pending'")
            pending_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM swarm_channels")
            channel_count = cursor.fetchone()[0]

            conn.close()

            embed = discord.Embed(
                title="🐝 Ralph Swarm - Status",
                color=0x00FF00
            )
            embed.add_field(name="Agentes", value=str(agent_count), inline=True)
            embed.add_field(name="Canais", value=str(channel_count), inline=True)
            embed.add_field(name="Tarefas Totais", value=str(task_count), inline=True)
            embed.add_field(name="Tarefas Pendentes", value=str(pending_count), inline=True)
            embed.set_footer(text="Dashboard: http://100.94.223.52:3003/swarm")

            await message.reply(embed=embed)

        except Exception as e:
            await message.reply(f"❌ Erro ao consultar status: {e}")

    async def _cmd_agents(self, message: discord.Message):
        """List available agents"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT name, role, model_tier FROM swarm_agents ORDER BY id")
            agents = cursor.fetchall()
            conn.close()

            embed = discord.Embed(
                title="🤖 Agentes Disponíveis",
                color=0xFFA500
            )

            emojis = {"ralph": "🎩", "scout": "🔍", "max": "🛠️", "maya": "📝", "tracker": "📊", "watcher": "👁️"}

            for name, role, tier in agents:
                emoji = emojis.get(name.lower(), "🤖")
                tier_emoji = "$" * (3 if tier == "expensive" else 2 if tier == "medium" else 1)
                embed.add_field(
                    name=f"{emoji} {name.title()}",
                    value=f"{role}\n{tier_emoji}",
                    inline=True
                )

            await message.reply(embed=embed)

        except Exception as e:
            await message.reply(f"❌ Erro: {e}")

    async def _cmd_channels(self, message: discord.Message):
        """List swarm channels"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT name, description FROM swarm_channels ORDER BY name")
            channels = cursor.fetchall()
            conn.close()

            embed = discord.Embed(
                title="📡 Canais do Swarm",
                color=0x7289DA
            )

            for name, desc in channels[:20]:  # Limit to 20
                embed.add_field(name=f"#{name}", value=desc or "Sem descrição", inline=False)

            if len(channels) > 20:
                embed.set_footer(text=f"...e mais {len(channels) - 20} canais")

            await message.reply(embed=embed)

        except Exception as e:
            await message.reply(f"❌ Erro: {e}")

    # 🆕 Comandos RAG
    async def _cmd_rag_status(self, message: discord.Message):
        """Mostra estatísticas do RAG"""
        if not HAS_RAG:
            await message.reply("❌ RAG não está disponível")
            return

        stats = rag_memory.get_stats()

        embed = discord.Embed(
            title="🧠 Swarm RAG - Estatísticas",
            color=0x9B59B6
        )
        embed.add_field(name="✅ Exemplos Aprovados", value=str(stats['examples']), inline=True)
        embed.add_field(name="❌ Erros Aprendidos", value=str(stats['mistakes']), inline=True)
        embed.add_field(name="⭐ Qualidade Média", value=f"{stats['avg_quality']}/5", inline=True)

        if stats['by_task_type']:
            types_text = "\n".join([f"• {k}: {v}" for k, v in list(stats['by_task_type'].items())[:5]])
            embed.add_field(name="📊 Por Tipo", value=types_text, inline=False)

        await message.reply(embed=embed)

    async def _cmd_rag_examples(self, message: discord.Message, task_type: str):
        """Mostra exemplos recentes por tipo"""
        if not HAS_RAG:
            await message.reply("❌ RAG não está disponível")
            return

        examples = rag_memory.search_examples(task_type, "", "", limit=5)

        if not examples:
            await message.reply(f"📭 Nenhum exemplo de `{task_type}` ainda.")
            return

        embed = discord.Embed(
            title=f"📚 Exemplos Recentes - {task_type}",
            color=0x2ECC71
        )

        for i, ex in enumerate(examples, 1):
            embed.add_field(
                name=f"{i}. {ex['task'][:50]}...",
                value=f"⭐ {ex['quality_score']}/5 | 👤 {ex['approved_by'][:20]}",
                inline=False
            )

        await message.reply(embed=embed)

    # 🆕 Método para enviar task para review (chamado pelo sistema)
    async def send_task_for_review(self, channel_id: int, task_id: str, agent_name: str,
                                    project: str, task_type: str, task_desc: str, output: str):
        """
        Envia output de uma task para review no Discord.
        Chamado quando uma task é completada.
        """
        try:
            channel = self.get_channel(channel_id)
            if not channel:
                print(f"❌ Canal {channel_id} não encontrado para review")
                return

            # Cria embed
            embed = discord.Embed(
                title=f"🤖 {agent_name} - Output para Review",
                description=f"**Task:** {task_desc[:150]}{'...' if len(task_desc) > 150 else ''}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )

            embed.add_field(name="📁 Projeto", value=project, inline=True)
            embed.add_field(name="📋 Tipo", value=task_type, inline=True)
            embed.add_field(name="🆔 Task ID", value=task_id, inline=True)

            # Output truncado
            output_display = output[:800] + "..." if len(output) > 800 else output
            embed.add_field(
                name="📤 Output",
                value=f"```\n{output_display}\n```",
                inline=False
            )

            # Cria view com botões
            view = RAGReviewView(
                task_id=task_id,
                task_type=task_type,
                project=project,
                task_desc=task_desc,
                output=output,
                agent_name=agent_name
            )

            await channel.send(embed=embed, view=view)
            print(f"📤 Task {task_id} enviada para review em #{channel.name}")

        except Exception as e:
            print(f"❌ Erro ao enviar para review: {e}")

    async def _cmd_project(self, message: discord.Message):
        """Show project brief for current channel"""
        project = self.get_project_context(message)
        brief = self.load_project_brief(project)

        if brief:
            embed = discord.Embed(
                title=f"📚 Projeto: {project.title()}",
                description=brief[:2000] + ("..." if len(brief) > 2000 else ""),
                color=0x7289DA
            )
            embed.set_footer(text=f"Contexto carregado de projects/{project}/PROJECT.md")
            await message.reply(embed=embed)
        else:
            await message.reply(
                f"📭 Nenhum PROJECT.md encontrado para o projeto **{project}**.\n\n"
                f"Crie o arquivo em `swarm/projects/{project}/PROJECT.md` para adicionar contexto."
            )

    async def _cmd_task(self, message: discord.Message, args: list):
        """Create a new task with project context"""
        if not args:
            await message.reply("❌ Uso: `!ralph task <descrição da tarefa>`")
            return

        task_description = " ".join(args)
        project = self.get_project_context(message)

        try:
            # Use task manager directly
            from ralph_swarm_core import SwarmTaskManager

            tasks = SwarmTaskManager()

            # Load project brief
            project_brief = self.load_project_brief(project)

            # Build task with project context
            full_request = f"[{project.upper()}] {task_description}"
            if project_brief:
                full_request += f"\n\n[CONTEXT DO PROJETO]:\n{project_brief[:1500]}..."  # Limit to avoid token explosion

            # Create task with project context
            task = tasks.create_task(
                original_request=full_request,
                coordinator_agent_slug='ralph',
                project=project,
                source='discord',
                channel_id=message.channel.id
            )

            # Hybrid: reply in same channel, or in output channel if exists
            output_channel = await self.get_output_channel(message.guild)
            target_channel = output_channel if output_channel else message.channel

            embed = discord.Embed(
                title="✅ Tarefa Criada",
                description=f"**Projeto:** {project}\n**Descrição:** {task_description}",
                color=0x00FF00
            )
            embed.add_field(name="Task ID", value=f"`{task.task_code}`", inline=True)
            embed.add_field(name="Solicitante", value=message.author.mention, inline=True)

            if project_brief:
                embed.add_field(name="📚 Contexto", value="Brief do projeto carregado", inline=False)

            embed.set_footer(text="🎩 Ralph vai analisar e fazer perguntas para refinar a task")

            await target_channel.send(embed=embed)

            # React to original message
            await message.add_reaction("✅")

        except Exception as e:
            await message.reply(f"❌ Erro ao criar tarefa: {e}")

    async def _relay_to_swarm(self, message: discord.Message, from_reply: bool = False):
        """Relay Discord message to swarm database with project context"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Get project context
            project = self.get_project_context(message)

            # v4.0: Use discord_channel_id for consistency with notifications
            # This ensures responses are saved to the same channel where questions were sent
            channel_name = f"discord-{message.channel.id}"
            cursor.execute("SELECT id FROM swarm_channels WHERE name = ?", (channel_name,))
            result = cursor.fetchone()

            if not result:
                # Create channel
                cursor.execute("""
                    INSERT INTO swarm_channels (channel_code, name, description, created_by)
                    VALUES (?, ?, ?, ?)
                """, (channel_name, channel_name, f"Discord bridge for channel: {message.channel.name} (project: {project})", "system"))
                conn.commit()
                channel_id = cursor.lastrowid
            else:
                channel_id = result[0]

            # Store message with project context
            cursor.execute("""
                INSERT INTO swarm_messages (channel_id, author_type, author_id, content, mentions)
                VALUES (?, ?, ?, ?, ?)
            """, (
                channel_id,
                "user",
                str(message.author),
                message.content,
                json.dumps({
                    "discord_message_id": message.id,
                    "discord_channel_id": message.channel.id,
                    "discord_author_id": message.author.id,
                    "project": project,
                    "from_reply": from_reply
                })
            ))

            conn.commit()
            conn.close()

            # React to show received
            await message.add_reaction("🐝")

        except Exception as e:
            print(f"Error relaying to swarm: {e}")

    async def _check_and_relay_any_channel(self, message: discord.Message):
        """Check if message should be relayed from any channel (v4.0 - for task responses)"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Check if this channel has pending questions from Ralph
            channel_name = f"discord-{message.channel.id}"
            cursor.execute("""
                SELECT id FROM swarm_channels
                WHERE name = ?
            """, (channel_name,))

            result = cursor.fetchone()
            conn.close()

            if result:
                # Channel exists in our system, relay the message
                await self._relay_to_swarm(message)

        except Exception as e:
            print(f"Error checking channel: {e}")

    async def _cmd_project_update(self, message: discord.Message, args: list):
        """Update project brief field"""
        if len(args) < 2:
            await message.reply(
                "❌ Uso: `!ralph project update <campo> <valor>`\n\n"
                "Campos disponíveis:\n"
                "• `visao` - Visão geral do projeto\n"
                "• `objetivo` - Objetivo principal\n"
                "• `stack` - Stack tecnológico\n"
                "• `status` - Status atual\n"
                "• `prioridade` - Prioridade do projeto\n"
                "• `tom` - Tom de voz do projeto\n"
                "• `dos` - O que fazer (DOs)\n"
                "• `donts` - O que NÃO fazer (DON'Ts)\n\n"
                "Exemplo: `!ralph project update stack Python + Node.js`"
            )
            return

        field = args[0].lower()
        value = " ".join(args[1:])
        project = self.get_project_context(message)

        # Map field names to markdown sections
        field_map = {
            "visao": "Visão Geral",
            "objetivo": "Objetivo principal",
            "stack": "Stack Tecnológico",
            "status": "Status",
            "prioridade": "Prioridade",
            "tom": "Tom de Voz",
            "dos": "DOs",
            "donts": "DON'Ts"
        }

        if field not in field_map:
            await message.reply(
                f"❌ Campo `{field}` não reconhecido.\n"
                f"Campos disponíveis: visao, objetivo, stack, status, prioridade, tom, dos, donts"
            )
            return

        try:
            # Load existing file
            project_dir = os.path.join(os.path.dirname(__file__), 'projects', project)
            project_file = os.path.join(project_dir, 'PROJECT.md')

            if not os.path.exists(project_file):
                # Create new file
                os.makedirs(project_dir, exist_ok=True)
                content = f"# 🌀 Projeto {project.title()}\n\n## {field_map[field]}\n{value}\n"
            else:
                # Read existing and update
                with open(project_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check if section exists
                section_header = f"## {field_map[field]}"
                if section_header in content:
                    # Replace existing section content
                    import re
                    pattern = f"({re.escape(section_header)}\\n).*?(?=\\n## |\\Z)"
                    content = re.sub(pattern, f"\\1{value}\\n", content, flags=re.DOTALL)
                else:
                    # Add new section
                    content += f"\n## {field_map[field]}\n{value}\n"

            # Write updated content
            with open(project_file, 'w', encoding='utf-8') as f:
                f.write(content)

            await message.reply(f"✅ Projeto **{project}** atualizado!\n📋 Campo `{field}` definido como:\n```{value}```")

        except Exception as e:
            await message.reply(f"❌ Erro ao atualizar projeto: {e}")

    async def _handle_approval(self, message: discord.Message) -> bool:
        """Handle task approval messages (user says 'aprovado')"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Find tasks awaiting approval in this channel
            cursor.execute("""
                SELECT task_code, original_request
                FROM swarm_tasks
                WHERE status = 'awaiting_approval'
                AND metadata LIKE ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (f'%"discord_channel_id": {message.channel.id}%',))

            result = cursor.fetchone()
            conn.close()

            if not result:
                return False  # No task awaiting approval

            task_code, original_request = result

            # Approve the task
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE swarm_tasks
                SET status = 'approved', awaiting_approval = 0
                WHERE task_code = ?
            """, (task_code,))
            conn.commit()
            conn.close()

            # Confirm to user
            embed = discord.Embed(
                title="✅ Task Aprovada!",
                description=f"**{task_code}**\n\n{original_request[:100]}...",
                color=0x00FF00
            )
            embed.set_footer(text="Ralph vai iniciar a execução em breve...")
            await message.reply(embed=embed)

            logger.info(f"✅ Task {task_code} aprovada por {message.author}")
            return True

        except Exception as e:
            logger.error(f"Error handling approval: {e}")
            return False

    async def send_to_discord(self, channel_id: int, content: str, embed: Optional[discord.Embed] = None):
        """Send message from swarm to Discord"""
        channel = self.get_channel(channel_id)
        if channel:
            if embed:
                await channel.send(content, embed=embed)
            else:
                await channel.send(content)

def run_bridge():
    """Run the Discord bridge"""
    bridge = SwarmDiscordBridge()
    bridge.run(DISCORD_TOKEN)

if __name__ == "__main__":
    run_bridge()
