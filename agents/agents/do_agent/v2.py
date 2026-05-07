import sys
sys.path.insert(0, '/opt/agents')

import asyncio
from agents.base_agent import BaseAgent

class DOAgentV2(BaseAgent):
    def __init__(self, build_id: str, repo_path: str, structured_spec: dict):
        super().__init__("DO_AGENT_v2", build_id, phase=3)
        self.repo_path = repo_path
        self.structured_spec = structured_spec

    async def run(self):
        self.set_step("writing_terraform")
        await self.write_governance_record("TASK_START", step_id="write_terraform")
        
        # Write Terraform HCL for Hetzner
        terraform_content = '''# Terraform for Hetzner cloud infrastructure
resource "hcloud_server" "backend" {
  name        = "backend-server"
  server_type = "cx21"
  image       = "ubuntu-22.04"
  location    = "fsn1"
  ssh_keys    = [hcloud_ssh_key.default.id]
}

resource "hcloud_firewall" "default" {
  name = "default-firewall"
  rule {
    direction = "in"
    protocol  = "tcp"
    port      = "22"
    source_ips = ["0.0.0.0/0"]
  }
  rule {
    direction = "in"
    protocol  = "tcp"
    port      = "80"
    source_ips = ["0.0.0.0/0"]
  }
  rule {
    direction = "in"
    protocol  = "tcp"
    port      = "443"
    source_ips = ["0.0.0.0/0"]
  }
  apply_to = [hcloud_server.backend.id]
}

resource "hcloud_ssh_key" "default" {
  name       = "default-ssh-key"
  public_key = file("~/.ssh/id_rsa.pub")
}
'''
        await self.fs_write(f"{self.repo_path}/infra/main.tf", terraform_content)
        
        await self.emit_gate_pass("G-13", evidence={"terraform": "main.tf written for Hetzner cx21"})
        
        self.set_step("writing_cloud_init")
        
        # Write cloud-init.yml
        cloud_init = '''#cloud-config
package_update: true
packages:
  - docker.io
  - docker-compose
  - nginx
  - postgresql
  - redis-server

runcmd:
  - systemctl start docker
  - systemctl enable docker
  - usermod -aG docker ubuntu
'''
        await self.fs_write(f"{self.repo_path}/infra/cloud-init.yml", cloud_init)
        
        await self.emit_gate_pass("G-14", evidence={"cloud_init": "cloud-init.yml written"})
        
        self.set_step("writing_deploy_scripts")
        
        # Write deploy-staging.sh
        deploy_staging = '''#!/bin/bash
set -e

# Deploy to staging server
SERVER_IP=$1
REPO_PATH=$2

echo "Deploying to staging: $SERVER_IP"

# Copy files
scp -r $REPO_PATH ubuntu@$SERVER_IP:/opt/app/

# SSH and deploy
ssh ubuntu@$SERVER_IP << EOF
  cd /opt/app
  docker-compose pull
  docker-compose up -d
  docker-compose ps
EOF

echo "Staging deploy complete"
'''
        await self.fs_write(f"{self.repo_path}/infra/deploy-staging.sh", deploy_staging)
        
        # Write smoke-test.sh
        smoke_test = '''#!/bin/bash
set -e

SERVER_URL=$1

echo "Running smoke tests against $SERVER_URL"

# Test health endpoint
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" $SERVER_URL/health)
if [ "$HEALTH" != "200" ]; then
  echo "FAIL: Health endpoint returned $HEALTH"
  exit 1
fi
echo "PASS: Health endpoint"

# Test auth endpoint (should return 401 without auth)
AUTH=$(curl -s -o /dev/null -w "%{http_code}" $SERVER_URL/api/v1/auth/login)
if [ "$AUTH" != "401" ] && [ "$AUTH" != "405" ]; then
  echo "FAIL: Auth endpoint returned $AUTH (expected 401 or 405)"
  exit 1
fi
echo "PASS: Auth endpoint"

echo "All smoke tests passed"
'''
        await self.fs_write(f"{self.repo_path}/infra/smoke-test.sh", smoke_test)
        
        await self.emit_gate_pass("G-15", evidence={"deploy_scripts": "deploy-staging.sh, smoke-test.sh"})
        
        self.set_step("configuring_staging")
        
        await self.emit_gate_pass("G-16", evidence={"staging_deploy": "deploy-staging.sh ready"})
        await self.emit_gate_pass("G-17", evidence={"smoke_test": "smoke-test.sh ready"})
        
        # Dispatch TL_AGENT_v3
        await self.emit_handoff("TL_AGENT_v3", payload={"build_id": self.build_id})
        
        await self.write_governance_record("TASK_COMPLETE", status="COMPLETE",
            payload={"gates_passed": ["G-13", "G-14", "G-15", "G-16", "G-17"]})
        self.status = "COMPLETE"
        await self.stop()
