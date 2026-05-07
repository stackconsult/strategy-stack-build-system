import sys
sys.path.insert(0, '/opt/agents')

import os
import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import structlog

log = structlog.get_logger()
app = FastAPI(title="git_mcp", version="1.0.0")

class CloneRepoRequest(BaseModel):
    repo_url: str
    dest_path: str

class CreateBranchRequest(BaseModel):
    repo_path: str
    branch_name: str

class CommitRequest(BaseModel):
    repo_path: str
    message: str

class PushRequest(BaseModel):
    repo_path: str

@app.get("/health")
def health():
    return {"status": "ok", "server": "git_mcp", "port": 8002}

@app.post("/clone_repo")
def clone_repo(req: CloneRepoRequest):
    try:
        subprocess.run(["git", "clone", req.repo_url, req.dest_path], check=True, capture_output=True)
        log.info("repo_cloned", repo_url=req.repo_url, dest=req.dest_path)
        return {"cloned": req.dest_path}
    except subprocess.CalledProcessError as e:
        raise HTTPException(500, f"Git clone failed: {e.stderr.decode()}")

@app.post("/create_branch")
def create_branch(req: CreateBranchRequest):
    if req.branch_name == "main":
        raise HTTPException(400, "Cannot create branch named 'main'")
    try:
        subprocess.run(["git", "-C", req.repo_path, "checkout", "-b", req.branch_name], check=True, capture_output=True)
        log.info("branch_created", branch=req.branch_name, repo=req.repo_path)
        return {"branch": req.branch_name}
    except subprocess.CalledProcessError as e:
        raise HTTPException(500, f"Branch creation failed: {e.stderr.decode()}")

@app.post("/commit")
def commit(req: CommitRequest):
    try:
        subprocess.run(["git", "-C", req.repo_path, "add", "."], check=True, capture_output=True)
        subprocess.run(["git", "-C", req.repo_path, "commit", "-m", req.message], check=True, capture_output=True)
        log.info("commit_made", repo=req.repo_path, message=req.message)
        return {"committed": True}
    except subprocess.CalledProcessError as e:
        raise HTTPException(500, f"Commit failed: {e.stderr.decode()}")

@app.post("/push")
def push(req: PushRequest):
    try:
        subprocess.run(["git", "-C", req.repo_path, "push"], check=True, capture_output=True)
        log.info("pushed", repo=req.repo_path)
        return {"pushed": True}
    except subprocess.CalledProcessError as e:
        raise HTTPException(500, f"Push failed: {e.stderr.decode()}")
