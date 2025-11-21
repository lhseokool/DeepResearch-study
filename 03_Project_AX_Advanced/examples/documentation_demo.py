"""Demo: Documentation Synchronization Agent.

This example demonstrates:
- FR-DS-01: Automatic documentation synchronization
"""

import asyncio
from pathlib import Path

from agentic_coding_assistant.agents import DocumentationAgent


async def demo_docstring_generation():
    """Demo automatic docstring generation."""
    print("=" * 60)
    print("Demo 1: Docstring Generation")
    print("=" * 60)
    
    agent = DocumentationAgent()
    
    # Function without docstring
    function_code = '''
def calculate_statistics(numbers: list[float]) -> dict[str, float]:
    if not numbers:
        raise ValueError("List cannot be empty")
    
    total = sum(numbers)
    count = len(numbers)
    mean = total / count
    
    sorted_nums = sorted(numbers)
    median = sorted_nums[count // 2]
    
    return {
        "mean": mean,
        "median": median,
        "min": min(numbers),
        "max": max(numbers),
    }
'''
    
    print("\n📝 Original function (no docstring):")
    print(function_code[:200] + "...")
    
    # Generate docstring
    docstring = await agent.generate_docstring(
        function_code=function_code,
        function_name="calculate_statistics",
        style="google",
    )
    
    print("\n✨ Generated Google-style docstring:")
    print(docstring)


async def demo_code_change_analysis():
    """Demo analysis of code changes."""
    print("\n" + "=" * 60)
    print("Demo 2: Code Change Analysis")
    print("=" * 60)
    
    agent = DocumentationAgent()
    
    old_code = '''
def process_data(data):
    """Process input data."""
    return [x * 2 for x in data]

class DataProcessor:
    """Simple data processor."""
    def run(self):
        pass
'''
    
    new_code = '''
def process_data(data: list[int]) -> list[int]:
    """Process input data with type hints.
    
    Args:
        data: List of integers to process
        
    Returns:
        List of processed integers
    """
    return [x * 2 for x in data if x > 0]

def validate_data(data: list[int]) -> bool:
    """Validate input data.
    
    Args:
        data: Data to validate
        
    Returns:
        True if valid
    """
    return len(data) > 0

class DataProcessor:
    """Enhanced data processor."""
    def __init__(self):
        self.processed = []
    
    def run(self, data):
        self.processed = process_data(data)
'''
    
    print("\n🔍 Analyzing changes...")
    changes = agent.analyze_code_changes(
        old_code=old_code,
        new_code=new_code,
        file_path="data_processor.py",
    )
    
    print(f"\n📊 Analysis Results:")
    print(f"  Functions changed: {changes['functions_changed']}")
    print(f"  Classes changed: {changes['classes_changed']}")
    print(f"  Docstrings changed: {len(changes['docstrings_changed'])}")


async def demo_readme_update():
    """Demo README update generation."""
    print("\n" + "=" * 60)
    print("Demo 3: README Update")
    print("=" * 60)
    
    agent = DocumentationAgent()
    
    current_readme = '''# My Project

## Features

- Process data with `process_data()` function
- Simple data processing

## Usage

```python
from my_project import process_data

result = process_data([1, 2, 3])
```
'''
    
    code_changes = {
        "file_path": "data_processor.py",
        "functions_changed": ["process_data", "validate_data"],
        "classes_changed": ["DataProcessor"],
        "imports_changed": [],
        "docstrings_changed": [],
    }
    
    print("\n📄 Current README:")
    print(current_readme)
    
    print("\n🔄 Generating updated README...")
    updated_readme = await agent.update_readme(
        current_readme=current_readme,
        code_changes=code_changes,
    )
    
    print("\n✨ Updated README:")
    print(updated_readme[:500] + "..." if len(updated_readme) > 500 else updated_readme)


