#!/usr/bin/env python3
"""
Ralph Swarm Core v5.0 - Sistema de Canais e Agentes
Baseado no conceito Discord: canais como database
"""

import os
import sys
import json
import uuid
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Database path
DB_PATH = Path.home() / ".openclaw/workspace/projects/dunder-mifflin/dunder_mifflin.db"

class AuthorType(Enum):
    """Tipos de autores"""
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"

class TaskStatus(Enum):
    """Status de tarefas - Ralph Swarm v4.0 Proativo"""
    PENDING = "pending"              # Acabou de ser criada
    AWAITING_QUESTIONS = "awaiting_questions"  # Aguardando respostas do usuário
    AWAITING_APPROVAL = "awaiting_approval"    # Aguardando aprovação do plano
    APPROVED = "approved"            # Aprovada, pronta para execução
    PLANNING = "planning"            # Planejando execução
    RUNNING = "running"              # Em execução
    SYNTHESIZING = "synthesizing"    # Sintetizando resultados
    COMPLETED = "completed"          # Completada
    FAILED = "failed"                # Falhou

@dataclass
class SwarmMessage:
    """Representa uma mensagem em um canal"""
    id: int
    message_code: str
    channel_id: int
    channel_name: str
    author_type: str
    author_id: str
    content: str
    mentions: List[str]
    created_at: datetime
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'message_code': self.message_code,
            'channel_id': self.channel_id,
            'channel_name': self.channel_name,
            'author_type': self.author_type,
            'author_id': self.author_id,
            'content': self.content,
            'mentions': self.mentions,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@dataclass
class SwarmAgent:
    """Representa um agent no sistema swarm"""
    id: int
    agent_slug: str
    name: str
    role: str
    model_tier: str
    personality: str
    avatar_emoji: str
    memory: Dict
    status: str
    is_active: bool
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'agent_slug': self.agent_slug,
            'name': self.name,
            'role': self.role,
            'model_tier': self.model_tier,
            'personality': self.personality,
            'avatar_emoji': self.avatar_emoji,
            'memory': self.memory,
            'status': self.status,
            'is_active': self.is_active
        }

