import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncpg
import structlog

log = structlog.get_logger()
DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://agents_user:agents_secure_pass_2026@localhost/governance_db"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = await asyncpg.create_pool(DB_URL, min_size=2, max_size=10)
    log.info("orchestrator_started", port=8008)
    yield
    await app.state.db_pool.close()
    log.info("orchestrator_stopped")

app = FastAPI(title="Orchestrator", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class BuildStartRequest(BaseModel):
    prd_path: str
    build_id: Optional[str] = None

@app.get("/health")
def health():
    return {"status": "ok", "server": "orchestrator", "port": 8008}

@app.post("/api/builds/start")
async def start_build(req: BuildStartRequest):
    build_id = req.build_id or f"BUILD_{asyncio.get_event_loop().time()}"
    async with app.state.db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO builds (build_id, status, prd_path) VALUES ($1, 'PENDING', $2)",
            build_id, req.prd_path
        )
    return {"build_id": build_id, "status": "PENDING"}

@app.get("/api/builds/{build_id}/status")
async def get_build_status(build_id: str):
    async with app.state.db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM builds WHERE build_id = $1", build_id
        )
    if not row:
        raise HTTPException(status_code=404, detail="Build not found")
    return dict(row)

@app.get("/api/gates")
async def list_gates():
    async with app.state.db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM gates ORDER BY passed_at DESC LIMIT 100")
    return {"gates": [dict(r) for r in rows]}

@app.get("/api/builds/{build_id}/events")
async def list_build_events(build_id: str):
    async with app.state.db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM events WHERE build_id = $1 ORDER BY created_at", build_id
        )
    return {"events": [dict(r) for r in rows]}
