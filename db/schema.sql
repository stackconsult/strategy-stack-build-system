-- governance_db schema — all tables use IF NOT EXISTS
-- Safe to run multiple times

CREATE TABLE IF NOT EXISTS builds (
    id           SERIAL PRIMARY KEY,
    build_id     VARCHAR(128) UNIQUE NOT NULL,
    status       VARCHAR(32)  NOT NULL DEFAULT 'PENDING',
    current_phase INTEGER      NOT NULL DEFAULT 1,
    prd_path     TEXT,
    spec_path    TEXT,
    started_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    metadata     JSONB        NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS events (
    id         SERIAL PRIMARY KEY,
    build_id   VARCHAR(128) NOT NULL,
    agent_id   VARCHAR(64)  NOT NULL,
    event_type VARCHAR(64)  NOT NULL,
    step_id    VARCHAR(64),
    payload    JSONB        NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS gates (
    id         SERIAL PRIMARY KEY,
    build_id   VARCHAR(128) NOT NULL,
    gate_id    VARCHAR(32)  NOT NULL,
    status     VARCHAR(16)  NOT NULL DEFAULT 'PENDING',
    passed_by  VARCHAR(64),
    evidence   JSONB        NOT NULL DEFAULT '{}',
    passed_at  TIMESTAMPTZ,
    UNIQUE (build_id, gate_id)
);

CREATE TABLE IF NOT EXISTS blockers (
    id         SERIAL PRIMARY KEY,
    build_id   VARCHAR(128) NOT NULL,
    agent_id   VARCHAR(64)  NOT NULL,
    gate_id    VARCHAR(32),
    message    TEXT         NOT NULL,
    resolved   BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS messages (
    id          SERIAL PRIMARY KEY,
    build_id    VARCHAR(128) NOT NULL,
    from_agent  VARCHAR(64)  NOT NULL,
    to_agent    VARCHAR(64)  NOT NULL,
    message_type VARCHAR(64) NOT NULL,
    payload     JSONB        NOT NULL DEFAULT '{}',
    read        BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_heartbeats (
    id         SERIAL PRIMARY KEY,
    build_id   VARCHAR(128) NOT NULL,
    agent_id   VARCHAR(64)  NOT NULL,
    status     VARCHAR(32)  NOT NULL,
    last_seen  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_events_build_id ON events(build_id);
CREATE INDEX IF NOT EXISTS idx_gates_build_id ON gates(build_id);
CREATE INDEX IF NOT EXISTS idx_blockers_build_id ON blockers(build_id);
CREATE INDEX IF NOT EXISTS idx_messages_to_agent ON messages(to_agent, build_id);