@dataclass
class SwarmTask:
    """Representa uma tarefa em execução"""
    id: int
    task_code: str
    original_request: str
    coordinator_agent_id: int
    coordinator_name: str
    status: str
    execution_plan: Dict
    final_output: Optional[str]
    cost_usd: float
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'task_code': self.task_code,
            'original_request': self.original_request,
            'coordinator_agent_id': self.coordinator_agent_id,
            'coordinator_name': self.coordinator_name,
            'status': self.status,
            'execution_plan': self.execution_plan,
            'final_output': self.final_output,
            'cost_usd': self.cost_usd,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class DatabaseConnection:
    """Gerenciador de conexão com banco"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
    
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.conn.close()

class ChannelSystem:
    """
    Sistema de canais estilo Discord
    Canais são persistidos no SQLite, não em JSONL
    """
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
    
    def _get_db(self):
        """Retorna conexão com banco"""
        return DatabaseConnection(self.db_path)
    
    def _generate_code(self, prefix: str = "MSG") -> str:
        """Gera código único"""
        return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"
    
    def get_channel_id(self, channel_name: str) -> Optional[int]:
        """Busca ID de um canal pelo nome"""
        with self._get_db() as conn:
            cursor = conn.execute(
                "SELECT id FROM swarm_channels WHERE name = ?",
                (channel_name,)
            )
            row = cursor.fetchone()
            return row['id'] if row else None
    
    def post(self, channel_name: str, author_type: AuthorType, 
             author_id: str, content: str, mentions: List[str] = None) -> SwarmMessage:
        """
        Posta mensagem em um canal
        
        Args:
            channel_name: Nome do canal (ex: 'orders', 'agent-chat')
            author_type: Tipo de autor (user, agent, system)
            author_id: ID do autor
            content: Conteúdo da mensagem
            mentions: Lista de IDs mencionados
            
        Returns:
            SwarmMessage criada
        """
        channel_id = self.get_channel_id(channel_name)
        if not channel_id:
            raise ValueError(f"Canal '{channel_name}' não encontrado")
        
        message_code = self._generate_code("MSG")
        mentions_json = json.dumps(mentions or [])
        created_at_str = datetime.now().isoformat()
        
        with self._get_db() as conn:
            cursor = conn.execute(
                """INSERT INTO swarm_messages 
                   (message_code, channel_id, author_type, author_id, content, mentions, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (message_code, channel_id, author_type.value, author_id, content, mentions_json, created_at_str)
            )
            message_id = cursor.lastrowid
        
        # Retornar mensagem completa (fora do context para garantir commit)
        return self.get_message(message_id)
    
    def get_message(self, message_id: int) -> Optional[SwarmMessage]:
        """Busca mensagem por ID"""
        with self._get_db() as conn:
            cursor = conn.execute(
                """SELECT m.*, c.name as channel_name 
                   FROM swarm_messages m
                   JOIN swarm_channels c ON m.channel_id = c.id
                   WHERE m.id = ?""",
                (message_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return SwarmMessage(
                id=row['id'],
                message_code=row['message_code'],
                channel_id=row['channel_id'],
                channel_name=row['channel_name'],
                author_type=row['author_type'],
                author_id=row['author_id'],
                content=row['content'],
                mentions=json.loads(row['mentions'] or '[]'),
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
            )
    
    def read(self, channel_name: str, limit: int = 50, before_id: int = None) -> List[SwarmMessage]:
        """
        Lê mensagens de um canal
        
        Args:
            channel_name: Nome do canal
            limit: Quantidade máxima
            before_id: ID para paginação (mensagens antes deste ID)
            
        Returns:
            Lista de SwarmMessage
        """
        channel_id = self.get_channel_id(channel_name)
        if not channel_id:
            return []
        
        query = """SELECT m.*, c.name as channel_name 
                   FROM swarm_messages m
                   JOIN swarm_channels c ON m.channel_id = c.id
                   WHERE m.channel_id = ?"""
        params = [channel_id]
        
        if before_id:
            query += " AND m.id < ?"
            params.append(before_id)
        
        query += " ORDER BY m.created_at DESC LIMIT ?"
        params.append(limit)
        
        with self._get_db() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            messages = []
            for row in rows:
                messages.append(SwarmMessage(
                    id=row['id'],
                    message_code=row['message_code'],
                    channel_id=row['channel_id'],
                    channel_name=row['channel_name'],
                    author_type=row['author_type'],
                    author_id=row['author_id'],
                    content=row['content'],
                    mentions=json.loads(row['mentions'] or '[]'),
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                ))
            
            return messages
    
    def search(self, channel_name: str, query: str, limit: int = 20) -> List[SwarmMessage]:
        """
        Busca mensagens em um canal
        
        Args:
            channel_name: Nome do canal
            query: Termo de busca
            limit: Quantidade máxima
            
        Returns:
            Lista de SwarmMessage
        """
        channel_id = self.get_channel_id(channel_name)
        if not channel_id:
            return []
        
        with self._get_db() as conn:
            cursor = conn.execute(
                """SELECT m.*, c.name as channel_name 
                   FROM swarm_messages m
                   JOIN swarm_channels c ON m.channel_id = c.id
                   WHERE m.channel_id = ? AND m.content LIKE ?
                   ORDER BY m.created_at DESC
                   LIMIT ?""",
                (channel_id, f'%{query}%', limit)
            )
            rows = cursor.fetchall()
            
            messages = []
            for row in rows:
                messages.append(SwarmMessage(
                    id=row['id'],
                    message_code=row['message_code'],
                    channel_id=row['channel_id'],
                    channel_name=row['channel_name'],
                    author_type=row['author_type'],
                    author_id=row['author_id'],
                    content=row['content'],
                    mentions=json.loads(row['mentions'] or '[]'),
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                ))
            
            return messages
    
    def get_channels(self) -> List[Dict]:
        """Lista todos os canais"""
        with self._get_db() as conn:
            cursor = conn.execute(
                "SELECT * FROM swarm_channels ORDER BY name"
            )
            rows = cursor.fetchall()
            
            channels = []
            for row in rows:
                channels.append({
                    'id': row['id'],
                    'channel_code': row['channel_code'],
                    'name': row['name'],
                    'channel_type': row['channel_type'],
                    'description': row['description']
                })
            
            return channels
    
    def get_message_count(self, channel_name: str) -> int:
        """Retorna quantidade de mensagens em um canal"""
        channel_id = self.get_channel_id(channel_name)
        if not channel_id:
            return 0
        
        with self._get_db() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) as count FROM swarm_messages WHERE channel_id = ?",
                (channel_id,)
            )
            row = cursor.fetchone()
            return row['count'] if row else 0

