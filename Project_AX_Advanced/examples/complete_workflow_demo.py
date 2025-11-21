"""Demo: Complete Workflow with All Features.

This example demonstrates the full integration of:
- FR-FS: File System Exploration and Manipulation
- FR-AC: Self-Healing Code Generation
- FR-DS: Documentation Synchronization
"""

import asyncio
from pathlib import Path

from agentic_coding_assistant.agents import AdvancedCoordinator


async def demo_complete_refactoring():
    """Demo complete refactoring workflow."""
    print("=" * 70)
    print("Complete Refactoring Workflow Demo")
    print("=" * 70)
    
    # Initialize coordinator
    project_root = Path.cwd()
    coordinator = AdvancedCoordinator(project_root=project_root)
    
    print("\n🎯 Scenario: Refactor a legacy calculator module")
    print("   - Add type hints")
    print("   - Add error handling")
    print("   - Generate tests")
    print("   - Update documentation")
    
    # Step 1: Explore project context
    print("\n" + "=" * 70)
    print("Step 1: Explore Project Context (FR-FS-01)")
    print("=" * 70)
    
    context = await coordinator.explore_project()
    print(f"\n✅ Project explored")
    print(f"📊 Insights: {context['insights'][:150]}...")
    
    # Step 2: Create test file with legacy code
    print("\n" + "=" * 70)
    print("Step 2: Create Test File")
    print("=" * 70)
    
    test_file = project_root / "legacy_calculator.py"
    legacy_code = '''
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    return a / b  # No error handling!

def power(base, exponent):
    return base ** exponent
'''
    
    test_file.write_text(legacy_code)
    print(f"✅ Created {test_file.name}")
    print(f"📝 Legacy code (no type hints, no error handling, no docstrings)")
    
    # Step 3: Search for similar patterns (FR-FS-02)
    print("\n" + "=" * 70)
    print("Step 3: Pattern Search (FR-FS-02)")
    print("=" * 70)
    
    search_result = await coordinator.search_code(
        pattern="**/*calculator*.py",
    )
    print(f"✅ Found {len(search_result.get('glob_results', []))} calculator files")
    
    # Step 4: Apply self-healing refactoring (FR-AC-01, FR-AC-02, FR-AC-03)
    print("\n" + "=" * 70)
    print("Step 4: Self-Healing Refactoring (FR-AC-01, FR-AC-02, FR-AC-03)")
    print("=" * 70)
    
    # Improved code (simulating LLM generation)
    improved_code = '''
from typing import Union

def add(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Add two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of a and b
    """
    return a + b

def subtract(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Subtract b from a.
    
    Args:
        a: Number to subtract from
        b: Number to subtract
        
    Returns:
        Difference of a and b
    """
    return a - b

def multiply(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Multiply two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Product of a and b
    """
    return a * b

def divide(a: Union[int, float], b: Union[int, float]) -> float:
    """Divide a by b.
    
    Args:
        a: Dividend
        b: Divisor
        
    Returns:
        Quotient of a and b
        
    Raises:
        ValueError: If b is zero
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def power(base: Union[int, float], exponent: Union[int, float]) -> Union[int, float]:
    """Raise base to exponent power.
    
    Args:
        base: Base number
        exponent: Exponent
        
    Returns:
        base raised to exponent power
    """
    return base ** exponent
'''
    
    def human_callback(message: str) -> bool:
        """Simulate human approval."""
        print(f"\n🤔 Human Decision Required:")
        print(message)
        print("✅ Auto-approving for demo...")
        return True
    
    healing_result = await coordinator.refactor_with_healing(
        code=improved_code,
        file_path=test_file,
        related_docs="Best practices: Type hints, docstrings, error handling",
        human_callback=human_callback,
    )
    
    print(f"\n✅ Refactoring completed")
    print(f"📊 Success: {healing_result['success']}")
    print(f"📊 Test file: {healing_result.get('test_file', 'N/A')}")
    print(f"✅ Tests passed: {healing_result.get('test_passed', False)}")
    
    # Step 5: Synchronize documentation (FR-DS-01)
    print("\n" + "=" * 70)
    print("Step 5: Documentation Synchronization (FR-DS-01)")
    print("=" * 70)
    
    doc_result = await coordinator.synchronize_documentation(
        old_code=legacy_code,
        new_code=improved_code,
        file_path=str(test_file),
        auto_apply=False,
    )
    
    print(f"\n✅ Documentation analyzed")
    print(f"📊 Updates needed: {doc_result['updates_needed']}")
    
    if doc_result.get('proposed_updates'):
        print(f"\n📝 Proposed documentation updates:")
        for update in doc_result['proposed_updates']:
            print(f"  - {update['type']}: {update['reason']}")
    
    # Step 6: Demonstrate precise code modification (FR-FS-03)
    print("\n" + "=" * 70)
    print("Step 6: Precise Code Modification (FR-FS-03)")
    print("=" * 70)
    
    modification_result = await coordinator.modify_code_precise(
        file_path=str(test_file),
        old_string='Union[int, float]',
        new_string='float',
    )
    
    print(f"✅ Code modified: {modification_result['success']}")
    
    # Clean up
    print("\n" + "=" * 70)
    print("Cleanup")
    print("=" * 70)
    
    test_file.unlink(missing_ok=True)
    test_file_path = Path(healing_result.get('test_file', ''))
    if test_file_path.exists():
        test_file_path.unlink()
    
    print("🧹 Cleaned up test files")


