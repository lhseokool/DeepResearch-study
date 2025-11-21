# Quick Start: Advanced Features

This guide shows how to quickly get started with the advanced autonomous coding features.

## Installation

```bash
# Clone repository
git clone <repository-url>
cd project-ax-advanced

# Install dependencies with UV (recommended)
uv sync

# Or with pip
pip install -e .
```

## Prerequisites

Set up your OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or create a `.env` file:

```
OPENAI_API_KEY=your-api-key-here
```

## Quick Examples

### 1. Self-Healing Code Generation

Automatically fix code errors with up to 3 retry attempts:

```python
import asyncio
from pathlib import Path
from agentic_coding_assistant.agents import SelfHealingAgent

async def main():
    agent = SelfHealingAgent(work_dir=Path.cwd())
    
    # Code with error
    broken_code = '''
def divide(a, b):
    return a / b  # Missing zero check!
'''
    
    # Self-heal with automatic retry
    result = await agent.self_heal(
        code=broken_code,
        file_path="calculator.py",
    )
    
    print(f"Success: {result['success']}")
    print(f"Attempts: {result['attempts']}")
    print(f"Fixed code:\n{result['final_code']}")

asyncio.run(main())
```

**Output:**
```
🔄 Healing attempt 1/3
Error: runtime_error

✅ Success: True
📊 Attempts: 1
📝 Fixed code:
def divide(a: float, b: float) -> float:
    """Divide two numbers safely."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

### 2. File System Exploration

Explore your codebase using DeepAgents FileSystemBackend:

```python
import asyncio
from pathlib import Path
from agentic_coding_assistant.agents import FileSystemAgent

async def main():
    agent = FileSystemAgent(work_dir=Path.cwd())
    
    # Explore project structure
    context = await agent.explore_context("src")
    print("Project insights:", context['insights'])
    
    # Search for Python files
    results = await agent.pattern_search(pattern="**/*.py")
    print(f"Found {len(results['glob_results'])} Python files")
    
    # Search for specific code
    grep_results = await agent.pattern_search(
        query="def calculate",
        extension="py"
    )
    print(f"Found 'calculate' in {len(grep_results['grep_results'])} locations")

asyncio.run(main())
```

### 3. Documentation Synchronization

Keep documentation in sync with code changes:

```python
import asyncio
from pathlib import Path
from agentic_coding_assistant.agents import DocumentationAgent

async def main():
    agent = DocumentationAgent()
    
    old_code = '''
def process(data):
    return data
'''
    
    new_code = '''
def process(data: list[int]) -> list[int]:
    """Process input data.
    
    Args:
        data: List of integers
        
    Returns:
        Processed data
    """
    return [x * 2 for x in data if x > 0]
'''
    
    result = await agent.synchronize_documentation(
        old_code=old_code,
        new_code=new_code,
        file_path="processor.py",
        project_root=Path.cwd(),
    )
    
    print(f"Updates needed: {result['updates_needed']}")
    for update in result.get('proposed_updates', []):
        print(f"- {update['type']}: {update['reason']}")

asyncio.run(main())
```

### 4. Complete Workflow

Use the AdvancedCoordinator for end-to-end refactoring:

```python
import asyncio
from pathlib import Path
from agentic_coding_assistant.agents import AdvancedCoordinator

async def main():
    coordinator = AdvancedCoordinator(project_root=Path.cwd())
    
    # Human-in-the-loop callback
    def human_callback(message: str) -> bool:
        print(f"\n🤔 Decision needed:\n{message}")
        response = input("Proceed? (y/n): ")
        return response.lower() == 'y'
    
    # Code to refactor
    code = '''
def calculate_stats(numbers):
    total = sum(numbers)
    count = len(numbers)
    return total / count
'''
    
    # Complete refactoring with tests
    result = await coordinator.refactor_with_healing(
        code=code,
        file_path="stats.py",
        related_docs="Add type hints, docstrings, and error handling",
        human_callback=human_callback,
    )
    
    if result['success']:
        print("✅ Refactoring successful!")
        print(f"📝 Code: {result['code'][:200]}...")
        print(f"✅ Tests: {result['test_file']}")
        print(f"✔️  Tests passed: {result['test_passed']}")

asyncio.run(main())
```

## Running Examples

We provide complete working examples:

```bash
# Self-healing demo
python examples/self_healing_demo.py

# FileSystem exploration demo
python examples/filesystem_demo.py

# Documentation sync demo
python examples/documentation_demo.py

# Complete workflow demo
python examples/complete_workflow_demo.py
```

## Common Use Cases

### Use Case 1: Add Type Hints to Legacy Code

```python
from agentic_coding_assistant.agents import SelfHealingAgent

agent = SelfHealingAgent()

legacy_code = """
def add(a, b):
    return a + b
"""

# Agent will add type hints, docstrings, and tests
result = await agent.refactor_with_tests(
    code=legacy_code,
    file_path="math_utils.py",
    related_docs="Add type hints using Python 3.10+ syntax"
)
```

### Use Case 2: Large Codebase Exploration

```python
from agentic_coding_assistant.agents import AdvancedCoordinator

