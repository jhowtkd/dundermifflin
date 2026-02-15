# Forum handlers completo com integração execution_plans
import discord
import sqlite3
import json
import uuid
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from pathlib import Path
import logging
import sys

logger = logging.getLogger('ralph_forum')

FORUM_CHANNEL_IDS = []  # Deixe vazio para aceitar QUALQUER fórum automaticamente
DB_PATH = Path(__file__).parent.parent / "dunder_mifflin.db"

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

try:
    from coordination_engine import SwarmCoordinator
    HAS_COORDINATION = True
except ImportError:
    HAS_COORDINATION = False
    logger.warning("Coordination engine não disponível")


class ForumTaskManager:
    """Gerencia tasks do fórum integrado com execution_plans"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_tables()
    
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_tables(self):
        migration_path = Path(__file__).parent.parent / "migrations" / "001_forum_integration.sql"
        if migration_path.exists():
            with open(migration_path) as f:
                conn = self._get_connection()
                conn.executescript(f.read())
                conn.commit()
                conn.close()
    
    def generate_code(self, prefix: str = "FORUM") -> str:
        timestamp = int(datetime.now().timestamp())
        unique_id = uuid.uuid4().hex[:8]
        return f"{prefix}-{timestamp}-{unique_id}"
    
    def create_task(self, thread_id: str, channel_id: str, guild_id: str, 
                    starter_message_id: str, title: str) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        task_code = self.generate_code("TASK")
        
        cursor.execute("""
            INSERT INTO forum_tasks (task_code, discord_thread_id, discord_channel_id, 
                                     discord_guild_id, starter_message_id, title, status)
            VALUES (?, ?, ?, ?, ?, ?, 'draft')
            ON CONFLICT(discord_thread_id) DO UPDATE SET
                title = excluded.title,
                updated_at = CURRENT_TIMESTAMP
        """, (task_code, str(thread_id), str(channel_id), str(guild_id), 
              str(starter_message_id), title))
        conn.commit()
        task_id = cursor.lastrowid
        conn.close()
        return task_id
    
    def update_task_content(self, task_id: int, raw_content: str, 
                           context_json: List[Dict], attachments_json: List[Dict] = None):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE forum_tasks 
            SET raw_content = ?, context_json = ?, attachments_json = ?,
                status = 'pending_approval', triggered_by = 'mention',
                triggered_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (raw_content, json.dumps(context_json), 
              json.dumps(attachments_json or []), task_id))
        conn.commit()
        conn.close()
    
    def create_execution_plan(self, task_id: int, title: str, objective: str, 
                             strategy: str, steps: List[Dict], 
                             estimated_minutes: int = 60) -> Dict:
        """Cria execution_plan e vincula à task do fórum"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        plan_code = self.generate_code("PLAN")
        
        # Cria execution_plan
        cursor.execute("""
            INSERT INTO execution_plans 
            (plan_code, service_id, title, objective, strategy, planned_steps, 
             estimated_duration_minutes, status, created_at)
            VALUES (?, NULL, ?, ?, ?, ?, ?, 'pending_approval', CURRENT_TIMESTAMP)
        """, (plan_code, title, objective, strategy, 
              json.dumps(steps, ensure_ascii=False), estimated_minutes))
        plan_id = cursor.lastrowid
        
        # Vincula à task
        cursor.execute("""
            UPDATE forum_tasks SET execution_plan_id = ?, status = 'pending_approval'
            WHERE id = ?
        """, (plan_id, task_id))
        
        # Cria referência Discord
        cursor.execute("""
            INSERT INTO forum_plan_discord_refs 
            (execution_plan_id, forum_task_id, approval_status)
            VALUES (?, ?, 'pending')
        """, (plan_id, task_id))
        
        conn.commit()
        conn.close()
        
        return {'id': plan_id, 'plan_code': plan_code, 'title': title,
                'objective': objective, 'strategy': strategy, 'steps': steps,
                'estimated_duration_minutes': estimated_minutes}
    
    def link_discord_message(self, plan_id: int, discord_message_id: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE forum_plan_discord_refs
            SET discord_plan_message_id = ?
            WHERE execution_plan_id = ?
        """, (str(discord_message_id), plan_id))
        conn.commit()
        conn.close()
    
    def update_approval_status(self, execution_plan_id: int, status: str,
                               response_type: str = None, response_content: str = None):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE forum_plan_discord_refs
            SET approval_status = ?, response_type = ?, response_content = ?,
                responded_at = CURRENT_TIMESTAMP
            WHERE execution_plan_id = ?
        """, (status, response_type, response_content, execution_plan_id))
        
        cursor.execute("""
            UPDATE execution_plans SET status = ? WHERE id = ?
        """, (status, execution_plan_id))
        
        cursor.execute("""
            SELECT forum_task_id FROM forum_plan_discord_refs WHERE execution_plan_id = ?
        """, (execution_plan_id,))
        row = cursor.fetchone()
        
        if row:
            task_status = 'approved' if status == 'approved' else 'cancelled' if status == 'rejected' else 'pending_approval'
            cursor.execute("""
                UPDATE forum_tasks SET status = ? WHERE id = ?
            """, (task_status, row[0]))
        
        conn.commit()
        conn.close()
    
    def create_mission(self, task_id: int, execution_plan_id: int, agent_id: int = 1) -> int:
        """Cria missão a partir do plano aprovado"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT plan_code, title, objective, planned_steps
            FROM execution_plans WHERE id = ?
        """, (execution_plan_id,))
        plan = cursor.fetchone()
        
        if not plan:
            conn.close()
            raise ValueError(f"Plano {execution_plan_id} não encontrado")
        
        mission_code = self.generate_code("MSN")
        
        cursor.execute("""
            INSERT INTO missions (mission_code, agent_id, title, description, 
                                  mission_type, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'approved', CURRENT_TIMESTAMP)
        """, (mission_code, agent_id, plan['title'], 
              f"{plan['objective']}\n\nPlano: {plan['plan_code']}", 'forum_task'))
        
        mission_id = cursor.lastrowid
        
        # Cria steps
        steps = json.loads(plan['planned_steps'])
        for i, step in enumerate(steps, 1):
            step_code = f"{mission_code}-S{i:03d}"
            cursor.execute("""
                INSERT INTO steps (mission_id, step_number, step_code, title, 
                                   description, status)
                VALUES (?, ?, ?, ?, ?, 'queued')
            """, (mission_id, i, step_code, step.get('title', f'Step {i}'), 
                  step.get('description', '')))
        
        cursor.execute("""
            UPDATE forum_tasks SET mission_id = ?, status = 'executing' WHERE id = ?
        """, (mission_id, task_id))
        
        conn.commit()
        conn.close()
        return mission_id
    
    def get_task_by_thread(self, thread_id: str) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM forum_tasks WHERE discord_thread_id = ?", (str(thread_id),))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_plan_by_discord_message(self, message_id: str) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT fpr.*, ft.discord_thread_id, ft.title
            FROM forum_plan_discord_refs fpr
            JOIN forum_tasks ft ON ft.id = fpr.forum_task_id
            WHERE fpr.discord_plan_message_id = ?
        """, (str(message_id),))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_execution_plan(self, plan_id: int) -> Optional[Dict]:
        """Busca dados do execution_plan pelo ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM execution_plans WHERE id = ?
        """, (plan_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_mission_steps(self, mission_id: int) -> List[Dict]:
        """Busca steps da missão"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM steps WHERE mission_id = ? ORDER BY step_number
        """, (mission_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def complete_step(self, step_id: int, output: str = None):
        """Marca step como completado"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE steps 
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP, output_data = ?
            WHERE id = ?
        """, (json.dumps({'output': output}) if output else None, step_id))
        conn.commit()
        conn.close()
    
    def complete_mission(self, mission_id: int, result: str = None):
        """Marca missão como completada"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE missions 
            SET status = 'succeeded', completed_at = CURRENT_TIMESTAMP, result = ?
            WHERE id = ?
        """, (json.dumps({'result': result}) if result else None, mission_id))
        conn.commit()
        conn.close()
    
    def complete_task(self, task_id: int, result: str = None):
        """Marca task como completada"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE forum_tasks 
            SET status = 'completed'
            WHERE id = ?
        """, (task_id,))
        conn.commit()
        conn.close()
        logger.info(f"✅ Task {task_id} completada")

class PlanGenerator:
    """Gera planos de execução"""
    
    def __init__(self):
        self.coordinator = SwarmCoordinator() if HAS_COORDINATION else None
    
    def generate_plan(self, task_description: str, context: str = "") -> Dict:
        if not self.coordinator:
            return self._generate_simple_plan(task_description)
        
        try:
            analysis = self.coordinator.analyze_task(task_description)
            
            # Se for um objeto ExecutionPlan (dataclass), converte para dict
            if hasattr(analysis, 'to_dict'):
                analysis = analysis.to_dict()
            elif hasattr(analysis, '__dict__'):
                analysis = analysis.__dict__
            
            # Garante que é um dict
            if not isinstance(analysis, dict):
                logger.warning(f"analysis não é dict, é {type(analysis)}. Usando plano simples.")
                return self._generate_simple_plan(task_description)
            
            steps = []
            agents_required = analysis.get('agents_required', ['ralph'])
            if hasattr(agents_required, '__iter__') and not isinstance(agents_required, str):
                agents_list = list(agents_required)
            else:
                agents_list = ['ralph']
            
            for agent_slug in agents_list:
                agent_info = self._get_agent_info(agent_slug)
                steps.append({
                    'agent': agent_slug,
                    'title': f"Executar como {agent_info.get('name', agent_slug)}",
                    'description': agent_info.get('role', 'Executar tarefa'),
                    'estimated_minutes': 15
                })
            
            return {
                'complexity': analysis.get('complexity', 'medium'),
                'needs_swarm': analysis.get('needs_swarm', True),
                'agents_required': agents_list,
                'execution_strategy': analysis.get('execution_strategy', 'Execução sequencial'),
                'estimated_steps': len(steps),
                'steps': steps,
                'estimated_duration_minutes': len(steps) * 15
            }
        except Exception as e:
            logger.error(f"Erro ao gerar plano com coordinator: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._generate_simple_plan(task_description)
    
    def _generate_simple_plan(self, task_description: str) -> Dict:
        return {
            'complexity': 'medium',
            'needs_swarm': True,
            'agents_required': ['scout', 'max', 'maya'],
            'execution_strategy': 'Execução sequencial',
            'estimated_steps': 3,
            'steps': [
                {'agent': 'scout', 'title': 'Análise e Research', 
                 'description': 'Analisar requisitos', 'estimated_minutes': 15},
                {'agent': 'max', 'title': 'Execução Principal',
                 'description': 'Implementar solução', 'estimated_minutes': 30},
                {'agent': 'maya', 'title': 'Review',
                 'description': 'Revisar resultado', 'estimated_minutes': 15}
            ],
            'estimated_duration_minutes': 60
        }
    
    def _get_agent_info(self, agent_slug: str) -> Dict:
        agents = {
            'scout': {'name': 'Scout', 'role': 'Research'},
            'max': {'name': 'Max', 'role': 'Desenvolvimento'},
            'maya': {'name': 'Maya', 'role': 'Copywriting'},
            'ralph': {'name': 'Ralph', 'role': 'Coordenação'}
        }
        return agents.get(agent_slug, {'name': agent_slug, 'role': 'Agente'})


class ForumHandlers:
    """Handlers de eventos do Discord para fóruns"""
    
    def __init__(self, bot: discord.Client, db_path: Path = None):
        self.bot = bot
        self.db = ForumTaskManager(db_path or DB_PATH)
        self.plan_generator = PlanGenerator()
        self.forum_channel_ids = set(FORUM_CHANNEL_IDS)
    
    async def on_thread_create(self, thread: discord.Thread):
        if self.forum_channel_ids and thread.parent_id not in self.forum_channel_ids:
            return
        logger.info(f"Novo thread: {thread.name}")
        self.db.create_task(
            thread_id=thread.id, channel_id=thread.parent_id,
            guild_id=thread.guild.id if thread.guild else None,
            starter_message_id=thread.id, title=thread.name
        )
    
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if not isinstance(message.channel, discord.Thread):
            return
        if self.forum_channel_ids and message.channel.parent_id not in self.forum_channel_ids:
            return
        if self.bot.user not in message.mentions:
            return
        
        logger.info(f"Menção em: {message.channel.name}")
        
        # Reação de processamento
        await message.add_reaction('⏳')
        
        # Busca ou cria task
        task = self.db.get_task_by_thread(str(message.channel.id))
        if not task:
            task_id = self.db.create_task(
                thread_id=message.channel.id, channel_id=message.channel.parent_id,
                guild_id=message.channel.guild.id if message.channel.guild else None,
                starter_message_id=message.channel.id, title=message.channel.name
            )
            task = {'id': task_id}
        
        # Consolida conteúdo
        raw_content, context, attachments = await self._consolidate_thread(message.channel)
        self.db.update_task_content(task['id'], raw_content, context, attachments)
        
        try:
            # Gera plano
            logger.info(f"Gerando plano para task {task['id']}...")
            plan_data = self.plan_generator.generate_plan(raw_content)
            logger.info(f"Plano gerado: {plan_data.get('execution_strategy', 'N/A')}")
            
            # Cria execution_plan no banco
            logger.info(f"Criando execution_plan...")
            plan = self.db.create_execution_plan(
                task_id=task['id'],
                title=message.channel.name,
                objective=raw_content[:500],
                strategy=plan_data['execution_strategy'],
                steps=plan_data['steps'],
                estimated_minutes=plan_data['estimated_duration_minutes']
            )
            logger.info(f"Execution_plan criado: {plan['plan_code']}")
            
            # Cria embed do plano
            embed = discord.Embed(
                title=f"📋 Plano de Execução: {plan['plan_code']}",
                description=f"**Objetivo:** {plan['objective'][:300]}...",
                color=discord.Color.blue()
            )
            embed.add_field(name="Estratégia", value=plan['strategy'], inline=False)
            embed.add_field(name="Duração Estimada", 
                           value=f"{plan['estimated_duration_minutes']} minutos", inline=True)
            embed.add_field(name="Steps", value=str(len(plan['steps'])), inline=True)
            
            for i, step in enumerate(plan['steps'][:5], 1):
                embed.add_field(
                    name=f"{i}. {step['title']}",
                    value=f"{step['description'][:100]}..." if len(step['description']) > 100 else step['description'],
                    inline=False
                )
            
            embed.set_footer(text="Reaja com ✅ para aprovar | ❌ para rejeitar | 📝 para revisar")
            
            # Envia plano
            logger.info(f"Enviando embed para Discord...")
            plan_message = await message.reply(embed=embed)
            logger.info(f"Embed enviado, message_id: {plan_message.id}")
            
            # Vincula mensagem do Discord ao plano
            self.db.link_discord_message(plan['id'], str(plan_message.id))
            
            # Adiciona reações
            await plan_message.add_reaction('✅')
            await plan_message.add_reaction('❌')
            await plan_message.add_reaction('📝')
            
            # Remove reação de processamento
            await message.remove_reaction('⏳', self.bot.user)
            await message.add_reaction('✅')
            
            logger.info(f"Plano {plan['plan_code']} criado e enviado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar/enviar plano: {e}")
            import traceback
            logger.error(traceback.format_exc())
            await message.channel.send(f"❌ Erro ao gerar plano: {str(e)}")
    
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return
        
        plan = self.db.get_plan_by_discord_message(str(payload.message_id))
        if not plan:
            return
        
        emoji = str(payload.emoji)
        channel = self.bot.get_channel(payload.channel_id)
        
        if emoji == '✅':
            self.db.update_approval_status(plan['execution_plan_id'], 'approved', 'reaction', '✅')
            
            if channel:
                await channel.send("✅ **Plano aprovado!** Iniciando execução...")
            
            # Cria missão
            try:
                mission_id = self.db.create_mission(plan['forum_task_id'], plan['execution_plan_id'])
                if channel:
                    await channel.send(f"🚀 Missão criada! ID: {mission_id}")
                    
                    # Inicia execução e posta updates no Discord
                    await self._execute_mission_with_updates(
                        mission_id=mission_id,
                        plan_id=plan['execution_plan_id'],
                        channel=channel,
                        forum_task_id=plan['forum_task_id']
                    )
            except Exception as e:
                logger.error(f"Erro criando missão: {e}")
                if channel:
                    await channel.send(f"❌ Erro ao criar missão: {e}")
                    
        elif emoji == '❌':
            self.db.update_approval_status(plan['execution_plan_id'], 'rejected', 'reaction', '❌')
            if channel:
                await channel.send("❌ **Plano rejeitado.** Task cancelada.")
                
        elif emoji == '📝':
            self.db.update_approval_status(plan['execution_plan_id'], 'pending', 'reaction', '📝')
            if channel:
                await channel.send("📝 **Revisão solicitada.** Responda com ajustes e mencione @Ralph.")
    
    async def _execute_mission_with_updates(self, mission_id: int, plan_id: int, 
                                            channel: discord.TextChannel, forum_task_id: int):
        """Executa missão com agentes reais e posta updates no Discord"""
        import asyncio
        
        # Posta início
        start_msg = await channel.send("⏳ **Iniciando execução com agentes...**")
        
        try:
            # Busca dados da missão e plano
            steps = self.db.get_mission_steps(mission_id)
            plan = self.db.get_execution_plan(plan_id)
            total_steps = len(steps)
            
            if not steps:
                await channel.send("❌ Nenhum step encontrado para esta missão.")
                return
            
            # Resultados acumulados
            step_results = []
            
            for i, step in enumerate(steps, 1):
                agent_slug = step.get('agent_slug', 'ralph')
                step_title = step.get('title', f'Step {i}')
                
                # Atualiza status
                await start_msg.edit(content=f"⏳ **Executando Step {i}/{total_steps}:** {step_title} (@{agent_slug})")
                
                # Prepara o prompt para o agente
                context = f"""Missão: {plan.get('title', 'Task')}
