# Tolaria Integration Research & Implementation Plan

## Executive Summary

This document outlines how the 19-Agent Build System integrates with Tolaria, StackConsulting's desktop vault application for managing markdown knowledge bases. Tolaria is built with Tauri (Rust + React) and serves as the governance and project management layer for the build system.

---

## Current State Analysis

### What Exists Now

**19-Agent Build System (Built in /opt/agents):**

- 18 agents (PO_AGENT_v1 through TL_AGENT_v5)
- 45 gates across 6 phases
- PostgreSQL governance_db for state persistence
- Redis for message streaming
- 7 MCP servers (ports 8001-8007)
- Orchestrator (port 8008)
- Web dashboard (port 8081) - basic implementation
- Tolaria shell (command-line interface)
- **Location:** `/opt/agents` on Mac (can be run from USB or GitHub)

**Tolaria (External Desktop Application):**

- Tauri-based desktop app (Rust + React + TypeScript)
- Markdown vault management
- Git-first architecture
- Files-first storage
- AI agent integration support
- **Vault Location:** Configurable (Mac, USB, or any path)

**Deployment Architecture:**

- **USB Drive (Store and Go):** Stores all source files
- **Mac:** Runs the system from USB or local copy
- **GitHub:** Public repo for anyone to clone and run
- **Tolaria Vault:** Can be anywhere (Mac, USB, separate drive)

---

## Integration Architecture

### 4 Connection Points (Per Specifications)

#### CONNECTION POINT 1: Build Initiation

**Tolaria → Build System**

Tolaria UI triggers new builds via API:

```
POST /api/builds/start
{
  "client_id": "[client]",
  "build_name": "[project name]",
  "prd_path": "[path to PRD in Tolaria vault]",
  "sla_targets": {...},
  "tech_stack_overrides": {...}
}
```

**Implementation Required:**

- Add Tauri command in Tolaria: `start_build(payload)`
- Add HTTP client in Tolaria Rust backend
- Add UI button/form in Tolaria React frontend
- Build system API endpoint exists at `/api/builds/start`

#### CONNECTION POINT 2: Governance Visibility

**Build System → Tolaria**

Tolaria reads `/builds/[BUILD_ID]/state.json` every 30 seconds:

```json
{
  "build_id": "[uuid]",
  "current_phase": "PHASE_N",
  "current_step": "NN",
  "active_agents": ["AGENT_ID_1"],
  "open_blockers": ["BLOCKER_ID_1"],
  "open_handoffs_awaiting_ack": ["MESSAGE_ID_1"],
  "gates_passed": ["G-01", "G-02"],
  "gates_remaining": ["G-03"],
  "last_updated_utc": "[ISO8601]"
}
```

**Implementation Required:**

- ORCHESTRATOR_AGENT must write state.json to Tolaria vault path
- Tolaria must watch state.json for changes (fs watcher)
- Tolaria UI must display: current phase, active agents, blockers, gates
- Health status: GREEN/YELLOW/RED based on blockers

#### CONNECTION POINT 3: Documentation Sync

**Build System → Tolaria**

On every PHASE_CLOSE, TL_AGENT writes:

```
/builds/[BUILD_ID]/docs/phase-reports/phase-[N]-closure.md
```

Tolaria surfaces these as project journal entries.

**Implementation Required:**

- TL_AGENT_vN must write phase reports to Tolaria vault path
- Tolaria must index phase reports in its search
- Tolaria must display phase reports in chronological order

#### CONNECTION POINT 4: Build Archive

**Build System → Tolaria**

On BUILD_COMPLETE, TL_AGENT_v5 writes:

```
/builds/[BUILD_ID]/archived/
  ├── BUILD-CERTIFICATE.md
  ├── KNOWLEDGE-TRANSFER.md
  ├── ARCHITECTURE-DECISIONS.md
  ├── RUNBOOKS/
  ├── API-SPEC.yaml
  └── ... (full delivery package)
```

Tolaria ingests as completed project record.

**Implementation Required:**

