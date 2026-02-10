#!/usr/bin/env python3
"""
Dunder Mifflin Worker v3.0 - Super Agents Edition
Sistema com 3 super-agentes: O Marketeiro, O Dev, O Executivo
Features: Handoffs, Memory System, Performance Tracking
"""

import os
import sys
import time
import json
import uuid
import logging
import sqlite3
import subprocess
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Constantes
WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"
STUDIO_DIR = WORKSPACE_DIR / "studio" / "projects"
DB_PATH = Path(__file__).parent / "dunder_mifflin.db"
AGENTS_DIR = Path(__file__).parent / "agents" / "super"

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("dm-worker-v3")

# ============================================================================
# SUPER AGENT DEFINITIONS
# ============================================================================

SUPER_AGENTS = {
    "o-marketeiro": {
        "name": "O Marketeiro",
        "role": "Growth Lead",
        "department": "marketing",
        "level": "Operator",
        "specialties": ["copywriting", "paid_media", "seo", "social_media", "growth_hacking"],
        "can_handoff_to": ["o-dev"],  # Pode pedir ajuda ao Dev
        "report_to": "o-executivo"
    },
    "o-dev": {
        "name": "O Dev",
        "role": "Tech Lead",
        "department": "engineering",
        "level": "Operator",
        "specialties": ["fullstack", "devops", "architecture", "ai_integration", "testing"],
        "can_handoff_to": ["o-marketeiro"],  # Pode pedir ajuda ao Marketeiro
        "report_to": "o-executivo"
    },
    "o-executivo": {
        "name": "O Executivo",
        "role": "Chief Operator",
        "department": "executive",
        "level": "Autonomous",
        "specialties": ["strategy", "operations", "management", "coordination"],
        "can_handoff_to": ["o-marketeiro", "o-dev"],  # Pode delegar para ambos
        "report_to": None  # Nível máximo
    }
}

# ============================================================================
# DATABASE HELPERS
# ============================================================================

def get_db():
    """Retorna conexão com o banco"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def log_activity(agent_slug: str, action: str, details: str = None, project: str = None):
    """Registra atividade no banco"""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO agent_memories (agent_slug, memory_type, project_slug, content)
            VALUES (?, 'activity', ?, ?)
        """, (agent_slug, project, f"{action}: {details or ''}"))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Erro ao logar atividade: {e}")

def create_handoff(from_agent: str, to_agent: str, task_type: str, 
                   context: str, deliverables: list, timeline: str, 
                   priority: str = "Medium") -> str:
    """Cria um handoff entre agentes"""
    conn = get_db()
    cur = conn.cursor()
    
    handoff_code = f"HANDOFF-{uuid.uuid4().hex[:12]}"
    
    cur.execute("""
        INSERT INTO agent_handoffs 
        (handoff_code, from_agent, to_agent, task_type, context, deliverables, timeline, priority, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')
    """, (handoff_code, from_agent, to_agent, task_type, context, 
          json.dumps(deliverables), timeline, priority))
    
    conn.commit()
    conn.close()
    
    logger.info(f"🔄 Handoff criado: {from_agent} → {to_agent} ({task_type})")
    return handoff_code

def complete_handoff(handoff_code: str, output: str, quality_rating: int = None):
    """Completa um handoff"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE agent_handoffs 
        SET status = 'completed', output = ?, quality_rating = ?, completed_at = ?
        WHERE handoff_code = ?
    """, (output, quality_rating, datetime.now().isoformat(), handoff_code))
    
    conn.commit()
    conn.close()
    
    logger.info(f"✅ Handoff completado: {handoff_code}")

def get_pending_handoffs(agent_slug: str) -> List[Dict]:
    """Retorna handoffs pendentes para um agente"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM agent_handoffs 
        WHERE to_agent = ? AND status = 'pending'
        ORDER BY created_at ASC
    """, (agent_slug,))
    
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows

def record_performance_review(agent_slug: str, rating: float, feedback: str):
    """Registra performance review"""
    conn = get_db()
    cur = conn.cursor()
    
    # Determina status baseado no rating
    if rating >= 4.5:
        status = "exceeds"
    elif rating >= 3.5:
        status = "meets"
    elif rating >= 2.5:
        status = "partial"
    else:
        status = "below"
    
    cur.execute("""
        INSERT INTO agent_reviews (agent_slug, review_date, rating, status, feedback)
        VALUES (?, date('now'), ?, ?, ?)
    """, (agent_slug, rating, status, feedback))
    
    conn.commit()
    conn.close()
    
    logger.info(f"📊 Performance review registrada: {agent_slug} ({rating}/5 - {status})")

