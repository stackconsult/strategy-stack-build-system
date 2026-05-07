"""
FE_AGENT_v2 — Frontend Engineer Agent
Phase 4: Waits for G-10, emits G-11
"""
import sys
sys.path.insert(0, '/opt/agents')
from agents.base_agent import BaseAgent
import asyncio

class FEAgentV2(BaseAgent):
    """Frontend Engineer Agent v2 — Phase 4"""
    
    def __init__(self):
        super().__init__("FE_AGENT_v2", "postgresql://agents_user:agents_secure_pass_2026@localhost/governance_db")
    
    async def execute(self, build_id: str, context: dict):
        # Wait for G-10
        max_wait = 30
        for i in range(max_wait):
            async with self.db_pool.acquire() as conn:
                gate = await conn.fetchrow(
                    "SELECT * FROM gates WHERE build_id = $1 AND gate_id = 'G-10'",
                    build_id
                )
            if gate and gate['status'] == 'PASSED':
                break
            await asyncio.sleep(1)
        else:
            raise TimeoutError("G-10 not passed within timeout")
        
        # Emit G-11
        await self.write_gate(build_id, "G-11", "PASSED", {
            "awaited_gate": "G-10",
            "status": "confirmed"
        })
        
        # Log event
        await self.write_governance_event(build_id, "FRONTEND_TESTED", {
            "gate": "G-10",
            "next_gate": "G-11"
        })
        
        return {
            "status": "COMPLETE",
            "gate_emitted": "G-11",
            "awaited_gate": "G-10"
        }
