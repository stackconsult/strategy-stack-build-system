import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.fe_agent.v2 import FEAgentV2

async def test_agent_identity():
    agent = FEAgentV2("TEST_BUILD", "/builds/test/repo")
    assert agent.agent_id == "FE_AGENT_v2"
    assert agent.phase == 4
    print("test_agent_identity PASSED")

async def test_aria_attributes_present():
    # Read the agent file to verify ARIA attributes are present
    with open("/opt/agents/agents/fe_agent/v2.py", 'r') as f:
        content = f.read()
    assert "aria-invalid" in content
    assert "aria-label" in content
    assert 'role="alert"' in content
    print("test_aria_attributes_present PASSED")

if __name__ == "__main__":
    asyncio.run(test_agent_identity())
    asyncio.run(test_aria_attributes_present())
    print("\nAll FE_AGENT_v2 tests PASSED")
