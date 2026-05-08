-- StackConsulting 19-Agent Build System - Governance Database Schema

-- Builds table
CREATE TABLE IF NOT EXISTS builds (
    build_id VARCHAR(255) PRIMARY KEY,
    status VARCHAR(50) NOT NULL DEFAULT 'INIT',
    current_phase INTEGER DEFAULT 1,
    prd_path TEXT,
    structured_spec JSONB,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB
);

-- Events table (governance records)
CREATE TABLE IF NOT EXISTS events (
    event_id VARCHAR(255) PRIMARY KEY,
    build_id VARCHAR(255) NOT NULL REFERENCES builds(build_id),
    agent_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB,
    timestamp_utc TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Gates table
CREATE TABLE IF NOT EXISTS gates (
    gate_id VARCHAR(50) NOT NULL,
    build_id VARCHAR(255) NOT NULL REFERENCES builds(build_id),
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    evidence JSONB,
    passed_at TIMESTAMP WITH TIME ZONE,
    passed_by VARCHAR(100),
    PRIMARY KEY (gate_id, build_id)
);

-- Blockers table
CREATE TABLE IF NOT EXISTS blockers (
    blocker_id VARCHAR(255) PRIMARY KEY,
    build_id VARCHAR(255) NOT NULL REFERENCES builds(build_id),
    gate_id VARCHAR(50),
    message TEXT NOT NULL,
    raised_by VARCHAR(100) NOT NULL,
    raised_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Agent heartbeats table
CREATE TABLE IF NOT EXISTS agent_heartbeats (
    agent_id VARCHAR(100),
    build_id VARCHAR(255) NOT NULL REFERENCES builds(build_id),
    status VARCHAR(50),
    current_step TEXT,
    last_heartbeat TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (agent_id, build_id)
);

-- Messages table (agent-to-agent communication)
CREATE TABLE IF NOT EXISTS messages (
    message_id VARCHAR(255) PRIMARY KEY,
    from_agent VARCHAR(100) NOT NULL,
    to_agent VARCHAR(100) NOT NULL,
    message_type VARCHAR(100) NOT NULL,
    build_id VARCHAR(255) NOT NULL REFERENCES builds(build_id),
    payload JSONB,
    timestamp_utc TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_events_build_id ON events(build_id);
CREATE INDEX IF NOT EXISTS idx_events_agent_id ON events(agent_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp_utc);
CREATE INDEX IF NOT EXISTS idx_gates_build_id ON gates(build_id);
CREATE INDEX IF NOT EXISTS idx_gates_status ON gates(status);
CREATE INDEX IF NOT EXISTS idx_blockers_build_id ON blockers(build_id);
CREATE INDEX IF NOT EXISTS idx_blockers_resolved ON blockers(resolved);
CREATE INDEX IF NOT EXISTS idx_messages_to_agent ON messages(to_agent);
CREATE INDEX IF NOT EXISTS idx_messages_build_id ON messages(build_id);
CREATE INDEX IF NOT EXISTS idx_messages_processed ON messages(processed);
