import asyncio
import sys
import time
sys.path.insert(0, '/opt/agents')
from agents.fe_agent.v2 import FEAgentV2

async def test():
    build_id = f"TEST_{int(time.time())}"
    agent = FEAgentV2()
    await agent.initialize()
    
    # Create test build and G-10
    async with agent.db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO builds (build_id, status, current_phase) VALUES ($1, 'PENDING', 4)",
            build_id
        )
        await conn.execute(
            """INSERT INTO gates (gate_id, build_id, status, passed_by, evidence, passed_at)
               VALUES ('G-10', $1, 'PASSED', 'BE_AGENT_v2', '{}'::jsonb, NOW())""",
            build_id
        )
    
    # Execute agent
    result = await agent.execute(build_id, {})
    assert result["status"] == "COMPLETE", "execute failed"
    print("✅ execute: PASS")
    
    # Verify G-11 was emitted
    async with agent.db_pool.acquire() as conn:
        gate = await conn.fetchrow("SELECT * FROM gates WHERE build_id = $1 AND gate_id = 'G-11'", build_id)
    assert gate is not None, "gate G-11 not emitted"
    print("✅ gate_emitted: PASS")
    
    # Verify awaited G-10
    assert result["awaited_gate"] == "G-10", "did not await G-10"
    print("✅ awaited_gate: PASS")
    
    # Cleanup
    async with agent.db_pool.acquire() as conn:
        await conn.execute("DELETE FROM gates WHERE build_id = $1", build_id)
        await conn.execute("DELETE FROM events WHERE build_id = $1", build_id)
        await conn.execute("DELETE FROM builds WHERE build_id = $1", build_id)
    
    await agent.cleanup()
    print("\n✅ FE_AGENT_v2 test 4/4 PASS")

if __name__ == "__main__":
    asyncio.run(test())