coordinator = AdvancedCoordinator(project_root="/path/to/large/project")

# Find all API routes
routes = await coordinator.search_code(
    pattern="**/routes/**/*.py",
    query="@app.route"
)

# Handle large files with summaries
for file in routes['glob_results']:
    result = await coordinator.handle_large_file(
        file_path=file,
        human_callback=lambda msg: True  # Auto-approve
    )
    print(f"Summary: {result['summary']}")
```

### Use Case 3: Batch Documentation Update

```python
from agentic_coding_assistant.agents import DocumentationAgent

agent = DocumentationAgent()

# Update docs for multiple files
files_to_update = [
    ("old_code_1.py", "new_code_1.py"),
    ("old_code_2.py", "new_code_2.py"),
]

for old_file, new_file in files_to_update:
    old_code = Path(old_file).read_text()
    new_code = Path(new_file).read_text()
    
    result = await agent.synchronize_documentation(
        old_code=old_code,
        new_code=new_code,
        file_path=new_file,
        project_root=Path.cwd(),
        auto_apply=False,  # Review before applying
    )
    
    print(f"{new_file}: {result['updates_needed']} updates")
```

## Configuration

### Custom LLM Model

```python
from agentic_coding_assistant.agents import AdvancedCoordinator

# Use different model
coordinator = AdvancedCoordinator(
    project_root=Path.cwd(),
    model="gpt-4o-mini",  # Faster, cheaper
    temperature=0.1,      # More deterministic
)
```

### Adjust Retry Limits

```python
from agentic_coding_assistant.agents import SelfHealingAgent

# Modify MAX_RETRIES (default: 3)
SelfHealingAgent.MAX_RETRIES = 5

agent = SelfHealingAgent()
```

### Large File Threshold

```python
from agentic_coding_assistant.agents import FileSystemAgent

# Lower threshold for testing
agent = FileSystemAgent(
    work_dir=Path.cwd(),
    max_token_output=1000,  # Default: 4000
)
```

## Best Practices

### 1. Always Use Human-in-the-Loop for Production

```python
def careful_callback(message: str) -> bool:
    """Review all changes before applying."""
    print(message)
    print("\n⚠️  Review the changes carefully before proceeding!")
    return input("Apply changes? (yes/no): ").lower() == 'yes'

result = await coordinator.refactor_with_healing(
    code=code,
    file_path="critical_module.py",
    human_callback=careful_callback,  # Always review!
)
```

### 2. Provide Context for Better Results

```python
result = await agent.self_heal(
    code=code,
    file_path="module.py",
    related_docs="""
    Project style guide:
    - Use type hints (PEP 484)
    - Google-style docstrings
    - Raise ValueError for invalid inputs
    - Use logging instead of print
    """,
)
```

### 3. Test Changes Before Committing

```python
# Generate and run tests
result = await agent.refactor_with_tests(
    code=code,
    file_path="module.py",
)

if result['test_passed']:
    print("✅ Safe to commit!")
else:
    print("❌ Tests failed, review changes")
```

### 4. Version Control Integration

```bash
# Always work on a branch
git checkout -b feature/autonomous-refactoring

# Run refactoring
python my_refactoring_script.py

# Review changes
git diff

# Commit if satisfied
git commit -am "refactor: Apply autonomous code improvements"
```

## Troubleshooting

### Issue: "DeepAgents not found"

```bash
# Ensure deepagents is installed
pip install deepagents>=0.2.5
```

### Issue: "OpenAI API key not set"

```bash
# Set environment variable
export OPENAI_API_KEY="your-key"

# Or in Python
import os
os.environ['OPENAI_API_KEY'] = "your-key"
```

### Issue: "Self-healing failed after 3 attempts"

The code might be too complex for automatic fixing. Options:

1. **Simplify the problem**: Break into smaller functions
2. **Provide more context**: Add related documentation
3. **Manual intervention**: Review the healing history and fix manually

```python
if not result['success']:
    print("Healing history:")
    for attempt in result['history']:
        print(f"Attempt {attempt.attempt_number}:")
        print(f"  Error: {attempt.error_context[:100]}")
        print(f"  Patch: {attempt.patch_generated[:100]}...")
```

## Next Steps

1. **Read detailed documentation**: See `docs/ADVANCED_FEATURES.md`
2. **Explore examples**: Check out `examples/` directory
3. **Run tests**: `pytest tests/test_advanced_agents.py`
4. **Integrate with your workflow**: Adapt examples to your needs

## Support

- **Documentation**: `docs/` directory
- **Examples**: `examples/` directory
- **Issues**: GitHub Issues (if applicable)

## References

- [DeepAgents Documentation](https://docs.langchain.com/oss/python/deepagents/overview)
- [FileSystemBackend Guide](https://docs.langchain.com/oss/python/deepagents/backends#filesystembackend-local-disk)
- [LangChain Documentation](https://python.langchain.com/)