async def demo_large_codebase_handling():
    """Demo handling large codebase with human-in-the-loop."""
    print("\n" + "=" * 70)
    print("Large Codebase Handling Demo (FR-FS-04)")
    print("=" * 70)
    
    coordinator = AdvancedCoordinator(project_root=Path.cwd())
    
    # Create a large test file
    large_file = Path("large_module.py")
    large_content = "\n".join([
        f'''
def function_{i}(x: int) -> int:
    """Function number {i}.
    
    Args:
        x: Input value
        
    Returns:
        Processed value
    """
    return x * {i}
'''
        for i in range(100)
    ])
    
    large_file.write_text(large_content)
    print(f"\n✅ Created large file: {large_file.name}")
    print(f"📊 Size: {len(large_content)} characters")
    
    # Handle with human-in-the-loop
    def human_callback(message: str) -> bool:
        print(f"\n🤔 Human Decision Required:")
        print(message[:200] + "...")
        print("✅ Approving to process...")
        return True
    
    result = await coordinator.handle_large_file(
        file_path=str(large_file),
        human_callback=human_callback,
    )
    
    print(f"\n✅ Large file handled")
    print(f"📊 Type: {result.get('type')}")
    print(f"📊 Tokens: {result.get('tokens')}")
    print(f"🤝 Human decision: {result.get('human_decision', 'N/A')}")
    
    # Clean up
    large_file.unlink(missing_ok=True)
    if result.get('saved_to'):
        saved_path = Path(result['saved_to'])
        if saved_path.exists():
            saved_path.unlink()
    
    print("🧹 Cleaned up test files")


async def demo_end_to_end_workflow():
    """Demo complete end-to-end workflow."""
    print("\n" + "=" * 70)
    print("End-to-End Workflow Demo")
    print("=" * 70)
    
    coordinator = AdvancedCoordinator(project_root=Path.cwd())
    
    # Setup test environment
    test_project = Path("test_project")
    test_project.mkdir(exist_ok=True)
    
    # Create sample files
    (test_project / "module1.py").write_text('''
def old_function():
    pass
''')
    
    (test_project / "module2.py").write_text('''
class OldClass:
    pass
''')
    
    (test_project / "README.md").write_text('''# Test Project
Basic documentation.
''')
    
    print("\n✅ Test project created")
    
    # Run complete workflow
    def human_callback(message: str) -> bool:
        print(f"\n🤔 {message[:100]}...")
        print("✅ Auto-approving...")
        return True
    
    # Note: This is a simplified version
    # In practice, you'd provide actual refactoring requirements
    print("\n🚀 Running complete workflow...")
    print("   (This is a simplified demo)")
    
    # Explore
    context = await coordinator.explore_project(str(test_project))
    print(f"\n✅ Step 1: Project explored")
    
    # Search
    search = await coordinator.search_code(pattern="**/*.py")
    print(f"✅ Step 2: Found {len(search.get('glob_results', []))} Python files")
    
    print(f"\n✅ Workflow completed (simplified demo)")
    
    # Clean up
    import shutil
    shutil.rmtree(test_project)
    print("🧹 Cleaned up test project")


async def main():
    """Run all workflow demos."""
    print("🚀 Complete Workflow Demonstration\n")
    print("This demo showcases the integration of all features:")
    print("  - FR-FS: File System Exploration & Manipulation")
    print("  - FR-AC: Self-Healing Code Generation")
    print("  - FR-DS: Documentation Synchronization")
    print()
    
    await demo_complete_refactoring()
    await demo_large_codebase_handling()
    await demo_end_to_end_workflow()
    
    print("\n" + "=" * 70)
    print("✅ All workflow demos completed!")
    print("=" * 70)
    print("\n📚 Summary:")
    print("  ✅ FR-FS-01: Contextual Exploration")
    print("  ✅ FR-FS-02: Pattern-based Search")
    print("  ✅ FR-FS-03: Precise Code Modification")
    print("  ✅ FR-FS-04: Large Output Handling")
    print("  ✅ FR-AC-01: Refactoring Execution")
    print("  ✅ FR-AC-02: Self-Healing Loop (Max 3 retries)")
    print("  ✅ FR-AC-03: Test Generation")
    print("  ✅ FR-DS-01: Documentation Synchronization")


if __name__ == "__main__":
    asyncio.run(main())
