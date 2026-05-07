#!/bin/bash
source /opt/agents/venv/bin/activate
python3 -c "import sys; sys.path.insert(0, '/opt/agents'); from agents import ALL_AGENTS; import asyncio; agent = ALL_AGENTS['QA_AGENT_v1'](); print(f'QA_AGENT_v1: INSTANTIABLE')"