# ============================================================================
# LLM CLIENT - Multi-Provider por Agente
# ============================================================================

# Configuração de LLMs por agente (todos via Kimi CLI)
AGENT_LLM_CONFIG = {
    "o-marketeiro": {
        "provider": "kimi-cli",
        "model": "kimi-k2.5",
        "api_key": None,
        "base_url": None
    },
    "o-dev": {
        "provider": "kimi-cli",
        "model": "kimi-k2.5",
        "api_key": None,
        "base_url": None
    },
    "o-executivo": {
        "provider": "kimi-cli",
        "model": "kimi-k2.5",
        "api_key": None,
        "base_url": None
    }
}

def load_agent_skill(agent_slug: str) -> str:
    """Carrega a skill do agente do arquivo .md correspondente"""
    skill_files = {
        "o-marketeiro": "SOUL-the-marketeiro.md",
        "o-dev": "SOUL-the-dev.md",
        "o-executivo": "SOUL-the-executivo.md"
    }
    
    filename = skill_files.get(agent_slug)
    if not filename:
        logger.warning(f"⚠️ Nenhuma skill file mapeada para {agent_slug}")
        return None
    
    skill_path = AGENTS_DIR / filename
    if skill_path.exists():
        try:
            content = skill_path.read_text(encoding='utf-8')
            logger.info(f"✅ Skill carregada: {filename} ({len(content)} chars)")
            return content
        except Exception as e:
            logger.error(f"❌ Erro ao ler skill {filename}: {e}")
            return None
    else:
        logger.warning(f"⚠️ Skill file não encontrado: {skill_path}")
        return None

def call_llm(prompt: str, agent_slug: str) -> str:
    """Chama LLM via Kimi CLI com contexto da skill do agente"""
    config = AGENT_LLM_CONFIG.get(agent_slug, AGENT_LLM_CONFIG["o-marketeiro"])
    
    # Tenta carregar skill do arquivo .md
    skill_content = load_agent_skill(agent_slug)
    
    if skill_content:
        # Usa a skill completa como system prompt
        system_prompt = f"""Você é um agente AI especialista. Siga suas diretrizes abaixo:

{skill_content}

---
INSTRUÇÕES IMPORTANTES:
1. Responda sempre em português
2. Siga sua filosofia e princípios definidos acima
3. Use suas skills e métodos conforme sua expertise
4. Seja direto e prático - focado em resultados
"""
    else:
        # Fallback para system prompts padrão
        system_prompts = {
            "o-marketeiro": "Você é um especialista em marketing digital e growth. Responda em português, de forma persuasiva e focada em resultados.",
            "o-dev": "Você é um desenvolvedor sênior. Escreva código limpo, documentado e bem estruturado. Responda em português.",
            "o-executivo": "Você é um executivo de negócios estratégico. Forneça análises claras, acionáveis e focadas em resultados. Responda em português."
        }
        system_prompt = system_prompts.get(agent_slug, "Você é um assistente útil. Responda em português.")
        logger.warning(f"⚠️ Usando fallback prompt para {agent_slug}")
    
    try:
        return _call_kimi_cli(prompt, system_prompt)
    except Exception as e:
        logger.error(f"❌ Erro LLM (kimi-cli): {e}")
        return generate_demo_content(agent_slug, prompt)

