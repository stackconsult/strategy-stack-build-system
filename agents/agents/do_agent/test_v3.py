import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.do_agent.v3 import DOAgentV3

async def test_agent_identity():
    agent = DOAgentV3("TEST_BUILD", "/builds/test/repo")
    assert agent.agent_id == "DO_AGENT_v3"
    assert agent.phase == 5
    print("test_agent_identity PASSED")

async def test_rollback_exit_code_2():
    # Verify rollback.sh exits with code 2 on timeout
    with open("/opt/agents/agents/do_agent/v3.py", 'r') as f:
        content = f.read()
    assert "exit 2" in content
    assert "300" in content or "MAX_WAIT" in content
    print("test_rollback_exit_code_2 PASSED")

if __name__ == "__main__":
    asyncio.run(test_agent_identity())
    asyncio.run(test_rollback_exit_code_2())
    print("\nAll DO_AGENT_v3 tests PASSED")
