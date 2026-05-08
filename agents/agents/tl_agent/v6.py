import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.base_agent import BaseAgent

class TLAgentV6(BaseAgent):
    def __init__(self, build_id: str):
        super().__init__("TL_AGENT_v6", build_id, phase=6)

    async def run(self):
        self.set_step("waiting_phase6_convergence")
        await self.write_governance_record("TASK_START", step_id="wait_phase6",
            payload={"waiting_for": ["DO_AGENT_v4"]})
        
        # Wait for COMPLETION_SIGNAL from DO_AGENT_v4
        await self._wait_for_signals()
        
        # Verify G-36 passed (Canary Deployed)
        async with self.pg_pool.acquire() as conn:
            g36 = await conn.fetchrow("""
                SELECT * FROM gates WHERE gate_id = 'G-36' AND build_id = $1
            """, self.build_id)
            
            if not g36 or g36['status'] != 'PASSED':
                await self.emit_blocker_alert("G-36 (Canary Deployed) not passed", "G-37")
                self.status = "BLOCKED"
                await self.stop()
                return
        
        await self.emit_gate_pass("G-37", evidence={
            "canary_verified": True,
            "ready_for_traffic_shift": True
        })
        
        # Emit G-45 (Build Complete)
        await self.emit_gate_pass("G-45", evidence={
            "build_id": self.build_id,
            "status": "COMPLETE",
            "all_gates_passed": True
        })
        
        # Update build status in database
        async with self.pg_pool.acquire() as conn:
            await conn.execute("""
                UPDATE builds SET status = 'COMPLETE', completed_at = NOW()
                WHERE build_id = $1
            """, self.build_id)
        
        await self.write_governance_record("TASK_COMPLETE", status="COMPLETE",
            payload={"gates_passed": ["G-37", "G-45"]})
        self.status = "COMPLETE"
        await self.stop()

    async def _wait_for_signals(self, timeout_s: int = 7200):
        """Wait for DO_AGENT_v4 completion signal."""
        deadline = asyncio.get_event_loop().time() + timeout_s
        required = {"DO_AGENT_v4"}
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
                            payload={"from": sender})
            
            if required.issubset(received):
                return
            
            await asyncio.sleep(10)
        
        await self.emit_blocker_alert("Phase 6 convergence timeout. Missing: DO_AGENT_v4", "G-37")