async def demo_full_synchronization():
    """Demo complete documentation synchronization."""
    print("\n" + "=" * 60)
    print("Demo 4: Full Documentation Synchronization")
    print("=" * 60)
    
    # Setup test environment
    test_dir = Path("test_docs_sync")
    test_dir.mkdir(exist_ok=True)
    
    readme_path = test_dir / "README.md"
    readme_path.write_text('''# Test Project

## API

The `calculate_sum` function adds two numbers.
''')
    
    agent = DocumentationAgent()
    
    old_code = '''
def calculate_sum(a, b):
    return a + b
'''
    
    new_code = '''
def calculate_sum(a: int, b: int) -> int:
    """Calculate sum of two integers.
    
    Args:
        a: First integer
        b: Second integer
        
    Returns:
        Sum of a and b
        
    Raises:
        TypeError: If inputs are not integers
    """
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("Both arguments must be integers")
    return a + b

def calculate_product(a: int, b: int) -> int:
    """Calculate product of two integers.
    
    Args:
        a: First integer
        b: Second integer
        
    Returns:
        Product of a and b
    """
    return a * b
'''
    
    print("\n🔄 Synchronizing documentation...")
    result = await agent.synchronize_documentation(
        old_code=old_code,
        new_code=new_code,
        file_path="calculator.py",
        project_root=test_dir,
        auto_apply=False,
    )
    
    print(f"\n📊 Synchronization Results:")
    print(f"  Success: {result['success']}")
    print(f"  Updates needed: {result['updates_needed']}")
    print(f"  Message: {result['message']}")
    
    if result['proposed_updates']:
        print(f"\n📝 Proposed Updates:")
        for update in result['proposed_updates']:
            print(f"\n  Type: {update['type']}")
            print(f"  File: {update['file']}")
            print(f"  Reason: {update['reason']}")
            print(f"  Preview: {update['proposed_preview']}")
    
    # Clean up
    import shutil
    shutil.rmtree(test_dir)
    print(f"\n🧹 Cleaned up test directory")


async def demo_api_documentation():
    """Demo API documentation update."""
    print("\n" + "=" * 60)
    print("Demo 5: API Documentation Update")
    print("=" * 60)
    
    agent = DocumentationAgent()
    
    current_api_doc = '''# API Documentation

## Endpoints

### GET /api/data
Returns all data items.

**Response:**
```json
{
  "data": []
}
```
'''
    
    code_changes = {
        "file_path": "api/routes.py",
        "functions_changed": ["get_data", "create_data"],
        "classes_changed": [],
        "imports_changed": [],
        "docstrings_changed": [],
    }
    
    print("\n📄 Current API Documentation:")
    print(current_api_doc)
    
    print("\n🔄 Generating updated API documentation...")
    updated_doc = await agent.update_api_documentation(
        current_doc=current_api_doc,
        code_changes=code_changes,
    )
    
    print("\n✨ Updated API Documentation:")
    print(updated_doc[:600] + "..." if len(updated_doc) > 600 else updated_doc)


async def demo_batch_synchronization():
    """Demo batch documentation synchronization for multiple files."""
    print("\n" + "=" * 60)
    print("Demo 6: Batch Synchronization")
    print("=" * 60)
    
    agent = DocumentationAgent()
    
    # Simulate multiple file changes
    file_changes = [
        {
            "file": "utils.py",
            "old_code": "def helper(): pass",
            "new_code": "def helper(x: int) -> str:\n    return str(x)",
        },
        {
            "file": "models.py",
            "old_code": "class User: pass",
            "new_code": "class User:\n    def __init__(self, name: str):\n        self.name = name",
        },
    ]
    
    test_dir = Path("test_batch")
    test_dir.mkdir(exist_ok=True)
    
    results = []
    
    for change in file_changes:
        print(f"\n🔄 Processing {change['file']}...")
        
        result = await agent.synchronize_documentation(
            old_code=change['old_code'],
            new_code=change['new_code'],
            file_path=change['file'],
            project_root=test_dir,
            auto_apply=False,
        )
        
        results.append({
            "file": change['file'],
            "updates": result['updates_needed'],
        })
    
    print(f"\n📊 Batch Results:")
    for res in results:
        print(f"  {res['file']}: {res['updates']} updates needed")
    
    # Clean up
    import shutil
    shutil.rmtree(test_dir)
    print(f"\n🧹 Cleaned up test directory")


async def main():
    """Run all demos."""
    print("🚀 Documentation Synchronization Agent Demonstration\n")
    
    await demo_docstring_generation()
    await demo_code_change_analysis()
    await demo_readme_update()
    await demo_full_synchronization()
    await demo_api_documentation()
    await demo_batch_synchronization()
    
    print("\n" + "=" * 60)
    print("✅ All demos completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
