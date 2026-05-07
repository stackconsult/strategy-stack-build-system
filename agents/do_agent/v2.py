"""
DO_AGENT_v2 — DevOps Agent
Phase 3: Waits for G-06, emits G-07
"""
import sys
sys.path.insert(0, '/opt/agents')
from agents.base_agent import BaseAgent
import asyncio

class DOAgentV2(BaseAgent):
    """DevOps Agent v2 — Phase 3"""
    
    def __init__(self):
        super().__init__("DO_AGENT_v2", "postgresql://agents_user:agents_secure_pass_2026@localhost/governance_db")
    
    async def execute(self, build_id: str, context: dict):
        # Wait for G-06
        max_wait = 30
        for i in range(max_wait):
            async with self.db_pool.acquire() as conn:
                gate = await conn.fetchrow(
                    "SELECT * FROM gates WHERE build_id = $1 AND gate_id = 'G-06'",
                    build_id
                )
            if gate and gate['status'] == 'PASSED':
                break
            await asyncio.sleep(1)
        else:
            raise TimeoutError("G-06 not passed within timeout")
        
        # Emit G-07
        await self.write_gate(build_id, "G-07", "PASSED", {
            "awaited_gate": "G-06",
            "status": "confirmed"
        })
        
        # Log event
        await self.write_governance_event(build_id, "INFRA_DEPLOYED", {
            "gate": "G-06",
            "next_gate": "G-07"
        })
        
        return {
            "status": "COMPLETE",
            "gate_emitted": "G-07",
            "awaited_gate": "G-06"
        }
