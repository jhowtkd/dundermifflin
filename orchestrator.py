#!/usr/bin/env python3
"""
Orchestrator - Sistema de Orquestração Multi-Agente
Michael Scott (studio-producer) como Master Orquestrador
"""

"""
Orchestrator - Sistema de Orquestração Multi-Agente
Michael Scott (studio-producer) como Master Orquestrador
"""

import json
import sqlite3
import re
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Constantes
DB_PATH = Path(__file__).parent / "dunder_mifflin.db"
MASTER_AGENT_SLUG = "studio-producer"
DEFAULT_STEP_MINUTES = 15

DB_PATH = Path(__file__).parent / "dunder_mifflin.db"
MASTER_AGENT_SLUG = "studio-producer"

# Prompt do sistema para o Master Agent (Michael Scott)
MASTER_SYSTEM_PROMPT = """Você é Michael Scott, o Regional Manager da Dunder Mifflin.
Seu papel é coordenar uma equipe de agentes especialistas.

Ao receber uma tarefa:
1. Analise o objetivo e quebre em subtarefas claras
2. Selecione os agentes necessários da equipe
3. Defina a sequência de execução (quem faz o quê)
4. Estime tempo e recursos
5. Crie um plano detalhado para aprovação do usuário

IMPORTANTE: O usuário DEVE aprovar seu plano antes da execução.
Seja claro e objetivo na explicação da estratégia.

Retorne APENAS um JSON válido no formato:
{
    "objective": "Descrição clara do objetivo",
    "strategy": "Explicação da estratégia escolhida",
    "estimated_duration_minutes": 45,
    "steps": [
        {
            "order": 1,
            "agent_slug": "nome-do-agente",
            "agent_name": "Nome do Agente",
            "title": "Título da tarefa",
            "description": "Descrição detalhada do que fazer",
            "estimated_minutes": 15
        }
    ]
}"""


class Database:
    """Helper para acesso ao banco"""
    
    @staticmethod
    def get_connection():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    @staticmethod
    def generate_code(prefix: str) -> str:
        return f"{prefix}-{uuid.uuid4().hex[:12]}"


class MasterAgent:
    """
    Michael Scott (studio-producer) - O Orquestrador Central
    
    Executa via Clawdbot internamente (sem API key externa).
    O Kimi 2.5 Thinking é chamado através do sistema Clawdbot.
    """
    
    AGENT_SLUG = MASTER_AGENT_SLUG
    
    def __init__(self):
        self.available_agents = self._load_available_agents()
        self.master_id = self._get_master_id()
    
    def _get_master_id(self) -> Optional[int]:
        """Busca ID do agente master"""
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM agents WHERE slug = ?", (self.AGENT_SLUG,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None
    
    def _load_available_agents(self) -> List[Dict]:
        """Carrega todos os agentes disponíveis"""
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, slug, name, role, description, capabilities, avatar_emoji
            FROM agents WHERE is_active = 1
            ORDER BY name
        """)
        agents = [dict(row) for row in cur.fetchall()]
        conn.close()
        return agents
    
    def create_plan(self, service_id: int, title: str, objective: str, 
                    input_data: Dict = None) -> Dict:
        """
        Analisa request e gera plano estruturado
        
        Nota: A chamada ao LLM (Kimi 2.5) é feita via Clawdbot,
        que gerencia a integração internamente.
        """
        # Busca informações do serviço
        service = self._get_service(service_id)
        if not service:
            raise ValueError(f"Serviço não encontrado: {service_id}")
        
        # Constrói o prompt para o LLM
        prompt = self._build_planning_prompt(service, title, objective, input_data)
        
        # Chama o LLM (simulado - na prática seria via Clawdbot)
        plan_data = self._call_llm(prompt)
        
        # Salva o plano no banco
        plan = self._save_execution_plan(service_id, title, objective, plan_data)
        
        # Cria mensagem do Master sobre o plano
        self._create_master_message(plan['id'], 
            f"📋 Plano criado para: {title}\n\n"
            f"Estratégia: {plan_data.get('strategy', 'N/A')}\n"
            f"Tempo estimado: {plan_data.get('estimated_duration_minutes', 0)} minutos")
        
        return plan
    
    def _get_service(self, service_id: int) -> Optional[Dict]:
        """Busca serviço por ID"""
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM services WHERE id = ?", (service_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def _build_planning_prompt(self, service: Dict, title: str, 
                               objective: str, input_data: Dict) -> str:
        """Constrói o prompt para o LLM"""
        agents_info = "\n".join([
            f"- {a['slug']}: {a['name']} - {a['role']}"
            for a in self.available_agents
            if a['slug'] in json.loads(service.get('agent_sequence', '[]'))
        ])
        
        prompt = f"""{MASTER_SYSTEM_PROMPT}

