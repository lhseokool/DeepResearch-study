# LangGraph 활용 패턴

## 1. StateGraph 정의

### 기본 구조

```python
from langgraph.graph import StateGraph, START, END

# Main Graph
deep_researcher_builder = StateGraph(
    state_schema=AgentState,           # 상태 스키마
    input_schema=AgentInputState,      # 입력 스키마
    context_schema=Configuration,      # 컨텍스트 스키마
)
```

**스키마 역할:**
- `state_schema`: 그래프 내부 상태 정의
- `input_schema`: 그래프 입력 타입 제한
- `context_schema`: 모든 노드에서 접근 가능한 설정

### Subgraph 정의

```python
# Supervisor Subgraph
supervisor_builder = StateGraph(
    state_schema=SupervisorState,
    context_schema=Configuration,
)

# Researcher Subgraph
researcher_builder = StateGraph(
    state_schema=ResearcherState,
    output_schema=ResearcherOutputState,  # 출력 스키마
    context_schema=Configuration,
)
```

**output_schema:**
- Subgraph의 반환값 타입 정의
- 부모 그래프로 전달될 데이터 명시

## 2. 노드 추가 및 연결

### add_node

```python
# 함수를 노드로 추가
deep_researcher_builder.add_node("clarify_with_user", clarify_with_user)
deep_researcher_builder.add_node("write_research_brief", write_research_brief)

# Subgraph를 노드로 추가
deep_researcher_builder.add_node("research_supervisor", supervisor_subgraph)
deep_researcher_builder.add_node("final_report_generation", final_report_generation)
```

### add_edge

```python
# 정적 엣지 (항상 같은 노드로 이동)
deep_researcher_builder.add_edge(START, "clarify_with_user")
deep_researcher_builder.add_edge("research_supervisor", "final_report_generation")
deep_researcher_builder.add_edge("final_report_generation", END)

# Supervisor Subgraph
supervisor_builder.add_edge(START, "supervisor")
supervisor_builder.add_edge("supervisor", "supervisor_tools")

# Researcher Subgraph
researcher_builder.add_edge(START, "researcher")
researcher_builder.add_edge("compress_research", END)
```

## 3. Command 기반 동적 라우팅

### Command 객체

```python
from langgraph.types import Command

# 기본 사용
return Command(
    goto="next_node",           # 다음 노드 지정
    update={"key": "value"}     # 상태 업데이트
)
```

### 조건부 라우팅

```python
async def clarify_with_user(state, config) -> Command[Literal["write_research_brief", END]]:
    if response.need_clarification:
        # 사용자에게 질문하고 종료
        return Command(goto=END, update={"messages": [AIMessage(...)]})
    else:
        # 연구 계획 작성으로 이동
        return Command(goto="write_research_brief", update={"messages": [AIMessage(...)]})
```

### 타입 힌트

```python
# 가능한 다음 노드를 타입으로 명시
Command[Literal["researcher_tools"]]
Command[Literal["supervisor", END]]
Command[Literal["write_research_brief", END]]
```

## 4. Subgraph 패턴

### Subgraph 컴파일

```python
# Supervisor Subgraph 컴파일
supervisor_subgraph = supervisor_builder.compile()

# Researcher Subgraph 컴파일
researcher_subgraph = researcher_builder.compile()
```

### Subgraph를 노드로 사용

```python
# Main Graph에 Subgraph 추가
deep_researcher_builder.add_node("research_supervisor", supervisor_subgraph)

# Subgraph 내에서 다른 Subgraph 호출
research_tasks = [
    researcher_subgraph.ainvoke(
        {
            "researcher_messages": [HumanMessage(content=tool_call["args"]["research_topic"])],
            "research_topic": tool_call["args"]["research_topic"],
        },
        config,
    )
    for tool_call in allowed_conduct_research_calls
]
tool_results = await asyncio.gather(*research_tasks)
```

### 상태 전달

```python
# Main Graph → Supervisor Subgraph
return Command(
    goto="research_supervisor",
    update={
        "research_brief": response.research_brief,
        "supervisor_messages": {...},
    },
)

# Supervisor → Researcher Subgraph (ainvoke 호출)
researcher_subgraph.ainvoke(
    {
        "researcher_messages": [HumanMessage(...)],
        "research_topic": tool_call["args"]["research_topic"],
    },
    config,
)

# Researcher → Supervisor (자동 병합)
# ResearcherOutputState의 필드가 SupervisorState에 자동 추가됨
```

## 5. Context Schema 활용

### Configuration 정의

```python
class Configuration(BaseModel):
    research_model: str = "openai:gpt-4.1"
    max_concurrent_research_units: int = 5
    max_researcher_iterations: int = 6
    # ...
    
    @classmethod
    def from_runnable_config(cls, config: RunnableConfig) -> "Configuration":
        configurable = config.get("configurable", {}) if config else {}
        # ...
        return cls(**{k: v for k, v in values.items() if v is not None})
```

### 노드에서 접근

```python
async def supervisor(state: SupervisorState, config: RunnableConfig) -> dict:
    # Configuration 추출
    configurable = Configuration.from_runnable_config(config)
    
    # 설정값 사용
    max_units = configurable.max_concurrent_research_units
    research_model = configurable.research_model
```

### 런타임 설정

