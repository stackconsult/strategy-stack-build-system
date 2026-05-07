import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.be_agent.v1 import BEAgentV1, User

async def test_agent_identity():
    agent = BEAgentV1("TEST_BUILD", "/builds/test/repo", "/builds/test/api.yaml")
    assert agent.agent_id == "BE_AGENT_v1"
    assert agent.phase == 3
    print("test_agent_identity PASSED")

async def test_user_model():
    user = User(email="test@example.com", password_hash="hash123", full_name="Test User")
    assert user.email == "test@example.com"
    assert user.password_hash == "hash123"
    assert user.full_name == "Test User"
    print("test_user_model PASSED")

if __name__ == "__main__":
    asyncio.run(test_agent_identity())
    asyncio.run(test_user_model())
    print("\nAll BE_AGENT_v1 tests PASSED")
