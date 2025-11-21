# DeepAgent Integration Guide

This document describes how the Agentic Coding Assistant integrates the DeepAgent framework for enhanced autonomous capabilities.

## Overview

The project has been updated to use the [DeepAgent framework](https://github.com/deepagents/deepagents), which provides:

- **Planning**: Automatic task planning with TodoList middleware
- **FileSystem**: Virtual filesystem operations for agent workspaces
- **SubAgent**: Dynamic delegation to specialized sub-agents
- **Summarization**: Automatic context compression for long conversations
- **Prompt Caching**: Cost optimization with Anthropic prompt caching

## Architecture

### Core Components

#### 1. Configuration (`configuration.py`)

Manages DeepAgent-specific settings:

```python
from agentic_coding_assistant.configuration import DeepAgentConfiguration

config = DeepAgentConfiguration(
    main_model="openai:gpt-4.1",
    max_parallel_analyzers=3,
    enable_self_healing=True,
    enable_documentation_sync=True,
)
```

#### 2. State Management (`state.py`)

Defines state structures for agents and sub-agents:

- `AgentState`: Main agent state with messages and analysis data
- `CoordinatorState`: Coordinator-specific state
- `AnalyzerState`: Analyzer sub-agent state

#### 3. Sub-Agents (`subagents/`)

Specialized agents for specific tasks:

- **Analyzer** (`analyzer.py`): Code analysis and impact detection
- **Refactorer** (`refactorer.py`): Code refactoring with self-healing
- **Documenter** (`documenter.py`): Documentation synchronization

### Sub-Agent Patterns

#### Creating a Sub-Agent

```python
from deepagents import SubAgent

analyzer = SubAgent(
    name="analyzer",
    description="Specialized code analysis agent",
    system_prompt="You are a code analyzer...",
    tools=[analyze_tool, read_file_tool],
)
```

#### Using Sub-Agents in Coordinator

```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

agent = create_deep_agent(
    model="openai:gpt-4.1",
    tools=tools,
    system_prompt=orchestrator_prompt,
    subagents=[analyzer, refactorer, documenter],
    backend=lambda rt: FilesystemBackend(
        root_dir=get_agent_workspace("coordinator"),
        virtual_mode=True,
    ),
    checkpointer=checkpointer,
    name="AdvancedCoordinator",
    debug=True,
)
```

## Usage Examples

### Basic Analysis with DeepAgent

```python
from agentic_coding_assistant.agents.coordinator import ImpactAnalysisCoordinator

coordinator = ImpactAnalysisCoordinator(
    model="openai/gpt-4.1-mini",
    project_root="/path/to/project",
)

# Create DeepAgent-based coordinator
agent = await coordinator.create_deep_coordinator(
    tools=analysis_tools,
    checkpointer=None,  # Uses default MemorySaver
)

# Run analysis
result = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "Analyze function X"}]},
    config={"configurable": {"thread_id": "analysis-1"}},
)
```

### Advanced Workflow

```python
from agentic_coding_assistant.agents.advanced_coordinator import AdvancedCoordinator

coordinator = AdvancedCoordinator(
    project_root="/path/to/project",
    model="openai/gpt-4.1",
)

# Create comprehensive coordinator with all sub-agents
agent = await coordinator.create_deep_advanced_coordinator(
    tools=all_tools,
    checkpointer=None,
)

# Execute complete workflow
result = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "Refactor and document module Y"}]},
    config={"configurable": {"thread_id": "workflow-1"}},
)
```

## Workspace Management

### Environment Configuration

Set the workspace root via environment variable:

```bash
export WORKSPACE_ROOT=/custom/path/to/workspace
```

Or use the default: `{PROJECT_ROOT}/workspace`

### Agent Workspaces

Each agent gets its own workspace directory:

```
workspace/
├── coordinator/          # Main coordinator workspace
├── analysis_agent/       # Analysis agent workspace
├── advanced_coordinator/ # Advanced coordinator workspace
└── analyzer_01/          # Dynamic sub-agent workspaces
```

### Workspace Utilities

```python
from agentic_coding_assistant.utils.workspace import (
    get_workspace_root,
    get_agent_workspace,
    ensure_workspace_exists,
)

# Get workspace root
workspace = get_workspace_root()

# Get agent-specific workspace
agent_ws = get_agent_workspace("my_agent")

# Ensure workspace exists
ensure_workspace_exists(agent_ws)
```

## Middleware

DeepAgent automatically configures middleware:

1. **TodoListMiddleware**: Automatic task planning
2. **FilesystemMiddleware**: Virtual file operations
3. **SubAgentMiddleware**: Dynamic sub-agent delegation
4. **SummarizationMiddleware**: Context compression
5. **AnthropicPromptCachingMiddleware**: Cost optimization
6. **PatchToolCallsMiddleware**: Tool call corrections

## State Persistence

### Using Checkpointers

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

# In-memory persistence (default)
checkpointer = MemorySaver()

# Persistent storage
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")

agent = await coordinator.create_deep_coordinator(
    tools=tools,
    checkpointer=checkpointer,
)
```

### Thread Management

```python
# Use thread_id for session management
config = {
    "configurable": {
        "thread_id": "user-session-123",
    },
    "recursion_limit": 100,
}

result = await agent.ainvoke(input_data, config=config)
```

## Best Practices

### 1. Sub-Agent Design

- Keep sub-agents focused on specific tasks
- Provide clear descriptions for delegation
- Filter tools appropriately for each sub-agent

### 2. Prompt Engineering

- Use date context in prompts
- Clearly define sub-agent capabilities
- Include workspace information

### 3. Error Handling

- Implement fallback strategies
- Use human-in-the-loop for critical decisions
- Log errors with appropriate context

### 4. Performance

- Use prompt caching for repeated queries
- Limit recursion depth appropriately
- Monitor token usage

## Migration from Original Structure

### Key Changes

1. **Configuration**: Moved from ad-hoc settings to `DeepAgentConfiguration`
2. **State**: Unified state management with `AgentState` and sub-states
3. **Coordinators**: Enhanced with `create_deep_coordinator()` methods
4. **Sub-Agents**: New modular sub-agent system
5. **Workspace**: Centralized workspace management

### Backward Compatibility

The original coordinator methods remain available:

```python
# Original method still works
result = coordinator.analyze(request)

# New DeepAgent method
agent = await coordinator.create_deep_coordinator(tools)
```

## Testing

Run the demo to verify integration:

```bash
python examples/deep_agent_demo.py
```

## References

- [DeepAgent Framework](https://github.com/deepagents/deepagents)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Project Documentation](./PROJECT_SUMMARY.md)

## Troubleshooting

### Common Issues

1. **Workspace not found**: Ensure `WORKSPACE_ROOT` is set or use default
2. **Sub-agent errors**: Check tool filtering and permissions
3. **Checkpointer issues**: Verify database connection for persistent storage
4. **Token limits**: Use summarization middleware for long conversations

### Debug Mode

Enable debug mode for detailed logging:

```python
agent = create_deep_agent(
    # ... other params
    debug=True,  # Enable debug logging
)
```

## Future Enhancements

- [ ] Dynamic sub-agent spawning at runtime
- [ ] Multi-agent collaboration patterns
- [ ] Advanced planning strategies
- [ ] Integration with MCP servers
- [ ] Enhanced error recovery mechanisms
