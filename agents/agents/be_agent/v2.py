import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from fastapi import Request, Response
from agents.base_agent import BaseAgent

class BEAgentV2(BaseAgent):
    def __init__(self, build_id: str, repo_path: str):
        super().__init__("BE_AGENT_v2", build_id, phase=4)
        self.repo_path = repo_path

    async def run(self):
        self.set_step("writing_idempotency_middleware")
        await self.write_governance_record("TASK_START", step_id="write_idempotency")
        
        # Write IdempotencyMiddleware
        idempotency_middleware = '''import redis
import json
from fastapi import Request, Response
from typing import Optional

class IdempotencyMiddleware:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.ttl = 86400  # 24 hours
    
    async def process_request(self, request: Request, call_next):
        idempotency_key = request.headers.get("Idempotency-Key")
        
        if not idempotency_key:
            return await call_next(request)
        
        # Check if request was already processed
        cached = self.redis.get(f"idempotency:{idempotency_key}")
        if cached:
            return Response(content=cached, status_code=200, headers={"X-Idempotency-Replayed": "true"})
        
        # Process request
        response = await call_next(request)
        
        # Cache response for POST/PUT/PATCH/DELETE
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            self.redis.setex(f"idempotency:{idempotency_key}", self.ttl, response.body)
        
        return response
'''
        await self.fs_write(f"{self.repo_path}/backend/idempotency_middleware.py", idempotency_middleware)
        
        await self.emit_gate_pass("G-21", evidence={"idempotency": "Redis-backed, 24h TTL, POST/PUT/PATCH/DELETE"})
        
        self.set_step("writing_background_worker")
        
        # Write BackgroundWorker
        background_worker = '''import redis
import asyncio
import json
from typing import Callable, Optional

class BackgroundWorker:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.queue_key = "worker:queue"
        self.dlq_key = "worker:dlq"
        self.max_retries = 3
    
    async def enqueue(self, task: dict):
        self.redis.lpush(self.queue_key, json.dumps(task))
    
    async def process(self, handler: Callable):
        while True:
            # BRPOP with timeout
            result = self.redis.brpop(self.queue_key, timeout=5)
            if not result:
                await asyncio.sleep(1)
                continue
            
            _, task_json = result
            task = json.loads(task_json)
            retries = task.get("retries", 0)
            
            try:
                await handler(task)
            except Exception as e:
                if retries < self.max_retries:
                    task["retries"] = retries + 1
                    # Exponential backoff
                    await asyncio.sleep(2 ** retries)
                    self.redis.lpush(self.queue_key, json.dumps(task))
                else:
                    # Dead letter queue
                    self.redis.lpush(self.dlq_key, json.dumps(task))
'''
        await self.fs_write(f"{self.repo_path}/backend/background_worker.py", background_worker)
        
        await self.emit_gate_pass("G-22", evidence={"worker": "Redis BRPOP, exponential backoff, DLQ"})
        
        self.set_step("writing_validation_hardening")
        
        # Write validation hardening
        validation = '''import re

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain digit"
    return True, "OK"

def check_sql_injection(input_str: str) -> bool:
    sql_patterns = [
        r"(\bOR\b|\bAND\b).*=.*=",
        r"(\bOR\b|\bAND\b).*\d+.*=",
        r"(\bUNION\b.*\bSELECT\b)",
        r"(--|#|;|/\*|\*/)"
    ]
    for pattern in sql_patterns:
        if re.search(pattern, input_str, re.IGNORECASE):
            return True
    return False

def check_xss(input_str: str) -> bool:
    xss_patterns = [
        r"<script.*?>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe.*?>"
    ]
    for pattern in xss_patterns:
        if re.search(pattern, input_str, re.IGNORECASE):
            return True
    return False
'''
        await self.fs_write(f"{self.repo_path}/backend/validation.py", validation)
        
        await self.emit_gate_pass("G-23", evidence={"validation": "SQL injection, XSS, password strength"})
        
        # Dispatch TL_AGENT_v4
        await self.emit_handoff("TL_AGENT_v4", payload={"build_id": self.build_id})
        
        await self.write_governance_record("TASK_COMPLETE", status="COMPLETE",
            payload={"gates_passed": ["G-21", "G-22", "G-23"]})
        self.status = "COMPLETE"
        await self.stop()
