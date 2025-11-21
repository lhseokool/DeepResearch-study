# Examples

이 디렉토리는 Agentic Coding Assistant의 사용 예제를 포함합니다.

## Demo Script

```bash
# Run the demo
python examples/demo.py
```

## CLI Usage

### SPEED Mode

```bash
python -m agentic_coding_assistant.cli \
  --file path/to/file.py \
  --symbol function_name \
  --mode SPEED \
  --max-depth 3
```

### PRECISION Mode

```bash
python -m agentic_coding_assistant.cli \
  --file path/to/file.py \
  --symbol function_name \
  --mode PRECISION \
  --project-root /path/to/project
```

### Human-in-the-Loop

```bash
python -m agentic_coding_assistant.cli \
  --file path/to/file.py \
  --symbol function_name \
  --mode PRECISION \
  --human-in-loop
```

### Save Results to File

```bash
python -m agentic_coding_assistant.cli \
  --file path/to/file.py \
  --symbol function_name \
  --output results.json
```

## API Server

### Start the Server

```bash
python -m agentic_coding_assistant.api
```

Or with uvicorn:

```bash
uvicorn agentic_coding_assistant.api:app --reload
```

### API Endpoints

#### Analyze Impact

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "SPEED",
    "file_path": "/path/to/file.py",
    "symbol_name": "function_name",
    "max_depth": 3
  }'
```

#### Check Available Modes

```bash
curl "http://localhost:8000/modes"
```

## LangGraph Platform

### Start LangGraph Server

```bash
langgraph dev
```

Access the LangGraph Studio at: http://localhost:8123

## Python API

```python
from agentic_coding_assistant import (
    ImpactAnalysisCoordinator,
    AnalysisRequest,
    AnalysisMode
)

# Create coordinator
coordinator = ImpactAnalysisCoordinator()

# SPEED mode
request = AnalysisRequest(
    mode=AnalysisMode.SPEED,
    file_path="path/to/file.py",
    symbol_name="function_name"
)

result = coordinator.analyze(request)

print(f"Found {len(result.dependencies)} dependencies")
for dep in result.dependencies:
    print(f"  - {dep.symbol_name} ({dep.impact_level})")
```

## Using LangGraph Workflow

```python
from agentic_coding_assistant import analysis_graph
from agentic_coding_assistant.models.schema import AnalysisRequest, AnalysisMode
from agentic_coding_assistant.nodes.analysis_nodes import AnalysisState

# Create request
request = AnalysisRequest(
    mode=AnalysisMode.SPEED,
    file_path="path/to/file.py",
    symbol_name="function_name"
)

# Create initial state
state: AnalysisState = {
    "request": request,
    "result": None,
    "should_fallback": False,
    "error_count": 0
}

# Run workflow
final_state = analysis_graph.invoke(state)

# Get result
result = final_state["result"]
print(result)
```
