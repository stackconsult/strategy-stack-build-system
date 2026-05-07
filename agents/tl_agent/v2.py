"""
TL_AGENT_v2 — Technical Lead Agent
Phase 2: Waits for G-03, emits G-04
"""
import sys
sys.path.insert(0, '/opt/agents')
from agents.base_agent import BaseAgent
import asyncio

class TLAgentV2(BaseAgent):
    """Technical Lead Agent v2 — Phase 2"""
    
    def __init__(self):
        super().__init__("TL_AGENT_v2", "postgresql://agents_user:agents_secure_pass_2026@localhost/governance_db")
    
    async def execute(self, build_id: str, context: dict):
        # Wait for G-03
        max_wait = 30
        for i in range(max_wait):
            async with self.db_pool.acquire() as conn:
                gate = await conn.fetchrow(
                    "SELECT * FROM gates WHERE build_id = $1 AND gate_id = 'G-03'",
                    build_id
                )
            if gate and gate['status'] == 'PASSED':
                break
            await asyncio.sleep(1)
        else:
            raise TimeoutError("G-03 not passed within timeout")
        
        # Emit G-04
        await self.write_gate(build_id, "G-04", "PASSED", {
            "awaited_gate": "G-03",
            "status": "confirmed"
        })
        
        # Log event
        await self.write_governance_event(build_id, "PHASE_2_READY", {
            "gate": "G-03",
            "next_gate": "G-04"
        })
        
        return {
            "status": "COMPLETE",
            "gate_emitted": "G-04",
            "awaited_gate": "G-03"
        }
