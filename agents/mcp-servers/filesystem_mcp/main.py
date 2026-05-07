"""
MCP-1: Filesystem MCP Server
Port: 8001
Purpose: Append-only governance log writer, safe file operations
"""
import sys
sys.path.insert(0, '/opt/agents/mcp-servers')

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from shared.governance import append_governance_record, read_governance_log
from shared.auth import create_auth_context, AuthContext

# Configuration
VAULT_ROOT = Path(os.getenv("VAULT_PATH", "/opt/agents"))
MCP_NAME = "filesystem_mcp"

app = FastAPI(
    title="Filesystem MCP",
    description="Safe file operations for StackConsulting 19-Agent Build System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ReadFileRequest(BaseModel):
    path: str = Field(..., description="File path relative to vault or absolute")
    build_id: str = Field(..., description="Build ID for authorization")

class ReadFileResponse(BaseModel):
    content: str
    path: str
    size_bytes: int
    modified_at: str

class WriteFileRequest(BaseModel):
    path: str = Field(..., description="File path to write")
    content: str = Field(..., description="File content")
    build_id: str = Field(..., description="Build ID for authorization")

class WriteFileResponse(BaseModel):
    path: str
    bytes_written: int
    record_id: Optional[str] = None

class AppendJsonlRequest(BaseModel):
    path: str = Field(..., description="JSONL file path to append to")
    record: Dict[str, Any] = Field(..., description="JSON record to append")
    build_id: str = Field(..., description="Build ID for authorization")

class AppendJsonlResponse(BaseModel):
    path: str
    record_id: str

class ListDirRequest(BaseModel):
    path: str = Field(..., description="Directory path to list")
    build_id: str = Field(..., description="Build ID for authorization")

class ListDirResponse(BaseModel):
    path: str
    entries: List[Dict[str, Any]]

# Authentication dependency
async def get_auth_context(
    x_agent_id: str = Header(...),
    x_agent_token: str = Header(...),
    x_build_id: str = Header(...)
) -> AuthContext:
    """Dependency to authenticate and authorize requests."""
    auth = create_auth_context(x_agent_id, x_agent_token, x_build_id)
    
    if not auth.authenticate():
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    return auth

# Health endpoint
@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "filesystem_mcp",
        "port": 8001,
        "vault_root": str(VAULT_ROOT),
        "timestamp": datetime.utcnow().isoformat()
    }

# Read file endpoint
@app.post("/read_file")
def read_file(
    request: ReadFileRequest,
    auth: AuthContext = Depends(get_auth_context)
) -> ReadFileResponse:
    """
    Read a file from the vault.
    
    Authorization required:
    - Agent must be authenticated
    - Agent must have 'read' access to filesystem_mcp
    - Path must be within build scope
    """
    # Check authorization
    if not auth.authorize(MCP_NAME, "read"):
        raise HTTPException(status_code=403, detail="Not authorized for read")
    
    # Verify path is within scope
    if not auth.verify_path(request.path):
        raise HTTPException(status_code=403, detail="Path outside allowed scope")
    
    # Resolve path
    file_path = Path(request.path)
    if not file_path.is_absolute():
        file_path = VAULT_ROOT / "builds" / request.build_id / request.path
    
    file_path = file_path.resolve()
    
    # Check file exists
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {request.path}")
    
    if not file_path.is_file():
        raise HTTPException(status_code=400, detail=f"Path is not a file: {request.path}")
    
    # Read file
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
    
    # Get file stats
    stat = file_path.stat()
    
    return ReadFileResponse(
        content=content,
        path=str(file_path.relative_to(VAULT_ROOT)),
        size_bytes=len(content.encode("utf-8")),
        modified_at=datetime.fromtimestamp(stat.st_mtime).isoformat()
    )

