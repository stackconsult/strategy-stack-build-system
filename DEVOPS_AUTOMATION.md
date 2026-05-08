# DevOps Automation: 19-Agent Build System
# Wire Specific Flow/Components/Functions to Prevent Drift

## Overview

This document defines the DevOps automation strategy to prevent configuration drift, ensure consistent deployments, and maintain system reliability across environments.

## Infrastructure as Code (IaC)

### Supabase Configuration

**Supabase CLI Setup:**
```bash
# Initialize Supabase in project
cd ~/Desktop/19-agent-workspace
supabase init

# Link to project
supabase link --project-ref asaajoefhifdqhprowek
```

**Database Schema Migration:**
```sql
-- supabase/migrations/001_init_schema.sql
-- This ensures consistent database structure across environments

CREATE TABLE IF NOT EXISTS builds (
    build_id VARCHAR(255) PRIMARY KEY,
    status VARCHAR(50) NOT NULL,
    current_phase INTEGER DEFAULT 1,
    prd_path TEXT,
    metadata JSONB,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS events (
    event_id SERIAL PRIMARY KEY,
    build_id VARCHAR(255) REFERENCES builds(build_id),
    agent_type VARCHAR(100),
    agent_version VARCHAR(50),
    event_type VARCHAR(100),
    event_data JSONB,
    timestamp_utc TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Apply Migrations:**
```bash
# Push to remote
supabase db push

# Verify schema
supabase db diff
```

### Environment Configuration

**.env Template:**
```env
# Database
SUPABASE_PROJECT_REF=asaajoefhifdqhprowek
SUPABASE_DB_PASSWORD=agents_secure_pass_2026
DATABASE_URL=postgresql://postgres:agents_secure_pass_2026@db.asaajoefhifdqhprowek.supabase.co:5432/postgres

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Orchestrator
ORCHESTRATOR_HOST=localhost
ORCHESTRATOR_PORT=8008

# MCP Servers
MCP_FILESYSTEM_PORT=8001
MCP_GIT_PORT=8002
MCP_DATABASE_PORT=8003
MCP_CICD_PORT=8004
MCP_OBSERVABILITY_PORT=8006
MCP_SECRETS_PORT=8007
```

**Environment-Specific Configs:**
```bash
# Development
cp .env.development .env

# Staging
cp .env.staging .env

# Production
cp .env.production .env
```

## CI/CD Pipeline

### GitHub Actions Workflow

**.github/workflows/ci-cd.yml:**
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run tests
        run: pytest --cov=agents --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Supabase CLI
        run: |
          brew install supabase/tap/supabase-beta
      
      - name: Link to project
        run: |
          supabase link --project-ref ${{ secrets.SUPABASE_PROJECT_REF }}
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
      
      - name: Push migrations
        run: supabase db push
        env:
          SUPABASE_DB_PASSWORD: ${{ secrets.SUPABASE_DB_PASSWORD }}
      
      - name: Deploy orchestrator
        run: |
          # Deploy orchestrator to production
          # This would involve restarting services, etc.
```

### Pre-commit Hooks

**.pre-commit-config.yaml:**
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  
  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

**Install hooks:**
```bash
pip install pre-commit
pre-commit install
```

## Service Orchestration

### Systemd Services

**Orchestrator Service:**
```ini
# /etc/systemd/system/orchestrator.service
[Unit]
Description=19-Agent Build Orchestrator
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=kirtissiemens
WorkingDirectory=/Users/kirtissiemens/Desktop/19-agent-workspace
Environment="PATH=/Users/kirtissiemens/Desktop/19-agent-workspace/agents/venv/bin"
ExecStart=/Users/kirtissiemens/Desktop/19-agent-workspace/agents/venv/bin/python -m uvicorn agents.orchestrator.main:app --host 0.0.0.0 --port 8008
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Redis Service:**
```ini
# /usr/local/etc/supervisord.d/redis.conf
[program:redis]
command=/usr/local/bin/redis-server
autostart=true
autorestart=true
stderr_logfile=/var/log/redis.err.log
stdout_logfile=/var/log/redis.out.log
```

**Start Services:**
```bash
# Enable orchestrator
sudo systemctl enable orchestrator
sudo systemctl start orchestrator

