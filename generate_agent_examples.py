#!/usr/bin/env python3
"""
Gera exemplos práticos específicos para cada agente baseado nas especificações
"""

import os
import json
import re
from pathlib import Path

AGENTS_DIR = Path(__file__).parent / "agents"
OUTPUT_FILE = Path(__file__).parent / "docs" / "agents_examples_proposed.json"

# Exemplos específicos baseados nas especialidades de cada agente
EXAMPLES_MAP = {
    # Agentes Autônomos
    "bolt": "Analisa aplicação React com Lighthouse, identifica bundle de 2MB e propõe code splitting para reduzir para 400KB",
    "sentinel": "Escaneia código em busca de secrets hardcoded, encontra AWS key em commit e abre alerta de segurança",
    "janitor": "Remove 15 dependências não utilizadas do package.json e elimina 3 arquivos de código morto",
    "migrator": "Cria plano de migração de Node 14 para 20, identifica breaking changes e atualiza dependências críticas",
    "optimizer": "Refatora função de processamento de dados de O(n²) para O(n log n), reduzindo tempo de 12s para 800ms",
    "a11y-specialist": "Audita formulário de checkout, encontra labels ausentes e propõe correções para WCAG 2.1 AA",
    "i18n-specialist": "Prepara aplicação para suporte a RTL (árabe/hebraico) e implementa pluralização correta",
    
    # Desenvolvimento
    "debugger": "Investiga erro 500 intermitente em produção, analisa logs e identifica race condition em transação de banco",
    "tester": "Cria suite de testes E2E para fluxo de pagamento com Cypress, cobrindo sucesso e casos de erro",
    "code-reviewer": "Revisa PR de autenticação JWT, identifica vulnerabilidade de timing attack e sugere bcrypt constant-time",
    "architect": "Projeta arquitetura de microserviços para sistema de notificações, definindo APIs e filas de mensageria",
    "fullstack-developer": "Implementa feature de exportação CSV completa: backend endpoint, frontend UI e download progressivo",
    "ai-engineer": "Integra modelo LLM da OpenAI para geração automática de descrições de produtos no e-commerce",
    "database-engineer": "Projeta índices para query de relatório mensal, reduzindo tempo de execução de 45s para 2s",
    "cicd-engineer": "Configura pipeline GitHub Actions com testes, build Docker e deploy automático em staging",
    "api-designer": "Define contrato REST para API de pedidos com versionamento, paginação e documentação OpenAPI",
    "rapid-prototyper": "Cria protótipo funcional de app de tarefas em Next.js + Prisma em 2 horas para validação com cliente",
    
    # Design
    "ui-designer": "Cria design system completo com componentes Figma: botões, inputs, cards e variações de estado",
    "ux-researcher": "Conduz 5 entrevistas com usuários sobre onboarding, sintetiza findings e propõe redesign do fluxo",
    "ux-writer": "Reescreve microcopy de formulário de erro genérico para mensagens claras e orientadas a ação",
    "palette": "Define paleta de cores acessível com contraste WCAG AA e tema escuro automático",
    "polish": "Refina animações de transição entre telas, ajustando easing e duration para sensação de fluidez",
    "brand-guardian": "Revisa landing page garantindo consistência de tipografia, cores e tom de voz da marca",
    "visual-storyteller": "Cria storyboard visual para vídeo de lançamento de produto em 6 cenas",
    "whimsy-injector": "Adiciona micro-interações delight: confete no complete de tarefa e easter eggs em páginas de erro",
    
    # Produto
    "researcher": "Mapeia 10 competidores de ferramenta de email marketing e identifica 3 oportunidades de diferenciação",
    "feedback-synthesizer": "Analisa 50 respostas de NPS, agrupa temas principais e prioriza 5 melhorias de produto",
    "sprint-prioritizer": "Organiza backlog de 30 itens usando RICE scoring e define sprint goal para próximas 2 semanas",
    "trend-researcher": "Analisa tendências de UX em 2025 e propõe 3 features baseadas em padrões emergentes",
    
    # Marketing
    "content-creator": "Cria calendário de conteúdo para Instagram com 12 posts sobre dicas de produtividade",
    "tiktok-strategist": "Cria roteiro de vídeo de 60s sobre 'day in the life de dev' com hooks nos primeiros 3 segundos e call-to-action no final",
    "instagram-curator": "Produz grid de 9 posts com tema 'Behind the Scenes' do desenvolvimento de produto, mantendo consistência visual e cronograma de stories",
    "growth-hacker": "Propõe experimento de viral loop com referral program e calcula potencial de crescimento",
    "app-store-optimizer": "Otimiza descrição e screenshots do app para Play Store, focando em keywords de conversão",
    "reddit-community-builder": "Participa de discussões em r/webdev oferecendo valor e construindo autoridade",
    
    # Social Media
    "twitter-engager": "Cria thread técnica de 10 tweets explicando arquitetura de microsserviços com diagramas",
    "linkedin-storyteller": "Escreve post sobre case de cliente com antes/depois de métricas de performance",
    "instagram-visual": "Produz carrossel de 5 slides com dicas de produtividade usando identidade visual da marca",
    "youtube-scriptwriter": "Roteiriza vídeo tutorial de 10 minutos sobre configuração de CI/CD com GitHub Actions",
    "tiktok-creator": "Cria roteiro de vídeo curto (60s) mostrando life hack de produtividade no VS Code",
    
    # Testes
    "mocker": "Cria factory de dados para testes de usuário com Faker.js, incluindo cenários edge cases",
    "api-tester": "Desenvolve coleção Postman com 50 testes automatizados para API de pagamentos",
    "performance-benchmarker": "Executa testes de carga com k6, identifica gargalo em 1000 req/s e propõe otimização",
    "tool-evaluator": "Compara 3 ferramentas de testes E2E (Cypress, Playwright, Selenium) em critérios objetivos",
    "test-results-analyzer": "Analisa relatório de cobertura de testes, identifica gaps críticos e sugere testes faltantes",
    "workflow-optimizer": "Mapeia processo de code review atual e propõe automações para reduzir tempo de 3 dias para 4h",
    
    # Gestão de Projetos
    "studio-producer": "Coordena lançamento de feature em 3 squads paralelos, gerenciando dependências e riscos",
    "project-shipper": "Prepara checklist de Go Live com rollback plan, comunicação e métricas de sucesso",
    "experiment-tracker": "Define framework de experimentos com hipóteses, métricas north star e critérios de sucesso",
    
    # Operações
    "infrastructure-maintainer": "Configura monitoramento com alerts para CPU >80% e disco >90% em todos os servidores",
    "support-responder": "Cria base de conhecimento com 20 artigos FAQ baseados nos tickets mais frequentes",
    "finance-tracker": "Projeta dashboard financeiro de projeto com burn rate, runway e projeção de custos",
    "legal-compliance-checker": "Audita fluxo de cadastro para LGPD, verificando consentimentos e direito ao esquecimento",
    "analytics-specialist": "Implementa tracking de funil de conversão de signup a primeira compra com Mixpanel",
}

