"""Universal MCP server base — each server extends this."""
import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

log = structlog.get_logger()

def make_mcp_app(server_name: str, port: int) -> FastAPI:
    app = FastAPI(title=f"{server_name} MCP", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "server": server_name,
            "port": port,
            "mcp_version": "1.0.0"
        }

    @app.post("/tools/call")
    async def call_tool(body: dict):
        tool = body.get("tool", "")
        args = body.get("args", {})
        log.info("mcp_tool_call", server=server_name, tool=tool)
        return {
            "server": server_name,
            "tool": tool,
            "status": "executed",
            "result": {}
        }

    @app.get("/tools")
    def list_tools():
        return {"server": server_name, "tools": []}

    return app
