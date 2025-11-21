"""Tests for advanced agents.

Tests for:
- FileSystemAgent (FR-FS)
- SelfHealingAgent (FR-AC)
- DocumentationAgent (FR-DS)
- AdvancedCoordinator (Integration)
"""

import asyncio
import tempfile
from pathlib import Path

import pytest

from agentic_coding_assistant.agents import (
    AdvancedCoordinator,
    DocumentationAgent,
    FileSystemAgent,
    SelfHealingAgent,
)


class TestFileSystemAgent:
    """Tests for FileSystemAgent (FR-FS)."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    async def test_explore_context(self, temp_dir):
        """Test FR-FS-01: Contextual Exploration."""
        # Create test structure
        (temp_dir / "src").mkdir()
        (temp_dir / "src" / "module.py").write_text("def test(): pass")
        
        agent = FileSystemAgent(work_dir=temp_dir)
        context = await agent.explore_context("src")
        
        assert context["path"] == "src"
        assert "structure" in context
        assert "insights" in context

    @pytest.mark.asyncio
    async def test_pattern_search(self, temp_dir):
        """Test FR-FS-02: Pattern-based Search."""
        # Create test files
        (temp_dir / "test1.py").write_text("def hello(): pass")
        (temp_dir / "test2.py").write_text("def world(): pass")
        
        agent = FileSystemAgent(work_dir=temp_dir)
        results = await agent.pattern_search(pattern="*.py")
        
        assert "glob_results" in results
        assert len(results["glob_results"]) >= 2

    @pytest.mark.asyncio
    async def test_modify_code(self, temp_dir):
        """Test FR-FS-03: Precise Code Modification."""
        test_file = temp_dir / "modify.py"
        test_file.write_text("def old(): pass")
        
        agent = FileSystemAgent(work_dir=temp_dir)
        result = await agent.modify_code(
            file_path=str(test_file),
            old_string="def old():",
            new_string="def new():",
        )
        
        assert result["success"] is True
        assert "def new():" in test_file.read_text()

    @pytest.mark.asyncio
    async def test_large_output_handling(self, temp_dir):
        """Test FR-FS-04: Large Output Handling."""
        agent = FileSystemAgent(work_dir=temp_dir, max_token_output=50)
        
        # Large content
        large_content = " ".join([f"word{i}" for i in range(200)])
        
        result = await agent.handle_large_output(large_content)
        
        assert "type" in result
        assert result["tokens"] > 50


class TestSelfHealingAgent:
    """Tests for SelfHealingAgent (FR-AC)."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    async def test_execute_code(self, temp_dir):
        """Test code execution."""
        agent = SelfHealingAgent(work_dir=temp_dir)
        
        valid_code = "def test(): return 42"
        result = await agent.execute_code(
            code=valid_code,
            file_path=temp_dir / "test.py",
        )
        
        assert result.success is True

    @pytest.mark.asyncio
    async def test_error_classification(self, temp_dir):
        """Test error type classification."""
        agent = SelfHealingAgent(work_dir=temp_dir)
        
        from agentic_coding_assistant.agents.self_healing_agent import ErrorType
        
        # Test syntax error classification
        error_type = agent._classify_error("SyntaxError: invalid syntax")
        assert error_type == ErrorType.SYNTAX_ERROR
        
        # Test import error classification
        error_type = agent._classify_error("ImportError: No module named 'foo'")
        assert error_type == ErrorType.IMPORT_ERROR

    @pytest.mark.asyncio
    async def test_self_heal_simple(self, temp_dir):
        """Test FR-AC-02: Self-Healing Loop (simple case)."""
        agent = SelfHealingAgent(work_dir=temp_dir)
        
        # Valid code that should work on first attempt
        valid_code = '''
def calculate(x: int) -> int:
    """Calculate double of x."""
    return x * 2
'''
        
        result = await agent.self_heal(
            code=valid_code,
            file_path=temp_dir / "calc.py",
        )
        
        assert result["success"] is True
        assert result["attempts"] == 0

    @pytest.mark.asyncio
    async def test_generate_unit_tests(self, temp_dir):
        """Test FR-AC-03: Test Generation."""
        agent = SelfHealingAgent(work_dir=temp_dir)
        
        code = '''
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
'''
        
        test_code = await agent.generate_unit_tests(
            code=code,
            file_path=temp_dir / "math.py",
        )
        
        assert test_code is not None
        assert len(test_code) > 0
        # Check for common test patterns
        assert "def test" in test_code.lower() or "def test_" in test_code


