"""LangGraph workflow for impact analysis using DeepAgent framework."""

from datetime import datetime
from typing import Any, Optional

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from .configuration import DeepAgentConfiguration
from .nodes.analysis_nodes import (
    AnalysisState,
    decide_mode,
    execute_analysis,
    handle_fallback,
    validate_input,
)
from .subagents import create_analyzer_subagent
from .utils.workspace import get_agent_workspace


def should_fallback(state: AnalysisState) -> str:
    """Determine if fallback is needed.

    Args:
        state: Current workflow state

    Returns:
        Next node name
    """
    if state.get("should_fallback", False):
        return "handle_fallback"
    return END


def create_analysis_graph() -> StateGraph:
    """Create the impact analysis workflow graph.

    Returns:
        Compiled StateGraph for analysis workflow
    """
    # Create workflow graph
    workflow = StateGraph(AnalysisState)

    # Add nodes
    workflow.add_node("validate_input", validate_input)
    workflow.add_node("decide_mode", decide_mode)
    workflow.add_node("execute_analysis", execute_analysis)
    workflow.add_node("handle_fallback", handle_fallback)

    # Define edges
    workflow.set_entry_point("validate_input")

    workflow.add_edge("validate_input", "decide_mode")
    workflow.add_edge("decide_mode", "execute_analysis")

    # Conditional edge for fallback
    workflow.add_conditional_edges(
        "execute_analysis",
        should_fallback,
        {
            "handle_fallback": "handle_fallback",
            END: END,
        },
    )

    workflow.add_edge("handle_fallback", END)

    return workflow.compile()


# Create the compiled graph
analysis_graph = create_analysis_graph()


def create_deep_analysis_agent(
    tools: list[Any],
    *,
    model: str = "openai:gpt-4.1",
    config: Optional[RunnableConfig] = None,
    checkpointer=None,
) -> CompiledStateGraph:
    """Create a DeepAgent-based analysis agent.

    This creates an agent using the DeepAgent framework with analyzer sub-agents
    for comprehensive code analysis and impact detection.

    Args:
        tools: List of tool objects for analysis
        model: LLM model identifier (format: provider:model)
        config: Optional runtime configuration
        checkpointer: Checkpointer for session persistence (default: MemorySaver)

    Returns:
        Compiled LangGraph agent ready for execution
    """
    # Default checkpointer
    if checkpointer is None:
        checkpointer = MemorySaver()

    # Get current date for prompts
    now = datetime.now()
    date = f"{now:%a} {now:%b} {now.day}, {now:%Y}"

    # Create analyzer sub-agent configuration
    analyzer_config = create_analyzer_subagent(tools=tools, date=date)

    # Sub-agents list
    subagents = [analyzer_config]

    # Orchestrator system prompt
    orchestrator_prompt = f"""You are an intelligent code analysis agent.

Your role is to:
1. Understand user requests for code analysis and impact assessment
2. Delegate analysis tasks to specialized analyzer sub-agents
3. Coordinate analysis across multiple files and symbols
4. Synthesize results into actionable insights

Available sub-agents:
- analyzer: Deep code analysis and impact detection

Current date: {date}

Use the analyzer sub-agent to perform detailed code analysis.
Provide clear, actionable insights based on the analysis results.
Handle fallback scenarios gracefully when precision analysis is not available.
"""

    # Create DeepAgent
    agent = create_deep_agent(
        model=model,
        tools=tools,
        system_prompt=orchestrator_prompt,
        subagents=subagents,
        backend=lambda rt: FilesystemBackend(
            root_dir=get_agent_workspace("analysis_agent"),
            virtual_mode=True,
        ),
        checkpointer=checkpointer,
        name="CodeAnalysisAgent",
        debug=True,
    )

    return agent
