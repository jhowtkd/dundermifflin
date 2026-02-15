#!/usr/bin/env python3
"""
Ralph Swarm - Task Monitor & Recovery System
Sistema de monitoramento, timeout, retry e graceful shutdown
"""

import sqlite3
import asyncio
import signal
import sys
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('task_monitor')

DB_PATH = Path.home() / ".openclaw/workspace/projects/dunder-mifflin/dunder_mifflin.db"
STATE_FILE = Path.home() / ".openclaw/workspace/projects/dunder-mifflin/swarm/task_state.json"

# Configurações
TASK_TIMEOUT_SECONDS = 600  # 10 minutos max por task
MAX_RETRIES = 3
MAX_CONCURRENT_TASKS = 5
HEARTBEAT_INTERVAL = 30  # segundos
RETRY_DELAYS = [60, 300, 900]  # 1min, 5min, 15min

@dataclass
class TaskState:
    """Estado de uma task em execução"""
    task_id: int
    task_code: str
    started_at: datetime
    last_heartbeat: datetime
    retry_count: int = 0
    agent_slug: str = ""
    pid: int = 0

class TaskMonitor:
    """
    Monitor de tasks do Swarm.
    Responsável por: timeout, retry, graceful shutdown, recovery
    """
    
    def __init__(self):
        self.running_tasks: Dict[int, TaskState] = {}
        self.shutdown_requested = False
        self.monitor_task = None
        self.heartbeat_task = None
        
    def _init_db(self):
        """Inicializa tabelas necessárias"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Tabela de execução de tasks (para rastreamento)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                task_code TEXT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_heartbeat TIMESTAMP,
                completed_at TIMESTAMP,
                status TEXT DEFAULT 'running',  -- running, completed, failed, timeout
                retry_count INTEGER DEFAULT 0,
                error_message TEXT,
                pid INTEGER,
                FOREIGN KEY (task_id) REFERENCES swarm_tasks(id)
            )
        """)
        
        # Índices
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_exec_task 
            ON task_executions(task_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_exec_status 
            ON task_executions(status)
        """)
        
        conn.commit()
        conn.close()
        logger.info("📊 Task monitor database initialized")
    
    def register_task(self, task_id: int, task_code: str, agent_slug: str = "") -> TaskState:
        """Registra uma task em execução"""
        state = TaskState(
            task_id=task_id,
            task_code=task_code,
            started_at=datetime.now(),
            last_heartbeat=datetime.now(),
            retry_count=0,
            agent_slug=agent_slug,
            pid=os.getpid()
        )
        
        self.running_tasks[task_id] = state
        
        # Salva no banco
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO task_executions (task_id, task_code, started_at, last_heartbeat, status, pid)
            VALUES (?, ?, ?, ?, 'running', ?)
        """, (task_id, task_code, state.started_at, state.last_heartbeat, state.pid))
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Task {task_code} registered (PID: {state.pid})")
        return state
    
    def heartbeat(self, task_id: int):
        """Atualiza heartbeat de uma task"""
        if task_id in self.running_tasks:
            self.running_tasks[task_id].last_heartbeat = datetime.now()
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE task_executions 
                SET last_heartbeat = ?
                WHERE task_id = ? AND status = 'running'
            """, (datetime.now(), task_id))
            conn.commit()
            conn.close()
    
    def complete_task(self, task_id: int, success: bool = True, error: str = None):
        """Marca task como completada"""
        if task_id in self.running_tasks:
            del self.running_tasks[task_id]
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE task_executions 
            SET status = ?, completed_at = ?, error_message = ?
            WHERE task_id = ? AND status = 'running'
        """, ('completed' if success else 'failed', datetime.now(), error, task_id))
        
        # Atualiza swarm_tasks também
        cursor.execute("""
            UPDATE swarm_tasks 
            SET status = ?
            WHERE id = ?
        """, ('completed' if success else 'failed', task_id))
        
        conn.commit()
        conn.close()
        
        status = "✅ completed" if success else "❌ failed"
        logger.info(f"Task {task_id} {status}")
    
    async def _monitor_loop(self):
        """Loop principal de monitoramento"""
        while not self.shutdown_requested:
            try:
                await self._check_timeouts()
                await self._check_stalled_tasks()
                await asyncio.sleep(HEARTBEAT_INTERVAL)
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                await asyncio.sleep(5)
    
    async def _check_timeouts(self):
        """Verifica tasks que expiraram timeout"""
        now = datetime.now()
        timed_out = []
        
        for task_id, state in self.running_tasks.items():
            elapsed = (now - state.started_at).total_seconds()
            
            if elapsed > TASK_TIMEOUT_SECONDS:
                timed_out.append(task_id)
                logger.warning(f"⏱️ Task {state.task_code} timed out ({elapsed}s)")
        
        for task_id in timed_out:
            await self._handle_timeout(task_id)
    
    async def _handle_timeout(self, task_id: int):
        """Lida com task que deu timeout"""
        state = self.running_tasks.get(task_id)
        if not state:
            return
        
        # Marca como timeout no banco
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE task_executions 
            SET status = 'timeout', completed_at = ?, error_message = 'Task exceeded maximum execution time'
            WHERE task_id = ?
        """, (datetime.now(), task_id))
        conn.commit()
        conn.close()
        
        # Remove do running
        del self.running_tasks[task_id]
        
        # Tenta retry
        await self._schedule_retry(task_id, state.task_code, "Timeout")
    
    async def _check_stalled_tasks(self):
        """Verifica tasks que pararam de enviar heartbeat"""
        now = datetime.now()
        stalled = []
        
        for task_id, state in self.running_tasks.items():
            since_last = (now - state.last_heartbeat).total_seconds()
            
            # Se não houve heartbeat em 2 minutos, considera travada
            if since_last > 120:
                stalled.append(task_id)
                logger.warning(f"💔 Task {state.task_code} stalled (no heartbeat for {since_last}s)")
        
        for task_id in stalled:
            await self._handle_stalled(task_id)
    
    async def _handle_stalled(self, task_id: int):
        """Lida com task travada"""
        state = self.running_tasks.get(task_id)
        if not state:
            return
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE task_executions 
            SET status = 'stalled', completed_at = ?, error_message = 'Task stopped responding (no heartbeat)'
            WHERE task_id = ?
        """, (datetime.now(), task_id))
        conn.commit()
        conn.close()
        
        del self.running_tasks[task_id]
        
        await self._schedule_retry(task_id, state.task_code, "Stalled")
    
    async def _schedule_retry(self, task_id: int, task_code: str, reason: str):
        """Agenda retry de uma task"""
        # Busca retry count atual
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT retry_count FROM task_executions 
            WHERE task_id = ? 
            ORDER BY started_at DESC LIMIT 1
        """, (task_id,))
        row = cursor.fetchone()
        retry_count = row[0] if row else 0
        conn.close()
        
        if retry_count >= MAX_RETRIES:
            logger.error(f"❌ Task {task_code} failed permanently after {MAX_RETRIES} retries")
            await self._notify_failure(task_code, f"Failed after {MAX_RETRIES} retries. Reason: {reason}")
            return
        
        delay = RETRY_DELAYS[min(retry_count, len(RETRY_DELAYS) - 1)]
        logger.info(f"🔄 Scheduling retry {retry_count + 1} for {task_code} in {delay}s")
        
        await asyncio.sleep(delay)
        
        if not self.shutdown_requested:
            await self._execute_retry(task_id, retry_count + 1)
    
    async def _execute_retry(self, task_id: int, new_retry_count: int):
        """Executa retry de uma task"""
        try:
            # Busca dados da task original
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT original_request, coordinator_agent_id 
                FROM swarm_tasks WHERE id = ?
            """, (task_id,))
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return
            
            request, agent_id = row
            
            # Re-executa via coordination engine
            sys.path.insert(0, str(Path(__file__).parent))
            from coordination_engine import SwarmCoordinator
            
            coordinator = SwarmCoordinator()
            plan = coordinator.analyze_task(request)
            
            # Atualiza retry count
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE swarm_tasks SET status = 'running' WHERE id = ?
            """, (task_id,))
            conn.commit()
            conn.close()
            
            # Executa
            result = coordinator.execute_swarm(request, plan, task_id)
            
            logger.info(f"✅ Retry of task {task_id} completed")
            
        except Exception as e:
            logger.error(f"❌ Retry failed for task {task_id}: {e}")
            await self._schedule_retry(task_id, f"task_{task_id}", str(e))
    
    async def _notify_failure(self, task_code: str, reason: str):
        """Notifica falha permanente"""
        logger.error(f"🚨 TASK FAILED PERMANENTLY: {task_code} - {reason}")
        # TODO: Enviar notificação no Discord
    
    def save_state(self):
        """Salva estado atual para recovery"""
        state = {
            'timestamp': datetime.now().isoformat(),
            'running_tasks': {
                tid: {
                    'task_code': ts.task_code,
                    'started_at': ts.started_at.isoformat(),
                    'last_heartbeat': ts.last_heartbeat.isoformat(),
                    'retry_count': ts.retry_count,
                    'agent_slug': ts.agent_slug
                }
                for tid, ts in self.running_tasks.items()
            }
        }
        
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"💾 State saved ({len(self.running_tasks)} running tasks)")
    
    def load_state(self) -> List[int]:
        """Carrega estado anterior e retorna tasks que precisam ser recuperadas"""
        if not STATE_FILE.exists():
            return []
        
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
            
            # Verifica se há tasks que estavam rodando
            orphaned_tasks = []
            
            for tid, ts_data in state.get('running_tasks', {}).items():
                tid = int(tid)
                
                # Verifica no banco se a task ainda está em running
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT status FROM swarm_tasks WHERE id = ?
                """, (tid,))
                row = cursor.fetchone()
                conn.close()
                
                if row and row[0] == 'running':
                    orphaned_tasks.append(tid)
                    logger.warning(f"🔄 Found orphaned task {ts_data['task_code']} (ID: {tid})")
            
            return orphaned_tasks
            
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            return []
    
    async def recover_orphaned_tasks(self, orphaned: List[int]):
        """Recupera tasks que ficaram órfãs após crash"""
        for task_id in orphaned:
            logger.info(f"🔄 Recovering orphaned task {task_id}")
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Marca como failed
            cursor.execute("""
                UPDATE swarm_tasks 
                SET status = 'failed', final_output = 'Task failed due to system restart'
                WHERE id = ?
            """, (task_id,))
            
            # Marca execução como stalled
            cursor.execute("""
                UPDATE task_executions 
                SET status = 'stalled', completed_at = ?, error_message = 'Process crashed during execution'
                WHERE task_id = ? AND status = 'running'
            """, (datetime.now(), task_id))
            
            conn.commit()
            conn.close()
            
            # Agenda retry
            await self._schedule_retry(task_id, f"recovered_task_{task_id}", "System restart")
    
    def setup_signal_handlers(self):
        """Configura handlers para graceful shutdown"""
        def signal_handler(sig, frame):
            logger.info(f"🛑 Shutdown signal received ({sig})")
            self.shutdown_requested = True
            self.save_state()
            sys.exit(0)
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    async def start(self):
        """Inicia o monitor"""
        self._init_db()
        self.setup_signal_handlers()
        
        # Recupera tasks órfãs
        orphaned = self.load_state()
        if orphaned:
            await self.recover_orphaned_tasks(orphaned)
        
        # Inicia loops
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        
        logger.info("🚀 Task monitor started")
    
    async def stop(self):
        """Para o monitor"""
        self.shutdown_requested = True
        self.save_state()
        
        if self.monitor_task:
            self.monitor_task.cancel()
        
        logger.info("🛑 Task monitor stopped")


# Singleton global
task_monitor = TaskMonitor()

# Funções de conveniência
def register_task(task_id: int, task_code: str, agent_slug: str = "") -> TaskState:
    """Registra uma task no monitor"""
    return task_monitor.register_task(task_id, task_code, agent_slug)

def heartbeat(task_id: int):
    """Envia heartbeat para uma task"""
    task_monitor.heartbeat(task_id)

def complete_task(task_id: int, success: bool = True, error: str = None):
    """Marca task como completada"""
    task_monitor.complete_task(task_id, success, error)


# Exemplo de uso
if __name__ == "__main__":
    async def main():
        monitor = TaskMonitor()
        await monitor.start()
        
        # Mantém rodando
        while not monitor.shutdown_requested:
            await asyncio.sleep(1)
    
    asyncio.run(main())
