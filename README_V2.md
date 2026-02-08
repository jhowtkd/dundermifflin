# 🏢 Dunder Mifflin V2 - Sistema de Orquestração de Agentes

Sistema de gerenciamento de agentes AI em squads, com mestres orquestradores e fluxos de trabalho colaborativos.

## ✨ Novidades V2

### 1. Squads Especializados (6 grupos)

| Squad | Emoji | Master | Especialidade |
|-------|-------|--------|---------------|
| **Fábrica de Conteúdo** | ✍️ | Content Creator | Posts, blogs, SEO |
| **Guardiões do Código** | 🛡️ | Code Reviewer | Review, refatoração, segurança |
| **Esquadrão UX** | 🎨 | UX Researcher | Pesquisa, design, acessibilidade |
| **Time de Growth** | 📈 | Growth Hacker | Marketing, analytics, experimentos |
| **Esquadrão QA** | 🧪 | Tester | Testes, performance, qualidade |
| **Crew DevOps** | ⚙️ | CI/CD Engineer | Infra, deploy, monitoramento |

### 2. Serviços com Fluxo Sequencial

Serviços pré-configurados com passos sequenciais:
- **Post LinkedIn**: Pesquisa → Rascunho → Revisão → Polimento
- **Code Review**: Análise → Segurança → Otimização → Limpeza
- **Landing Page**: Pesquisa → Copy → Design → Polimento
- **Experimento Growth**: Hipótese → Analytics → Assets → Documentação
- **Suíte QA**: Testes → API → Performance → Análise
- **Pipeline Deploy**: CI/CD → Check → Deploy → Monitoramento

### 3. Planos com Aprovação

Fluxo completo:
1. Você cria uma solicitação (plano)
2. O **Master do Squad** analisa e estrutura o fluxo
3. Você **aprova ou rejeita** o plano antes da execução
4. Após aprovação, os agentes executam sequencialmente
5. Você pode acompanhar a conversa entre os agentes em tempo real

### 4. Mensagens entre Agentes

Os agentes conversam entre si durante a execução:
- Master delega tarefas
- Especialistas reportam progresso
- Revisores dão feedback
- Decisões são tomadas colaborativamente

## 🚀 Como Usar

### Iniciar o Sistema

```bash
# 1. Garantir que os agentes Jules estão importados
python3 import_jules.py

# 2. Popular squads e serviços
python3 seed_squads_v2.py

# 3. Iniciar a API
python3 start_v2.py
```

Acesse: http://localhost:3003

### Criar um Plano

1. Vá em **Serviços** e escolha um (ex: "Post para LinkedIn")
2. Preencha o título e descrição
3. O Master criará um plano com o fluxo de trabalho
4. Você recebe o plano para **aprovação**
5. Após aprovar, a execução começa automaticamente

### Acompanhar Execução

Na aba **Execuções** você vê:
- Progresso em tempo real
- Qual agente está trabalhando
- Conversa entre os agentes
- Resultados parciais

## 📁 Estrutura do Projeto

```
dundermifflin/
├── api_v2.py              # API Flask V2
├── schema_v2.sql          # Schema do banco V2
├── seed_squads_v2.py      # Popula squads e serviços
├── start_v2.py            # Script de inicialização
├── frontend/
│   └── v2/
│       └── index.html     # Interface minimalista
└── dunder_mifflin.db      # Banco SQLite
```

## 🔌 API Endpoints

### Squads
- `GET /api/v2/squads` - Lista todos os squads
- `GET /api/v2/squads/:slug` - Detalhes de um squad
- `POST /api/v2/squads` - Cria novo squad

### Serviços
- `GET /api/v2/services` - Lista todos os serviços
- `GET /api/v2/services/:slug` - Detalhes de um serviço com fluxo
- `POST /api/v2/services` - Cria novo serviço

### Planos
- `GET /api/v2/plans` - Lista planos
- `GET /api/v2/plans/:code` - Detalhes do plano
- `POST /api/v2/plans` - Cria novo plano
- `POST /api/v2/plans/:code/submit` - Submete para aprovação
- `POST /api/v2/plans/:code/approve` - Aprova plano
- `POST /api/v2/plans/:code/reject` - Rejeita plano

### Execuções
- `GET /api/v2/executions` - Lista execuções
- `GET /api/v2/executions/:code` - Detalhes com steps e mensagens
- `POST /api/v2/executions/:code/next` - Avança para próximo step

### Mensagens
- `GET /api/v2/messages` - Lista mensagens
- `POST /api/v2/messages` - Cria mensagem entre agentes

## 🎨 Interface

A nova interface é minimalista e retrô:
- **Sidebar** com navegação por abas
- **Cores escuras** com acentos verdes
- **Fonte monospace** para código e identificadores
- **Cards limpos** sem bordas excessivas
- **Estados visuais** claros para cada situação

## 🔄 Fluxo Completo

```
┌─────────────┐
│   Serviço   │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│ Novo Plano  │────▶│   Draft     │
└─────────────┘     └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Submit    │
                    └──────┬──────┘
                           │
                           ▼
┌─────────────┐     ┌─────────────┐
│  Rejeitar   │◀────│  Pendente   │
└─────────────┘     └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐     ┌─────────────┐
                    │  Aprovar    │────▶│  Executando │
                    └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │  Concluído  │
                                        └─────────────┘
```

## 🛠️ Configuração

Variáveis de ambiente:
```bash
DM_API_PORT=3003    # Porta da API
```

## 📊 Banco de Dados

Tabelas principais:
- `squads` - Grupos de agentes
- `squad_members` - Relação squad-agente
- `services` - Serviços configuráveis
- `service_steps` - Passos de cada serviço
- `plans` - Planos de execução
- `service_executions` - Execuções concretas
- `execution_steps` - Steps individuais
- `agent_messages` - Mensagens entre agentes