SERVIÇO: {service['name']}
TÍTULO: {title}
OBJETIVO: {objective}
INPUTS: {json.dumps(input_data or {}, ensure_ascii=False)}

AGENTES DISPONÍVEIS PARA ESTE SERVIÇO:
{agents_info}

Crie um plano detalhado para esta tarefa."""
        
        return prompt
    
    def _call_llm(self, prompt: str) -> Dict:
        """
        Chama o LLM (Kimi 2.5) via Clawdbot
        
        Na implementação real, isto seria uma chamada ao sistema Clawdbot.
        Por enquanto, simulamos uma resposta estruturada.
        """
        # Simulação: retorna um plano estruturado baseado no prompt
        # Na implementação real, substituir por chamada ao Clawdbot
        
        # Extrai informações do prompt para criar plano realista
        service_match = re.search(r'SERVIÇO:\s*(.+)', prompt)
        objective_match = re.search(r'OBJETIVO:\s*(.+)', prompt)
        
        service_name = service_match.group(1).strip() if service_match else "Tarefa"
        objective = objective_match.group(1).strip() if objective_match else "Executar tarefa"
        
        # Cria steps baseados nos agentes mencionados
        agent_slugs = re.findall(r'-\s*(\w+):', prompt)
        
        steps = []
        for idx, slug in enumerate(agent_slugs, 1):
            agent = next((a for a in self.available_agents if a['slug'] == slug), None)
            if agent:
                steps.append({
                    "order": idx,
                    "agent_slug": slug,
                    "agent_name": agent['name'],
                    "title": f"Executar como {agent['name']}",
                    "description": f"{agent['role']} - {agent.get('description', 'Tarefa especializada')}",
                    "estimated_minutes": DEFAULT_STEP_MINUTES
                })
        
        return {
            "objective": objective,
            "strategy": f"Vou utilizar {len(steps)} agentes especialistas em sequência para garantir qualidade. Cada agente foca em sua especialidade.",
            "estimated_duration_minutes": len(steps) * 15,
            "steps": steps
        }
    
    def _save_execution_plan(self, service_id: int, title: str, objective: str, 
                            plan_data: Dict) -> Dict:
        """Salva o plano no banco de dados"""
        conn = Database.get_connection()
        cur = conn.cursor()
        
        plan_code = Database.generate_code("PLAN")
        
        cur.execute("""
            INSERT INTO execution_plans 
            (plan_code, service_id, title, objective, strategy, planned_steps, 
             estimated_duration_minutes, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending_approval')
        """, (
            plan_code,
            service_id,
            title,
            objective,
            plan_data.get('strategy', ''),
            json.dumps(plan_data.get('steps', []), ensure_ascii=False),
            plan_data.get('estimated_duration_minutes', 0)
        ))
        
        plan_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "id": plan_id,
            "plan_code": plan_code,
            "title": title,
            "status": "pending_approval",
            "strategy": plan_data.get('strategy', ''),
            "steps": plan_data.get('steps', []),
            "estimated_duration_minutes": plan_data.get('estimated_duration_minutes', 0)
        }
    
    def _create_master_message(self, plan_id: int, content: str):
        """Cria mensagem do Master sobre o plano"""
        # Por enquanto não criamos mensagem aqui, será feito na sessão
        pass
    
    def execute_approved_plan(self, plan_id: int) -> 'OrchestrationSession':
        """Inicia execução de um plano aprovado"""
        return OrchestrationSession(plan_id)


class OrchestrationSession:
    """Gerencia uma sessão de execução multi-agente"""
    
    def __init__(self, plan_id: int):
        self.plan_id = plan_id
        self.session_id = None
        self.session_code = None
        self.current_step_index = 0
        self.plan = None
        self.outputs = []
        self.master_id = self._get_master_id()
        
        self._load_plan()
        self._create_session()
    
    def _get_master_id(self) -> Optional[int]:
        """Busca ID do agente master"""
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM agents WHERE slug = ?", (MASTER_AGENT_SLUG,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None
    
    def _load_plan(self):
        """Carrega plano do banco"""
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT ep.*, s.agent_sequence, s.loop_config
            FROM execution_plans ep
            JOIN services s ON ep.service_id = s.id
            WHERE ep.id = ?
        """, (self.plan_id,))
        row = cur.fetchone()
        conn.close()
        
        if not row:
            raise ValueError(f"Plano não encontrado: {self.plan_id}")
        
        self.plan = dict(row)
        self.plan['planned_steps'] = json.loads(self.plan.get('planned_steps', '[]') or '[]')
        self.plan['agent_sequence'] = json.loads(self.plan.get('agent_sequence', '[]') or '[]')
        self.plan['loop_config'] = json.loads(self.plan.get('loop_config', '{}') or '{}')
    
    def _create_session(self):
        """Cria sessão no banco"""
        conn = Database.get_connection()
        cur = conn.cursor()
        
        self.session_code = Database.generate_code("SESSION")
        now = datetime.now().isoformat()
        
        cur.execute("""
            INSERT INTO orchestration_sessions 
            (session_code, execution_plan_id, status, started_at, shared_context, agent_outputs)
            VALUES (?, ?, 'running', ?, ?, ?)
        """, (
            self.session_code,
            self.plan_id,
            now,
            json.dumps({"objective": self.plan['objective'], "title": self.plan['title']}),
            json.dumps([])
        ))
        
        self.session_id = cur.lastrowid
        
        # Atualiza plano para executing
        cur.execute("""
            UPDATE execution_plans 
            SET status = 'executing', started_at = ?
            WHERE id = ?
        """, (now, self.plan_id))
        
        conn.commit()
        conn.close()
        
        # Mensagem inicial do Master
        self._broadcast_message(
            "instruction",
            f"🚀 Iniciando execução do plano: {self.plan['title']}\n"
            f"📋 Objetivo: {self.plan['objective']}\n"
            f"🎯 Total de steps: {len(self.plan['planned_steps'])}"
        )
    
    def start(self):
        """Inicia a execução"""
        pass  # Execução é passo a passo via next_step()
    
    def next_step(self) -> Optional[Dict]:
        """Retorna o próximo step a ser executado"""
        steps = self.plan['planned_steps']
        
        if self.current_step_index >= len(steps):
            return None
        
        step = steps[self.current_step_index]
        step['session_id'] = self.session_id
        step['session_code'] = self.session_code
        step['step_index'] = self.current_step_index
        step['total_steps'] = len(steps)
        
        # Atualiza sessão com step atual
        self._update_current_step()
        
        # Envia instrução para o agente
        agent_id = self._get_agent_id(step['agent_slug'])
        if agent_id:
            self._send_instruction(agent_id, step)
        
        return step
    
    def _update_current_step(self):
        """Atualiza step atual na sessão"""
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE orchestration_sessions 
            SET current_step_index = ?, current_agent_id = ?
            WHERE id = ?
        """, (self.current_step_index, self.master_id, self.session_id))
        conn.commit()
        conn.close()
    
    def _get_agent_id(self, agent_slug: str) -> Optional[int]:
        """Busca ID do agente pelo slug"""
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM agents WHERE slug = ?", (agent_slug,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None
    
    def execute_step(self, step: Dict, output: str, quality_score: int = None) -> Dict:
        """Registra output de um step"""
        result = {
            "step_index": step['step_index'],
            "agent_slug": step['agent_slug'],
            "output": output,
            "quality_score": quality_score,
            "completed_at": datetime.now().isoformat()
        }
        
        self.outputs.append(result)
        self.current_step_index += 1
        
        # Atualiza outputs na sessão
        self._update_outputs()
        
        # Notifica conclusão do step
        self._broadcast_message(
            "handoff",
            f"✅ Step {step['step_index'] + 1}/{step['total_steps']} concluído por {step['agent_name']}\n"
            f"📤 Output: {output[:200]}..." if len(output) > 200 else f"📤 Output: {output}"
        )
        
        return result
    
    def _update_outputs(self):
        """Atualiza outputs na sessão"""
        conn = Database.get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE orchestration_sessions 
            SET agent_outputs = ?
            WHERE id = ?
        """, (json.dumps(self.outputs, ensure_ascii=False), self.session_id))
        conn.commit()
        conn.close()
    
    def should_loop(self) -> bool:
        """Verifica se deve fazer loop baseado na qualidade"""
        loop_config = self.plan.get('loop_config', {})
        
        if not loop_config or not loop_config.get('enabled'):
            return False
        
        # Verifica último output
        if not self.outputs:
            return False
        
        last_output = self.outputs[-1]
        quality = last_output.get('quality_score', 0)
        min_score = loop_config.get('until_score', 8)
        
        return quality < min_score
    
    def handle_loop(self):
        """Repete o último step se necessário"""
        loop_config = self.plan.get('loop_config', {})
        max_iterations = loop_config.get('max_iterations', 1)
        
        # Conta quantas vezes repetimos o step atual
        current_step_outputs = [o for o in self.outputs if o['step_index'] == self.current_step_index - 1]
        
        if len(current_step_outputs) < max_iterations:
            # Volta para repetir o step
            self.current_step_index -= 1
            
            self._broadcast_message(
                "feedback",
                f"🔄 Qualidade insuficiente. Repetindo step {self.current_step_index + 1}..."
            )
            
            return True
        
        return False
    
    def complete(self, final_result: str, quality_score: int = None):
        """Finaliza a sessão"""
        now = datetime.now().isoformat()
        
        conn = Database.get_connection()
        cur = conn.cursor()
        
        # Atualiza sessão
        cur.execute("""
            UPDATE orchestration_sessions 
            SET status = 'completed', completed_at = ?
            WHERE id = ?
        """, (now, self.session_id))
        
        # Atualiza plano
        cur.execute("""
            UPDATE execution_plans 
            SET status = 'completed', completed_at = ?, final_result = ?, quality_score = ?
            WHERE id = ?
        """, (now, final_result, quality_score, self.plan_id))
        
        conn.commit()
        conn.close()
        
        # Mensagem final
        self._broadcast_message(
            "instruction",
            f"✅ Execução concluída!\n\n🏁 Resultado final:\n{final_result[:500]}..."
        )
    
    def fail(self, error_message: str):
        """Marca sessão como falha"""
        now = datetime.now().isoformat()
        
        conn = Database.get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE orchestration_sessions 
            SET status = 'failed', completed_at = ?
            WHERE id = ?
        """, (now, self.session_id))
        
        cur.execute("""
            UPDATE execution_plans 
            SET status = 'failed', completed_at = ?
            WHERE id = ?
        """, (now, self.plan_id))
        
        conn.commit()
        conn.close()
        
        self._broadcast_message("feedback", f"❌ Execução falhou: {error_message}")
    
    def is_complete(self) -> bool:
        """Verifica se execução está completa"""
        return self.current_step_index >= len(self.plan['planned_steps'])
    
    def get_context_for_step(self, step: Dict) -> Dict:
        """Retorna contexto acumulado para um step"""
        context = {
            "objective": self.plan['objective'],
            "title": self.plan['title'],
            "previous_outputs": self.outputs,
            "current_step": step
        }
        return context
    
    def _send_instruction(self, to_agent_id: int, step: Dict):
        """Envia instrução para um agente específico"""
        self._create_message(
            message_type="instruction",
            content=f"🎯 Sua tarefa: {step['title']}\n\n{step['description']}",
            to_agent_id=to_agent_id
        )
    
    def _broadcast_message(self, message_type: str, content: str):
        """Envia mensagem para todos (broadcast)"""
        self._create_message(
            message_type=message_type,
            content=content,
            to_agent_id=None
        )
    
    def _create_message(self, message_type: str, content: str, to_agent_id: int = None):
        """Cria mensagem no banco"""
        conn = Database.get_connection()
        cur = conn.cursor()
        
        msg_code = Database.generate_code("MSG")
        
        cur.execute("""
            INSERT INTO agent_messages_v2 
            (message_code, session_id, from_agent_id, to_agent_id, message_type, content)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            msg_code,
            self.session_id,
            self.master_id,  # Master envia
            to_agent_id,
            message_type,
            content
        ))
        
        conn.commit()
        conn.close()
    
    def get_messages(self) -> List[Dict]:
        """Retorna todas as mensagens da sessão"""
        conn = Database.get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT m.*, 
                   fa.name as from_name, fa.avatar_emoji as from_emoji,
                   ta.name as to_name, ta.avatar_emoji as to_emoji
            FROM agent_messages_v2 m
            LEFT JOIN agents fa ON m.from_agent_id = fa.id
            LEFT JOIN agents ta ON m.to_agent_id = ta.id
            WHERE m.session_id = ?
            ORDER BY m.created_at
        """, (self.session_id,))
        
        messages = [dict(row) for row in cur.fetchall()]
        conn.close()
        
        return messages


# ============================================================
# Funções Helper
# ============================================================

def get_pending_plans() -> List[Dict]:
    """Retorna planos pendentes de aprovação"""
    conn = Database.get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT ep.*, s.name as service_name, s.icon_emoji
        FROM execution_plans ep
        JOIN services s ON ep.service_id = s.id
        WHERE ep.status = 'pending_approval'
        ORDER BY ep.created_at DESC
    """)
    
    plans = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    for plan in plans:
        plan['planned_steps'] = json.loads(plan.get('planned_steps', '[]') or '[]')
    
    return plans


