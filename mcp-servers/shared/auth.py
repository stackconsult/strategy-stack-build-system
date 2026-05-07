"""
Authentication and authorization for MCP servers.
"""
import os
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path

VAULT_ROOT = Path(os.getenv("VAULT_PATH", "/opt/agents"))

def verify_agent_token(token: str, agent_id: str) -> bool:
    """
    Verify that an agent token is valid for the given agent_id.
    In production, this would check against a secrets store.
    """
    # Simple token format: agent_id:hmac
    # In production, use proper JWT or mTLS
    expected_prefix = f"{agent_id}:"
    if not token.startswith(expected_prefix):
        return False
    
    # Verify HMAC with shared secret
    secret = os.getenv("AGENT_SHARED_SECRET", "dev-secret-change-in-prod")
    payload = token[len(expected_prefix):]
    expected_hmac = hmac.new(
        secret.encode(),
        agent_id.encode(),
        hashlib.sha256
    ).hexdigest()[:16]
    
    return hmac.compare_digest(payload, expected_hmac)

def generate_agent_token(agent_id: str) -> str:
    """Generate a token for an agent."""
    secret = os.getenv("AGENT_SHARED_SECRET", "dev-secret-change-in-prod")
    token_hmac = hmac.new(
        secret.encode(),
        agent_id.encode(),
        hashlib.sha256
    ).hexdigest()[:16]
    return f"{agent_id}:{token_hmac}"

def verify_mcp_access(agent_id: str, mcp_name: str, action: str) -> bool:
    """
    Verify that an agent has access to a specific MCP server action.
    
    Access control matrix:
    - ORCHESTRATOR_AGENT: all MCPs, all actions
    - PO agents: filesystem (read), communication (write)
    - TL agents: all MCPs (read), communication (write)
    - BE agents: filesystem (write), git (write), cicd (read), database (write)
    - FE agents: filesystem (write), git (write)
    - DO agents: filesystem (write), cicd (write), secrets (read), database (write)
    - QA agents: filesystem (read), observability (read), communication (write)
    """
    # ORCHESTRATOR has full access
    if agent_id == "ORCHESTRATOR_AGENT":
        return True
    
    # Parse agent type from agent_id (e.g., "PO_AGENT_v1" -> "PO")
    agent_type = agent_id.split("_")[0]
    
    # Define access matrix
    access_matrix = {
        "ORCHESTRATOR": {
            "filesystem_mcp": ["read", "write", "list", "append"],
            "git_mcp": ["clone", "branch", "commit", "pr"],
            "cicd_mcp": ["trigger", "monitor", "status"],
            "secrets_mcp": ["get", "set", "list"],
            "database_mcp": ["read", "write", "migrate"],
            "observability_mcp": ["query", "trace", "alert"],
            "communication_mcp": ["slack", "pagerduty", "email"],
        },
        "PO": {
            "filesystem_mcp": ["read", "list"],
            "communication_mcp": ["slack", "email"],
        },
        "TL": {
            "filesystem_mcp": ["read", "list"],
            "git_mcp": ["read", "status"],
            "cicd_mcp": ["read", "status"],
            "database_mcp": ["read"],
            "communication_mcp": ["slack", "email"],
        },
        "BE": {
            "filesystem_mcp": ["read", "write", "list"],
            "git_mcp": ["read", "write", "commit"],
            "cicd_mcp": ["read", "status"],
            "database_mcp": ["read", "write"],
            "secrets_mcp": ["get"],
        },
        "FE": {
            "filesystem_mcp": ["read", "write", "list"],
            "git_mcp": ["read", "write", "commit"],
        },
        "DO": {
            "filesystem_mcp": ["read", "write", "list"],
            "cicd_mcp": ["read", "write", "trigger", "monitor"],
            "secrets_mcp": ["get"],
            "database_mcp": ["read", "write"],
            "git_mcp": ["read", "clone"],
        },
        "QA": {
            "filesystem_mcp": ["read", "list"],
            "observability_mcp": ["query", "trace"],
            "communication_mcp": ["slack", "pagerduty"],
            "git_mcp": ["read", "status"],
        },
    }
    
    # Check if agent type has access to this MCP
    agent_perms = access_matrix.get(agent_type, {})
    mcp_perms = agent_perms.get(mcp_name, [])
    
    return action in mcp_perms

def verify_path_within_scope(path: str, build_id: str) -> bool:
    """
    Verify that a file path is within the allowed scope for a build.
    Paths must be within /opt/agents/builds/[BUILD_ID]/ or shared system paths.
    """
    try:
        requested = Path(path).resolve()
        allowed_build = (VAULT_ROOT / "builds" / build_id).resolve()
        allowed_shared = VAULT_ROOT.resolve()
        
        # Check if path is within build directory or shared system paths
        return (
            str(requested).startswith(str(allowed_build)) or
            str(requested).startswith(str(allowed_shared / "shared")) or
            str(requested).startswith(str(allowed_shared / "mcp-servers"))
        )
    except Exception:
        return False

def sanitize_path(path: str) -> Optional[str]:
    """
    Sanitize a file path to prevent directory traversal attacks.
    Returns None if path is unsafe.
    """
    # Remove null bytes
    path = path.replace('\x00', '')
    
    # Check for path traversal patterns
    dangerous_patterns = ['..', '~', '//', '\\']
    for pattern in dangerous_patterns:
        if pattern in path:
            return None
    
    # Normalize path
    try:
        normalized = Path(path).resolve()
        return str(normalized)
    except Exception:
        return None

class AuthContext:
    """Context for an authenticated request."""
    
    def __init__(self, agent_id: str, token: str, build_id: str):
        self.agent_id = agent_id
        self.token = token
        self.build_id = build_id
        self.authenticated = False
        self.authorized_mcp = set()
        
    def authenticate(self) -> bool:
        """Authenticate the agent."""
        self.authenticated = verify_agent_token(self.token, self.agent_id)
        return self.authenticated
    
    def authorize(self, mcp_name: str, action: str) -> bool:
        """Check if agent is authorized for this MCP action."""
        if not self.authenticated:
            return False
        return verify_mcp_access(self.agent_id, mcp_name, action)
    
    def verify_path(self, path: str) -> bool:
        """Verify path is within allowed scope."""
        if not self.authenticated:
            return False
        return verify_path_within_scope(path, self.build_id)


def create_auth_context(agent_id: str, token: str, build_id: str) -> AuthContext:
    """Create and return an authentication context."""
    return AuthContext(agent_id, token, build_id)
