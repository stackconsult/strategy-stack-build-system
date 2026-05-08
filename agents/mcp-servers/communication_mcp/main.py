"""MCP-7: Communication MCP Server - Port 8007"""
import sys; sys.path.insert(0, '/opt/agents/mcp-servers')
import os; from pathlib import Path; from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from shared.auth import create_auth_context, AuthContext

MCP_NAME = "communication_mcp"
app = FastAPI(title="Communication MCP", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class SlackRequest(BaseModel):
    channel: str; message: str; build_id: str

class PagerDutyRequest(BaseModel):
    service_key: str; description: str; severity: str = "critical"; build_id: str

async def get_auth(x_agent_id: str = Header(...), x_agent_token: str = Header(...), x_build_id: str = Header(...)):
    auth = create_auth_context(x_agent_id, x_agent_token, x_build_id)
    if not auth.authenticate(): raise HTTPException(401, "Auth failed")
    return auth

@app.get("/health")
def health(): return {"status": "ok", "service": "communication_mcp", "port": 8007, "timestamp": datetime.utcnow().isoformat()}

@app.post("/send_slack_message")
def send_slack(request: SlackRequest, auth: AuthContext = Depends(get_auth)):
    if not auth.authorize(MCP_NAME, "slack"): raise HTTPException(403, "Not authorized for Slack")
    # Log the message (in production, use slack_sdk)
    return {"channel": request.channel, "sent": True, "timestamp": datetime.utcnow().isoformat()}

@app.post("/send_pagerduty_alert")
def send_pagerduty(request: PagerDutyRequest, auth: AuthContext = Depends(get_auth)):
    # Blocked for non-MONITORING/ORCH agents
    if not (auth.agent_id.startswith("ORCHESTRATOR") or auth.agent_id.startswith("MONITORING")):
        raise HTTPException(403, "PagerDuty blocked for this agent type")
    return {"service_key": request.service_key, "triggered": True, "incident_id": f"pd-{datetime.utcnow().timestamp()}"}

@app.post("/send_email")
def send_email(to: str, subject: str, body: str, build_id: str, auth: AuthContext = Depends(get_auth)):
    if not auth.authorize(MCP_NAME, "email"): raise HTTPException(403, "Not authorized for email")
    return {"to": to, "sent": True, "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn; uvicorn.run(app, host="0.0.0.0", port=8007)
