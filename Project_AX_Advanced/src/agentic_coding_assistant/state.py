"""State definitions for Agentic Coding Assistant using DeepAgent framework.

This module defines graph state and data structures for the DeepAgent-based
coding assistant workflow.
"""

import operator
from typing import Annotated, Any

from langchain_core.messages import MessageLikeRepresentation
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


###################
# Structured Outputs
###################


class AnalyzeCode(BaseModel):
    """Call this tool to perform code analysis on a specific file."""

    file_path: str = Field(
        description="Path to the file to analyze",
    )
    symbol_name: str = Field(
        description="Name of the symbol (function, class, variable) to analyze",
    )
    analysis_mode: str = Field(
        description="Analysis mode: 'speed' or 'precision'",
    )


class AnalysisComplete(BaseModel):
    """Call this tool to indicate that analysis is complete."""


class RefactorCode(BaseModel):
    """Call this tool to refactor code with self-healing."""

    file_path: str = Field(
        description="Path to the file to refactor",
    )
    refactoring_goal: str = Field(
        description="Goal of the refactoring (e.g., 'Add type hints', 'Improve performance')",
    )


class SyncDocumentation(BaseModel):
    """Call this tool to synchronize documentation with code changes."""

    file_path: str = Field(
        description="Path to the changed file",
    )
    auto_apply: bool = Field(
        default=False,
        description="Whether to automatically apply documentation updates",
    )


class ImpactSummary(BaseModel):
    """Summary of impact analysis with key findings."""

    summary: str
    affected_files: list[str]
    risk_level: str


class ClarifyWithUser(BaseModel):
    """Request clarification from the user."""

    need_clarification: bool = Field(
        description="Whether clarification is needed from the user",
    )
    question: str = Field(
        description="Question to ask the user for clarification",
    )
    verification: str = Field(
        description="Confirmation message after user provides information",
    )


###################
# State Definitions
###################


def override_reducer(current_value, new_value):
    """Reducer function to allow overriding values in state."""
    if isinstance(new_value, dict) and new_value.get("type") == "override":
        return new_value.get("value", new_value)
    else:
        return operator.add(current_value, new_value)


class AgentInputState(MessagesState):
    """InputState contains only 'messages'."""


class AgentState(MessagesState):
    """Main agent state containing messages and analysis data."""

    coordinator_messages: Annotated[list[MessageLikeRepresentation], override_reducer]
    analysis_goal: str | None
    analysis_results: Annotated[list[dict[str, Any]], override_reducer] = []
    impact_notes: Annotated[list[str], override_reducer] = []
    final_report: str
    analysis_iterations: int = 0


class CoordinatorState(TypedDict):
    """State for the coordinator managing analysis tasks."""

    # Required
    coordinator_messages: Annotated[list[MessageLikeRepresentation], override_reducer]
    analysis_goal: str
    # Internal
    impact_notes: Annotated[list[str], override_reducer] = []
    analysis_iterations: int = 0
    analysis_results: Annotated[list[dict[str, Any]], override_reducer] = []


class AnalyzerState(TypedDict):
    """State for individual analyzers performing analysis."""

    analyzer_messages: Annotated[list[MessageLikeRepresentation], operator.add]
    tool_call_iterations: int = 0
    file_path: str
    symbol_name: str
    analysis_mode: str
    analysis_result: dict[str, Any]
    impact_notes: Annotated[list[str], override_reducer] = []


class AnalyzerOutputState(BaseModel):
    """Output state from individual analyzers."""

    analysis_result: dict[str, Any]
    impact_notes: Annotated[list[str], override_reducer] = []
