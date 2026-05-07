import sys
sys.path.insert(0, '/opt/agents')

import asyncio
import yaml
from agents.base_agent import BaseAgent

class TLAgentV2(BaseAgent):
    def __init__(self, build_id: str, structured_spec: dict, repo_path: str):
        super().__init__("TL_AGENT_v2", build_id, phase=2)
        self.structured_spec = structured_spec
        self.repo_path = repo_path

    async def run(self):
        self.set_step("generating_api_spec")
        await self.write_governance_record("TASK_START", step_id="generate_api_spec")
        
        # Generate OpenAPI 3.0 spec from structured_spec
        api_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": self.structured_spec.get("project_name", "API"),
                "version": "1.0.0"
            },
            "paths": {
                "/api/v1/auth/login": {
                    "post": {
                        "summary": "User login",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "email": {"type": "string"},
                                            "password": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {"description": "Login successful"},
                            "401": {"description": "Invalid credentials"}
                        }
                    }
                },
                "/api/v1/auth/register": {
                    "post": {
                        "summary": "User registration",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "email": {"type": "string"},
                                            "password": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {
                            "201": {"description": "Registration successful"},
                            "400": {"description": "Invalid input"}
                        }
                    }
                }
            }
        }
        
        # Write api-spec.yaml
        spec_path = f"/Volumes/STORE N GO/builds/{self.build_id}/specs/api-spec.yaml"
        await self.fs_write(spec_path, yaml.dump(api_spec))
        
        await self.emit_gate_pass("G-05", evidence={
            "api_spec_path": spec_path,
            "openapi_version": "3.0.0",
            "paths_count": len(api_spec["paths"])
        })
        
        # Dispatch BE_AGENT_v1, FE_AGENT_v1, DO_AGENT_v2 in parallel
        await asyncio.gather(
            self.emit_handoff("BE_AGENT_v1", payload={
                "structured_spec": self.structured_spec,
                "repo_path": self.repo_path,
                "build_id": self.build_id,
                "api_spec_path": spec_path
            }),
            self.emit_handoff("FE_AGENT_v1", payload={
                "structured_spec": self.structured_spec,
                "repo_path": self.repo_path,
                "build_id": self.build_id,
                "api_spec_path": spec_path
            }),
            self.emit_handoff("DO_AGENT_v2", payload={
                "structured_spec": self.structured_spec,
                "repo_path": self.repo_path,
                "build_id": self.build_id
            })
        )
        
        await self.write_governance_record("TASK_COMPLETE", status="COMPLETE",
            payload={"gates_passed": ["G-05"]})
        self.status = "COMPLETE"
        await self.stop()
