#!/usr/bin/env python3
"""
Agent Dashboard - Sistema de Monitoramento dos 3 Super-Agentes
Visualiza status, atividades e loads em tempo real
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

class AgentDashboard:
    def __init__(self):
        self.agents = {
            "O Marketeiro": {
                "level": "Operator",
                "status": "Active",
                "load": 0,
                "current_task": None,
                "last_activity": None,
                "specialties": ["Copywriting", "Paid Media", "Social Media"]
            },
            "O Dev": {
                "level": "Operator", 
                "status": "Active",
                "load": 0,
                "current_task": None,
                "last_activity": None,
                "specialties": ["Fullstack", "DevOps", "AI Integration"]
            },
            "O Executivo": {
                "level": "Autonomous",
                "status": "Active",
                "load": 0,
                "current_task": None,
                "last_activity": None,
                "specialties": ["Strategy", "Operations", "Management"]
            }
        }
        self.activity_log = []
        self.projects = {}
    
    def render(self):
        """Renderiza dashboard no terminal"""
        print("=" * 60)
        print("  DUNDER MIFFLIN - Agent Dashboard")
        print("=" * 60)
        print()
        
        # Active Agents
        print("┌─ Active Agents ─" + "─" * 42 + "┐")
        for name, data in self.agents.items():
            status_emoji = "🟢" if data["status"] == "Active" else "🟡" if data["status"] == "Busy" else "🔴"
            load_bar = "█" * int(data["load"] / 10) + "░" * (10 - int(data["load"] / 10))
            
            print(f"│                                                           │")
            print(f"│ {status_emoji} {name:<15} Level: {data['level']:<12}          │")
            print(f"│    Load: [{load_bar}] {data['load']}%                      │")
            
            if data["current_task"]:
                print(f"│    Task: {data['current_task'][:35]:<35}     │")
            
            if data["last_activity"]:
                mins_ago = (datetime.now() - data["last_activity"]).seconds // 60
                print(f"│    Last: {mins_ago} min ago                                 │")
        
        print(f"│                                                           │")
        print("└─" + "─" * 58 + "┘")
        print()
        
        # Recent Activity
        print("┌─ Recent Activity (Last 24h) ─" + "─" * 29 + "┐")
        recent = [a for a in self.activity_log 
                  if datetime.now() - a["timestamp"] < timedelta(hours=24)]
        
        if recent:
            for activity in recent[-8:]:  # Últimas 8 atividades
                time_str = activity["timestamp"].strftime("%H:%M")
                agent = activity["agent"][:12]
                action = activity["action"][:25]
                print(f"│ {time_str}  {agent:<12}  {action:<25}     │")
        else:
            print(f"│                                                           │")
            print(f"│  No recent activity                                       │")
        
        print(f"│                                                           │")
        print("└─" + "─" * 58 + "┘")
        print()
        
        # Project Status
        print("┌─ Project Status ─" + "─" * 41 + "┐")
        if self.projects:
            for name, data in self.projects.items():
                progress = int(data.get("progress", 0))
                bar = "█" * int(progress / 5) + "░" * (20 - int(progress / 5))
                print(f"│                                                           │")
                print(f"│ {name[:20]:<20}  [{bar}] {progress}%          │")
        else:
            print(f"│                                                           │")
            print(f"│  No active projects                                       │")
        
        print(f"│                                                           │")
        print("└─" + "─" * 58 + "┘")
        print()
    
    def log_activity(self, agent, action, project=None, details=None):
        """Registra atividade no log"""
        entry = {
            "timestamp": datetime.now(),
            "agent": agent,
            "action": action,
            "project": project,
            "details": details
        }
        self.activity_log.append(entry)
        
        # Atualiza last activity do agente
        if agent in self.agents:
            self.agents[agent]["last_activity"] = datetime.now()
        
        # Salva em arquivo
        self._save_log(entry)
    
    def update_agent_status(self, agent, status, load=None, current_task=None):
        """Atualiza status de um agente"""
        if agent in self.agents:
            self.agents[agent]["status"] = status
            if load is not None:
                self.agents[agent]["load"] = max(0, min(100, load))
            if current_task is not None:
                self.agents[agent]["current_task"] = current_task
    
    def update_project(self, name, progress, status="Active"):
        """Atualiza status de projeto"""
        self.projects[name] = {
            "progress": progress,
            "status": status,
            "last_updated": datetime.now()
        }
    
    def _save_log(self, entry):
        """Salva log em arquivo"""
        log_dir = Path("./projects/dunder-mifflin/agents/super/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"activity-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        
        with open(log_file, "a") as f:
            # Converte timestamp para string
            entry_copy = entry.copy()
            entry_copy["timestamp"] = entry_copy["timestamp"].isoformat()
            f.write(json.dumps(entry_copy) + "\n")
    
    def performance_review(self, agent, period_days=30):
        """Gera relatório de performance"""
        since = datetime.now() - timedelta(days=period_days)
        
        activities = [a for a in self.activity_log 
                     if a["agent"] == agent and a["timestamp"] > since]
        
        completed = len([a for a in activities if "completed" in a["action"].lower()])
        
        print(f"\n{'='*60}")
        print(f"  PERFORMANCE REVIEW - {agent}")
        print(f"{'='*60}")
        print(f"Period: Last {period_days} days")
        print(f"Total Activities: {len(activities)}")
        print(f"Tasks Completed: {completed}")
        
        if activities:
            # Calcula rating simulado (1-5)
            rating = min(5, max(1, completed / 5))
            print(f"Performance Rating: {rating:.1f}/5.0")
            
            if rating >= 4.5:
                print("Status: EXCEEDS EXPECTATIONS - Consider up-level")
            elif rating >= 3.5:
                print("Status: MEETS EXPECTATIONS - Maintain level")
            elif rating >= 2.5:
                print("Status: PARTIAL - Action plan needed")
            else:
                print("Status: BELOW EXPECTATIONS - Down-level or retrain")
        
        print(f"{'='*60}\n")

# Singleton
dashboard = AgentDashboard()

def main():
    """Demo do dashboard"""
    dash = AgentDashboard()
    
    # Simula algumas atividades
    dash.update_agent_status("O Marketeiro", "Active", 75, "Campaign X")
    dash.update_agent_status("O Dev", "Active", 60, "Feature Y")
    dash.update_agent_status("O Executivo", "Active", 40, "Reviewing")
    
    dash.log_activity("O Marketeiro", "Completed blog post draft", "Content Q1")
    dash.log_activity("O Dev", "Deployed API endpoint", "Project Alpha")
    dash.log_activity("O Executivo", "Approved Q2 budget")
    
    dash.update_project("Project Alpha", 80)
    dash.update_project("Project Beta", 50)
    
    # Renderiza
    dash.render()
    
    # Performance review
    dash.performance_review("O Marketeiro")

if __name__ == "__main__":
    main()
