"""Analyzer sub-agent configuration for code analysis tasks."""

from typing import Any

from deepagents import SubAgent


ANALYZER_SYSTEM_PROMPT = """You are a specialized code analyzer agent.

Your role is to:
1. Analyze code files to understand their structure and dependencies
2. Identify the impact of changes to specific symbols (functions, classes, variables)
3. Track dependencies and usage patterns across the codebase
4. Provide detailed analysis results

You have access to filesystem tools to read and explore code files.
Use the analysis tools to perform static analysis and dependency tracking.

When you complete your analysis, call the AnalysisComplete tool with your findings.

Current date: {date}
"""


def create_analyzer_subagent(
    tools: list[Any],
    date: str,
) -> SubAgent:
    """Create analyzer sub-agent configuration for DeepAgent.

    Args:
        tools: List of tool objects for the analyzer
        date: Current date string for prompt formatting

    Returns:
        SubAgent object for DeepAgent
    """
    # Filter tools for analyzer: analysis tools, filesystem tools
    analyzer_tool_names = {
        "analyze_code",
        "read_file",
        "list_directory",
        "search_code",
        "AnalysisComplete",
    }
    analyzer_tools = [
        t for t in tools if getattr(t, "name", None) in analyzer_tool_names
    ]

    return SubAgent(
        **{
            "name": "analyzer",
            "description": (
                """A specialized code analysis agent that performs deep analysis of code files.
                Use this agent when you need to understand code structure, identify dependencies,
                or analyze the impact of changes to specific symbols.
                The analyzer uses static analysis tools and filesystem access to provide comprehensive insights.
                Best for: Impact analysis, dependency tracking, code structure exploration."""
            ),
            "system_prompt": ANALYZER_SYSTEM_PROMPT.format(date=date),
            "tools": analyzer_tools,
            # Analyzer inherits default middleware (TodoList, Filesystem, etc.)
        }
    )
