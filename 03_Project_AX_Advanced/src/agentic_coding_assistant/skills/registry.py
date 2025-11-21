"""Skill Registry for Agentic Coding Assistant.

This module manages the mapping between abstract skills and concrete tools.
It allows for dynamic retrieval of tools based on requested skills.
"""

from typing import Any


class SkillRegistry:
    """Registry for managing skills and their associated tools."""

    def __init__(self):
        self._skills: dict[str, list[str]] = {}
        self._tools: dict[str, Any] = {}

        # Initialize default skills
        self._init_default_skills()

    def _init_default_skills(self):
        """Initialize default skill mappings."""
        self._skills = {
            "code_analysis": ["analyze_code", "find_references", "get_symbol_info"],
            "impact_detection": ["detect_impact", "analyze_dependencies"],
            "refactoring": ["refactor_code", "apply_changes"],
            "documentation": ["sync_documentation", "update_docstrings"],
            "testing": ["run_tests", "generate_tests"],
            "code_generation": [],  # LLM only
            "review": [],  # LLM only
        }

    def register_tool(self, tool: Any):
        """Register a tool instance."""
        tool_name = tool.name if hasattr(tool, "name") else tool.get("name")
        if tool_name:
            self._tools[tool_name] = tool

    def register_skill(self, skill_name: str, tool_names: list[str]):
        """Register a new skill or update an existing one."""
        self._skills[skill_name] = tool_names

    def get_tools_for_skill(self, skill_name: str) -> list[Any]:
        """Get tool instances for a specific skill."""
        tool_names = self._skills.get(skill_name, [])
        return [self._tools[name] for name in tool_names if name in self._tools]

    def get_all_skills(self) -> list[str]:
        """Get list of all available skills."""
        return list(self._skills.keys())


# Global registry instance
registry = SkillRegistry()
