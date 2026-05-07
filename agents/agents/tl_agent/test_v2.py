import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.tl_agent.v2 import TLAgentV2

async def test_agent_identity():
    agent = TLAgentV2("TEST_BUILD", {"project_name": "Test"}, "/builds/test/repo")
    assert agent.agent_id == "TL_AGENT_v2"
    assert agent.phase == 2
    print("test_agent_identity PASSED")

async def test_api_spec_generation():
    agent = TLAgentV2("TEST_BUILD", {"project_name": "TestAPI"}, "/builds/test/repo")
    assert agent.structured_spec["project_name"] == "TestAPI"
    assert agent.repo_path == "/builds/test/repo"
    print("test_api_spec_generation PASSED")

if __name__ == "__main__":
    asyncio.run(test_agent_identity())
    asyncio.run(test_api_spec_generation())
    print("\nAll TL_AGENT_v2 tests PASSED")
