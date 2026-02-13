"""
Integração Ralph Swarm → Super Agents
Permite que O Marketeiro, O Dev e O Executivo consultem as 52 skills documentadas.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from knowledge.ralph_swarm_loader import get_knowledge, find_by_tag, find_by_agent


class RalphSwarmIntegration:
    """
    Interface para Super Agents usarem skills do Ralph Swarm.
    
    Usage:
        from ralph_swarm_integration import swarm_skills
        
        # O Marketeiro precisa de copywriting
        skills = swarm_skills.for_copywriting()
        
        # O Dev precisa debugar
        skills = swarm_skills.for_debugging()
        
        # Buscar skill específica
        skill = swarm_skills.get_skill('MAY-002')  # Framework AIDA
    """
    
    def __init__(self):
        self.kb = get_knowledge()
    
    def for_copywriting(self):
        """Skills de copywriting para O Marketeiro."""
        return {
            'maya_skills': self.kb.get_agent_skills('Maya'),
            'frameworks': ['AIDA', 'PAS', '4P', 'FAB'],
            'tags': ['copywriting', 'headlines', 'email-marketing']
        }
    
    def for_research(self):
        """Skills de research para O Marketeiro e O Executivo."""
        return {
            'scout_skills': self.kb.get_agent_skills('Scout'),
            'frameworks': ['ESTRATEGIC', 'Competitor Tracking'],
            'tags': ['research', 'analysis', 'monitoring']
        }
    
    def for_debugging(self):
        """Skills de debugging para O Dev."""
        return {
            'max_skills': self.kb.get_agent_skills('Max'),
            'frameworks': ['DEBUG', '5 Fases'],
            'tags': ['debugging', 'security', 'testing']
        }
    
    def for_analytics(self):
        """Skills de analytics para todos."""
        return {
            'tracker_skills': self.kb.get_agent_skills('Tracker'),
            'frameworks': ['Processo de Análise', 'Sistema de Alertas'],
            'tags': ['analysis', 'metrics', 'dashboard']
        }
    
    def for_coordination(self):
        """Skills de coordenação para O Executivo."""
        return {
            'ralph_skills': self.kb.get_agent_skills('Ralph'),
            'frameworks': ['Chain-of-Thought', 'Swarm vs Single', 'Síntese 4 Camadas'],
            'tags': ['coordination', 'synthesis', 'decision-making']
        }
    
    def get_skill(self, skill_id):
        """Busca skill específica pelo ID (ex: 'MAY-002', 'RAL-007')."""
        for agent_name in ['Ralph', 'Scout', 'Max', 'Maya', 'Tracker', 'Watcher']:
            for skill in self.kb.get_agent_skills(agent_name):
                if skill.get('id') == skill_id:
                    return skill
        return None
    
    def get_framework(self, name):
        """Busca framework pelo nome."""
        frameworks = self.kb.get_frameworks()
        for fw in frameworks:
            if name.lower() in fw.get('name', '').lower():
                return fw
        return None
    
    def suggest_skills_for_task(self, task_description):
        """
        Sugere skills relevantes baseado na descrição da tarefa.
        
        Exemplo:
            suggest_skills_for_task("criar landing page")
            → Retorna skills de Maya (copy) e Max (build)
        """
        task_lower = task_description.lower()
        suggestions = []
        
        # Keywords mapping
        if any(k in task_lower for k in ['copy', 'email', 'headline', 'ad', 'post']):
            suggestions.extend(self.kb.get_agent_skills('Maya'))
        
        if any(k in task_lower for k in ['research', 'análise', 'competidor', 'mercado']):
            suggestions.extend(self.kb.get_agent_skills('Scout'))
        
        if any(k in task_lower for k in ['code', 'debug', 'build', 'dev', 'api']):
            suggestions.extend(self.kb.get_agent_skills('Max'))
        
        if any(k in task_lower for k in ['métrica', 'dashboard', 'analytics', 'kpi']):
            suggestions.extend(self.kb.get_agent_skills('Tracker'))
        
        if any(k in task_lower for k in ['monitor', 'trend', 'alerta', 'observar']):
            suggestions.extend(self.kb.get_agent_skills('Watcher'))
        
        if any(k in task_lower for k in ['coordenar', 'orquestrar', 'sintetizar', 'decidir']):
            suggestions.extend(self.kb.get_agent_skills('Ralph'))
        
        return suggestions


# Instância global
swarm_skills = RalphSwarmIntegration()


# Funções de conveniência para uso direto
def get_copywriting_frameworks():
    """Retorna frameworks de copywriting disponíveis."""
    return swarm_skills.for_copywriting()

def get_debug_methodology():
    """Retorna metodologia DEBUG."""
    return swarm_skills.for_debugging()

def get_research_framework():
    """Retorna framework ESTRATEGIC."""
    return swarm_skills.for_research()

def suggest_for_task(task):
    """Sugere skills para uma tarefa."""
    return swarm_skills.suggest_skills_for_task(task)


if __name__ == "__main__":
    # Teste
    print("🧪 Testando integração Ralph Swarm...")
    print(f"Skills de copywriting: {len(swarm_skills.for_copywriting()['maya_skills'])}")
    print(f"Skills de debugging: {len(swarm_skills.for_debugging()['max_skills'])}")
    
    # Teste de sugestão
    task = "criar landing page para campanha"
    suggested = swarm_skills.suggest_skills_for_task(task)
    print(f"\nSugestões para '{task}': {len(suggested)} skills")
