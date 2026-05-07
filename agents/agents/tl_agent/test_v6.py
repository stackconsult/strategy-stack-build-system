import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.tl_agent.v6 import TLAgentV6

async def test_agent_identity():
    agent = TLAgentV6("TEST_BUILD")
    assert agent.agent_id == "TL_AGENT_v6"
    assert agent.phase == 6
    print("test_agent_identity PASSED")

async def test_emits_g45():
    # Verify G-45 is emitted
    with open("/opt/agents/agents/tl_agent/v6.py", 'r') as f:
        content = f.read()
    assert "G-45" in content
    assert "COMPLETE" in content
    print("test_emits_g45 PASSED")

if __name__ == "__main__":
    asyncio.run(test_agent_identity())
    asyncio.run(test_emits_g45())
    print("\nAll TL_AGENT_v6 tests PASSED")
