"""MCP-6: Observability MCP Server - Port 8006"""
import sys; sys.path.insert(0, '/opt/agents/mcp-servers')
import os; from pathlib import Path; from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from shared.auth import create_auth_context, AuthContext

MCP_NAME = "observability_mcp"
app = FastAPI(title="Observability MCP", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class QueryRequest(BaseModel):
    promql: str; timeout: int = 30; build_id: str

class TraceRequest(BaseModel):
    trace_id: str; build_id: str

async def get_auth(x_agent_id: str = Header(...), x_agent_token: str = Header(...), x_build_id: str = Header(...)):
    auth = create_auth_context(x_agent_id, x_agent_token, x_build_id)
    if not auth.authenticate(): raise HTTPException(401, "Auth failed")
    return auth

@app.get("/health")
def health(): return {"status": "ok", "service": "observability_mcp", "port": 8006, "timestamp": datetime.utcnow().isoformat()}

@app.post("/query_prometheus")
def query_prometheus(request: QueryRequest, auth: AuthContext = Depends(get_auth)):
    if not auth.authorize(MCP_NAME, "query"): raise HTTPException(403, "Not authorized")
    # Simulate Prometheus query
    return {"query": request.promql, "result": [], "status": "success"}

@app.post("/check_trace_exists")
def check_trace(request: TraceRequest, auth: AuthContext = Depends(get_auth)):
    if not auth.authorize(MCP_NAME, "trace"): raise HTTPException(403, "Not authorized")
    return {"trace_id": request.trace_id, "found": False}

@app.post("/fire_test_alert")
def fire_alert(build_id: str, auth: AuthContext = Depends(get_auth)):
    # Gated to Phase 5 only
    raise HTTPException(403, "Test alerts only in Phase 5")

if __name__ == "__main__":
    import uvicorn; uvicorn.run(app, host="0.0.0.0", port=8006)