- TL_AGENT_v5 must write archive to Tolaria vault
- Tolaria must create project record linking to archive
- Tolaria must make archive searchable and linkable

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    TOLARIA DESKTOP APP                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   React UI   │  │  Rust Backend │  │   Vault Filesystem   │  │
│  │              │  │   (Tauri)     │  │   (Markdown + JSON)  │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
└─────────┼────────────────┼────────────────────┼───────────────┘
          │                │                    │
          │  HTTP API      │    File I/O        │
          │                │                    │
┌─────────┼────────────────┼────────────────────┼───────────────┐
│         │   ┌────────────▼────────────────────▼──────────┐   │
│         └──►│         19-AGENT BUILD SYSTEM               │   │
│             │  ┌──────────────┐  ┌──────────────────────┐  │   │
│             │  │ ORCHESTRATOR │  │   AGENTS (18)       │  │   │
│             │  │   (Port 8008)│  │   (Spawn per-phase) │  │   │
│             │  └──────┬───────┘  └──────────┬───────────┘  │   │
│             │         │                     │              │   │
│             │  ┌──────▼──────┐  ┌───────────▼──────────┐  │   │
│             │  │ PostgreSQL  │  │   7 MCP SERVERS      │  │   │
│             │  │ governance  │  │   (Ports 8001-8007)│  │   │
│             │  │    _db      │  │                      │  │   │
│             │  └─────────────┘  └──────────────────────┘  │   │
│             └───────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Build System API Enhancement (Priority: HIGH)

**Deliverable:** Enhanced REST API for Tolaria integration

1. **Extend dashboard/server.py with new endpoints:**
   - `POST /api/builds/start` - Build initiation
   - `GET /api/builds/:build_id/status` - Live status
   - `GET /api/builds/:build_id/phases` - Phase reports
   - `GET /api/builds/:build_id/blockers` - Active blockers
   - `POST /api/builds/:build_id/pause` - Human pause
   - `POST /api/builds/:build_id/resume` - Human resume

2. **Add state.json file writer to orchestrator:**
   - Write state.json to configured Tolaria vault path
   - Update every 30 seconds or on state change
   - Include all fields from spec

3. **Modify agents to write to Tolaria paths:**
   - TL_AGENT_vN: Write phase reports to `/builds/[BUILD_ID]/docs/`
   - TL_AGENT_v5: Write delivery package to `/builds/[BUILD_ID]/archived/`

**Estimated Effort:** 2-3 days

---

### Phase 2: Tolaria Plugin/Extension (Priority: HIGH)

**Deliverable:** Tolaria plugin for Build System integration

**Option A: Tauri Sidecar (Recommended)**
Create a Tauri sidecar that runs alongside Tolaria:

```rust
// Tolaria sidecar - build_system_bridge.rs
// Runs as separate process, communicates with Tolaria via IPC

#[tauri::command]
async fn poll_build_status(build_id: String) -> Result<BuildState, String> {
    // Polls http://localhost:8081/api/builds/{build_id}/status
    // Returns state to Tolaria UI
}

#[tauri::command]
async fn start_new_build(config: BuildConfig) -> Result<String, String> {
    // POSTs to /api/builds/start
    // Returns build_id
}
```

**Option B: Tolaria Fork/PR**
Contribute Build System support directly to Tolaria codebase:

- Add "Build Projects" section to Tolaria UI
- Add build monitoring sidebar/panel
- Add build initiation command

**Implementation Steps:**

1. Set up Tolaria development environment
2. Create Build System plugin architecture
3. Add Build System panel to UI
4. Implement file watcher for state.json
5. Add build initiation UI
6. Test integration end-to-end

**Estimated Effort:** 5-7 days

---

### Phase 3: File System Integration (Priority: MEDIUM)

**Deliverable:** Bidirectional file sync between systems

**Architecture Constraint:**

- Build system runs from: USB drive, Mac, or GitHub clone (location-agnostic)
- Tolaria vault can be: Mac, USB, separate drive (configurable)
- Integration must work regardless of source/destination locations

1. **Configuration (Environment Variables):**

   ```bash
   # Build System Config
   BUILD_SYSTEM_ROOT=/path/to/agents  # Auto-detected if not set
   TOLARIA_VAULT_PATH=/path/to/tolaria/vault  # Required
   BUILD_OUTPUT_DIR=/path/to/builds  # Default: ./builds
   ```

