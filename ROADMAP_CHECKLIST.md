---
title: "19-Agent Build System — Master Roadmap Checklist"
type: roadmap
version: "3.0"
last_updated: ""
current_chunk: "01"
chunks_complete: 0
chunks_total: 14
tags: [roadmap, checklist, cascade, master]
---

# StackConsulting 19-Agent Build System
## Master Roadmap Checklist v3.0

*Cascade: Read this file on every session start and context resume.*
*Update checkbox and last_updated frontmatter after every chunk.*
*This is the single source of truth for what has been built.*

---

## PART 1 — IDE BOOTSTRAP
- [x] CHUNK-01: Skills self-assessment + dependency install
- [x] CHUNK-01: Windsurf extensions installed
- [x] CHUNK-01: Memory system files created
- [x] CHUNK-01: Workspace settings configured

## PART 2 — ROADMAP + STRUCTURE
- [x] CHUNK-02: ROADMAP_CHECKLIST.md written (this file)
- [x] CHUNK-02: BRANCH_MAP.md written
- [x] CHUNK-02: Directory structure created
- [ ] CHUNK-02: Git repo initialised + committed

## PART 3 — INFRASTRUCTURE (SWE-AGT-01)
- [ ] CHUNK-03: PostgreSQL + governance_db live
- [ ] CHUNK-03: All tables: builds, events, gates, blockers, messages
- [ ] CHUNK-03: Redis live and queue-tested
- [ ] CHUNK-03: All 7 MCP servers live (ports 8001-8007)
- [ ] CHUNK-03: Orchestrator live on port 8008
- [ ] CHUNK-03: All MCP servers installed IN IDE (via Windsurf MCP config)

## PART 4 — BASE AGENT + SKILL EXECUTOR
- [ ] CHUNK-04: base_agent.py — all 5 methods real-run tested
- [ ] CHUNK-04: skill_executor.py installed and running
- [ ] CHUNK-04: All SKILL.yaml workflow files installed
- [ ] CHUNK-04: Workflows registered in CASCADE_WORKFLOWS.md

## PART 5 — PHASE 1-2 AGENTS (SWE-AGT-02)
- [ ] CHUNK-05: PO_AGENT_v1 — test 4/4 PASS
- [ ] CHUNK-05: TL_AGENT_v1 — test 4/4 PASS
- [ ] CHUNK-05: DO_AGENT_v1 — test 4/4 PASS
- [ ] CHUNK-05: TL_AGENT_v2 — test 4/4 PASS

## PART 6 — PHASE 3 AGENTS (SWE-AGT-03)
- [ ] CHUNK-06: BE_AGENT_v1 — test 4/4 PASS
- [ ] CHUNK-06: FE_AGENT_v1 — test 4/4 PASS
- [ ] CHUNK-06: DO_AGENT_v2 — test 4/4 PASS
- [ ] CHUNK-06: TL_AGENT_v3 — test 4/4 PASS

## PART 7 — PHASE 4 AGENTS (SWE-AGT-04)
- [ ] CHUNK-07: QA_AGENT_v1 — test 4/4 PASS
- [ ] CHUNK-07: BE_AGENT_v2 — test 4/4 PASS
- [ ] CHUNK-07: FE_AGENT_v2 — test 4/4 PASS
- [ ] CHUNK-07: TL_AGENT_v4 — test 4/4 PASS

## PART 8 — PHASE 5 AGENTS (SWE-AGT-05)
- [ ] CHUNK-08: BE_AGENT_v3 — test 4/4 PASS
- [ ] CHUNK-08: DO_AGENT_v3 — test 4/4 PASS
- [ ] CHUNK-08: PO_AGENT_v2 — test 4/4 PASS
- [ ] CHUNK-08: TL_AGENT_v5 — test 4/4 PASS

