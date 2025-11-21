"""Skills management for Agentic Coding Assistant.

This module manages the mapping between abstract skills and concrete tools.
"""

from .registry import SkillRegistry, registry
from .tool_collections import get_analysis_tools, get_refactoring_tools

__all__ = [
    "SkillRegistry",
    "registry",
    "get_analysis_tools",
    "get_refactoring_tools",
]
