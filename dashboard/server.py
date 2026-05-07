"""
Dashboard Server — Web UI for 19-Agent Build System
Provides real-time build monitoring and status display
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncpg
import json
from datetime import datetime
from pathlib import Path

app = FastAPI(title="Build System Dashboard", version="1.0.0")

# Database connection
DB_URL = "postgresql://agents_user:agents_secure_pass_2026@localhost/governance_db"

# Templates
templates = Jinja2Templates(directory="/opt/agents/dashboard/templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/builds")
async def get_builds():
    """Get all builds"""
    async with asyncpg.create_pool(DB_URL, min_size=1, max_size=5) as pool:
        async with pool.acquire() as conn:
            builds = await conn.fetch("SELECT * FROM builds ORDER BY created_at DESC LIMIT 20")
            return [{"build_id": b["build_id"], "status": b["status"], "current_phase": b["current_phase"], 
                    "created_at": str(b.get("created_at", "")), "completed_at": str(b.get("completed_at", ""))} 
                   for b in builds]

@app.get("/api/builds/{build_id}/gates")
async def get_build_gates(build_id: str):
    """Get gates for a specific build"""
    async with asyncpg.create_pool(DB_URL, min_size=1, max_size=5) as pool:
        async with pool.acquire() as conn:
            gates = await conn.fetch("SELECT * FROM gates WHERE build_id = $1 ORDER BY passed_at", build_id)
            return [{"gate_id": g["gate_id"], "status": g["status"], "passed_by": g["passed_by"], 
                    "passed_at": str(g.get("passed_at", ""))} for g in gates]

@app.get("/api/builds/{build_id}/events")
async def get_build_events(build_id: str):
    """Get events for a specific build"""
    async with asyncpg.create_pool(DB_URL, min_size=1, max_size=5) as pool:
        async with pool.acquire() as conn:
            events = await conn.fetch("SELECT * FROM events WHERE build_id = $1 ORDER BY event_at DESC LIMIT 50", build_id)
            return [{"event_type": e["event_type"], "event_at": str(e.get("event_at", "")), 
                    "payload": e.get("payload", {})} for e in events]

@app.get("/api/agents")
async def get_agents():
    """Get all agents"""
    import sys
    sys.path.insert(0, '/opt/agents')
    from agents import ALL_AGENTS
    return [{"name": name} for name in ALL_AGENTS.keys()]

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    async with asyncpg.create_pool(DB_URL, min_size=1, max_size=5) as pool:
        async with pool.acquire() as conn:
            total_builds = await conn.fetchval("SELECT COUNT(*) FROM builds")
            completed_builds = await conn.fetchval("SELECT COUNT(*) FROM builds WHERE status = 'COMPLETE'")
            total_gates = await conn.fetchval("SELECT COUNT(*) FROM gates")
            passed_gates = await conn.fetchval("SELECT COUNT(*) FROM gates WHERE status = 'PASSED'")
            return {
                "total_builds": total_builds,
                "completed_builds": completed_builds,
                "total_gates": total_gates,
                "passed_gates": passed_gates
            }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
