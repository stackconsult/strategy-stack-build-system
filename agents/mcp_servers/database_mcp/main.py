import sys
sys.path.insert(0, '/opt/agents')

import asyncpg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import structlog

log = structlog.get_logger()
app = FastAPI(title="database_mcp", version="1.0.0")

class QueryRequest(BaseModel):
    query: str

class ExecuteRequest(BaseModel):
    query: str

@app.get("/health")
def health():
    return {"status": "ok", "server": "database_mcp", "port": 8005}

@app.post("/query")
async def query(req: QueryRequest):
    # Execute read-only query
    conn = await asyncpg.connect(
        user="agents_user",
        password="agents_secure_pass_2026",
        database="governance_db",
        host="localhost"
    )
    try:
        result = await conn.fetch(req.query)
        return {"rows": [dict(row) for row in result]}
    finally:
        await conn.close()

@app.post("/execute")
async def execute(req: ExecuteRequest):
    # Execute write query
    conn = await asyncpg.connect(
        user="agents_user",
        password="agents_secure_pass_2026",
        database="governance_db",
        host="localhost"
    )
    try:
        result = await conn.execute(req.query)
        return {"result": result}
    finally:
        await conn.close()