# Write file endpoint
@app.post("/write_file")
def write_file(
    request: WriteFileRequest,
    auth: AuthContext = Depends(get_auth_context)
) -> WriteFileResponse:
    """
    Write a file to the vault.
    
    Authorization required:
    - Agent must be authenticated
    - Agent must have 'write' access to filesystem_mcp
    - Path must be within build scope
    
    Note: Cannot overwrite governance.jsonl directly.
    """
    # Check authorization
    if not auth.authorize(MCP_NAME, "write"):
        raise HTTPException(status_code=403, detail="Not authorized for write")
    
    # Verify path is within scope
    if not auth.verify_path(request.path):
        raise HTTPException(status_code=403, detail="Path outside allowed scope")
    
    # Resolve path
    file_path = Path(request.path)
    if not file_path.is_absolute():
        file_path = VAULT_ROOT / "builds" / request.build_id / request.path
    
    file_path = file_path.resolve()
    
    # Prevent overwriting governance.jsonl directly
    if file_path.name == "governance.jsonl":
        raise HTTPException(
            status_code=403, 
            detail="Cannot write governance.jsonl directly — use governance API"
        )
    
    # Create parent directories
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write file
    try:
        content_bytes = request.content.encode("utf-8")
        file_path.write_bytes(content_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error writing file: {str(e)}")
    
    # Log to governance
    record_id = append_governance_record(
        record_type="FILE_WRITTEN",
        build_id=request.build_id,
        agent_id=auth.agent_id,
        payload={
            "path": str(file_path.relative_to(VAULT_ROOT)),
            "size_bytes": len(content_bytes),
        },
        step="write_file"
    )
    
    return WriteFileResponse(
        path=str(file_path.relative_to(VAULT_ROOT)),
        bytes_written=len(content_bytes),
        record_id=record_id
    )

# Append to JSONL endpoint (append-only for governance)
@app.post("/append_jsonl")
def append_jsonl(
    request: AppendJsonlRequest,
    auth: AuthContext = Depends(get_auth_context)
) -> AppendJsonlResponse:
    """
    Append a JSON record to a JSONL file.
    
    This is append-only — cannot overwrite existing records.
    Used primarily for governance.jsonl.
    """
    # Check authorization
    if not auth.authorize(MCP_NAME, "append"):
        raise HTTPException(status_code=403, detail="Not authorized for append")
    
    # Verify path is within scope
    if not auth.verify_path(request.path):
        raise HTTPException(status_code=403, detail="Path outside allowed scope")
    
    # Resolve path
    file_path = Path(request.path)
    if not file_path.is_absolute():
        file_path = VAULT_ROOT / "builds" / request.build_id / request.path
    
    file_path = file_path.resolve()
    
    # Ensure it's a .jsonl file
    if not file_path.name.endswith(".jsonl"):
        raise HTTPException(status_code=400, detail="File must be .jsonl format")
    
    # Create parent directories
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Append record
    try:
        record_json = json.dumps(request.record, default=str)
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(record_json + "\n")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error appending to file: {str(e)}")
    
    # Generate record ID
    record_id = f"jsonl-{request.build_id}-{datetime.utcnow().isoformat()}"
    
    return AppendJsonlResponse(
        path=str(file_path.relative_to(VAULT_ROOT)),
        record_id=record_id
    )

# List directory endpoint
@app.post("/list_dir")
def list_dir(
    request: ListDirRequest,
    auth: AuthContext = Depends(get_auth_context)
) -> ListDirResponse:
    """
    List directory contents.
    
    Authorization required:
    - Agent must be authenticated
    - Agent must have 'list' access to filesystem_mcp
    - Path must be within build scope
    """
    # Check authorization
    if not auth.authorize(MCP_NAME, "list"):
        raise HTTPException(status_code=403, detail="Not authorized for list")
    
    # Verify path is within scope
    if not auth.verify_path(request.path):
        raise HTTPException(status_code=403, detail="Path outside allowed scope")
    
    # Resolve path
    dir_path = Path(request.path)
    if not dir_path.is_absolute():
        dir_path = VAULT_ROOT / "builds" / request.build_id / request.path
    
    dir_path = dir_path.resolve()
    
    # Check directory exists
    if not dir_path.exists():
        raise HTTPException(status_code=404, detail=f"Directory not found: {request.path}")
    
    if not dir_path.is_dir():
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {request.path}")
    
    # List entries
    entries = []
    try:
        for entry in dir_path.iterdir():
            stat = entry.stat()
            entries.append({
                "name": entry.name,
                "type": "directory" if entry.is_dir() else "file",
                "size_bytes": stat.st_size if entry.is_file() else None,
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing directory: {str(e)}")
    
    return ListDirResponse(
        path=str(dir_path.relative_to(VAULT_ROOT)),
        entries=entries
    )

# Governance log read endpoint
@app.post("/read_governance_log")
def read_governance(
    build_id: str,
    limit: int = 100,
    auth: AuthContext = Depends(get_auth_context)
):
    """
    Read governance log for a build.
    
    Authorization required:
    - Agent must be authenticated
    - Agent must have 'read' access
    """
    if not auth.authorize(MCP_NAME, "read"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    records = read_governance_log(build_id, limit)
    return {
        "build_id": build_id,
        "records": records,
        "count": len(records)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
