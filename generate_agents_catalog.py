#!/usr/bin/env python3
"""
Gera catálogo completo de agentes com departamentos, descrições e exemplos
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime

AGENTS_DIR = Path(__file__).parent / "agents"
OUTPUT_DIR = Path(__file__).parent / "docs"

# Estrutura de departamentos
DEPARTMENTS = {
    "autonomous": {
        "name": "Agentes Autônomos",
        "icon": "🤖",
        "description": "Agentes que operam de forma autônoma, sem intervenção humana"
    },
    "development": {
        "name": "Desenvolvimento",
        "icon": "💻",
        "description": "Especialistas em código, arquitetura e desenvolvimento de software"
    },
    "design": {
        "name": "Design & UX",
        "icon": "🎨",
        "description": "Criação de interfaces, experiência do usuário e identidade visual"
    },
    "product": {
        "name": "Produto",
        "icon": "📦",
        "description": "Pesquisa, priorização e estratégia de produto"
    },
    "marketing": {
        "name": "Marketing & Growth",
        "icon": "📢",
        "description": "Estratégias de marketing, conteúdo e crescimento"
    },
    "project-management": {
        "name": "Gestão de Projetos",
        "icon": "📊",
        "description": "Coordenação de projetos, sprints e entregas"
    },
    "social-media": {
        "name": "Social Media",
        "icon": "📱",
        "description": "Criação de conteúdo para redes sociais"
    },
    "testing": {
        "name": "Testes & QA",
        "icon": "🧪",
        "description": "Testes de software, qualidade e automação"
    },
    "studio-operations": {
        "name": "Operações do Studio",
        "icon": "🏢",
        "description": "Operações internas e suporte ao studio"
    },
    "tools": {
        "name": "Ferramentas",
        "icon": "🛠️",
        "description": "Utilitários e ferramentas especializadas"
    }
}

def extract_agent_info(file_path: Path, dept: str) -> dict:
    """Extrai informações do arquivo markdown do agente"""
    
    content = file_path.read_text(encoding='utf-8')
    
    # Extrai nome do título (# Nome 🐛)
    name_match = re.search(r'^#\s+(.+?)(?:\s+[-–])', content, re.MULTILINE)
    if not name_match:
        name_match = re.search(r'^#\s+(.+?)(?:\s+[🐛🔍🧪🔬💻🎨📦📢🤖⚡🛡️🧹🔄🚀♿🌍🖼️✨📝🛡️📖✨🗄️🔌📱📊🔗🧭⚙️🔧🧪🎭🔥📈📧🤝📋⚠️🚀🔀🐙🎬🎪🎪🔍📊🎮💬🎥📸🎨🐦💼📖🔗🔮🔍🗃️🐚🔀📋🐍🎭📊🔧🔄])?', content, re.MULTILINE)
    name = name_match.group(1).strip() if name_match else file_path.stem
    
    # Extrai descrição do ## Identidade ou primeiro parágrafo
    identity_match = re.search(r'##\s*Identidade\s*\n\s*\n?Você é \*\*(.+?)\*\*[-–](.+?)(?:\n\n|\Z)', content, re.DOTALL)
    if identity_match:
        description = identity_match.group(2).strip()
        # Limpa formatação markdown
        description = re.sub(r'\*\*', '', description)
        description = re.sub(r'\s+', ' ', description)
        description = description[:200]  # Limita tamanho
    else:
        # Tenta primeiro parágrafo
        para_match = re.search(r'^([A-Z][^.]+\.(?:\s+[A-Z][^.]+\.){0,2})', content, re.MULTILINE)
        description = para_match.group(1).strip() if para_match else f"Agente especializado em {file_path.stem.replace('-', ' ')}"
    
    # Extrai exemplo prático de ## Processo Diário ou ## Quando Usar
    example = None
    
    # Tenta encontrar exemplo em Processo Diário
    process_match = re.search(r'###\s*\d+\.\s*\w+.+?\n\s*\n?(-\s+\[.+?\n)+', content, re.DOTALL)
    if process_match:
        lines = process_match.group(0).split('\n')
        tasks = [re.sub(r'^-\s*\[.\]\s*', '', line).strip() for line in lines if line.strip().startswith('-')]
        if tasks:
            example = f"Exemplo: {tasks[0]}"
    
    # Se não achou, tenta exemplo genérico
    if not example:
        example_match = re.search(r'##\s*Exemplo\s*\n(.+?)(?:\n##|\Z)', content, re.DOTALL)
        if example_match:
            example = example_match.group(1).strip()[:300]
        else:
            # Cria exemplo baseado no nome
            examples_map = {
                "debugger": "Investiga um bug reportado em produção e identifica a causa raiz",
                "tester": "Cria testes unitários para uma nova feature antes do deploy",
                "code-reviewer": "Revisa um PR crítico antes do merge na main",
                "architect": "Projeta a arquitetura para um novo microserviço",
                "researcher": "Pesquisa tendências de mercado para nova funcionalidade",
                "copywriter": "Escreve copy para landing page de lançamento",
                "seo-specialist": "Otimiza meta tags e estrutura de URLs para SEO",
                "twitter-engager": "Cria thread sobre novo recurso do produto",
                "linkedin-storyteller": "Escreve post sobre case de sucesso do cliente",
                "bolt": "Otimiza performance de queries lentas no banco",
                "sentinel": "Audita segurança do código buscando vulnerabilidades",
                "janitor": "Remove código morto e dependências não utilizadas",
                "migrator": "Migra componentes de Vue 2 para Vue 3",
                "ui-designer": "Cria mockups para nova tela de onboarding",
                "ux-researcher": "Conduz entrevistas com usuários sobre nova feature",
                "mermaid-architect": "Gera diagrama de arquitetura do sistema",
            }
            example = examples_map.get(file_path.stem, f"Executa tarefas especializadas de {file_path.stem.replace('-', ' ')}")
    
    return {
        "slug": file_path.stem,
        "name": name,
        "department": dept,
        "department_info": DEPARTMENTS.get(dept, {}),
        "description": description,
        "example": example,
        "file": str(file_path.relative_to(AGENTS_DIR.parent))
    }

def scan_agents():
    """Escaneia todos os agentes nos departamentos"""
    agents = []
    
    for dept_dir in AGENTS_DIR.iterdir():
        if not dept_dir.is_dir():
            continue
        
        dept = dept_dir.name
        if dept not in DEPARTMENTS:
            continue
        
        for agent_file in dept_dir.glob("*.md"):
            if agent_file.name in ["README.md", "COMMANDS.md", "INDEX.md"]:
                continue
            
            try:
                agent_info = extract_agent_info(agent_file, dept)
                agents.append(agent_info)
                print(f"✅ {agent_info['slug']} ({dept})")
            except Exception as e:
                print(f"❌ Erro em {agent_file}: {e}")
    
    return agents

def generate_json_catalog(agents):
    """Gera catálogo em JSON"""
    catalog = {
        "generated_at": datetime.now().isoformat(),
        "total_agents": len(agents),
        "departments": DEPARTMENTS,
        "agents": agents
    }
    
    output_file = OUTPUT_DIR / "agents_catalog.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 JSON gerado: {output_file}")
    return catalog

def generate_markdown_catalog(agents):
    """Gera catálogo em Markdown"""
    
    # Agrupa por departamento
    by_dept = {}
    for agent in agents:
        dept = agent['department']
        if dept not in by_dept:
            by_dept[dept] = []
        by_dept[dept].append(agent)
    
    lines = [
        "# 🤖 Catálogo de Agentes - Dunder Mifflin",
        "",
        f"**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        f"**Total de agentes:** {len(agents)}",
        "",
        "---",
        "",
    ]
    
    for dept_key, dept_info in DEPARTMENTS.items():
        if dept_key not in by_dept:
            continue
        
        dept_agents = by_dept[dept_key]
        icon = dept_info.get('icon', '📁')
        name = dept_info.get('name', dept_key)
        
        lines.extend([
            f"## {icon} {name}",
            f"*{dept_info.get('description', '')}*",
            "",
            f"**{len(dept_agents)} agentes**",
            "",
        ])
        
        for agent in sorted(dept_agents, key=lambda x: x['name']):
            lines.extend([
                f"### {agent['name']}",
                f"**Tag:** `{agent['slug']}` | **Arquivo:** `{agent['file']}`",
                "",
                f"**Descrição:** {agent['description']}",
                "",
                f"**Exemplo prático:** 📝 {agent['example']}",
                "",
            ])
        
        lines.append("---")
        lines.append("")
    
    output_file = OUTPUT_DIR / "AGENTS_CATALOG.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"📄 Markdown gerado: {output_file}")

def generate_quick_reference(agents):
    """Gera referência rápida em formato de tabela"""
    
    lines = [
        "# 📋 Referência Rápida de Agentes",
        "",
        "| Agente | Departamento | Descrição | Exemplo de Uso |",
        "|--------|--------------|-----------|----------------|",
    ]
    
    for agent in sorted(agents, key=lambda x: (x['department'], x['name'])):
        dept_info = DEPARTMENTS.get(agent['department'], {})
        dept_icon = dept_info.get('icon', '')
        dept_name = dept_info.get('name', agent['department'])
        
        # Escapa pipes na descrição
        desc = agent['description'].replace('|', '\\|')[:80]
        example = agent['example'].replace('|', '\\|')[:80]
        
        lines.append(f"| **{agent['name']}** | {dept_icon} {dept_name} | {desc}... | {example}... |")
    
    lines.extend([
        "",
        "---",
        "",
        f"*Total: {len(agents)} agentes*",
    ])
    
    output_file = OUTPUT_DIR / "AGENTS_QUICK_REF.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"📄 Quick Reference gerado: {output_file}")

def main():
    print("🔍 Escaneando agentes...\n")
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    agents = scan_agents()
    
    print(f"\n📊 Total: {len(agents)} agentes encontrados\n")
    
    print("📝 Gerando documentação...")
    generate_json_catalog(agents)
    generate_markdown_catalog(agents)
    generate_quick_reference(agents)
    
    print("\n✅ Catálogo completo gerado!")

if __name__ == "__main__":
    main()
