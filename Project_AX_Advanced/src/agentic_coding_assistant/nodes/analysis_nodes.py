"""LangGraph nodes for impact analysis workflow."""

from typing import TypedDict

from ..agents.coordinator import ImpactAnalysisCoordinator
from ..models.schema import AnalysisMode, AnalysisRequest, AnalysisResult


class AnalysisState(TypedDict):
    """State for impact analysis workflow."""

    request: AnalysisRequest
    result: AnalysisResult | None
    should_fallback: bool
    error_count: int


def validate_input(state: AnalysisState) -> AnalysisState:
    """Validate input parameters.

    Args:
        state: Current workflow state

    Returns:
        Updated state
    """
    request = state["request"]

    # Basic validation
    if not request.file_path:
        state["result"] = AnalysisResult(
            mode=request.mode,
            success=False,
            error_message="File path is required",
            execution_time=0.0,
        )
        return state

    if not request.symbol_name:
        state["result"] = AnalysisResult(
            mode=request.mode,
            success=False,
            error_message="Symbol name is required",
            execution_time=0.0,
        )
        return state

    state["should_fallback"] = False
    state["error_count"] = 0

    return state


def decide_mode(state: AnalysisState) -> AnalysisState:
    """Decide which analysis mode to use.

    Args:
        state: Current workflow state

    Returns:
        Updated state with mode decision
    """
    request = state["request"]

    # If mode is not specified, default to SPEED
    if not request.mode:
        request.mode = AnalysisMode.SPEED

    # If PRECISION mode requested, check if it's available
    if request.mode == AnalysisMode.PRECISION:
        coordinator = ImpactAnalysisCoordinator()
        if not coordinator.precision_analyzer.is_available():
            # Suggest fallback
            state["should_fallback"] = True
            request.mode = AnalysisMode.SPEED

    state["request"] = request
    return state


def execute_analysis(state: AnalysisState) -> AnalysisState:
    """Execute the impact analysis.

    Args:
        state: Current workflow state

    Returns:
        Updated state with analysis results
    """
    request = state["request"]

    # Create coordinator and execute analysis
    coordinator = ImpactAnalysisCoordinator()
    result = coordinator.analyze(request)

    state["result"] = result

    # Check if fallback is needed
    if not result.success and result.fallback_suggested:
        state["should_fallback"] = True
        state["error_count"] = state.get("error_count", 0) + 1

    return state


def handle_fallback(state: AnalysisState) -> AnalysisState:
    """Handle fallback to SPEED mode.

    Args:
        state: Current workflow state

    Returns:
        Updated state after fallback
    """
    # Prevent infinite loops
    if state.get("error_count", 0) > 1:
        if state["result"]:
            state["result"].error_message = (
                "Multiple analysis attempts failed. " + state["result"].error_message
            )
        return state

    # Create fallback request
    original_request = state["request"]
    fallback_request = AnalysisRequest(
        mode=AnalysisMode.SPEED,
        file_path=original_request.file_path,
        symbol_name=original_request.symbol_name,
        project_root=original_request.project_root,
        max_depth=original_request.max_depth,
    )

    # Execute with fallback mode
    coordinator = ImpactAnalysisCoordinator()
    result = coordinator.analyze(fallback_request)

    # Mark as fallback execution
    result.metadata["fallback_from"] = original_request.mode.value
    result.metadata["fallback_reason"] = (
        state["result"].error_message if state.get("result") else "Unknown"
    )

    state["result"] = result
    state["should_fallback"] = False

    return state
