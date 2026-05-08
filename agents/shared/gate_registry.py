GATE_REGISTRY = {
  "G-01": {
    "gate_id": "G-01",
    "name": "PRD_SIGN_OFF",
    "owner_agent": "PO_AGENT_v1",
    "phase": "PHASE_1",
    "blocks": "Phase 1 → TL_AGENT_v1",
    "hard": True
  },
  "G-02": {
    "gate_id": "G-02",
    "name": "ADR_LOCK",
    "owner_agent": "TL_AGENT_v1",
    "phase": "PHASE_1",
    "blocks": "Phase 1 → DO_AGENT_v1",
    "hard": True
  },
  "G-03": {
    "gate_id": "G-03",
    "name": "REPO_ZERO_TO_RUNNING",
    "owner_agent": "DO_AGENT_v1",
    "phase": "PHASE_2",
    "blocks": "Phase 2 → CI pipeline",
    "hard": True
  },
  "G-04": {
    "gate_id": "G-04",
    "name": "CI_GREEN",
    "owner_agent": "DO_AGENT_v1",
    "phase": "PHASE_2",
    "blocks": "Phase 2 → TL_AGENT_v2",
    "hard": True
  },
  "G-05": {
    "gate_id": "G-05",
    "name": "API_SPEC_LOCK",
    "owner_agent": "TL_AGENT_v2",
    "phase": "PHASE_2",
    "blocks": "Phase 2 → Phase 3 parallel tracks",
    "hard": True
  },
  "G-06": {
    "gate_id": "G-06",
    "name": "SCAFFOLD_TL_REVIEW_BE",
    "owner_agent": "BE_AGENT_v1",
    "phase": "PHASE_3",
    "blocks": "Phase 3 Track A → core features",
    "hard": True
  },
  "G-07": {
    "gate_id": "G-07",
    "name": "AUTH_PR_REVIEW",
    "owner_agent": "BE_AGENT_v1",
    "phase": "PHASE_3",
    "blocks": "Phase 3 Track A → ERD",
    "hard": True
  },
  "G-08": {
    "gate_id": "G-08",
    "name": "ERD_APPROVAL",
    "owner_agent": "BE_AGENT_v1",
    "phase": "PHASE_3",
    "blocks": "Phase 3 Track A → test coverage",
    "hard": True
  },
  "G-09": {
    "gate_id": "G-09",
    "name": "BE_COVERAGE_GATE",
    "owner_agent": "BE_AGENT_v1",
    "phase": "PHASE_3",
    "blocks": "Phase 3 Track A → Track complete",
    "hard": True
  },
  "G-10": {
    "gate_id": "G-10",
    "name": "SCAFFOLD_TL_REVIEW_FE",
    "owner_agent": "FE_AGENT_v1",
    "phase": "PHASE_3",
    "blocks": "Phase 3 Track B → auth flow",
    "hard": True
  },
  "G-11": {
    "gate_id": "G-11",
    "name": "AUTH_FLOW_VISUAL",
    "owner_agent": "FE_AGENT_v1",
    "phase": "PHASE_3",
    "blocks": "Phase 3 Track B → core UI",
    "hard": True
  },
  "G-12": {
    "gate_id": "G-12",
    "name": "FE_COVERAGE_GATE",
    "owner_agent": "FE_AGENT_v1",
    "phase": "PHASE_3",
    "blocks": "Phase 3 Track B → Track complete",
    "hard": True
  },
  "G-13": {
    "gate_id": "G-13",
    "name": "TF_PLAN_GATE",
    "owner_agent": "DO_AGENT_v2",
    "phase": "PHASE_3",
    "blocks": "Phase 3 Track C → container hardening",
    "hard": True
  },
  "G-14": {
    "gate_id": "G-14",
    "name": "CVE_SCAN",
    "owner_agent": "DO_AGENT_v2",
    "phase": "PHASE_3",
    "blocks": "Phase 3 Track C → non-root check",
    "hard": True
  },
  "G-15": {
    "gate_id": "G-15",
    "name": "NON_ROOT",
    "owner_agent": "DO_AGENT_v2",
    "phase": "PHASE_3",
    "blocks": "Phase 3 Track C → staging env",
    "hard": True
  },
  "G-16": {
    "gate_id": "G-16",
    "name": "LOAD_TEST",
    "owner_agent": "DO_AGENT_v2",
    "phase": "PHASE_3",
    "blocks": "Phase 3 Track C → SSL check",
    "hard": True
  },
  "G-17": {
    "gate_id": "G-17",
    "name": "STAGING_SSL",
    "owner_agent": "DO_AGENT_v2",
    "phase": "PHASE_3",
    "blocks": "Phase 3 Track C → Track complete",
    "hard": True
  },
  "G-18": {
    "gate_id": "G-18",
    "name": "PHASE_3_COMPLETE",
    "owner_agent": "TL_AGENT_v3",
    "phase": "PHASE_4",
    "blocks": "Phase 4 → Phase 4 agents",
    "hard": True
  },
  "G-19": {
    "gate_id": "G-19",
    "name": "SECURITY_SCAN_PASS",
    "owner_agent": "QA_AGENT_v1",
    "phase": "PHASE_4",
    "blocks": "Phase 4 → hardening",
    "hard": True
  },
  "G-20": {
    "gate_id": "G-20",
    "name": "E2E_PASS",
    "owner_agent": "QA_AGENT_v1",
    "phase": "PHASE_4",
    "blocks": "Phase 4 → Phase 4 complete",
    "hard": True
  },
  "G-21": {
    "gate_id": "G-21",
    "name": "TASK_IDEMPOTENCY",
    "owner_agent": "BE_AGENT_v2",
    "phase": "PHASE_4",
    "blocks": "Phase 4 BE → validation",
    "hard": True
  },
  "G-22": {
    "gate_id": "G-22",
    "name": "VALIDATION_GATE",
    "owner_agent": "BE_AGENT_v2",
    "phase": "PHASE_4",
    "blocks": "Phase 4 BE → security scan",
    "hard": True
  },
  "G-23": {
    "gate_id": "G-23",
    "name": "SECURITY_SCAN_GATE",
    "owner_agent": "BE_AGENT_v2",
    "phase": "PHASE_4",
    "blocks": "Phase 4 BE → Phase 4 BE complete",
    "hard": True
  },
  "G-24": {
    "gate_id": "G-24",
    "name": "API_INTEGRATION_PASS",
    "owner_agent": "FE_AGENT_v2",
    "phase": "PHASE_4",
    "blocks": "Phase 4 FE → UX optimization",
    "hard": True
  },
  "G-25": {
    "gate_id": "G-25",
    "name": "UX_OPTIMIZATION",
    "owner_agent": "FE_AGENT_v2",
    "phase": "PHASE_4",
    "blocks": "Phase 4 FE → Phase 4 FE complete",
    "hard": True
  },
  "G-26": {
    "gate_id": "G-26",
    "name": "METRICS_LIVE",
    "owner_agent": "BE_AGENT_v3",
    "phase": "PHASE_5",
    "blocks": "Phase 5 BE → tracing",
    "hard": True
  },
  "G-27": {
    "gate_id": "G-27",
    "name": "TRACE_VISIBLE",
    "owner_agent": "BE_AGENT_v3",
    "phase": "PHASE_5",
    "blocks": "Phase 5 BE → Phase 5 BE complete",
    "hard": True
  },
  "G-28": {
    "gate_id": "G-28",
    "name": "ALERT_FIRE",
    "owner_agent": "DO_AGENT_v3",
    "phase": "PHASE_5",
    "blocks": "Phase 5 DO → dashboard",
    "hard": True
  },
  "G-29": {
    "gate_id": "G-29",
    "name": "DASHBOARD",
    "owner_agent": "DO_AGENT_v3",
    "phase": "PHASE_5",
    "blocks": "Phase 5 DO → runbooks",
    "hard": True
  },
  "G-30": {
    "gate_id": "G-30",
    "name": "ROLLBACK_TEST",
    "owner_agent": "DO_AGENT_v3",
    "phase": "PHASE_5",
    "blocks": "Phase 5 DO → DB restore",
    "hard": True
  },
  "G-31": {
    "gate_id": "G-31",
    "name": "DB_RESTORE",
    "owner_agent": "DO_AGENT_v3",
    "phase": "PHASE_5",
    "blocks": "Phase 5 DO → Phase 5 DO complete",
    "hard": True
  },
  "G-32": {
    "gate_id": "G-32",
    "name": "AUTH_UAT_PASS",
    "owner_agent": "PO_AGENT_v2",
    "phase": "PHASE_5",
    "blocks": "Phase 5 PO → UAT sign-off",
    "hard": True
  },
  "G-33": {
    "gate_id": "G-33",
    "name": "UAT_ACCEPTANCE",
    "owner_agent": "PO_AGENT_v2",
    "phase": "PHASE_5",
    "blocks": "Phase 5 PO → Phase 5 PO complete",
    "hard": True
  },
  "G-34": {
    "gate_id": "G-34",
    "name": "PHASE_5_COMPLETE",
    "owner_agent": "TL_AGENT_v4",
    "phase": "PHASE_5",
    "blocks": "Phase 5 → Phase 6",
    "hard": True
  },
  "G-35": {
    "gate_id": "G-35",
    "name": "PREDEPLOY_CHECKLIST",
    "owner_agent": "DO_AGENT_v4",
    "phase": "PHASE_6",
    "blocks": "Phase 6 → image verified",
    "hard": True
  },
  "G-36": {
    "gate_id": "G-36",
    "name": "IMAGE_VERIFIED",
    "owner_agent": "DO_AGENT_v4",
    "phase": "PHASE_6",
    "blocks": "Phase 6 → migration dry run",
    "hard": True
  },
  "G-37": {
    "gate_id": "G-37",
    "name": "MIGRATION_DRY_RUN",
    "owner_agent": "DO_AGENT_v4",
    "phase": "PHASE_6",
    "blocks": "Phase 6 → production deploy",
    "hard": True
  },
  "G-38": {
    "gate_id": "G-38",
    "name": "MIGRATION_PROD",
    "owner_agent": "DO_AGENT_v4",
    "phase": "PHASE_6",
    "blocks": "Phase 6 → canary deploy",
    "hard": True
  },
  "G-39": {
    "gate_id": "G-39",
    "name": "CANARY_LIVE",
    "owner_agent": "DO_AGENT_v4",
    "phase": "PHASE_6",
    "blocks": "Phase 6 → full rollout",
    "hard": True
  },
  "G-40": {
    "gate_id": "G-40",
    "name": "CANARY_QA",
    "owner_agent": "QA_AGENT_v2",
    "phase": "PHASE_6",
    "blocks": "Phase 6 → 7-day stability watch",
    "hard": True
  },
  "G-41": {
    "gate_id": "G-41",
    "name": "FULL_ROLLOUT",
    "owner_agent": "DO_AGENT_v4",
    "phase": "PHASE_6",
    "blocks": "Phase 6 → smoke test",
    "hard": True
  },
  "G-42": {
    "gate_id": "G-42",
    "name": "SMOKE_PASS",
    "owner_agent": "DO_AGENT_v4",
    "phase": "PHASE_6",
    "blocks": "Phase 6 → 7-day watch",
    "hard": True
  },
  "G-43": {
    "gate_id": "G-43",
    "name": "STABLE_7D",
    "owner_agent": "QA_AGENT_v2",
    "phase": "PHASE_6",
    "blocks": "Phase 6 → build closure",
    "hard": True
  },
  "G-44": {
    "gate_id": "G-44",
    "name": "BUILD_CERTIFICATE",
    "owner_agent": "TL_AGENT_v5",
    "phase": "PHASE_6",
    "blocks": "Phase 6 → archive",
    "hard": True
  },
  "G-45": {
    "gate_id": "G-45",
    "name": "ARCHIVE_COMPLETE",
    "owner_agent": "TL_AGENT_v5",
    "phase": "PHASE_6",
    "blocks": "Phase 6 → build complete",
    "hard": True
  }
}

def get_gate(gate_id: str) -> dict:
  return GATE_REGISTRY.get(gate_id)

def get_gates_for_phase(phase: str) -> list:
  return [gate for gate in GATE_REGISTRY.values() if gate["phase"] == phase]

def get_gate_owner(gate_id: str) -> str:
  gate = GATE_REGISTRY.get(gate_id)
  if gate:
    return gate["owner_agent"]
  return None

def validate_gate_pass_authority(gate_id: str, agent_id: str) -> bool:
  gate = GATE_REGISTRY.get(gate_id)
  if not gate:
    return False
  return gate["owner_agent"] == agent_id
