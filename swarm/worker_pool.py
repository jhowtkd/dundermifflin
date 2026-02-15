#!/usr/bin/env python3
"""
Ralph Swarm - Worker Pool Manager
Gerencia execução de tasks com limite de concorrência e fila
"""

import asyncio
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('worker_pool')

DB_PATH = Path.home() / ".openclaw/workspace/projects/dunder-mifflin/dunder_mifflin.db"

# Config
MAX_CONCURRENT_TASKS = 5  # Máximo de tasks simultâneas


@dataclass
class QueuedTask:
    """Task na fila de espera"""
    task_id: int
    task_code: str
    request: str
    queued_at: datetime
    priority: int = 0


class WorkerPool:
    """
    Pool de workers para execução de tasks.
    Limita concorrência e gerencia fila.
    """
    
    def __init__(self, max_workers: int = MAX_CONCURRENT_TASKS):
        self.max_workers = max_workers
        self.running_tasks: Dict[int, asyncio.Task] = {}
        self.queue: List[QueuedTask] = []
        self.semaphore = asyncio.Semaphore(max_workers)
        self.processing = False
        
    def _init_db(self):
        """Inicializa tabela de fila"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER UNIQUE NOT NULL,
                task_code TEXT NOT NULL,
                request TEXT NOT NULL,
                queued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                status TEXT DEFAULT 'queued',  -- queued, running, completed, failed
                priority INTEGER DEFAULT 0,
                FOREIGN KEY (task_id) REFERENCES swarm_tasks(id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_queue_status 
            ON task_queue(status)
        """)
        
        conn.commit()
        conn.close()
    
    def get_running_count(self) -> int:
        """Retorna número de tasks em execução"""
        # Limpa tasks finalizadas
        done = [tid for tid, task in self.running_tasks.items() if task.done()]
        for tid in done:
            del self.running_tasks[tid]
        
        return len(self.running_tasks)
    
    def can_execute(self) -> bool:
        """Verifica se pode executar mais uma task"""
        return self.get_running_count() < self.max_workers
    
    async def submit_task(self, task_id: int, task_code: str, request: str) -> bool:
        """
        Submete uma task para execução.
        Se não houver slot disponível, vai para fila.
        """
        if self.can_execute():
            # Executa imediatamente
            await self._execute_task(task_id, task_code, request)
            return True
        else:
            # Adiciona à fila
            await self._queue_task(task_id, task_code, request)
            return False
    
    async def _queue_task(self, task_id: int, task_code: str, request: str):
        """Adiciona task à fila"""
        queued = QueuedTask(
            task_id=task_id,
            task_code=task_code,
            request=request,
            queued_at=datetime.now()
        )
        
        self.queue.append(queued)
        
        # Salva no banco
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO task_queue (task_id, task_code, request, status)
            VALUES (?, ?, ?, 'queued')
        """, (task_id, task_code, request))
        conn.commit()
        conn.close()
        
        logger.info(f"📥 Task {task_code} queued (position: {len(self.queue)})")
    
    async def _execute_task(self, task_id: int, task_code: str, request: str):
        """Executa uma task com o semaphore"""
        async with self.semaphore:
            # Registra como running
            self.running_tasks[task_id] = asyncio.current_task()
            
            # Atualiza no banco
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE task_queue 
                SET status = 'running', started_at = ?
                WHERE task_id = ?
            """, (datetime.now(), task_id))
            conn.commit()
            conn.close()
            
            logger.info(f"▶️  Task {task_code} started ({self.get_running_count()}/{self.max_workers} running)")
            
            try:
                # Executa via coordination engine
                sys_path = str(Path(__file__).parent)
                if sys_path not in sys.path:
                    sys.path.insert(0, sys_path)
                
                from coordination_engine import SwarmCoordinator
                
                coordinator = SwarmCoordinator()
                plan = coordinator.analyze_task(request)
                result = coordinator.execute_swarm(request, plan, task_id)
                
                # Marca como completada
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE task_queue 
                    SET status = 'completed', completed_at = ?
                    WHERE task_id = ?
                """, (datetime.now(), task_id))
                conn.commit()
                conn.close()
                
                logger.info(f"✅ Task {task_code} completed")
                
            except Exception as e:
                logger.error(f"❌ Task {task_code} failed: {e}")
                
                # Marca como falha
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE task_queue 
                    SET status = 'failed', completed_at = ?
                    WHERE task_id = ?
                """, (datetime.now(), task_id))
                conn.commit()
                conn.close()
            
            finally:
                # Processa próxima da fila
                if self.queue:
                    await self._process_queue()
    
    async def _process_queue(self):
        """Processa próxima task da fila"""
        if not self.queue or not self.can_execute():
            return
        
        # Pega próxima da fila
        next_task = self.queue.pop(0)
        
        # Executa
        asyncio.create_task(
            self._execute_task(
                next_task.task_id,
                next_task.task_code,
                next_task.request
            )
        )
        
        logger.info(f"🔄 Processing queued task {next_task.task_code} ({len(self.queue)} remaining)")
    
    async def start(self):
        """Inicia o worker pool"""
        self._init_db()
        self.processing = True
        
        # Recupera tasks que estavam na fila
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT task_id, task_code, request 
            FROM task_queue 
            WHERE status = 'queued'
            ORDER BY queued_at ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        
        for row in rows:
            await self._queue_task(row[0], row[1], row[2])
        
        logger.info(f"🚀 Worker pool started (max: {self.max_workers}, queued: {len(self.queue)})")
    
    def get_status(self) -> dict:
        """Retorna status do pool"""
        return {
            'max_workers': self.max_workers,
            'running': self.get_running_count(),
            'queued': len(self.queue),
            'available_slots': self.max_workers - self.get_running_count()
        }
    
    def stop(self):
        """Para o worker pool"""
        self.processing = False
        logger.info("🛑 Worker pool stopped")


# Singleton global
worker_pool = WorkerPool()


async def submit_task(task_id: int, task_code: str, request: str) -> bool:
    """Submete uma task para o pool"""
    return await worker_pool.submit_task(task_id, task_code, request)


def get_pool_status() -> dict:
    """Retorna status do pool"""
    return worker_pool.get_status()


if __name__ == "__main__":
    async def main():
        pool = WorkerPool(max_workers=3)
        await pool.start()
        
        # Teste
        for i in range(5):
            await submit_task(i, f"TEST-{i}", f"Test task {i}")
        
        # Mantém rodando
        await asyncio.sleep(60)
    
    asyncio.run(main())
