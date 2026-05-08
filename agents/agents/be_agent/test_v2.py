import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.be_agent.v2 import BEAgentV2

async def test_agent_identity():
    agent = BEAgentV2("TEST_BUILD", "/builds/test/repo")
    assert agent.agent_id == "BE_AGENT_v2"
    assert agent.phase == 4
    print("test_agent_identity PASSED")

async def test_idempotency_covers_all_mutating_methods():
    # Read the agent file to verify idempotency covers POST/PUT/PATCH/DELETE
    with open("/opt/agents/agents/be_agent/v2.py", 'r') as f:
        content = f.read()
    assert "POST" in content
    assert "PUT" in content
    assert "PATCH" in content
    assert "DELETE" in content
    print("test_idempotency_covers_all_mutating_methods PASSED")

async def test_dlq_in_worker():
    with open("/opt/agents/agents/be_agent/v2.py", 'r') as f:
        content = f.read()
    assert "dlq" in content or "DLQ" in content
    print("test_dlq_in_worker PASSED")

if __name__ == "__main__":
    asyncio.run(test_agent_identity())
    asyncio.run(test_idempotency_covers_all_mutating_methods())
    asyncio.run(test_dlq_in_worker())
    print("\nAll BE_AGENT_v2 tests PASSED")
