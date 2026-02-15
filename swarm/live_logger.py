#!/usr/bin/env python3
"""
Live Logger - Reporta logs em tempo real pro Dashboard
"""

import os
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import json

@dataclass
class LogEntry:
    timestamp: str
    agent: str
    level: str  # DEBUG, INFO, STEP, WARN, ERROR, SUCCESS
    message: str
    step_name: Optional[str] = None
    step_status: Optional[str] = None  # started, running, completed, failed
    context: Optional[Dict[str, Any]] = None
    mission_id: Optional[str] = None

class LiveLogger:
    """Logger que envia pro dashboard em tempo real via Convex"""
    
    def __init__(self, convex_url: Optional[str] = None):
        self.convex_url = convex_url or os.getenv("CONVEX_URL")
        self.enabled = self.convex_url is not None
        self.session = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Lazy init da sessão HTTP"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _send_to_convex(self, mutation: str, args: Dict) -> bool:
        """Envia mutation pro Convex"""
        if not self.enabled or not self.convex_url:
            return False
        
        try:
            session = await self._get_session()
            url = f"{self.convex_url}/api/mutation"
            
            payload = {
                "path": mutation,
                "args": args
            }
            
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                return resp.status == 200
        except Exception as e:
            print(f"⚠️ Dashboard log failed: {e}")
            return False
    
    async def log(self, agent: str, level: str, message: str, 
                  context: Dict[str, Any] = None, mission_id: str = None):
        """Log genérico"""
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            agent=agent,
            level=level,
            message=message,
            context=context,
            mission_id=mission_id
        )
        
        # Envia pro dashboard
        await self._send_to_convex("activityLogs:create", {
            "timestamp": entry.timestamp,
            "agent": agent,
            "action": f"[{level}] {message}",
            "metadata": {
                "level": level,
                "context": context or {},
                "mission_id": mission_id
            }
        })
        
        # Print local também
        emoji = {
            "DEBUG": "🐛",
            "INFO": "ℹ️",
            "STEP": "▶️",
            "WARN": "⚠️",
            "ERROR": "❌",
            "SUCCESS": "✅"
        }.get(level, "•")
        
        print(f"{emoji} [{agent}] {message}")
        
        return entry
    
    async def step(self, agent: str, step_name: str, status: str, 
                   details: Dict[str, Any] = None, mission_id: str = None):
        """Log de step específico (started, running, completed, failed)"""
        level = {
            "started": "STEP",
            "running": "STEP",
            "completed": "SUCCESS",
            "failed": "ERROR",
            "skipped": "WARN"
        }.get(status, "INFO")
        
        emoji_status = {
            "started": "🚀",
            "running": "⏳",
            "completed": "✅",
            "failed": "❌",
            "skipped": "⏭️"
        }.get(status, "•")
        
        message = f"{emoji_status} {step_name}: {status}"
        if details:
            detail_str = ", ".join(f"{k}={v}" for k, v in details.items() if v is not None)
            if detail_str:
                message += f" ({detail_str})"
        
        entry = await self.log(
            agent=agent,
            level=level,
            message=message,
            context={"step_name": step_name, "step_status": status, **(details or {})},
            mission_id=mission_id
        )
        
        entry.step_name = step_name
        entry.step_status = status
        
        return entry
    
    async def debug(self, agent: str, message: str, context: Dict = None, mission_id: str = None):
        """Log de debug"""
        return await self.log(agent, "DEBUG", message, context, mission_id)
    
    async def info(self, agent: str, message: str, context: Dict = None, mission_id: str = None):
        """Log de info"""
        return await self.log(agent, "INFO", message, context, mission_id)
    
    async def warn(self, agent: str, message: str, context: Dict = None, mission_id: str = None):
        """Log de warning"""
        return await self.log(agent, "WARN", message, context, mission_id)
    
    async def error(self, agent: str, message: str, context: Dict = None, mission_id: str = None):
        """Log de erro"""
        return await self.log(agent, "ERROR", message, context, mission_id)
    
    async def success(self, agent: str, message: str, context: Dict = None, mission_id: str = None):
        """Log de sucesso"""
        return await self.log(agent, "SUCCESS", message, context, mission_id)
    
    async def close(self):
        """Fecha sessão HTTP"""
        if self.session:
            await self.session.close()
            self.session = None


# Singleton global
_logger = None

def get_logger() -> LiveLogger:
    """Retorna instância global do logger"""
    global _logger
    if _logger is None:
        _logger = LiveLogger()
    return _logger


# Funções síncronas de conveniência (para uso em código não-async)
import threading

def _run_async(coro):
    """Helper para rodar coro em contexto síncrono"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Se já tem loop rodando (dentro de async), agenda task
            asyncio.create_task(coro)
        else:
            # Se não tem loop, roda direto
            loop.run_until_complete(coro)
    except RuntimeError:
        # Sem loop, cria novo
        asyncio.run(coro)

def log_sync(agent: str, level: str, message: str, context: Dict = None, mission_id: str = None):
    """Log síncrono (bloqueante)"""
    logger = get_logger()
    _run_async(logger.log(agent, level, message, context, mission_id))

def step_sync(agent: str, step_name: str, status: str, details: Dict = None, mission_id: str = None):
    """Step log síncrono"""
    logger = get_logger()
    _run_async(logger.step(agent, step_name, status, details, mission_id))


if __name__ == "__main__":
    # Teste
    async def test():
        logger = LiveLogger()
        await logger.step("deployer", "detect_platform", "started", mission_id="test-123")
        await asyncio.sleep(0.5)
        await logger.step("deployer", "detect_platform", "completed", {"platform": "vercel"}, mission_id="test-123")
        await asyncio.sleep(0.5)
        await logger.step("deployer", "build", "started", mission_id="test-123")
        await asyncio.sleep(1)
        await logger.step("deployer", "build", "completed", {"duration": 12.5}, mission_id="test-123")
        await logger.close()
    
    asyncio.run(test())
