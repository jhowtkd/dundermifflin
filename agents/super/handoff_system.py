#!/usr/bin/env python3
"""
Agent Handoff System - Coordenação entre O Marketeiro, O Dev e O Executivo
"""

import json
from datetime import datetime
from pathlib import Path

class HandoffSystem:
    def __init__(self):
        self.handoffs_dir = Path("./projects/dunder-mifflin/agents/super/handoffs")
        self.handoffs_dir.mkdir(parents=True, exist_ok=True)
    
    def create_handoff(self, from_agent, to_agent, task_type, context, deliverables, 
                      timeline, priority="Medium", success_criteria=None):
        """
        Cria um handoff entre agentes
        
        Args:
            from_agent: Agente solicitante (ex: "O Marketeiro")
            to_agent: Agente executor (ex: "O Dev")
            task_type: Tipo de tarefa (ex: "landing-page", "api-integration")
            context: Contexto completo (string)
            deliverables: Lista de entregáveis
            timeline: String com deadline
            priority: Low/Medium/High
            success_criteria: Lista de critérios de sucesso
        """
        
        handoff_id = f"HANDOFF-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        handoff = {
            "id": handoff_id,
            "from": from_agent,
            "to": to_agent,
            "task_type": task_type,
            "context": context,
            "deliverables": deliverables,
            "timeline": timeline,
            "priority": priority,
            "success_criteria": success_criteria or [],
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
            "output": None,
            "quality_rating": None
        }
        
        # Salva handoff
        handoff_file = self.handoffs_dir / f"{handoff_id}.json"
        with open(handoff_file, "w") as f:
            json.dump(handoff, f, indent=2)
        
        print(f"✅ Handoff criado: {handoff_id}")
        print(f"   De: {from_agent}")
        print(f"   Para: {to_agent}")
        print(f"   Task: {task_type}")
        print(f"   Prioridade: {priority}")
        print(f"   Timeline: {timeline}")
        
        return handoff_id
    
    def complete_handoff(self, handoff_id, output, quality_rating=None):
        """
        Completa um handoff
        
        Args:
            handoff_id: ID do handoff
            output: Output entregue
            quality_rating: Rating opcional (1-5)
        """
        handoff_file = self.handoffs_dir / f"{handoff_id}.json"
        
        if not handoff_file.exists():
            print(f"❌ Handoff {handoff_id} não encontrado")
            return False
        
        with open(handoff_file, "r") as f:
            handoff = json.load(f)
        
        handoff["status"] = "completed"
        handoff["completed_at"] = datetime.now().isoformat()
        handoff["output"] = output
        handoff["quality_rating"] = quality_rating
        
        with open(handoff_file, "w") as f:
            json.dump(handoff, f, indent=2)
        
        print(f"✅ Handoff {handoff_id} completado")
        if quality_rating:
            print(f"   Rating: {quality_rating}/5")
        
        return True
    
    def list_pending(self, for_agent=None):
        """Lista handoffs pendentes"""
        pending = []
        
        for handoff_file in self.handoffs_dir.glob("HANDOFF-*.json"):
            with open(handoff_file) as f:
                handoff = json.load(f)
            
            if handoff["status"] == "pending":
                if for_agent is None or handoff["to"] == for_agent:
                    pending.append(handoff)
        
        return pending
    
    def get_stats(self):
        """Estatísticas de handoffs"""
        total = 0
        completed = 0
        pending = 0
        
        for handoff_file in self.handoffs_dir.glob("HANDOFF-*.json"):
            with open(handoff_file) as f:
                handoff = json.load(f)
            
            total += 1
            if handoff["status"] == "completed":
                completed += 1
            else:
                pending += 1
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "completion_rate": completed / total if total > 0 else 0
        }

# Funções de conveniência
handoff_system = HandoffSystem()

def request_help(from_agent, to_agent, task_description, **kwargs):
    """Shortcut para criar handoff"""
    return handoff_system.create_handoff(
        from_agent=from_agent,
        to_agent=to_agent,
        task_type=kwargs.get("task_type", "general"),
        context=task_description,
        deliverables=kwargs.get("deliverables", []),
        timeline=kwargs.get("timeline", "48 hours"),
        priority=kwargs.get("priority", "Medium"),
        success_criteria=kwargs.get("success_criteria", [])
    )

def main():
    """Demo do sistema de handoff"""
    
    # Exemplo 1: O Marketeiro pede ajuda ao O Dev
    print("=" * 60)
    print("EXEMPLO 1: Landing Page Request")
    print("=" * 60)
    
    handoff_id = handoff_system.create_handoff(
        from_agent="O Marketeiro",
        to_agent="O Dev",
        task_type="landing-page",
        context="""
Campanha de lançamento do novo produto precisa de landing page 
com formulário de captura de leads. Audience: profissionais de 
marketing, B2B. Tone: profissional mas moderno.

Referências:
- Competidor X: landing similar que converte bem
- Nossa brand guide: cores azul #0066CC e branco
        """,
        deliverables=[
            "Landing page HTML/CSS responsiva",
            "Formulário (nome, email, empresa)",
            "Integração com CRM via API",
            "Meta tags para SEO e social",
            "Testes em mobile e desktop"
        ],
        timeline="48 hours (need by 2026-02-11)",
        priority="High",
        success_criteria=[
            "PageSpeed > 90",
            "Form submits without errors",
            "Data appears in CRM within 5 min",
            "Works on mobile (iOS + Android)"
        ]
    )
    
    print()
    
    # Exemplo 2: O Dev pede ajuda ao O Marketeiro
    print("=" * 60)
    print("EXEMPLO 2: Copy Request")
    print("=" * 60)
    
    handoff_id2 = handoff_system.create_handoff(
        from_agent="O Dev",
        to_agent="O Marketeiro",
        task_type="copywriting",
        context="""
Preciso de copy para mensagens de erro do sistema. Precisa ser:
- Clara (usuário entende o que aconteceu)
- Útil (sugere próximo passo)
- On-brand (tom profissional, não robótico)

Contexto técnico:
- Erros de validação de formulário
- Erros de conexão com API
- Erros de autenticação
- Erros genéricos (fallback)
        """,
        deliverables=[
            "Mensagens de erro para 10 cenários",
            "Variações de tom (formal vs friendly)",
            "Guidelines de quando usar cada uma"
        ],
        timeline="24 hours",
        priority="Medium"
    )
    
    print()
    
    # Lista pendentes para O Dev
    print("=" * 60)
    print("HANDOFFS PENDENTES PARA O DEV")
    print("=" * 60)
    
    pending = handoff_system.list_pending(for_agent="O Dev")
    for p in pending:
        print(f"\n📋 {p['id']}")
        print(f"   De: {p['from']}")
        print(f"   Task: {p['task_type']}")
        print(f"   Prioridade: {p['priority']}")
        print(f"   Deadline: {p['timeline']}")
    
    print()
    
    # Stats
    print("=" * 60)
    print("ESTATÍSTICAS")
    print("=" * 60)
    
    stats = handoff_system.get_stats()
    print(f"Total handoffs: {stats['total']}")
    print(f"Completados: {stats['completed']}")
    print(f"Pendentes: {stats['pending']}")
    print(f"Taxa de conclusão: {stats['completion_rate']:.1%}")

if __name__ == "__main__":
    main()
