import sys
sys.path.insert(0, '/opt/agents')
from mcp_servers.base_mcp import make_mcp_app
app = make_mcp_app("observability_mcp", 8006)
