"""Demo script showing DeepAgent-based coding assistant usage.

This demonstrates:
1. Creating a DeepAgent-based coordinator
2. Using sub-agents for specialized tasks
3. Coordinating analysis, refactoring, and documentation
"""

import asyncio
from pathlib import Path

from agentic_coding_assistant.agents.advanced_coordinator import AdvancedCoordinator
from agentic_coding_assistant.agents.coordinator import ImpactAnalysisCoordinator
from agentic_coding_assistant.configuration import DeepAgentConfiguration
from agentic_coding_assistant.graph import create_deep_analysis_agent


async def demo_basic_analysis():
    """Demo basic code analysis using DeepAgent."""
    print("=" * 60)
    print("Demo 1: Basic Code Analysis with DeepAgent")
    print("=" * 60)

    # Create coordinator
    coordinator = ImpactAnalysisCoordinator(
        model="openai/gpt-4.1-mini",
        project_root="/Users/hseokool/Desktop/src/project-ax-advanced",
    )

    # Example: Analyze a specific function
    from agentic_coding_assistant.models.schema import AnalysisMode, AnalysisRequest

    request = AnalysisRequest(
        mode=AnalysisMode.SPEED,
        file_path="src/agentic_coding_assistant/agents/coordinator.py",
        symbol_name="ImpactAnalysisCoordinator",
        project_root="/Users/hseokool/Desktop/src/project-ax-advanced",
        max_depth=3,
    )

    result = coordinator.analyze(request)

    print(f"\n✅ Analysis completed: {result.success}")
    print(f"Mode: {result.mode}")
    print(f"Execution time: {result.execution_time:.2f}s")
    if result.affected_symbols:
        print(f"Affected symbols: {len(result.affected_symbols)}")


async def demo_deep_agent_coordinator():
    """Demo creating and using a DeepAgent-based coordinator."""
    print("\n" + "=" * 60)
    print("Demo 2: DeepAgent-based Coordinator")
    print("=" * 60)

    # Create coordinator
    coordinator = ImpactAnalysisCoordinator(
        model="openai/gpt-4.1-mini",
        project_root="/Users/hseokool/Desktop/src/project-ax-advanced",
    )

    # Create DeepAgent-based coordinator
    # Note: In a real scenario, you would provide actual tools
    tools = []  # Add your tools here

    agent = await coordinator.create_deep_coordinator(
        tools=tools,
        checkpointer=None,  # Uses default MemorySaver
    )

    print("\n✅ DeepAgent coordinator created successfully")
    print(f"Agent name: {agent.name if hasattr(agent, 'name') else 'CodeAnalysisAgent'}")
    print("Sub-agents: analyzer")
    print("Backend: FilesystemBackend (virtual mode)")


async def demo_advanced_workflow():
    """Demo advanced workflow with all sub-agents."""
    print("\n" + "=" * 60)
    print("Demo 3: Advanced Workflow with All Sub-Agents")
    print("=" * 60)

    # Create advanced coordinator
    coordinator = AdvancedCoordinator(
        project_root="/Users/hseokool/Desktop/src/project-ax-advanced",
        model="openai/gpt-4.1",
    )

    # Example 1: Explore project structure
    print("\n📂 Exploring project structure...")
    context = coordinator.explore_project()
    print(f"Project root: {context.get('project_root', 'N/A')}")

    # Example 2: Search for Python files
    print("\n🔍 Searching for Python files...")
    search_result = coordinator.search_code(pattern="**/*.py", extension="py")
    print(f"Found {len(search_result.get('glob_results', []))} Python files")

    # Example 3: Create DeepAgent-based advanced coordinator
    print("\n🚀 Creating DeepAgent-based advanced coordinator...")
    tools = []  # Add your tools here

    agent = await coordinator.create_deep_advanced_coordinator(
        tools=tools,
        checkpointer=None,
    )

    print("✅ Advanced coordinator created successfully")
    print("Sub-agents: analyzer, refactorer, documenter")
    print("Capabilities:")
    print("  - Code analysis and impact detection")
    print("  - Self-healing code refactoring")
    print("  - Documentation synchronization")


async def demo_configuration():
    """Demo configuration management."""
    print("\n" + "=" * 60)
    print("Demo 4: Configuration Management")
    print("=" * 60)

    # Create configuration
    config = DeepAgentConfiguration(
        main_model="openai:gpt-4.1",
        max_parallel_analyzers=3,
        max_coordinator_iterations=10,
        enable_self_healing=True,
        enable_documentation_sync=True,
        project_root="/Users/hseokool/Desktop/src/project-ax-advanced",
    )

    print("\n📋 Configuration:")
    print(f"  Main model: {config.main_model}")
    print(f"  Max parallel analyzers: {config.max_parallel_analyzers}")
    print(f"  Max coordinator iterations: {config.max_coordinator_iterations}")
    print(f"  Self-healing enabled: {config.enable_self_healing}")
    print(f"  Documentation sync enabled: {config.enable_documentation_sync}")
    print(f"  Project root: {config.project_root}")

    # Convert to runnable config
    runnable_config = config.to_runnable_config()
    print("\n✅ Configuration can be converted to LangGraph runnable config")


async def main():
    """Run all demos."""
    print("\n🎯 DeepAgent-based Coding Assistant Demo")
    print("=" * 60)

    try:
        # Run demos
        await demo_basic_analysis()
        await demo_deep_agent_coordinator()
        await demo_advanced_workflow()
        await demo_configuration()

        print("\n" + "=" * 60)
        print("✅ All demos completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
