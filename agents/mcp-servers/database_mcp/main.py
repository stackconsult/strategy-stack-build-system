"""MCP-5: Database MCP Server - Port 8005"""
import sys; sys.path.insert(0, '/opt/agents/mcp-servers')
import os; from pathlib import Path; from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from shared.auth import create_auth_context, AuthContext
import asyncpg, asyncio

MCP_NAME = "database_mcp"
DB_URL = "postgresql://agents_user:agents_secure_pass_2026@localhost/governance_db"

app = FastAPI(title="Database MCP", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class QueryRequest(BaseModel):
    sql: str; params: list = []; build_id: str

async def get_auth(x_agent_id: str = Header(...), x_agent_token: str = Header(...), x_build_id: str = Header(...)):
    auth = create_auth_context(x_agent_id, x_agent_token, x_build_id)
    if not auth.authenticate(): raise HTTPException(401, "Auth failed")
    return auth

@app.get("/health")
def health(): return {"status": "ok", "service": "database_mcp", "port": 8005, "timestamp": datetime.utcnow().isoformat()}

@app.post("/read_query")
async def read_query(request: QueryRequest, auth: AuthContext = Depends(get_auth)):
    if not auth.authorize(MCP_NAME, "read"): raise HTTPException(403, "Not authorized")
    # Only allow SELECT queries
    if not request.sql.strip().upper().startswith("SELECT"): raise HTTPException(403, "Only SELECT allowed via read_query")
    conn = await asyncpg.connect(DB_URL)
    try:
        rows = await conn.fetch(request.sql, *request.params)
        return {"rows": [dict(r) for r in rows], "count": len(rows)}
    finally:
        await conn.close()

@app.post("/write_query")
async def write_query(request: QueryRequest, auth: AuthContext = Depends(get_auth)):
    # Blocked for QA, PO, TL agents
    blocked_agents = ["QA", "PO", "TL"]
    if any(auth.agent_id.startswith(a) for a in blocked_agents): raise HTTPException(403, "Write queries blocked for this agent type")
    if not auth.authorize(MCP_NAME, "write"): raise HTTPException(403, "Not authorized")
    conn = await asyncpg.connect(DB_URL)
    try:
        result = await conn.execute(request.sql, *request.params)
        return {"result": str(result)}
    finally:
        await conn.close()

if __name__ == "__main__":
    import uvicorn; uvicorn.run(app, host="0.0.0.0", port=8005)
