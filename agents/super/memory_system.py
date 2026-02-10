#!/usr/bin/env python3
"""
Agent Memory System - Persistência de memória dos 3 Super-Agentes
Três camadas: Daily Notes, Long-Term Memory, Project Context
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

class MemorySystem:
    def __init__(self):
        self.memory_dir = Path("./projects/dunder-mifflin/agents/super/memory")
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.agents = ["O Marketeiro", "O Dev", "O Executivo"]
    
    def get_memory_path(self, agent, memory_type):
        """Retorna path para tipo de memória"""
        agent_slug = agent.lower().replace(" ", "-")
        
        if memory_type == "daily":
            return self.memory_dir / agent_slug / "daily-notes"
        elif memory_type == "longterm":
            return self.memory_dir / agent_slug / "long-term-memory.md"
        elif memory_type == "projects":
            return self.memory_dir / agent_slug / "projects"
        else:
            raise ValueError(f"Unknown memory type: {memory_type}")
    
    # =========================================================================
    # DAILY NOTES - Raw logs de cada dia
    # =========================================================================
    
    def add_daily_note(self, agent, note):
        """Adiciona nota ao daily notes"""
        daily_dir = self.get_memory_path(agent, "daily")
        daily_dir.mkdir(parents=True, exist_ok=True)
        
        today_file = daily_dir / f"{datetime.now().strftime('%Y-%m-%d')}.md"
        
        timestamp = datetime.now().strftime("%H:%M")
        entry = f"\n## {timestamp}\n{note}\n"
        
        with open(today_file, "a") as f:
            f.write(entry)
    
    def get_daily_notes(self, agent, date=None):
        """Recupera daily notes de um dia"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        daily_dir = self.get_memory_path(agent, "daily")
        note_file = daily_dir / f"{date}.md"
        
        if note_file.exists():
            with open(note_file) as f:
                return f.read()
        return None
    
    # =========================================================================
    # LONG-TERM MEMORY - Curated insights
    # =========================================================================
    
    def get_longterm_memory(self, agent):
        """Recupera long-term memory"""
        mem_file = self.get_memory_path(agent, "longterm")
        
        if mem_file.exists():
            with open(mem_file) as f:
                return f.read()
        
        # Template inicial
        return f"""# Long-Term Memory - {agent}

## What Works (Validated)
[Liste aqui o que funcionou bem]

## What Doesn't Work (Lessons)
[Liste aqui lições aprendidas]

## Preferences
[Como este agente prefere trabalhar]

## Relationships
[Como interage com outros agentes]
"""
    
    def update_longterm_memory(self, agent, section, content):
        """Atualiza seção da long-term memory"""
        mem_file = self.get_memory_path(agent, "longterm")
        mem_file.parent.mkdir(parents=True, exist_ok=True)
        
        current = self.get_longterm_memory(agent)
        
        # Simples append para demonstração
        # Em produção, faria parse markdown adequado
        with open(mem_file, "a") as f:
            f.write(f"\n\n## {section} - {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(content)
    
    # =========================================================================
    # PROJECT CONTEXT - Memória específica de projeto
    # =========================================================================
    
    def add_project_insight(self, agent, project, insight):
        """Adiciona insight a um projeto"""
        proj_dir = self.get_memory_path(agent, "projects") / project
        proj_dir.mkdir(parents=True, exist_ok=True)
        
        insights_file = proj_dir / "insights.md"
        
        with open(insights_file, "a") as f:
            f.write(f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"{insight}\n")
    
    def get_project_memory(self, agent, project):
        """Recupera memória de projeto"""
        proj_dir = self.get_memory_path(agent, "projects") / project
        insights_file = proj_dir / "insights.md"
        
        if insights_file.exists():
            with open(insights_file) as f:
                return f.read()
        return None
    
    # =========================================================================
    # BACKUP & RECOVERY
    # =========================================================================
    
    def backup(self, destination=None):
        """Faz backup de todas as memórias"""
        if destination is None:
            destination = self.memory_dir / "backups" / datetime.now().strftime("%Y%m%d-%H%M%S")
        
        destination = Path(destination)
        destination.mkdir(parents=True, exist_ok=True)
        
        # Copia toda a pasta memory
        shutil.copytree(self.memory_dir, destination / "memory", dirs_exist_ok=True)
        
        print(f"✅ Backup criado: {destination}")
        return destination
    
    def restore(self, backup_path):
        """Restaura memória de backup"""
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            print(f"❌ Backup não encontrado: {backup_path}")
            return False
        
        # Remove memória atual
        if self.memory_dir.exists():
            shutil.rmtree(self.memory_dir)
        
        # Restaura do backup
        shutil.copytree(backup_path / "memory", self.memory_dir)
        
        print(f"✅ Memória restaurada de: {backup_path}")
        return True
    
    def export_for_agent(self, agent):
        """Exporta toda memória de um agente (para recriação)"""
        agent_slug = agent.lower().replace(" ", "-")
        agent_mem_dir = self.memory_dir / agent_slug
        
        if not agent_mem_dir.exists():
            print(f"❌ Sem memória para {agent}")
            return None
        
        export_file = self.memory_dir / f"{agent_slug}-memory-export.json"
        
        export_data = {
            "agent": agent,
            "exported_at": datetime.now().isoformat(),
            "daily_notes": [],
            "longterm_memory": self.get_longterm_memory(agent),
            "projects": {}
        }
        
        # Coleta daily notes
        daily_dir = agent_mem_dir / "daily-notes"
        if daily_dir.exists():
            for note_file in daily_dir.glob("*.md"):
                with open(note_file) as f:
                    export_data["daily_notes"].append({
                        "date": note_file.stem,
                        "content": f.read()
                    })
        
        # Coleta projetos
        proj_dir = agent_mem_dir / "projects"
        if proj_dir.exists():
            for project in proj_dir.iterdir():
                if project.is_dir():
                    insights = self.get_project_memory(agent, project.name)
                    if insights:
                        export_data["projects"][project.name] = insights
        
        with open(export_file, "w") as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✅ Memória exportada: {export_file}")
        return export_file
    
    def import_for_agent(self, agent, export_file):
        """Importa memória para recriar agente"""
        with open(export_file) as f:
            data = json.load(f)
        
        agent_slug = agent.lower().replace(" ", "-")
        agent_mem_dir = self.memory_dir / agent_slug
        agent_mem_dir.mkdir(parents=True, exist_ok=True)
        
        # Restaura daily notes
        for note in data.get("daily_notes", []):
            daily_dir = agent_mem_dir / "daily-notes"
            daily_dir.mkdir(exist_ok=True)
            
            note_file = daily_dir / f"{note['date']}.md"
            with open(note_file, "w") as f:
                f.write(note["content"])
        
        # Restaura long-term memory
        longterm_file = agent_mem_dir / "long-term-memory.md"
        with open(longterm_file, "w") as f:
            f.write(data.get("longterm_memory", ""))
        
        # Restaura projetos
        for proj_name, insights in data.get("projects", {}).items():
            proj_dir = agent_mem_dir / "projects" / proj_name
            proj_dir.mkdir(parents=True, exist_ok=True)
            
            insights_file = proj_dir / "insights.md"
            with open(insights_file, "w") as f:
                f.write(insights)
        
        print(f"✅ Memória importada para {agent}")
        return True

# Singleton
memory_system = MemorySystem()

def main():
    """Demo do sistema de memória"""
    
    mem = MemorySystem()
    
    print("=" * 60)
    print("SISTEMA DE MEMÓRIA - DEMO")
    print("=" * 60)
    
    # Adiciona daily notes
    print("\n1. Adicionando Daily Notes...")
    mem.add_daily_note("O Marketeiro", "Started campaign for Product X")
    mem.add_daily_note("O Marketeiro", "Completed competitive analysis")
    mem.add_daily_note("O Dev", "Deployed new API endpoint")
    
    # Atualiza long-term memory
    print("\n2. Atualizando Long-Term Memory...")
    mem.update_longterm_memory("O Marketeiro", "What Works", 
        "- TikTok hooks with 'mistakes' perform 3x better\n- Tuesday 10am posts get most engagement")
    
    # Adiciona project insight
    print("\n3. Adicionando Project Insight...")
    mem.add_project_insight("O Marketeiro", "Q1-Growth", 
        "Audience prefers 'how-to' content over 'why' content")
    
    # Recupera dados
    print("\n4. Recuperando Memória...")
    
    daily = mem.get_daily_notes("O Marketeiro")
    if daily:
        print("\nDaily Notes (O Marketeiro):")
        print(daily[:200] + "...")
    
    longterm = mem.get_longterm_memory("O Marketeiro")
    print("\nLong-Term Memory (O Marketeiro):")
    print(longterm[:200] + "...")
    
    proj_mem = mem.get_project_memory("O Marketeiro", "Q1-Growth")
    if proj_mem:
        print("\nProject Memory (Q1-Growth):")
        print(proj_mem[:200] + "...")
    
    # Backup
    print("\n5. Criando Backup...")
    backup_path = mem.backup()
    
    # Export
    print("\n6. Exportando Memória...")
    export_file = mem.export_for_agent("O Marketeiro")
    
    print("\n" + "=" * 60)
    print("Demo completo!")
    print("=" * 60)

if __name__ == "__main__":
    main()
