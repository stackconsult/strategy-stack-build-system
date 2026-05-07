"""
BE_AGENT_v1 — Backend Engineer Agent
Phase 3: Waits for G-04, emits G-05
"""
import sys
sys.path.insert(0, '/opt/agents')
from agents.base_agent import BaseAgent
import asyncio

class BEAgentV1(BaseAgent):
    """Backend Engineer Agent v1 — Phase 3"""
    
    def __init__(self):
        super().__init__("BE_AGENT_v1", "postgresql://agents_user:agents_secure_pass_2026@localhost/governance_db")
    
    async def execute(self, build_id: str, context: dict):
        # Wait for G-04
        max_wait = 30
        for i in range(max_wait):
            async with self.db_pool.acquire() as conn:
                gate = await conn.fetchrow(
                    "SELECT * FROM gates WHERE build_id = $1 AND gate_id = 'G-04'",
                    build_id
                )
            if gate and gate['status'] == 'PASSED':
                break
            await asyncio.sleep(1)
        else:
            raise TimeoutError("G-04 not passed within timeout")
        
        # Emit G-05
        await self.write_gate(build_id, "G-05", "PASSED", {
            "awaited_gate": "G-04",
            "status": "confirmed"
        })
        
        # Log event
        await self.write_governance_event(build_id, "BACKEND_READY", {
            "gate": "G-04",
            "next_gate": "G-05"
        })
        
        return {
            "status": "COMPLETE",
            "gate_emitted": "G-05",
            "awaited_gate": "G-04"
        }