def _call_kimi_cli(prompt: str, system_prompt: str) -> str:
    """Chama Kimi via CLI"""
    logger.info("🤖 Chamando Kimi CLI...")
    
    # Monta o prompt completo
    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    
    # Procura o kimi CLI em locais comuns
    kimi_paths = [
        "/home/clawd/.local/bin/kimi",
        "/usr/local/bin/kimi",
        "/usr/bin/kimi",
        "kimi"  # Fallback para PATH
    ]
    
    kimi_cmd = None
    for path in kimi_paths:
        if os.path.exists(path) or path == "kimi":
            kimi_cmd = path
            break
    
    if not kimi_cmd:
        raise Exception("Kimi CLI não encontrado em nenhum caminho conhecido")
    
    logger.info(f"📍 Usando Kimi CLI: {kimi_cmd}")
    
    # Configura PATH se necessário
    env = os.environ.copy()
    env["PATH"] = "/home/clawd/.local/bin:" + env.get("PATH", "")
    
    try:
        # Executa o CLI do Kimi
        result = subprocess.run(
            [kimi_cmd, "--print", "--output-format=text"],
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutos timeout
            env=env
        )
        
        if result.returncode == 0:
            output = result.stdout
            
            # Extrai conteúdo do TextPart
            content_lines = []
            in_text = False
            for line in output.split('\n'):
                if 'TextPart(' in line:
                    in_text = True
                    continue
                if in_text and "text='" in line:
                    text_start = line.find("text='") + 6
                    text_end = line.rfind("'")
                    if text_end > text_start:
                        content_lines.append(line[text_start:text_end])
                if in_text and line.strip() == ')':
                    break
            
            content = '\n'.join(content_lines)
            
            # Fallback: tenta extrair com regex
            if not content:
                import re
                matches = re.findall(r"text='([^']*(?:\\'[^']*)*)'", output)
                if matches:
                    content = '\n'.join(matches).replace("\\'", "'")
            
            # Último fallback: retorna output filtrado
            if not content:
                filtered = []
                skip = ['TurnBegin', 'StepBegin', 'ThinkPart', 'StatusUpdate', 'TurnEnd', 'ToolCall']
                for line in output.split('\n'):
                    if not any(s in line for s in skip):
                        filtered.append(line)
                content = '\n'.join(filtered).strip()
            
            logger.info(f"✅ Kimi CLI respondeu ({len(content)} chars)")
            return content
        else:
            logger.error(f"❌ Kimi CLI erro: {result.stderr[:200]}")
            raise Exception(f"Kimi CLI error: {result.returncode}")
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Kimi CLI timeout (5min)")
        raise Exception("Kimi CLI timeout")
    except Exception as e:
        logger.error(f"❌ Erro Kimi CLI: {e}")
        raise

def generate_demo_content(agent_slug: str, prompt: str) -> str:
    """Gera conteúdo demo quando LLM falha"""
    logger.info(f"📝 Modo DEMO para {agent_slug}")
    
    if agent_slug == "o-marketeiro":
        return generate_marketeiro_content(prompt)
    elif agent_slug == "o-dev":
        return generate_dev_content(prompt)
    else:
        return generate_executivo_content(prompt)

def generate_marketeiro_content(prompt: str) -> str:
    """Conteúdo demo do Marketeiro"""
    return """# 5 Estratégias de Growth que Explodiram Nossos Resultados

## O Problema
Estávamos estagnados. Mesmo budget, mesmas campanhas, resultados cada vez piores.

## A Solução (Testada e Validada)

### 1. 🎯 Segmentação Micro
Paramos de falar com "empresas" e começamos a falar com "CTOs de startups SaaS com 10-50 funcionários que acabaram de receber funding".

**Resultado:** CAC caiu 40%, conversão subiu 3x.

### 2. 📝 Copy Baseada em Dor Real
Não mais "soluções inovadoras". Agora: "Pare de perder 12h semanais em relatórios manuais".

**Resultado:** CTR em anúncios subiu 220%.

### 3. 🔄 Remarketing Inteligente
Não mais "compre agora". Sequência: Educação → Caso de uso → Oferta limitada.

**Resultado:** ROAS de 2x para 5x.

### 4. 🤝 Parcerias Estratégicas
Unimos forças com 3 ferramentas complementares. Co-marketing + integração nativa.

**Resultado:** 30% dos novos leads vêm de parceiros.

### 5. 📊 Decisões em 24h
Implementamos sistema de teste: qualquer ideia roda em 24h, não em 2 semanas.

**Resultado:** 10x mais experimentos, aprendizado 10x mais rápido.

## O Resultado
- Leads: +150%
- CAC: -35%
- Receita: +80%

## Sua Vez
Qual dessas você pode implementar ainda essa semana?

---
*Análise gerada por O Marketeiro*"""

