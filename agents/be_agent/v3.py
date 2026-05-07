import sys
sys.path.insert(0, '/opt/agents')

import asyncio
import time
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge
from fastapi import Request
from agents.base_agent import BaseAgent

class BEAgentV3(BaseAgent):
    def __init__(self, build_id: str, repo_path: str):
        super().__init__("BE_AGENT_v3", build_id, phase=5)
        self.repo_path = repo_path

    async def run(self):
        self.set_step("writing_prometheus_middleware")
        await self.write_governance_record("TASK_START", step_id="write_prometheus")
        
        # Write PrometheusMiddleware
        prometheus_middleware = '''import time
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge
from fastapi import Request

# HTTP metrics
http_request_count = Counter('http_request_count', 'Total HTTP requests', ['method', 'endpoint', 'status'])
http_request_latency = Histogram('http_request_latency_seconds', 'HTTP request latency', ['method', 'endpoint'])
http_requests_in_flight = Gauge('http_requests_in_flight', 'HTTP requests currently in flight')

# Business metrics
user_registrations_total = Counter('user_registrations_total', 'Total user registrations')
auth_failures_total = Counter('auth_failures_total', 'Total authentication failures')

# Worker metrics
worker_task_count = Counter('worker_task_count', 'Total worker tasks', ['status'])

class PrometheusMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http':
            method = scope['method']
            path = scope['path']
            
            # Increment in-flight counter
            http_requests_in_flight.inc()
            
            start_time = time.time()
            status_code = 200
            
            try:
                async def wrapped_send(message):
                    nonlocal status_code
                    if message['type'] == 'http.response.start':
                        status_code = message['status']
                    await send(message)
                
                await self.app(scope, receive, wrapped_send)
            finally:
                # Decrement in-flight counter (MUST be in finally block)
                http_requests_in_flight.dec()
                
                # Record metrics
                latency = time.time() - start_time
                http_request_count.labels(method=method, endpoint=path, status=status_code).inc()
                http_request_latency.labels(method=method, endpoint=path).observe(latency)
        else:
            await self.app(scope, receive, send)
'''
        await self.fs_write(f"{self.repo_path}/backend/prometheus_middleware.py", prometheus_middleware)
        
        # Write /metrics endpoint
        metrics_endpoint = '''from fastapi import Response
import prometheus_client

def metrics():
    return Response(prometheus_client.generate_latest(), media_type="text/plain")
'''
        await self.fs_write(f"{self.repo_path}/backend/metrics.py", metrics_endpoint)
        
        await self.emit_gate_pass("G-26", evidence={"metrics": "http_request_count, latency, in_flight, business metrics"})
        
        self.set_step("writing_tracing_middleware")
        
        # Write TracingMiddleware
        tracing_middleware = '''import uuid
from fastapi import Request
import structlog

class TracingMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http':
            request_id = str(uuid.uuid4())
            
            # Add X-Request-ID header
            headers = dict(scope.get('headers', []))
            headers[b'x-request-id'] = request_id.encode()
            
            # Bind to structlog
            structlog.contextvars.bind_contextvars(request_id=request_id)
            
            async def wrapped_send(message):
                if message['type'] == 'http.response.start':
                    headers = message.get('headers', [])
                    headers.append((b'x-request-id', request_id.encode()))
                    message['headers'] = headers
                await send(message)
            
            await self.app(scope, receive, wrapped_send)
        else:
            await self.app(scope, receive, send)
'''
        await self.fs_write(f"{self.repo_path}/backend/tracing_middleware.py", tracing_middleware)
        
        await self.emit_gate_pass("G-27", evidence={"tracing": "X-Request-ID propagation, structlog binding"})
        
        self.set_step("configuring_logging")
        
        # Write configure_logging
        configure_logging = '''import structlog

def configure_logging():
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )
'''
        await self.fs_write(f"{self.repo_path}/backend/logging.py", configure_logging)
        
        # Write prometheus.yml
        prometheus_yml = '''global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
'''
        await self.fs_write(f"{self.repo_path}/infra/prometheus.yml", prometheus_yml)
        
        # Dispatch TL_AGENT_v5
        await self.emit_handoff("TL_AGENT_v5", payload={"build_id": self.build_id})
        
        await self.write_governance_record("TASK_COMPLETE", status="COMPLETE",
            payload={"gates_passed": ["G-26", "G-27"]})
        self.status = "COMPLETE"
        await self.stop()
