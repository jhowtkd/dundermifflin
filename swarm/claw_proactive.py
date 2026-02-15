#!/usr/bin/env python3
"""
Claw Proactive Mode - Identifica problemas e propõe soluções
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

class ProactiveDetector:
    """
    Detecta problemas e oportunidades sem você pedir
    """
    
    def __init__(self):
        self.last_proactive_check = None
        self.silenced_until = None
        self.detected_issues: List[Dict] = []
    
    async def scan(self) -> List[Dict]:
        """
        Scan completo proativo
        Retorna lista de issues detectadas
        """
        issues = []
        
        # 1. Verifica se há silêncio ativo
        if self.silenced_until and datetime.now() < self.silenced_until:
            return []
        
        # 2. Verifica projetos com código não deployado
        code_issues = await self._check_undeployed_code()
        issues.extend(code_issues)
        
        # 3. Verifica tasks atrasadas
        task_issues = await self._check_overdue_tasks()
        issues.extend(task_issues)
        
        # 4. Verifica erros recorrentes
        error_issues = await self._check_recurring_errors()
        issues.extend(error_issues)
        
        # 5. Verifica oportunidades de melhoria
        improvement_issues = await self._check_improvements()
        issues.extend(improvement_issues)
        
        self.last_proactive_check = datetime.now()
        return issues
    
    async def _check_undeployed_code(self) -> List[Dict]:
        """Verifica código commitado mas não deployado"""
        issues = []
        try:
            from project_registry import get_registry
            registry = get_registry()
            projects = registry.list_projects()
            
            for p in projects:
                if p['ahead'] > 0 and p['ahead'] >= 3:  # 3+ commits sem deploy
                    issues.append({
                        'type': 'undeployed_code',
                        'severity': 'medium',
                        'project': p['name'],
                        'message': f"📦 {p['name']} tem {p['ahead']} commits não deployados",
                        'action': f"deploya o {p['name']}",
                        'auto_fixable': True
                    })
        except Exception as e:
            print(f"⚠️ Erro check undeployed: {e}")
        return issues
    
    async def _check_overdue_tasks(self) -> List[Dict]:
        """Verifica tasks atrasadas"""
        issues = []
        # Integração com ClickUp skill
        # Por enquanto simulado
        return issues
    
    async def _check_recurring_errors(self) -> List[Dict]:
        """Verifica erros que acontecem repetidamente"""
        issues = []
        try:
            import subprocess
            result = subprocess.run(
                ['tail', '-n', '500', '/tmp/discord_bridge.log'],
                capture_output=True, text=True, timeout=10
            )
            
            # Conta erros por tipo
            error_counts = {}
            for line in result.stdout.split('\n'):
                if 'ERROR' in line:
                    # Extrai tipo de erro (simplificado)
                    error_type = line.split(':')[-1][:50] if ':' in line else 'unknown'
                    error_counts[error_type] = error_counts.get(error_type, 0) + 1
            
            # Se algum erro aconteceu 5+ vezes
            for error_type, count in error_counts.items():
                if count >= 5:
                    issues.append({
                        'type': 'recurring_error',
                        'severity': 'high',
                        'message': f"⚠️ Erro recorrente ({count}x): {error_type[:50]}...",
                        'action': "analisa os logs de erro",
                        'auto_fixable': False
                    })
        except:
            pass
        return issues
    
    async def _check_improvements(self) -> List[Dict]:
        """Verifica oportunidades de melhoria"""
        issues = []
        
        # Verifica se tem muitos arquivos não commitados
        try:
            import subprocess
            result = subprocess.run(
                ['git', '-C', str(Path(__file__).parent.parent), 'status', '--porcelain'],
                capture_output=True, text=True, timeout=10
            )
            
            uncommitted = len([l for l in result.stdout.split('\n') if l.strip()])
            if uncommitted >= 10:
                issues.append({
                    'type': 'improvement',
                    'severity': 'low',
                    'message': f"💡 {uncommitted} arquivos não commitados. Quer que eu organize isso?",
                    'action': "commita as mudanças pendentes",
                    'auto_fixable': True
                })
        except:
            pass
        
        return issues
    
    def format_proactive_message(self, issues: List[Dict]) -> Optional[str]:
        """Formata mensagem proativa pro usuário"""
        if not issues:
            return None
        
        # Separa por severidade
        high = [i for i in issues if i['severity'] == 'high']
        medium = [i for i in issues if i['severity'] == 'medium']
        low = [i for i in issues if i['severity'] == 'low']
        
        message = f"🤖 **Detectei algumas coisas:**\n\n"
        
        if high:
            message += "🔴 **Urgente:**\n"
            for i, issue in enumerate(high[:2], 1):
                message += f"{i}. {issue['message']}\n"
            message += "\n"
        
        if medium:
            message += "🟡 **Atenção:**\n"
            for i, issue in enumerate(medium[:3], 1):
                message += f"{i}. {issue['message']}\n"
                if issue.get('auto_fixable'):
                    message += f"   → Posso executar: *\"{issue['action']}\"*\n"
            message += "\n"
        
        if low:
            message += "🟢 **Sugestões:**\n"
            for issue in low[:2]:
                message += f"• {issue['message']}\n"
            message += "\n"
        
        message += "Quer que eu execute alguma ação? (número da ação, 'todas', 'não', ou 'silencia 2h')"
        
        return message
    
    def silence(self, duration_hours: int = 2):
        """Silencia notificações proativas por X horas"""
        self.silenced_until = datetime.now() + timedelta(hours=duration_hours)
        return f"🔕 Modo proativo silenciado por {duration_hours}h. Só falo se for urgente."


# Integração com Claw Coordinator
class ClawProactiveMode:
    """
    Modo proativo do Claw - executa periodicamente
    """
    
    def __init__(self):
        self.detector = ProactiveDetector()
        self.enabled = True
    
    async def check_and_notify(self):
        """
        Verifica e notifica se necessário
        """
        if not self.enabled:
            return None
        
        issues = await self.detector.scan()
        
        if issues:
            return self.detector.format_proactive_message(issues)
        
        return None
    
    def disable(self):
        self.enabled = False
        return "🛑 Modo proativo desativado. Só executo quando você pedir."
    
    def enable(self):
        self.enabled = True
        return "✅ Modo proativo ativado. Vou te avisar quando detectar algo."


# Singleton
_proactive = None

def get_proactive_mode() -> ClawProactiveMode:
    """Retorna instância global"""
    global _proactive
    if _proactive is None:
        _proactive = ClawProactiveMode()
    return _proactive


if __name__ == "__main__":
    async def test():
        proactive = get_proactive_mode()
        message = await proactive.check_and_notify()
        if message:
            print(message)
        else:
            print("Nada detectado")
    
    import asyncio
    asyncio.run(test())
