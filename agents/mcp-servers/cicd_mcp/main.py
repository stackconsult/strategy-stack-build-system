"""MCP-3: CICD MCP Server - Port 8003"""
import sys; sys.path.insert(0, '/opt/agents/mcp-servers')
import os; from pathlib import Path; from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from shared.auth import create_auth_context, AuthContext
import httpx, asyncio

MCP_NAME, VAULT_ROOT = "cicd_mcp", Path(os.getenv("VAULT_PATH", "/opt/agents"))
app = FastAPI(title="CICD MCP", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class TriggerRequest(BaseModel):
    repo_path: str; workflow: str; branch: str = "main"; build_id: str

class MonitorRequest(BaseModel):
    run_id: str; timeout: int = 300

async def get_auth(x_agent_id: str = Header(...), x_agent_token: str = Header(...), x_build_id: str = Header(...)):
    auth = create_auth_context(x_agent_id, x_agent_token, x_build_id)
    if not auth.authenticate(): raise HTTPException(401, "Auth failed")
    return auth

@app.get("/health")
def health(): return {"status": "ok", "service": "cicd_mcp", "port": 8003, "timestamp": datetime.utcnow().isoformat()}

@app.post("/trigger_workflow")
def trigger(request: TriggerRequest, auth: AuthContext = Depends(get_auth)):
    if not auth.authorize(MCP_NAME, "trigger"): raise HTTPException(403, "Not authorized")
    # Simulate GitHub Actions trigger
    run_id = f"gha-{request.build_id}-{datetime.utcnow().timestamp()}"
    return {"status": "triggered", "run_id": run_id, "workflow": request.workflow}

@app.post("/monitor_workflow")
async def monitor(request: MonitorRequest, auth: AuthContext = Depends(get_auth)):
    if not auth.authorize(MCP_NAME, "monitor"): raise HTTPException(403, "Not authorized")
    # Simulate monitoring
    return {"run_id": request.run_id, "status": "completed", "conclusion": "success"}

if __name__ == "__main__":
    import uvicorn; uvicorn.run(app, host="0.0.0.0", port=8003)
