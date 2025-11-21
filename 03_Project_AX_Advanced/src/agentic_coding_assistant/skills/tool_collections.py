"""Tool collections for different skill categories.

This module provides functions to retrieve tool collections for specific skills.
"""

from typing import Any


def get_analysis_tools() -> list[str]:
    """Get list of tool names for code analysis.

    Returns:
        List of tool names for analysis tasks
    """
    return [
        "analyze_code",
        "find_references",
        "get_symbol_info",
        "detect_impact",
        "analyze_dependencies",
    ]


def get_refactoring_tools() -> list[str]:
    """Get list of tool names for code refactoring.

    Returns:
        List of tool names for refactoring tasks
    """
    return [
        "refactor_code",
        "apply_changes",
        "validate_syntax",
    ]


def get_documentation_tools() -> list[str]:
    """Get list of tool names for documentation tasks.

    Returns:
        List of tool names for documentation tasks
    """
    return [
        "sync_documentation",
        "update_docstrings",
        "generate_docs",
    ]


def get_testing_tools() -> list[str]:
    """Get list of tool names for testing tasks.

    Returns:
        List of tool names for testing tasks
    """
    return [
        "run_tests",
        "generate_tests",
        "analyze_coverage",
    ]


def get_all_tool_collections() -> dict[str, list[str]]:
    """Get all tool collections organized by skill category.

    Returns:
        Dictionary mapping skill names to tool name lists
    """
    return {
        "code_analysis": get_analysis_tools(),
        "refactoring": get_refactoring_tools(),
        "documentation": get_documentation_tools(),
        "testing": get_testing_tools(),
    }
