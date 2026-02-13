#!/usr/bin/env python3
"""
Ralph Swarm Task Executor v4.0 - Modo Proativo
Processa tasks com fluxo: Perguntas → Plano → Aprovação → Execução
"""

import os
import sys
import json
import uuid
import traceback
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'swarm'))

from ralph_swarm_core import SwarmTaskManager, SwarmAgentManager, TaskStatus, ChannelSystem, AuthorType
import sqlite3

# Config
DB_PATH = Path.home() / ".openclaw/workspace/projects/dunder-mifflin/dunder_mifflin.db"

# Templates de perguntas inteligentes por tipo de task
QUESTION_TEMPLATES = {
    'default': [
        "Qual é o objetivo principal desta tarefa? (ex: informar, vender, educar)",
        "Qual o público-alvo? (ex: B2B, B2C, nicho específico)",
        "Qual o prazo ou urgência? (ex: hoje, esta semana, pode esperar)",
        "Você tem alguma referência, tom de voz ou restrição específica?",
        "Qual formato você espera no resultado? (ex: resumo, detalhado, bullets)"
    ],
    'audit': [
        "Qual o escopo da auditoria? (ex: site, redes sociais, concorrentes)",
        "Qual o objetivo da análise? (ex: identificar falhas, benchmarks, oportunidades)",
        "Há aspectos específicos para focar? (ex: SEO, UX, conteúdo, design)",
        "Precisa de comparação com concorrentes?",
        "Qual formato do relatório? (ex: lista de falhas, análise detalhada, apresentação)"
    ],
    'scraping': [
        "Quais dados específicos precisa extrair?",
        "Qual o volume esperado de dados?",
        "Há requisitos de frequência? (ex: one-time, diário, semanal)",
        "Qual formato de saída? (ex: JSON, CSV, banco de dados)"
    ],
    'social_media': [
        "Qual a plataforma principal? (Instagram, LinkedIn, TikTok, etc)",
        "O foco é próprio perfil ou análise de concorrente?",
        "Qual o objetivo? (ex: engajamento, crescimento, conteúdo)",
        "Precisa de análise de métricas?",
        "Há período específico para analisar?"
    ],
    'copy': [
        "Qual é o objetivo da copy? (ex: converter, engajar, informar)",
        "Qual o público-alvo e sua dor principal?",
        "Qual tom de voz? (ex: formal, casual, técnico, provocativo)",
        "Há alguma CTA específica ou oferta?",
        "Onde será publicado? (ex: LinkedIn, Instagram, Email, Site)"
    ],
    'research': [
        "Qual o escopo da pesquisa? (ex: mercado, concorrentes, tendências)",
        "Qual nível de profundidade? (ex: overview, análise detalhada, dados brutos)",
        "Há fontes preferidas ou a evitar?",
        "Qual o objetivo com esses dados? (ex: decisão, apresentação, estratégia)"
    ],
    'code': [
        "Qual a stack tecnológica preferida?",
        "Há requisitos de performance ou escalabilidade?",
        "Precisa de integração com sistemas existentes?",
        "Qual nível de documentação necessário?"
    ],
    'design': [
        "Qual o estilo visual desejado? (ex: moderno, clássico, minimalista)",
        "Há guideline de marca ou cores obrigatórias?",
        "Qual o formato de entrega? (ex: PNG, SVG, Figma link)"
    ]
}

def detect_task_type(request: str) -> str:
    """Detecta o tipo de task para escolher perguntas adequadas"""
    request_lower = request.lower()
    
    # Auditoria e análise de marca/redes sociais
    if any(k in request_lower for k in ['auditoria', 'análise de marca', 'análise da marca', 'social media audit', 'audit']):
        return 'audit'
    elif any(k in request_lower for k in ['scraping', 'scraper', 'extrair dados', 'coletar dados', 'crawler']):
        return 'scraping'
    elif any(k in request_lower for k in ['instagram', 'linkedin', 'redes sociais', 'social media', 'tiktok', 'youtube']):
        return 'social_media'
    elif any(k in request_lower for k in ['copy', 'escrever', 'texto', 'headline', 'post', 'blog', 'roteiro', 'conteúdo']):
        return 'copy'
    elif any(k in request_lower for k in ['pesquisa', 'research', 'análise', 'concorrente', 'mercado', 'tendência']):
        return 'research'
    elif any(k in request_lower for k in ['código', 'code', 'implementar', 'script', 'api', 'desenvolver']):
        return 'code'
    elif any(k in request_lower for k in ['design', 'imagem', 'visual', 'layout', 'logo']):
        return 'design'
    return 'default'

