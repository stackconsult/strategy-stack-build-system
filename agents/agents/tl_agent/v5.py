import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.base_agent import BaseAgent

class TLAgentV5(BaseAgent):
    def __init__(self, build_id: str):
        super().__init__("TL_AGENT_v5", build_id, phase=6)

    async def run(self):
        self.set_step("waiting_phase5_convergence")
        await self.write_governance_record("TASK_START", step_id="wait_phase5",
            payload={"waiting_for": ["BE_AGENT_v3", "DO_AGENT_v3", "PO_AGENT_v2"]})
        
        # Wait for COMPLETION_SIGNAL from BE_AGENT_v3, DO_AGENT_v3, PO_AGENT_v2
        await self._wait_for_signals()
        
        # Verify G-33 passed (PO launch authorization)
        async with self.pg_pool.acquire() as conn:
            g33 = await conn.fetchrow("""
                SELECT * FROM gates WHERE gate_id = 'G-33' AND build_id = $1
            """, self.build_id)
            
            if not g33 or g33['status'] != 'PASSED':
                await self.emit_blocker_alert("G-33 (Launch Authorization) not passed", "G-34")
                self.status = "BLOCKED"
                await self.stop()
                return
        
        await self.emit_gate_pass("G-34", evidence={
            "phase5_tracks_complete": ["BE_AGENT_v3", "DO_AGENT_v3", "PO_AGENT_v2"],
            "g33_verified": True
        })
        
        # Dispatch Phase 6 agents: DO_AGENT_v4 + TL_AGENT_v6
        await asyncio.gather(
            self.emit_handoff("DO_AGENT_v4", payload={"build_id": self.build_id}),
            self.emit_handoff("TL_AGENT_v6", payload={"build_id": self.build_id})
        )
        
        await self.write_governance_record("TASK_COMPLETE", status="COMPLETE",
            payload={"gates_passed": ["G-34"]})
        self.status = "COMPLETE"
        await self.stop()

    async def _wait_for_signals(self, timeout_s: int = 7200):
        """Wait for all 3 completion signals."""
        deadline = asyncio.get_event_loop().time() + timeout_s
        required = {"BE_AGENT_v3", "DO_AGENT_v3", "PO_AGENT_v2"}
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
            f"Phase 5 convergence timeout. Missing: {missing}", "G-34")