def enhance_catalog_with_examples():
    """Adiciona exemplos específicos ao catálogo existente"""
    
    catalog_path = Path(__file__).parent / "docs" / "agents_catalog.json"
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    enhanced_count = 0
    for agent in catalog['agents']:
        slug = agent['slug']
        if slug in EXAMPLES_MAP:
            agent['example'] = EXAMPLES_MAP[slug]
            enhanced_count += 1
            print(f"✅ {slug}: {EXAMPLES_MAP[slug][:60]}...")
        else:
            print(f"⚠️  {slug}: Sem exemplo específico (mantendo original)")
    
    # Salva catálogo melhorado
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 Total: {enhanced_count}/{len(catalog['agents'])} agentes com exemplos específicos")
    print(f"📄 Salvo em: {OUTPUT_FILE}")
    
    return catalog

def generate_batch_report(catalog, batch_size=5):
    """Gera relatório em lotes de 5 agentes"""
    
    agents = catalog['agents']
    batches = [agents[i:i+batch_size] for i in range(0, len(agents), batch_size)]
    
    reports = []
    for i, batch in enumerate(batches):
        report = f"\n📦 LOTE {i+1}/{len(batches)}\n" + "="*60 + "\n\n"
        
        for agent in batch:
            dept_info = agent.get('department_info', {})
            report += f"🤖 **{agent['name']}**\n"
            report += f"   Tag: `{agent['slug']}` | Dept: {dept_info.get('icon', '')} {dept_info.get('name', '')}\n\n"
            report += f"   📝 **Exemplo Prático:**\n"
            report += f"   {agent.get('example', 'N/A')}\n\n"
            report += "-"*50 + "\n\n"
        
        reports.append(report)
    
    return reports

if __name__ == "__main__":
    print("🎯 Gerando exemplos específicos...\n")
    catalog = enhance_catalog_with_examples()
    
    print("\n" + "="*60)
    print("📋 RELATÓRIO POR LOTES DE 5")
    print("="*60)
    
    reports = generate_batch_report(catalog, batch_size=5)
    
    # Mostra primeiro lote
    print(reports[0])
    
    # Salva todos os lotes em arquivo
    all_batches_file = Path(__file__).parent / "docs" / "AGENTS_EXAMPLES_BATCHES.md"
    with open(all_batches_file, 'w', encoding='utf-8') as f:
        f.write("# 📋 Exemplos Práticos de Agentes - Aprovação por Lotes\n\n")
        f.write(f"**Total de agentes:** {len(catalog['agents'])}\n")
        f.write(f"**Lotes:** {len(reports)}\n\n")
        for report in reports:
            f.write(report)
            f.write("\n---\n\n")
    
    print(f"\n📄 Todos os lotes salvos em: {all_batches_file}")
