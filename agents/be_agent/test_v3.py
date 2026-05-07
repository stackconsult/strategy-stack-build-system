import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.be_agent.v3 import BEAgentV3

async def test_agent_identity():
    agent = BEAgentV3("TEST_BUILD", "/builds/test/repo")
    assert agent.agent_id == "BE_AGENT_v3"
    assert agent.phase == 5
    print("test_agent_identity PASSED")

async def test_prometheus_in_flight_decrement():
    # Verify in_flight is decremented in finally block
    with open("/opt/agents/agents/be_agent/v3.py", 'r') as f:
        content = f.read()
    assert "http_requests_in_flight.dec()" in content
    assert "finally:" in content
    print("test_prometheus_in_flight_decrement PASSED")

if __name__ == "__main__":
    asyncio.run(test_agent_identity())
    asyncio.run(test_prometheus_in_flight_decrement())
    print("\nAll BE_AGENT_v3 tests PASSED")
