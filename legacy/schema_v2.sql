-- Dunder Mifflin V2 - Sistema de Squads, Serviços e Orquestração
-- Schema atualizado para suportar agentes em grupos com mestres

-- ============================================================
-- TABELAS EXISTENTES (mantidas para compatibilidade)
-- ============================================================

-- Departments (9 departamentos Jules)
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    emoji TEXT NOT NULL DEFAULT '📁',
    description TEXT,
    agent_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Agents (52+ agentes Jules)
CREATE TABLE IF NOT EXISTS agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    department TEXT NOT NULL DEFAULT 'general',
    role TEXT,
    description TEXT,
    capabilities TEXT, -- JSON array
    avatar_emoji TEXT DEFAULT '🤖',
    file_path TEXT,
    is_active BOOLEAN DEFAULT 1,
    priority INTEGER DEFAULT 5,
    daily_quota INTEGER DEFAULT 10,
    quota_used INTEGER DEFAULT 0,
    missions_completed INTEGER DEFAULT 0,
    last_active_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department) REFERENCES departments(slug)
);

-- Personas
CREATE TABLE IF NOT EXISTS personas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    avatar_emoji TEXT NOT NULL,
    agent_id INTEGER,
    catch_phrase TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);

-- Commands
CREATE TABLE IF NOT EXISTS commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    command_type TEXT DEFAULT 'simple',
    agents TEXT,
    parameters TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Mission Proposals
CREATE TABLE IF NOT EXISTS proposals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proposal_code TEXT UNIQUE NOT NULL,
    agent_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    mission_type TEXT DEFAULT 'general',
    priority INTEGER DEFAULT 5,
    parameters TEXT,
    status TEXT DEFAULT 'pending',
    proposed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reviewed_at DATETIME,
    reviewed_by TEXT,
    review_notes TEXT,
    auto_approved BOOLEAN DEFAULT 0,
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);

-- Missions
CREATE TABLE IF NOT EXISTS missions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_code TEXT UNIQUE NOT NULL,
    proposal_id INTEGER,
    agent_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    mission_type TEXT DEFAULT 'general',
    priority INTEGER DEFAULT 5,
    status TEXT DEFAULT 'approved',
    started_at DATETIME,
    completed_at DATETIME,
    result TEXT,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (proposal_id) REFERENCES proposals(id),
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);

-- Mission Steps
CREATE TABLE IF NOT EXISTS steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,
    step_number INTEGER NOT NULL,
    step_code TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    action_type TEXT,
    action_config TEXT,
    status TEXT DEFAULT 'queued',
    started_at DATETIME,
    completed_at DATETIME,
    input_data TEXT,
    output_data TEXT,
    error_details TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    FOREIGN KEY (mission_id) REFERENCES missions(id)
);

-- Events
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_code TEXT UNIQUE NOT NULL,
    event_type TEXT NOT NULL,
    severity TEXT DEFAULT 'info',
    agent_id INTEGER,
    mission_id INTEGER,
    step_id INTEGER,
    proposal_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    payload TEXT,
    occurred_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id),
    FOREIGN KEY (mission_id) REFERENCES missions(id)
);

-- Memories
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_code TEXT UNIQUE NOT NULL,
    agent_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    memory_type TEXT DEFAULT 'short_term',
    context TEXT,
    tags TEXT,
    importance INTEGER DEFAULT 5,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);

-- ============================================================
-- NOVAS TABELAS V2 - SQUADS E ORQUESTRAÇÃO
-- ============================================================

-- Squads - Grupos de agentes especializados com um mestre
CREATE TABLE IF NOT EXISTS squads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    emoji TEXT DEFAULT '👥',
    color TEXT DEFAULT '#3B82F6', -- cor para UI
    master_agent_id INTEGER NOT NULL, -- agente mestre/orquestrador
    capabilities TEXT, -- JSON array de capacidades do squad
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (master_agent_id) REFERENCES agents(id)
);

-- Squad Members - Relacionamento many-to-many entre squads e agentes
CREATE TABLE IF NOT EXISTS squad_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    squad_id INTEGER NOT NULL,
    agent_id INTEGER NOT NULL,
    role_in_squad TEXT DEFAULT 'member', -- member, specialist, reviewer
    order_index INTEGER DEFAULT 0, -- ordem de execução no fluxo
    can_loop BOOLEAN DEFAULT 0, -- se este agente pode ser repetido no fluxo
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (squad_id) REFERENCES squads(id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
    UNIQUE(squad_id, agent_id)
);

-- Services - Serviços configuráveis com fluxo de agentes
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    emoji TEXT DEFAULT '⚙️',
    squad_id INTEGER, -- squad responsável (opcional)
    input_schema TEXT, -- JSON schema para entrada
    output_schema TEXT, -- JSON schema para saída
    config TEXT, -- JSON com configurações diversas
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (squad_id) REFERENCES squads(id)
);

