-- Database initialization for governance_db
-- Create tables for 19-agent build system

-- Builds table
CREATE TABLE IF NOT EXISTS builds (
    build_id VARCHAR(255) PRIMARY KEY,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    current_phase INTEGER NOT NULL DEFAULT 1,
    prd_path TEXT,
    metadata JSONB,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Events table
CREATE TABLE IF NOT EXISTS events (
    event_id SERIAL PRIMARY KEY,
    build_id VARCHAR(255) REFERENCES builds(build_id) ON DELETE CASCADE,
    agent_type VARCHAR(50),
    agent_version VARCHAR(10),
    event_type VARCHAR(100),
    event_data JSONB,
    timestamp_utc TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_events_build_id (build_id)
);

-- Gates table
CREATE TABLE IF NOT EXISTS gates (
    gate_id VARCHAR(50) PRIMARY KEY,
    gate_name VARCHAR(255),
    gate_description TEXT,
    phase INTEGER,
    gate_status VARCHAR(50) DEFAULT 'PENDING',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Blockers table
CREATE TABLE IF NOT EXISTS blockers (
    blocker_id SERIAL PRIMARY KEY,
    build_id VARCHAR(255) REFERENCES builds(build_id) ON DELETE CASCADE,
    blocker_type VARCHAR(100),
    blocker_description TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_blockers_build_id (build_id)
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    message_id SERIAL PRIMARY KEY,
    build_id VARCHAR(255) REFERENCES builds(build_id) ON DELETE CASCADE,
    from_agent VARCHAR(50),
    to_agent VARCHAR(50),
    message_content TEXT,
    message_type VARCHAR(50),
    timestamp_utc TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_messages_build_id (build_id)
);

-- Agent heartbeats table
CREATE TABLE IF NOT EXISTS agent_heartbeats (
    heartbeat_id SERIAL PRIMARY KEY,
    agent_type VARCHAR(50),
    agent_version VARCHAR(10),
    build_id VARCHAR(255) REFERENCES builds(build_id) ON DELETE CASCADE,
    status VARCHAR(50),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    INDEX idx_heartbeats_build_id (build_id),
    INDEX idx_heartbeats_agent_type (agent_type)
);

-- Insert default gates
INSERT INTO gates (gate_id, gate_name, gate_description, phase) VALUES
('G-01', 'Requirements Emitted', 'PO Agent emits requirements from PRD', 1),
('G-02', 'Architecture Design', 'TL Agent designs technical architecture', 1),
('G-03', 'Infrastructure Plan', 'DO Agent defines infrastructure requirements', 1),
('G-04', 'Detailed Specification', 'TL Agent refines architecture with details', 2),
('G-05', 'API Schema Design', 'BE Agent designs API schema', 3),
('G-06', 'UI Component Design', 'FE Agent designs UI components', 3),
('G-07', 'CI/CD Configuration', 'DO Agent sets up CI/CD pipeline', 3),
('G-08', 'Integration Plan', 'TL Agent reviews integration requirements', 3),
('G-09', 'Test Strategy', 'QA Agent defines test strategy', 4),
('G-10', 'Backend Implementation', 'BE Agent implements backend code', 4),
('G-11', 'Frontend Implementation', 'FE Agent implements frontend code', 4),
('G-12', 'Code Review', 'TL Agent performs code review', 4),
('G-13', 'Backend Optimization', 'BE Agent optimizes backend performance', 5),
('G-14', 'Infrastructure Tuning', 'DO Agent optimizes infrastructure', 5),
('G-15', 'Requirements Validation', 'PO Agent validates against requirements', 5),
('G-16', 'Final Architecture Review', 'TL Agent performs final architecture review', 5),
('G-36', 'Canary Deployment', 'DO Agent performs canary deployment', 6),
('G-37', 'Canary Validation', 'DO Agent validates canary deployment', 6),
('G-45', 'Build Complete', 'QA Agent finalizes build validation', 6)
ON CONFLICT (gate_id) DO NOTHING;

-- Create database user for agents
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'agents_user') THEN
        CREATE ROLE agents_user WITH LOGIN PASSWORD 'agents_secure_pass_2026';
    END IF;
END
$$;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO agents_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO agents_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO agents_user;
