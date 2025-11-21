"""Sub-agents for DeepAgent-based coding assistant.

This module provides sub-agent configurations for specialized tasks:
- Analyzer: Code analysis and impact detection
- Refactorer: Code refactoring with self-healing
- Documenter: Documentation synchronization
"""

from .analyzer import create_analyzer_subagent
from .documenter import create_documenter_subagent
from .refactorer import create_refactorer_subagent

__all__ = [
    "create_analyzer_subagent",
    "create_refactorer_subagent",
    "create_documenter_subagent",
]
