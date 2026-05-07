"""
PO_AGENT_v2 — Product Owner Agent
Phase 5: Waits for G-14, emits G-15
"""
import sys
sys.path.insert(0, '/opt/agents')
from agents.base_agent import BaseAgent
import asyncio

class POAgentV2(BaseAgent):
    """Product Owner Agent v2 — Phase 5"""
    
    def __init__(self):
        super().__init__("PO_AGENT_v2", "postgresql://agents_user:agents_secure_pass_2026@localhost/governance_db")
    
    async def execute(self, build_id: str, context: dict):
        # Wait for G-14
        max_wait = 30
        for i in range(max_wait):
            async with self.db_pool.acquire() as conn:
                gate = await conn.fetchrow(
                    "SELECT * FROM gates WHERE build_id = $1 AND gate_id = 'G-14'",
                    build_id
                )
            if gate and gate['status'] == 'PASSED':
                break
            await asyncio.sleep(1)
        else:
            raise TimeoutError("G-14 not passed within timeout")
        
        # Emit G-15
        await self.write_gate(build_id, "G-15", "PASSED", {
            "awaited_gate": "G-14",
            "status": "confirmed"
        })
        
        # Log event
        await self.write_governance_event(build_id, "PRODUCT_VALIDATED", {
            "gate": "G-14",
            "next_gate": "G-15"
        })
        
        return {
            "status": "COMPLETE",
            "gate_emitted": "G-15",
            "awaited_gate": "G-14"
        }
