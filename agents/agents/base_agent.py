import sys
sys.path.insert(0, '/opt/agents')

import asyncio
import asyncpg
import redis
import json
import structlog
from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import uuid4

log = structlog.get_logger()

class BaseAgent:
    def __init__(self, agent_id: str, build_id: str, phase: int):
        self.agent_id = agent_id
        self.build_id = build_id
        self.phase = phase
        self.status = "INIT"
        self.current_step = None
        self.pg_pool = None
        self.redis_client = None
        self.heartbeat_task = None
        self.running = False

    async def initialize(self):
        """Initialize database connections and start heartbeat."""
        self.pg_pool = await asyncpg.create_pool(
            user="agents_user",
            password="agents_secure_pass_2026",
            database="governance_db",
            host="localhost"
        )
        self.redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
        self.running = True
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        log.info("agent_initialized", agent_id=self.agent_id, build_id=self.build_id)

    async def _heartbeat_loop(self):
        """Send heartbeat every 30 seconds."""
        while self.running:
            try:
                await self.write_governance_record("HEARTBEAT", 
                    payload={"agent_id": self.agent_id, "status": self.status})
                await asyncio.sleep(30)
            except Exception as e:
                log.error("heartbeat_error", error=str(e))
                await asyncio.sleep(30)

    def set_step(self, step: str):
        """Set current step."""
        self.current_step = step
        log.info("step_set", step=step, agent_id=self.agent_id)

    async def fs_write(self, path: str, content: str):
        """Write content to filesystem via MCP."""
        # TODO: Integrate with filesystem_mcp
        with open(path, 'w') as f:
            f.write(content)
        log.info("file_written", path=path)

    async def emit_gate_pass(self, gate_id: str, evidence: Dict[str, Any]):
        """Emit gate pass event."""
        await self.write_governance_record("GATE_PASS",
            payload={"gate_id": gate_id, "evidence": evidence})
        # Also insert to gates table
        async with self.pg_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO gates (gate_id, build_id, status, evidence, passed_at, passed_by)
                VALUES ($1, $2, 'PASSED', $3, $4, $5)
                ON CONFLICT (gate_id, build_id) DO UPDATE SET
                    status = 'PASSED', evidence = $3, passed_at = $4, passed_by = $5
            """, gate_id, self.build_id, json.dumps(evidence), 
                datetime.utcnow(), self.agent_id)
        log.info("gate_passed", gate_id=gate_id, agent_id=self.agent_id)

    async def emit_completion_signal(self, to_agent: str, summary: str, 
                                     gates_passed: List[str], payload: Dict[str, Any]):
        """Emit completion signal to another agent."""
        await self.write_governance_record("COMPLETION_SIGNAL",
            payload={
                "from_agent": self.agent_id,
                "to_agent": to_agent,
                "summary": summary,
                "gates_passed": gates_passed,
                "payload": payload
            })
        # Store message for recipient
        async with self.pg_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO messages (message_id, from_agent, to_agent, message_type, build_id, payload, timestamp_utc)
                VALUES ($1, $2, $3, 'COMPLETION_SIGNAL', $4, $5, $6)
            """, str(uuid4()), self.agent_id, to_agent, self.build_id, 
                json.dumps(payload), datetime.utcnow())
        log.info("completion_emitted", to_agent=to_agent, agent_id=self.agent_id)

    async def emit_blocker_alert(self, message: str, gate_id: Optional[str] = None):
        """Emit blocker alert."""
        await self.write_governance_record("BLOCKER_ALERT",
            payload={"message": message, "gate_id": gate_id})
        # Insert to blockers table
        if gate_id:
            async with self.pg_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO blockers (blocker_id, build_id, gate_id, message, raised_by, raised_at, resolved)
                    VALUES ($1, $2, $3, $4, $5, $6, false)
                """, str(uuid4()), self.build_id, gate_id, message, 
                    self.agent_id, datetime.utcnow())
        log.error("blocker_raised", message=message, agent_id=self.agent_id)

    async def emit_handoff(self, to_agent: str, payload: Dict[str, Any]):
        """Emit handoff to another agent."""
        await self.write_governance_record("HANDOFF",
            payload={"from_agent": self.agent_id, "to_agent": to_agent, "payload": payload})
        log.info("handoff_emitted", to_agent=to_agent, agent_id=self.agent_id)

    async def receive_messages(self, max_messages: int = 10) -> List[Dict[str, Any]]:
        """Receive messages for this agent."""
        async with self.pg_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM messages 
                WHERE to_agent = $1 AND build_id = $2
                ORDER BY timestamp_utc DESC
                LIMIT $3
            """, self.agent_id, self.build_id, max_messages)
        return [dict(row) for row in rows]

    async def write_governance_record(self, event_type: str, payload: Dict[str, Any]):
        """Write governance record."""
        async with self.pg_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO events (event_id, build_id, agent_id, event_type, payload, timestamp_utc)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, str(uuid4()), self.build_id, self.agent_id, event_type, 
                json.dumps(payload), datetime.utcnow())

    async def run(self):
        """Main agent run method - to be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement run()")

    async def stop(self):
        """Stop the agent."""
        self.running = False
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        if self.pg_pool:
            await self.pg_pool.close()
        if self.redis_client:
            self.redis_client.close()
        log.info("agent_stopped", agent_id=self.agent_id)
