import os
from dataclasses import dataclass

@dataclass
class MCPConfig:
  filesystem_url: str = os.getenv("MCP_FILESYSTEM_URL", "http://127.0.0.1:8001")
  git_url: str = os.getenv("MCP_GIT_URL", "http://127.0.0.1:8002")
  cicd_url: str = os.getenv("MCP_CICD_URL", "http://127.0.0.1:8003")
  secrets_url: str = os.getenv("MCP_SECRETS_URL", "http://127.0.0.1:8004")
  database_url: str = os.getenv("MCP_DATABASE_URL", "http://127.0.0.1:8005")
  observability_url: str = os.getenv("MCP_OBSERVABILITY_URL", "http://127.0.0.1:8006")
  communication_url: str = os.getenv("MCP_COMMUNICATION_URL", "http://127.0.0.1:8007")

@dataclass
class OrchestratorConfig:
  watchdog_interval_seconds: int = int(os.getenv("WATCHDOG_INTERVAL", "60"))
  ack_timeout_normal: int = int(os.getenv("ACK_TIMEOUT_NORMAL", "300"))
  ack_timeout_critical: int = int(os.getenv("ACK_TIMEOUT_CRITICAL", "60"))
  max_retries: int = 3
  circuit_breaker_threshold: int = 3
  stall_threshold_minutes: int = int(os.getenv("STALL_THRESHOLD_MINUTES", "30"))
  escalation_threshold_minutes: int = 60
  max_concurrent_builds: int = int(os.getenv("MAX_CONCURRENT_BUILDS", "3"))
  builds_dir: str = os.getenv("BUILDS_DIR", "/Volumes/STORE N GO/builds")
  agents_dir: str = os.getenv("AGENTS_DIR", "/opt/agents")

@dataclass
class DatabaseConfig:
  postgres_url: str = os.getenv(
    "POSTGRES_URL",
    "postgresql://stackagent@localhost/build_registry")
  redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

MCP = MCPConfig()
ORCH = OrchestratorConfig()
DB = DatabaseConfig()
