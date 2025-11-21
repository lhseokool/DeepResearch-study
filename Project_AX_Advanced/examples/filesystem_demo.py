"""Demo: FileSystem Agent using DeepAgents Library with create_deep_agent.

This example demonstrates:
- FR-FS-01: Contextual Exploration
- FR-FS-02: Pattern-based Search
- FR-FS-03: Precise Code Modification
- FR-FS-04: Large Output Handling

Note: FileSystemAgent now uses create_deep_agent, so all methods are synchronous.
"""

from pathlib import Path

from agentic_coding_assistant.agents import FileSystemAgent


def demo_contextual_exploration():
    """Demo FR-FS-01: Contextual Exploration."""
    print("=" * 60)
    print("Demo 1: Contextual Exploration (using create_deep_agent)")
    print("=" * 60)
    
    agent = FileSystemAgent(work_dir=Path.cwd())
    
    # Explore current project (now synchronous)
    context = agent.explore_context("src")
    
    print(f"\n📂 Path: {context['path']}")
    print(f"\n📋 Structure:")
    print(context['structure'][:500] + "..." if len(context['structure']) > 500 else context['structure'])
    print(f"\n💡 Insights:")
    print(context['insights'][:300] + "..." if len(context['insights']) > 300 else context['insights'])


def demo_pattern_search():
    """Demo FR-FS-02: Pattern-based Search."""
    print("\n" + "=" * 60)
    print("Demo 2: Pattern-based Search (using create_deep_agent)")
    print("=" * 60)
    
    agent = FileSystemAgent(work_dir=Path.cwd())
    
    # Search for Python files (now synchronous)
    print("\n🔍 Searching for Python files...")
    results = agent.pattern_search(pattern="**/*.py")
    
    print(f"\n📊 Search Results:")
    print(results.get('results', 'No results')[:500])
    
    # Search for specific string (now synchronous)
    print("\n🔍 Searching for 'create_deep_agent' in files...")
    grep_results = agent.pattern_search(
        query="create_deep_agent",
        extension="py",
    )
    
    print(f"\n📝 Grep Results:")
    print(grep_results.get('results', 'No results')[:500])


def demo_precise_modification():
    """Demo FR-FS-03: Precise Code Modification."""
    print("\n" + "=" * 60)
    print("Demo 3: Precise Code Modification (using create_deep_agent)")
    print("=" * 60)
    
    agent = FileSystemAgent(work_dir=Path.cwd())
    
    # Create a test file (now synchronous)
    test_file = "demo_modification.py"
    original_code = '''
def old_function():
    """This is the old function."""
    return "old"
'''
    
    agent.create_file(test_file, original_code)
    print(f"\n✅ Created test file: {test_file}")
    
    # Modify the file (now synchronous)
    print("\n🔧 Modifying file...")
    result = agent.modify_code(
        file_path=test_file,
        old_string='def old_function():',
        new_string='def new_function():',
    )
    
    print(f"✅ Success: {result['success']}")
    print(f"📄 File: {result.get('file', 'N/A')}")
    print(f"💬 Message: {result.get('modification', result.get('error', 'N/A'))}")
    
    # Clean up
    Path(test_file).unlink(missing_ok=True)
    print(f"\n🧹 Cleaned up test file")


def demo_large_output_handling():
    """Demo FR-FS-04: Large Output Handling."""
    print("\n" + "=" * 60)
    print("Demo 4: Large Output Handling (using create_deep_agent)")
    print("=" * 60)
    
    agent = FileSystemAgent(
        work_dir=Path.cwd(),
        max_token_output=100,  # Set low threshold for demo
    )
    
    # Create a large content
    large_content = "\n".join([
        f"Line {i}: This is a long line with lots of content to simulate a large file."
        for i in range(200)
    ])
    
    print(f"\n📊 Content size: {len(large_content.split())} words")
    
    # Handle large content (now synchronous)
    result = agent.handle_large_output(large_content)
    
    if result.get('large_output'):
        print(f"\n💾 Large Output Detected!")
        print(f"🔢 Estimated Tokens: {result['estimated_tokens']}")
        print(f"💾 Saved to: {result.get('saved_to', 'N/A')}")
        print(f"📝 Summary: {result.get('summary', 'N/A')[:200]}...")
        
        # Clean up
        if Path(result['saved_to']).exists():
            Path(result['saved_to']).unlink()
            print(f"\n🧹 Cleaned up cache file")


def demo_safe_file_read():
    """Demo safe file reading with automatic large file handling."""
    print("\n" + "=" * 60)
    print("Demo 5: Safe File Reading (using create_deep_agent)")
    print("=" * 60)
    
    agent = FileSystemAgent(
        work_dir=Path.cwd(),
        max_token_output=1000,
    )
    
    # Read a small file
    test_file = "small_test.py"
    small_content = '''
def hello():
    """A small function."""
    return "Hello, World!"
'''
    
    agent.create_file(test_file, small_content)
    
    print(f"\n📖 Reading small file: {test_file}")
    result = agent.read_file_safe(test_file)
    
    if result.get('success'):
        print(f"✅ Success!")
        print(f"\n📝 Content preview:")
        print(result.get('content', 'N/A')[:200])
    else:
        print(f"❌ Error: {result.get('error')}")
    
    # Clean up
    Path(test_file).unlink(missing_ok=True)
    print(f"\n🧹 Cleaned up test file")


def demo_human_in_loop():
    """Demo human-in-the-loop for large files."""
    print("\n" + "=" * 60)
    print("Demo 6: Human-in-the-Loop (using create_deep_agent)")
    print("=" * 60)
    
    agent = FileSystemAgent(
        work_dir=Path.cwd(),
        max_token_output=50,  # Very low threshold
    )
    
    # Create a moderately large file
    test_file = "moderate_file.py"
    moderate_content = "\n".join([
        f"# Line {i}: Some code content here"
        for i in range(100)
    ])
    
    agent.create_file(test_file, moderate_content)
    
    print(f"\n📖 Reading file: {test_file}")
    print("💡 Note: With create_deep_agent, large file handling is automatic!")
    
    result = agent.read_file_safe(test_file)
    
    if result.get('large_output'):
        print(f"\n💾 Large output detected and handled!")
        print(f"📝 Summary: {result.get('summary', 'N/A')[:200]}")
    elif result.get('success'):
        print(f"\n✅ File content loaded successfully")
    
    # Clean up
    Path(test_file).unlink(missing_ok=True)
    print(f"\n🧹 Cleaned up test files")


def main():
    """Run all demos."""
    print("🚀 FileSystem Agent Demonstration (using create_deep_agent)\n")
    print("💡 Note: All operations are now synchronous thanks to create_deep_agent!\n")
    
    demo_contextual_exploration()
    demo_pattern_search()
    demo_precise_modification()
    demo_large_output_handling()
    demo_safe_file_read()
    demo_human_in_loop()
    
    print("\n" + "=" * 60)
    print("✅ All demos completed!")
    print("DeepAgent Pattern Applied: Planning + FileSystem + SubAgent")
    print("=" * 60)


if __name__ == "__main__":
    main()  # No async needed!
