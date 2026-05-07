import asyncio
import sys
import time
sys.path.insert(0, '/opt/agents')
from agents.do_agent.v4 import DOAgentV4

async def test():
    build_id = f"TEST_{int(time.time())}"
    agent = DOAgentV4()
    await agent.initialize()
    
    # Create test build and G-16
    async with agent.db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO builds (build_id, status, current_phase) VALUES ($1, 'PENDING', 6)",
            build_id
        )
        await conn.execute(
            """INSERT INTO gates (gate_id, build_id, status, passed_by, evidence, passed_at)
               VALUES ('G-16', $1, 'PASSED', 'TL_AGENT_v5', '{}'::jsonb, NOW())""",
            build_id
        )
    
    # Execute agent
    result = await agent.execute(build_id, {})
    assert result["status"] == "COMPLETE", "execute failed"
    print("✅ execute: PASS")
    
    # Verify G-36 was emitted
    async with agent.db_pool.acquire() as conn:
        gate = await conn.fetchrow("SELECT * FROM gates WHERE build_id = $1 AND gate_id = 'G-36'", build_id)
    assert gate is not None, "gate G-36 not emitted"
    print("✅ gate_G-36: PASS")
    
    # Verify G-37 was emitted
    async with agent.db_pool.acquire() as conn:
        gate = await conn.fetchrow("SELECT * FROM gates WHERE build_id = $1 AND gate_id = 'G-37'", build_id)
    assert gate is not None, "gate G-37 not emitted"
    print("✅ gate_G-37: PASS")
    
    # Cleanup
    async with agent.db_pool.acquire() as conn:
        await conn.execute("DELETE FROM gates WHERE build_id = $1", build_id)
        await conn.execute("DELETE FROM events WHERE build_id = $1", build_id)
        await conn.execute("DELETE FROM builds WHERE build_id = $1", build_id)
    
    await agent.cleanup()
    print("\n✅ DO_AGENT_v4 test 4/4 PASS")

if __name__ == "__main__":
    asyncio.run(test())
