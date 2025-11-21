"""Configuration for Agentic Coding Assistant using DeepAgent framework.

This module provides configuration management for the DeepAgent-based coding assistant,
extending the original configuration with DeepAgent-specific parameters.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AnalysisMode(str, Enum):
    """Analysis mode options."""

    SPEED = "speed"
    PRECISION = "precision"
    AUTO = "auto"


class LLMProvider(str, Enum):
    """LLM provider options."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"


class DeepAgentConfiguration(BaseModel):
    """Configuration for DeepAgent-based Agentic Coding Assistant.

    This configuration extends the original settings with DeepAgent-specific
    parameters for dynamic delegation and skill management.
    """

    # Model configuration
    main_model: str = Field(
        default="openai:gpt-4.1",
        description="Main orchestrator model",
    )
    coordinator_model: Optional[str] = Field(
        default=None,
        description="Model for coordinator sub-agent (inherits main_model if None)",
    )
    analyzer_model: Optional[str] = Field(
        default=None,
        description="Model for analyzer sub-agents (inherits main_model if None)",
    )

    # Analysis configuration
    default_analysis_mode: AnalysisMode = Field(
        default=AnalysisMode.AUTO,
        description="Default analysis mode",
    )
    max_analysis_depth: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum depth for impact analysis",
    )

    # DeepAgent-specific configuration
    max_parallel_analyzers: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of parallel analyzers",
    )
    max_coordinator_iterations: int = Field(
        default=10,
        ge=1,
        le=20,
        description="Maximum coordinator iterations before finalization",
    )
    enable_self_healing: bool = Field(
        default=True,
        description="Enable self-healing agent for code generation",
    )
    enable_documentation_sync: bool = Field(
        default=True,
        description="Enable documentation synchronization",
    )

    # Retry configuration
    max_structured_output_retries: int = Field(
        default=3,
        description="Maximum retries for structured output parsing",
    )
    max_healing_retries: int = Field(
        default=3,
        description="Maximum retries for self-healing loop",
    )

    # Backend configuration
    use_persistent_backend: bool = Field(
        default=False,
        description="Use persistent filesystem backend instead of state-based",
    )
    workspace_root: Optional[str] = Field(
        default=None,
        description="Root directory for persistent filesystem backend",
    )

    # Project configuration
    project_root: Optional[str] = Field(
        default=None,
        description="Root directory of the project to analyze",
    )

    @classmethod
    def from_runnable_config(cls, config: dict) -> "DeepAgentConfiguration":
        """Create configuration from LangGraph runnable config.

        Args:
            config: Runtime configuration dictionary

        Returns:
            DeepAgentConfiguration instance
        """
        if config is None:
            config = {}
        configurable = config.get("configurable", {})

        return cls(
            main_model=configurable.get(
                "main_model", cls.model_fields["main_model"].default
            ),
            coordinator_model=configurable.get("coordinator_model"),
            analyzer_model=configurable.get("analyzer_model"),
            default_analysis_mode=configurable.get(
                "default_analysis_mode",
                cls.model_fields["default_analysis_mode"].default,
            ),
            max_parallel_analyzers=configurable.get(
                "max_parallel_analyzers",
                cls.model_fields["max_parallel_analyzers"].default,
            ),
            max_coordinator_iterations=configurable.get(
                "max_coordinator_iterations",
                cls.model_fields["max_coordinator_iterations"].default,
            ),
            enable_self_healing=configurable.get(
                "enable_self_healing",
                cls.model_fields["enable_self_healing"].default,
            ),
            enable_documentation_sync=configurable.get(
                "enable_documentation_sync",
                cls.model_fields["enable_documentation_sync"].default,
            ),
            project_root=configurable.get("project_root"),
        )

    def to_runnable_config(self) -> dict:
        """Convert to LangGraph runnable config format.

        Returns:
            Dictionary suitable for LangGraph config parameter
        """
        return {
            "configurable": {
                "main_model": self.main_model,
                "coordinator_model": self.coordinator_model,
                "analyzer_model": self.analyzer_model,
                "default_analysis_mode": self.default_analysis_mode.value,
                "max_parallel_analyzers": self.max_parallel_analyzers,
                "max_coordinator_iterations": self.max_coordinator_iterations,
                "enable_self_healing": self.enable_self_healing,
                "enable_documentation_sync": self.enable_documentation_sync,
                "project_root": self.project_root,
            }
        }


# Default configuration instance
DEFAULT_CONFIG = DeepAgentConfiguration()
