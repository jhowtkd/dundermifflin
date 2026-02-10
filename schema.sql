-- Dunder Mifflin + Jules Agents SQLite Schema
-- Sistema de Gerenciamento de Agentes AI

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

-- Agents (52 agentes Jules + expansível)
CREATE TABLE IF NOT EXISTS agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    department TEXT NOT NULL DEFAULT 'general',
    role TEXT,
    description TEXT,
    capabilities TEXT, -- JSON array
    avatar_emoji TEXT DEFAULT '🤖',
    file_path TEXT, -- Path para o .md original
    is_active BOOLEAN DEFAULT 1,
    priority INTEGER DEFAULT 5,
    daily_quota INTEGER DEFAULT 10,
    quota_used INTEGER DEFAULT 0,
    missions_completed INTEGER DEFAULT 0,
    last_active_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department) REFERENCES departments(slug)
);

-- Personas (personagens The Office mapeados para agentes)
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

-- Commands (comandos do COMMANDS.md)
CREATE TABLE IF NOT EXISTS commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL, -- '/review', '/test', etc
    name TEXT NOT NULL,
    description TEXT,
    command_type TEXT DEFAULT 'simple', -- simple, workflow, composition
    agents TEXT, -- JSON array de agent slugs
    parameters TEXT, -- JSON de parâmetros aceitos
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
    parameters TEXT, -- JSON
    status TEXT DEFAULT 'pending', -- pending, accepted, rejected
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
    status TEXT DEFAULT 'approved', -- approved, running, succeeded, failed, cancelled
    started_at DATETIME,
    completed_at DATETIME,
    result TEXT, -- JSON
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
    action_config TEXT, -- JSON
    status TEXT DEFAULT 'queued', -- queued, running, succeeded, failed, skipped
    started_at DATETIME,
    completed_at DATETIME,
    input_data TEXT, -- JSON
    output_data TEXT, -- JSON
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
    severity TEXT DEFAULT 'info', -- debug, info, warning, error, critical
    agent_id INTEGER,
    mission_id INTEGER,
    step_id INTEGER,
    proposal_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    payload TEXT, -- JSON
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
    memory_type TEXT DEFAULT 'short_term', -- short_term, long_term, episodic, semantic
    context TEXT, -- JSON
    tags TEXT, -- JSON array
    importance INTEGER DEFAULT 5,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_missions_status ON missions(status);
CREATE INDEX IF NOT EXISTS idx_missions_agent ON missions(agent_id);
CREATE INDEX IF NOT EXISTS idx_proposals_status ON proposals(status);
CREATE INDEX IF NOT EXISTS idx_steps_mission ON steps(mission_id);
CREATE INDEX IF NOT EXISTS idx_events_occurred ON events(occurred_at);
CREATE INDEX IF NOT EXISTS idx_agents_department ON agents(department);
CREATE INDEX IF NOT EXISTS idx_personas_agent ON personas(agent_id);

-- Seed Departments (9 departamentos Jules)
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

-- ============================================================
-- ORCHESTRATION V2 - 5 Novas Tabelas
-- ============================================================

-- 1. SERVICES (Workflows reutilizáveis)
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    icon_emoji TEXT DEFAULT '⚙️',
    agent_sequence TEXT NOT NULL,      -- JSON: ["researcher", "writer", "reviewer"]
    loop_config TEXT,                   -- JSON: {enabled, max_iterations, until_score}
    requires_approval BOOLEAN DEFAULT 1,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. SERVICE_STEPS (Template de cada step)
CREATE TABLE IF NOT EXISTS service_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER NOT NULL,
    step_order INTEGER NOT NULL,
    agent_slug TEXT NOT NULL,
    step_name TEXT NOT NULL,
    action_type TEXT DEFAULT 'execute',  -- execute, review, transform
    input_mapping TEXT,                   -- JSON
    timeout_seconds INTEGER DEFAULT 300,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
);

