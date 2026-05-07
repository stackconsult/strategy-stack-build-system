"""
All Agents Index — 19-Agent Build System
"""
from agents.base_agent import BaseAgent

# Phase 1
from agents.po_agent.v1 import POAgentV1
from agents.tl_agent.v1 import TLAgentV1
from agents.do_agent.v1 import DOAgentV1

# Phase 2
from agents.tl_agent.v2 import TLAgentV2

# Phase 3
from agents.be_agent.v1 import BEAgentV1
from agents.fe_agent.v1 import FEAgentV1
from agents.do_agent.v2 import DOAgentV2
from agents.tl_agent.v3 import TLAgentV3

# Phase 4
from agents.qa_agent.v1 import QAAgentV1
from agents.be_agent.v2 import BEAgentV2
from agents.fe_agent.v2 import FEAgentV2
from agents.tl_agent.v4 import TLAgentV4

# Phase 5
from agents.be_agent.v3 import BEAgentV3
from agents.do_agent.v3 import DOAgentV3
from agents.po_agent.v2 import POAgentV2
from agents.tl_agent.v5 import TLAgentV5

# Phase 6
from agents.do_agent.v4 import DOAgentV4
from agents.qa_agent.v2 import QAAgentV2

ALL_AGENTS = {
    "PO_AGENT_v1": POAgentV1,
    "TL_AGENT_v1": TLAgentV1,
    "DO_AGENT_v1": DOAgentV1,
    "TL_AGENT_v2": TLAgentV2,
    "BE_AGENT_v1": BEAgentV1,
    "FE_AGENT_v1": FEAgentV1,
    "DO_AGENT_v2": DOAgentV2,
    "TL_AGENT_v3": TLAgentV3,
    "QA_AGENT_v1": QAAgentV1,
    "BE_AGENT_v2": BEAgentV2,
    "FE_AGENT_v2": FEAgentV2,
    "TL_AGENT_v4": TLAgentV4,
    "BE_AGENT_v3": BEAgentV3,
    "DO_AGENT_v3": DOAgentV3,
    "PO_AGENT_v2": POAgentV2,
    "TL_AGENT_v5": TLAgentV5,
    "DO_AGENT_v4": DOAgentV4,
    "QA_AGENT_v2": QAAgentV2,
}

def get_agent(agent_name: str):
    """Get agent class by name."""
    return ALL_AGENTS.get(agent_name)
