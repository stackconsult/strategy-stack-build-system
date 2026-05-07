import asyncio
import sys
import time
sys.path.insert(0, '/opt/agents')
from agents.do_agent.v1 import DOAgentV1

async def test():
    build_id = f"TEST_{int(time.time())}"
    agent = DOAgentV1()
    await agent.initialize()
    
    # Create test build and G-02
    async with agent.db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO builds (build_id, status, current_phase) VALUES ($1, 'PENDING', 1)",
            build_id
        )
        await conn.execute(
            """INSERT INTO gates (gate_id, build_id, status, passed_by, evidence, passed_at)
               VALUES ('G-02', $1, 'PASSED', 'TL_AGENT_v1', '{}'::jsonb, NOW())""",
            build_id
        )
    
    # Execute agent
    result = await agent.execute(build_id, {})
    assert result["status"] == "COMPLETE", "execute failed"
    print("✅ execute: PASS")
    
    # Verify G-03 was emitted
    async with agent.db_pool.acquire() as conn:
        gate = await conn.fetchrow("SELECT * FROM gates WHERE build_id = $1 AND gate_id = 'G-03'", build_id)
    assert gate is not None, "gate G-03 not emitted"
    print("✅ gate_emitted: PASS")
    
    # Verify awaited G-02
    assert result["awaited_gate"] == "G-02", "did not await G-02"
    print("✅ awaited_gate: PASS")
    
    # Cleanup
    async with agent.db_pool.acquire() as conn:
        await conn.execute("DELETE FROM gates WHERE build_id = $1", build_id)
        await conn.execute("DELETE FROM events WHERE build_id = $1", build_id)
        await conn.execute("DELETE FROM builds WHERE build_id = $1", build_id)
    
    await agent.cleanup()
    print("\n✅ DO_AGENT_v1 test 4/4 PASS")

if __name__ == "__main__":
    asyncio.run(test())
