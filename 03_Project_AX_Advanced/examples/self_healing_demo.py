"""Demo: Self-Healing Agent with automatic code recovery.

This example demonstrates:
- FR-AC-01: Refactoring Execution
- FR-AC-02: Self-Healing Loop (Max 3 retries)
- FR-AC-03: Test Generation
"""

import asyncio
from pathlib import Path

from agentic_coding_assistant.agents import SelfHealingAgent


async def demo_basic_healing():
    """Demo basic self-healing with syntax error."""
    print("=" * 60)
    print("Demo 1: Basic Self-Healing (Syntax Error)")
    print("=" * 60)
    
    agent = SelfHealingAgent(work_dir=Path.cwd())
    
    # Intentionally broken code
    broken_code = '''
def calculate_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    return total / count  # Missing zero check!

# Test
result = calculate_average([])  # This will cause ZeroDivisionError
print(result)
'''
    
    result = await agent.self_heal(
        code=broken_code,
        file_path="demo_average.py",
    )
    
    print(f"\n✅ Success: {result['success']}")
    print(f"📊 Attempts: {result['attempts']}")
    print(f"💬 Message: {result['message']}")
    
    if result['success']:
        print("\n📝 Final Code:")
        print(result['final_code'])


async def demo_test_generation():
    """Demo automatic test generation."""
    print("\n" + "=" * 60)
    print("Demo 2: Automatic Test Generation")
    print("=" * 60)
    
    agent = SelfHealingAgent(work_dir=Path.cwd())
    
    # Sample code
    code = '''
def fibonacci(n: int) -> int:
    """Calculate nth Fibonacci number.
    
    Args:
        n: Position in Fibonacci sequence
        
    Returns:
        Fibonacci number at position n
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if n == 1 or n == 2:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)
'''
    
    test_code = await agent.generate_unit_tests(
        code=code,
        file_path="fibonacci.py",
        framework="pytest",
    )
    
    print("\n📝 Generated Test Code:")
    print(test_code)


async def demo_refactoring_with_tests():
    """Demo complete refactoring workflow with tests."""
    print("\n" + "=" * 60)
    print("Demo 3: Refactoring with Automatic Tests")
    print("=" * 60)
    
    agent = SelfHealingAgent(work_dir=Path.cwd())
    
    # Code that needs improvement
    code = '''
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
'''
    
    result = await agent.refactor_with_tests(
        code=code,
        file_path="data_processor.py",
    )
    
    print(f"\n✅ Success: {result['success']}")
    print(f"📊 Healing attempts: {result.get('healing_attempts', 0)}")
    print(f"✔️  Tests passed: {result['test_passed']}")
    print(f"📄 Test file: {result['test_file']}")
    
    if result['success']:
        print("\n📝 Final Code:")
        print(result['code'][:500] + "..." if len(result['code']) > 500 else result['code'])


async def demo_complex_healing():
    """Demo complex healing scenario with multiple error types."""
    print("\n" + "=" * 60)
    print("Demo 4: Complex Healing (Multiple Error Types)")
    print("=" * 60)
    
    agent = SelfHealingAgent(work_dir=Path.cwd())
    
    # Code with multiple issues
    complex_code = '''
import nonexistent_module  # ImportError

def complex_function(x, y):
    # Missing type hints
    # Missing docstring
    result = x + y
    print(f"Result: {result}")  # Should use logging
    return result

# Missing error handling
def divide(a, b):
    return a / b  # No zero check

class MyClass:
    # Missing __init__
    def method(self):
        return self.attribute  # AttributeError if not initialized
'''
    
    result = await agent.self_heal(
        code=complex_code,
        file_path="complex_demo.py",
        related_docs="""
Best practices:
- Use type hints for all functions
- Add comprehensive docstrings
- Handle potential errors
- Use logging instead of print
""",
    )
    
    print(f"\n✅ Success: {result['success']}")
    print(f"📊 Attempts: {result['attempts']}")
    
    if result['success']:
        print("\n📝 Healed Code Preview:")
        print(result['final_code'][:800] + "...")
        
        print("\n📜 Healing History:")
        for i, attempt in enumerate(result.get('history', []), 1):
            print(f"\nAttempt {i}:")
            print(f"  Error Type: {attempt.result.error_type.value if attempt.result.error_type else 'unknown'}")
            print(f"  Error: {attempt.error_context[:100]}...")
    else:
        print(f"\n❌ Failed: {result['message']}")
        print(f"Last error: {result.get('last_error', 'Unknown')[:200]}")


async def main():
    """Run all demos."""
    print("🚀 Self-Healing Agent Demonstration\n")
    
    await demo_basic_healing()
    await demo_test_generation()
    await demo_refactoring_with_tests()
    await demo_complex_healing()
    
    print("\n" + "=" * 60)
    print("✅ All demos completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
