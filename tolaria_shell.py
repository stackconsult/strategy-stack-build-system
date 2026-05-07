"""
Tolaria Operator Shell — Interactive command interface for the build system.
Provides commands to run builds, check status, and manage agents.
"""
import sys
import asyncio
import argparse
sys.path.insert(0, '/opt/agents')
from agents import ALL_AGENTS
import asyncpg

class TolariaShell:
    """Tolaria Operator Shell"""
    
    def __init__(self):
        self.db_url = "postgresql://agents_user:agents_secure_pass_2026@localhost/governance_db"
    
    async def run_build(self, build_id: str):
        """Run a full build through all phases."""
        print(f"Starting build: {build_id}")
        
        # Initialize build in database
        async with asyncpg.create_pool(self.db_url, min_size=1, max_size=5) as pool:
            async with pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO builds (build_id, status, current_phase) VALUES ($1, 'RUNNING', 1)",
                    build_id
                )
            
            # Run agents sequentially by phase
            phases = [
                ["PO_AGENT_v1", "TL_AGENT_v1", "DO_AGENT_v1"],
                ["TL_AGENT_v2"],
                ["BE_AGENT_v1", "FE_AGENT_v1", "DO_AGENT_v2", "TL_AGENT_v3"],
                ["QA_AGENT_v1", "BE_AGENT_v2", "FE_AGENT_v2", "TL_AGENT_v4"],
                ["BE_AGENT_v3", "DO_AGENT_v3", "PO_AGENT_v2", "TL_AGENT_v5"],
                ["DO_AGENT_v4", "QA_AGENT_v2"],
            ]
            
            for phase_idx, phase_agents in enumerate(phases, 1):
                print(f"\n=== Phase {phase_idx} ===")
                for agent_name in phase_agents:
                    agent_class = ALL_AGENTS.get(agent_name)
                    if agent_class:
                        agent = agent_class()
                        agent.db_pool = pool
                        try:
                            # Provide context for agents that need it
                            context = {}
                            if agent_name == "PO_AGENT_v1":
                                context = {"prd_path": "/opt/agents/specs/sample_prd.md"}
                            result = await agent.execute(build_id, context)
                            print(f"✅ {agent_name}: {result['status']}")
                        except Exception as e:
                            print(f"❌ {agent_name}: FAILED - {e}")
                            return False
            
            # Mark build as complete
            async with pool.acquire() as conn:
                await conn.execute(
                    "UPDATE builds SET status = 'COMPLETE', completed_at = NOW() WHERE build_id = $1",
                    build_id
                )
        
        print(f"\n✅ Build {build_id} COMPLETE")
        return True
    
    async def check_status(self, build_id: str):
        """Check build status."""
        async with asyncpg.create_pool(self.db_url, min_size=1, max_size=5) as pool:
            async with pool.acquire() as conn:
                build = await conn.fetchrow("SELECT * FROM builds WHERE build_id = $1", build_id)
                
                if not build:
                    print(f"Build {build_id} not found")
                    return
                
                print(f"Build ID: {build['build_id']}")
                print(f"Status: {build['status']}")
                print(f"Phase: {build['current_phase']}")
                print(f"Created: {build.get('created_at', 'N/A')}")
                if build.get('completed_at'):
                    print(f"Completed: {build['completed_at']}")
                
                # Show gates
                gates = await conn.fetch("SELECT * FROM gates WHERE build_id = $1 ORDER BY passed_at", build_id)
                print(f"\nGates ({len(gates)}):")
                for gate in gates:
                    print(f"  {gate['gate_id']}: {gate['status']} (by {gate['passed_by']})")
    
    async def list_agents(self):
        """List all available agents."""
        print("Available Agents:")
        for agent_name in ALL_AGENTS.keys():
            print(f"  {agent_name}")
    
    async def run_validation(self):
        """Run validation harness."""
        print("Running validation harness...")
        import subprocess
        result = subprocess.run([sys.executable, "/opt/agents/validation_harness.py"])
        return result.returncode == 0

async def main():
    parser = argparse.ArgumentParser(description="Tolaria Operator Shell")
    parser.add_argument("command", choices=["run", "status", "agents", "validate"], help="Command to run")
    parser.add_argument("--build-id", help="Build ID")
    
    args = parser.parse_args()
    
    shell = TolariaShell()
    
    if args.command == "run":
        if not args.build_id:
            print("Error: --build-id required for run command")
            sys.exit(1)
        success = await shell.run_build(args.build_id)
        sys.exit(0 if success else 1)
    
    elif args.command == "status":
        if not args.build_id:
            print("Error: --build-id required for status command")
            sys.exit(1)
        await shell.check_status(args.build_id)
    
    elif args.command == "agents":
        await shell.list_agents()
    
    elif args.command == "validate":
        success = await shell.run_validation()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
