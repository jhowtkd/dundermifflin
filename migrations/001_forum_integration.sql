-- Migration: Forum Integration for Ralph Swarm
-- Adiciona suporte a fóruns do Discord como entrada de tasks

-- ============================================================
-- FORUM INTEGRATION TABLES
-- ============================================================

-- 1. FORUM_TASKS - Tasks criadas via fóruns do Discord
CREATE TABLE IF NOT EXISTS forum_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_code TEXT UNIQUE NOT NULL,
    
    -- Discord IDs
    discord_thread_id TEXT NOT NULL UNIQUE,
    discord_channel_id TEXT NOT NULL,
    discord_guild_id TEXT,
    starter_message_id TEXT,
    
    -- Conteúdo
    title TEXT NOT NULL,
    raw_content TEXT,                    -- Texto completo concatenado
    context_json TEXT,                   -- JSON com histórico completo
    attachments_json TEXT,               -- JSON com anexos (arquivos .txt etc)
    
    -- Status
    status TEXT DEFAULT 'draft',         -- draft, pending_approval, approved, executing, completed, cancelled
    
    -- Controle
    triggered_by TEXT,                   -- 'mention', 'reaction', 'command'
    triggered_at TIMESTAMP,
    
    -- Relacionamento com sistema existente
    execution_plan_id INTEGER,           -- FK para execution_plans
    mission_id INTEGER,                  -- FK para missions (quando aprovado)
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (execution_plan_id) REFERENCES execution_plans(id) ON DELETE SET NULL,
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE SET NULL
);

-- 2. FORUM_PLANS - Planos gerados para tasks do fórum
-- (Usa execution_plans existente, mas guarda referência ao Discord)
CREATE TABLE IF NOT EXISTS forum_plan_discord_refs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_plan_id INTEGER NOT NULL,
    forum_task_id INTEGER NOT NULL,
    discord_plan_message_id TEXT,        -- ID da mensagem do plano no Discord
    discord_status_message_id TEXT,      -- ID da mensagem de status/atualização
    
    -- Resposta do usuário
    approval_status TEXT DEFAULT 'pending', -- pending, approved, rejected, revised
    response_type TEXT,                  -- 'reaction', 'reply'
    response_content TEXT,
    responded_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (execution_plan_id) REFERENCES execution_plans(id) ON DELETE CASCADE,
    FOREIGN KEY (forum_task_id) REFERENCES forum_tasks(id) ON DELETE CASCADE
);

-- 3. FORUM_EVENTS - Log de eventos para debugging
CREATE TABLE IF NOT EXISTS forum_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_code TEXT UNIQUE NOT NULL,
    forum_task_id INTEGER,
    execution_plan_id INTEGER,
    event_type TEXT NOT NULL,            -- 'thread_created', 'triggered', 'plan_generated', 'approved', etc
    event_data TEXT,                     -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (forum_task_id) REFERENCES forum_tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (execution_plan_id) REFERENCES execution_plans(id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_forum_tasks_status ON forum_tasks(status);
CREATE INDEX IF NOT EXISTS idx_forum_tasks_thread ON forum_tasks(discord_thread_id);
CREATE INDEX IF NOT EXISTS idx_forum_tasks_mission ON forum_tasks(mission_id);
CREATE INDEX IF NOT EXISTS idx_forum_plan_refs_plan ON forum_plan_discord_refs(execution_plan_id);
CREATE INDEX IF NOT EXISTS idx_forum_plan_refs_task ON forum_plan_discord_refs(forum_task_id);
CREATE INDEX IF NOT EXISTS idx_forum_events_task ON forum_events(forum_task_id);
CREATE INDEX IF NOT EXISTS idx_forum_events_type ON forum_events(event_type);

-- ============================================================
-- VIEWS ÚTEIS
-- ============================================================

-- View: Tasks pendentes de aprovação com dados do Discord
CREATE VIEW IF NOT EXISTS v_forum_tasks_pending AS
SELECT 
    ft.*,
    ep.plan_code,
    ep.title as plan_title,
    ep.strategy,
    fpr.discord_plan_message_id,
    fpr.approval_status
FROM forum_tasks ft
LEFT JOIN execution_plans ep ON ep.id = ft.execution_plan_id
LEFT JOIN forum_plan_discord_refs fpr ON fpr.execution_plan_id = ep.id
WHERE ft.status = 'pending_approval' 
   OR (fpr.approval_status = 'pending' AND ft.status = 'pending_approval');

-- View: Tasks em execução com status atual
CREATE VIEW IF NOT EXISTS v_forum_tasks_executing AS
SELECT 
    ft.*,
    m.status as mission_status,
    m.mission_code,
    m.result as mission_result
FROM forum_tasks ft
LEFT JOIN missions m ON m.id = ft.mission_id
WHERE ft.status = 'executing' OR ft.status = 'approved';

-- ============================================================
-- TRIGGER: Atualiza updated_at automaticamente
-- ============================================================

CREATE TRIGGER IF NOT EXISTS tr_forum_tasks_updated_at 
AFTER UPDATE ON forum_tasks
BEGIN
    UPDATE forum_tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================================
-- SEED: Configuração padrão
-- ============================================================

-- Registra o evento de criação das tabelas
INSERT OR IGNORE INTO forum_events (event_code, event_type, event_data, created_at)
VALUES (
    'INIT-' || strftime('%s', 'now'),
    'schema_initialized',
    '{"version": "1.0", "tables": ["forum_tasks", "forum_plan_discord_refs", "forum_events"]}',
    CURRENT_TIMESTAMP
);
