import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.do_agent.v1 import DOAgentV1

async def test_agent_identity():
    agent = DOAgentV1("TEST_BUILD", "/builds/test/repo", {})
    assert agent.agent_id == "DO_AGENT_v1"
    assert agent.phase == 1
    print("test_agent_identity PASSED")

async def test_repo_path_and_tech_stack():
    agent = DOAgentV1("TEST_BUILD", "/builds/test/repo", {"backend": "FastAPI"})
    assert agent.repo_path == "/builds/test/repo"
    assert agent.tech_stack["backend"] == "FastAPI"
    print("test_repo_path_and_tech_stack PASSED")

if __name__ == "__main__":
    asyncio.run(test_agent_identity())
    asyncio.run(test_repo_path_and_tech_stack())
    print("\nAll DO_AGENT_v1 tests PASSED")
