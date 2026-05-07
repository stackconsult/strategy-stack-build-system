"""
QA_AGENT_v2 — QA Agent
Phase 6: Waits for G-37, emits G-45 (build complete)
"""
import sys
sys.path.insert(0, '/opt/agents')
from agents.base_agent import BaseAgent
import asyncio

class QAAgentV2(BaseAgent):
    """QA Agent v2 — Phase 6 (final validation)"""
    
    def __init__(self):
        super().__init__("QA_AGENT_v2", "postgresql://agents_user:agents_secure_pass_2026@localhost/governance_db")
    
    async def execute(self, build_id: str, context: dict):
        # Wait for G-37
        max_wait = 30
        for i in range(max_wait):
            async with self.db_pool.acquire() as conn:
                gate = await conn.fetchrow(
                    "SELECT * FROM gates WHERE build_id = $1 AND gate_id = 'G-37'",
                    build_id
                )
            if gate and gate['status'] == 'PASSED':
                break
            await asyncio.sleep(1)
        else:
            raise TimeoutError("G-37 not passed within timeout")
        
        # Emit G-45 (build complete)
        await self.write_gate(build_id, "G-45", "PASSED", {
            "awaited_gate": "G-37",
            "status": "build_complete"
        })
        
        # Update build status to COMPLETE
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                "UPDATE builds SET status = 'COMPLETE', completed_at = NOW() WHERE build_id = $1",
                build_id
            )
        
        # Log event
        await self.write_governance_event(build_id, "BUILD_COMPLETE", {
            "gate": "G-37",
            "final_gate": "G-45"
        })
        
        return {
            "status": "COMPLETE",
            "gate_emitted": "G-45",
            "awaited_gate": "G-37",
            "build_status": "COMPLETE"
        }
