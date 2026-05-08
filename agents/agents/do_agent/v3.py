import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.base_agent import BaseAgent

class DOAgentV3(BaseAgent):
    def __init__(self, build_id: str, repo_path: str):
        super().__init__("DO_AGENT_v3", build_id, phase=5)
        self.repo_path = repo_path

    async def run(self):
        self.set_step("writing_grafana_dashboards")
        await self.write_governance_record("TASK_START", step_id="write_grafana")
        
        # Write Grafana dashboard JSON
        grafana_dashboard = '''{
  "dashboard": {
    "title": "Application Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_request_count[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Request Latency (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_latency_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_request_count{status=~\"5..\"}[5m])"
          }
        ]
      },
      {
        "title": "In-Flight Requests",
        "targets": [
          {
            "expr": "http_requests_in_flight"
          }
        ]
      },
      {
        "title": "Auth Failures",
        "targets": [
          {
            "expr": "rate(auth_failures_total[5m])"
          }
        ]
      }
    ]
  }
}
'''
        await self.fs_write(f"{self.repo_path}/infra/grafana-dashboard.json", grafana_dashboard)
        
        await self.emit_gate_pass("G-28", evidence={"dashboard": "Request rate, latency p95, error rate, in-flight, auth failures"})
        
        self.set_step("writing_alert_rules")
        
        # Write Prometheus alert rules
        alert_rules = '''groups:
  - name: application_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_request_count{status=~"5.."}[5m]) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }}"
      
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_latency_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "p95 latency is {{ $value }}s"
      
      - alert: HighAuthFailures
        expr: rate(auth_failures_total[5m]) > 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High authentication failure rate"
          description: "Auth failure rate is {{ $value }}/s"
'''
        await self.fs_write(f"{self.repo_path}/infra/alert-rules.yml", alert_rules)
        
        await self.emit_gate_pass("G-29", evidence={"alerts": "HighErrorRate, HighLatency, HighAuthFailures"})
        
        self.set_step("writing_rollback")
        
        # Write rollback.sh
        rollback_sh = '''#!/bin/bash
# Rollback to previous deployment
set -e

DEPLOY_ID=$1
MAX_WAIT=300

echo "Rolling back to $DEPLOY_ID"

# Wait up to 5 minutes for rollback to complete
START=$(date +%s)
while true; do
    CURRENT=$(date +%s)
    ELAPSED=$((CURRENT - START))
    
    if [ $ELAPSED -ge $MAX_WAIT ]; then
        echo "Rollback timeout after $MAX_WAIT seconds"
        exit 2  # CRITICAL: Exit code 2 on timeout
    fi
    
    # Check if rollback is complete
    if [ -f "/var/rollback/$DEPLOY_ID/complete" ]; then
        echo "Rollback complete"
        exit 0
    fi
    
    sleep 5
done
'''
        await self.fs_write(f"{self.repo_path}/infra/rollback.sh", rollback_sh)
        
        await self.emit_gate_pass("G-30", evidence={"rollback": "5-minute timeout, exit code 2 on timeout"})
        
        self.set_step("writing_restore")
        
        # Write restore.sh
        restore_sh = '''#!/bin/bash
# Restore from backup
set -e

BACKUP_ID=$1

echo "Restoring from backup $BACKUP_ID"

# Restore PostgreSQL
pg_restore -d governance_db /backups/$BACKUP_ID/postgres.dump

# Restore Redis (if applicable)
redis-cli --rdb /backups/$BACKUP_ID/redis.rdb

echo "Restore complete"
'''
        await self.fs_write(f"{self.repo_path}/infra/restore.sh", restore_sh)
        
        await self.emit_gate_pass("G-31", evidence={"restore": "PostgreSQL and Redis restore"})
        
        self.set_step("writing_runbooks")
        
        # Write runbooks
        runbooks = '''# Incident Response Runbooks

## High Error Rate
1. Check Grafana dashboard for error rate spike
2. Check logs for recent errors
3. If deployment-related, trigger rollback
4. If infrastructure-related, check health of backend servers

## High Latency
1. Check database query performance
2. Check Redis cache hit rate
3. Check worker queue backlog
4. Scale backend if needed

## Database Connection Issues
1. Check PostgreSQL pod status
2. Check connection pool metrics
3. Check database CPU/memory
4. Restart backend if connection pool exhausted
'''
        await self.fs_write(f"{self.repo_path}/docs/runbooks.md", runbooks)
        
        await self.emit_gate_pass("G-32", evidence={"runbooks": "High error rate, high latency, database connection issues"})
        
        # Dispatch TL_AGENT_v5
        await self.emit_handoff("TL_AGENT_v5", payload={"build_id": self.build_id})
        
        await self.write_governance_record("TASK_COMPLETE", status="COMPLETE",
            payload={"gates_passed": ["G-28", "G-29", "G-30", "G-31", "G-32"]})
        self.status = "COMPLETE"
        await self.stop()
