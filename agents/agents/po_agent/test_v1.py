import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.po_agent.v1 import POAgentV1

async def test_agent_identity():
    agent = POAgentV1("TEST_BUILD", "/tmp/test_prd.md")
    assert agent.agent_id == "PO_AGENT_v1"
    assert agent.phase == 1
    print("test_agent_identity PASSED")

async def test_prd_parsing():
    agent = POAgentV1("TEST_BUILD", "/tmp/test_prd.md")
    prd_content = """# Project Name
TestProject

# Objective
Build a test system

# User Stories
- As a user I can login

# Acceptance Criteria
- Login form validates email
"""
    spec = agent._parse_prd(prd_content)
    assert spec["project_name"] == "TestProject"
    assert spec["objective"] == "Build a test system"
    assert len(spec["user_stories"]) == 1
    assert len(spec["acceptance_criteria"]) == 1
    print("test_prd_parsing PASSED")

async def test_spec_validation():
    agent = POAgentV1("TEST_BUILD", "/tmp/test_prd.md")
    agent.structured_spec = {"project_name": "Test", "objective": "Test", "user_stories": [], "acceptance_criteria": []}
    assert agent._validate_spec() == True
    
    agent.structured_spec = {"project_name": "", "objective": "Test", "user_stories": [], "acceptance_criteria": []}
    assert agent._validate_spec() == False
    print("test_spec_validation PASSED")

if __name__ == "__main__":
    asyncio.run(test_agent_identity())
    asyncio.run(test_prd_parsing())
    asyncio.run(test_spec_validation())
    print("\nAll PO_AGENT_v1 tests PASSED")
