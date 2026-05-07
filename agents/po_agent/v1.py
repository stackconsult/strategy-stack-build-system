"""
PO_AGENT_v1 — Product Owner Agent
Phase 1: Takes PRD, writes spec, emits G-01
"""
import sys
sys.path.insert(0, '/opt/agents')
from agents.base_agent import BaseAgent
from pathlib import Path
import json

class POAgentV1(BaseAgent):
    """Product Owner Agent v1 — Phase 1"""
    
    def __init__(self):
        super().__init__("PO_AGENT_v1", "postgresql://agents_user:agents_secure_pass_2026@localhost/governance_db")
    
    async def execute(self, build_id: str, context: dict):
        prd_path = context.get("prd_path")
        if not prd_path:
            raise ValueError("prd_path required in context")
        
        # Read PRD
        prd_file = Path(prd_path)
        if not prd_file.exists():
            raise FileNotFoundError(f"PRD not found: {prd_path}")
        
        with open(prd_file) as f:
            prd_content = f.read()
        
        # Write spec (simplified for v1)
        spec_path = prd_file.parent / f"{prd_file.stem}_SPEC.md"
        with open(spec_path, 'w') as f:
            f.write(f"# Specification for {prd_file.stem}\n\n")
            f.write(f"Generated from PRD: {prd_path}\n\n")
            f.write(f"PRD Content:\n{prd_content}\n")
        
        # Emit gate G-01
        await self.write_gate(build_id, "G-01", "PASSED", {
            "prd_path": prd_path,
            "spec_path": str(spec_path),
            "prd_lines": len(prd_content.splitlines())
        })
        
        # Log event
        await self.write_governance_event(build_id, "SPEC_WRITTEN", {
            "spec_path": str(spec_path),
            "prd_lines": len(prd_content.splitlines())
        })
        
        return {
            "status": "COMPLETE",
            "spec_path": str(spec_path),
            "gate_emitted": "G-01"
        }
