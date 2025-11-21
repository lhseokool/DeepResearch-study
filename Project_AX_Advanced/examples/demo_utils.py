"""Common utilities for demo scripts.

Provides helpers to reduce code duplication across examples.
"""

from pathlib import Path
from typing import Callable


def print_section(title: str, width: int = 70):
    """Print a section header.
    
    Args:
        title: Section title
        width: Width of separator line
    """
    print("\n" + "=" * width)
    print(title)
    print("=" * width)


def print_subsection(title: str, width: int = 70):
    """Print a subsection header.
    
    Args:
        title: Subsection title
        width: Width of separator line
    """
    print("\n" + "-" * width)
    print(title)
    print("-" * width)


def print_completion(message: str = "All demos completed!", width: int = 70):
    """Print completion message.
    
    Args:
        message: Completion message
        width: Width of separator line
    """
    print("\n" + "=" * width)
    print(f"✅ {message}")
    print("=" * width)


def get_project_root() -> Path:
    """Get project root directory.
    
    Returns:
        Path to project root
    """
    return Path.cwd()


def human_callback_simulator(message: str) -> bool:
    """Simulate human approval for demos.
    
    Args:
        message: Decision message
        
    Returns:
        Always True for automated demos
    """
    print(f"\n🤔 Human Decision Required:")
    print(message[:200] + ("..." if len(message) > 200 else ""))
    print("✅ Auto-approving for demo...")
    return True


def create_human_callback(auto_approve: bool = True) -> Callable[[str], bool]:
    """Create a human callback function.
    
    Args:
        auto_approve: Whether to auto-approve decisions
        
    Returns:
        Callback function
    """
    if auto_approve:
        return human_callback_simulator
    else:
        def manual_callback(message: str) -> bool:
            print(f"\n🤔 Decision Required:")
            print(message)
            response = input("Proceed? (y/n): ")
            return response.lower() in ('y', 'yes')
        return manual_callback
