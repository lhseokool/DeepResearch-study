"""Schema definitions for analysis requests and results."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AnalysisMode(str, Enum):
    """Analysis mode selection."""

    SPEED = "SPEED"
    PRECISION = "PRECISION"


class ImpactLevel(str, Enum):
    """Impact criticality level."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class DependencyNode(BaseModel):
    """Represents a code dependency node."""

    file_path: str = Field(..., description="File path of the node")
    symbol_name: str = Field(..., description="Symbol name (function, class, etc.)")
    line_number: int | None = Field(None, description="Line number in the file")
    node_type: str = Field(..., description="Type of node (function, class, variable)")
    impact_level: ImpactLevel = Field(
        ImpactLevel.MEDIUM, description="Impact criticality"
    )


class AnalysisRequest(BaseModel):
    """Request for impact analysis."""

    mode: AnalysisMode = Field(
        AnalysisMode.SPEED, description="Analysis mode (SPEED or PRECISION)"
    )
    file_path: str = Field(..., description="Path to the file to analyze")
    symbol_name: str = Field(..., description="Symbol name to analyze")
    project_root: str | None = Field(
        None, description="Project root directory (for LSP)"
    )
    max_depth: int = Field(3, description="Maximum dependency depth to traverse")


class AnalysisResult(BaseModel):
    """Result of impact analysis."""

    mode: AnalysisMode = Field(..., description="Mode used for analysis")
    success: bool = Field(..., description="Whether analysis succeeded")
    dependencies: list[DependencyNode] = Field(
        default_factory=list, description="List of dependency nodes"
    )
    error_message: str | None = Field(None, description="Error message if failed")
    execution_time: float = Field(..., description="Execution time in seconds")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
    fallback_suggested: bool = Field(
        False, description="Whether fallback to SPEED mode is suggested"
    )