# Enable Redis
brew services start redis
```

### Health Checks

**Orchestrator Health Check:**
```python
# agents/orchestrator/health.py
from fastapi import APIRouter, HTTPException
import asyncpg
import redis

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "services": {}
    }
    
    # Check PostgreSQL
    try:
        pool = await asyncpg.create_pool(
            user="postgres",
            password=os.getenv('SUPABASE_DB_PASSWORD'),
            database="postgres",
            host=f"db.{os.getenv('SUPABASE_PROJECT_REF')}.supabase.co",
            port=5432
        )
        async with pool.acquire() as conn:
            await conn.fetchval('SELECT 1')
        status["services"]["database"] = "healthy"
        await pool.close()
    except Exception as e:
        status["services"]["database"] = f"unhealthy: {str(e)}"
        status["status"] = "degraded"
    
    # Check Redis
    try:
        client = redis.Redis(host='localhost', port=6379)
        client.ping()
        status["services"]["redis"] = "healthy"
    except Exception as e:
        status["services"]["redis"] = f"unhealthy: {str(e)}"
        status["status"] = "degraded"
    
    if status["status"] == "degraded":
        raise HTTPException(status_code=503, detail=status)
    
    return status
```

## Monitoring and Observability

### Structured Logging

**Logging Configuration:**
```python
# agents/shared/logging_config.py
import structlog
import logging
import sys

def configure_logging():
    """Configure structured logging"""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO
    )
```

### Metrics Collection

**Prometheus Metrics:**
```python
# agents/shared/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Build metrics
build_counter = Counter('builds_total', 'Total builds')
build_duration = Histogram('build_duration_seconds', 'Build duration')
active_builds = Gauge('active_builds', 'Active builds')

# Agent metrics
agent_counter = Counter('agent_executions_total', 'Total agent executions', ['agent_type'])
agent_duration = Histogram('agent_duration_seconds', 'Agent duration', ['agent_type'])

