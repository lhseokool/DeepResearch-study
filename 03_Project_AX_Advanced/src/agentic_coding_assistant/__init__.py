"""Agentic Coding Assistant for impact analysis and autonomous refactoring."""

from .agents.advanced_coordinator import AdvancedCoordinator
from .agents.coordinator import ImpactAnalysisCoordinator
from .agents.documentation_agent import DocumentationAgent
from .agents.filesystem_agent import FileSystemAgent
from .agents.self_healing_agent import SelfHealingAgent
from .graph import analysis_graph
from .models.schema import (
    AnalysisMode,
    AnalysisRequest,
    AnalysisResult,
    DependencyNode,
    ImpactLevel,
)

__version__ = "0.2.0"

__all__ = [
    # Legacy impact analysis
    "ImpactAnalysisCoordinator",
    "analysis_graph",
    # Advanced agents
    "AdvancedCoordinator",
    "FileSystemAgent",
    "SelfHealingAgent",
    "DocumentationAgent",
    # Models
    "AnalysisMode",
    "AnalysisRequest",
    "AnalysisResult",
    "DependencyNode",
    "ImpactLevel",
]
