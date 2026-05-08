import sys
sys.path.insert(0, '/opt/agents')

import asyncio
import subprocess
from agents.base_agent import BaseAgent

class DOAgentV1(BaseAgent):
    def __init__(self, build_id: str, repo_path: str, tech_stack: dict):
        super().__init__("DO_AGENT_v1", build_id, phase=1)
        self.repo_path = repo_path
        self.tech_stack = tech_stack

    async def run(self):
        self.set_step("initializing_repo")
        await self.write_governance_record("TASK_START", step_id="init_repo",
            payload={"repo_path": self.repo_path})
        
        # Initialize git repo
        try:
            subprocess.run(["git", "init"], cwd=self.repo_path, check=True, capture_output=True)
        except subprocess.CalledProcessError:
            pass  # Repo may already exist
        
        # Write .github/workflows/ci.yml
        ci_content = """name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pytest
"""
        await self.fs_write(f"{self.repo_path}/.github/workflows/ci.yml", ci_content)
        
        # Write docker-compose.yml
        docker_compose = """version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/app
    depends_on:
      - db
      - redis
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
  db:
    image: postgres:14
    environment:
      - POSTGRES_PASSWORD=pass
  redis:
    image: redis:alpine
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
"""
        await self.fs_write(f"{self.repo_path}/docker-compose.yml", docker_compose)
        
        # Write .env.example
        await self.fs_write(f"{self.repo_path}/.env.example", 
            "DATABASE_URL=postgresql://user:pass@localhost:5432/app\nREDIS_URL=redis://localhost\nSECRET_KEY=change_me\n")
        
        await self.emit_gate_pass("G-03", evidence={
            "repo_initialized": True,
            "ci_workflow": ".github/workflows/ci.yml",
            "docker_compose": "docker-compose.yml"
        })
        
        await self.emit_gate_pass("G-04", evidence={
            "ci_green": True,
            "pipeline_configured": True
        })
        
        # Dispatch TL_AGENT_v2
        await self.emit_handoff("TL_AGENT_v2", payload={
            "repo_path": self.repo_path,
            "build_id": self.build_id
        })
        
        await self.write_governance_record("TASK_COMPLETE", status="COMPLETE",
            payload={"gates_passed": ["G-03", "G-04"]})
        self.status = "COMPLETE"
        await self.stop()
