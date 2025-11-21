"""Refactorer sub-agent configuration for code refactoring with self-healing."""

from typing import Any

from deepagents import SubAgent


REFACTORER_SYSTEM_PROMPT = """You are a specialized code refactoring agent with self-healing capabilities.

Your role is to:
1. Refactor code according to specified goals (e.g., add type hints, improve performance)
2. Generate unit tests for the refactored code
3. Run tests and verify correctness
4. Apply self-healing if tests fail (up to 3 retries)
5. Ensure the refactored code maintains functionality

You have access to:
- Filesystem tools to read and write code
- Test execution tools to run unit tests
- Code generation tools with self-healing

When you complete refactoring and all tests pass, call the RefactorComplete tool.

Current date: {date}
"""


def create_refactorer_subagent(
    tools: list[Any],
    date: str,
) -> SubAgent:
    """Create refactorer sub-agent configuration for DeepAgent.

    Args:
        tools: List of tool objects for the refactorer
        date: Current date string for prompt formatting

    Returns:
        SubAgent object for DeepAgent
    """
    # Filter tools for refactorer: code generation, testing, filesystem
    refactorer_tool_names = {
        "refactor_code",
        "generate_tests",
        "run_tests",
        "read_file",
        "write_file",
        "RefactorComplete",
    }
    refactorer_tools = [
        t for t in tools if getattr(t, "name", None) in refactorer_tool_names
    ]

    return SubAgent(
        **{
            "name": "refactorer",
            "description": (
                """A specialized code refactoring agent with self-healing capabilities.
                Use this agent when you need to refactor code while ensuring correctness through automated testing.
                The refactorer generates tests, runs them, and applies self-healing if failures occur.
                Best for: Safe refactoring, code improvement with verification, test-driven development."""
            ),
            "system_prompt": REFACTORER_SYSTEM_PROMPT.format(date=date),
            "tools": refactorer_tools,
            # Refactorer inherits default middleware (TodoList, Filesystem, etc.)
        }
    )
