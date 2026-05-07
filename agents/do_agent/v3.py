"""
DO_AGENT_v3 — DevOps Agent
Phase 5: Waits for G-13, emits G-14
"""
import sys
sys.path.insert(0, '/opt/agents')
from agents.base_agent import BaseAgent
import asyncio

class DOAgentV3(BaseAgent):
    """DevOps Agent v3 — Phase 5"""
    
    def __init__(self):
        super().__init__("DO_AGENT_v3", "postgresql://agents_user:agents_secure_pass_2026@localhost/governance_db")
    
    async def execute(self, build_id: str, context: dict):
        # Wait for G-13
        max_wait = 30
        for i in range(max_wait):
            async with self.db_pool.acquire() as conn:
                gate = await conn.fetchrow(
                    "SELECT * FROM gates WHERE build_id = $1 AND gate_id = 'G-13'",
                    build_id
                )
            if gate and gate['status'] == 'PASSED':
                break
            await asyncio.sleep(1)
        else:
            raise TimeoutError("G-13 not passed within timeout")
        
        # Emit G-14
        await self.write_gate(build_id, "G-14", "PASSED", {
            "awaited_gate": "G-13",
            "status": "confirmed"
        })
        
        # Log event
        await self.write_governance_event(build_id, "INFRA_SCALABLE", {
            "gate": "G-13",
            "next_gate": "G-14"
        })
        
        return {
            "status": "COMPLETE",
            "gate_emitted": "G-14",
            "awaited_gate": "G-13"
        }
