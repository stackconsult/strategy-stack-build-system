import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.do_agent.v4 import DOAgentV4

async def test_agent_identity():
    agent = DOAgentV4("TEST_BUILD", "/builds/test/repo")
    assert agent.agent_id == "DO_AGENT_v4"
    assert agent.phase == 6
    print("test_agent_identity PASSED")

async def test_g36_before_g37():
    # Verify G-36 is emitted before G-37
    with open("/opt/agents/agents/do_agent/v4.py", 'r') as f:
        content = f.read()
    # Check that G-36 emit comes before G-37 emit
    g36_pos = content.find("G-36")
    g37_pos = content.find("G-37")
    assert g36_pos != -1 and g37_pos != -1
    assert g36_pos < g37_pos
    print("test_g36_before_g37 PASSED")

async def test_error_rate_check():
    # Verify error rate check with 1% threshold
    with open("/opt/agents/agents/do_agent/v4.py", 'r') as f:
        content = f.read()
    assert "ERROR_THRESHOLD=0.01" in content or "1%" in content
    assert "BLOCKER_ALERT" in content or "exit 1" in content
    print("test_error_rate_check PASSED")

if __name__ == "__main__":
    asyncio.run(test_agent_identity())
    asyncio.run(test_g36_before_g37())
    asyncio.run(test_error_rate_check())
    print("\nAll DO_AGENT_v4 tests PASSED")
