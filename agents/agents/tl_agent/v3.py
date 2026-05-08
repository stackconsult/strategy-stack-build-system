import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.base_agent import BaseAgent

class TLAgentV3(BaseAgent):
    def __init__(self, build_id: str):
        super().__init__("TL_AGENT_v3", build_id, phase=4)

    async def run(self):
        self.set_step("waiting_phase3_convergence")
        await self.write_governance_record("TASK_START", step_id="wait_phase3",
            payload={"waiting_for": ["BE_AGENT_v1", "FE_AGENT_v1", "DO_AGENT_v2"]})
        
        # Wait for COMPLETION_SIGNAL from BE_AGENT_v1, FE_AGENT_v1, DO_AGENT_v2
        await self._wait_for_signals()
        
        await self.emit_gate_pass("G-18", evidence={
            "phase3_tracks_complete": ["BE_AGENT_v1", "FE_AGENT_v1", "DO_AGENT_v2"],
            "integration_gate": "PASSED"
        })
        
        # Dispatch QA_AGENT_v1 + BE_AGENT_v2 + FE_AGENT_v2 in parallel
        await asyncio.gather(
            self.emit_handoff("QA_AGENT_v1", payload={"build_id": self.build_id}),
            self.emit_handoff("BE_AGENT_v2", payload={"build_id": self.build_id}),
            self.emit_handoff("FE_AGENT_v2", payload={"build_id": self.build_id})
        )
        
        await self.write_governance_record("TASK_COMPLETE", status="COMPLETE",
            payload={"gates_passed": ["G-18"]})
        self.status = "COMPLETE"
        await self.stop()

    async def _wait_for_signals(self, timeout_s: int = 7200):
        """Wait for all 3 completion signals."""
        deadline = asyncio.get_event_loop().time() + timeout_s
        required = {"BE_AGENT_v1", "FE_AGENT_v1", "DO_AGENT_v2"}
        received = set()
        
        while asyncio.get_event_loop().time() < deadline:
            messages = await self.receive_messages(max_messages=20)
            for msg in messages:
                if msg.get("message_type") == "COMPLETION_SIGNAL":
                    sender = msg.get("from_agent")
                    if sender in required:
                        received.add(sender)
                        await self.write_governance_record("STATUS_UPDATE",
                            step_id="signal_received",
                            payload={"from": sender, "remaining": list(required - received)})
            
            if required.issubset(received):
                return
            
            await asyncio.sleep(10)
        
        missing = required - received
        await self.emit_blocker_alert(
            f"Phase 3 convergence timeout. Missing: {missing}", "G-18")