2. **Tolaria vault structure for builds:**

   ```
   [TOLARIA_VAULT_PATH]/
     ├── builds/
     │   ├── [BUILD_ID]/
     │   │   ├── state.json          ← Written by ORCHESTRATOR
     │   │   ├── docs/
     │   │   │   └── phase-reports/  ← Written by TL_AGENT
     │   │   └── archived/           ← Written by TL_AGENT_v5
     │   └── active-builds-index.md  ← Managed by Tolaria
     └── clients/
         └── [CLIENT_NAME]/
             └── builds/             ← Symlinks to active builds
   ```

3. **Path Resolution Strategy:**

   ```python
   # In orchestrator and agents
   import os
   from pathlib import Path

   def get_tolaria_vault_path():
       """Get Tolaria vault path from env or prompt user"""
       path = os.getenv('TOLARIA_VAULT_PATH')
       if not path:
           # Check common locations
           for candidate in [
               Path.home() / 'tolaria-vault',
               Path.home() / 'Documents' / 'tolaria',
               Path.home() / 'vault',
               '/Volumes/STORE N GO/tolaria-vault',  # USB
           ]:
               if candidate.exists():
                   path = str(candidate)
                   break
       return path
   ```

4. **File watchers:**
   - Tolaria watches state.json for changes (via native OS watcher)
   - Build system writes to configured path (no watching needed)
   - Both use absolute paths to avoid confusion

5. **Deployment Configuration:**

   ```bash
   # When running from USB
   export BUILD_SYSTEM_ROOT="/Volumes/STORE N GO/agents"
   export TOLARIA_VAULT_PATH="/Volumes/STORE N GO/tolaria-vault"

   # When running from GitHub clone
   export BUILD_SYSTEM_ROOT="/Users/[user]/agents"
   export TOLARIA_VAULT_PATH="/Users/[user]/tolaria-vault"

   # When running from Mac local copy
   export BUILD_SYSTEM_ROOT="/opt/agents"
   export TOLARIA_VAULT_PATH="/Users/[user]/tolaria-vault"
   ```

**Estimated Effort:** 2 days

---

### Phase 4: UI Components (Priority: MEDIUM)

**Deliverable:** React components for Tolaria integration

1. **Build Dashboard Card:**

   ```tsx
   // BuildCard.tsx - Shows in Tolaria UI
   interface BuildCardProps {
     buildId: string;
     status: 'GREEN' | 'YELLOW' | 'RED';
     phase: string;
     activeAgents: string[];
     gatesPassed: number;
     gatesTotal: number;
   }
   ```

2. **Build Initiation Modal:**

   ```tsx
   // StartBuildModal.tsx
   interface StartBuildForm {
     clientId: string;
     buildName: string;
     prdPath: string;  // Selected from Tolaria vault
     slaTargets: SLATargets;
   }
   ```

3. **Blocker Alert Component:**
   - Shows when build has open blockers
   - Links to detailed blocker view

**Estimated Effort:** 3 days

---

### Phase 5: Testing & Validation (Priority: HIGH)

**Deliverable:** Integration test suite

1. **Unit tests:**
   - API endpoint tests
   - File I/O tests
   - State serialization tests

2. **Integration tests:**
   - End-to-end build flow
   - Tolaria file watching
   - Build initiation from Tolaria

3. **Manual validation:**
   - Full build lifecycle
   - Error handling
   - UI responsiveness

**Estimated Effort:** 2 days

---

## Technical Specifications

### API Contract

