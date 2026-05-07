import sys
sys.path.insert(0, '/opt/agents')
from mcp_servers.base_mcp import make_mcp_app
app = make_mcp_app("cicd_mcp", 8003)
