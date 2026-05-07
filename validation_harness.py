"""
Validation Harness — Pre-Tolaria System Validation
Runs all agent tests and infrastructure checks.
"""
import sys
import asyncio
sys.path.insert(0, '/opt/agents')
from agents import ALL_AGENTS
import asyncpg

async def validate_infrastructure():
    """Validate PostgreSQL and Redis connectivity."""
    print("=== INFRASTRUCTURE VALIDATION ===")
    
    # Test PostgreSQL
    try:
        conn = await asyncpg.connect("postgresql://agents_user:agents_secure_pass_2026@localhost/governance_db")
        await conn.execute("SELECT 1")
        await conn.close()
        print("✅ PostgreSQL: CONNECTED")
    except Exception as e:
        print(f"❌ PostgreSQL: FAILED - {e}")
        return False
    
    # Test Redis
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis: CONNECTED")
    except Exception as e:
        print(f"❌ Redis: FAILED - {e}")
        return False
    
    # Test Orchestrator (check port 8008)
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 8008))
        sock.close()
        if result == 0:
            print("✅ Orchestrator: RUNNING (port 8008)")
        else:
            print("❌ Orchestrator: NOT RUNNING (port 8008)")
            return False
    except Exception as e:
        print(f"❌ Orchestrator: FAILED - {e}")
        return False
    
    return True

async def validate_agents():
    """Validate all agents can be instantiated."""
    print("\n=== AGENT VALIDATION ===")
    
    for agent_name, agent_class in ALL_AGENTS.items():
        try:
            agent = agent_class()
            print(f"✅ {agent_name}: INSTANTIABLE")
        except Exception as e:
            print(f"❌ {agent_name}: FAILED - {e}")
            return False
    
    return True

async def run_agent_tests():
    """Run all agent tests."""
    print("\n=== AGENT TESTS ===")
    
    test_files = [
        ("PO_AGENT_v1", "/opt/agents/agents/po_agent/test_v1.py"),
        ("TL_AGENT_v1", "/opt/agents/agents/tl_agent/test_v1.py"),
        ("DO_AGENT_v1", "/opt/agents/agents/do_agent/test_v1.py"),
        ("TL_AGENT_v2", "/opt/agents/agents/tl_agent/test_v2.py"),
        ("BE_AGENT_v1", "/opt/agents/agents/be_agent/test_v1.py"),
        ("FE_AGENT_v1", "/opt/agents/agents/fe_agent/test_v1.py"),
        ("DO_AGENT_v2", "/opt/agents/agents/do_agent/test_v2.py"),
        ("TL_AGENT_v3", "/opt/agents/agents/tl_agent/test_v3.py"),
        ("QA_AGENT_v1", "/opt/agents/agents/qa_agent/test_v1.py"),
        ("BE_AGENT_v2", "/opt/agents/agents/be_agent/test_v2.py"),
        ("FE_AGENT_v2", "/opt/agents/agents/fe_agent/test_v2.py"),
        ("TL_AGENT_v4", "/opt/agents/agents/tl_agent/test_v4.py"),
        ("BE_AGENT_v3", "/opt/agents/agents/be_agent/test_v3.py"),
        ("DO_AGENT_v3", "/opt/agents/agents/do_agent/test_v3.py"),
        ("PO_AGENT_v2", "/opt/agents/agents/po_agent/test_v2.py"),
        ("TL_AGENT_v5", "/opt/agents/agents/tl_agent/test_v5.py"),
        ("DO_AGENT_v4", "/opt/agents/agents/do_agent/test_v4.py"),
        ("QA_AGENT_v2", "/opt/agents/agents/qa_agent/test_v2.py"),
    ]
    
    passed = 0
    failed = 0
    
    for agent_name, test_file in test_files:
        try:
            result = await asyncio.create_subprocess_exec(
                sys.executable, test_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                print(f"✅ {agent_name}: TEST PASS")
                passed += 1
            else:
                print(f"❌ {agent_name}: TEST FAIL")
                failed += 1
        except Exception as e:
            print(f"❌ {agent_name}: TEST ERROR - {e}")
            failed += 1
    
    print(f"\n=== TEST SUMMARY ===")
    print(f"Passed: {passed}/{len(test_files)}")
    print(f"Failed: {failed}/{len(test_files)}")
    
    return failed == 0

async def main():
    print("=" * 50)
    print("PRE-TOLARIA VALIDATION HARNESS")
    print("=" * 50)
    
    # Validate infrastructure
    infra_ok = await validate_infrastructure()
    
    # Validate agents
    agents_ok = await validate_agents()
    
    # Run agent tests
    tests_ok = await run_agent_tests()
    
    print("\n" + "=" * 50)
    if infra_ok and agents_ok and tests_ok:
        print("✅ VALIDATION COMPLETE: ALL CHECKS PASS")
        print("=" * 50)
        return 0
    else:
        print("❌ VALIDATION FAILED: SOME CHECKS FAILED")
        print("=" * 50)
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