-- Service Steps - Passos sequenciais de um serviço
CREATE TABLE IF NOT EXISTS service_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER NOT NULL,
    step_number INTEGER NOT NULL,
    agent_id INTEGER NOT NULL, -- agente responsável por este passo
    title TEXT NOT NULL,
    description TEXT,
    instructions TEXT, -- instruções específicas para o agente
    input_mapping TEXT, -- JSON: como mapear inputs para este step
    output_mapping TEXT, -- JSON: como mapear outputs deste step
    is_loop_enabled BOOLEAN DEFAULT 0, -- se permite loop/repetição
    loop_condition TEXT, -- condição para repetir (ex: "quality < 0.8")
    max_loops INTEGER DEFAULT 1,
    on_failure TEXT DEFAULT 'stop', -- stop, continue, retry
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES agents(id),
    UNIQUE(service_id, step_number)
);

-- Plans - Planos de execução criados pelo master para aprovação
CREATE TABLE IF NOT EXISTS plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_code TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    service_id INTEGER, -- serviço associado (opcional)
    squad_id INTEGER, -- squad responsável
    master_agent_id INTEGER NOT NULL, -- master que criou o plano
    status TEXT DEFAULT 'draft', -- draft, pending_approval, approved, rejected, executing, completed, failed
    input_data TEXT, -- JSON: dados de entrada
    planned_steps TEXT, -- JSON: array de steps planejados
    estimated_duration INTEGER, -- em minutos
    estimated_cost INTEGER, -- em tokens/créditos (se aplicável)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    submitted_at DATETIME,
    approved_at DATETIME,
    approved_by TEXT,
    approval_notes TEXT,
    started_at DATETIME,
    completed_at DATETIME,
    result TEXT, -- JSON: resultado final
    FOREIGN KEY (service_id) REFERENCES services(id),
    FOREIGN KEY (squad_id) REFERENCES squads(id),
    FOREIGN KEY (master_agent_id) REFERENCES agents(id)
);

-- Service Executions - Execuções concretas de serviços
CREATE TABLE IF NOT EXISTS service_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_code TEXT UNIQUE NOT NULL,
    service_id INTEGER NOT NULL,
    plan_id INTEGER, -- plano associado (se houver)
    title TEXT NOT NULL,
    input_data TEXT, -- JSON: dados de entrada
    status TEXT DEFAULT 'pending', -- pending, running, waiting_approval, succeeded, failed, cancelled
    current_step INTEGER DEFAULT 0,
    total_steps INTEGER DEFAULT 0,
    loop_count INTEGER DEFAULT 0,
    output_data TEXT, -- JSON: resultado final
    started_at DATETIME,
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (service_id) REFERENCES services(id),
    FOREIGN KEY (plan_id) REFERENCES plans(id)
);

-- Execution Steps - Steps individuais de uma execução
CREATE TABLE IF NOT EXISTS execution_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id INTEGER NOT NULL,
    service_step_id INTEGER NOT NULL,
    step_number INTEGER NOT NULL,
    agent_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    status TEXT DEFAULT 'pending', -- pending, running, waiting_review, succeeded, failed, skipped, looped
    input_data TEXT,
    output_data TEXT,
    started_at DATETIME,
    completed_at DATETIME,
    review_requested_at DATETIME,
    review_completed_at DATETIME,
    review_notes TEXT,
    loop_iteration INTEGER DEFAULT 0,
    FOREIGN KEY (execution_id) REFERENCES service_executions(id) ON DELETE CASCADE,
    FOREIGN KEY (service_step_id) REFERENCES service_steps(id),
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);

-- Agent Messages - Mensagens entre agentes (chat/conversa)
CREATE TABLE IF NOT EXISTS agent_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_code TEXT UNIQUE NOT NULL,
    from_agent_id INTEGER NOT NULL,
    to_agent_id INTEGER, -- null = broadcast para o squad
    squad_id INTEGER, -- se for mensagem dentro de um squad
    execution_id INTEGER, -- se relacionada a uma execução
    message_type TEXT DEFAULT 'text', -- text, request, response, review, decision
    content TEXT NOT NULL,
    context TEXT, -- JSON: contexto adicional
    is_read BOOLEAN DEFAULT 0,
    parent_message_id INTEGER, -- para threads/conversas
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_agent_id) REFERENCES agents(id),
    FOREIGN KEY (to_agent_id) REFERENCES agents(id),
    FOREIGN KEY (squad_id) REFERENCES squads(id),
    FOREIGN KEY (execution_id) REFERENCES service_executions(id),
    FOREIGN KEY (parent_message_id) REFERENCES agent_messages(id)
);

-- Reviews - Pontos de revisão/revisão humana no fluxo
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_code TEXT UNIQUE NOT NULL,
    plan_id INTEGER, -- se for revisão de plano
    execution_id INTEGER, -- se for revisão de execução
    execution_step_id INTEGER, -- se for revisão de step específico
    reviewer_type TEXT DEFAULT 'human', -- human, master_agent
    status TEXT DEFAULT 'pending', -- pending, approved, rejected, needs_changes
    title TEXT NOT NULL,
    description TEXT,
    content_to_review TEXT, -- JSON: o que precisa ser revisado
    review_notes TEXT,
    requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES plans(id),
    FOREIGN KEY (execution_id) REFERENCES service_executions(id),
    FOREIGN KEY (execution_step_id) REFERENCES execution_steps(id)
);

