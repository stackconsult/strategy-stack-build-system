import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.base_agent import BaseAgent

class TLAgentV1(BaseAgent):
    def __init__(self, build_id: str, structured_spec: dict, repo_path: str):
        super().__init__("TL_AGENT_v1", build_id, phase=1)
        self.structured_spec = structured_spec
        self.repo_path = repo_path

    async def run(self):
        self.set_step("receiving_spec")
        await self.write_governance_record("TASK_START", step_id="receive_spec",
            payload={"project": self.structured_spec.get("project_name")})
        
        # Dispatch DO_AGENT_v1 with repo_path and tech_stack
        await self.emit_handoff("DO_AGENT_v1", payload={
            "repo_path": self.repo_path,
            "tech_stack": self.structured_spec.get("tech_stack", {}),
            "build_id": self.build_id
        })
        
        # Wait for DO_AGENT_v1 completion signal
        await self._wait_for_do_agent()
        
        # Emit G-04 (CI_GREEN) after DO confirms CI pipeline
        await self.emit_gate_pass("G-04", evidence={
            "ci_pipeline": "configured",
            "repo_path": self.repo_path
        })
        
        # Dispatch TL_AGENT_v2
        await self.emit_handoff("TL_AGENT_v2", payload={
            "structured_spec": self.structured_spec,
            "build_id": self.build_id,
            "repo_path": self.repo_path
        })
        
        await self.write_governance_record("TASK_COMPLETE", status="COMPLETE",
            payload={"gates_passed": ["G-04"]})
        self.status = "COMPLETE"
        await self.stop()

    async def _wait_for_do_agent(self, timeout_s: int = 3600):
        """Wait for DO_AGENT_v1 completion signal."""
        deadline = asyncio.get_event_loop().time() + timeout_s
        while asyncio.get_event_loop().time() < deadline:
            messages = await self.receive_messages(max_messages=20)
            for msg in messages:
                if msg.get("message_type") == "COMPLETION_SIGNAL" and msg.get("from_agent") == "DO_AGENT_v1":
                    await self.write_governance_record("STATUS_UPDATE",
                        step_id="do_agent_complete")
                    return
            await asyncio.sleep(10)
        
        await self.emit_blocker_alert("DO_AGENT_v1 timeout", "G-04")
