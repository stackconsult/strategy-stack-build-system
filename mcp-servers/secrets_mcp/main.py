"""MCP-4: Secrets MCP Server - Port 8004"""
import sys; sys.path.insert(0, '/opt/agents/mcp-servers')
import os; from pathlib import Path; from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from shared.auth import create_auth_context, AuthContext

MCP_NAME, VAULT_ROOT = "secrets_mcp", Path(os.getenv("VAULT_PATH", "/opt/agents"))
app = FastAPI(title="Secrets MCP", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# In-memory secrets store (use Infisical in production)
_secrets_store = {}

class GetSecretRequest(BaseModel):
    key: str; build_id: str

class SetSecretRequest(BaseModel):
    key: str; value: str; build_id: str

async def get_auth(x_agent_id: str = Header(...), x_agent_token: str = Header(...), x_build_id: str = Header(...)):
    auth = create_auth_context(x_agent_id, x_agent_token, x_build_id)
    if not auth.authenticate(): raise HTTPException(401, "Auth failed")
    return auth

@app.get("/health")
def health(): return {"status": "ok", "service": "secrets_mcp", "port": 8004, "timestamp": datetime.utcnow().isoformat()}

@app.post("/get_secret")
def get_secret(request: GetSecretRequest, auth: AuthContext = Depends(get_auth)):
    if not auth.authorize(MCP_NAME, "get"): raise HTTPException(403, "Not authorized")
    value = _secrets_store.get(request.key)
    if value is None: raise HTTPException(404, f"Secret {request.key} not found")
    return {"key": request.key, "found": True}  # Never return actual value in response

@app.post("/set_secret")
def set_secret(request: SetSecretRequest, auth: AuthContext = Depends(get_auth)):
    # Only ORCHESTRATOR can set secrets
    if auth.agent_id != "ORCHESTRATOR_AGENT": raise HTTPException(403, "Only ORCHESTRATOR can set secrets")
    _secrets_store[request.key] = request.value
    return {"key": request.key, "set": True}

@app.post("/list_secret_names")
def list_secrets(build_id: str, auth: AuthContext = Depends(get_auth)):
    if not auth.authorize(MCP_NAME, "list"): raise HTTPException(403, "Not authorized")
    return {"keys": list(_secrets_store.keys())}

if __name__ == "__main__":
    import uvicorn; uvicorn.run(app, host="0.0.0.0", port=8004)
