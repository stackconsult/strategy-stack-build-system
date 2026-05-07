import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.tl_agent.v1 import TLAgentV1

async def test_agent_identity():
    agent = TLAgentV1("TEST_BUILD", {"project_name": "Test"}, "/builds/test/repo")
    assert agent.agent_id == "TL_AGENT_v1"
    assert agent.phase == 1
    print("test_agent_identity PASSED")

async def test_dispatches_do_agent():
    agent = TLAgentV1("TEST_BUILD", {"project_name": "Test"}, "/builds/test/repo")
    # Test that agent has the structured_spec and repo_path
    assert agent.structured_spec["project_name"] == "Test"
    assert agent.repo_path == "/builds/test/repo"
    print("test_dispatches_do_agent PASSED")

if __name__ == "__main__":
    asyncio.run(test_agent_identity())
    asyncio.run(test_dispatches_do_agent())
    print("\nAll TL_AGENT_v1 tests PASSED")
