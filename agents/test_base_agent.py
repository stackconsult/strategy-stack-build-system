import asyncio
import sys
import time
sys.path.insert(0, '/opt/agents')
from agents.base_agent import BaseAgent

class TestAgent(BaseAgent):
    async def execute(self, build_id: str, context: dict):
        return {"status": "ok", "build_id": build_id}

async def test():
    build_id = f"TEST_{int(time.time())}"
    agent = TestAgent("TEST_AGENT", "postgresql://agents_user:agents_secure_pass_2026@localhost/governance_db")
    await agent.initialize()
    
    # Create test build first
    async with agent.db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO builds (build_id, status, current_phase) VALUES ($1, 'PENDING', 1)",
            build_id
        )
    
    # Test execute
    result = await agent.execute(build_id, {})
    assert result["status"] == "ok", "execute failed"
    print("✅ execute: PASS")
    
    # Test governance event
    await agent.write_governance_event(build_id, "TEST_EVENT", {"test": True})
    print("✅ write_governance_event: PASS")
    
    # Test gate
    await agent.write_gate(build_id, "G-TEST", "PASSED", {"test": True})
    print("✅ write_gate: PASS")
    
    # Test message
    await agent.send_message(build_id, "OTHER_AGENT", "TEST_MSG", {"test": True})
    print("✅ send_message: PASS")
    
    # Test heartbeat
    await agent.write_heartbeat(build_id, "RUNNING")
    print("✅ write_heartbeat: PASS")
    
    # Cleanup test data
    async with agent.db_pool.acquire() as conn:
        await conn.execute("DELETE FROM events WHERE build_id = $1", build_id)
        await conn.execute("DELETE FROM gates WHERE build_id = $1", build_id)
        await conn.execute("DELETE FROM messages WHERE build_id = $1", build_id)
        await conn.execute("DELETE FROM agent_heartbeats WHERE build_id = $1", build_id)
        await conn.execute("DELETE FROM builds WHERE build_id = $1", build_id)
    
    await agent.cleanup()
    print("\n✅ All 5 base_agent methods PASS")

if __name__ == "__main__":
    asyncio.run(test())
