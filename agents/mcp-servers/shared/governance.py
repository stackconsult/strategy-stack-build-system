"""
Governance log writer — append-only JSONL for all agent records.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

VAULT_ROOT = Path(os.getenv("VAULT_PATH", "/opt/agents"))

def append_governance_record(
    record_type: str,
    build_id: str,
    agent_id: str,
    payload: Dict[str, Any],
    phase: Optional[str] = None,
    step: Optional[str] = None
) -> str:
    """
    Append a governance record to the build's governance.jsonl file.
    Returns the record_id written.
    """
    record_id = f"{record_type}-{build_id}-{datetime.utcnow().isoformat()}"
    
    record = {
        "record_id": record_id,
        "record_type": record_type,
        "build_id": build_id,
        "agent_id": agent_id,
        "phase": phase,
        "step": step,
        "timestamp_utc": datetime.utcnow().isoformat(),
        "payload": payload,
    }
    
    # Build-specific governance log
    gov_path = VAULT_ROOT / "builds" / build_id / "governance.jsonl"
    gov_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(gov_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")
    
    # Also append to global bootstrap log
    bootstrap_path = VAULT_ROOT / "bootstrap-log.md"
    with open(bootstrap_path, "a", encoding="utf-8") as f:
        f.write(f"\n[{record_type}] {datetime.utcnow().isoformat()} | {build_id} | {agent_id}")
        if payload.get("gate_id"):
            f.write(f" | Gate: {payload['gate_id']}")
        if payload.get("status"):
            f.write(f" | Status: {payload['status']}")
        f.write("\n")
    
    return record_id

def read_governance_log(build_id: str, limit: int = 100) -> list:
    """Read governance records for a build."""
    gov_path = VAULT_ROOT / "builds" / build_id / "governance.jsonl"
    if not gov_path.exists():
        return []
    
    records = []
    with open(gov_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    
    return records[-limit:]

def get_latest_gate(build_id: str, gate_prefix: str = "G-") -> Optional[Dict]:
    """Get the latest gate record for a build."""
    records = read_governance_log(build_id, limit=1000)
    for record in reversed(records):
        if record.get("record_type") == "GATE_PASS":
            payload = record.get("payload", {})
            gate_id = payload.get("gate_id", "")
            if gate_id.startswith(gate_prefix):
                return record
    return None

def verify_log_completeness(build_id: str) -> bool:
    """
    Verify that the governance log for a build is complete.
    Checks for required record types in sequence.
    """
    records = read_governance_log(build_id, limit=10000)
    required_types = [
        "BUILD_INITIALIZED",
        "ORCHESTRATOR_READY",
        "TASK_START",
    ]
    
    found_types = set()
    for record in records:
        found_types.add(record.get("record_type"))
    
    for req in required_types:
        if req not in found_types:
            return False
    
    return True

def write_build_certificate(build_id: str) -> str:
    """
    Write the final build certificate after all gates pass.
    Returns the certificate file path.
    """
    cert_path = VAULT_ROOT / "builds" / build_id / "BUILD_CERTIFICATE.json"
    
    records = read_governance_log(build_id, limit=10000)
    gate_records = [r for r in records if r.get("record_type") == "GATE_PASS"]
    blocker_records = [r for r in records if r.get("record_type") == "BLOCKER_RAISED"]
    
    certificate = {
        "build_id": build_id,
        "certified_at": datetime.utcnow().isoformat(),
        "certification_version": "1.0.0",
        "total_gates": 45,
        "gates_passed": len(gate_records),
        "blockers_raised": len(blocker_records),
        "blockers_resolved": len([r for r in blocker_records if any(
            br.get("record_type") == "BLOCKER_RESOLVED" and 
            br.get("payload", {}).get("blocker_id") == r.get("payload", {}).get("blocker_id")
            for br in records
        )]),
        "log_completeness_verified": verify_log_completeness(build_id),
        "gates": [
            {
                "gate_id": r.get("payload", {}).get("gate_id"),
                "passed_at": r.get("timestamp_utc"),
                "passed_by": r.get("agent_id"),
            }
            for r in gate_records
        ],
    }
    
    with open(cert_path, "w", encoding="utf-8") as f:
        json.dumps(certificate, f, indent=2, default=str)
    
    # Append certificate write to governance log
    append_governance_record(
        record_type="BUILD_CERTIFICATE_WRITTEN",
        build_id=build_id,
        agent_id="ORCHESTRATOR_AGENT",
        payload={"certificate_path": str(cert_path)},
    )
    
    return str(cert_path)

def rebuild_state_from_log(build_id: str) -> Dict[str, Any]:
    """
    Rebuild the current state of a build from its governance log.
    Used on orchestrator restart.
    """
    records = read_governance_log(build_id, limit=10000)
    
    state = {
        "build_id": build_id,
        "status": "UNKNOWN",
        "current_phase": None,
        "active_agents": set(),
        "passed_gates": [],
        "open_blockers": [],
        "last_record_timestamp": None,
    }
    
    for record in records:
        record_type = record.get("record_type")
        payload = record.get("payload", {})
        
        if record_type == "BUILD_INITIALIZED":
            state["status"] = "INITIALIZED"
        elif record_type == "PHASE_OPEN":
            state["current_phase"] = payload.get("phase")
        elif record_type == "TASK_START":
            state["active_agents"].add(record.get("agent_id"))
        elif record_type == "TASK_COMPLETE":
            state["active_agents"].discard(record.get("agent_id"))
        elif record_type == "GATE_PASS":
            state["passed_gates"].append(payload.get("gate_id"))
        elif record_type == "BLOCKER_RAISED":
            state["open_blockers"].append(payload.get("blocker_id"))
        elif record_type == "BLOCKER_RESOLVED":
            resolved_id = payload.get("blocker_id")
            if resolved_id in state["open_blockers"]:
                state["open_blockers"].remove(resolved_id)
        elif record_type == "BUILD_COMPLETE":
            state["status"] = "COMPLETE"
        
        state["last_record_timestamp"] = record.get("timestamp_utc")
    
    # Convert sets to lists for JSON serialization
    state["active_agents"] = list(state["active_agents"])
    
    return state

def archive_build_log(build_id: str) -> str:
    """
    Archive a completed build's governance log.
    Returns the archive file path.
    """
    import shutil
    import gzip
    
    build_dir = VAULT_ROOT / "builds" / build_id
    archive_dir = VAULT_ROOT / "builds" / ".archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    archive_path = archive_dir / f"{build_id}.tar.gz"
    
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(build_dir, arcname=build_id)
    
    # Write archive record
    append_governance_record(
        record_type="ARCHIVE_COMPLETE",
        build_id=build_id,
        agent_id="ORCHESTRATOR_AGENT",
        payload={"archive_path": str(archive_path)},
    )
    
    return str(archive_path)

def backfill_missing_records(build_id: str, records: list) -> int:
    """
    Backfill missing governance records (e.g., from failed writes).
    Returns count of records backfilled.
    """
    gov_path = VAULT_ROOT / "builds" / build_id / "governance.jsonl"
    
    backfilled = 0
    with open(gov_path, "a", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, default=str) + "\n")
            backfilled += 1
    
    # Write backfill record
    append_governance_record(
        record_type="BACKFILL_RECORD",
        build_id=build_id,
        agent_id="ORCHESTRATOR_AGENT",
        payload={"count": backfilled},
    )
    
    return backfilled

def log_unauthorized_halt_attempt(build_id: str, agent_id: str, reason: str) -> None:
    """Log an unauthorized halt attempt."""
    append_governance_record(
        record_type="UNAUTHORIZED_HALT_ATTEMPT",
        build_id=build_id,
        agent_id=agent_id,
        payload={"reason": reason, "timestamp": datetime.utcnow().isoformat()},
    )

def write_heartbeat(build_id: str, agent_id: str, step: str, status: str) -> None:
    """Write a heartbeat record."""
    append_governance_record(
        record_type="HEARTBEAT",
        build_id=build_id,
        agent_id=agent_id,
        payload={"step": step, "status": status},
    )


# Import tarfile at module level for archive function
import tarfile
import shutil
import gzip

# Initialize VAULT_ROOT
VAULT_ROOT = Path(os.getenv("VAULT_PATH", "/opt/agents"))
