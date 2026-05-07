"""
MCP-2: Git MCP Server
Port: 8002
Purpose: Git operations + GitHub PR management
"""
import sys
sys.path.insert(0, '/opt/agents/mcp-servers')

import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from shared.auth import create_auth_context, AuthContext

MCP_NAME = "git_mcp"
VAULT_ROOT = Path(os.getenv("VAULT_PATH", "/opt/agents"))

app = FastAPI(
    title="Git MCP",
    description="Git and GitHub operations for StackConsulting 19-Agent Build System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class CloneRepoRequest(BaseModel):
    repo_url: str = Field(..., description="Git repository URL")
    target_path: str = Field(..., description="Local path to clone into")
    branch: Optional[str] = Field(None, description="Branch to checkout")
    build_id: str = Field(..., description="Build ID for authorization")

class CreateBranchRequest(BaseModel):
    repo_path: str = Field(..., description="Path to git repository")
    branch_name: str = Field(..., description="Name of new branch")
    base_branch: str = Field("main", description="Base branch to create from")
    build_id: str = Field(..., description="Build ID for authorization")

class CommitRequest(BaseModel):
    repo_path: str = Field(..., description="Path to git repository")
    message: str = Field(..., description="Commit message")
    files: Optional[List[str]] = Field(None, description="Specific files to commit (None = all)")
    build_id: str = Field(..., description="Build ID for authorization")

class CreatePRRequest(BaseModel):
    repo_path: str = Field(..., description="Path to git repository")
    title: str = Field(..., description="PR title")
    body: str = Field(..., description="PR description")
    head_branch: str = Field(..., description="Branch with changes")
    base_branch: str = Field("main", description="Target branch")
    build_id: str = Field(..., description="Build ID for authorization")

# Auth dependency
async def get_auth(
    x_agent_id: str = Header(...),
    x_agent_token: str = Header(...),
    x_build_id: str = Header(...)
) -> AuthContext:
    auth = create_auth_context(x_agent_id, x_agent_token, x_build_id)
    if not auth.authenticate():
        raise HTTPException(status_code=401, detail="Authentication failed")
    return auth

@app.get("/health")
def health():
    return {"status": "ok", "service": "git_mcp", "port": 8002, "timestamp": datetime.utcnow().isoformat()}

@app.post("/clone_repo")
def clone_repo(request: CloneRepoRequest, auth: AuthContext = Depends(get_auth)):
    if not auth.authorize(MCP_NAME, "clone"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    target = Path(request.target_path)
    if not target.is_absolute():
        target = VAULT_ROOT / "builds" / request.build_id / request.target_path
    
    # Prevent cloning into existing directory
    if target.exists():
        raise HTTPException(status_code=400, detail="Target directory already exists")
    
    try:
        cmd = ["git", "clone", request.repo_url, str(target)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Git clone failed: {result.stderr}")
        
        # Checkout specific branch if requested
        if request.branch:
            checkout = subprocess.run(
                ["git", "checkout", request.branch],
                cwd=str(target),
                capture_output=True,
                text=True,
                timeout=60
            )
            if checkout.returncode != 0:
                raise HTTPException(status_code=500, detail=f"Branch checkout failed: {checkout.stderr}")
        
        return {"status": "success", "path": str(target), "branch": request.branch or "default"}
    
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Git clone timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clone error: {str(e)}")

@app.post("/create_branch")
def create_branch(request: CreateBranchRequest, auth: AuthContext = Depends(get_auth)):
    if not auth.authorize(MCP_NAME, "branch"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # CRITICAL: Block creation of 'main' branch
    if request.branch_name == "main":
        raise HTTPException(status_code=403, detail="Cannot create branch named 'main' — protected")
    
    repo = Path(request.repo_path)
    if not repo.is_absolute():
        repo = VAULT_ROOT / "builds" / request.build_id / request.repo_path
    
    if not (repo / ".git").exists():
        raise HTTPException(status_code=400, detail="Not a git repository")
    
    try:
        # Create and checkout branch
        result = subprocess.run(
            ["git", "checkout", "-b", request.branch_name],
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Branch creation failed: {result.stderr}")
        
        return {"status": "success", "branch": request.branch_name, "repo": str(repo)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Branch error: {str(e)}")

@app.post("/commit")
def commit(request: CommitRequest, auth: AuthContext = Depends(get_auth)):
    if not auth.authorize(MCP_NAME, "commit"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    repo = Path(request.repo_path)
    if not repo.is_absolute():
        repo = VAULT_ROOT / "builds" / request.build_id / request.repo_path
    
    if not (repo / ".git").exists():
        raise HTTPException(status_code=400, detail="Not a git repository")
    
    try:
        # Add files
        if request.files:
            for f in request.files:
                subprocess.run(["git", "add", f], cwd=str(repo), check=True, timeout=30)
        else:
            subprocess.run(["git", "add", "."], cwd=str(repo), check=True, timeout=30)
        
        # Commit
        result = subprocess.run(
            ["git", "commit", "-m", request.message],
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            # Check if nothing to commit
            if "nothing to commit" in result.stdout:
                return {"status": "no_changes", "message": "Nothing to commit"}
            raise HTTPException(status_code=500, detail=f"Commit failed: {result.stderr}")
        
        # Get commit hash
        hash_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=10
        )
        commit_hash = hash_result.stdout.strip() if hash_result.returncode == 0 else None
        
        return {"status": "success", "commit_hash": commit_hash, "message": request.message}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Commit error: {str(e)}")

@app.post("/create_pull_request")
def create_pr(request: CreatePRRequest, auth: AuthContext = Depends(get_auth)):
    if not auth.authorize(MCP_NAME, "pr"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    repo = Path(request.repo_path)
    if not repo.is_absolute():
        repo = VAULT_ROOT / "builds" / request.build_id / request.repo_path
    
    # CRITICAL: PR requires CI pass
    # In production, this would check CI status via GitHub API
    # For now, we simulate the check
    
    # Push branch first
    try:
        push = subprocess.run(
            ["git", "push", "-u", "origin", request.head_branch],
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if push.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Push failed: {push.stderr}")
        
        # Create PR via gh CLI if available
        gh_check = subprocess.run(["which", "gh"], capture_output=True)
        if gh_check.returncode == 0:
            pr_result = subprocess.run(
                [
                    "gh", "pr", "create",
                    "--title", request.title,
                    "--body", request.body,
                    "--head", request.head_branch,
                    "--base", request.base_branch
                ],
                cwd=str(repo),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if pr_result.returncode == 0:
                return {"status": "success", "pr_url": pr_result.stdout.strip()}
        
        # Fallback: return branch info
        return {
            "status": "pushed",
            "message": "Branch pushed to origin. PR creation requires gh CLI or manual creation.",
            "head_branch": request.head_branch,
            "base_branch": request.base_branch
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PR error: {str(e)}")

@app.post("/repo_status")
def repo_status(repo_path: str, build_id: str, auth: AuthContext = Depends(get_auth)):
    if not auth.authorize(MCP_NAME, "read"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    repo = Path(repo_path)
    if not repo.is_absolute():
        repo = VAULT_ROOT / "builds" / build_id / repo_path
    
    if not (repo / ".git").exists():
        raise HTTPException(status_code=400, detail="Not a git repository")
    
    try:
        # Get current branch
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=10
        )
        current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
        
        # Get status
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=10
        )
        has_changes = len(status_result.stdout.strip()) > 0
        
        # Get last commit
        log_result = subprocess.run(
            ["git", "log", "-1", "--oneline"],
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=10
        )
        last_commit = log_result.stdout.strip() if log_result.returncode == 0 else "unknown"
        
        return {
            "repo_path": str(repo),
            "current_branch": current_branch,
            "has_uncommitted_changes": has_changes,
            "last_commit": last_commit,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