def generate_intelligent_questions(request: str) -> List[str]:
    """Gera perguntas inteligentes baseadas na task"""
    task_type = detect_task_type(request)
    questions = QUESTION_TEMPLATES.get(task_type, QUESTION_TEMPLATES['default'])
    return questions

def create_orchestration_plan(request: str, answers: Dict[str, str]) -> Dict:
    """Cria plano de orquestração baseado nas respostas"""
    request_lower = request.lower()
    
    # Detectar agents necessários
    agents = []
    if any(k in request_lower for k in ['pesquisa', 'research', 'análise', 'mercado', 'tendência']):
        agents.append('scout')
    if any(k in request_lower for k in ['copy', 'escrever', 'texto', 'conteúdo']):
        agents.append('maya')
    if any(k in request_lower for k in ['código', 'code', 'implementar', 'api', 'script', 'scraper', 'scraping']):
        agents.append('max')
    if any(k in request_lower for k in ['dados', 'métricas', 'dashboard', 'kpi', 'analytics']):
        agents.append('tracker')
    if any(k in request_lower for k in ['auditoria', 'monitorar', 'observar', 'watcher', 'concorrente']):
        agents.append('watcher')
    if not agents:
        agents = ['scout']  # default
    
    # Detectar tipo de execução
    exec_type = "single"  # Padrão: execução única
    if any(k in request_lower for k in ['semanal', 'diário', 'mensal', 'recorrente']):
        exec_type = "recorrente"
    elif any(k in request_lower for k in ['loop', 'iteração', 'ciclo', 'melhorar']):
        exec_type = "loop"
    
    # Detectar complexidade
    complexity = "simple"
    if len(request) > 300 or len(agents) > 2:
        complexity = "medium"
    if len(request) > 800 or len(agents) > 3:
        complexity = "complex"
    
    return {
        'agents_required': agents,
        'execution_type': exec_type,
        'complexity': complexity,
        'estimated_time': '15-30 min' if complexity == 'simple' else '1-2h' if complexity == 'medium' else '3-4h',
        'strategy': f'Executar com {", ".join(agents)} em modo {exec_type}'
    }

def format_plan_for_discord(plan: Dict, request: str) -> str:
    """Formata o plano para exibição no Discord"""
    emoji_map = {
        'scout': '🔍', 'max': '🛠️', 'maya': '📝',
        'tracker': '📊', 'watcher': '👁️', 'ralph': '🎩'
    }
    
    agents_formatted = '\n'.join([
        f"{emoji_map.get(a, '🤖')} **{a.title()}**"
        for a in plan['agents_required']
    ])
    
    exec_emoji = {
        'single': '▶️',
        'recorrente': '🔄',
        'loop': '🔁'
    }
    
    return f"""📋 **Plano de Orquestração**

🎯 **Tarefa:** {request[:80]}{'...' if len(request) > 80 else ''}

👥 **Agents Necessários:**
{agents_formatted}

⚙️ **Execução:** {exec_emoji.get(plan['execution_type'], '▶️')} {plan['execution_type'].title()}
📊 **Complexidade:** {plan['complexity'].upper()}
⏱️ **Tempo Estimado:** {plan['estimated_time']}

💡 **Estratégia:** {plan['strategy']}

---
✅ **Responda "aprovado" para iniciar**
🔄 **Ou "ajustar: <seu feedback>" para modificar**
"""

