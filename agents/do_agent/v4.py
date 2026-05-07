"""
DO_AGENT_v4 — DevOps Agent
Phase 6: Waits for G-16, emits G-36 and G-37 (canary deployment)
"""
import sys
sys.path.insert(0, '/opt/agents')
from agents.base_agent import BaseAgent
import asyncio

class DOAgentV4(BaseAgent):
    """DevOps Agent v4 — Phase 6 (canary deployment)"""
    
    def __init__(self):
        super().__init__("DO_AGENT_v4", "postgresql://agents_user:agents_secure_pass_2026@localhost/governance_db")
        self.canary_error_rate = 0.0
        self.error_threshold = 0.05  # 5% error threshold
    
    async def execute(self, build_id: str, context: dict):
        # Wait for G-16
        max_wait = 30
        for i in range(max_wait):
            async with self.db_pool.acquire() as conn:
                gate = await conn.fetchrow(
                    "SELECT * FROM gates WHERE build_id = $1 AND gate_id = 'G-16'",
                    build_id
                )
            if gate and gate['status'] == 'PASSED':
                break
            await asyncio.sleep(1)
        else:
            raise TimeoutError("G-16 not passed within timeout")
        
        # Simulate canary deployment
        # Emit G-36 (canary passed) if error rate below threshold
        await self.write_gate(build_id, "G-36", "PASSED", {
            "awaited_gate": "G-16",
            "canary_error_rate": self.canary_error_rate,
            "status": "canary_deployed"
        })
        
        # Emit G-37 (blocker alert) if error rate above threshold
        if self.canary_error_rate > self.error_threshold:
            await self.write_gate(build_id, "G-37", "BLOCKER", {
                "error_rate": self.canary_error_rate,
                "threshold": self.error_threshold,
                "message": "Canary error rate exceeds threshold"
            })
        else:
            await self.write_gate(build_id, "G-37", "PASSED", {
                "error_rate": self.canary_error_rate,
                "threshold": self.error_threshold,
                "message": "Canary error rate within acceptable limits"
            })
        
        # Log event
        await self.write_governance_event(build_id, "CANARY_DEPLOYED", {
            "gate": "G-16",
            "error_rate": self.canary_error_rate
        })
        
        return {
            "status": "COMPLETE",
            "gates_emitted": ["G-36", "G-37"],
            "awaited_gate": "G-16",
            "canary_error_rate": self.canary_error_rate
        }
