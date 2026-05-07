"""
TL_AGENT_v4 — Technical Lead Agent
Phase 4: Waits for G-11, emits G-12
"""
import sys
sys.path.insert(0, '/opt/agents')
from agents.base_agent import BaseAgent
import asyncio

class TLAgentV4(BaseAgent):
    """Technical Lead Agent v4 — Phase 4"""
    
    def __init__(self):
        super().__init__("TL_AGENT_v4", "postgresql://agents_user:agents_secure_pass_2026@localhost/governance_db")
    
    async def execute(self, build_id: str, context: dict):
        # Wait for G-11
        max_wait = 30
        for i in range(max_wait):
            async with self.db_pool.acquire() as conn:
                gate = await conn.fetchrow(
                    "SELECT * FROM gates WHERE build_id = $1 AND gate_id = 'G-11'",
                    build_id
                )
            if gate and gate['status'] == 'PASSED':
                break
            await asyncio.sleep(1)
        else:
            raise TimeoutError("G-11 not passed within timeout")
        
        # Emit G-12
        await self.write_gate(build_id, "G-12", "PASSED", {
            "awaited_gate": "G-11",
            "status": "confirmed"
        })
        
        # Log event
        await self.write_governance_event(build_id, "PHASE_4_COMPLETE", {
            "gate": "G-11",
            "next_gate": "G-12"
        })
        
        return {
            "status": "COMPLETE",
            "gate_emitted": "G-12",
            "awaited_gate": "G-11"
        }
