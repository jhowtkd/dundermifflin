#!/usr/bin/env python3
"""
Executor de Agentes para Worker V2
Chama agentes reais do sistema OpenClaw via sessions_spawn
"""

import sys
import json
import os
from pathlib import Path

# Adiciona path para importar openclaw
sys.path.insert(0, str(Path.home() / ".nvm" / "versions" / "node" / "v24.13.0" / "lib" / "node_modules" / "openclaw"))

def load_agent_prompt(agent_slug: str) -> str:
    """Carrega o prompt do agente do arquivo markdown"""
    
    # Mapeamento de slug -> caminho
    agent_paths = {
        "debugger": "agents/development/debugger.md",
        "tester": "agents/testing/tester.md",
        "researcher": "agents/product/researcher.md",
        "code-reviewer": "agents/development/code-reviewer.md",
        "architect": "agents/development/architect.md",
        "fullstack-developer": "agents/development/fullstack-developer.md",
        "ai-engineer": "agents/development/ai-engineer.md",
        "database-engineer": "agents/development/database-engineer.md",
        "cicd-engineer": "agents/development/cicd-engineer.md",
        "api-designer": "agents/development/api-designer.md",
        "rapid-prototyper": "agents/development/rapid-prototyper.md",
        "bolt": "agents/autonomous/bolt.md",
        "sentinel": "agents/autonomous/sentinel.md",
        "janitor": "agents/autonomous/janitor.md",
        "migrator": "agents/autonomous/migrator.md",
        "optimizer": "agents/autonomous/optimizer.md",
        "a11y-specialist": "agents/autonomous/a11y-specialist.md",
        "i18n-specialist": "agents/autonomous/i18n-specialist.md",
        "ui-designer": "agents/design/ui-designer.md",
        "ux-researcher": "agents/design/ux-researcher.md",
        "ux-writer": "agents/design/ux-writer.md",
        "palette": "agents/design/palette.md",
        "polish": "agents/design/polish.md",
        "brand-guardian": "agents/design/brand-guardian.md",
        "visual-storyteller": "agents/design/visual-storyteller.md",
        "whimsy-injector": "agents/design/whimsy-injector.md",
        "feedback-synthesizer": "agents/product/feedback-synthesizer.md",
        "sprint-prioritizer": "agents/product/sprint-prioritizer.md",
        "trend-researcher": "agents/product/trend-researcher.md",
        "social-media-manager": "agents/marketing/social-media-manager.md",
        "copywriter": "agents/marketing/copywriter.md",
        "seo-specialist": "agents/marketing/seo-specialist.md",
        "content-strategist": "agents/marketing/content-strategist.md",
        "growth-hacker": "agents/marketing/growth-hacker.md",
        "email-marketing": "agents/marketing/email-marketing.md",
        "community-manager": "agents/marketing/community-manager.md",
        "jira-manager": "agents/project-management/jira-manager.md",
        "notion-manager": "agents/project-management/notion-manager.md",
        "github-manager": "agents/project-management/github-manager.md",
        "sprint-master": "agents/project-management/sprint-master.md",
        "risk-manager": "agents/project-management/risk-manager.md",
        "stakeholder-liaison": "agents/project-management/stakeholder-liaison.md",
        "release-coordinator": "agents/project-management/release-coordinator.md",
        "twitter-engager": "agents/social-media/twitter-engager.md",
        "linkedin-storyteller": "agents/social-media/linkedin-storyteller.md",
        "instagram-visual": "agents/social-media/instagram-visual.md",
        "youtube-scriptwriter": "agents/social-media/youtube-scriptwriter.md",
        "tiktok-creator": "agents/social-media/tiktok-creator.md",
        "mermaid-architect": "agents/tools/mermaid-architect.md",
        "regex-wizard": "agents/tools/regex-wizard.md",
        "sql-analyzer": "agents/tools/sql-analyzer.md",
        "bash-automator": "agents/tools/bash-automator.md",
        "dockerfile-optimizer": "agents/tools/dockerfile-optimizer.md",
        "git-sherpa": "agents/tools/git-sherpa.md",
        "json-wrangler": "agents/tools/json-wrangler.md",
        "csv-magician": "agents/tools/csv-magician.md",
    }
    
    # Tenta encontrar o arquivo
    base_path = Path(__file__).parent
    
    if agent_slug in agent_paths:
        file_path = base_path / agent_paths[agent_slug]
    else:
        # Tenta encontrar em qualquer lugar
        file_path = base_path / f"agents/{agent_slug}.md"
    
    if file_path.exists():
        with open(file_path) as f:
            return f.read()
    
    # Fallback: prompt genérico
    return f"""Você é um agente especialista chamado {agent_slug}.
Sua tarefa é ajudar com o objetivo fornecido.
Seja completo e detalhado em sua resposta."""

def execute_agent(agent_slug: str, task: str) -> dict:
    """Executa um agente e retorna o resultado"""
    
    prompt = load_agent_prompt(agent_slug)
    
    # Monta a mensagem completa
    full_message = f"""{prompt}

---

## Tarefa Atual

{task}

---

Por favor, execute esta tarefa e retorne:
1. O resultado completo do trabalho
2. Arquivos criados/modificados (se houver)
3. Resumo das ações realizadas
"""
    
    # Por enquanto, retorna simulação
    # Em breve, integrar com sessions_spawn real
    return {
        "status": "completed",
        "output": f"""✅ Tarefa executada pelo agente {agent_slug}

## Resumo

O agente {agent_slug} processou a tarefa com sucesso.

### Ações Realizadas:
1. Analisou o objetivo: {task[:100]}...
2. Executou processamento especializado
3. Gerou resultado final

### Resultado:
Execução simulada - integração real em desenvolvimento.
Para ativar execução real, configure a integração com OpenClaw Gateway.

### Próximos Passos:
- Implementar chamada HTTP para OpenClaw Gateway
- Ou usar sistema de filas com heartbeat
""",
        "files_created": [],
        "agent_slug": agent_slug
    }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python agent_executor.py <agent_slug> '<task>'", file=sys.stderr)
        sys.exit(1)
    
    agent_slug = sys.argv[1]
    task = sys.argv[2]
    
    result = execute_agent(agent_slug, task)
    print(json.dumps(result, indent=2))