Objetivo: {plan.get('objective', 'N/A')}

Step atual ({i}/{total_steps}): {step_title}

Contexto acumulado das etapas anteriores:
{chr(10).join(step_results) if step_results else 'Nenhum contexto anterior.'}

Execute esta tarefa de forma completa e entregue um resultado concreto."""
                
                # Executa o agente via AgentBrain
                try:
                    from agent_brain import AgentBrain
                    brain = AgentBrain(agent_slug, use_real_llm=True)
                    result = brain.think(context)
                    
                    # Salva resultado do step
                    self.db.complete_step(step['id'], result)
                    step_results.append(f"[Step {i} - @{agent_slug}]: {result[:200]}...")
                    
                    # Posta resultado no Discord (resumido)
                    result_preview = result[:500] + "..." if len(result) > 500 else result
                    await channel.send(
                        f"✅ **Step {i}/{total_steps} concluído:** {step_title}\n"
                        f"```\n{result_preview}\n```"
                    )
                    
                except Exception as agent_error:
                    error_msg = f"Erro no agente {agent_slug}: {str(agent_error)}"
                    logger.error(error_msg)
                    self.db.complete_step(step['id'], f"ERRO: {error_msg}")
                    await channel.send(f"❌ **Step {i}/{total_steps} falhou:** {error_msg}")
                    raise agent_error
            
            # Síntese final
            await start_msg.edit(content="🧠 **Gerando síntese final...**")
            
            try:
                from agent_brain import AgentBrain
                ralph = AgentBrain('ralph', use_real_llm=True)
                synthesis_prompt = f"""Sintetize os resultados desta missão em um resumo executivo:

