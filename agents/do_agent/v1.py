"""
DO_AGENT_v1 — DevOps Agent
Phase 1: Waits for G-02, emits G-03
"""
import sys
sys.path.insert(0, '/opt/agents')
from agents.base_agent import BaseAgent
import asyncio

class DOAgentV1(BaseAgent):
    """DevOps Agent v1 — Phase 1"""
    
    def __init__(self):
        super().__init__("DO_AGENT_v1", "postgresql://agents_user:agents_secure_pass_2026@localhost/governance_db")
    
    async def execute(self, build_id: str, context: dict):
        # Wait for G-02
        max_wait = 30
        for i in range(max_wait):
            async with self.db_pool.acquire() as conn:
                gate = await conn.fetchrow(
                    "SELECT * FROM gates WHERE build_id = $1 AND gate_id = 'G-02'",
                    build_id
                )
            if gate and gate['status'] == 'PASSED':
                break
            await asyncio.sleep(1)
        else:
            raise TimeoutError("G-02 not passed within timeout")
        
        # Emit G-03
        await self.write_gate(build_id, "G-03", "PASSED", {
            "awaited_gate": "G-02",
            "status": "confirmed"
        })
        
        # Log event
        await self.write_governance_event(build_id, "INFRA_READY", {
            "gate": "G-02",
            "next_gate": "G-03"
        })
        
        return {
            "status": "COMPLETE",
            "gate_emitted": "G-03",
            "awaited_gate": "G-02"
        }
