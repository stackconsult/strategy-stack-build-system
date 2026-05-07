---
title: "Full Scope Branch Repo Map"
type: branch-map
version: "1.0"
last_updated: ""
total_files: 0
tags: [branch-map, repo, cascade, navigation]
---

# Full Scope Branch Repo Map
## StackConsulting 19-Agent Build System

*Cascade: Add every new file here. Never delete entries.*
*Format: PATH | TYPE | STATUS | CHUNK | LAST_UPDATED*

## Core Governance
ROADMAP_CHECKLIST.md       | roadmap   | ACTIVE | 02 | [NOW]
BRANCH_MAP.md              | map       | ACTIVE | 02 | [NOW]
JOURNAL.md                 | journal   | ACTIVE | 01 | [NOW]
MEMORY_LOG.md              | memory    | ACTIVE | 01 | [NOW]
CASCADE_SKILLS.md          | registry  | ACTIVE | 01 | [NOW]
CASCADE_WORKFLOWS.md       | registry  | ACTIVE | 01 | [NOW]
CASCADE_IDE_STATE.md       | registry  | ACTIVE | 01 | [NOW]
bootstrap-log.md           | log       | ACTIVE | 00 | [NOW]
TEST_REPORT.md             | test      | PENDING| 10 | -
AGENTS                     | contract  | PENDING| 11 | -
GATE_DASHBOARD.md          | dashboard | PENDING| 11 | -

## Orchestrator
orchestrator/__init__.py   | python    | PENDING| 03 | -
orchestrator/main.py       | python    | PENDING| 03 | -
orchestrator/vault_sync.py | python    | PENDING| 11 | -
orchestrator/test_vault_sync.py | python | PENDING | 11 | -

## Database
db/schema.sql              | sql       | PENDING| 03 | -
db/migrations/             | dir       | PENDING| 03 | -

## MCP Servers (7)
mcp_servers/filesystem_mcp/| dir       | PENDING| 03 | -
mcp_servers/git_mcp/       | dir       | PENDING| 03 | -
mcp_servers/cicd_mcp/      | dir       | PENDING| 03 | -
mcp_servers/secrets_mcp/   | dir       | PENDING| 03 | -
mcp_servers/database_mcp/  | dir       | PENDING| 03 | -
mcp_servers/observability_mcp/ | dir   | PENDING| 03 | -
mcp_servers/communication_mcp/ | dir   | PENDING| 03 | -

## Agents (18)
agents/__init__.py         | python    | PENDING| 04 | -
agents/base_agent.py       | python    | PENDING| 04 | -
agents/po_agent/           | dir       | PENDING| 05 | -
agents/tl_agent/           | dir       | PENDING| 05 | -
agents/do_agent/           | dir       | PENDING| 05 | -
agents/be_agent/           | dir       | PENDING| 06 | -
agents/fe_agent/           | dir       | PENDING| 06 | -
agents/qa_agent/           | dir       | PENDING| 07 | -

## Workflows + Skills
workflows/skill_executor.py       | python | PENDING | 04 | -
workflows/check_skills.yaml       | yaml   | PENDING | 04 | -
workflows/upgrade_skills.yaml     | yaml   | PENDING | 13 | -
workflows/validate_audit.yaml     | yaml   | PENDING | 13 | -
workflows/build_agent.yaml        | yaml   | PENDING | 04 | -

## Tests + Harness
tests/integration_harness.py      | python | PENDING | 10 | -
tests/real_deploy_test.py         | python | PENDING | 10 | -

## Integrations
integrations/__init__.py          | python | PENDING | 11 | -
integrations/tolaria_bridge.py    | python | PENDING | 11 | -
integrations/discover_mcp.sh      | bash   | PENDING | 11 | -

## IDE Config
.vscode/settings.json             | json   | ACTIVE  | 01 | [NOW]
.vscode/tasks.json                | json   | PENDING | 12 | -
.vscode/launch.json               | json   | PENDING | 12 | -
.tolaria/config.json              | json   | PENDING | 11 | -

## Startup Scripts
start-tolaria.sh                  | bash   | PENDING | 11 | -
start-system.sh                   | bash   | PENDING | 14 | -

## Tolaria
/opt/tolaria/                     | dir    | PENDING | 11 | -

