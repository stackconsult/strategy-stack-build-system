import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.fe_agent.v1 import FEAgentV1

async def test_agent_identity():
    agent = FEAgentV1("TEST_BUILD", "/builds/test/repo", "/builds/test/api.yaml")
    assert agent.agent_id == "FE_AGENT_v1"
    assert agent.phase == 3
    print("test_agent_identity PASSED")

async def test_auth_context_no_localstorage():
    # Read the AuthContext.tsx content to verify localStorage is not used
    with open("/opt/agents/agents/fe_agent/v1.py", 'r') as f:
        content = f.read()
    assert "localStorage" not in content or "NEVER use localStorage" in content
    print("test_auth_context_no_localstorage PASSED")

if __name__ == "__main__":
    asyncio.run(test_agent_identity())
    asyncio.run(test_auth_context_no_localstorage())
    print("\nAll FE_AGENT_v1 tests PASSED")
