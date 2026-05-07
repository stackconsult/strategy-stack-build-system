import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.base_agent import BaseAgent

class QAAgentV1(BaseAgent):
    def __init__(self, build_id: str, repo_path: str):
        super().__init__("QA_AGENT_v1", build_id, phase=4)
        self.repo_path = repo_path

    async def run(self):
        self.set_step("writing_e2e_tests")
        await self.write_governance_record("TASK_START", step_id="write_e2e_tests")
        
        # Write E2E test suite
        e2e_tests = '''import pytest
import httpx

BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    response = httpx.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_user_registration():
    response = httpx.post(f"{BASE_URL}/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "TestPass123!",
        "full_name": "Test User"
    })
    assert response.status_code == 201

def test_user_login_success():
    httpx.post(f"{BASE_URL}/api/v1/auth/register", json={
        "email": "login@example.com",
        "password": "TestPass123!",
        "full_name": "Login User"
    })
    response = httpx.post(f"{BASE_URL}/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "TestPass123!"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_user_login_invalid_credentials():
    response = httpx.post(f"{BASE_URL}/api/v1/auth/login", json={
        "email": "wrong@example.com",
        "password": "WrongPass"
    })
    assert response.status_code == 401

def test_protected_route_requires_auth():
    response = httpx.get(f"{BASE_URL}/api/v1/users/me")
    assert response.status_code == 401

def test_token_refresh():
    # Register and login
    httpx.post(f"{BASE_URL}/api/v1/auth/register", json={
        "email": "refresh@example.com",
        "password": "TestPass123!",
        "full_name": "Refresh User"
    })
    login_resp = httpx.post(f"{BASE_URL}/api/v1/auth/login", json={
        "email": "refresh@example.com",
        "password": "TestPass123!"
    })
    token = login_resp.json()["access_token"]
    
    refresh_resp = httpx.post(f"{BASE_URL}/api/v1/auth/refresh", json={"token": token})
    assert refresh_resp.status_code == 200
    assert "access_token" in refresh_resp.json()

def test_user_profile_update():
    # Register and login
    httpx.post(f"{BASE_URL}/api/v1/auth/register", json={
        "email": "update@example.com",
        "password": "TestPass123!",
        "full_name": "Update User"
    })
    login_resp = httpx.post(f"{BASE_URL}/api/v1/auth/login", json={
        "email": "update@example.com",
        "password": "TestPass123!"
    })
    token = login_resp.json()["access_token"]
    
    update_resp = httpx.patch(f"{BASE_URL}/api/v1/users/me", 
        json={"full_name": "Updated Name"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert update_resp.status_code == 200

def test_error_handling_404():
    response = httpx.get(f"{BASE_URL}/api/v1/nonexistent")
    assert response.status_code == 404

def test_input_validation_missing_fields():
    response = httpx.post(f"{BASE_URL}/api/v1/auth/register", json={
        "email": "test@example.com"
        # Missing password and full_name
    })
    assert response.status_code == 422
'''
        await self.fs_write(f"{self.repo_path}/backend/tests/test_e2e.py", e2e_tests)
        
        # Write contract tests
        contract_tests = '''import pytest
import httpx

BASE_URL = "http://localhost:8000"

def test_api_contract_login():
    response = httpx.post(f"{BASE_URL}/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    schema = response.json()
    assert "access_token" in schema
    assert "token_type" in schema
    assert schema["token_type"] == "bearer"

def test_api_contract_register():
    response = httpx.post(f"{BASE_URL}/api/v1/auth/register", json={
        "email": "contract@example.com",
        "password": "TestPass123!",
        "full_name": "Contract User"
    })
    schema = response.json()
    assert "user_id" in schema
    assert "email" in schema

def test_api_contract_user_profile():
    response = httpx.get(f"{BASE_URL}/api/v1/users/me")
    # Should fail without auth, but contract check
    assert response.status_code in [401, 422]
'''
        await self.fs_write(f"{self.repo_path}/backend/tests/test_contract.py", contract_tests)
        
        await self.emit_gate_pass("G-19", evidence={"e2e_tests": "9 tests written"})
        await self.emit_gate_pass("G-20", evidence={"contract_tests": "3 tests written"})
        
        self.set_step("writing_security_scan")
        
        # Write security scan script
        security_scan = '''#!/bin/bash
# Security scan using bandit and safety

echo "Running security scan..."

# Bandit scan for Python security issues
bandit -r backend/

# Safety check for known vulnerable dependencies
safety check backend/requirements.txt

echo "Security scan complete"
'''
        await self.fs_write(f"{self.repo_path}/infra/security-scan.sh", security_scan)
        
        await self.emit_gate_pass("G-24", evidence={"security_scan": "security-scan.sh written"})
        
        # Dispatch TL_AGENT_v4
        await self.emit_handoff("TL_AGENT_v4", payload={"build_id": self.build_id})
        
        await self.write_governance_record("TASK_COMPLETE", status="COMPLETE",
            payload={"gates_passed": ["G-19", "G-20", "G-24"]})
        self.status = "COMPLETE"
        await self.stop()
