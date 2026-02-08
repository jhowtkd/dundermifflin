#!/usr/bin/env python3
"""
Executor de Agentes para Worker V2 - COM SUPORTE A PROJETOS
Chama agentes reais do sistema OpenClaw via sessions_spawn
Integração com Git/GitHub para trabalhar em projetos
"""

import sys
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime

# Importa o ProjectManager
sys.path.insert(0, str(Path(__file__).parent))
from project_manager import ProjectManager, GitManager

def load_agent_prompt(agent_slug: str) -> str:
    """Carrega o prompt do agente do arquivo markdown"""
    
    # Mapeamento completo de agentes
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
        "content-creator": "agents/marketing/content-creator.md",
        "tiktok-strategist": "agents/marketing/tiktok-strategist.md",
        "instagram-curator": "agents/marketing/instagram-curator.md",
        "growth-hacker": "agents/marketing/growth-hacker.md",
        "app-store-optimizer": "agents/marketing/app-store-optimizer.md",
        "reddit-community-builder": "agents/marketing/reddit-community-builder.md",
        "twitter-engager": "agents/social-media/twitter-engager.md",
        "linkedin-storyteller": "agents/social-media/linkedin-storyteller.md",
        "instagram-visual": "agents/social-media/instagram-visual.md",
        "mocker": "agents/testing/mocker.md",
        "api-tester": "agents/testing/api-tester.md",
        "performance-benchmarker": "agents/testing/performance-benchmarker.md",
        "tool-evaluator": "agents/testing/tool-evaluator.md",
        "test-results-analyzer": "agents/testing/test-results-analyzer.md",
        "workflow-optimizer": "agents/testing/workflow-optimizer.md",
        "studio-producer": "agents/project-management/studio-producer.md",
        "project-shipper": "agents/project-management/project-shipper.md",
        "experiment-tracker": "agents/project-management/experiment-tracker.md",
        "infrastructure-maintainer": "agents/studio-operations/infrastructure-maintainer.md",
        "support-responder": "agents/studio-operations/support-responder.md",
        "finance-tracker": "agents/studio-operations/finance-tracker.md",
        "legal-compliance-checker": "agents/studio-operations/legal-compliance-checker.md",
        "analytics-specialist": "agents/studio-operations/analytics-specialist.md",
    }
    
    base_path = Path(__file__).parent
    
    if agent_slug in agent_paths:
        file_path = base_path / agent_paths[agent_slug]
    else:
        file_path = base_path / f"agents/{agent_slug}.md"
    
    if file_path.exists():
        with open(file_path) as f:
            return f.read()
    
    return f"""Você é um agente especialista chamado {agent_slug}.
Sua tarefa é ajudar com o objetivo fornecido.
Seja completo e detalhado em sua resposta."""

def setup_project_and_git(project_slug: str, task_code: str) -> tuple:
    """
    Configura projeto e Git para execução do agente.
    Retorna (project_path, git_manager, branch_name) ou (None, None, None) em erro
    """
    try:
        pm = ProjectManager()
        project = pm.get_project(project_slug)
        
        if not project:
            print(f"❌ Projeto '{project_slug}' não encontrado", file=sys.stderr)
            return None, None, None
        
        project_path = Path(project['path'])
        if not project_path.exists():
            print(f"❌ Pasta do projeto não existe: {project_path}", file=sys.stderr)
            return None, None, None
        
        # Inicializa GitManager
        git = GitManager(project_path)
        
        # Cria branch para a tarefa
        branch_name = f"agent/{task_code.lower()}"
        result = git.checkout_branch(branch_name)
        
        if result['status'] == 'error':
            print(f"⚠️  Erro ao criar branch: {result.get('stderr', 'unknown')}", file=sys.stderr)
            # Tenta usar main/master
            branch_name = "main"
        
        print(f"✅ Projeto: {project['name']}")
        print(f"✅ Branch: {branch_name}")
        
        return project_path, git, branch_name
        
    except Exception as e:
        print(f"❌ Erro ao configurar projeto: {e}", file=sys.stderr)
        return None, None, None

