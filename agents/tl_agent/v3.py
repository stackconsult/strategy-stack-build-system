"""
TL_AGENT_v3 — Technical Lead Agent
Phase 3: Waits for G-07, emits G-08
"""
import sys
sys.path.insert(0, '/opt/agents')
from agents.base_agent import BaseAgent
import asyncio

class TLAgentV3(BaseAgent):
    """Technical Lead Agent v3 — Phase 3"""
    
    def __init__(self):
        super().__init__("TL_AGENT_v3", "postgresql://agents_user:agents_secure_pass_2026@localhost/governance_db")
    
    async def execute(self, build_id: str, context: dict):
        # Wait for G-07
        max_wait = 30
        for i in range(max_wait):
            async with self.db_pool.acquire() as conn:
                gate = await conn.fetchrow(
                    "SELECT * FROM gates WHERE build_id = $1 AND gate_id = 'G-07'",
                    build_id
                )
            if gate and gate['status'] == 'PASSED':
                break
            await asyncio.sleep(1)
        else:
            raise TimeoutError("G-07 not passed within timeout")
        
        # Emit G-08
        await self.write_gate(build_id, "G-08", "PASSED", {
            "awaited_gate": "G-07",
            "status": "confirmed"
        })
        
        # Log event
        await self.write_governance_event(build_id, "PHASE_3_COMPLETE", {
            "gate": "G-07",
            "next_gate": "G-08"
        })
        
        return {
            "status": "COMPLETE",
            "gate_emitted": "G-08",
            "awaited_gate": "G-07"
        }
