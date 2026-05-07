import sys
sys.path.insert(0, '/opt/agents')

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import structlog

log = structlog.get_logger()
app = FastAPI(title="secrets_mcp", version="1.0.0")

class GetSecretRequest(BaseModel):
    secret_name: str

class SetSecretRequest(BaseModel):
    secret_name: str
    secret_value: str

@app.get("/health")
def health():
    return {"status": "ok", "server": "secrets_mcp", "port": 8004}

@app.post("/get_secret")
def get_secret(req: GetSecretRequest):
    # For local dev, use environment variables
    value = os.getenv(req.secret_name)
    if value is None:
        raise HTTPException(404, f"Secret not found: {req.secret_name}")
    # Never log secret values
    log.info("secret_retrieved", secret_name=req.secret_name)
    return {"secret_name": req.secret_name, "value": value}

@app.post("/set_secret")
def set_secret(req: SetSecretRequest):
    # For local dev, set environment variable
    os.environ[req.secret_name] = req.secret_value
    log.info("secret_set", secret_name=req.secret_name)
    return {"secret_name": req.secret_name, "set": True}

@app.get("/list_secrets")
def list_secrets():
    # List secret names only (not values)
    return {"secrets": ["DATABASE_URL", "REDIS_URL", "SECRET_KEY"]}