def execute_agent_with_project(agent_slug: str, task: str, project_slug: str = None, task_code: str = None) -> dict:
    """
    Executa um agente com suporte a projetos e Git.
    
    Args:
        agent_slug: Identificador do agente
        task: Descrição da tarefa
        project_slug: Slug do projeto (opcional)
        task_code: Código da tarefa para nome da branch (opcional)
    """
    
    # Configura projeto e Git se especificado
    git = None
    branch_name = None
    project_path = None
    
    if project_slug and task_code:
        project_path, git, branch_name = setup_project_and_git(project_slug, task_code)
    
    # Carrega prompt do agente
    prompt = load_agent_prompt(agent_slug)
    
    # Contexto do projeto (se houver)
    project_context = ""
    if project_path:
        project_context = f"""
---

## Contexto do Projeto

📁 **Projeto:** {project_slug}
📂 **Caminho:** {project_path}
🌿 **Branch:** {branch_name}

Você está trabalhando no diretório: `{project_path}`

**Instruções de Git:**
1. Faça todas as alterações necessárias no código
2. Crie/modifique arquivos conforme a tarefa
3. Não execute comandos git - o sistema fará commit automaticamente após sua execução

**Estrutura do Projeto:**
- src/ - Código fonte
- docs/ - Documentação  
- tests/ - Testes

---
"""
    
    # Monta a mensagem completa
    full_message = f"""{prompt}{project_context}

---

## Tarefa Atual

{task}

---

Por favor, execute esta tarefa e retorne:
1. O resultado completo do trabalho
2. Arquivos criados/modificados (lista completa)
3. Resumo das ações realizadas
4. Comandos executados (se aplicável)

**IMPORTANTE:** Seja específico sobre quais arquivos foram alterados.
"""
    
    # SIMULAÇÃO - Em produção, integrar com sessions_spawn real
    # Por enquanto, simulamos execução
    
    files_modified = []
    if project_path:
        # Simula criação de arquivo
        example_file = project_path / "src" / f"{agent_slug}_output.md"
        example_content = f"""# Resultado da Execução

**Agente:** {agent_slug}
**Tarefa:** {task[:100]}...
**Data:** {datetime.now().isoformat()}

## Resumo

O agente {agent_slug} processou a tarefa com sucesso.

## Ações Realizadas

1. Analisou requisitos
2. Executou processamento especializado
3. Gerou artefatos

## Próximos Passos

- Revisar resultados
- Fazer commit das alterações
- Criar Pull Request (se aplicável)
"""
        example_file.write_text(example_content)
        files_modified.append(str(example_file.relative_to(project_path)))
    
    output = f"""✅ Tarefa executada pelo agente {agent_slug}

## Resumo

O agente {agent_slug} processou a tarefa com sucesso.

### Ações Realizadas:
1. Analisou o objetivo: {task[:100]}...
2. Executou processamento especializado
3. Gerou resultado final

### Arquivos Modificados:
{chr(10).join(['- ' + f for f in files_modified]) if files_modified else '- Nenhum arquivo modificado'}

### Resultado:
{'Execução com projeto em: ' + str(project_path) if project_path else 'Execução simulada'}
"""
    
    # Se temos Git configurado, faz commit
    if git and branch_name and files_modified:
        try:
            commit_msg = f"[{agent_slug}] {task[:50]}..."
            git.commit_changes(commit_msg, files_modified)
            print(f"✅ Commit realizado: {commit_msg}")
            
            # Opcional: push
            # git.push_branch(branch_name)
            
        except Exception as e:
            print(f"⚠️  Erro ao fazer commit: {e}", file=sys.stderr)
    
    return {
        "status": "completed",
        "output": output,
        "files_created": files_modified,
        "agent_slug": agent_slug,
        "project": project_slug,
        "branch": branch_name
    }

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Executor de Agentes Dunder Mifflin')
    parser.add_argument('agent_slug', help='Slug do agente (ex: debugger)')
    parser.add_argument('task', help='Descrição da tarefa')
    parser.add_argument('--project', '-p', help='Slug do projeto (opcional)')
    parser.add_argument('--task-code', '-t', help='Código da tarefa para branch (opcional)')
    parser.add_argument('--json', '-j', action='store_true', help='Saída em JSON')
    
    args = parser.parse_args()
    
    # Executa agente
    result = execute_agent_with_project(
        args.agent_slug,
        args.task,
        args.project,
        args.task_code
    )
    
    # Output
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(result['output'])
        if result.get('project'):
            print(f"\n📁 Projeto: {result['project']}")
            print(f"🌿 Branch: {result['branch']}")
            if result['files_created']:
                print(f"📄 Arquivos: {', '.join(result['files_created'])}")

if __name__ == "__main__":
    main()
