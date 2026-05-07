import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.do_agent.v2 import DOAgentV2

async def test_agent_identity():
    agent = DOAgentV2("TEST_BUILD", "/builds/test/repo", {"project_name": "Test"})
    assert agent.agent_id == "DO_AGENT_v2"
    assert agent.phase == 3
    print("test_agent_identity PASSED")

async def test_terraform_content():
    agent = DOAgentV2("TEST_BUILD", "/builds/test/repo", {"project_name": "Test"})
    assert agent.structured_spec["project_name"] == "Test"
    assert agent.repo_path == "/builds/test/repo"
    print("test_terraform_content PASSED")

if __name__ == "__main__":
    asyncio.run(test_agent_identity())
    asyncio.run(test_terraform_content())
    print("\nAll DO_AGENT_v2 tests PASSED")
