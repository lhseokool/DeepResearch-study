"""Tests for SPEED mode analyzer."""

import pytest
from pathlib import Path

from agentic_coding_assistant.analyzers import SpeedAnalyzer
from agentic_coding_assistant.models.schema import (
    AnalysisMode,
    AnalysisRequest,
)


@pytest.fixture
def speed_analyzer():
    """Create a speed analyzer instance."""
    return SpeedAnalyzer()


@pytest.fixture
def sample_python_file(tmp_path):
    """Create a sample Python file for testing."""
    file_path = tmp_path / "sample.py"
    file_path.write_text("""
def helper_function():
    return "helper"

def main_function():
    result = helper_function()
    return result

def another_function():
    main_function()
    return "another"

class SampleClass:
    def method(self):
        another_function()
""")
    return file_path


def test_speed_analyzer_is_available(speed_analyzer):
    """Test that speed analyzer is always available."""
    assert speed_analyzer.is_available() is True


def test_speed_analyzer_basic_analysis(speed_analyzer, sample_python_file):
    """Test basic analysis with speed analyzer."""
    request = AnalysisRequest(
        mode=AnalysisMode.SPEED,
        file_path=str(sample_python_file),
        symbol_name="helper_function",
        max_depth=2,
    )

    result = speed_analyzer.analyze(request)

    assert result.success is True
    assert result.mode == AnalysisMode.SPEED
    assert result.execution_time > 0
    assert isinstance(result.dependencies, list)


def test_speed_analyzer_file_not_found(speed_analyzer):
    """Test analysis with non-existent file."""
    request = AnalysisRequest(
        mode=AnalysisMode.SPEED,
        file_path="/nonexistent/file.py",
        symbol_name="some_function",
    )

    result = speed_analyzer.analyze(request)

    assert result.success is False
    assert "not found" in result.error_message.lower()


def test_speed_analyzer_metadata(speed_analyzer, sample_python_file):
    """Test that metadata is included in results."""
    request = AnalysisRequest(
        mode=AnalysisMode.SPEED,
        file_path=str(sample_python_file),
        symbol_name="main_function",
    )

    result = speed_analyzer.analyze(request)

    assert "total_nodes" in result.metadata
    assert "total_edges" in result.metadata
    assert "max_depth" in result.metadata
