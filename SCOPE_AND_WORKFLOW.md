# Full Scope of Work - 19-Agent Build System

## Repository Overview
**GitHub**: https://github.com/stackconsult/strategy-stack-build-system
**Branch**: main (master in workspace)
**Location**: ~/Desktop/19-agent-workspace

## System Architecture

### 19-Agent Build System
A comprehensive multi-phase build orchestration system with:

**Agent Types (6 categories)**:
- **PO Agent** (Product Owner): Requirements analysis, PRD processing
- **TL Agent** (Technical Lead): Architecture design, technical specifications
- **DO Agent** (DevOps): Infrastructure, deployment, CI/CD
- **BE Agent** (Backend Engineer): API development, database design
- **FE Agent** (Frontend Engineer): UI/UX implementation
- **QA Agent** (Quality Assurance): Testing, validation

**Agent Versions**:
- PO: v1, v2
- TL: v1, v2, v3, v4, v5, v6
- DO: v1, v2, v3, v4
- BE: v1, v2, v3
- FE: v1, v2
- QA: v1, v2

**Total**: 18 agents across 6 build phases

### Infrastructure Components

**Database Layer**:
- PostgreSQL governance_db (builds, events, gates, blockers, messages, agent_heartbeats)
- Redis cache (session management, pub/sub)

**MCP Servers (7 servers)**:
- filesystem_mcp: port 8001
- git_mcp: port 8002
- database_mcp: port 8003
- cicd_mcp: port 8004
- observability_mcp: port 8006
- secrets_mcp: port 8007
- orchestrator: port 8008

**Orchestrator**:
- FastAPI application (port 8008)
- Build lifecycle management
- Agent coordination
- Event tracking

**Desktop App**:
- Tauri-based application
- React frontend with build monitoring UI
- Rust backend with API integration
- macOS packaged application

## Current State Assessment

### ✅ Completed
1. Workspace created on Mac desktop
2. Agents directory copied from USB drive
3. Desktop app copied to workspace
4. Git initialized and connected to GitHub
5. Successfully pushed to master branch (7,974 files, 340 MB)

### ❌ Blocking Issues
1. **Docker Desktop**: Won't start on macOS Monterey 12.7.6 Intel
2. **PostgreSQL Service**: Bootstrap error when starting via brew services
3. **Redis**: Not installed/running
4. **MCP Servers**: Not running
5. **Orchestrator**: Not running
6. **Builder.io**: Open but not integrated into workflow

### ⚠️ System Limitations
- macOS Monterey 12.7.6 too old for Docker Desktop 4.24.2
- PostgreSQL brew services bootstrap failure (launchd issue)
- No automated health checks implemented
- Working directory confusion (USB vs Mac)

## Full Workflow Definition

### Phase 1: Infrastructure Foundation (BLOCKED)

**Goal**: Get database and cache services running