class SwarmTaskExecutorV4:
    """Executor v4.0 com modo proativo"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.tasks_mgr = SwarmTaskManager()
        self.channels = ChannelSystem()
    
    def _get_db(self):
        """Obtém conexão com retry"""
        import time
        for i in range(5):
            try:
                conn = sqlite3.connect(self.db_path, timeout=60.0)
                conn.execute("PRAGMA busy_timeout = 30000;")
                return conn
            except sqlite3.OperationalError:
                if i < 4:
                    time.sleep(2 ** i)
                else:
                    raise
    
    def process_awaiting_questions(self):
        """Processa tasks aguardando perguntas - envia perguntas ao usuário (apenas 1x)"""
        conn = self._get_db()
        cursor = conn.cursor()
        
        # v4.0 FIX: Só enviar perguntas se ainda não foram enviadas (questions_asked IS NULL)
        cursor.execute("""
            SELECT id, task_code, original_request, metadata 
            FROM swarm_tasks 
            WHERE status = ?
            AND (questions_asked IS NULL OR questions_asked = '')
        """, (TaskStatus.AWAITING_QUESTIONS.value,))
        
        tasks = cursor.fetchall()
        conn.close()
        
        if not tasks:
            return
        
        for task in tasks:
            task_id, task_code, request, metadata = task
            print(f"\n📝 Task {task_code} - Enviando perguntas inteligentes...")
            
            # Gerar perguntas
            questions = generate_intelligent_questions(request)
            
            # Salvar perguntas no banco (marcar como enviadas)
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.execute("PRAGMA journal_mode=WAL;")
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE swarm_tasks 
                SET questions_asked = ?
                WHERE id = ?
            """, (json.dumps(questions), task_id))
            conn.commit()
            conn.close()
            
            # Formatar mensagem para Discord
            questions_text = '\n'.join([f"{i+1}. {q}" for i, q in enumerate(questions)])
            message = f"""🎩 **Ralph - Perguntas para Refinar sua Task**

Para entregar o melhor resultado, preciso saber:

{questions_text}

---
💡 **Responda numerando as respostas (1. ..., 2. ...) ou texto livre**
            """
            
            # Enviar para o canal (se tiver channel_id no metadata)
            meta = json.loads(metadata or '{}')
            channel_id = meta.get('discord_channel_id')
            if channel_id:
                self._send_to_discord(channel_id, message, task_code)
                print(f"   ✅ Perguntas enviadas para Discord channel {channel_id}")
            else:
                print(f"   ⚠️ Sem channel_id, salvando apenas no banco")
                # Salvar no swarm_messages
                self.channels.post('agent-chat', AuthorType.AGENT, 'ralph', 
                    f"[TASK-{task_code}] Perguntas:\n{questions_text}")
    
    def check_for_user_responses(self):
        """Verifica se há respostas do usuário para tasks aguardando_questions"""
        conn = self._get_db()
        cursor = conn.cursor()
        
        # Buscar tasks que enviaram perguntas mas ainda não receberam respostas
        cursor.execute("""
            SELECT t.id, t.task_code, t.original_request, t.metadata, t.created_at
            FROM swarm_tasks t
            WHERE t.status = ?
            AND t.user_answers IS NULL
        """, (TaskStatus.AWAITING_QUESTIONS.value,))
        
        tasks = cursor.fetchall()
        conn.close()
        
        for task in tasks:
            task_id, task_code, request, metadata, created_at = task
            meta = json.loads(metadata or '{}')
            discord_channel_id = meta.get('discord_channel_id')
            
            if not discord_channel_id:
                continue
            
            # Buscar mensagens do usuário no canal correspondente
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.execute("PRAGMA journal_mode=WAL;")
            cursor = conn.cursor()
            
            # Procurar canal pelo nome discord-{channel_id}
            channel_name = f"discord-{discord_channel_id}"
            cursor.execute("SELECT id FROM swarm_channels WHERE name = ?", (channel_name,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                continue
            
            channel_db_id = result[0]
            
            # Buscar mensagens do usuário após a criação da task
            cursor.execute("""
                SELECT content, created_at
                FROM swarm_messages
                WHERE channel_id = ?
                AND author_type = 'user'
                AND created_at > ?
                ORDER BY created_at ASC
            """, (channel_db_id, created_at))
            
            messages = cursor.fetchall()
            conn.close()
            
            if messages:
                # Consolidar todas as mensagens do usuário como respostas
                responses = []
                for msg_content, msg_time in messages:
                    if msg_content and not msg_content.startswith('!'):
                        responses.append(msg_content)
                
                if responses:
                    answers_text = "\n".join(responses)
                    print(f"\n💬 Task {task_code} - Respostas recebidas!")
                    print(f"   {len(responses)} mensagens do usuário")
                    
                    # Parse answers
                    answers = {"raw_responses": responses}
                    
                    # CRIAR PLANO IMEDIATAMENTE
                    print(f"\n📋 Task {task_code} - Criando plano de orquestração...")
                    plan = create_orchestration_plan(request, answers)
                    plan_message = format_plan_for_discord(plan, request)
                    
                    # Atualizar task com respostas, plano e mudar status
                    conn = sqlite3.connect(self.db_path, timeout=30.0)
                    conn.execute("PRAGMA journal_mode=WAL;")
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE swarm_tasks 
                        SET user_answers = ?, 
                            execution_plan = ?,
                            status = ?, 
                            awaiting_approval = 1
                        WHERE id = ?
                    """, (json.dumps(answers), json.dumps(plan), TaskStatus.AWAITING_APPROVAL.value, task_id))
                    conn.commit()
                    conn.close()
                    
                    print(f"   ✅ Task atualizada para 'awaiting_approval'")
                    
                    # ENVIAR PLANO PARA APROVAÇÃO IMEDIATAMENTE
                    if discord_channel_id:
                        self._send_to_discord(discord_channel_id, plan_message, task_code)
                        print(f"   ✅ Plano enviado para aprovação no Discord")
                    else:
                        self.channels.post('agent-chat', AuthorType.AGENT, 'ralph', plan_message)
    
    def process_awaiting_approval(self):
        """Processa tasks aguardando aprovação - já tem plano criado"""
        conn = self._get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, task_code, original_request, user_answers, execution_plan, metadata
            FROM swarm_tasks 
            WHERE status = ? AND awaiting_approval = 1
        """, (TaskStatus.AWAITING_APPROVAL.value,))
        
        tasks = cursor.fetchall()
        conn.close()
        
        for task in tasks:
            task_id, task_code, request, answers_json, plan_json, metadata = task
            
            # Se já tem plano salvo, não precisa fazer nada (aguardando user responder "aprovado")
            if plan_json:
                continue
            
            print(f"\n📋 Task {task_code} - Criando plano de orquestração...")
            
            # Parse answers
            answers = json.loads(answers_json or '{}')
            
            # Criar plano
            plan = create_orchestration_plan(request, answers)
            
            # Salvar plano
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.execute("PRAGMA journal_mode=WAL;")
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE swarm_tasks 
                SET execution_plan = ?
                WHERE id = ?
            """, (json.dumps(plan), task_id))
            conn.commit()
            conn.close()
            
            # Enviar plano para aprovação
            plan_message = format_plan_for_discord(plan, request)
            
            meta = json.loads(metadata or '{}')
            channel_id = meta.get('discord_channel_id')
            if channel_id:
                self._send_to_discord(channel_id, plan_message, task_code)
                print(f"   ✅ Plano enviado para aprovação no Discord")
            else:
                self.channels.post('agent-chat', AuthorType.AGENT, 'ralph', plan_message)
    
    def check_for_approval(self, task_code: str, message_content: str) -> bool:
        """Verifica se mensagem é aprovação de uma task"""
        if 'aprovado' not in message_content.lower():
            return False
        
        conn = self._get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id FROM swarm_tasks 
            WHERE task_code = ? AND status = ?
        """, (task_code, TaskStatus.AWAITING_APPROVAL.value))
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def approve_task(self, task_code: str):
        """Aprova uma task e muda status para execução"""
        conn = self._get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE swarm_tasks 
            SET status = ?, awaiting_approval = 0
            WHERE task_code = ?
        """, (TaskStatus.APPROVED.value, task_code))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Task {task_code} aprovada! Pronta para execução.")
        
        # Notificar
        message = f"✅ **Task {task_code} Aprovada!**\n\nIniciando execução conforme plano..."
        # Enviar notificação...
    
    def process_approved_tasks(self):
        """Processa tasks aprovadas - executa conforme plano"""
        conn = self._get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, task_code, original_request, execution_plan, metadata
            FROM swarm_tasks 
            WHERE status = ?
        """, (TaskStatus.APPROVED.value,))
        
        tasks = cursor.fetchall()
        conn.close()
        
        for task in tasks:
            task_id, task_code, request, plan_json, metadata = task
            print(f"\n🚀 Task {task_code} - Executando plano aprovado...")
            
            plan = json.loads(plan_json or '{}')
            agents = plan.get('agents_required', ['scout'])
            
            # Executar agents
            results = {}
            for agent_slug in agents:
                print(f"   🤖 Executando {agent_slug}...")
                output = self._execute_agent(agent_slug, request)
                results[agent_slug] = output
                print(f"   ✅ {agent_slug} completado")
            
            # Consolidar resultado
            final_output = self._consolidate_results(results, plan)
            
            # Salvar e marcar como completada
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.execute("PRAGMA journal_mode=WAL;")
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE swarm_tasks 
                SET status = ?, final_output = ?, completed_at = datetime('now')
                WHERE id = ?
            """, (TaskStatus.COMPLETED.value, final_output, task_id))
            conn.commit()
            conn.close()
            
            print(f"   ✅ Task {task_code} completada!")
            
            # Notificar conclusão
            self._send_completion_notification(task_code, final_output, metadata)
    
    def _execute_agent(self, agent_slug: str, request: str) -> str:
        """Executa um agent específico (usa templates por enquanto)"""
        from swarm_task_executor import execute_task_with_agent
        return execute_task_with_agent(agent_slug, request)
    
    def _consolidate_results(self, results: Dict, plan: Dict) -> str:
        """Consolida resultados de múltiplos agents"""
        if len(results) == 1:
            return list(results.values())[0]
        
        output = "## Resultado da Orquestração\n\n"
        for agent, result in results.items():
            output += f"### Contribuição de {agent.title()}\n\n{result}\n\n---\n\n"
        return output
    
    def _send_to_discord(self, channel_id: int, message: str, task_code: str):
        """Envia mensagem para Discord via banco"""
        # Reutilizar lógica do swarm_task_executor.py
        from swarm_task_executor import send_discord_notification
        send_discord_notification(channel_id, message, task_code)
    
    def _send_completion_notification(self, task_code: str, output: str, metadata: str):
        """Envia notificação de conclusão"""
        meta = json.loads(metadata or '{}')
        channel_id = meta.get('discord_channel_id')
        
        message = f"""✅ **Task {task_code} Completada!**

📄 **Resumo:**
{output[:500]}{'...' if len(output) > 500 else ''}

🎩 Executada com sucesso!
        """
        
        if channel_id:
            self._send_to_discord(channel_id, message, task_code)
    
    def run(self):
        """Executa o ciclo completo do executor v4.0"""
        print(f"🤖 Ralph Swarm Task Executor v4.0 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        # 1. Tasks novas → Enviar perguntas
        self.process_awaiting_questions()
        
        # 1.5 Verificar respostas do usuário
        self.check_for_user_responses()
        
        # 2. Tasks com respostas → Criar plano e aguardar aprovação
        self.process_awaiting_approval()
        
        # 3. Tasks aprovadas → Executar
        self.process_approved_tasks()
        
        print("-" * 60)
        print("✅ Ciclo concluído")


def main():
    """Ponto de entrada"""
    executor = SwarmTaskExecutorV4()
    executor.run()


if __name__ == "__main__":
    main()
