"""
TL_AGENT_v1 — Technical Lead Agent
Phase 1: Waits for G-01, emits G-02
"""
import sys
sys.path.insert(0, '/opt/agents')
from agents.base_agent import BaseAgent
import asyncio

class TLAgentV1(BaseAgent):
    """Technical Lead Agent v1 — Phase 1"""
    
    def __init__(self):
        super().__init__("TL_AGENT_v1", "postgresql://agents_user:agents_secure_pass_2026@localhost/governance_db")
    
    async def execute(self, build_id: str, context: dict):
        # Wait for G-01
        max_wait = 30
        for i in range(max_wait):
            async with self.db_pool.acquire() as conn:
                gate = await conn.fetchrow(
                    "SELECT * FROM gates WHERE build_id = $1 AND gate_id = 'G-01'",
                    build_id
                )
            if gate and gate['status'] == 'PASSED':
                break
            await asyncio.sleep(1)
        else:
            raise TimeoutError("G-01 not passed within timeout")
        
        # Emit G-02
        await self.write_gate(build_id, "G-02", "PASSED", {
            "awaited_gate": "G-01",
            "status": "confirmed"
        })
        
        # Log event
        await self.write_governance_event(build_id, "GATE_CONFIRMED", {
            "gate": "G-01",
            "next_gate": "G-02"
        })
        
        return {
            "status": "COMPLETE",
            "gate_emitted": "G-02",
            "awaited_gate": "G-01"
        }