**Tasks**:
1. **PostgreSQL Setup** (BLOCKED - bootstrap error)
   - Alternative: Use cloud PostgreSQL (Supabase, Neon)
   - Alternative: Use Docker container (BLOCKED - Docker won't start)
   - Alternative: Manual PostgreSQL installation without brew services

2. **Redis Setup** (NOT STARTED)
   - Install via Homebrew
   - Start service
   - Verify connectivity

3. **Database Initialization** (BLOCKED - depends on PostgreSQL)
   - Create governance_db
   - Create tables (builds, events, gates, blockers, messages, agent_heartbeats)
   - Create user (agents_user)

### Phase 2: MCP Server Startup (BLOCKED)

**Goal**: Start 7 MCP servers

**Tasks**:
1. Install MCP server dependencies
2. Configure each MCP server
3. Start servers on ports 8001-8007
4. Health check all servers

### Phase 3: Orchestrator Startup (BLOCKED)

**Goal**: Start FastAPI orchestrator

**Tasks**:
1. Install Python dependencies (FastAPI, asyncpg, redis, structlog)
2. Configure orchestrator
3. Start on port 8008
4. Verify health endpoint

### Phase 4: Agent Validation (BLOCKED)

**Goal**: Validate all 18 agents

**Tasks**:
1. Run validation_harness.py
2. Test all 18 agents
3. Verify agent imports
4. Run agent-specific tests

### Phase 5: Desktop App Integration (READY)

**Goal**: Connect desktop app to orchestrator

**Tasks**:
1. Update desktop app API endpoints
2. Test build monitoring UI
3. Verify Rust backend connectivity
4. Package for macOS

### Phase 6: Workflow Execution (BLOCKED)

**Goal**: Execute full build lifecycle

**Tasks**:
1. Test tolaria_shell.py commands
2. Execute sample build
3. Verify agent coordination
4. Monitor build progress

## Agent Roles and Responsibilities

### Phase 1 Agents (Requirements & Architecture)
- **PO_AGENT_v1**: Process PRD, emit G-01 (requirements)
- **TL_AGENT_v1**: Design architecture, emit G-02 (tech spec)
- **DO_AGENT_v1**: Define infrastructure, emit G-03 (infra plan)
- **TL_AGENT_v2**: Refine architecture, emit G-04 (detailed spec)

### Phase 2 Agents (Backend & Frontend)
- **BE_AGENT_v1**: Design API schema, emit G-05 (API spec)
- **FE_AGENT_v1**: Design UI components, emit G-06 (UI spec)
- **DO_AGENT_v2**: Set up CI/CD, emit G-07 (deployment config)
- **TL_AGENT_v3**: Review integration, emit G-08 (integration plan)

### Phase 3 Agents (Testing & Refinement)
- **QA_AGENT_v1**: Define test strategy, emit G-09 (test plan)
- **BE_AGENT_v2**: Implement backend, emit G-10 (backend code)
- **FE_AGENT_v2**: Implement frontend, emit G-11 (frontend code)
- **TL_AGENT_v4**: Code review, emit G-12 (review results)

### Phase 4 Agents (Optimization)
- **BE_AGENT_v3**: Optimize backend, emit G-13 (performance)
- **DO_AGENT_v3**: Optimize infrastructure, emit G-14 (infra tuning)
- **PO_AGENT_v2**: Review against requirements, emit G-15 (validation)
- **TL_AGENT_v5**: Final architecture review, emit G-16 (final spec)

### Phase 5 Agents (Deployment)
- **DO_AGENT_v4**: Canary deployment, emit G-36, G-37 (deployment gates)
- **QA_AGENT_v2**: Final validation, emit G-45 (build complete)

## Next Steps to Get Up and Running

### Immediate Actions (Priority: CRITICAL)

1. **Bypass Docker Completely**
   - Use cloud PostgreSQL (Supabase free tier)
   - Install Redis via Homebrew directly
   - Skip Docker containerization entirely

2. **Fix PostgreSQL Bootstrap Issue**
   - Try manual PostgreSQL start without brew services
   - Or use cloud PostgreSQL alternative
   - Update orchestrator connection string

3. **Start Infrastructure Services**
   - PostgreSQL (local or cloud)
   - Redis (local)
   - Initialize database schema

4. **Start MCP Servers**
   - Install dependencies
   - Start 7 servers
   - Verify connectivity

5. **Start Orchestrator**
   - Install Python dependencies
   - Start FastAPI server
   - Verify health endpoint

6. **Validate Agents**
   - Run validation_harness.py
   - Fix any import errors
   - Run agent tests

### Alternative Approach: Cloud Development Environment

**If local infrastructure continues to fail**:
1. Create GitHub Codespace
2. Use cloud PostgreSQL (Supabase)
3. Use cloud Redis (Upstash)
4. Run orchestrator in Codespace
5. Access via browser

## Recommended Execution Order

1. **Set up cloud PostgreSQL** (Supabase - free tier, 5GB)
2. **Install and start Redis locally** (brew install redis, brew services start redis)
3. **Update orchestrator config** for cloud PostgreSQL
4. **Start orchestrator** (python -m uvicorn orchestrator.main:app --port 8008)
5. **Start MCP servers** (one by one, verify each)
6. **Run validation harness** (python validation_harness.py)
7. **Test tolaria shell** (python tolaria_shell.py)
8. **Connect desktop app** (update API endpoints)
9. **Execute sample build** (via tolaria shell)

## Success Criteria

- PostgreSQL accessible (local or cloud)
- Redis running on localhost:6379
- All 7 MCP servers running (ports 8001-8007)
- Orchestrator running on port 8008
- validation_harness.py passes all tests
- tolaria_shell.py can list all 18 agents
- Desktop app connects to orchestrator
- Sample build executes successfully

## Anti-Patterns to Avoid

- ❌ Trying to fix Docker on macOS Monterey (won't work)
- ❌ Using brew services for PostgreSQL (bootstrap error)
- ❌ Working in USB drive for active development
- ❌ Skipping validation steps
- ❌ Starting services without health checks

## Best Practices

- ✅ Use cloud services when local fails
- ✅ Implement automated health checks
- ✅ Work in ~/Desktop/19-agent-workspace
- ✅ Push changes to GitHub frequently
- ✅ Test each service before moving to next
- ✅ Document all configuration changes
