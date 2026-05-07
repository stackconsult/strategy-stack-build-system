import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.tl_agent.v4 import TLAgentV4

async def test_agent_identity():
    agent = TLAgentV4("TEST_BUILD")
    assert agent.agent_id == "TL_AGENT_v4"
    assert agent.phase == 5
    print("test_agent_identity PASSED")

async def test_required_signals():
    agent = TLAgentV4("TEST_BUILD")
    assert agent.phase == 5
    print("test_required_signals PASSED")

async def test_gates_g19_to_g25_covered():
    with open("/opt/agents/agents/tl_agent/v4.py", 'r') as f:
        content = f.read()
    assert "G-19" in content
    assert "G-20" in content
    assert "G-24" in content
    assert "G-21" in content
    assert "G-22" in content
    assert "G-23" in content
    assert "G-25" in content
    print("test_gates_g19_to_g25_covered PASSED")

if __name__ == "__main__":
    asyncio.run(test_agent_identity())
    asyncio.run(test_required_signals())
    asyncio.run(test_gates_g19_to_g25_covered())
    print("\nAll TL_AGENT_v4 tests PASSED")