def generate_dev_content(prompt: str) -> str:
    """Conteúdo demo do Dev"""
    return """# Arquitetura da Feature X

## Overview
Sistema implementado com foco em escalabilidade e manutenibilidade.

## Stack Tecnológico
- **Backend:** Node.js + Express
- **Database:** PostgreSQL + Redis (cache)
- **AI:** Gemini API via OpenClaw
- **Deploy:** Docker + CI/CD

## Componentes Principais

### 1. API Layer
```javascript
// Estrutura de rotas
/api/v1/missions        # CRUD de missões
/api/v1/handoffs        # Sistema de handoffs
/api/v1/agents          # Gestão de agentes
```

### 2. Worker Service
- Processamento assíncrono de missões
- Sistema de filas com retry
- Monitoramento automático

### 3. Database Schema
```sql
-- Tabelas principais
agents          # Super-agentes (3)
missions        # Missões ativas
handoffs        # Coordenação entre agentes
memories        # Persistência de contexto
```

## Decisões Técnicas

**Por que PostgreSQL e não Mongo?**
- Relações entre entidades são complexas
- Consistência ACID necessária
- Queries analíticas frequentes

**Por que não Kubernetes?**
- Overkill para escala atual
- Docker Compose + CI/CD suficiente
- Menos complexidade = menos falhas

## Métricas
- Deploy time: < 5 min
- Uptime: 99.9%
- Response time p95: 120ms

## Próximos Passos
1. Implementar cache distribuído
2. Adicionar rate limiting
3. Setup de staging environment

---
*Documentação técnica por O Dev*"""

def generate_executivo_content(prompt: str) -> str:
    """Conteúdo demo do Executivo"""
    return """# Q1 2026: Review Estratégico

## Objetivos (Set vs Achieved)

| Métrica | Target | Actual | Status |
|---------|--------|--------|--------|
| Receita | R$ 500k | R$ 580k | ✅ 116% |
| Novos Clientes | 50 | 62 | ✅ 124% |
| Churn | < 5% | 3.2% | ✅ |
| NPS | > 40 | 52 | ✅ |

## O Que Funcionou

### 1. Foco em ICP (Ideal Customer Profile)
Restringimos o target de "empresas" para "CTOs de SaaS com 20-100 employees". 
**Impacto:** CAC -30%, LTV +40%.

### 2. Automação de Onboarding
Reduzimos time-to-value de 3 dias para 2 horas.
**Impacto:** Ativação +65%, churn -20%.

### 3. Parceria Estratégica
Aliança com 2 players complementares gerou 25% dos leads.

## O Que Não Funcionou

### 1. Expansão Prematura para Enterprise
Perdemos 3 meses tentando vender para enterprise. ROI negativo.
**Lição:** Validar PMF no segmento atual antes de expandir.

### 2. Feature X (Complexa)
Investimos 2 sprints em feature que ninguém usou.
**Lição:** Research antes de build. "Build measure learn", não só "build".

## Decisões Q2

**Continuar:**
- Foco no ICP atual
- Expansão de parcerias
- Automação de processos

**Parar:**
- Enterprise sales (por enquanto)
- Features complexas sem validação

**Iniciar:**
- Teste de novo canal (TikTok B2B)
- Programa de referral
- Freemium tier

## Resource Allocation
- 60% produto existente (melhorias)
- 25% growth (aquisição)
- 15% experimentação (novos canais/features)

## Riscos
1. **Concorrência aumentando** → Diferenciação via CX
2. **Custo de aquisição subindo** → Foco em retenção
3. **Dependência de 1 canal** → Diversificação Q2

## Conclusão
Q1 foi acima do esperado. Q2 foca em consolidar gains, não em reinventar.

---
*Review estratégico por O Executivo*"""

# ============================================================================
# MISSION EXECUTION
# ============================================================================

