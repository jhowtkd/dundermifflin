#!/usr/bin/env python3
"""
Claw Skill Dispatcher - Detecta e usa skills automaticamente
"""

import os
import sys
import importlib
from pathlib import Path
from typing import Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

class SkillWrapper:
    """Wrapper padronizado para skills"""
    
    def __init__(self, name: str, module_path: str, execute_func: str = None):
        self.name = name
        self.module_path = module_path
        self.execute_func = execute_func or "execute"
        self._module = None
    
    def load(self):
        """Lazy load do módulo"""
        if self._module is None:
            try:
                self._module = importlib.import_module(self.module_path)
            except Exception as e:
                print(f"⚠️ Erro carregando skill {self.name}: {e}")
        return self._module
    
    async def execute(self, **kwargs) -> Any:
        """Executa a skill"""
        mod = self.load()
        if mod and hasattr(mod, self.execute_func):
            func = getattr(mod, self.execute_func)
            if asyncio.iscoroutinefunction(func):
                return await func(**kwargs)
            return func(**kwargs)
        return None


class SkillDispatcher:
    """
    Detecta qual skill usar baseado na intenção da task
    """
    
    # Mapeamento de keywords -> skill
    SKILL_MAP = {
        'weather': {
            'keywords': ['tempo', 'clima', 'previsão', 'weather', 'forecast', 'temperatura'],
            'module': 'skills.weather.skill',
            'description': 'Previsão do tempo'
        },
        'github': {
            'keywords': ['github', 'pr', 'pull request', 'commit', 'branch', 'merge', 'repo'],
            'module': 'skills.github.skill',
            'description': 'Operações GitHub'
        },
        'clickup': {
            'keywords': ['clickup', 'task', 'tarefa', 'projeto', 'sprint'],
            'module': 'skills.clickup.skill',
            'description': 'Gestão ClickUp'
        },
        'gog': {
            'keywords': ['email', 'gmail', 'calendario', 'calendar', 'drive', 'docs'],
            'module': 'skills.gog.skill',
            'description': 'Google Workspace'
        },
        'filesystem': {
            'keywords': ['arquivo', 'pasta', 'file', 'folder', 'buscar', 'find', 'listar'],
            'module': 'skills.filesystem.skill',
            'description': 'Operações de arquivo'
        },
        'deploy': {
            'keywords': ['deploy', 'publicar', 'subir', 'vercel', 'railway'],
            'module': 'swarm.agents.deployer',
            'execute_func': 'handle_command',
            'description': 'Deploy de projetos'
        }
    }
    
    def __init__(self):
        self.skills: Dict[str, SkillWrapper] = {}
        self._load_skills()
    
    def _load_skills(self):
        """Carrega todas as skills disponíveis"""
        for skill_id, config in self.SKILL_MAP.items():
            self.skills[skill_id] = SkillWrapper(
                name=skill_id,
                module_path=config['module'],
                execute_func=config.get('execute_func', 'execute')
            )
    
    def detect_skill(self, task: str) -> Optional[str]:
        """
        Detecta qual skill usar baseado na task
        Retorna skill_id ou None
        """
        task_lower = task.lower()
        
        scores = {}
        for skill_id, config in self.SKILL_MAP.items():
            score = 0
            for keyword in config['keywords']:
                if keyword in task_lower:
                    score += 1
            if score > 0:
                scores[skill_id] = score
        
        # Retorna a skill com maior score
        if scores:
            return max(scores, key=scores.get)
        return None
    
    async def execute_with_skill(self, task: str, **kwargs) -> Any:
        """
        Detecta skill e executa
        """
        skill_id = self.detect_skill(task)
        
        if not skill_id:
            return {
                'success': False,
                'error': 'Nenhuma skill detectada para esta task',
                'task': task
            }
        
        skill = self.skills.get(skill_id)
        if not skill:
            return {
                'success': False,
                'error': f'Skill {skill_id} não encontrada',
                'task': task
            }
        
        try:
            result = await skill.execute(task=task, **kwargs)
            return {
                'success': True,
                'skill': skill_id,
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'skill': skill_id,
                'error': str(e),
                'task': task
            }
    
    def list_skills(self) -> str:
        """Lista skills disponíveis"""
        lines = ["🔧 **Skills Disponíveis:**\n"]
        for skill_id, config in self.SKILL_MAP.items():
            lines.append(f"• **{skill_id}**: {config['description']}")
            lines.append(f"  Keywords: {', '.join(config['keywords'][:3])}...")
        return "\n".join(lines)


# Singleton
_dispatcher = None

def get_skill_dispatcher() -> SkillDispatcher:
    """Retorna instância global"""
    global _dispatcher
    if _dispatcher is None:
        _dispatcher = SkillDispatcher()
    return _dispatcher


if __name__ == "__main__":
    async def test():
        dispatcher = get_skill_dispatcher()
        
        test_tasks = [
            "Qual o tempo hoje?",
            "Faz deploy do dashboard",
            "Lista meus emails",
            "Cria uma função de teste"
        ]
        
        for task in test_tasks:
            skill = dispatcher.detect_skill(task)
            print(f"'{task}' -> Skill: {skill}")
    
    import asyncio
    asyncio.run(test())