# Database metrics
db_query_duration = Histogram('db_query_duration_seconds', 'Database query duration')
db_connection_pool = Gauge('db_connection_pool_size', 'Database connection pool size')
```

### Alerting

**Alert Rules:**
```yaml
# alerting/alerts.yml
groups:
  - name: build_system
    rules:
      - alert: HighFailureRate
        expr: rate(build_failures_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High build failure rate"
      
      - alert: DatabaseConnectionPoolExhausted
        expr: db_connection_pool_size < 5
        for: 2m
        annotations:
          summary: "Database connection pool exhausted"
      
      - alert: AgentNotResponding
        expr: agent_heartbeat_seconds > 60
        for: 2m
        annotations:
          summary: "Agent not responding"
```

## Backup and Recovery

### Automated Backups

**Backup Script:**
```bash
#!/bin/bash
# scripts/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/Users/kirtissiemens/Desktop/backups"
BACKUP_FILE="${BACKUP_DIR}/backup_${DATE}.sql"

mkdir -p $BACKUP_DIR

# Backup Supabase database
supabase db dump -f $BACKUP_FILE

# Upload to remote storage (optional)
# rclone copy $BACKUP_FILE remote:backups/

# Keep last 7 days
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
```

**Cron Job:**
```bash
# Add to crontab
0 2 * * * /Users/kirtissiemens/Desktop/19-agent-workspace/scripts/backup.sh
```

### Restore Procedure

**Restore Script:**
```bash
#!/bin/bash
# scripts/restore.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: ./restore.sh <backup-file>"
    exit 1
fi

# Stop services
sudo systemctl stop orchestrator
brew services stop redis

# Restore database
supabase db reset
psql -h localhost -p 54322 -U postgres -d postgres -f $BACKUP_FILE

# Start services
brew services start redis
sudo systemctl start orchestrator

echo "Restore completed"
```

## Configuration Drift Prevention

### Configuration Validation

**Validation Script:**
```python
# scripts/validate_config.py
import os
from dotenv import load_dotenv
import yaml

def validate_config():
    """Validate environment configuration"""
    load_dotenv()
    
    required_vars = [
        'SUPABASE_PROJECT_REF',
        'SUPABASE_DB_PASSWORD',
        'REDIS_HOST',
        'REDIS_PORT',
        'ORCHESTRATOR_PORT'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"Missing required variables: {', '.join(missing)}")
        return False
    
    print("Configuration valid")
    return True

if __name__ == "__main__":
    validate_config()
```

### Schema Drift Detection

**Schema Check:**
```bash
# Compare local vs remote schema
supabase db diff

# If differences exist, alert
if [ $? -ne 0 ]; then
    echo "Schema drift detected!"
    # Send alert (email, Slack, etc.)
fi
```

## Deployment Automation

### Blue-Green Deployment

**Deployment Script:**
```bash
#!/bin/bash
# scripts/deploy.sh

ENVIRONMENT=$1
VERSION=$2

if [ -z "$ENVIRONMENT" ] || [ -z "$VERSION" ]; then
    echo "Usage: ./deploy.sh <environment> <version>"
    exit 1
fi

echo "Deploying version $VERSION to $ENVIRONMENT"

# Run tests
pytest

# Backup current version
./scripts/backup.sh

# Deploy new version
# This would involve:
# 1. Deploy new orchestrator version
# 2. Run database migrations
# 3. Verify health checks
# 4. Switch traffic

# Health check
curl -f http://localhost:8008/health || exit 1

echo "Deployment successful"
```

### Rollback Procedure

**Rollback Script:**
```bash
#!/bin/bash
# scripts/rollback.sh

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "Usage: ./rollback.sh <version>"
    exit 1
fi

echo "Rolling back to version $VERSION"

# Stop current version
sudo systemctl stop orchestrator

# Restore previous version
# This would involve:
# 1. Restore previous orchestrator binary
# 2. Rollback database migrations
# 3. Restart services

# Start previous version
sudo systemctl start orchestrator

# Health check
curl -f http://localhost:8008/health || exit 1

echo "Rollback successful"
```

## Security Automation

### Secrets Management

**Using Supabase Secrets:**
```bash
# Set secrets via Supabase CLI
supabase secrets set DATABASE_PASSWORD=agents_secure_pass_2026

# In code, access via environment
import os
password = os.getenv('DATABASE_PASSWORD')
```

### Security Scanning

**Dependency Scanning:**
```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [main]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run safety check
        run: |
          pip install safety
          safety check -r requirements.txt
      
      - name: Run bandit
        run: |
          pip install bandit
          bandit -r agents/
```

## Documentation Automation

### API Documentation

**Automatic OpenAPI Generation:**
```python
# agents/orchestrator/main.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="19-Agent Build System API",
        version="1.0.0",
        description="API for orchestrating 19-agent build system",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

**Generate Documentation:**
```bash
# Generate OpenAPI spec
curl http://localhost:8008/openapi.json > openapi.json
```

## Summary

This DevOps automation strategy prevents drift by:
1. Using IaC for infrastructure (Supabase CLI)
2. Implementing CI/CD pipelines (GitHub Actions)
3. Adding pre-commit hooks for code quality
4. Using systemd for service management
5. Implementing health checks and monitoring
6. Automating backups and recovery
7. Validating configuration and schema
8. Implementing blue-green deployments
9. Managing secrets securely
10. Automating security scanning

This ensures consistent, reliable deployments across all environments.
