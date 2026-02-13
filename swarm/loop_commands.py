#!/usr/bin/env python3
"""
Ralph Loop Commands - Integração Discord
Fase 3: Comandos de loop para o Discord Bridge
"""

import discord
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional, List
from datetime import datetime

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'loops' / 'discord'))

# Imports do sistema de loops
try:
    from loop_manager import LoopManager, LoopStatus
    from iteration_engine import IterationEngine, EngineConfig
    from llm_client import LLMClient
    LOOPS_AVAILABLE = True
except ImportError as e:
    print(f"❌ Erro ao importar loops: {e}")
    LOOPS_AVAILABLE = False


class LoopCommands:
    """Handler de comandos de loop para Discord"""
    
    def __init__(self, bot_client):
        self.bot = bot_client
        self.loop_manager = LoopManager() if LOOPS_AVAILABLE else None
        self.engine = IterationEngine() if LOOPS_AVAILABLE else None
        self.active_loops = {}  # loop_code -> {message, channel}
    
    async def handle(self, message: discord.Message, parts: List[str]):
        """
        Handler principal de comandos de loop.
        
        Uso:
        !ralph loop <agente> "<tarefa>" [--max N]
        !ralph loop status <loop_code>
        !ralph loop pause <loop_code>
        !ralph loop resume <loop_code>
        !ralph loop stop <loop_code>
        !ralph loops
        !ralph loop history <loop_code>
        """
        if not LOOPS_AVAILABLE:
            await message.reply("❌ Sistema de loops não disponível.")
            return
        
        if len(parts) < 1:
            await self._cmd_help(message)
            return
        
        subcommand = parts[0].lower()
        
        if subcommand == "help":
            await self._cmd_help(message)
        elif subcommand in ["list", "ls"]:
            await self._cmd_list(message)
        elif subcommand == "status":
            if len(parts) < 2:
                await message.reply("❌ Código do loop obrigatório. Uso: `!ralph loop status <loop_code>`")
                return
            await self._cmd_status(message, parts[1])
        elif subcommand == "pause":
            if len(parts) < 2:
                await message.reply("❌ Código do loop obrigatório.")
                return
            await self._cmd_pause(message, parts[1])
        elif subcommand == "resume":
            if len(parts) < 2:
                await message.reply("❌ Código do loop obrigatório.")
                return
            await self._cmd_resume(message, parts[1])
        elif subcommand == "stop":
            if len(parts) < 2:
                await message.reply("❌ Código do loop obrigatório.")
                return
            await self._cmd_stop(message, parts[1])
        elif subcommand == "history":
            if len(parts) < 2:
                await message.reply("❌ Código do loop obrigatório.")
                return
            await self._cmd_history(message, parts[1])
        else:
            # Formato: !ralph loop <agente> "<tarefa>" [--max N]
            await self._cmd_start(message, parts)
    
    async def _cmd_help(self, message: discord.Message):
        """Mostra ajuda de comandos de loop"""
        embed = discord.Embed(
            title="🔄 Ralph Loop - Comandos",
            description="Sistema de iteração contínua para tarefas complexas",
            color=0x5865F2
        )
        
        embed.add_field(
            name="Iniciar Loop",
            value=(
                "`!ralph loop <agente> \"<tarefa>\" [--max N]`\n"
                "Ex: `!ralph loop dev \"Criar API JWT\" --max 20`"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Gerenciar Loops",
            value=(
                "`!ralph loops` - Lista loops ativos\n"
                "`!ralph loop status <code>` - Status de um loop\n"
                "`!ralph loop pause <code>` - Pausa loop\n"
                "`!ralph loop resume <code>` - Retoma loop\n"
                "`!ralph loop stop <code>` - Para loop\n"
                "`!ralph loop history <code>` - Histórico de iterações"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Agentes Disponíveis",
            value="`dev`, `ralf`, `max`, `maya`, `scout`, `watcher`, `tracker`",
            inline=False
        )
        
        embed.add_field(
            name="💡 Dica",
            value="Use `--max 30` para tarefas complexas (padrão: 20)",
            inline=False
        )
        
        await message.reply(embed=embed)
    
    async def _cmd_start(self, message: discord.Message, parts: List[str]):
        """Inicia um novo loop"""
        if len(parts) < 2:
            await message.reply("❌ Formato inválido. Use: `!ralph loop <agente> \"<tarefa>\"`")
            return
        
        agent_slug = parts[0]
        
        # Parse da tarefa e args
        task_parts = []
        max_iterations = 20
        
        i = 1
        while i < len(parts):
            part = parts[i]
            if part == "--max" and i + 1 < len(parts):
                try:
                    max_iterations = int(parts[i + 1])
                    i += 2
                    continue
                except ValueError:
                    pass
            task_parts.append(part)
            i += 1
        
        task_description = " ".join(task_parts).strip('"\'')
        
        if not task_description:
            await message.reply("❌ Descrição da tarefa obrigatória.")
            return
        
        # Validação de max_iterations
        if max_iterations < 1 or max_iterations > 100:
            await message.reply("❌ Max iterations deve ser entre 1 e 100.")
            return
        
        # Criar embed inicial
        embed = discord.Embed(
            title="🚀 Iniciando Loop",
            description=f"**Tarefa:** {task_description[:200]}{'...' if len(task_description) > 200 else ''}",
            color=0xFEE75C,
            timestamp=datetime.now()
        )
        embed.add_field(name="Agente", value=agent_slug, inline=True)
        embed.add_field(name="Max Iterações", value=str(max_iterations), inline=True)
        embed.add_field(name="Status", value="⏳ Criando...", inline=True)
        
        status_msg = await message.reply(embed=embed)
        
        try:
            # Criar loop no banco
            loop_code = self.loop_manager.create_loop(
                agent_slug=agent_slug,
                task_description=task_description,
                max_iterations=max_iterations,
                discord_channel_id=str(message.channel.id),
                discord_user_id=str(message.author.id),
                discord_guild_id=str(message.guild.id) if message.guild else None
            )
            
            # Atualizar embed
            embed.title = f"🔄 Loop Iniciado: `{loop_code}`"
            embed.color = 0x57F287
            embed.set_field_at(2, name="Status", value="▶️ Rodando", inline=True)
            embed.add_field(
                name="Progresso",
                value="Iteração 0/{}".format(max_iterations),
                inline=False
            )
            await status_msg.edit(embed=embed)
            
            # Armazenar referência
            self.active_loops[loop_code] = {
                'message': status_msg,
                'channel': message.channel
            }
            
            # Iniciar loop em background
            asyncio.create_task(
                self._run_loop(loop_code, status_msg, embed, max_iterations)
            )
            
        except ValueError as e:
            embed.title = "❌ Erro"
            embed.description = str(e)
            embed.color = 0xED4245
            await status_msg.edit(embed=embed)
        except Exception as e:
            embed.title = "❌ Erro Inesperado"
            embed.description = f"```{str(e)}```"
            embed.color = 0xED4245
            await status_msg.edit(embed=embed)
    
    async def _run_loop(self, loop_code: str, status_msg: discord.Message, 
                        embed: discord.Embed, max_iterations: int):
        """Executa o loop em background"""
        
        iteration_count = 0
        
        def on_progress(data):
            nonlocal iteration_count
            iteration_count = data['iteration']
            
            # Atualizar embed
            progress = f"Iteração {iteration_count}/{max_iterations}"
            if data['status'] == 'running':
                embed.set_field_at(2, name="Status", value="▶️ " + progress, inline=True)
            elif data['status'] == 'completed':
                embed.set_field_at(2, name="Status", value="✅ Completo", inline=True)
            elif data['status'] == 'error':
                embed.set_field_at(2, name="Status", value="❌ Erro", inline=True)
            
            # Atualizar campo de progresso
            if len(embed.fields) > 3:
                embed.set_field_at(3, name="Progresso", value=progress, inline=False)
            
            # Atualizar mensagem assíncrono
            asyncio.create_task(self._safe_edit(status_msg, embed))
        
        def on_complete(data):
            # Loop completado
            embed.title = f"✅ Loop Completo: `{loop_code}`"
            embed.color = 0x57F287
            embed.set_field_at(2, name="Status", value=f"✅ {data['status']}", inline=True)
            embed.set_field_at(3, name="Progresso", 
                             value=f"{data['iterations']}/{max_iterations} iterações", 
                             inline=False)
            
            # Adicionar resumo se houver
            if data.get('summary'):
                embed.add_field(name="Resumo", 
                              value=data['summary'][:500] + '...' if len(data['summary']) > 500 else data['summary'],
                              inline=False)
            
            asyncio.create_task(self._safe_edit(status_msg, embed))
            
            # Limpar referência
            if loop_code in self.active_loops:
                del self.active_loops[loop_code]
        
        def on_error(data):
            embed.title = f"❌ Loop Falhou: `{loop_code}`"
            embed.color = 0xED4245
            embed.set_field_at(2, name="Status", value="❌ Erro", inline=True)
            embed.add_field(name="Erro", value=str(data.get('error', 'Desconhecido'))[:500], inline=False)
            
            asyncio.create_task(self._safe_edit(status_msg, embed))
            
            if loop_code in self.active_loops:
                del self.active_loops[loop_code]
        
        try:
            # Executar loop
            self.engine.run_loop(
                loop_code=loop_code,
                on_progress=on_progress,
                on_complete=on_complete,
                on_error=on_error
            )
        except Exception as e:
            on_error({'error': str(e)})
    
    async def _safe_edit(self, message: discord.Message, embed: discord.Embed):
        """Edita mensagem de forma segura"""
        try:
            await message.edit(embed=embed)
        except Exception as e:
            print(f"Erro ao editar mensagem: {e}")
    
    async def _cmd_list(self, message: discord.Message):
        """Lista loops ativos"""
        loops = self.loop_manager.list_loops(limit=10)
        
        if not loops:
            await message.reply("📭 Nenhum loop encontrado.")
            return
        
        embed = discord.Embed(
            title="🔄 Loops Recentes",
            color=0x5865F2
        )
        
        for loop in loops:
            status_emoji = {
                'pending': '⏳',
                'running': '▶️',
                'paused': '⏸️',
                'completed': '✅',
                'failed': '❌',
                'incomplete': '⚠️'
            }.get(loop.status, '❓')
            
            value = f"{status_emoji} `{loop.status}` | {loop.current_iteration}/{loop.max_iterations} iters"
            embed.add_field(
                name=f"`{loop.loop_code}` | {loop.agent_slug}",
                value=value,
                inline=False
            )
        
        await message.reply(embed=embed)
    
    async def _cmd_status(self, message: discord.Message, loop_code: str):
        """Mostra status detalhado de um loop"""
        loop = self.loop_manager.get_loop(loop_code)
        
        if not loop:
            await message.reply(f"❌ Loop `{loop_code}` não encontrado.")
            return
        
        report = self.engine.get_loop_report(loop_code)
        
        embed = discord.Embed(
            title=f"📊 Status: `{loop_code}`",
            color=0x5865F2,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="Agente", value=loop.agent_slug, inline=True)
        embed.add_field(name="Status", value=loop.status, inline=True)
        embed.add_field(
            name="Iterações", 
            value=f"{loop.current_iteration}/{loop.max_iterations}", 
            inline=True
        )
        
        if report.get('cost'):
            embed.add_field(
                name="Custo Estimado", 
                value=f"${report['cost']['estimated_usd']}", 
                inline=True
            )
        
        if report.get('tokens'):
            embed.add_field(
                name="Tokens", 
                value=f"{report['tokens']['total']} total", 
                inline=True
            )
        
        if loop.result_summary:
            embed.add_field(
                name="Resumo",
                value=loop.result_summary[:500] + '...' if len(loop.result_summary) > 500 else loop.result_summary,
                inline=False
            )
        
        await message.reply(embed=embed)
    
    async def _cmd_pause(self, message: discord.Message, loop_code: str):
        """Pausa um loop"""
        loop = self.loop_manager.get_loop(loop_code)
        
        if not loop:
            await message.reply(f"❌ Loop `{loop_code}` não encontrado.")
            return
        
        if loop.status != 'running':
            await message.reply(f"⚠️ Loop `{loop_code}` não está rodando (status: {loop.status}).")
            return
        
        self.loop_manager.update_loop_status(loop_code, LoopStatus.PAUSED.value)
        await message.reply(f"⏸️ Loop `{loop_code}` pausado.")
    
    async def _cmd_resume(self, message: discord.Message, loop_code: str):
        """Retoma um loop pausado"""
        loop = self.loop_manager.get_loop(loop_code)
        
        if not loop:
            await message.reply(f"❌ Loop `{loop_code}` não encontrado.")
            return
        
        if loop.status != 'paused':
            await message.reply(f"⚠️ Loop `{loop_code}` não está pausado (status: {loop.status}).")
            return
        
        self.loop_manager.update_loop_status(loop_code, LoopStatus.RUNNING.value)
        await message.reply(f"▶️ Loop `{loop_code}` retomado.")
        
        # TODO: Implementar retomada real da execução
        # Por enquanto só atualiza o status no banco
    
    async def _cmd_stop(self, message: discord.Message, loop_code: str):
        """Para um loop"""
        loop = self.loop_manager.get_loop(loop_code)
        
        if not loop:
            await message.reply(f"❌ Loop `{loop_code}` não encontrado.")
            return
        
        if loop.status in ['completed', 'failed']:
            await message.reply(f"⚠️ Loop `{loop_code}` já finalizado.")
            return
        
        self.loop_manager.update_loop_status(
            loop_code, 
            LoopStatus.FAILED.value,
            "Parado pelo usuário"
        )
        await message.reply(f"🛑 Loop `{loop_code}` parado.")
    
    async def _cmd_history(self, message: discord.Message, loop_code: str):
        """Mostra histórico de iterações"""
        loop = self.loop_manager.get_loop(loop_code)
        
        if not loop:
            await message.reply(f"❌ Loop `{loop_code}` não encontrado.")
            return
        
        iterations = self.loop_manager.get_iterations(loop_code)
        
        if not iterations:
            await message.reply(f"📭 Nenhuma iteração registrada para `{loop_code}`.")
            return
        
        embed = discord.Embed(
            title=f"📜 Histórico: `{loop_code}`",
            description=f"Total: {len(iterations)} iterações",
            color=0x5865F2
        )
        
        # Mostrar últimas 5 iterações
        for it in iterations[-5:]:
            summary = it.response_summary or "Sem resumo"
            if len(summary) > 100:
                summary = summary[:97] + '...'
            
            embed.add_field(
                name=f"Iteração {it.iteration_number}",
                value=f"📝 {summary}\n"
                      f"💰 {it.tokens_in} in / {it.tokens_out} out | ⏱️ {it.duration_seconds}s",
                inline=False
            )
        
        await message.reply(embed=embed)


# Função para integração com o bridge existente
async def handle_loop_command(bot_client, message: discord.Message, parts: List[str]):
    """
    Função de entrada para o Discord Bridge.
    
    Args:
        bot_client: Instância do bot Discord
        message: Mensagem do Discord
        parts: Argumentos do comando (sem o 'loop')
    """
    handler = LoopCommands(bot_client)
    await handler.handle(message, parts)
