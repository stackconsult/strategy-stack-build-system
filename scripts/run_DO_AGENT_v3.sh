#!/bin/bash
source /opt/agents/venv/bin/activate
python3 -c "import sys; sys.path.insert(0, '/opt/agents'); from agents import ALL_AGENTS; import asyncio; agent = ALL_AGENTS['DO_AGENT_v3'](); print(f'DO_AGENT_v3: INSTANTIABLE')"