**Build System Endpoints (to be implemented):**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/builds/start` | POST | Initiate new build |
| `/api/builds/:id/status` | GET | Get build state |
| `/api/builds/:id/pause` | POST | Pause build |
| `/api/builds/:id/resume` | POST | Resume build |
| `/api/builds/active` | GET | List active builds |
| `/api/builds/history` | GET | List completed builds |

### File Locations

**Architecture:** Location-agnostic - works from USB, Mac, or GitHub clone

**Build System runs from:**

- USB: `/Volumes/STORE N GO/agents`
- Mac: `/opt/agents` or `/Users/[user]/agents`
- GitHub clone: Any user-selected path

**Build System writes to:**

- `[BUILD_OUTPUT_DIR]/[BUILD_ID]/state.json`
- `[BUILD_OUTPUT_DIR]/[BUILD_ID]/docs/`
- `[BUILD_OUTPUT_DIR]/[BUILD_ID]/archived/`
- Default: `./builds/` relative to BUILD_SYSTEM_ROOT

**Tolaria vault location:**

- Configurable via `TOLARIA_VAULT_PATH` environment variable
- Auto-detection checks: `~/tolaria-vault`, `~/Documents/tolaria`, `/Volumes/STORE N GO/tolaria-vault`

**Tolaria reads from:**

- `[TOLARIA_VAULT_PATH]/builds/[BUILD_ID]/state.json`
- `[TOLARIA_VAULT_PATH]/builds/[BUILD_ID]/docs/`
- `[TOLARIA_VAULT_PATH]/builds/[BUILD_ID]/archived/`

**Sync mechanism:**

- Option 1: Build system writes directly to Tolaria vault path (RECOMMENDED for USB deployment)
- Option 2: File watcher syncs between paths (for separate locations)
- Option 3: API-based data transfer (no file sharing - least preferred)

### Data Formats

**state.json:**

```json
{
  "build_id": "BUILD-2026-05-07-002",
  "current_phase": "PHASE_6",
  "current_step": "27",
  "active_agents": ["QA_AGENT_v2"],
  "open_blockers": [],
  "open_handoffs_awaiting_ack": [],
  "gates_passed": ["G-01", "G-02", ..., "G-45"],
  "gates_remaining": [],
  "health_status": "GREEN",
  "last_updated_utc": "2026-05-07T16:02:21Z"
}
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Tolaria path configuration mismatched | Medium | High | Clear documentation, validation on startup |
| File watcher performance issues | Low | Medium | Debounce changes, use native OS watchers |
| API version incompatibility | Medium | High | Version negotiation, backward compatibility |
| Tolaria UI clutter | Medium | Low | Optional panel, collapse by default |

---

## Success Criteria

1. ✅ Build can be initiated from Tolaria UI
2. ✅ Build status visible in real-time in Tolaria
3. ✅ Phase reports automatically appear in Tolaria
4. ✅ Completed builds archived and searchable in Tolaria
5. ✅ Blockers trigger notifications in Tolaria
6. ✅ No manual file copying between systems

---

## Next Steps

1. **Decision Point:** Which integration approach?
   - A) Build system writes directly to Tolaria vault path (simplest)
   - B) Tauri sidecar as bridge (most robust)
   - C) Full Tolaria fork with native integration (most integrated)

2. **Immediate Actions:**
   - Confirm Tolaria vault path configuration
   - Implement state.json writer in orchestrator
   - Extend API with missing endpoints
   - Create Tolaria plugin prototype

3. **Timeline:**
   - Phase 1 (API Enhancement): 2-3 days
   - Phase 2 (Tolaria Plugin): 5-7 days  
   - Phase 3 (File Integration): 2 days
   - Phase 4 (UI Components): 3 days
   - Phase 5 (Testing): 2 days
   - **Total: 14-17 days**

---

## Questions for Clarification

1. What is the exact path to your Tolaria vault on this Mac?
2. Do you have Tolaria source code locally, or do we need to clone it?
3. Should the build system write directly to Tolaria's vault, or use a sync mechanism?
4. What Tolaria version are you running?
5. Do you want the build dashboard as a Tolaria panel, separate window, or both?
6. Should Tolaria vault also be on the USB drive for portability?

## Deployment Scenarios

**Scenario A: USB-Only Deployment (Most Portable)**

- Build system on USB: `/Volumes/STORE N GO/agents`
- Tolaria vault on USB: `/Volumes/STORE N GO/tolaria-vault`
- Mac runs both from USB
- Everything portable, plug-and-play

**Scenario B: Hybrid Deployment**

- Build system on USB: `/Volumes/STORE N GO/agents`
- Tolaria vault on Mac: `~/tolaria-vault`
- Build system writes to Mac vault via configured path
- Good for development, requires configuration

**Scenario C: GitHub Clone Deployment**

- Build system cloned from GitHub to Mac
- Tolaria vault on Mac
- Standard development setup
- Requires git clone and configuration

---

*Document prepared for StackConsulting 19-Agent Build System integration with Tolaria*