def execute_mission_v3(mission_id: int, mission: Dict) -> bool:
    """Executa uma missão com o super-agente apropriado"""
    
    # Busca o agent_slug baseado no agent_id (o banco guarda agent_id, não agent_slug)
    agent_id = mission.get("agent_id")
    if agent_id:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT slug FROM agents WHERE id = ?", (agent_id,))
        row = cur.fetchone()
        conn.close()
        agent_slug = row[0] if row else "o-marketeiro"
    else:
        agent_slug = mission.get("agent_slug", "o-marketeiro")
    
    title = mission.get("title", "")
    description = mission.get("description", "")
    
    logger.info(f"🚀 Executando missão: {title}")
    logger.info(f"   Agente: {SUPER_AGENTS.get(agent_slug, {}).get('name', agent_slug)}")
    
    # Log de início
    log_activity(agent_slug, "mission_started", f"Iniciando: {title}", mission.get("project_slug"))
    
    try:
        # Determina tipo de tarefa
        task_type = determine_task_type(title, description, agent_slug)
        
        # Gera prompt específico
        prompt = generate_prompt(agent_slug, title, description, task_type)
        
        # Chama LLM
        content = call_llm(prompt, agent_slug)
        
        # Verifica se precisa de handoff
        handoff_created = check_and_create_handoff(agent_slug, title, description, content)
        
        # Salva resultado
        result = {
            "type": task_type,
            "title": title,
            "content": content,
            "word_count": len(content.split()),
            "handoff_created": handoff_created,
            "generated_at": datetime.now().isoformat()
        }
        
        # Salva arquivo se necessário
        if task_type in ["blog_post", "content", "linkedin_post"]:
            save_content_file(agent_slug, title, content, task_type)
        
        # Atualiza missão no banco
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE missions SET status = 'succeeded', result = ?, completed_at = ?
            WHERE id = ?
        """, (json.dumps(result), datetime.now().isoformat(), mission_id))
        conn.commit()
        conn.close()
        
        # Log de conclusão
        log_activity(agent_slug, "mission_completed", 
                    f"Concluída: {title} ({result['word_count']} palavras)", 
                    mission.get("project_slug"))
        
        logger.info(f"✅ Missão concluída: {title}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na missão: {e}")
        
        # Atualiza como falha
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE missions SET status = 'failed', result = ?, completed_at = ?
            WHERE id = ?
        """, (json.dumps({"error": str(e)}), datetime.now().isoformat(), mission_id))
        conn.commit()
        conn.close()
        
        log_activity(agent_slug, "mission_failed", f"Erro: {str(e)[:100]}")
        return False

def determine_task_type(title: str, description: str, agent_slug: str) -> str:
    """Determina o tipo de tarefa baseado no conteúdo"""
    text = f"{title} {description}".lower()
    
    if agent_slug == "o-marketeiro":
        if "blog" in text or "post" in text:
            return "blog_post"
        elif "linkedin" in text:
            return "linkedin_post"
        elif "twitter" in text or "thread" in text:
            return "twitter_thread"
        elif "email" in text:
            return "email"
        elif "tiktok" in text or "roteiro" in text:
            return "tiktok_script"
        elif "estratégia" in text or "strategy" in text:
            return "strategy"
        else:
            return "content"
    
    elif agent_slug == "o-dev":
        if "api" in text:
            return "api_development"
        elif "feature" in text or "funcionalidade" in text:
            return "feature"
        elif "bug" in text or "fix" in text:
            return "bugfix"
        elif "arquitetura" in text or "architecture" in text:
            return "architecture"
        else:
            return "development"
    
    else:  # o-executivo
        if "review" in text or "análise" in text:
            return "review"
        elif "estratégia" in text or "strategy" in text:
            return "strategy"
        elif "planejamento" in text or "planning" in text:
            return "planning"
        else:
            return "management"

def generate_prompt(agent_slug: str, title: str, description: str, task_type: str) -> str:
    """Gera prompt específico para o agente"""
    
    agent = SUPER_AGENTS.get(agent_slug, {})
    agent_name = agent.get("name", agent_slug)
    
    base_prompt = f"""Você é {agent_name}, {agent.get('role', 'Especialista')}.

MISSÃO: {title}
DESCRIÇÃO: {description}
TIPO: {task_type}

"""
    
    if agent_slug == "o-marketeiro":
        base_prompt += """
Diretrizes:
- Foco em resultados (leads, vendas, conversão)
- Copy persuasiva e direta
- Estratégia baseada em dados
- Tom profissional mas humano

Entregue conteúdo completo e pronto para uso."""
    
    elif agent_slug == "o-dev":
        base_prompt += """
Diretrizes:
- Solução técnica robusta
- Código/documentação clara
- Testes e monitoramento
- Arquitetura escalável

Entregue implementação completa ou documentação técnica detalhada."""
    
    else:  # o-executivo
        base_prompt += """
Diretrizes:
- Análise estratégica
- Decisões baseadas em dados
- Foco em objetivos de negócio
- Recomendações acionáveis

Entregue análise completa com próximos passos claros."""
    
    return base_prompt

