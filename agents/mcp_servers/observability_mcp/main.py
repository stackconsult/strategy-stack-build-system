import sys
sys.path.insert(0, '/opt/agents')

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import structlog

log = structlog.get_logger()
app = FastAPI(title="observability_mcp", version="1.0.0")

class QueryPrometheusRequest(BaseModel):
    query: str

class CheckTraceRequest(BaseModel):
    trace_id: str

class FireTestAlertRequest(BaseModel):
    alert_name: str

@app.get("/health")
def health():
    return {"status": "ok", "server": "observability_mcp", "port": 8006}

@app.post("/query_prometheus")
def query_prometheus(req: QueryPrometheusRequest):
    # Placeholder for Prometheus query
    log.info("prometheus_queried", query=req.query)
    return {"query": req.query, "result": []}

@app.post("/check_trace")
def check_trace(req: CheckTraceRequest):
    # Placeholder for trace check
    return {"trace_id": req.trace_id, "found": False}

@app.post("/fire_test_alert")
def fire_test_alert(req: FireTestAlertRequest):
    # Placeholder for test alert
    log.info("test_alert_fired", alert=req.alert_name)
    return {"alert": req.alert_name, "fired": True}
