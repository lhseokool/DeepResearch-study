"""Documenter sub-agent configuration for documentation synchronization."""

from deepagents import SubAgent


DOCUMENTER_SYSTEM_PROMPT = """You are a specialized documentation synchronization agent.

Your role is to:
1. Detect changes between old and new code versions
2. Identify documentation that needs updating
3. Generate updated documentation that reflects code changes
4. Maintain consistency between code and documentation

You have access to filesystem tools to read documentation files and code.
Use diff analysis to identify what changed and update relevant documentation.

When you complete documentation updates, provide a summary of changes made.

Current date: {date}
"""


def create_documenter_subagent(date: str) -> SubAgent:
    """Create documenter sub-agent configuration for DeepAgent.

    Args:
        date: Current date string for prompt formatting

    Returns:
        SubAgent object for DeepAgent
    """
    # Documenter uses only filesystem tools (provided by middleware)
    # No additional tools needed beyond ls, read_file, write_file

    return SubAgent(
        **{
            "name": "documenter",
            "description": (
                "A specialized documentation synchronization agent that keeps documentation "
                "in sync with code changes. Use this agent after code modifications to ensure "
                "documentation remains accurate and up-to-date. The documenter analyzes code diffs, "
                "identifies affected documentation, and generates appropriate updates. "
                "Best for: Documentation maintenance, keeping docs synchronized with code, "
                "ensuring documentation accuracy."
            ),
            "system_prompt": DOCUMENTER_SYSTEM_PROMPT.format(date=date),
            "tools": [],  # Uses only filesystem middleware tools
        }
    )
