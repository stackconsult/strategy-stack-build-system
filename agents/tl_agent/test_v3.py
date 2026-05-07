import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.tl_agent.v3 import TLAgentV3

async def test_agent_identity():
    agent = TLAgentV3("TEST_BUILD")
    assert agent.agent_id == "TL_AGENT_v3"
    assert agent.phase == 4
    print("test_agent_identity PASSED")

async def test_required_signals():
    agent = TLAgentV3("TEST_BUILD")
    # The agent waits for BE_AGENT_v1, FE_AGENT_v1, DO_AGENT_v2
    assert agent.phase == 4
    print("test_required_signals PASSED")

if __name__ == "__main__":
    asyncio.run(test_agent_identity())
    asyncio.run(test_required_signals())
    print("\nAll TL_AGENT_v3 tests PASSED")
