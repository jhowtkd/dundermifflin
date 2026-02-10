# Auditoria de Interface - Dunder Mifflin

## Contexto
O usuário reportou que a interface atual do Dunder Mifflin não está condizente com o que foi definido anteriormente. Foi feito um desenvolvimento com interface Win95, mas pode haver inconsistências.

## Objetivo da Auditoria
O agente DEV deve auditar a interface do Dunder Mifflin e comparar com as especificações/definições anteriores.

## Especificações Esperadas (baseado em memórias e código)

### 1. Estrutura de Telas
- **Dashboard principal** (`index.html`): Menu de navegação, logo, status do sistema
- **Agents** (`agents.html`): Grid dos 52 agentes organizados por departamentos
- **Missions** (`missions.html`): Lista de missões com filtros por status
- **Mission Detail** (`mission-detail.html`): Detalhes de uma missão específica
- **Proposals** (`proposals.html`): Criar novas propostas de missões
- **Files** (`files.html`): Arquivos gerados pelas missões
- **Services** (`services.html`): Catálogo de 10+ serviços de marketing
- **History** (`history.html`): Histórico de execuções

### 2. Design System Win95
- Cores: `#c0c0c0` (bg), `#000080` (azul título), `#ffffff` (highlight), `#808080` (shadow)
- Fontes: `VT323` (monospace), `Space Grotesk` (sans-serif)
- Elementos: Janelas com bordas 3D, botões com efeito pressed, título gradiente azul
- Layout: Responsivo, mobile-friendly

### 3. Funcionalidades por Tela

#### Dashboard (index.html)
- [ ] Menu com ícones grandes (Agents, Missions, Proposals, Files, Services, History)
- [ ] Status do sistema (API, Worker, Database)
- [ ] Missões recentes
- [ ] Estatísticas rápidas

#### Agents (agents.html)
- [ ] Grid de agentes por departamento
- [ ] Ícone/avatar para cada agente
- [ ] Nome e descrição curta
- [ ] Filtro por departamento
- [ ] 52 agentes totais

#### Missions (missions.html)
- [ ] Lista de missões com paginação
- [ ] Filtros: status (pending, approved, running, succeeded, failed)
- [ ] Badge de prioridade
- [ ] Botão "Ver Detalhes"
- [ ] Criar nova missão

#### Mission Detail (mission-detail.html)
- [ ] Informações da missão (título, tipo, status, prioridade)
- [ ] Steps da execução
- [ ] Logs/output
- [ ] Arquivos gerados
- [ ] Ações (reexecutar, cancelar)

#### Proposals (proposals.html)
- [ ] Formulário de criação
- [ ] Campos: título, tipo, prioridade, descrição, agente
- [ ] Lista de propostas pendentes
- [ ] Botões Aprovar/Rejeitar

#### Services (services.html)
- [ ] 10 serviços de marketing catalogados
- [ ] Cards com ícone, título, descrição
- [ ] Botão "Usar este serviço"

#### Files (files.html)
- [ ] Lista de arquivos gerados
- [ ] Filtro por tipo (carousels, posts, content)
- [ ] Preview/download

#### History (history.html)
- [ ] Timeline de eventos
- [ ] Filtro por tipo (mission_start, mission_complete, error)

### 4. Integração API
- [ ] Todas as telas chamam `API_BASE = http://100.94.223.52:3003/api`
- [ ] Handles de erro (404, 500, network)
- [ ] Loading states
- [ ] Tratamento de dados vazios

### 5. Navegação
- [ ] Menu lateral ou superior consistente
- [ ] Breadcrumbs onde apropriado
- [ ] Links com extensão `.html` (servidor estático)
- [ ] Voltar à página anterior

## Checklist de Auditoria

### Telas Existentes
1. [ ] Verificar se todas as 8 telas existem
2. [ ] Verificar se os links estão funcionando
3. [ ] Verificar se há navegação entre telas

### Design
1. [ ] Cores conforme especificação Win95
2. [ ] Fontes carregando corretamente
3. [ ] Elementos com bordas 3D
4. [ ] Responsividade em mobile

### Funcionalidades
1. [ ] API respondendo em todas as telas
2. [ ] Dados carregando corretamente
3. [ ] Formulários funcionando
4. [ ] Botões com ações

### Bugs/Issues
- [ ] Listar qualquer erro encontrado
- [ ] Listar inconsistências visuais
- [ ] Listar funcionalidades quebradas

## Entregável
Gerar um relatório completo da auditoria com:
1. **Status Geral** (✅ OK / ⚠️ Problemas / ❌ Quebrado)
2. **Lista de Problemas Encontrados** (por tela)
3. **Recomendações de Correção**
4. **Prioridade de Fixes** (Alta/Média/Baixa)

## Acesso
- Dashboard: http://clawd-b450mhp:8888
- API: http://clawd-b450mhp:3003
- Diretório: /home/clawd/.openclaw/workspace/projects/dunder-mifflin/frontend/

## Notas
- O sistema usa servidor Python estático (`python3 -m http.server`)
- URLs devem ter extensão `.html`
- API Flask roda na porta 3003
- CORS já configurado para aceitar chamadas do frontend