Missão: {plan.get('title', 'Task')}

Resultados por step:
{chr(10).join(step_results)}

Forneça um resumo conciso do que foi entregue."""
                
                synthesis = ralph.think(synthesis_prompt)
            except Exception as e:
                synthesis = f"Missão concluída com {total_steps} steps executados."
                logger.warning(f"Erro na síntese: {e}")
            
            # Finaliza
            self.db.complete_mission(mission_id, synthesis)
            await channel.send(f"🎉 **Missão concluída!**\n\n{synthesis[:1000]}")
            
            # Atualiza task do fórum
            self.db.complete_task(forum_task_id, synthesis)
            
        except Exception as e:
            logger.error(f"Erro na execução: {e}")
            await channel.send(f"❌ **Erro durante execução:** {str(e)}")
            # Marca missão como falha
            try:
                self.db.complete_mission(mission_id, f"FALHA: {str(e)}")
            except:
                pass
    
    async def _consolidate_thread(self, thread: discord.Thread) -> Tuple[str, List[Dict], List[Dict]]:
        messages = []
        attachments = []
        context_parts = []
        
        async for msg in thread.history(limit=100, oldest_first=True):
            if msg.author.bot:
                continue
            
            msg_data = {
                'message_id': str(msg.id),
                'author_id': str(msg.author.id),
                'author_name': msg.author.name,
                'content': msg.content,
                'created_at': msg.created_at.isoformat() if msg.created_at else None
            }
            messages.append(msg_data)
            
            full_content = msg.content
            if msg.attachments:
                for att in msg.attachments:
                    att_data = {'filename': att.filename, 'url': att.url, 
                               'content_type': att.content_type, 'size': att.size}
                    attachments.append(att_data)
                    
                    if att.filename.endswith('.txt'):
                        try:
                            text_content = await att.read()
                            decoded = text_content.decode('utf-8')
                            full_content += f"\n\n[Anexo: {att.filename}]\n{decoded}"
                        except Exception as e:
                            logger.error(f"Erro lendo anexo: {e}")
            
            context_parts.append(f"[{msg.author.name}]: {full_content}")
        
        return "\n\n".join(context_parts), messages, attachments


def setup_forum_handlers(bot: discord.Client, db_path: Path = None):
    """Configura handlers de fórum no bot existente"""
    handlers = ForumHandlers(bot, db_path)
    bot.forum_handlers = handlers
    return handlers