-- 3. EXECUTION_PLANS (Planos do Master para aprovação)
CREATE TABLE IF NOT EXISTS execution_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_code TEXT UNIQUE NOT NULL,
    mission_id INTEGER,
    service_id INTEGER,
    title TEXT NOT NULL,
    objective TEXT NOT NULL,
    strategy TEXT,                        -- Explicação do Master
    planned_steps TEXT NOT NULL,          -- JSON detalhado
    estimated_duration_minutes INTEGER,
    status TEXT DEFAULT 'pending_approval',  -- pending_approval → approved → executing → completed/failed
    approved_by TEXT,
    approved_at DATETIME,
    rejection_reason TEXT,
    started_at DATETIME,
    completed_at DATETIME,
    final_result TEXT,
    quality_score INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mission_id) REFERENCES missions(id),
    FOREIGN KEY (service_id) REFERENCES services(id)
);

-- 4. ORCHESTRATION_SESSIONS (Sessão de execução)
CREATE TABLE IF NOT EXISTS orchestration_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_code TEXT UNIQUE NOT NULL,
    execution_plan_id INTEGER NOT NULL,
    status TEXT DEFAULT 'initializing',
    current_step_index INTEGER DEFAULT 0,
    current_agent_id INTEGER,
    shared_context TEXT,                  -- JSON compartilhado entre agentes
    agent_outputs TEXT,                   -- JSON array dos outputs
    current_loop_iteration INTEGER DEFAULT 0,
    started_at DATETIME,
    completed_at DATETIME,
    FOREIGN KEY (execution_plan_id) REFERENCES execution_plans(id)
);

-- 5. AGENT_MESSAGES (Comunicação inter-agentes)
CREATE TABLE IF NOT EXISTS agent_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_code TEXT UNIQUE NOT NULL,
    session_id INTEGER NOT NULL,
    from_agent_id INTEGER,                -- NULL = Master
    to_agent_id INTEGER,                  -- NULL = broadcast
    message_type TEXT NOT NULL,           -- instruction, response, handoff, feedback
    content TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES orchestration_sessions(id) ON DELETE CASCADE
);

-- Indexes para performance
CREATE INDEX IF NOT EXISTS idx_services_slug ON services(slug);
CREATE INDEX IF NOT EXISTS idx_services_active ON services(is_active);
CREATE INDEX IF NOT EXISTS idx_service_steps_service ON service_steps(service_id);
CREATE INDEX IF NOT EXISTS idx_execution_plans_status ON execution_plans(status);
CREATE INDEX IF NOT EXISTS idx_execution_plans_mission ON execution_plans(mission_id);
CREATE INDEX IF NOT EXISTS idx_orchestration_sessions_plan ON orchestration_sessions(execution_plan_id);
CREATE INDEX IF NOT EXISTS idx_orchestration_sessions_status ON orchestration_sessions(status);
CREATE INDEX IF NOT EXISTS idx_agent_messages_session ON agent_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_agent_messages_created ON agent_messages(created_at);

-- ============================================================
-- RALPH SWARM v5.0 - Sistema de Canais (Discord-style)
-- ============================================================

-- 1. SWARM_CHANNELS (Canais como no Discord)
CREATE TABLE IF NOT EXISTS swarm_channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    channel_type TEXT DEFAULT 'text',  -- text, voice, thread
    description TEXT,
    is_private BOOLEAN DEFAULT 0,
    parent_channel_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_channel_id) REFERENCES swarm_channels(id)
);

-- 2. SWARM_MESSAGES (Mensagens nos canais)
CREATE TABLE IF NOT EXISTS swarm_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_code TEXT UNIQUE NOT NULL,
    channel_id INTEGER NOT NULL,
    author_type TEXT NOT NULL,  -- 'user', 'agent', 'system'
    author_id TEXT NOT NULL,    -- user_id ou agent_slug
    content TEXT NOT NULL,
    mentions TEXT,              -- JSON array de mentions
    thread_parent_id INTEGER,   -- Para threads
    attachments TEXT,           -- JSON array de anexos
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    edited_at DATETIME,
    FOREIGN KEY (channel_id) REFERENCES swarm_channels(id),
    FOREIGN KEY (thread_parent_id) REFERENCES swarm_messages(id)
);

