import asyncio
import sys
import time
from pathlib import Path
sys.path.insert(0, '/opt/agents')
from agents.po_agent.v1 import POAgentV1

async def test():
    build_id = f"TEST_{int(time.time())}"
    agent = POAgentV1()
    await agent.initialize()
    
    # Create test build
    async with agent.db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO builds (build_id, status, current_phase) VALUES ($1, 'PENDING', 1)",
            build_id
        )
    
    # Create test PRD
    prd_path = Path("/tmp/test_prd.md")
    prd_path.write_text("# Test PRD\n\nThis is a test product requirement document.")
    
    # Execute agent
    result = await agent.execute(build_id, {"prd_path": str(prd_path)})
    assert result["status"] == "COMPLETE", "execute failed"
    print("✅ execute: PASS")
    
    # Verify spec was created
    spec_path = Path("/tmp/test_prd_SPEC.md")
    assert spec_path.exists(), "spec not created"
    print("✅ spec_created: PASS")
    
    # Verify gate was emitted
    async with agent.db_pool.acquire() as conn:
        gate = await conn.fetchrow("SELECT * FROM gates WHERE build_id = $1 AND gate_id = 'G-01'", build_id)
    assert gate is not None, "gate G-01 not emitted"
    print("✅ gate_emitted: PASS")
    
    # Cleanup
    prd_path.unlink()
    spec_path.unlink()
    async with agent.db_pool.acquire() as conn:
        await conn.execute("DELETE FROM gates WHERE build_id = $1", build_id)
        await conn.execute("DELETE FROM events WHERE build_id = $1", build_id)
        await conn.execute("DELETE FROM builds WHERE build_id = $1", build_id)
    
    await agent.cleanup()
    print("\n✅ PO_AGENT_v1 test 4/4 PASS")

if __name__ == "__main__":
    asyncio.run(test())
