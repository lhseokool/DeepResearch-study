"""File system utilities."""

from pathlib import Path


def find_python_files(directory: str | Path, max_files: int = 1000) -> list[Path]:
    """Find all Python files in a directory.

    Args:
        directory: Directory to search
        max_files: Maximum number of files to return

    Returns:
        List of Python file paths
    """
    dir_path = Path(directory)

    if not dir_path.exists() or not dir_path.is_dir():
        return []

    python_files = []
    try:
        for py_file in dir_path.rglob("*.py"):
            if len(python_files) >= max_files:
                break

            # Skip virtual environments and common ignore directories
            if any(
                part in py_file.parts
                for part in [".venv", "venv", "__pycache__", ".git", "node_modules"]
            ):
                continue

            python_files.append(py_file)

    except PermissionError:
        pass

    return python_files


def read_file_safe(file_path: str | Path) -> str | None:
    """Safely read a file's contents.

    Args:
        file_path: Path to the file

    Returns:
        File contents or None if read fails
    """
    try:
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            return None

        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    except (OSError, UnicodeDecodeError):
        return None
