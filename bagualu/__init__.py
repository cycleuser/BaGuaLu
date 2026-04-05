"""BaGuaLu (八卦炉) - Intelligent Agent Orchestration Platform.

A powerful platform for deploying, orchestrating, and evolving AI agent clusters.
Supports OpenCode/Claude Code skills, multi-provider configuration, and self-evolution.
"""

__version__ = "0.1.5"
__build_time__ = "2026-04-05T00:00:00Z"
__author__ = "BaGuaLu Contributors"
__description__ = "八卦炉 - Intelligent Agent Orchestration Platform"

from bagualu.agents import AgentCluster
from bagualu.config import ConfigManager
from bagualu.core import BaGuaLuCore
from bagualu.skills import SkillEngine

__all__ = [
    "BaGuaLuCore",
    "AgentCluster",
    "SkillEngine",
    "ConfigManager",
    "__version__",
    "__build_time__",
]
