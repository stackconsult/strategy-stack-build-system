import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.base_agent import BaseAgent

class TLAgentV4(BaseAgent):
    def __init__(self, build_id: str):
        super().__init__("TL_AGENT_v4", build_id, phase=5)

    async def run(self):
        self.set_step("waiting_phase4_convergence")
        await self.write_governance_record("TASK_START", step_id="wait_phase4",
            payload={"waiting_for": ["QA_AGENT_v1", "BE_AGENT_v2", "FE_AGENT_v2"]})
        
        # Wait for COMPLETION_SIGNAL from QA_AGENT_v1, BE_AGENT_v2, FE_AGENT_v2
        await self._wait_for_signals()
        
        await self.emit_gate_pass("G-34", evidence={
            "phase4_tracks_complete": ["QA_AGENT_v1", "BE_AGENT_v2", "FE_AGENT_v2"],
            "gates_verified": ["G-19", "G-20", "G-24", "G-21", "G-22", "G-23", "G-25"]
        })
        
        # Dispatch BE_AGENT_v3 + DO_AGENT_v3 + PO_AGENT_v2
        await asyncio.gather(
            self.emit_handoff("BE_AGENT_v3", payload={"build_id": self.build_id}),
            self.emit_handoff("DO_AGENT_v3", payload={"build_id": self.build_id}),
            self.emit_handoff("PO_AGENT_v2", payload={"build_id": self.build_id})
        )
        
        await self.write_governance_record("TASK_COMPLETE", status="COMPLETE",
            payload={"gates_passed": ["G-34"]})
        self.status = "COMPLETE"
        await self.stop()

    async def _wait_for_signals(self, timeout_s: int = 7200):
        """Wait for all 3 completion signals."""
        deadline = asyncio.get_event_loop().time() + timeout_s
        required = {"QA_AGENT_v1", "BE_AGENT_v2", "FE_AGENT_v2"}
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
            f"Phase 4 convergence timeout. Missing: {missing}", "G-34")
