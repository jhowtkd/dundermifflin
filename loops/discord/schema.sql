-- Schema SQL para Ralph Loops no Discord
-- Fase 1: Estrutura Base

-- Tabela principal de loops
CREATE TABLE IF NOT EXISTS ralph_loops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    loop_code TEXT UNIQUE NOT NULL,
    agent_slug TEXT NOT NULL,
    task_description TEXT NOT NULL,
    status TEXT DEFAULT 'running',
    max_iterations INTEGER DEFAULT 20,
    current_iteration INTEGER DEFAULT 0,
    completion_promise TEXT DEFAULT 'RALPH_COMPLETE',
    iterations_log TEXT, -- JSON array (mantido para compatibilidade)
    total_tokens_in INTEGER DEFAULT 0,
    total_tokens_out INTEGER DEFAULT 0,
    total_cost_usd REAL DEFAULT 0,
    result_path TEXT,
    error_message TEXT,
    result_summary TEXT, -- Novo: resumo do resultado
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    created_by TEXT DEFAULT 'worker_v3',
    notified_at DATETIME,
    -- Campos Discord (novos)
    discord_channel_id TEXT,
    discord_user_id TEXT,
    discord_guild_id TEXT,
    task_code TEXT,
    FOREIGN KEY (agent_slug) REFERENCES agents(slug)
);

-- Tabela de iterações detalhadas (nova)
CREATE TABLE IF NOT EXISTS ralph_loop_iterations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    loop_code TEXT NOT NULL,
    iteration_number INTEGER NOT NULL,
    prompt_summary TEXT,
    response_summary TEXT,
    full_prompt TEXT,
    full_response TEXT,
    tokens_in INTEGER,
    tokens_out INTEGER,
    duration_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (loop_code) REFERENCES ralph_loops(loop_code)
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_ralph_loops_status ON ralph_loops(status);
CREATE INDEX IF NOT EXISTS idx_ralph_loops_agent ON ralph_loops(agent_slug);
CREATE INDEX IF NOT EXISTS idx_ralph_loops_started ON ralph_loops(started_at);
CREATE INDEX IF NOT EXISTS idx_loops_status ON ralph_loops(status);
CREATE INDEX IF NOT EXISTS idx_loops_agent ON ralph_loops(agent_slug);
CREATE INDEX IF NOT EXISTS idx_iterations_loop ON ralph_loop_iterations(loop_code);
