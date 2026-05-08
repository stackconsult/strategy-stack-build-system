import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import asyncpg
import redis
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
from uuid import uuid4
from datetime import datetime
import structlog

log = structlog.get_logger()
app = FastAPI(title="orchestrator", version="1.0.0")

# Database pool
pg_pool = None
redis_client = None

class BuildStartRequest(BaseModel):
    prd_path: str
    build_id: Optional[str] = None
    metadata: Dict[str, Any] = {}

@app.on_event("startup")
async def startup():
    global pg_pool, redis_client
    try:
        # Try cloud PostgreSQL first
        pg_pool = await asyncpg.create_pool(
            user="postgres",
            password="agents_secure_pass_2026",
            database="postgres",
            host="db.asaajoefhifdqhprowek.supabase.co",
            port=5432
        )
        log.info("connected_to_cloud_postgresql")
    except Exception as e:
        log.warning("cloud_postgresql_failed", error=str(e))
        # Fallback to local PostgreSQL
        try:
            pg_pool = await asyncpg.create_pool(
                user="agents_user",
                password="agents_secure_pass_2026",
                database="governance_db",
                host="localhost"
            )
            log.info("connected_to_local_postgresql")
        except Exception as local_error:
            log.error("postgresql_connection_failed", cloud_error=str(e), local_error=str(local_error))
            raise
    redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
    log.info("orchestrator_started")

@app.on_event("shutdown")
async def shutdown():
    if pg_pool:
        await pg_pool.close()
    if redis_client:
        redis_client.close()
    log.info("orchestrator_stopped")

@app.get("/health")
def health():
    return {"status": "ok", "server": "orchestrator", "port": 8008}

@app.post("/api/builds/start")
async def start_build(req: BuildStartRequest, background_tasks: BackgroundTasks):
    build_id = req.build_id or str(uuid4())
    
    # Create build record
    async with pg_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO builds (build_id, status, current_phase, prd_path, metadata, started_at)
            VALUES ($1, 'ACTIVE', 1, $2, $3, $4)
        """, build_id, req.prd_path, req.metadata, datetime.utcnow())
    
    log.info("build_started", build_id=build_id, prd_path=req.prd_path)
    
    # Start background build process
    background_tasks.add_task(run_build_process, build_id, req.prd_path)
    
    return {"build_id": build_id, "status": "ACTIVE", "phase": 1}

@app.get("/api/builds/{build_id}/status")
async def get_build_status(build_id: str):
    async with pg_pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT * FROM builds WHERE build_id = $1
        """, build_id)
    
    if not row:
        raise HTTPException(404, f"Build {build_id} not found")
    
    build = dict(row)
    
    # Get recent events
    async with pg_pool.acquire() as conn:
        events = await conn.fetch("""
            SELECT * FROM events WHERE build_id = $1
            ORDER BY timestamp_utc DESC LIMIT 10
        """, build_id)
    
    return {
        "build": build,
        "recent_events": [dict(e) for e in events]
    }

@app.get("/api/gates")
async def get_gates():
    async with pg_pool.acquire() as conn:
        gates = await conn.fetch("""
            SELECT * FROM gates ORDER BY gate_id
        """)
    
    return {"gates": [dict(g) for g in gates]}

@app.get("/api/blockers/{build_id}")
async def get_blockers(build_id: str):
    async with pg_pool.acquire() as conn:
        blockers = await conn.fetch("""
            SELECT * FROM blockers WHERE build_id = $1 AND resolved = false
        """, build_id)
    
    return {"blockers": [dict(b) for b in blockers]}

