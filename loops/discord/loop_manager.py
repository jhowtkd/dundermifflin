#!/usr/bin/env python3
"""
Ralph Loop Manager - Sistema de Iteração Contínua para Discord
Fase 1: Estrutura Base
"""

import os
import sys
import uuid
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Database path
DB_PATH = Path.home() / ".openclaw/workspace/projects/dunder-mifflin/dunder_mifflin.db"


class LoopStatus(Enum):
    """Status possíveis de um loop"""
    PENDING = "pending"           # Criado, aguardando início
    RUNNING = "running"           # Em execução
    PAUSED = "paused"             # Pausado pelo usuário
    COMPLETED = "completed"       # Completado com sucesso
    FAILED = "failed"             # Falhou
    INCOMPLETE = "incomplete"     # Max iterations atingido sem completion


@dataclass
class RalphLoop:
    """Representa um loop de iteração"""
    loop_code: str
    task_code: Optional[str]
    agent_slug: str
    task_description: str  # Nome da coluna no banco existente
    max_iterations: int
    current_iteration: int
    status: str
    total_tokens_in: int
    total_tokens_out: int
    created_at: datetime
    completed_at: Optional[datetime]
    result_summary: Optional[str]
    discord_channel_id: Optional[str]
    discord_user_id: Optional[str]
    discord_guild_id: Optional[str]
    
    def to_dict(self) -> Dict:
        return {
            'loop_code': self.loop_code,
            'task_code': self.task_code,
            'agent_slug': self.agent_slug,
            'task_description': self.task_description,
            'max_iterations': self.max_iterations,
            'current_iteration': self.current_iteration,
            'status': self.status,
            'total_tokens_in': self.total_tokens_in,
            'total_tokens_out': self.total_tokens_out,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'result_summary': self.result_summary,
            'discord_channel_id': self.discord_channel_id,
            'discord_user_id': self.discord_user_id,
            'discord_guild_id': self.discord_guild_id,
        }


