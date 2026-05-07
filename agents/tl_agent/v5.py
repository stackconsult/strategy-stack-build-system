"""
TL_AGENT_v5 — Technical Lead Agent
Phase 5: Waits for G-15, emits G-16
"""
import sys
sys.path.insert(0, '/opt/agents')
from agents.base_agent import BaseAgent
import asyncio

class TLAgentV5(BaseAgent):
    """Technical Lead Agent v5 — Phase 5"""
    
    def __init__(self):
        super().__init__("TL_AGENT_v5", "postgresql://agents_user:agents_secure_pass_2026@localhost/governance_db")
    
    async def execute(self, build_id: str, context: dict):
        # Wait for G-15
        max_wait = 30
        for i in range(max_wait):
            async with self.db_pool.acquire() as conn:
                gate = await conn.fetchrow(
                    "SELECT * FROM gates WHERE build_id = $1 AND gate_id = 'G-15'",
                    build_id
                )
            if gate and gate['status'] == 'PASSED':
                break
            await asyncio.sleep(1)
        else:
            raise TimeoutError("G-15 not passed within timeout")
        
        # Emit G-16
        await self.write_gate(build_id, "G-16", "PASSED", {
            "awaited_gate": "G-15",
            "status": "confirmed"
        })
        
        # Log event
        await self.write_governance_event(build_id, "PHASE_5_COMPLETE", {
            "gate": "G-15",
            "next_gate": "G-16"
        })
        
        return {
            "status": "COMPLETE",
            "gate_emitted": "G-16",
            "awaited_gate": "G-15"
        }