-- 3. SWARM_AGENTS (Agents do sistema swarm)
CREATE TABLE IF NOT EXISTS swarm_agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL,         -- coordinator, find, build, create, track, watch
    model_tier TEXT DEFAULT 'medium',  -- cheap, medium, expensive
    personality TEXT,
    avatar_emoji TEXT DEFAULT '🤖',
    memory TEXT,                -- JSON com memória do agent
    status TEXT DEFAULT 'idle', -- idle, busy, offline
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_active_at DATETIME
);

-- 4. SWARM_TASKS (Tarefas em execução)
CREATE TABLE IF NOT EXISTS swarm_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_code TEXT UNIQUE NOT NULL,
    original_request TEXT NOT NULL,
    coordinator_agent_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending, planning, running, synthesizing, completed, failed
    execution_plan TEXT,            -- JSON com plano
    final_output TEXT,
    cost_usd REAL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME,
    FOREIGN KEY (coordinator_agent_id) REFERENCES swarm_agents(id)
);

-- 5. SWARM_TASK_AGENTS (Relação many-to-many tasks <-> agents)
CREATE TABLE IF NOT EXISTS swarm_task_agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    agent_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending, running, completed, failed
    output TEXT,
    started_at DATETIME,
    completed_at DATETIME,
    FOREIGN KEY (task_id) REFERENCES swarm_tasks(id),
    FOREIGN KEY (agent_id) REFERENCES swarm_agents(id)
);

-- Seed Swarm Channels
INSERT OR IGNORE INTO swarm_channels (channel_code, name, channel_type, description) VALUES
    ('orders', 'orders', 'text', 'Entrada de tarefas do usuário'),
    ('agent-chat', 'agent-chat', 'text', 'Coordenação entre agents'),
    ('find-output', 'find-output', 'text', 'Resultados do agent Find'),
    ('find-logs', 'find-logs', 'text', 'Logs do agent Find'),
    ('find-memory', 'find-memory', 'text', 'Memória do agent Find'),
    ('build-output', 'build-output', 'text', 'Resultados do agent Build'),
    ('build-logs', 'build-logs', 'text', 'Logs do agent Build'),
    ('build-memory', 'build-memory', 'text', 'Memória do agent Build'),
    ('create-output', 'create-output', 'text', 'Resultados do agent Create'),
    ('create-logs', 'create-logs', 'text', 'Logs do agent Create'),
    ('create-memory', 'create-memory', 'text', 'Memória do agent Create'),
    ('track-output', 'track-output', 'text', 'Resultados do agent Track'),
    ('watch-output', 'watch-output', 'text', 'Resultados do agent Watch'),
    ('drop-links', 'drop-links', 'text', 'Links para research automático'),
    ('live-feed', 'live-feed', 'text', 'Atividade em tempo real'),
    ('memory', 'memory', 'text', 'Memória compartilhada da equipe');

-- Seed Swarm Agents
INSERT OR IGNORE INTO swarm_agents (agent_slug, name, role, model_tier, personality, avatar_emoji) VALUES
    ('ralph', 'Ralph', 'coordinator', 'expensive', 'Gestor estratégico focado em resultados', '🎩'),
    ('scout', 'Scout', 'find', 'cheap', 'Researcher rápido e curioso', '🔍'),
    ('max', 'Max', 'build', 'medium', 'Builder pragmático, entrega código que funciona', '🛠️'),
    ('maya', 'Maya', 'create', 'cheap', 'Copywriter persuasiva, entende marketing', '📝'),
    ('tracker', 'Tracker', 'track', 'cheap', 'Analista de métricas e dados', '📊'),
    ('watcher', 'Watcher', 'watch', 'cheap', 'Observador de tendências e concorrentes', '👁️');

-- Indexes para Swarm
CREATE INDEX IF NOT EXISTS idx_swarm_messages_channel ON swarm_messages(channel_id);
CREATE INDEX IF NOT EXISTS idx_swarm_messages_author ON swarm_messages(author_id);
CREATE INDEX IF NOT EXISTS idx_swarm_messages_created ON swarm_messages(created_at);
CREATE INDEX IF NOT EXISTS idx_swarm_tasks_status ON swarm_tasks(status);
CREATE INDEX IF NOT EXISTS idx_swarm_task_agents_task ON swarm_task_agents(task_id);
CREATE INDEX IF NOT EXISTS idx_swarm_task_agents_agent ON swarm_task_agents(agent_id);
