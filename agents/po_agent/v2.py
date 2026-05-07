import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.base_agent import BaseAgent

class POAgentV2(BaseAgent):
    def __init__(self, build_id: str, prd_path: str):
        super().__init__("PO_AGENT_v2", build_id, phase=5)
        self.prd_path = prd_path

    async def run(self):
        self.set_step("checking_launch_authorization")
        await self.write_governance_record("TASK_START", step_id="check_launch_auth")
        
        # CRITICAL: G-33 is a hard gate - must check failures before emitting
        async with self.pg_pool.acquire() as conn:
            # Check for unresolved blockers
            blockers = await conn.fetch("""
                SELECT * FROM blockers WHERE build_id = $1 AND resolved = false
            """, self.build_id)
            
            if blockers:
                failure_list = [f"{b['gate_id']}: {b['message']}" for b in blockers]
                await self.emit_blocker_alert(
                    f"Launch authorization blocked. Unresolved blockers: {failure_list}", 
                    "G-33")
                self.status = "BLOCKED"
                await self.stop()
                return
        
        # Check all gates are passed
        async with self.pg_pool.acquire() as conn:
            gates = await conn.fetch("""
                SELECT * FROM gates WHERE build_id = $1 AND status != 'PASSED'
            """, self.build_id)
            
            if gates:
                failure_list = [g['gate_id'] for g in gates]
                await self.emit_blocker_alert(
                    f"Launch authorization blocked. Gates not passed: {failure_list}", 
                    "G-33")
                self.status = "BLOCKED"
                await self.stop()
                return
        
        # All checks passed - emit G-33
        await self.emit_gate_pass("G-33", evidence={
            "authorized": True,
            "checked_by": self.agent_id,
            "blockers_count": 0,
            "gates_failed_count": 0
        })
        
        await self.emit_gate_pass("G-34", evidence={
            "launch_authorized": True,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # Dispatch TL_AGENT_v5
        await self.emit_handoff("TL_AGENT_v5", payload={"build_id": self.build_id})
        
        await self.write_governance_record("TASK_COMPLETE", status="COMPLETE",
            payload={"gates_passed": ["G-33", "G-34"]})
        self.status = "COMPLETE"
        await self.stop()
