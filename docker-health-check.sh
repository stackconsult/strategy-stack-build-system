#!/bin/bash

# Docker Daemon Health Check Script
# Backend Architect Pattern: Automated Health Verification with Retries

set -e

cd /opt/agents

function docker_health_check() {
    local max_attempts=30
    local attempt=0
    local wait_time=3
    
    echo "Checking Docker daemon health..."
    
    while [ $attempt -lt $max_attempts ]; do
        if docker ps > /dev/null 2>&1; then
            echo "✓ Docker daemon is running"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo "Attempt $attempt/$max_attempts: Docker daemon not ready, waiting ${wait_time}s..."
        sleep $wait_time
    done
    
    echo "✗ Docker daemon failed to start after ${max_attempts} attempts"
    return 1
}

function start_docker_desktop() {
    echo "Starting Docker Desktop..."
    
    # Check if already running
    if pgrep -f "Docker.app" > /dev/null; then
        echo "Docker Desktop is already running"
    else
        open /Applications/Docker.app
        echo "Docker Desktop launched"
    fi
}

function verify_docker_installation() {
    echo "Verifying Docker installation..."
    
    if command -v docker > /dev/null 2>&1; then
        echo "✓ Docker CLI found: $(docker --version)"
    else
        echo "✗ Docker CLI not found"
        return 1
    fi
    
    if [ -d "/Applications/Docker.app" ]; then
        echo "✓ Docker Desktop installed"
    else
        echo "✗ Docker Desktop not found"
        return 1
    fi
}

# Main execution
echo "=== Docker Health Check ==="
echo "Working directory: $(pwd)"
echo ""

verify_docker_installation || exit 1
start_docker_desktop
docker_health_check || exit 1

echo ""
echo "=== Docker Health Check Complete ==="
echo "Docker is ready for container operations"
