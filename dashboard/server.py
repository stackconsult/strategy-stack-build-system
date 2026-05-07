"""
Dashboard Server — Web UI for 19-Agent Build System
Provides real-time build monitoring and status display
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
import json
from datetime import datetime
from pathlib import Path

app = FastAPI(title="Build System Dashboard", version="1.0.0")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
DB_URL = "postgresql://agents_user:agents_secure_pass_2026@localhost/governance_db"

# HTML template as string (avoiding Jinja2 caching issues)
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>19-Agent Build System Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header h1 {
            color: #333;
            font-size: 28px;
            margin-bottom: 10px;
        }
        .header p {
            color: #666;
            font-size: 14px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .stat-card h3 {
            color: #666;
            font-size: 14px;
            margin-bottom: 10px;
            text-transform: uppercase;
        }
        .stat-card .value {
            color: #333;
            font-size: 36px;
            font-weight: bold;
        }
        .builds-section {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .builds-section h2 {
            color: #333;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .build-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }
        .build-card.complete {
            border-left-color: #10b981;
        }
        .build-card.running {
            border-left-color: #f59e0b;
        }
        .build-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .build-id {
            font-weight: bold;
            color: #333;
            font-size: 16px;
        }
        .build-status {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }
        .build-status.complete {
            background: #d1fae5;
            color: #065f46;
        }
        .build-status.running {
            background: #fef3c7;
            color: #92400e;
        }
        .build-details {
            color: #666;
            font-size: 14px;
        }
        .gates-list {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-top: 10px;
        }
        .gate-badge {
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            background: #e5e7eb;
            color: #374151;
        }
        .gate-badge.passed {
            background: #d1fae5;
            color: #065f46;
        }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            margin-top: 20px;
        }
        .refresh-btn:hover {
            background: #5568d3;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>19-Agent Build System Dashboard</h1>
            <p>Real-time build monitoring and status tracking</p>
        </div>
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Builds</h3>
                <div class="value" id="total-builds">-</div>
            </div>
            <div class="stat-card">
                <h3>Completed</h3>
                <div class="value" id="completed-builds">-</div>
            </div>
            <div class="stat-card">
                <h3>Total Gates</h3>
                <div class="value" id="total-gates">-</div>
            </div>
            <div class="stat-card">
                <h3>Gates Passed</h3>
                <div class="value" id="passed-gates">-</div>
            </div>
        </div>
        <div class="builds-section">
            <h2>Recent Builds</h2>
            <div id="builds-list"><p>Loading...</p></div>
            <button class="refresh-btn" onclick="loadData()">Refresh</button>
        </div>
    </div>
    <script>
        async function loadData() {
            try {
                const statsRes = await fetch('/api/stats');
                const stats = await statsRes.json();
                document.getElementById('total-builds').textContent = stats.total_builds;
                document.getElementById('completed-builds').textContent = stats.completed_builds;
                document.getElementById('total-gates').textContent = stats.total_gates;
                document.getElementById('passed-gates').textContent = stats.passed_gates;
                const buildsRes = await fetch('/api/builds');
                const builds = await buildsRes.json();
                const buildsList = document.getElementById('builds-list');
                if (builds.length === 0) {
                    buildsList.innerHTML = '<p>No builds found</p>';
                    return;
                }
                let html = builds.map(build => `
                    <div class="build-card ${build.status.toLowerCase()}">
                        <div class="build-header">
                            <span class="build-id">${build.build_id}</span>
                            <span class="build-status ${build.status.toLowerCase()}">${build.status}</span>
                        </div>
                        <div class="build-details">
                            Phase: ${build.current_phase} | 
                            Created: ${new Date(build.created_at).toLocaleString()}
                            ${build.completed_at ? ` | Completed: ${new Date(build.completed_at).toLocaleString()}` : ''}
                        </div>
                    </div>
                `).join('');
                buildsList.innerHTML = html;
            } catch (error) {
                console.error('Error loading data:', error);
                document.getElementById('builds-list').innerHTML = '<p>Error loading data</p>';
            }
        }
        loadData();
        setInterval(loadData, 10000);
    </script>
</body>
</html>'''

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return HTMLResponse(content=HTML_TEMPLATE, status_code=200)

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
