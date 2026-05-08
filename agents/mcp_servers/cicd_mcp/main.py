import sys
sys.path.insert(0, '/opt/agents')

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import structlog

log = structlog.get_logger()
app = FastAPI(title="cicd_mcp", version="1.0.0")

class TriggerWorkflowRequest(BaseModel):
    repo: str
    workflow: str
    branch: str

@app.get("/health")
def health():
    return {"status": "ok", "server": "cicd_mcp", "port": 8003}

@app.post("/trigger_workflow")
async def trigger_workflow(req: TriggerWorkflowRequest):
    # Placeholder for GitHub Actions trigger
    log.info("workflow_triggered", repo=req.repo, workflow=req.workflow, branch=req.branch)
    return {"triggered": True, "workflow": req.workflow, "branch": req.branch}

@app.get("/workflow_status/{run_id}")
async def workflow_status(run_id: str):
    # Placeholder for workflow status check
    return {"run_id": run_id, "status": "queued"}