## PART 9 — PHASE 6 AGENTS (SWE-AGT-06)
- [ ] CHUNK-09: DO_AGENT_v4 — test 4/4 PASS
- [ ] CHUNK-09: QA_AGENT_v2 — test 4/4 PASS
- [ ] CHUNK-09: All 18 agents importable
- [ ] CHUNK-09: ALL_AGENTS index complete

## PART 10 — PRE-TOLARIA VALIDATION HARNESS
- [ ] CHUNK-10: PostgreSQL real-run tests 5/5 PASS
- [ ] CHUNK-10: Redis real-run tests 5/5 PASS
- [ ] CHUNK-10: MCP servers HTTP tests 7/7 PASS
- [ ] CHUNK-10: Orchestrator API tests 5/5 PASS
- [ ] CHUNK-10: base_agent real-run tests 5/5 PASS
- [ ] CHUNK-10: All 18 agent imports verified
- [ ] CHUNK-10: 19 test suites: all PASS
- [ ] CHUNK-10: Cross-component integration: 5/5 PASS
- [ ] CHUNK-10: Security scan: CLEAN
- [ ] CHUNK-10: Architectural rules: all enforced
- [ ] CHUNK-10: Real deploy test: Phase 1 events firing
- [ ] CHUNK-10: TEST_REPORT.md score = 100%
- [ ] CHUNK-10: GO signal issued

## PART 11 — TOLARIA OPERATOR SHELL
- [ ] CHUNK-11: Tolaria cloned and version-pinned
- [ ] CHUNK-11: Vault structure: AGENTS, GATE_DASHBOARD.md
- [ ] CHUNK-11: .tolaria/config.json written
- [ ] CHUNK-11: vault_sync.py — syntax + tests PASS
- [ ] CHUNK-11: vault_sync wired into orchestrator
- [ ] CHUNK-11: Tolaria compiled and running
- [ ] CHUNK-11: MCP port 9710 live
- [ ] CHUNK-11: REST bridge on port 8009 live
- [ ] CHUNK-11: Live wire test: gate → Tolaria confirmed
- [ ] CHUNK-11: start-tolaria.sh boots all services

## PART 12 — AGENT SCRIPTS INSTALLED EVERYWHERE
- [ ] CHUNK-12: All scripts in /opt/agents (local)
- [ ] CHUNK-12: All scripts pushed to remote git repo
- [ ] CHUNK-12: All SKILL.yaml workflows in Windsurf skills dir
- [ ] CHUNK-12: All agent scripts registered in IDE as tasks
- [ ] CHUNK-12: Windsurf MCP config updated with all 7 MCPs
- [ ] CHUNK-12: Launch tasks in .vscode/tasks.json
- [ ] CHUNK-12: All scripts executable and path-validated

## PART 13 — SKILL EXECUTOR + WORKFLOW UPGRADE CYCLE
- [ ] CHUNK-13: skill_executor.py running in IDE
- [ ] CHUNK-13: All 18 agent workflows loaded
- [ ] CHUNK-13: check-your-skills workflow running
- [ ] CHUNK-13: upgrade-skills workflow: verify → log → upgrade
- [ ] CHUNK-13: validate-analyze-audit-optimize cycle configured
- [ ] CHUNK-13: All workflows registered in CASCADE_WORKFLOWS.md

## PART 14 — FINAL VALIDATION + LIVE SYSTEM SIGN-OFF
- [ ] CHUNK-14: Full system health check: all services
- [ ] CHUNK-14: ROADMAP_CHECKLIST all items checked
- [ ] CHUNK-14: BRANCH_MAP updated with all files
- [ ] CHUNK-14: JOURNAL complete with all entries
- [ ] CHUNK-14: bootstrap-log.md signed off
- [ ] CHUNK-14: Git: clean state, all committed
- [ ] CHUNK-14: System live and running end-to-end

---

## Execution Order
Paste one chunk at a time. Wait for COMPLETION BLOCK.
Only paste next chunk after COMPLETION BLOCK prints.
Never skip. Never rush. Gates are truth.

