"""Tests for DeepAgent coordinator."""

import pytest
from pathlib import Path

from agentic_coding_assistant.agents import ImpactAnalysisCoordinator
from agentic_coding_assistant.models.schema import (
    AnalysisMode,
    AnalysisRequest,
)


@pytest.fixture
def coordinator():
    """Create a coordinator instance."""
    return ImpactAnalysisCoordinator()


@pytest.fixture
def sample_file(tmp_path):
    """Create a sample file for testing."""
    file_path = tmp_path / "test.py"
    file_path.write_text("""
def test_function():
    return "test"
""")
    return file_path


def test_coordinator_speed_mode(coordinator, sample_file):
    """Test coordinator with SPEED mode."""
    request = AnalysisRequest(
        mode=AnalysisMode.SPEED,
        file_path=str(sample_file),
        symbol_name="test_function",
    )

    result = coordinator.analyze(request)

    assert result is not None
    assert result.mode == AnalysisMode.SPEED


def test_coordinator_file_access_validation(coordinator):
    """Test file access validation."""
    request = AnalysisRequest(
        mode=AnalysisMode.SPEED,
        file_path="/nonexistent/file.py",
        symbol_name="test",
    )

    result = coordinator.analyze(request)

    assert result.success is False


def test_coordinator_with_human_in_loop(coordinator, sample_file):
    """Test coordinator with human-in-the-loop."""
    request = AnalysisRequest(
        mode=AnalysisMode.SPEED,
        file_path=str(sample_file),
        symbol_name="test_function",
    )

    # Mock callback that always returns True
    def mock_callback(message):
        return True

    result = coordinator.analyze_with_human_in_loop(request, mock_callback)

    assert result is not None
