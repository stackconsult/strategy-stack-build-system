"""
QA_AGENT_v1 — QA Agent
Phase 4: Waits for G-08, emits G-09
"""
import sys
sys.path.insert(0, '/opt/agents')
from agents.base_agent import BaseAgent
import asyncio

class QAAgentV1(BaseAgent):
    """QA Agent v1 — Phase 4"""
    
    def __init__(self):
        super().__init__("QA_AGENT_v1", "postgresql://agents_user:agents_secure_pass_2026@localhost/governance_db")
    
    async def execute(self, build_id: str, context: dict):
        # Wait for G-08
        max_wait = 30
        for i in range(max_wait):
            async with self.db_pool.acquire() as conn:
                gate = await conn.fetchrow(
                    "SELECT * FROM gates WHERE build_id = $1 AND gate_id = 'G-08'",
                    build_id
                )
            if gate and gate['status'] == 'PASSED':
                break
            await asyncio.sleep(1)
        else:
            raise TimeoutError("G-08 not passed within timeout")
        
        # Emit G-09
        await self.write_gate(build_id, "G-09", "PASSED", {
            "awaited_gate": "G-08",
            "status": "confirmed"
        })
        
        # Log event
        await self.write_governance_event(build_id, "QA_READY", {
            "gate": "G-08",
            "next_gate": "G-09"
        })
        
        return {
            "status": "COMPLETE",
            "gate_emitted": "G-09",
            "awaited_gate": "G-08"
        }
