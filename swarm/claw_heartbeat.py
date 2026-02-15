#!/usr/bin/env python3
"""
Claw Heartbeat - Verificação gerencial periódica
Cron job que dispara o Claw pra verificar status e reportar
"""

import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from claw_coordinator import get_coordinator
from claw_telegram import send_to_user

class ClawHeartbeat:
    """
    Heartbeat gerencial - eu verifico o que precisa de atenção
    """
    
    def __init__(self):
        self.coordinator = get_coordinator()
        self.last_check = None
    
    async def run(self):
        """
        Executa verificação completa
        """
        print(f"🔍 Claw Heartbeat - {datetime.now().strftime('%H:%M')}")
        
        reports = []
        
        # 1. Verifica projetos
        project_report = await self._check_projects()
        if project_report:
            reports.append(project_report)
        
        # 2. Verifica deploys pendentes
        deploy_report = await self._check_pending_deploys()
        if deploy_report:
            reports.append(deploy_report)
        
        # 3. Verifica erros nos logs
        error_report = await self._check_errors()
        if error_report:
            reports.append(error_report)
        
        # 4. Verifica tasks atrasadas
        task_report = await self._check_overdue_tasks()
        if task_report:
            reports.append(task_report)
        
        # 5. Verifica PRs pendentes
        pr_report = await self._check_pending_prs()
        if pr_report:
            reports.append(pr_report)
        
        # Se tem algo importante, notifica
        if reports:
            await self._notify_user(reports)
        else:
            print("✅ Tudo em ordem")
        
        self.last_check = datetime.now()
    
    async def _check_projects(self) -> str:
        """Verifica status dos projetos"""
        try:
            from project_registry import get_registry
            registry = get_registry()
            projects = registry.list_projects()
            
            pending_deploy = []
            for p in projects:
                if p['ahead'] > 0 or p['modified']:
                    pending_deploy.append(f"• {p['name']}: {p['ahead']} commits ahead")
            
            if pending_deploy:
                return f"📦 Projetos com mudanças:\n" + "\n".join(pending_deploy)
            return None
        except Exception as e:
            print(f"⚠️ Erro check projects: {e}")
            return None
    
    async def _check_pending_deploys(self) -> str:
        """Verifica deploys pendentes"""
        # Por enquanto simulado, depois integra com deployer
        return None
    
    async def _check_errors(self) -> str:
        """Verifica erros recentes nos logs"""
        try:
            import subprocess
            result = subprocess.run(
                ['tail', '-n', '100', '/tmp/discord_bridge.log'],
                capture_output=True, text=True, timeout=10
            )
            
            errors = [line for line in result.stdout.split('\n') if 'ERROR' in line]
            recent_errors = errors[-5:]  # Últimos 5
            
            if recent_errors:
                return f"⚠️ {len(errors)} erros recentes nos logs"
            return None
        except:
            return None
    
    async def _check_overdue_tasks(self) -> str:
        """Verifica tasks atrasadas"""
        try:
            # Integração com ClickUp skill
            return None  # Por enquanto
        except:
            return None
    
    async def _check_pending_prs(self) -> str:
        """Verifica PRs pendentes"""
        try:
            # Integração com GitHub skill
            return None  # Por enquanto
        except:
            return None
    
    async def _notify_user(self, reports: list):
        """Notifica usuário com resumo"""
        message = f"🤖 **Claw Heartbeat - {datetime.now().strftime('%H:%M')}**\n\n"
        message += "\n\n".join(reports)
        message += "\n\nQuer que eu execute alguma ação? Responde com o número ou 'não'."
        
        # Salva no estado pra tracking de aprovação
        self.coordinator.pending_heartbeat = {
            'timestamp': datetime.now().isoformat(),
            'reports': reports,
            'message': message
        }
        
        print(f"📤 Notificação:\n{message}")
        return message


async def main():
    """Entry point pro cron"""
    heartbeat = ClawHeartbeat()
    await heartbeat.run()


if __name__ == "__main__":
    asyncio.run(main())
