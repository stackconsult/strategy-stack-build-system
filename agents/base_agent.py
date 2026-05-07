"""
Base Agent — all agents inherit from this.
Implements the 5 core methods required by the build system.
"""
import asyncio
import asyncpg
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime
import json
import structlog

log = structlog.get_logger()

class BaseAgent(ABC):
    """Abstract base class for all build agents."""
    
    def __init__(self, agent_id: str, db_url: str):
        self.agent_id = agent_id
        self.db_url = db_url
        self.db_pool: Optional[asyncpg.Pool] = None
    
    async def initialize(self):
        """Initialize database connection pool."""
        self.db_pool = await asyncpg.create_pool(self.db_url, min_size=1, max_size=5)
        log.info("agent_initialized", agent=self.agent_id)
    
    async def cleanup(self):
        """Close database connection pool."""
        if self.db_pool:
            await self.db_pool.close()
            log.info("agent_cleanup", agent=self.agent_id)
    
    @abstractmethod
    async def execute(self, build_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's primary task."""
        pass
    
    async def write_governance_event(self, build_id: str, event_type: str, 
                                     payload: Dict[str, Any]):
        """Write an event to the governance database."""
        if not self.db_pool:
            raise RuntimeError("Agent not initialized")
        
        event_id = f"{self.agent_id}_{event_type}_{int(datetime.utcnow().timestamp())}"
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO events (event_id, build_id, agent_id, event_type, payload)
                   VALUES ($1, $2, $3, $4, $5)""",
                event_id, build_id, self.agent_id, event_type, json.dumps(payload)
            )
        log.info("event_written", agent=self.agent_id, event_type=event_type)
    
    async def write_gate(self, build_id: str, gate_id: str, status: str,
                        evidence: Dict[str, Any]):
        """Write a gate result to the governance database."""
        if not self.db_pool:
            raise RuntimeError("Agent not initialized")
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO gates (gate_id, build_id, status, passed_by, evidence, passed_at)
                   VALUES ($1, $2, $3, $4, $5, NOW())
                   ON CONFLICT (gate_id, build_id) DO UPDATE SET
                   status = $3, passed_by = $4, evidence = $5, passed_at = NOW()""",
                gate_id, build_id, status, self.agent_id, json.dumps(evidence)
            )
        log.info("gate_written", agent=self.agent_id, gate_id=gate_id, status=status)
    
    async def send_message(self, build_id: str, to_agent: str, 
                          message_type: str, payload: Dict[str, Any]):
        """Send a message to another agent."""
        if not self.db_pool:
            raise RuntimeError("Agent not initialized")
        
        message_id = f"{self.agent_id}_to_{to_agent}_{int(datetime.utcnow().timestamp())}"
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO messages (message_id, from_agent, to_agent, message_type, build_id, payload)
                   VALUES ($1, $2, $3, $4, $5, $6)""",
                message_id, self.agent_id, to_agent, message_type, build_id, json.dumps(payload)
            )
        log.info("message_sent", agent=self.agent_id, to_agent=to_agent)
    
    async def read_messages(self, build_id: str) -> list[Dict[str, Any]]:
        """Read unprocessed messages for this agent."""
        if not self.db_pool:
            raise RuntimeError("Agent not initialized")
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT * FROM messages 
                   WHERE build_id = $1 AND to_agent = $2 AND processed = FALSE
                   ORDER BY timestamp_utc""",
                build_id, self.agent_id
            )
            # Mark as processed
            if rows:
                for row in rows:
                    await conn.execute(
                        """UPDATE messages SET processed = TRUE 
                           WHERE message_id = $1""",
                        row['message_id']
                    )
        return [dict(r) for r in rows]
    
    async def write_heartbeat(self, build_id: str, status: str, current_step: str = ""):
        """Write agent heartbeat."""
        if not self.db_pool:
            raise RuntimeError("Agent not initialized")
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO agent_heartbeats (build_id, agent_id, status, current_step, last_heartbeat)
                   VALUES ($1, $2, $3, $4, NOW())
                   ON CONFLICT (agent_id, build_id) DO UPDATE SET
                   status = $3, current_step = $4, last_heartbeat = NOW()""",
                build_id, self.agent_id, status, current_step
            )