class TestDocumentationAgent:
    """Tests for DocumentationAgent (FR-DS)."""

    @pytest.mark.asyncio
    async def test_analyze_code_changes(self):
        """Test code change analysis."""
        agent = DocumentationAgent()
        
        old_code = "def old(): pass"
        new_code = "def new(): pass\ndef another(): pass"
        
        changes = agent.analyze_code_changes(
            old_code=old_code,
            new_code=new_code,
            file_path="test.py",
        )
        
        assert "functions_changed" in changes
        assert "new" in changes["functions_changed"]

    @pytest.mark.asyncio
    async def test_generate_docstring(self):
        """Test docstring generation."""
        agent = DocumentationAgent()
        
        function_code = '''
def calculate(x: int, y: int) -> int:
    return x + y
'''
        
        docstring = await agent.generate_docstring(
            function_code=function_code,
            function_name="calculate",
        )
        
        assert docstring is not None
        assert len(docstring) > 0

    @pytest.mark.asyncio
    async def test_synchronize_documentation(self, tmp_path):
        """Test FR-DS-01: Documentation Synchronization."""
        agent = DocumentationAgent()
        
        old_code = "def old(): pass"
        new_code = '''
def new(x: int) -> int:
    """New function."""
    return x
'''
        
        result = await agent.synchronize_documentation(
            old_code=old_code,
            new_code=new_code,
            file_path="module.py",
            project_root=tmp_path,
            auto_apply=False,
        )
        
        assert result["success"] is True
        assert "updates_needed" in result


class TestAdvancedCoordinator:
    """Integration tests for AdvancedCoordinator."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    async def test_explore_project(self, temp_dir):
        """Test project exploration."""
        # Create test structure
        (temp_dir / "src").mkdir()
        (temp_dir / "src" / "main.py").write_text("def main(): pass")
        
        coordinator = AdvancedCoordinator(project_root=temp_dir)
        context = await coordinator.explore_project()
        
        assert context is not None
        assert "structure" in context

    @pytest.mark.asyncio
    async def test_search_code(self, temp_dir):
        """Test code search."""
        # Create test files
        (temp_dir / "test.py").write_text("def test(): pass")
        
        coordinator = AdvancedCoordinator(project_root=temp_dir)
        results = await coordinator.search_code(pattern="*.py")
        
        assert "glob_results" in results

    @pytest.mark.asyncio
    async def test_modify_code_precise(self, temp_dir):
        """Test precise code modification."""
        test_file = temp_dir / "code.py"
        test_file.write_text("old_code")
        
        coordinator = AdvancedCoordinator(project_root=temp_dir)
        result = await coordinator.modify_code_precise(
            file_path=str(test_file),
            old_string="old_code",
            new_string="new_code",
        )
        
        assert result["success"] is True


@pytest.mark.asyncio
async def test_integration_workflow():
    """Integration test for complete workflow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir)
        
        # Create test project structure
        (temp_dir / "src").mkdir()
        test_file = temp_dir / "src" / "calculator.py"
        test_file.write_text('''
def add(a, b):
    return a + b
''')
        
        coordinator = AdvancedCoordinator(project_root=temp_dir)
        
        # Test exploration
        context = await coordinator.explore_project("src")
        assert context is not None
        
        # Test search
        search_result = await coordinator.search_code(pattern="**/*.py")
        assert len(search_result.get("glob_results", [])) > 0
        
        print("✅ Integration workflow test passed")


if __name__ == "__main__":
    # Run async tests
    asyncio.run(test_integration_workflow())
    print("✅ All tests completed")
