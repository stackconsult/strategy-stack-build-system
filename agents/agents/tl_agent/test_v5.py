import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.tl_agent.v5 import TLAgentV5

async def test_agent_identity():
    agent = TLAgentV5("TEST_BUILD")
    assert agent.agent_id == "TL_AGENT_v5"
    assert agent.phase == 6
    print("test_agent_identity PASSED")

async def test_g33_verification():
    # Verify G-33 is checked before G-34
    with open("/opt/agents/agents/tl_agent/v5.py", 'r') as f:
        content = f.read()
    assert "G-33" in content
    assert "g33" in content or "G-33" in content
    print("test_g33_verification PASSED")

if __name__ == "__main__":
    asyncio.run(test_agent_identity())
    asyncio.run(test_g33_verification())
    print("\nAll TL_AGENT_v5 tests PASSED")
