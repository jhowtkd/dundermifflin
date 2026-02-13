"""
Ralph Swarm Skills Loader
Carrega e permite busca nas skills documentadas.
"""
import json
import os
from pathlib import Path

# Diretório base das skills
KNOWLEDGE_DIR = Path(__file__).parent
SKILLS_FILE = KNOWLEDGE_DIR / "ralph_swarm" / "ralph_swarm_skills_mapping.json"
RAG_SUMMARY_FILE = KNOWLEDGE_DIR / "ralph_swarm" / "ralph_swarm_rag_summary.json"


class RalphSwarmKnowledge:
    """Carrega e fornece acesso às skills do Ralph Swarm."""
    
    _instance = None
    _skills = None
    _rag_summary = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_data()
        return cls._instance
    
    def _load_data(self):
        """Carrega os dados JSON das skills."""
        try:
            with open(SKILLS_FILE, 'r', encoding='utf-8') as f:
                self._skills = json.load(f)
        except FileNotFoundError:
            self._skills = {"skills_by_agent": {}, "taxonomy": {}}
        
        try:
            with open(RAG_SUMMARY_FILE, 'r', encoding='utf-8') as f:
                self._rag_summary = json.load(f)
        except FileNotFoundError:
            self._rag_summary = {}
    
    def get_all_skills(self):
        """Retorna todas as skills."""
        return self._skills
    
    def get_agent_skills(self, agent_name):
        """
        Retorna skills de um agente específico.
        
        Args:
            agent_name: 'Ralph', 'Scout', 'Max', 'Maya', 'Tracker', 'Watcher'
        """
        agent_data = self._skills.get("skills_by_agent", {}).get(agent_name, {})
        return agent_data.get("skills", [])
    
    def find_by_tag(self, tag):
        """
        Busca skills por tag.
        
        Args:
            tag: Ex: 'analysis', 'research', 'copywriting', 'framework'
        """
        tags_index = self._skills.get("tags_index", {})
        skill_ids = tags_index.get(tag, [])
        
        # Buscar detalhes completos das skills
        results = []
        for agent_name, agent_data in self._skills.get("skills_by_agent", {}).items():
            for skill in agent_data.get("skills", []):
                if skill.get("id") in skill_ids:
                    results.append(skill)
        return results
    
    def find_by_category(self, category):
        """
        Busca skills por categoria.
        
        Args:
            category: 'tecnica', 'analitica', 'criativa', 'estrategica'
        """
        taxonomy = self._skills.get("taxonomy", {})
        by_category = taxonomy.get("by_category", {})
        return by_category.get(category, [])
    
    def get_skill_path(self, skill_id):
        """
        Retorna o caminho de dependências até uma skill.
        
        Args:
            skill_id: Ex: 'RAL-007', 'SCO-001'
        """
        relationships = self._skills.get("relationships", {})
        return relationships.get("dependency_chains", {}).get(skill_id, [])
    
    def get_agent_profile(self, agent_name):
        """
        Retorna o perfil de um agente.
        """
        profiles = self._rag_summary.get("agent_profiles", {})
        return profiles.get(agent_name, {})
    
    def get_frameworks(self, agent_name=None):
        """
        Retorna frameworks disponíveis.
        
        Args:
            agent_name: Opcional, filtra por agente
        """
        if agent_name:
            profile = self.get_agent_profile(agent_name)
            return profile.get("frameworks", [])
        
        # Todos os frameworks
        all_frameworks = []
        for profile in self._rag_summary.get("agent_profiles", {}).values():
            all_frameworks.extend(profile.get("frameworks", []))
        return all_frameworks
    
    def query_skills(self, agent=None, category=None, tag=None, complexity=None):
        """
        Query flexível por skills.
        
        Exemplos:
            kb.query_skills(agent='Maya', category='criativa')
            kb.query_skills(tag='analysis', complexity='alta')
        """
        results = []
        
        # Pegar skills por agente ou todos
        if agent:
            skills = self.get_agent_skills(agent)
        else:
            skills = []
            for agent_name, agent_data in self._skills.get("skills_by_agent", {}).items():
                skills.extend(agent_data.get("skills", []))
        
        # Filtrar
        for skill in skills:
            match = True
            
            if category and skill.get("category") != category:
                match = False
            
            if tag and tag not in skill.get("tags", []):
                match = False
            
            if complexity and skill.get("complexity") != complexity:
                match = False
            
            if match:
                results.append(skill)
        
        return results


# Instância singleton para uso fácil
_knowledge = None

def get_knowledge():
    """Retorna instância única do knowledge base."""
    global _knowledge
    if _knowledge is None:
        _knowledge = RalphSwarmKnowledge()
    return _knowledge


# Funções de conveniência
def load_skills():
    """Carrega todas as skills."""
    return get_knowledge().get_all_skills()

def find_by_agent(agent_name):
    """Busca skills por agente."""
    return get_knowledge().get_agent_skills(agent_name)

def find_by_tag(tag):
    """Busca skills por tag."""
    return get_knowledge().find_by_tag(tag)

def find_by_category(category):
    """Busca skills por categoria."""
    return get_knowledge().find_by_category(category)

def get_skill_path(skill_id):
    """Retorna caminho de dependências."""
    return get_knowledge().get_skill_path(skill_id)

def get_agent_profile(agent_name):
    """Retorna perfil do agente."""
    return get_knowledge().get_agent_profile(agent_name)


if __name__ == "__main__":
    # Teste
    kb = get_knowledge()
    print(f"Total de skills carregadas: {len(kb.get_all_skills().get('skills_by_agent', {}))} agentes")
    print(f"Skills do Ralph: {len(kb.get_agent_skills('Ralph'))}")
    print(f"Skills da Maya: {len(kb.get_agent_skills('Maya'))}")
    print(f"Frameworks disponíveis: {len(kb.get_frameworks())}")
