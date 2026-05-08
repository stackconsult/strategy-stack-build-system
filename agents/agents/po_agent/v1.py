import sys
sys.path.insert(0, '/opt/agents')

import asyncio
import json
from datetime import datetime
from agents.base_agent import BaseAgent

class POAgentV1(BaseAgent):
    def __init__(self, build_id: str, prd_path: str):
        super().__init__("PO_AGENT_v1", build_id, phase=1)
        self.prd_path = prd_path
        self.structured_spec = {}

    async def run(self):
        self.set_step("parsing_prd")
        await self.write_governance_record("TASK_START", step_id="parse_prd")
        
        # Read PRD
        with open(self.prd_path, 'r') as f:
            prd_content = f.read()
        
        # Parse PRD into structured_spec
        self.structured_spec = self._parse_prd(prd_content)
        
        # Validate minimum fields
        if not self._validate_spec():
            await self.emit_blocker_alert("PRD missing required fields", "G-01")
            return
        
        # Write spec JSON
        spec_path = f"/Volumes/STORE N GO/builds/{self.build_id}/specs/structured-spec.json"
        await self.fs_write(spec_path, json.dumps(self.structured_spec, indent=2))
        
        await self.emit_gate_pass("G-01", evidence={
            "prd_path": self.prd_path,
            "spec_path": spec_path,
            "fields": list(self.structured_spec.keys())
        })
        
        self.set_step("signing_off")
        await self.emit_gate_pass("G-02", evidence={
            "signed_by": self.agent_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Dispatch TL_AGENT_v1
        await self.emit_handoff("TL_AGENT_v1", payload={
            "structured_spec": self.structured_spec,
            "build_id": self.build_id
        })
        
        await self.write_governance_record("TASK_COMPLETE", status="COMPLETE",
            payload={"gates_passed": ["G-01", "G-02"]})
        self.status = "COMPLETE"
        await self.stop()

    def _parse_prd(self, prd_content: str) -> dict:
        """Parse PRD markdown into structured spec."""
        lines = prd_content.split('\n')
        spec = {
            "project_name": "",
            "objective": "",
            "user_stories": [],
            "acceptance_criteria": [],
            "tech_stack": {},
            "non_functional_requirements": [],
            "definition_of_done": []
        }
        
        current_section = None
        for line in lines:
            line = line.strip()
            if line.startswith("# "):
                current_section = line[2:].lower()
            elif line.startswith("- "):
                if current_section == "user stories":
                    spec["user_stories"].append(line[2:])
                elif current_section == "acceptance criteria":
                    spec["acceptance_criteria"].append(line[2:])
                elif current_section == "non-functional requirements":
                    spec["non_functional_requirements"].append(line[2:])
                elif current_section == "definition of done":
                    spec["definition_of_done"].append(line[2:])
            elif ": " in line and current_section:
                key, value = line.split(": ", 1)
                if current_section == "objective":
                    spec["objective"] = value
                elif current_section == "project name":
                    spec["project_name"] = value
        
        return spec

    def _validate_spec(self) -> bool:
        """Validate minimum required fields."""
        required = ["project_name", "objective", "user_stories", "acceptance_criteria"]
        return all(self.structured_spec.get(field) for field in required)