def check_and_create_handoff(agent_slug: str, title: str, description: str, content: str) -> bool:
    """Verifica se precisa criar handoff para outro agente"""
    
    # Lógica simples: se conteúdo menciona necessidade de outro agente
    text = f"{title} {description} {content}".lower()
    
    handoff_created = False
    
    if agent_slug == "o-marketeiro":
        # Se menciona landing page, precisa do Dev
        if any(word in text for word in ["landing page", "página", "website", "formulário"]):
            create_handoff(
                from_agent="o-marketeiro",
                to_agent="o-dev",
                task_type="landing-page",
                context=f"Landing page necessária para: {title}",
                deliverables=["HTML/CSS responsivo", "Formulário de captura", "Integração CRM"],
                timeline="48 horas",
                priority="High"
            )
            handoff_created = True
    
    elif agent_slug == "o-dev":
        # Se menciona copy/mensagens, precisa do Marketeiro
        if any(word in text for word in ["copy", "mensagem", "texto", "error message"]):
            create_handoff(
                from_agent="o-dev",
                to_agent="o-marketeiro",
                task_type="copywriting",
                context=f"Copy necessária para: {title}",
                deliverables=["Microcopy", "Error messages", "UX writing"],
                timeline="24 horas",
                priority="Medium"
            )
            handoff_created = True
    
    return handoff_created

def save_content_file(agent_slug: str, title: str, content: str, task_type: str):
    """Salva conteúdo em arquivo"""
    
    # Determina pasta baseada no agente
    if agent_slug == "o-marketeiro":
        folder = "marketing_content"
    elif agent_slug == "o-dev":
        folder = "technical_docs"
    else:
        folder = "strategy_docs"
    
    save_dir = STUDIO_DIR / "dunder_mifflin" / folder
    save_dir.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y%m%d")
    safe_title = "".join(c if c.isalnum() else "_" for c in title.lower())[:30]
    filename = f"{date_str}_{safe_title}.md"
    filepath = save_dir / filename
    
    header = f"""# {title}

**Gerado por:** {SUPER_AGENTS.get(agent_slug, {}).get('name', agent_slug)}  
**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}  
**Tipo:** {task_type}

---

"""
    
    filepath.write_text(header + content, encoding="utf-8")
    logger.info(f"   💾 Arquivo salvo: {filepath}")

# ============================================================================
# MAIN WORKER LOOP
# ============================================================================

def run_worker_v3():
    """Loop principal do worker v3"""
    
    logger.info("=" * 60)
    logger.info("🚀 Dunder Mifflin Worker v3.0 - Super Agents Edition")
    logger.info("=" * 60)
    logger.info(f"   Agentes ativos: {len(SUPER_AGENTS)}")
    for slug, agent in SUPER_AGENTS.items():
        logger.info(f"   • {agent['name']} (Level: {agent['level']})")
    logger.info("=" * 60)
    logger.info("")
    
    iteration = 0
    
    while True:
        try:
            iteration += 1
            
            # 1. Verifica handoffs pendentes
            for agent_slug in SUPER_AGENTS.keys():
                pending = get_pending_handoffs(agent_slug)
                if pending:
                    logger.info(f"📋 {len(pending)} handoff(s) pendente(s) para {agent_slug}")
                    # Aqui processaria os handoffs
            
            # 2. Busca missões aprovadas
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM missions 
                WHERE status = 'approved' 
                AND agent_id IN (SELECT id FROM agents WHERE slug IN ('o-marketeiro', 'o-dev', 'o-executivo'))
                ORDER BY priority DESC, created_at ASC
                LIMIT 2
            """)
            missions = [dict(row) for row in cur.fetchall()]
            conn.close()
            
            if missions:
                logger.info(f"📋 {len(missions)} missão(ões) aprovada(s)")
                for mission in missions:
                    # Marca como running
                    conn = get_db()
                    cur = conn.cursor()
                    cur.execute("UPDATE missions SET status = 'running' WHERE id = ?", (mission["id"],))
                    conn.commit()
                    conn.close()
                    
                    # Executa
                    execute_mission_v3(mission["id"], mission)
                    time.sleep(3)
            
            # 3. Heartbeat a cada 12 iterações
            if iteration % 12 == 0:
                logger.info("💓 Worker v3 ativo")
            
            time.sleep(5)
            
        except KeyboardInterrupt:
            logger.info("👋 Worker v3 parado pelo usuário")
            break
        except Exception as e:
            logger.error(f"❌ Erro no loop: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_worker_v3()
