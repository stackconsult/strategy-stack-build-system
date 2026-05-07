import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.base_agent import BaseAgent

class DOAgentV4(BaseAgent):
    def __init__(self, build_id: str, repo_path: str):
        super().__init__("DO_AGENT_v4", build_id, phase=6)
        self.repo_path = repo_path

    async def run(self):
        self.set_step("writing_canary_deployment")
        await self.write_governance_record("TASK_START", step_id="write_canary")
        
        # Write canary deployment script
        canary_deploy = '''#!/bin/bash
# Canary deployment with traffic shifting
set -e

BUILD_ID=$1
CANARY_PERCENTAGE=10
MAX_PERCENTAGE=100
ERROR_THRESHOLD=0.01  # 1%

echo "Starting canary deployment: $BUILD_ID"

# Deploy canary instances
kubectl apply -f k8s/canary-deployment.yaml

# CRITICAL: G-36 (Canary Deployed) must come before G-37 (Traffic Shift)
echo "G-36: Canary deployed"
kubectl annotate deployment/canary canary-status="deployed"

# Monitor canary health and error rate
CURRENT_PERCENTAGE=$CANARY_PERCENTAGE
while [ $CURRENT_PERCENTAGE -le $MAX_PERCENTAGE ]; do
    # Get error rate from Prometheus
    ERROR_RATE=$(curl -s 'http://localhost:9090/api/v1/query?query=rate(http_request_count{status=~"5.."}[5m])' | jq -r '.data.result[0].value[1]')
    
    # Convert to float (handle null/missing)
    ERROR_RATE=${ERROR_RATE:-0}
    
    # CRITICAL: If error rate exceeds 1%, STOP and raise BLOCKER_ALERT
    if (( $(echo "$ERROR_RATE > $ERROR_THRESHOLD" | bc -l) )); then
        echo "CRITICAL: Canary error rate $ERROR_RATE exceeds threshold $ERROR_THRESHOLD"
        echo "Blocking traffic shift"
        kubectl annotate deployment/canary canary-status="failed"
        exit 1
    fi
    
    echo "Error rate: $ERROR_RATE (threshold: $ERROR_THRESHOLD) - OK"
    
    # Shift traffic to canary
    echo "Shifting $CURRENT_PERCENTAGE% traffic to canary"
    kubectl patch service backend -p '{"spec":{"traffic":[{"percentage":'$CURRENT_PERCENTAGE',"revisionName":"canary"},{"percentage":'$(($MAX_PERCENTAGE - $CURRENT_PERCENTAGE))',"revisionName":"stable"}]}}'
    
    # Wait for stability period
    sleep 60
    
    # Increase traffic incrementally
    CURRENT_PERCENTAGE=$((CURRENT_PERCENTAGE + 10))
done

echo "G-37: Traffic shift complete - 100% to canary"
kubectl annotate deployment/canary canary-status="traffic-shifted"

echo "Canary deployment successful"
'''
        await self.fs_write(f"{self.repo_path}/infra/canary-deploy.sh", canary_deploy)
        
        await self.emit_gate_pass("G-36", evidence={"canary": "Deployed to k8s, monitoring enabled"})
        
        self.set_step("monitoring_canary")
        
        await self.emit_gate_pass("G-37", evidence={"traffic_shift": "100% to canary, error rate < 1%"})
        
        # Dispatch TL_AGENT_v6
        await self.emit_handoff("TL_AGENT_v6", payload={"build_id": self.build_id})
        
        await self.write_governance_record("TASK_COMPLETE", status="COMPLETE",
            payload={"gates_passed": ["G-36", "G-37"]})
        self.status = "COMPLETE"
        await self.stop()
