import sys
sys.path.insert(0, '/opt/agents')

import os
import shutil
import asyncio
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import structlog

log = structlog.get_logger()
app = FastAPI(title="filesystem_mcp", version="1.0.0")

ALLOWED_ROOTS = ["/opt/agents", "/Volumes/STORE N GO/builds", "/tmp"]

def _safe_path(path: str) -> Path:
    p = Path(path).resolve()
    if not any(str(p).startswith(root) for root in ALLOWED_ROOTS):
        raise HTTPException(400, f"Path {path} outside allowed roots: {ALLOWED_ROOTS}")
    return p

class ReadFileRequest(BaseModel):
    path: str

class WriteFileRequest(BaseModel):
    path: str
    content: str
    create_dirs: bool = True

class ListDirRequest(BaseModel):
    path: str

class DeleteFileRequest(BaseModel):
    path: str

class MoveFileRequest(BaseModel):
    src: str
    dst: str

class MakeDirRequest(BaseModel):
    path: str

class FileExistsRequest(BaseModel):
    path: str

@app.get("/health")
def health():
    return {"status": "ok", "server": "filesystem_mcp", "port": 8001}

@app.post("/read_file")
def read_file(req: ReadFileRequest):
    p = _safe_path(req.path)
    if not p.exists():
        raise HTTPException(404, f"File not found: {req.path}")
    return {"path": str(p), "content": p.read_text()}

@app.post("/write_file")
def write_file(req: WriteFileRequest):
    p = _safe_path(req.path)
    if req.create_dirs:
        p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(req.content)
    log.info("file_written", path=str(p), size=len(req.content))
    return {"path": str(p), "bytes_written": len(req.content)}

@app.post("/list_dir")
def list_dir(req: ListDirRequest):
    p = _safe_path(req.path)
    if not p.exists():
        raise HTTPException(404, f"Directory not found: {req.path}")
    entries = []
    for item in sorted(p.iterdir()):
        entries.append({"name": item.name, "type": "dir" if item.is_dir() else "file", "size": item.stat().st_size if item.is_file() else 0})
    return {"path": str(p), "entries": entries}

@app.post("/delete_file")
def delete_file(req: DeleteFileRequest):
    p = _safe_path(req.path)
    if not p.exists():
        raise HTTPException(404, f"Not found: {req.path}")
    if p.is_dir():
        shutil.rmtree(p)
    else:
        p.unlink()
    log.info("file_deleted", path=str(p))
    return {"deleted": str(p)}

@app.post("/move_file")
def move_file(req: MoveFileRequest):
    src = _safe_path(req.src)
    dst = _safe_path(req.dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    return {"moved": {"from": str(src), "to": str(dst)}}

@app.post("/make_dir")
def make_dir(req: MakeDirRequest):
    p = _safe_path(req.path)
    p.mkdir(parents=True, exist_ok=True)
    return {"created": str(p)}

@app.post("/file_exists")
def file_exists(req: FileExistsRequest):
    p = _safe_path(req.path)
    return {"path": str(p), "exists": p.exists(), "is_file": p.is_file(), "is_dir": p.is_dir}