def get_approved_plans() -> List[Dict]:
    """Retorna planos aprovados prontos para execução"""
    conn = Database.get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT ep.*, s.name as service_name, s.icon_emoji
        FROM execution_plans ep
        JOIN services s ON ep.service_id = s.id
        WHERE ep.status = 'approved'
        ORDER BY ep.approved_at ASC
    """)
    
    plans = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    for plan in plans:
        plan['planned_steps'] = json.loads(plan.get('planned_steps', '[]') or '[]')
    
    return plans


def approve_plan(plan_code: str, approved_by: str = "user") -> bool:
    """Aprova um plano"""
    conn = Database.get_connection()
    cur = conn.cursor()
    
    now = datetime.now().isoformat()
    
    cur.execute("""
        UPDATE execution_plans 
        SET status = 'approved', approved_by = ?, approved_at = ?
        WHERE plan_code = ? AND status = 'pending_approval'
    """, (approved_by, now, plan_code))
    
    success = cur.rowcount > 0
    conn.commit()
    conn.close()
    
    return success


def reject_plan(plan_code: str, reason: str) -> bool:
    """Rejeita um plano"""
    conn = Database.get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE execution_plans 
        SET status = 'rejected', rejection_reason = ?
        WHERE plan_code = ? AND status = 'pending_approval'
    """, (reason, plan_code))
    
    success = cur.rowcount > 0
    conn.commit()
    conn.close()
    
    return success


if __name__ == "__main__":
    # Teste
    print("🎬 Testando Orchestrator")
    print("=" * 60)
    
    master = MasterAgent()
    print(f"✅ Master Agent: {master.AGENT_SLUG}")
    print(f"   Agentes disponíveis: {len(master.available_agents)}")
    
    # Lista serviços
    conn = Database.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM services WHERE is_active = 1")
    services = cur.fetchall()
    conn.close()
    
    print(f"\n📋 Serviços disponíveis: {len(services)}")
    for svc in services:
        print(f"   - {svc[1]}")