async def run_build_process(build_id: str, prd_path: str):
    """Background process to run the build through all agents."""
    log.info("build_process_started", build_id=build_id)
    
    # Import agents
    from agents.po_agent.v1 import POAgentV1
    from agents.tl_agent.v1 import TLAgentV1
    from agents.do_agent.v1 import DOAgentV1
    from agents.tl_agent.v2 import TLAgentV2
    from agents.be_agent.v1 import BEAgentV1
    from agents.fe_agent.v1 import FEAgentV1
    from agents.do_agent.v2 import DOAgentV2
    from agents.tl_agent.v3 import TLAgentV3
    from agents.qa_agent.v1 import QAAgentV1
    from agents.be_agent.v2 import BEAgentV2
    from agents.fe_agent.v2 import FEAgentV2
    from agents.tl_agent.v4 import TLAgentV4
    from agents.be_agent.v3 import BEAgentV3
    from agents.do_agent.v3 import DOAgentV3
    from agents.po_agent.v2 import POAgentV2
    from agents.tl_agent.v5 import TLAgentV5
    from agents.do_agent.v4 import DOAgentV4
    from agents.tl_agent.v6 import TLAgentV6
    
    # Initialize agents
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    repo_path = f"{workspace_dir}/builds/{build_id}"
    
    # Phase 1: PO + TL + DO
    po_v1 = POAgentV1(build_id, prd_path)
    await po_v1.initialize()
    await po_v1.run()
    
    tl_v1 = TLAgentV1(build_id, po_v1.structured_spec, repo_path)
    await tl_v1.initialize()
    await tl_v1.run()
    
    do_v1 = DOAgentV1(build_id, repo_path, po_v1.structured_spec.get("tech_stack", {}))
    await do_v1.initialize()
    await do_v1.run()
    
    tl_v2 = TLAgentV2(build_id, po_v1.structured_spec, repo_path)
    await tl_v2.initialize()
    await tl_v2.run()
    
    # Phase 3: BE + FE + DO (parallel)
    be_v1 = BEAgentV1(build_id, repo_path, f"/builds/{build_id}/specs/api-spec.yaml")
    fe_v1 = FEAgentV1(build_id, repo_path, f"/builds/{build_id}/specs/api-spec.yaml")
    do_v2 = DOAgentV2(build_id, repo_path, po_v1.structured_spec)
    
    await asyncio.gather(
        be_v1.initialize(),
        fe_v1.initialize(),
        do_v2.initialize()
    )
    
    await asyncio.gather(
        be_v1.run(),
        fe_v1.run(),
        do_v2.run()
    )
    
    # Phase 4: QA + BE + FE + TL
    qa_v1 = QAAgentV1(build_id, repo_path)
    be_v2 = BEAgentV2(build_id, repo_path)
    fe_v2 = FEAgentV2(build_id, repo_path)
    tl_v4 = TLAgentV4(build_id)
    
    await asyncio.gather(
        qa_v1.initialize(),
        be_v2.initialize(),
        fe_v2.initialize(),
        tl_v4.initialize()
    )
    
    await asyncio.gather(
        qa_v1.run(),
        be_v2.run(),
        fe_v2.run(),
        tl_v4.run()
    )
    
    # Phase 5: BE + DO + PO + TL
    be_v3 = BEAgentV3(build_id, repo_path)
    do_v3 = DOAgentV3(build_id, repo_path)
    po_v2 = POAgentV2(build_id, prd_path)
    tl_v5 = TLAgentV5(build_id)
    
    await asyncio.gather(
        be_v3.initialize(),
        do_v3.initialize(),
        po_v2.initialize(),
        tl_v5.initialize()
    )
    
    await asyncio.gather(
        be_v3.run(),
        do_v3.run(),
        po_v2.run(),
        tl_v5.run()
    )
    
    # Phase 6: DO + TL
    do_v4 = DOAgentV4(build_id, repo_path)
    tl_v6 = TLAgentV6(build_id)
    
    await asyncio.gather(
        do_v4.initialize(),
        tl_v6.initialize()
    )
    
    await asyncio.gather(
        do_v4.run(),
        tl_v6.run()
    )
    
    log.info("build_process_complete", build_id=build_id)
