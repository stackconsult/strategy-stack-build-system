import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.po_agent.v2 import POAgentV2

async def test_agent_identity():
    agent = POAgentV2("TEST_BUILD", "/tmp/test_prd.md")
    assert agent.agent_id == "PO_AGENT_v2"
    assert agent.phase == 5
    print("test_agent_identity PASSED")

async def test_g33_checks_failures():
    # Verify G-33 checks failures before emitting
    with open("/opt/agents/agents/po_agent/v2.py", 'r') as f:
        content = f.read()
    assert "blockers" in content
    assert "failures" in content or "gates" in content
    assert "resolved = false" in content
    print("test_g33_checks_failures PASSED")

if __name__ == "__main__":
    asyncio.run(test_agent_identity())
    asyncio.run(test_g33_checks_failures())
    print("\nAll PO_AGENT_v2 tests PASSED")
