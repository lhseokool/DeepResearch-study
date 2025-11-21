# LangChain 활용 패턴

## 1. 모델 초기화 및 설정

### init_chat_model

```python
llm_model = init_chat_model(
    configurable_fields=("model", "max_tokens", "api_key"),
)
```

**특징:**
- 다양한 LLM 제공자 통합 (OpenAI, Anthropic, Google 등)
- 런타임에 모델 변경 가능
- API 키 동적 설정

**사용 예시:**

```python
model_config = {
    "model": "openai:gpt-4.1",
    "max_tokens": 16000,
    "api_key": get_api_key_for_model("openai:gpt-4.1", config),
}

research_model = llm_model.with_config(model_config)
```

## 2. 구조화된 출력 (Structured Output)

### with_structured_output

```python
clarification_model = llm_model.with_structured_output(ClarifyWithUser)
```

**Pydantic 모델 정의:**

```python
class ClarifyWithUser(BaseModel):
    need_clarification: bool = Field(description="사용자에게 명확화 질문을 해야 하는지 여부")
    question: str = Field(description="보고서 범위를 명확히 하기 위해 사용자에게 물을 질문")
    verification: str = Field(description="연구를 시작할 것임을 확인하는 메시지")
```

**장점:**
- 타입 안전성 보장
- 자동 파싱 및 검증
- 재시도 로직과 결합 가능

## 3. 도구 바인딩 (Tool Binding)

### bind_tools

```python
# Supervisor 도구
lead_researcher_tools = [ConductResearch, ResearchComplete, think_tool]
research_model = llm_model.bind_tools(lead_researcher_tools)

# Researcher 도구
tools = await get_all_tools(config)  # tavily_search, think_tool, MCP 도구
research_model = llm_model.bind_tools(tools)
```

**도구 정의 예시:**

```python
class ConductResearch(BaseModel):
    """특정 주제에 대한 연구를 수행하기 위해 이 도구를 호출합니다."""
    research_topic: str = Field(description="연구할 주제")

@tool(description="Strategic reflection tool for research planning")
def think_tool(reflection: str) -> str:
    """전략적 반성 도구"""
    return f"Reflection recorded: {reflection}"
```

## 4. 재시도 로직 (Retry Logic)

### with_retry

```python
research_model = (
    llm_model
    .with_structured_output(ClarifyWithUser)
    .with_retry(stop_after_attempt=configurable.max_structured_output_retries)
    .with_config(model_config)
)
```

**활용 사례:**
- 구조화된 출력 파싱 실패 시
- API 일시적 오류 시
- 토큰 제한 초과 시

## 5. 메시지 관리

### MessagesState

```python
class AgentState(MessagesState):
    """MessagesState에서 messages 필드 자동 상속"""
    supervisor_messages: Annotated[list[MessageLikeRepresentation], override_reducer]
    # ...
```

**자동 기능:**
- 메시지 자동 추가
- 중복 제거
- 타입 변환

### filter_messages

```python
# 특정 타입의 메시지만 필터링
tool_messages = filter_messages(researcher_messages, include_types=["tool", "ai"])

# 노트 추출
raw_notes_content = "\n".join([
    str(message.content)
    for message in filter_messages(researcher_messages, include_types=["tool", "ai"])
])
```

### get_buffer_string

```python
# 메시지를 문자열로 변환
prompt_content = clarify_with_user_instructions.format(
    messages=get_buffer_string(messages),
    date=get_today_str()
)
```

## 6. 도구 구현 패턴

### @tool 데코레이터

```python
@tool(description=TAVILY_SEARCH_DESCRIPTION)
async def tavily_search(
    queries: list[str],
    max_results: Annotated[int, InjectedToolArg] = 5,
    topic: Annotated[Literal["general", "news", "finance"], InjectedToolArg] = "general",
    config: RunnableConfig = None,
) -> str:
    """Tavily 검색 도구"""
    # 구현
```

**InjectedToolArg:**
- LLM이 제공하지 않는 인자
- 런타임에 자동 주입
- 설정값이나 컨텍스트 전달

### StructuredTool

```python
# MCP 도구를 StructuredTool로 래핑
def wrap_mcp_authenticate_tool(tool: StructuredTool) -> StructuredTool:
    original_coroutine = tool.coroutine
    
    async def authentication_wrapper(**kwargs):
        try:
            return await original_coroutine(**kwargs)
        except McpError as e:
            raise ToolException(error_message) from e
    
    tool.coroutine = authentication_wrapper
    return tool
```

## 7. 프롬프트 관리

### 프롬프트 템플릿

```python
lead_researcher_prompt = """You are a research supervisor...
For context, today's date is {date}.
Maximum {max_concurrent_research_units} parallel agents per iteration
"""

# 사용
supervisor_system_prompt = lead_researcher_prompt.format(
    date=get_today_str(),
    max_concurrent_research_units=configurable.max_concurrent_research_units,
    max_researcher_iterations=configurable.max_researcher_iterations,
)
```

### 시스템 메시지

```python
messages = [SystemMessage(content=researcher_prompt)] + researcher_messages
response = await research_model.ainvoke(messages)
```

## 8. 비동기 처리

### ainvoke

```python
# 단일 호출
response = await research_model.ainvoke(messages)

# 병렬 호출
research_tasks = [
    researcher_subgraph.ainvoke({...}, config)
    for tool_call in allowed_conduct_research_calls
]
tool_results = await asyncio.gather(*research_tasks)
```

### 도구 실행

```python
async def execute_tool_safely(tool, args, config):
    """오류 처리를 포함하여 도구를 안전하게 실행"""
    try:
        return await tool.ainvoke(args, config)
    except Exception as e:
        return f"Error executing tool: {str(e)}"
```

## 9. 모델별 API 키 관리

```python
def get_api_key_for_model(model_name: str, config: RunnableConfig):
    """환경 또는 구성에서 특정 모델에 대한 API 키를 가져옵니다."""
    model_name = model_name.lower()
    
    if model_name.startswith("openai:"):
        return os.getenv("OPENAI_API_KEY")
    elif model_name.startswith("anthropic:"):
        return os.getenv("ANTHROPIC_API_KEY")
    elif model_name.startswith("google"):
        return os.getenv("GOOGLE_API_KEY")
    
    return None
```

## 10. 에러 처리

### 토큰 제한 초과

```python
def is_token_limit_exceeded(exception: Exception, model_name: str = None) -> bool:
    """예외가 토큰/컨텍스트 제한 초과를 나타내는지 판단"""
    error_str = str(exception).lower()
    
    if provider == "openai":
        return _check_openai_token_limit(exception, error_str)
    elif provider == "anthropic":
        return _check_anthropic_token_limit(exception, error_str)
    # ...
```

### 메시지 절단

```python
def remove_up_to_last_ai_message(messages: list[MessageLikeRepresentation]):
    """마지막 AI 메시지까지 제거하여 메시지 기록을 잘라냅니다."""
    for i in range(len(messages) - 1, -1, -1):
        if isinstance(messages[i], AIMessage):
            return messages[:i]
    return messages
```
