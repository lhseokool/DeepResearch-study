"""DeepAgent-based workflow for code analysis and impact assessment."""

from datetime import datetime
from typing import Any, Optional

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph

from .configuration import DeepAgentConfiguration
from .prompts.orchestrator import format_orchestrator_prompt
from .subagents import (
    create_analyzer_subagent,
    create_documenter_subagent,
    create_refactorer_subagent,
)
from .utils.workspace import get_agent_workspace


def get_today_str() -> str:
    """Format current date for prompts.

    Returns:
        Human-readable date string like 'Mon Jan 15, 2024'
    """
    now = datetime.now()
    return f"{now:%a} {now:%b} {now.day}, {now:%Y}"


async def create_deep_analysis_agent(
    tools: list[Any],
    *,
    model: str = "openai:gpt-4.1",
    max_analysis_iterations: int = 10,
    enable_self_healing: bool = True,
    enable_documentation_sync: bool = True,
    config: Optional[RunnableConfig] = None,
    checkpointer=None,
) -> CompiledStateGraph:
    """Create a DeepAgent-based code analysis agent.

    This creates an agent using the DeepAgent framework with specialized sub-agents
    for code analysis, refactoring, and documentation synchronization.

    Args:
        tools: List of tool objects for analysis
        model: LLM model identifier (format: provider:model)
        max_analysis_iterations: Maximum analysis iterations before finalization
        enable_self_healing: Enable self-healing agent for code generation
        enable_documentation_sync: Enable documentation synchronization
        config: Optional runtime configuration
        checkpointer: Checkpointer for session persistence (default: MemorySaver)

    Returns:
        Compiled LangGraph agent ready for execution
    """
    # Default checkpointer
    if checkpointer is None:
        checkpointer = MemorySaver()

    # Get current date for prompts
    date = get_today_str()

    # Register tools with the global registry
    from .skills.registry import registry

    for tool in tools:
        registry.register_tool(tool)

    # Add SpawnSubAgent tool
    from .tools.subagent_tools import SpawnSubAgent

    spawn_tool = SpawnSubAgent()
    tools.append(spawn_tool)

    # Create sub-agent configurations
    analyzer_config = create_analyzer_subagent(tools=tools, date=date)

    # Sub-agents list
    subagents = [analyzer_config]

    # Optionally add refactorer
    if enable_self_healing:
        refactorer_config = create_refactorer_subagent(date=date)
        subagents.append(refactorer_config)

    # Optionally add documenter
    if enable_documentation_sync:
        documenter_config = create_documenter_subagent(date=date)
        subagents.append(documenter_config)

    # Format orchestrator system prompt
    orchestrator_prompt = format_orchestrator_prompt(
        date=date,
        max_analysis_iterations=max_analysis_iterations,
        enable_self_healing=enable_self_healing,
        enable_documentation_sync=enable_documentation_sync,
    )

    # Update prompt to mention dynamic sub-agents
    orchestrator_prompt += "\n\nYou can also spawn dynamic sub-agents using the 'spawn_subagent' tool to handle specific complex tasks autonomously."

    # Create DeepAgent
    agent = create_deep_agent(
        model=model,
        tools=tools,
        system_prompt=orchestrator_prompt,
        subagents=subagents,
        backend=lambda rt: FilesystemBackend(
            root_dir=get_agent_workspace("main_agent"),
            virtual_mode=True,
        ),
        checkpointer=checkpointer,
        name="DeepCodeAnalysisAgent",
        debug=True,
        # Middleware is automatically configured by create_deep_agent:
        # - TodoListMiddleware (planning)
        # - FilesystemMiddleware (file operations)
        # - SubAgentMiddleware (dynamic delegation)
        # - SummarizationMiddleware (context compression)
        # - AnthropicPromptCachingMiddleware (cost optimization)
        # - PatchToolCallsMiddleware (tool call fixes)
    )

    return agent


# Example usage function
async def run_analysis(
    request: str,
    tools: list[Any],
    *,
    model: str = "anthropic:claude-sonnet-4-5-20250929",
    thread_id: str = "default",
    max_analysis_iterations: int = 10,
    enable_self_healing: bool = True,
    enable_documentation_sync: bool = True,
    checkpointer=None,
) -> dict[str, Any]:
    """Run code analysis using the DeepAgent-based analysis agent.

    Args:
        request: User's analysis request
        tools: Tools available for analysis
        model: LLM model to use
        thread_id: Thread identifier for state persistence
        max_analysis_iterations: Maximum analysis iterations
        enable_self_healing: Enable self-healing for code generation
        enable_documentation_sync: Enable documentation sync
        checkpointer: Checkpointer for session persistence (default: MemorySaver)

    Returns:
        Final agent state containing messages and filesystem state
    """
    # Create agent
    agent = await create_deep_analysis_agent(
        tools=tools,
        model=model,
        max_analysis_iterations=max_analysis_iterations,
        enable_self_healing=enable_self_healing,
        enable_documentation_sync=enable_documentation_sync,
        checkpointer=checkpointer,
    )

    # Runtime configuration
    config = {
        "configurable": {
            "thread_id": thread_id,
        },
        "recursion_limit": 100,  # High limit for complex multi-agent workflows
    }

    # Execute agent
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": request}]},
        config=config,
    )

    return result
