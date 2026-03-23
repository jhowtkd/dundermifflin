#!/usr/bin/env python3
"""
Executor de Agentes para Worker V2 - COM SUPORTE A PROJETOS
Chama agentes reais do sistema OpenClaw via sessions_spawn
Integração com Git/GitHub para trabalhar em projetos
"""

import sys
import json
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
            print(f"[ERRO] Projeto '{project_slug}' não encontrado", file=sys.stderr)
            return None, None, None
        
        project_path = Path(project['path'])
        if not project_path.exists():
            print(f"[ERRO] Pasta do projeto não existe: {project_path}", file=sys.stderr)
            return None, None, None
        
        # Inicializa GitManager
        git = GitManager(project_path)
        
        # Cria branch para a tarefa
        branch_name = f"agent/{task_code.lower()}"
        result = git.checkout_branch(branch_name)
        
        if result['status'] == 'error':
            print(f"[AVISO]  Erro ao criar branch: {result.get('stderr', 'unknown')}", file=sys.stderr)
            # Tenta usar main/master
            branch_name = "main"
        
        print(f"[OK] Projeto: {project['name']}")
        print(f"[OK] Branch: {branch_name}")
        
        return project_path, git, branch_name
        
    except Exception as e:
        print(f"[ERRO] Erro ao configurar projeto: {e}", file=sys.stderr)
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

[PASTA] **Projeto:** {project_slug}
📂 **Caminho:** {project_path}
[BRANCH] **Branch:** {branch_name}

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
    full_prompt = f"""{prompt}{project_context}

## Tarefa a Executar

{task}

---

Execute esta tarefa e retorne APENAS o conteúdo solicitado."""
    
    # Chama LLM via cliente unificado (Kimi API > Ollama local)
    try:
        from llm_client import generate_content
        
        llm_output = generate_content(full_prompt, agent_slug)
        
        if not llm_output or len(llm_output) < 50:
            print("[AVISO] Resposta vazia ou muito curta")
            llm_output = "Erro: Resposta insuficiente do LLM"
            
    except Exception as e:
        print(f"[ERRO] Falha ao chamar LLM: {e}")
        llm_output = f"Erro na execução: {str(e)}"
    
    # Se falhou ou veio vazio, tenta fallback simples
    if not llm_output or len(llm_output) < 50 or "Erro:" in llm_output:
        print("[AVISO] Usando conteúdo de fallback")
        llm_output = f"""# Conteúdo Gerado por {agent_slug}

## Tarefa
{task[:100]}...

## Resultado
Este é um conteúdo de exemplo gerado pelo agente {agent_slug}.

Para obter resultados completos, por favor verifique a configuração da API do Gemini.

---
Gerado em: {datetime.now().isoformat()}
"""
    
    # Extrai apenas o conteúdo entre marcadores
    import re
    content_match = re.search(r'===CONTEUDO_INICIO===(.*?)===CONTEUDO_FIM===', llm_output, re.DOTALL)
    if content_match:
        clean_output = content_match.group(1).strip()
    else:
        # Fallback: remove logs conhecidos
        lines = llm_output.split('\n')
        clean_lines = []
        skip_patterns = [
            'Doctor warnings', 'Session store:', 'Sessions listed:',
            'Kind   Key', 'direct agent:', 'group  agent:',
            '◇', '│', '├', '╯', '╮'
        ]
        for line in lines:
            if not any(pattern in line for pattern in skip_patterns):
                clean_lines.append(line)
        clean_output = '\n'.join(clean_lines).strip()
        if not clean_output:
            clean_output = llm_output  # Use tudo se não conseguir limpar
    files_modified = []
    if project_path and clean_output:
        # Salva output em arquivo
        output_file = project_path / "src" / f"{agent_slug}_output.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(clean_output, encoding="utf-8")
        files_modified.append(str(output_file.relative_to(project_path)))
    
    # Monta output
    files_list = chr(10).join(['- ' + f for f in files_modified]) if files_modified else '- Nenhum arquivo modificado'
    output = "[OK] Tarefa executada pelo agente " + agent_slug + "\n\n"
    output += "## Resultado do Gemini Flash 3\n\n"
    output += clean_output + "\n\n"
    output += "### Arquivos Modificados:\n"
    output += files_list
    
    # Se temos Git configurado, faz commit
    if git and branch_name and files_modified:
        try:
            commit_msg = f"[{agent_slug}] {task[:50]}..."
            git.commit_changes(commit_msg, files_modified)
            print(f"[OK] Commit realizado: {commit_msg}")
            
            # Opcional: push
            # git.push_branch(branch_name)
            
        except Exception as e:
            print(f"[AVISO]  Erro ao fazer commit: {e}", file=sys.stderr)
    
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
            print(f"\n[PASTA] Projeto: {result['project']}")
            print(f"[BRANCH] Branch: {result['branch']}")
            if result['files_created']:
                print(f"[ARQUIVO] Arquivos: {', '.join(result['files_created'])}")

if __name__ == "__main__":
    main()
