# DeepResearch_DeepAgent 아키텍처 분석

> DeepAgents 프레임워크를 활용한 계층적 멀티-에이전트 연구 시스템

---

## 📋 목차

1. [전체 구조 및 아키텍처](#1-전체-구조-및-아키텍처)
2. [에이전트 패턴](#2-에이전트-패턴)
3. [LangChain & LangGraph 사용](#3-langchain--langgraph-사용)
4. [DeepAgents 프레임워크 적용](#4-deepagents-프레임워크-적용)
5. [핵심 컴포넌트](#5-핵심-컴포넌트)
6. [워크플로우 예시](#6-워크플로우-예시)
7. [주요 디자인 패턴](#7-주요-디자인-패턴)

---

## 1. 전체 구조 및 아키텍처

### 1.1 디렉토리 구조

```
DeepResearch_DeepAgent/
├── src/
│   ├── separate_agent.py          # 메인 에이전트 생성
│   ├── state.py                   # 상태 정의
│   ├── configuration.py           # 설정 관리
│   ├── utils.py                   # 유틸리티
│   ├── prompts/                   # 프롬프트 템플릿
│   ├── subagents/                 # 서브에이전트
│   ├── skills/                    # 스킬 관리
│   └── tools/                     # 도구
└── workspace/                     # 작업 공간
```

### 1.2 아키텍처 다이어그램

```
Main Orchestrator (DeepAgent)
├── Researcher SubAgent 1 (병렬)
├── Researcher SubAgent 2 (병렬)
├── Dynamic SubAgent (동적 생성)
├── Compressor SubAgent
└── Critic SubAgent (선택적)
```

### 1.3 워크플로우 단계

| Stage | 이름 | 설명 |
|-------|------|------|
| 0 | Context Restoration | 기존 작업 확인 |
| 1 | Clarification | 질문 명확화 |
| 2 | Planning | 연구 계획 수립 |
| 3 | Research | 병렬 연구 수행 |
| 4 | Compression | 결과 종합 |
| 5 | Final Report | 보고서 작성 |
| 6 | Critique | 품질 검증 |

---

## 2. 에이전트 패턴

### 2.1 Orchestrator Pattern

메인 에이전트가 전체 워크플로우를 관리합니다.

```python
agent = create_deep_agent(
    model=model,
    tools=tools,
    system_prompt=orchestrator_prompt,
    subagents=subagents,
    backend=FilesystemBackend(...),
    checkpointer=checkpointer,
)
```

### 2.2 서브에이전트 타입

**1. Researcher** - 웹 검색 및 정보 수집
- 도구: tavily_search, think_tool, ResearchComplete
- 출력: /output/notes/{topic}.md

**2. Compressor** - 연구 결과 종합
- 도구: 파일시스템 도구만
- 출력: /output/compressed_research.md

**3. Critic** - 품질 보증
- 도구: 파일시스템 도구만
- 출력: /output/feedback.md

**4. Dynamic SubAgent** - 런타임 생성
- 도구: 스킬에 따라 동적 할당
- 출력: 커스텀 워크스페이스

### 2.3 병렬 실행 전략

| 복잡도 | 연구자 수 | 예시 |
|--------|----------|------|
| Simple | 1 | 단순 질문 |
| Moderate | 2-3 | 비교 분석 |
| Complex | 4-5 | 다면적 연구 |

---

## 3. LangChain & LangGraph 사용

### 3.1 LangChain

#### Chat Model
```python
from langchain.chat_models import init_chat_model

model = init_chat_model(
    model="openai:gpt-4.1",
    max_tokens=4000,
)
```

#### Tools
```python
@tool(description="Strategic reflection")
def think_tool(reflection: str) -> str:
    return f"Reflection: {reflection}"

@tool(description="Web search")
async def tavily_search(queries: list[str]) -> str:
    # 검색 로직
    pass
```

#### Structured Output
```python
class Summary(BaseModel):
    summary: str
    key_excerpts: str

model.with_structured_output(Summary)
```

### 3.2 LangGraph

#### State 정의
```python
class AgentState(MessagesState):
    supervisor_messages: Annotated[list, override_reducer]
    research_brief: str | None
    raw_notes: Annotated[list[str], override_reducer]
    notes: Annotated[list[str], override_reducer]
    final_report: str
```

#### Checkpointer
```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()  # 메모리 내
# 또는
checkpointer = SqliteSaver.from_conn_string("db.sqlite")
```

#### Config
```python
config = {
    "configurable": {"thread_id": "default"},
    "recursion_limit": 100,
}

result = await agent.ainvoke(input, config=config)
```

---

## 4. DeepAgents 프레임워크 적용

### 4.1 create_deep_agent

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="openai:gpt-4.1",
    tools=tools,
    system_prompt=prompt,
    subagents=subagents,
    backend=FilesystemBackend(...),
    checkpointer=checkpointer,
)
```

### 4.2 자동 미들웨어

- TodoListMiddleware - 계획 수립
- FilesystemMiddleware - 파일 작업
- SubAgentMiddleware - 서브에이전트 할당
- SummarizationMiddleware - 컨텍스트 압축
- AnthropicPromptCachingMiddleware - 비용 최적화

### 4.3 SubAgent 정의

```python
from deepagents import SubAgent

researcher = SubAgent(
    name="researcher",
    description="전문 연구 에이전트",
    system_prompt=RESEARCHER_PROMPT,
    tools=["tavily_search", "think_tool"],
)
```

### 4.4 FilesystemBackend

```
workspace/main_agent/
├── status/
│   ├── current_stage.txt
│   └── context_mode.txt
└── output/
    ├── research_brief.md
    ├── notes/
    ├── compressed_research.md
    └── final_report.md
```

### 4.5 동적 서브에이전트

```python
def create_dynamic_subagent(name, goal, tools):
    return create_deep_agent(
        model=model,
        tools=tools,
        system_prompt=f"Goal: {goal}",
        backend=FilesystemBackend(...),
    )

# 사용
spawn_subagent(
    name="analyst",
    goal="Analyze data",
    skills=["data_analysis"]
)
```

---

## 5. 핵심 컴포넌트

### 5.1 State (상태)

```python
class AgentState(MessagesState):
    supervisor_messages: list
    research_brief: str
    notes: list[str]
    final_report: str
```

### 5.2 Configuration (설정)

```python
class DeepAgentConfiguration(BaseModel):
    main_model: str = "openai:gpt-4.1"
    search_api: SearchAPI = SearchAPI.TAVILY
    max_parallel_researchers: int = 5
    max_researcher_iterations: int = 10
    enable_critique_phase: bool = False
```

### 5.3 Skills Registry

```python
class SkillRegistry:
    _skills = {
        "web_research": ["tavily_search"],
        "data_analysis": ["python_repl"],
        "writing": [],
    }
    
    def get_tools_for_skill(self, skill):
        return [self._tools[name] for name in self._skills[skill]]
```

### 5.4 Prompts

각 에이전트는 상세한 시스템 프롬프트를 가집니다:

- **Orchestrator**: 워크플로우 관리, 서브에이전트 조율
- **Researcher**: 웹 검색, 정보 수집, think_tool 사용
- **Compressor**: 노트 종합, 중복 제거, 출처 보존
- **Critic**: 품질 검증, 피드백 제공

---

## 6. 워크플로우 예시

### 전체 실행 흐름

```python
# 1. 에이전트 생성
agent = await create_deep_research_agent(
    tools=[tavily_search, think_tool, tool(ResearchComplete)],
    model="openai:gpt-4.1",
)

# 2. 실행
result = await agent.ainvoke(
    {"messages": [{"role": "user", "content": question}]},
    config={"configurable": {"thread_id": "test"}},
)

# 3. 결과 확인
final_report = result["files"]["/output/final_report.md"]
```

### 단계별 실행

**STAGE 0: Context Restoration**
```python
ls /
read_file /status/current_stage.txt
# 작업 모드 결정: NEW/CONTINUING/REVISING
```

**STAGE 2: Planning**
```python
write_file /output/research_brief.md
write_todos
# 복잡도 평가 → 연구자 수 결정
```

**STAGE 3: Research (병렬)**
```python
task(description="Research topic 1", subagent_type="researcher")
task(description="Research topic 2", subagent_type="researcher")
task(description="Research topic 3", subagent_type="researcher")
```

**STAGE 4: Compression**
```python
task(description="Synthesize findings", subagent_type="compressor")
```

**STAGE 5: Final Report**
```python
read_file /output/compressed_research.md
write_file /output/final_report.md
```

---

## 7. 주요 디자인 패턴

### 7.1 계층적 에이전트 구조
- Orchestrator → SubAgents → Tools
- 명확한 책임 분리
- 독립적인 워크스페이스

### 7.2 파일시스템 기반 메모리
- 모든 상태를 파일로 저장
- 세션 간 컨텍스트 보존
- 투명하고 디버깅 가능

### 7.3 스킬 기반 도구 관리
- 추상적 스킬 ↔ 구체적 도구 분리
- 동적 도구 할당
- 확장 가능한 구조

### 7.4 병렬 실행 최적화
- 여러 연구자 동시 실행
- 복잡도 기반 동적 할당
- 효율적인 리소스 사용

### 7.5 품질 보증
- think_tool을 통한 자기 성찰
- 비평가를 통한 품질 검증
- 반복적 개선 가능

### 7.6 컨텍스트 관리
- 요약을 통한 압축
- 토큰 제한 관리
- 프롬프트 캐싱

---

## 8. 핵심 강점

✅ **LangChain/LangGraph 활용**
- 강력한 도구 시스템
- 상태 관리 및 영속화
- 구조화된 출력

✅ **DeepAgents 프레임워크**
- 미들웨어 자동 주입
- 서브에이전트 관리
- 백엔드 추상화

✅ **파일시스템 메모리**
- 세션 간 연속성
- 장기 메모리 역할
- 투명한 작업 추적

✅ **스킬 기반 아키텍처**
- 확장 가능한 구조
- 동적 도구 할당
- 재사용 가능한 컴포넌트

✅ **병렬 실행**
- 효율성 극대화
- 복잡도 기반 할당
- 확장 가능한 처리

✅ **명확한 워크플로우**
- 단계별 추적 가능
- 디버깅 용이
- 체계적인 진행

---

## 9. 사용 예시

```python
# test_separate.py
import asyncio
from separate_agent import create_deep_research_agent
from utils import tavily_search, think_tool
from state import ResearchComplete

async def main():
    question = "LangChain V1.0 변경사항 조사"
    
    tools = [tavily_search, think_tool, tool(ResearchComplete)]
    
    agent = await create_deep_research_agent(
        tools=tools,
        model="openai:gpt-4.1",
        max_researcher_iterations=3,
        enable_critique=True,
    )
    
    config = {
        "configurable": {"thread_id": "test"},
        "recursion_limit": 100,
    }
    
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": question}]},
        config=config,
    )
    
    # 결과 확인
    final_report = result["files"]["/output/final_report.md"]["content"]
    print(final_report)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 10. 결론

DeepResearch_DeepAgent는 **DeepAgents 프레임워크**를 활용하여 복잡한 연구 작업을 수행하는 **계층적 멀티-에이전트 시스템**입니다.

**핵심 기술 스택:**
- LangChain: 도구, 모델, 구조화된 출력
- LangGraph: 상태 관리, 체크포인터, 그래프 실행
- DeepAgents: 서브에이전트, 미들웨어, 백엔드

**주요 특징:**
- 계층적 에이전트 구조
- 파일시스템 기반 장기 메모리
- 스킬 기반 도구 관리
- 병렬 실행 최적화
- 품질 보증 메커니즘

이 아키텍처는 확장 가능하고, 유지보수가 쉬우며, 복잡한 연구 워크플로우를 효과적으로 처리할 수 있습니다.