```python
result = await deep_researcher.ainvoke(
    {"messages": {"role": "user", "content": "AI 안전성 연구"}},
    config={
        "configurable": {
            "research_model": "anthropic:claude-3-5-sonnet-20241022",
            "max_concurrent_research_units": 3,
        }
    }
)
```

## 6. 병렬 실행 패턴

### asyncio.gather 활용

```python
# 여러 Researcher를 병렬로 실행
research_tasks = [
    researcher_subgraph.ainvoke({...}, config)
    for tool_call in allowed_conduct_research_calls
]
tool_results = await asyncio.gather(*research_tasks)

# 도구를 병렬로 실행
tool_execution_tasks = [
    execute_tool_safely(tools_by_name[tool_call["name"]], tool_call["args"], config)
    for tool_call in tool_calls
]
observations = await asyncio.gather(*tool_execution_tasks)
```

### 동시성 제한

```python
# 최대 동시 실행 수 제한
allowed_conduct_research_calls = conduct_research_calls[:configurable.max_concurrent_research_units]
overflow_conduct_research_calls = conduct_research_calls[configurable.max_concurrent_research_units:]

# 초과된 호출은 오류 메시지로 처리
for overflow_call in overflow_conduct_research_calls:
    all_tool_messages.append(
        ToolMessage(
            content=f"Error: Did not run this research...",
            name="ConductResearch",
            tool_call_id=overflow_call["id"],
        )
    )
```

## 7. 상태 업데이트 패턴

### Command를 통한 업데이트

```python
return Command(
    goto="next_node",
    update={
        "research_brief": response.research_brief,
        "supervisor_messages": {
            "type": "override",
            "value": [SystemMessage(...), HumanMessage(...)],
        },
    },
)
```

### 딕셔너리 반환

```python
# 노드가 딕셔너리를 반환하면 상태에 자동 병합
return {
    "supervisor_messages": [response],
    "research_iterations": state.get("research_iterations", 0) + 1,
}
```

### override_reducer 활용

```python
# 기존 값에 추가
update = {"notes": ["새로운 노트"]}

# 값 덮어쓰기
update = {"notes": {"type": "override", "value": []}}
```

## 8. 종료 조건 처리

### 조건부 종료

```python
async def supervisor_tools(state, config) -> Command[Literal["supervisor", END]]:
    # 종료 조건 확인
    exceeded_allowed_iterations = research_iterations > configurable.max_researcher_iterations
    no_tool_calls = not most_recent_message.tool_calls
    research_complete_tool_call = any(...)
    
    if exceeded_allowed_iterations or no_tool_calls or research_complete_tool_call:
        return Command(goto=END, update={...})
    
    # 계속 진행
    return Command(goto="supervisor", update={...})
```

### 조기 종료

```python
async def researcher_tools(state, config) -> Command:
    # 도구 호출이 없으면 조기 종료
    if not has_tool_calls and not has_native_search:
        return Command(goto="compress_research")
    
    # 반복 횟수 초과 시 종료
    if exceeded_iterations or research_complete_called:
        return Command(goto="compress_research", update={...})
    
    # 연구 계속
    return Command(goto="researcher", update={...})
```

## 9. 그래프 컴파일 및 실행

### 컴파일

```python
# Main Graph 컴파일
deep_researcher = deep_researcher_builder.compile()

# Subgraph 컴파일
supervisor_subgraph = supervisor_builder.compile()
researcher_subgraph = researcher_builder.compile()
```

### 실행

```python
# 비동기 실행
result = await deep_researcher.ainvoke(
    {"messages": {"role": "user", "content": "AI 안전성 연구"}},
    config={
        "configurable": {
            "research_model": "openai:gpt-4.1",
        }
    }
)

# 동기 실행
result = deep_researcher.invoke({"messages": [...]})
```

## 10. 고급 패턴

### ReAct 루프

```python
# researcher ↔ researcher_tools 반복
researcher_builder.add_node("researcher", researcher)
researcher_builder.add_node("researcher_tools", researcher_tools)

# researcher_tools에서 조건부 라우팅
async def researcher_tools(state, config) -> Command:
    if should_continue:
        return Command(goto="researcher", update={...})
    else:
        return Command(goto="compress_research", update={...})
```

### 계층적 Subgraph

```
Main Graph
  └─ Supervisor Subgraph
      └─ Researcher Subgraph × N (병렬)
```

### 상태 격리

```python
# 각 Subgraph는 독립적인 State 사용
- AgentState (Main)
- SupervisorState (Supervisor)
- ResearcherState (Researcher)

# 명시적 데이터 전달
researcher_subgraph.ainvoke(
    {"research_topic": topic},  # 필요한 데이터만 전달
    config,
)
```

## 11. 디버깅 및 모니터링

### 상태 추적

```python
# 반복 횟수 추적
return {
    "research_iterations": state.get("research_iterations", 0) + 1,
    "tool_call_iterations": state.get("tool_call_iterations", 0) + 1,
}

# 데이터 크기 추적
return {
    "compressed_research_length": len(compressed_research),
    "raw_notes_length": len(raw_notes_str),
}
```

### 에러 처리

```python
try:
    tool_results = await asyncio.gather(*research_tasks)
except Exception as e:
    if is_token_limit_exceeded(e, configurable.research_model):
        return Command(goto=END, update={...})
```
