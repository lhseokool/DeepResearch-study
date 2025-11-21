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


def create_refactorer_subagent(date: str) -> SubAgent:
    """Create refactorer sub-agent configuration for DeepAgent.

    Args:
        date: Current date string for prompt formatting

    Returns:
        SubAgent object for DeepAgent
    """
    # Refactorer uses filesystem tools only (provided by middleware)
    # ls, read_file, write_file - no additional tools needed

    return SubAgent(
        **{
            "name": "refactorer",
            "description": (
                """A specialized code refactoring agent with self-healing capabilities.
                Use this agent when you need to refactor code while ensuring correctness through automated testing.
                The refactorer generates tests, runs them, and applies self-healing if failures occur.
                It reads existing code, generates improved versions, writes them to files, and verifies correctness.
                Best for: Safe refactoring, code improvement with verification, test-driven development."""
            ),
            "system_prompt": REFACTORER_SYSTEM_PROMPT.format(date=date),
            "tools": [],  # Uses filesystem middleware tools only
            # Refactorer inherits default middleware (TodoList, Filesystem, etc.)
        }
    )