@dataclass
class LoopIteration:
    """Representa uma iteração individual de um loop"""
    id: int
    loop_code: str
    iteration_number: int
    prompt_summary: Optional[str]
    response_summary: Optional[str]
    full_prompt: Optional[str]
    full_response: Optional[str]
    tokens_in: int
    tokens_out: int
    duration_seconds: int
    created_at: datetime
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'loop_code': self.loop_code,
            'iteration_number': self.iteration_number,
            'prompt_summary': self.prompt_summary,
            'response_summary': self.response_summary,
            'tokens_in': self.tokens_in,
            'tokens_out': self.tokens_out,
            'duration_seconds': self.duration_seconds,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class LoopManager:
    """Gerenciador de loops do Ralph"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_tables()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Obtém conexão com o banco"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Habilitar foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    def _ensure_tables(self):
        """Garante que as tabelas existem"""
        # As tabelas já devem existir (criadas pelo script SQL)
        pass
    
    def _generate_loop_code(self) -> str:
        """Gera código único para o loop"""
        return f"LOOP-{uuid.uuid4().hex[:10].upper()}"
    
    def create_loop(
        self,
        agent_slug: str,
        task_description: str,
        max_iterations: int = 20,
        discord_channel_id: Optional[str] = None,
        discord_user_id: Optional[str] = None,
        discord_guild_id: Optional[str] = None,
        task_code: Optional[str] = None
    ) -> str:
        """
        Cria um novo loop.
        
        Args:
            agent_slug: Slug do agente (ex: 'dev', 'max', 'ralf')
            original_request: Descrição da tarefa
            max_iterations: Máximo de iterações (padrão: 20)
            discord_channel_id: ID do canal do Discord
            discord_user_id: ID do usuário que iniciou
            discord_guild_id: ID do servidor
            task_code: Código da task relacionada (opcional)
            
        Returns:
            Código do loop criado
            
        Raises:
            ValueError: Se o agente não existir no banco
        """
        # Validar se o agente existe
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM agents WHERE slug = ?", (agent_slug,))
            if not cursor.fetchone():
                raise ValueError(f"Agente '{agent_slug}' não encontrado. Verifique o slug.")
        
        loop_code = self._generate_loop_code()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ralph_loops (
                    loop_code, task_code, agent_slug, task_description,
                    max_iterations, current_iteration, status,
                    total_tokens_in, total_tokens_out,
                    discord_channel_id, discord_user_id, discord_guild_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                loop_code, task_code, agent_slug, task_description,
                max_iterations, 0, LoopStatus.PENDING.value,
                0, 0,
                discord_channel_id, discord_user_id, discord_guild_id
            ))
            conn.commit()
        
        return loop_code
    
    def get_loop(self, loop_code: str) -> Optional[RalphLoop]:
        """Obtém um loop pelo código"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM ralph_loops WHERE loop_code = ?
            """, (loop_code,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return RalphLoop(
                loop_code=row['loop_code'],
                task_code=row['task_code'] if 'task_code' in row.keys() else None,
                agent_slug=row['agent_slug'],
                task_description=row['task_description'],
                max_iterations=row['max_iterations'],
                current_iteration=row['current_iteration'],
                status=row['status'],
                total_tokens_in=row['total_tokens_in'],
                total_tokens_out=row['total_tokens_out'],
                created_at=datetime.fromisoformat(row['started_at']) if row['started_at'] else None,
                completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None,
                result_summary=row['result_summary'] if 'result_summary' in row.keys() else None,
                discord_channel_id=row['discord_channel_id'] if 'discord_channel_id' in row.keys() else None,
                discord_user_id=row['discord_user_id'] if 'discord_user_id' in row.keys() else None,
                discord_guild_id=row['discord_guild_id'] if 'discord_guild_id' in row.keys() else None,
            )
    
    def list_loops(
        self,
        status: Optional[str] = None,
        agent_slug: Optional[str] = None,
        limit: int = 50
    ) -> List[RalphLoop]:
        """Lista loops com filtros opcionais"""
        query = "SELECT * FROM ralph_loops WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if agent_slug:
            query += " AND agent_slug = ?"
            params.append(agent_slug)
        
        query += " ORDER BY started_at DESC LIMIT ?"
        params.append(limit)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            loops = []
            for row in rows:
                loops.append(RalphLoop(
                    loop_code=row['loop_code'],
                    task_code=row['task_code'] if 'task_code' in row.keys() else None,
                    agent_slug=row['agent_slug'],
                    task_description=row['task_description'],
                    max_iterations=row['max_iterations'],
                    current_iteration=row['current_iteration'],
                    status=row['status'],
                    total_tokens_in=row['total_tokens_in'],
                    total_tokens_out=row['total_tokens_out'],
                    created_at=datetime.fromisoformat(row['started_at']) if row['started_at'] else None,
                    completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None,
                    result_summary=row['result_summary'] if 'result_summary' in row.keys() else None,
                    discord_channel_id=row['discord_channel_id'] if 'discord_channel_id' in row.keys() else None,
                    discord_user_id=row['discord_user_id'] if 'discord_user_id' in row.keys() else None,
                    discord_guild_id=row['discord_guild_id'] if 'discord_guild_id' in row.keys() else None,
                ))
            
            return loops
    
    def update_loop_status(
        self,
        loop_code: str,
        status: str,
        result_summary: Optional[str] = None
    ) -> bool:
        """Atualiza status de um loop"""
        # Validar status contra enum
        valid_statuses = [s.value for s in LoopStatus]
        if status not in valid_statuses:
            raise ValueError(f"Status inválido: '{status}'. Status válidos: {valid_statuses}")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if status in [LoopStatus.COMPLETED.value, LoopStatus.FAILED.value, LoopStatus.INCOMPLETE.value]:
                cursor.execute("""
                    UPDATE ralph_loops 
                    SET status = ?, completed_at = CURRENT_TIMESTAMP, result_summary = ?
                    WHERE loop_code = ?
                """, (status, result_summary, loop_code))
            else:
                cursor.execute("""
                    UPDATE ralph_loops 
                    SET status = ?, result_summary = ?
                    WHERE loop_code = ?
                """, (status, result_summary, loop_code))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def increment_iteration(
        self,
        loop_code: str,
        tokens_in: int = 0,
        tokens_out: int = 0
    ) -> bool:
        """Incrementa contador de iteração e tokens"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE ralph_loops 
                SET current_iteration = current_iteration + 1,
                    total_tokens_in = total_tokens_in + ?,
                    total_tokens_out = total_tokens_out + ?
                WHERE loop_code = ?
            """, (tokens_in, tokens_out, loop_code))
            conn.commit()
            return cursor.rowcount > 0
    
    def log_iteration(
        self,
        loop_code: str,
        iteration_number: int,
        prompt_summary: str,
        response_summary: str,
        full_prompt: Optional[str] = None,
        full_response: Optional[str] = None,
        tokens_in: int = 0,
        tokens_out: int = 0,
        duration_seconds: int = 0
    ) -> int:
        """
        Registra uma iteração no banco.
        
        Returns:
            ID da iteração criada
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ralph_loop_iterations (
                    loop_code, iteration_number, prompt_summary, response_summary,
                    full_prompt, full_response, tokens_in, tokens_out, duration_seconds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                loop_code, iteration_number, prompt_summary, response_summary,
                full_prompt, full_response, tokens_in, tokens_out, duration_seconds
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_iterations(self, loop_code: str) -> List[LoopIteration]:
        """Obtém todas as iterações de um loop"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM ralph_loop_iterations 
                WHERE loop_code = ?
                ORDER BY iteration_number ASC
            """, (loop_code,))
            rows = cursor.fetchall()
            
            iterations = []
            for row in rows:
                iterations.append(LoopIteration(
                    id=row['id'],
                    loop_code=row['loop_code'],
                    iteration_number=row['iteration_number'],
                    prompt_summary=row['prompt_summary'],
                    response_summary=row['response_summary'],
                    full_prompt=row['full_prompt'],
                    full_response=row['full_response'],
                    tokens_in=row['tokens_in'],
                    tokens_out=row['tokens_out'],
                    duration_seconds=row['duration_seconds'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                ))
            
            return iterations
    
    def get_latest_iteration(self, loop_code: str) -> Optional[LoopIteration]:
        """Obtém a iteração mais recente de um loop"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM ralph_loop_iterations 
                WHERE loop_code = ?
                ORDER BY iteration_number DESC
                LIMIT 1
            """, (loop_code,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return LoopIteration(
                id=row['id'],
                loop_code=row['loop_code'],
                iteration_number=row['iteration_number'],
                prompt_summary=row['prompt_summary'],
                response_summary=row['response_summary'],
                full_prompt=row['full_prompt'],
                full_response=row['full_response'],
                tokens_in=row['tokens_in'],
                tokens_out=row['tokens_out'],
                duration_seconds=row['duration_seconds'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            )
    
    def delete_loop(self, loop_code: str) -> bool:
        """Deleta um loop e suas iterações"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Deleta iterações primeiro (FK)
            cursor.execute("DELETE FROM ralph_loop_iterations WHERE loop_code = ?", (loop_code,))
            # Deleta loop
            cursor.execute("DELETE FROM ralph_loops WHERE loop_code = ?", (loop_code,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_stats(self) -> Dict:
        """Obtém estatísticas gerais de loops"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Total por status
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM ralph_loops 
                GROUP BY status
            """)
            status_counts = {row['status']: row['count'] for row in cursor.fetchall()}
            
            # Total de tokens
            cursor.execute("""
                SELECT 
                    SUM(total_tokens_in) as total_in,
                    SUM(total_tokens_out) as total_out,
                    COUNT(*) as total_loops
                FROM ralph_loops
            """)
            row = cursor.fetchone()
            
            return {
                'status_counts': status_counts,
                'total_tokens_in': row['total_in'] or 0,
                'total_tokens_out': row['total_out'] or 0,
                'total_loops': row['total_loops'] or 0,
            }


# Funções utilitárias para CLI

def create_loop_cli():
    """CLI para criar loop (para testes)"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Criar novo loop Ralph')
    parser.add_argument('agent', help='Slug do agente (dev, max, ralf, etc)')
    parser.add_argument('task', help='Descrição da tarefa')
    parser.add_argument('--max', type=int, default=20, help='Máximo de iterações')
    parser.add_argument('--channel', help='Discord channel ID')
    parser.add_argument('--user', help='Discord user ID')
    
    args = parser.parse_args()
    
    manager = LoopManager()
    loop_code = manager.create_loop(
        agent_slug=args.agent,
        task_description=args.task,
        max_iterations=args.max,
        discord_channel_id=args.channel,
        discord_user_id=args.user
    )
    
    print(f"✅ Loop criado: {loop_code}")
    print(f"   Agente: {args.agent}")
    print(f"   Tarefa: {args.task}")
    print(f"   Max iterações: {args.max}")


def list_loops_cli():
    """CLI para listar loops (para testes)"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Listar loops Ralph')
    parser.add_argument('--status', help='Filtrar por status')
    parser.add_argument('--agent', help='Filtrar por agente')
    parser.add_argument('--limit', type=int, default=20, help='Limite de resultados')
    
    args = parser.parse_args()
    
    manager = LoopManager()
    loops = manager.list_loops(
        status=args.status,
        agent_slug=args.agent,
        limit=args.limit
    )
    
    if not loops:
        print("Nenhum loop encontrado.")
        return
    
    print(f"{'Loop Code':<20} {'Agente':<15} {'Status':<12} {'Iter':<6} {'Criado':<20}")
    print("-" * 80)
    
    for loop in loops:
        created = loop.created_at.strftime("%Y-%m-%d %H:%M") if loop.created_at else "N/A"
        print(f"{loop.loop_code:<20} {loop.agent_slug:<15} {loop.status:<12} "
              f"{loop.current_iteration}/{loop.max_iterations:<3} {created:<20}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python3 loop_manager.py [create|list|test]")
        sys.exit(1)
    
    command = sys.argv[1]
    sys.argv = sys.argv[1:]  # Remove comando para argparse
    
    if command == "create":
        create_loop_cli()
    elif command == "list":
        list_loops_cli()
    elif command == "test":
        # Teste básico
        print("🧪 Testando LoopManager...")
        manager = LoopManager()
        
        # Pegar um agente válido do banco
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT slug FROM agents LIMIT 1")
        agent_row = cursor.fetchone()
        conn.close()
        
        if not agent_row:
            print("❌ Nenhum agente encontrado no banco!")
            sys.exit(1)
        
        valid_agent = agent_row[0]
        print(f"📌 Usando agente: {valid_agent}")
        
        # Criar loop
        loop_code = manager.create_loop(
            agent_slug=valid_agent,
            task_description="Teste de criação de loop",
            max_iterations=10,
            discord_channel_id="123456",
            discord_user_id="789012"
        )
        print(f"✅ Loop criado: {loop_code}")
        
        # Obter loop
        loop = manager.get_loop(loop_code)
        print(f"✅ Loop obtido: {loop.agent_slug} - {loop.status}")
        
        # Logar iteração
        iter_id = manager.log_iteration(
            loop_code=loop_code,
            iteration_number=1,
            prompt_summary="Prompt de teste...",
            response_summary="Resposta de teste...",
            tokens_in=1000,
            tokens_out=500,
            duration_seconds=5
        )
        print(f"✅ Iteração logada: ID {iter_id}")
        
        # Incrementar
        manager.increment_iteration(loop_code, 1000, 500)
        print(f"✅ Iteração incrementada")
        
        # Atualizar status
        manager.update_loop_status(loop_code, LoopStatus.COMPLETED.value, "Teste completado")
        print(f"✅ Status atualizado")
        
        # Listar
        loops = manager.list_loops()
        print(f"✅ Total de loops: {len(loops)}")
        
        # Stats
        stats = manager.get_stats()
        print(f"✅ Stats: {stats}")
        
        print("\n🎉 Todos os testes passaram!")
    else:
        print(f"Comando desconhecido: {command}")
        print("Comandos: create, list, test")
