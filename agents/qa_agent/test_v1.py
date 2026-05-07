import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.qa_agent.v1 import QAAgentV1

async def test_agent_identity():
    agent = QAAgentV1("TEST_BUILD", "/builds/test/repo")
    assert agent.agent_id == "QA_AGENT_v1"
    assert agent.phase == 4
    print("test_agent_identity PASSED")

async def test_security_scan_includes_bandit():
    # Read the agent file to verify security scan includes bandit
    with open("/opt/agents/agents/qa_agent/v1.py", 'r') as f:
        content = f.read()
    assert "bandit" in content
    assert "safety" in content
    print("test_security_scan_includes_bandit PASSED")

if __name__ == "__main__":
    asyncio.run(test_agent_identity())
    asyncio.run(test_security_scan_includes_bandit())
    print("\nAll QA_AGENT_v1 tests PASSED")