-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_missions_status ON missions(status);
CREATE INDEX IF NOT EXISTS idx_missions_agent ON missions(agent_id);
CREATE INDEX IF NOT EXISTS idx_proposals_status ON proposals(status);
CREATE INDEX IF NOT EXISTS idx_steps_mission ON steps(mission_id);
CREATE INDEX IF NOT EXISTS idx_events_occurred ON events(occurred_at);
CREATE INDEX IF NOT EXISTS idx_agents_department ON agents(department);
CREATE INDEX IF NOT EXISTS idx_personas_agent ON personas(agent_id);

-- Novos indexes
CREATE INDEX IF NOT EXISTS idx_squads_master ON squads(master_agent_id);
CREATE INDEX IF NOT EXISTS idx_squad_members_squad ON squad_members(squad_id);
CREATE INDEX IF NOT EXISTS idx_service_steps_service ON service_steps(service_id);
CREATE INDEX IF NOT EXISTS idx_plans_status ON plans(status);
CREATE INDEX IF NOT EXISTS idx_plans_squad ON plans(squad_id);
CREATE INDEX IF NOT EXISTS idx_executions_status ON service_executions(status);
CREATE INDEX IF NOT EXISTS idx_execution_steps_execution ON execution_steps(execution_id);
CREATE INDEX IF NOT EXISTS idx_agent_messages_squad ON agent_messages(squad_id);
CREATE INDEX IF NOT EXISTS idx_agent_messages_from ON agent_messages(from_agent_id);
CREATE INDEX IF NOT EXISTS idx_reviews_status ON reviews(status);

-- ============================================================
-- SEED DATA
-- ============================================================

-- Seed Departments
INSERT OR IGNORE INTO departments (slug, name, emoji, description) VALUES
    ('autonomous', 'Autônomos', '🤖', 'Agentes de qualidade de código e otimização'),
    ('development', 'Desenvolvimento', '💻', 'Construção de features e arquitetura'),
    ('design', 'Design', '🎨', 'Visual, UX e interfaces'),
    ('marketing', 'Marketing', '📢', 'Growth, social e conteúdo'),
    ('product', 'Produto', '📦', 'Pesquisa e priorização'),
    ('project-management', 'Gestão de Projetos', '📋', 'Coordenação e entregas'),
    ('studio-operations', 'Operações', '⚙️', 'Analytics, finanças e suporte'),
    ('testing', 'Testes', '🧪', 'QA e qualidade'),
    ('bonus', 'Bonus', '🎁', 'Agentes especiais');

-- Seed Personas (personagens The Office)
INSERT OR IGNORE INTO personas (slug, name, avatar_emoji, catch_phrase) VALUES
    ('michael', 'Michael Scott', '👔', 'That''s what she said!'),
    ('dwight', 'Dwight Schrute', '👓', 'Bears. Beets. Battlestar Galactica.'),
    ('jim', 'Jim Halpert', '😐', '*looks at camera*'),
    ('pam', 'Pam Beesly', '🎨', 'Dunder Mifflin, this is Pam.'),
    ('stanley', 'Stanley Hudson', '🥨', 'Did I stutter?'),
    ('angela', 'Angela Martin', '🐈', 'I don''t back down.'),
    ('kevin', 'Kevin Malone', '🍲', 'Why waste time say lot word?'),
    ('oscar', 'Oscar Martinez', '📊', 'Actually...');

-- Seed Squads (grupos especializados)
INSERT OR IGNORE INTO squads (slug, name, description, emoji, color, master_agent_id, capabilities) VALUES
    ('content-factory', 'Fábrica de Conteúdo', 'Criação de conteúdo para redes sociais e blogs', '✍️', '#10B981', 0, '["writing", "seo", "social_media", "content_strategy"]'),
    ('code-guardians', 'Guardiões do Código', 'Code review, refatoração e otimização', '🛡️', '#3B82F6', 0, '["code_review", "refactoring", "optimization", "security"]'),
    ('ux-squad', 'Esquadrão UX', 'Pesquisa, design e escrita UX', '🎨', '#8B5CF6', 0, '["ux_research", "ui_design", "ux_writing", "accessibility"]'),
    ('growth-team', 'Time de Growth', 'Growth hacking e marketing', '📈', '#F59E0B', 0, '["growth", "analytics", "experiments", "conversion"]'),
    ('qa-squad', 'Esquadrão QA', 'Testes e garantia de qualidade', '🧪', '#EF4444', 0, '["testing", "automation", "performance", "security_testing"]'),
    ('devops-crew', 'Crew DevOps', 'Infra, CI/CD e operações', '⚙️', '#6B7280', 0, '["infrastructure", "cicd", "monitoring", "deployment"]');
