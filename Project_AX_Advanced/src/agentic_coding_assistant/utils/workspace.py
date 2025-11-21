"""Workspace management utilities for DeepAgent-based coding assistant.

This module provides utilities for managing agent workspaces with support
for environment variable configuration.
"""

import os
from pathlib import Path


def get_workspace_root() -> str:
    """Get the workspace root directory path.

    Uses WORKSPACE_ROOT environment variable if set, otherwise uses
    the project root's 'workspace' directory.

    This allows flexibility for Docker environments and other deployment scenarios.

    Returns:
        Absolute path to the workspace root directory
    """
    # Check environment variable first
    workspace_root = os.getenv("WORKSPACE_ROOT")
    if workspace_root:
        return str(Path(workspace_root).resolve())

    # Default: workspace directory in project root
    # __file__ is the path to workspace.py, so parent.parent.parent.parent is project root
    project_root = Path(__file__).parent.parent.parent.parent
    return str(project_root / "workspace")


def get_agent_workspace(agent_name: str) -> str:
    """Get the workspace path for a specific agent.

    Args:
        agent_name: Agent name (e.g., "main_agent", "analyzer_01")

    Returns:
        Absolute path to the agent's workspace
    """
    workspace_root = Path(get_workspace_root())
    agent_workspace = workspace_root / agent_name
    
    # Create directory if it doesn't exist
    agent_workspace.mkdir(parents=True, exist_ok=True)
    
    return str(agent_workspace)


def get_project_root() -> str:
    """Get the project root directory.

    Returns:
        Absolute path to the project root
    """
    # __file__ is workspace.py, so parent.parent.parent.parent is project root
    return str(Path(__file__).parent.parent.parent.parent.resolve())


def ensure_workspace_exists(workspace_path: str) -> None:
    """Ensure that a workspace directory exists.

    Args:
        workspace_path: Path to the workspace directory
    """
    Path(workspace_path).mkdir(parents=True, exist_ok=True)