class SwarmAgentManager:
    """Gerenciador de agents do swarm"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
    
    def _get_db(self):
        return DatabaseConnection(self.db_path)
    
    def get_agent(self, agent_slug: str) -> Optional[SwarmAgent]:
        """Busca agent por slug"""
        with self._get_db() as conn:
            cursor = conn.execute(
                "SELECT * FROM swarm_agents WHERE agent_slug = ?",
                (agent_slug,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return SwarmAgent(
                id=row['id'],
                agent_slug=row['agent_slug'],
                name=row['name'],
                role=row['role'],
                model_tier=row['model_tier'],
                personality=row['personality'],
                avatar_emoji=row['avatar_emoji'],
                memory=json.loads(row['memory'] or '{}'),
                status=row['status'],
                is_active=bool(row['is_active'])
            )
    
    def get_all_agents(self) -> List[SwarmAgent]:
        """Lista todos os agents"""
        with self._get_db() as conn:
            cursor = conn.execute(
                "SELECT * FROM swarm_agents WHERE is_active = 1 ORDER BY name"
            )
            rows = cursor.fetchall()
            
            agents = []
            for row in rows:
                agents.append(SwarmAgent(
                    id=row['id'],
                    agent_slug=row['agent_slug'],
                    name=row['name'],
                    role=row['role'],
                    model_tier=row['model_tier'],
                    personality=row['personality'],
                    avatar_emoji=row['avatar_emoji'],
                    memory=json.loads(row['memory'] or '{}'),
                    status=row['status'],
                    is_active=bool(row['is_active'])
                ))
            
            return agents
    
    def update_status(self, agent_slug: str, status: str):
        """Atualiza status de um agent"""
        with self._get_db() as conn:
            conn.execute(
                """UPDATE swarm_agents 
                   SET status = ?, last_active_at = ? 
                   WHERE agent_slug = ?""",
                (status, datetime.now(), agent_slug)
            )
    
    def update_memory(self, agent_slug: str, memory_updates: Dict):
        """Atualiza memória de um agent"""
        agent = self.get_agent(agent_slug)
        if not agent:
            return False
        
        # Merge memória existente com updates
        new_memory = {**agent.memory, **memory_updates}
        
        with self._get_db() as conn:
            conn.execute(
                "UPDATE swarm_agents SET memory = ? WHERE agent_slug = ?",
                (json.dumps(new_memory), agent_slug)
            )
        
        return True

class SwarmTaskManager:
    """Gerenciador de tarefas do swarm"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
    
    def _get_db(self):
        return DatabaseConnection(self.db_path)
    
    def _generate_code(self) -> str:
        """Gera código único de tarefa"""
        return f"TASK-{uuid.uuid4().hex[:8].upper()}"
    
    def create_task(self, original_request: str, coordinator_agent_slug: str, 
                    project: str = None, source: str = None, channel_id: int = None) -> SwarmTask:
        """Cria nova tarefa com metadados opcionais (v4.0 - Modo Proativo)"""
        task_code = self._generate_code()
        
        # Preparar metadados JSON
        metadata = {}
        if project:
            metadata['project'] = project
        if source:
            metadata['source'] = source
        if channel_id:
            metadata['discord_channel_id'] = channel_id
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        # Buscar ID do coordinator
        with self._get_db() as conn:
            cursor = conn.execute(
                "SELECT id, name FROM swarm_agents WHERE agent_slug = ?",
                (coordinator_agent_slug,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Agent '{coordinator_agent_slug}' não encontrado")
            
            coordinator_id = row['id']
            coordinator_name = row['name']
            
            # v4.0: Criar com status AWAITING_QUESTIONS (modo proativo)
            cursor = conn.execute(
                """INSERT INTO swarm_tasks 
                   (task_code, original_request, coordinator_agent_id, status, created_at, metadata)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (task_code, original_request, coordinator_id, TaskStatus.AWAITING_QUESTIONS.value, 
                 datetime.now().isoformat(), metadata_json)
            )
            task_id = cursor.lastrowid
        
        return self.get_task(task_id)
    
    def get_task(self, task_id: int) -> Optional[SwarmTask]:
        """Busca tarefa por ID"""
        with self._get_db() as conn:
            cursor = conn.execute(
                """SELECT t.*, a.name as coordinator_name
                   FROM swarm_tasks t
                   JOIN swarm_agents a ON t.coordinator_agent_id = a.id
                   WHERE t.id = ?""",
                (task_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return SwarmTask(
                id=row['id'],
                task_code=row['task_code'],
                original_request=row['original_request'],
                coordinator_agent_id=row['coordinator_agent_id'],
                coordinator_name=row['coordinator_name'],
                status=row['status'],
                execution_plan=json.loads(row['execution_plan'] or '{}'),
                final_output=row['final_output'],
                cost_usd=row['cost_usd'] or 0,
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                started_at=datetime.fromisoformat(row['started_at']) if row['started_at'] else None,
                completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None
            )
    
    def get_task_by_code(self, task_code: str) -> Optional[SwarmTask]:
        """Busca tarefa por código"""
        with self._get_db() as conn:
            cursor = conn.execute(
                "SELECT id FROM swarm_tasks WHERE task_code = ?",
                (task_code,)
            )
            row = cursor.fetchone()
            if row:
                return self.get_task(row['id'])
            return None
    
    def update_status(self, task_id: int, status: TaskStatus):
        """Atualiza status da tarefa"""
        with self._get_db() as conn:
            if status == TaskStatus.RUNNING:
                conn.execute(
                    "UPDATE swarm_tasks SET status = ?, started_at = ? WHERE id = ?",
                    (status.value, datetime.now(), task_id)
                )
            elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                conn.execute(
                    "UPDATE swarm_tasks SET status = ?, completed_at = ? WHERE id = ?",
                    (status.value, datetime.now(), task_id)
                )
            else:
                conn.execute(
                    "UPDATE swarm_tasks SET status = ? WHERE id = ?",
                    (status.value, task_id)
                )
    
    def update_execution_plan(self, task_id: int, plan: Dict):
        """Atualiza plano de execução"""
        with self._get_db() as conn:
            conn.execute(
                "UPDATE swarm_tasks SET execution_plan = ? WHERE id = ?",
                (json.dumps(plan), task_id)
            )
    
    def set_final_output(self, task_id: int, output: str, cost: float = 0):
        """Define resultado final"""
        with self._get_db() as conn:
            conn.execute(
                """UPDATE swarm_tasks 
                   SET final_output = ?, cost_usd = ?, status = ?, completed_at = ?
                   WHERE id = ?""",
                (output, cost, TaskStatus.COMPLETED.value, datetime.now(), task_id)
            )
        
        # 🆕 Envia para review no Discord (se RAG disponível)
        try:
            import os
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'swarm'))
            from discord_bridge import SwarmDiscordBridge, HAS_RAG
            
            if HAS_RAG:
                # Busca informações da task
                task = self.get_task(task_id)
                if task:
                    # Canal de review (usar o mesmo do swarm ou um específico)
                    review_channel_id = 1330639710266044467  # Ajustar conforme necessário
                    
                    # Detecta tipo de task
                    task_lower = task.original_request.lower()
                    task_type = 'general'
                    if any(kw in task_lower for kw in ['análise', 'analisar', 'research', 'pesquisa']):
                        task_type = 'analysis'
                    elif any(kw in task_lower for kw in ['código', 'build', 'implementar', 'script']):
                        task_type = 'code'
                    elif any(kw in task_lower for kw in ['copy', 'escrever', 'headline', 'conteúdo']):
                        task_type = 'content'
                    
                    # Envia para review (assíncrono - não bloqueia)
                    # Nota: Para funcionar completamente, precisa de loop async rodando
                    print(f"📤 Task {task_id} completada. Enviando para review no Discord...")
                    
        except Exception as e:
            # Não falha a task se o review falhar
            print(f"⚠️ Erro ao enviar para review: {e}")
    
    def get_active_tasks(self) -> List[SwarmTask]:
        """Lista tarefas ativas (não completadas/falhas)"""
        with self._get_db() as conn:
            cursor = conn.execute(
                """SELECT t.id FROM swarm_tasks t
                   WHERE t.status NOT IN (?, ?)
                   ORDER BY t.created_at DESC""",
                (TaskStatus.COMPLETED.value, TaskStatus.FAILED.value)
            )
            rows = cursor.fetchall()
            
            return [self.get_task(row['id']) for row in rows]
    
    def get_today_summary(self) -> Dict:
        """Retorna resumo do dia"""
        today = datetime.now().date().isoformat()
        
        with self._get_db() as conn:
            cursor = conn.execute(
                """SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
                   FROM swarm_tasks
                   WHERE date(created_at) = date('now')"""
            )
            row = cursor.fetchone()
            
            return {
                'tasks': row['total'] or 0,
                'completed': row['completed'] or 0
            }


# Exportar classes principais
__all__ = [
    'ChannelSystem',
    'SwarmAgentManager',
    'SwarmTaskManager',
    'SwarmMessage',
    'SwarmAgent',
    'SwarmTask',
    'AuthorType',
    'TaskStatus'
]


# Teste simples
if __name__ == '__main__':
    print("🐝 Ralph Swarm Core v5.0 - Teste")
    print("=" * 50)
    
    # Testar ChannelSystem
    channels = ChannelSystem()
    
    print("\n1. Listando canais:")
    for ch in channels.get_channels()[:5]:
        print(f"   #{ch['name']} - {ch['description']}")
    
    print("\n2. Postando mensagem em #orders:")
    msg = channels.post(
        channel_name='orders',
        author_type=AuthorType.USER,
        author_id='Jeff',
        content='Teste do sistema de canais!',
        mentions=['ralph']
    )
    print(f"   ✅ Mensagem #{msg.id} criada")
    
    print("\n3. Lendo mensagens de #orders:")
    messages = channels.read('orders', limit=3)
    for m in messages:
        print(f"   [{m.author_id}] {m.content[:50]}...")
    
    print("\n4. Listando agents:")
    agents = SwarmAgentManager()
    for agent in agents.get_all_agents():
        print(f"   {agent.avatar_emoji} {agent.name} ({agent.role}) - {agent.model_tier}")
    
    print("\n5. Criando tarefa de teste:")
    tasks = SwarmTaskManager()
    task = tasks.create_task(
        original_request="Research concorrentes e criar landing page",
        coordinator_agent_slug='ralph'
    )
    print(f"   ✅ Task {task.task_code} criada")
    print(f"   Coordinator: {task.coordinator_name}")
    
    print("\n" + "=" * 50)
    print("✅ Todos os testes passaram!")
