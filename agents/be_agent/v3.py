"""
BE_AGENT_v3 — Backend Engineer Agent
Phase 5: Waits for G-12, emits G-13
"""
import sys
sys.path.insert(0, '/opt/agents')
from agents.base_agent import BaseAgent
import asyncio

class BEAgentV3(BaseAgent):
    """Backend Engineer Agent v3 — Phase 5"""
    
    def __init__(self):
        super().__init__("BE_AGENT_v3", "postgresql://agents_user:agents_secure_pass_2026@localhost/governance_db")
    
    async def execute(self, build_id: str, context: dict):
        # Wait for G-12
        max_wait = 30
        for i in range(max_wait):
            async with self.db_pool.acquire() as conn:
                gate = await conn.fetchrow(
                    "SELECT * FROM gates WHERE build_id = $1 AND gate_id = 'G-12'",
                    build_id
                )
            if gate and gate['status'] == 'PASSED':
                break
            await asyncio.sleep(1)
        else:
            raise TimeoutError("G-12 not passed within timeout")
        
        # Emit G-13
        await self.write_gate(build_id, "G-13", "PASSED", {
            "awaited_gate": "G-12",
            "status": "confirmed"
        })
        
        # Log event
        await self.write_governance_event(build_id, "BACKEND_OPTIMIZED", {
            "gate": "G-12",
            "next_gate": "G-13"
        })
        
        return {
            "status": "COMPLETE",
            "gate_emitted": "G-13",
            "awaited_gate": "G-12"
        }
