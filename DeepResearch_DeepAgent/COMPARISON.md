# DeepResearch_Original vs DeepResearch_DeepAgent 비교 분석

> 순수 LangGraph 구현 vs DeepAgents 프레임워크 기반 구현 비교

---

## 📋 목차

1. [개요](#1-개요)
2. [아키텍처 비교](#2-아키텍처-비교)
3. [코드 구조 비교](#3-코드-구조-비교)
4. [주요 차이점](#4-주요-차이점)
5. [장단점 분석](#5-장단점-분석)
6. [선택 가이드](#6-선택-가이드)

---

## 1. 개요

### DeepResearch_Original
- **프레임워크**: 순수 LangGraph + LangChain
- **접근 방식**: 직접 StateGraph 구성 및 노드/엣지 정의
- **특징**: 명시적 제어, 세밀한 커스터마이징

### DeepResearch_DeepAgent
- **프레임워크**: DeepAgents (LangGraph 위에 구축)
- **접근 방식**: SubAgent 패턴 및 미들웨어 시스템
- **특징**: 추상화, 자동화, 파일시스템 기반 메모리

---

## 2. 아키텍처 비교

### 2.1 전체 구조

#### DeepResearch_Original
```
Main Graph (StateGraph)
├── clarify_with_user
├── write_research_brief
├── research_supervisor (Subgraph)
│   ├── supervisor
│   └── supervisor_tools
│       └── researcher (Subgraph) × N (병렬)
│           ├── researcher
│           ├── researcher_tools
│           └── compress_research
└── final_report_generation
```

#### DeepResearch_DeepAgent
```
Main Orchestrator (DeepAgent)
├── [자동 미들웨어]
│   ├── TodoListMiddleware
│   ├── FilesystemMiddleware
│   ├── SubAgentMiddleware
│   └── SummarizationMiddleware
├── Researcher SubAgent × N
├── Compressor SubAgent
├── Critic SubAgent (선택적)
└── Dynamic SubAgent (런타임 생성)
```

### 2.2 워크플로우 비교

| 단계 | Original | DeepAgent |
|------|----------|-----------|
| **입력** | messages | messages |
| **명확화** | clarify_with_user 노드 | STAGE 1 (프롬프트 기반) |
| **계획** | write_research_brief 노드 | STAGE 2 (프롬프트 기반) |
| **연구** | supervisor → researcher 서브그래프 | task() 도구로 SubAgent 호출 |
| **압축** | compress_research 노드 (각 researcher) | Compressor SubAgent |
| **보고서** | final_report_generation 노드 | STAGE 5 (오케스트레이터) |
| **검증** | ❌ 없음 | Critic SubAgent (선택적) |

---

## 3. 코드 구조 비교

### 3.1 파일 구조

#### DeepResearch_Original (8개 파일)
```
src/
├── deep_researcher.py     # 메인 그래프 (781줄)
├── state.py               # 상태 정의
├── configuration.py       # 설정
├── prompts.py            # 프롬프트
├── utils.py              # 유틸리티
├── auth.py               # 인증
├── evaluation.py         # 평가
└── runner.py             # 실행
```

#### DeepResearch_DeepAgent (20개 파일)
```
src/
├── separate_agent.py      # 메인 에이전트 (186줄)
├── state.py
├── configuration.py
├── utils.py
├── prompts/              # 프롬프트 모듈화
│   ├── orchestrator.py
│   ├── researcher.py
│   ├── compressor.py
│   └── critic.py
├── subagents/            # 서브에이전트 정의
│   ├── researcher.py
│   ├── compressor.py
│   ├── critic.py
│   └── dynamic.py
├── skills/               # 스킬 관리
│   ├── registry.py
│   └── tool_collections.py
└── tools/
    └── subagent_tools.py
```

### 3.2 메인 그래프 생성 비교

#### DeepResearch_Original
```python
# deep_researcher.py (직접 StateGraph 구성)

# Supervisor 서브그래프
supervisor_builder = StateGraph(
    state_schema=SupervisorState, 
    context_schema=Configuration
)
supervisor_builder.add_node("supervisor", supervisor)
supervisor_builder.add_node("supervisor_tools", supervisor_tools)
supervisor_builder.add_edge(START, "supervisor")
supervisor_builder.add_edge("supervisor", "supervisor_tools")
supervisor_subgraph = supervisor_builder.compile()

# Researcher 서브그래프
researcher_builder = StateGraph(
    state_schema=ResearcherState,
    output_schema=ResearcherOutputState,
    context_schema=Configuration,
)
researcher_builder.add_node("researcher", researcher)
researcher_builder.add_node("researcher_tools", researcher_tools)
researcher_builder.add_node("compress_research", compress_research)
researcher_builder.add_edge(START, "researcher")
researcher_builder.add_edge("compress_research", END)
researcher_subgraph = researcher_builder.compile()

# 메인 그래프
deep_researcher_builder = StateGraph(
    state_schema=AgentState,
    input_schema=AgentInputState,
    context_schema=Configuration,
)
deep_researcher_builder.add_node("clarify_with_user", clarify_with_user)
deep_researcher_builder.add_node("write_research_brief", write_research_brief)
deep_researcher_builder.add_node("research_supervisor", supervisor_subgraph)
deep_researcher_builder.add_node("final_report_generation", final_report_generation)
deep_researcher_builder.add_edge(START, "clarify_with_user")
deep_researcher_builder.add_edge("research_supervisor", "final_report_generation")
deep_researcher_builder.add_edge("final_report_generation", END)
deep_researcher = deep_researcher_builder.compile()
```

**특징:**
- ✅ 명시적 제어
- ✅ 세밀한 커스터마이징
- ❌ 보일러플레이트 코드 많음
- ❌ 서브그래프 수동 관리

#### DeepResearch_DeepAgent
```python
# separate_agent.py (DeepAgents 사용)

from deepagents import create_deep_agent, SubAgent
from deepagents.backends import FilesystemBackend

# 서브에이전트 정의
researcher_config = SubAgent(
    name="researcher",
    description="전문 연구 에이전트",
    system_prompt=RESEARCHER_SYSTEM_PROMPT,
    tools=researcher_tools,
)

compressor_config = SubAgent(
    name="compressor",
    description="연구 종합 전문가",
    system_prompt=COMPRESSOR_SYSTEM_PROMPT,
    tools=[],
)

# 메인 에이전트 생성 (한 번의 호출로!)
agent = create_deep_agent(
    model=model,
    tools=tools,
    system_prompt=orchestrator_prompt,
    subagents=[researcher_config, compressor_config],
    backend=lambda rt: FilesystemBackend(
        root_dir=get_agent_workspace("main_agent"),
        virtual_mode=True,
    ),
    checkpointer=checkpointer,
    name="SeparateDeepAgentResearcher",
    debug=True,
)
```

**특징:**
- ✅ 간결한 코드
- ✅ 자동 미들웨어 주입
- ✅ 파일시스템 백엔드 자동 설정
- ❌ 내부 동작 추상화

---

## 4. 주요 차이점

### 4.1 서브에이전트 호출 방식

#### Original: 직접 서브그래프 호출
```python
# supervisor_tools 함수 내부
research_tasks = [
    researcher_subgraph.ainvoke(
        {
            "researcher_messages": [
                HumanMessage(content=tool_call["args"]["research_topic"])
            ],
            "research_topic": tool_call["args"]["research_topic"],
        },
        config,
    )
    for tool_call in allowed_conduct_research_calls
]
tool_results = await asyncio.gather(*research_tasks)
```

#### DeepAgent: task() 도구 사용
```python
# 오케스트레이터가 프롬프트에서 직접 호출
task(description="Research React features", subagent_type="researcher")
task(description="Research Vue features", subagent_type="researcher")
task(description="Research Angular features", subagent_type="researcher")
```

### 4.2 상태 관리

#### Original: 명시적 상태 전달
```python
class SupervisorState(TypedDict):
    supervisor_messages: Annotated[list, override_reducer]
    research_brief: str
    notes: Annotated[list[str], override_reducer]
    research_iterations: int
    raw_notes: Annotated[list[str], override_reducer]
    compressed_research_length: int
    raw_notes_length: int

# 노드 간 상태 업데이트
return {
    "supervisor_messages": [response],
    "research_iterations": state.get("research_iterations", 0) + 1,
}
```

#### DeepAgent: 파일시스템 기반
```python
# 상태는 파일로 저장
write_file /status/current_stage.txt
write_file /output/research_brief.md
write_file /output/notes/topic1.md

# 자동으로 checkpointer를 통해 영속화
# 세션 간 상태 보존
```

### 4.3 도구 관리

#### Original: 직접 도구 바인딩
```python
# researcher 함수 내부
tools = await get_all_tools(config)
research_model = (
    llm_model.bind_tools(tools)
    .with_retry(stop_after_attempt=retries)
    .with_config(research_model_config)
)
```

#### DeepAgent: 스킬 기반 레지스트리
```python
# skills/registry.py
class SkillRegistry:
    _skills = {
        "web_research": ["tavily_search"],
        "data_analysis": ["python_repl"],
    }
    
    def get_tools_for_skill(self, skill_name):
        return [self._tools[name] for name in self._skills[skill_name]]

# 동적 할당
tools = registry.get_tools_for_skill("web_research")
```

### 4.4 프롬프트 구조

#### Original: 간결한 프롬프트
```python
lead_researcher_prompt = """You are a research supervisor. 
Your job is to conduct research by calling the "ConductResearch" tool.

<Task>
Your focus is to call the "ConductResearch" tool to conduct research.
When satisfied, call "ResearchComplete".
</Task>

<Available Tools>
1. ConductResearch
2. ResearchComplete
3. think_tool
</Available Tools>
"""
```

#### DeepAgent: 상세한 워크플로우 프롬프트
```python
ORCHESTRATOR_SYSTEM_PROMPT = """You are a Deep Research Orchestrator.

<Core Responsibility>
Coordinate specialized subagents through explicit stages.
CRITICAL: Filesystem serves as long-term memory.
ALWAYS check for existing context before starting.
</Core Responsibility>

<Workflow Stages>
STAGE 0: CONTEXT RESTORATION
- ls / - Check root structure
- read_file /status/current_stage.txt
- Determine: NEW/CONTINUING/REVISING

STAGE 1: CLARIFICATION
...

STAGE 2: PLANNING
...
</Workflow Stages>
"""
```

### 4.5 압축 단계

#### Original: 각 researcher 내부에서 압축
```python
# researcher 서브그래프의 마지막 노드
async def compress_research(state: ResearcherState, config):
    """연구 결과를 압축"""
    researcher_messages = state.get("researcher_messages", [])
    researcher_messages.append(
        HumanMessage(content=compress_research_simple_human_message)
    )
    
    response = await synthesizer_model.ainvoke(messages)
    return {
        "compressed_research": str(response.content),
        "raw_notes": [raw_notes_content]
    }
```

#### DeepAgent: 별도의 Compressor SubAgent
```python
# 모든 researcher 완료 후 실행
task(description="Synthesize all research findings", subagent_type="compressor")

# Compressor SubAgent
SubAgent(
    name="compressor",
    description="여러 연구 노트를 읽고 종합 생성",
    system_prompt=COMPRESSOR_SYSTEM_PROMPT,
    tools=[],  # 파일시스템 도구만
)
```

---

## 5. 장단점 분석

### 5.1 DeepResearch_Original

#### 장점 ✅

1. **명시적 제어**
   - 모든 노드와 엣지를 직접 정의
   - 워크플로우가 코드에 명확히 드러남
   - 디버깅이 직관적

2. **세밀한 커스터마이징**
   - 각 노드의 동작을 완전히 제어
   - 상태 전달 방식 커스터마이징
   - 조건부 라우팅 자유롭게 구현

3. **의존성 최소화**
   - LangGraph + LangChain만 사용
   - 추가 프레임워크 불필요
   - 학습 곡선 낮음

4. **성능 최적화**
   - 불필요한 추상화 없음
   - 직접적인 함수 호출
   - 오버헤드 최소화

#### 단점 ❌

1. **보일러플레이트 코드**
   - 서브그래프 수동 생성
   - 반복적인 노드/엣지 정의
   - 코드 중복 발생

2. **상태 관리 복잡성**
   - 명시적 상태 전달 필요
   - 서브그래프 간 상태 동기화
   - 타입 안정성 관리 어려움

3. **확장성 제한**
   - 새 서브에이전트 추가 시 많은 코드 수정
   - 동적 에이전트 생성 어려움
   - 재사용성 낮음

4. **장기 메모리 부재**
   - 세션 간 상태 보존 어려움
   - 파일 기반 메모리 수동 구현 필요
   - 컨텍스트 복원 로직 직접 작성

### 5.2 DeepResearch_DeepAgent

#### 장점 ✅

1. **간결한 코드**
   - 메인 파일 186줄 (vs 781줄)
   - SubAgent 패턴으로 추상화
   - 보일러플레이트 제거

2. **자동 미들웨어**
   - TodoList, Filesystem, SubAgent 자동 주입
   - 파일 작업 도구 자동 제공
   - 요약 및 캐싱 자동화

3. **파일시스템 기반 메모리**
   - 세션 간 상태 자동 보존
   - 장기 메모리 역할
   - 투명한 작업 추적

4. **확장성**
   - 새 SubAgent 쉽게 추가
   - 동적 서브에이전트 생성 지원
   - 스킬 기반 도구 관리

5. **재사용성**
   - SubAgent 정의 재사용
   - 스킬 레지스트리 공유
   - 모듈화된 구조

6. **품질 보증**
   - Critic SubAgent 내장
   - 체계적인 워크플로우 단계
   - 컨텍스트 복원 자동화

#### 단점 ❌

1. **추상화 오버헤드**
   - 내부 동작 불투명
   - 디버깅 어려움
   - 성능 오버헤드 가능

2. **학습 곡선**
   - DeepAgents 프레임워크 학습 필요
   - 미들웨어 시스템 이해 필요
   - 프롬프트 기반 제어 익숙해지기

3. **제어 제한**
   - 미들웨어 동작 커스터마이징 어려움
   - 내부 그래프 구조 수정 불가
   - 세밀한 최적화 제한

4. **의존성 증가**
   - DeepAgents 프레임워크 의존
   - 버전 호환성 관리
   - 프레임워크 버그 영향

---

## 6. 선택 가이드

### 6.1 DeepResearch_Original을 선택해야 하는 경우

✅ **다음 상황에 적합:**

1. **세밀한 제어가 필요한 경우**
   - 워크플로우를 완전히 커스터마이징
   - 특정 노드의 동작을 최적화
   - 조건부 라우팅이 복잡한 경우

2. **의존성을 최소화하고 싶은 경우**
   - LangGraph만으로 충분
   - 추가 프레임워크 학습 부담
   - 프로덕션 안정성 중시

3. **성능이 중요한 경우**
   - 추상화 오버헤드 최소화
   - 직접적인 함수 호출
   - 리소스 제약 환경

4. **학습 목적인 경우**
   - LangGraph 내부 동작 이해
   - 멀티-에이전트 패턴 학습
   - 기초부터 구축

### 6.2 DeepResearch_DeepAgent를 선택해야 하는 경우

✅ **다음 상황에 적합:**

1. **빠른 프로토타이핑이 필요한 경우**
   - 간결한 코드로 빠른 구현
   - 자동 미들웨어 활용
   - 보일러플레이트 제거

2. **장기 메모리가 중요한 경우**
   - 세션 간 상태 보존
   - 컨텍스트 복원 자동화
   - 파일 기반 추적

3. **확장성이 중요한 경우**
   - 동적 서브에이전트 생성
   - 새 SubAgent 쉽게 추가
   - 스킬 기반 도구 관리

4. **품질 보증이 필요한 경우**
   - Critic SubAgent 활용
   - 체계적인 워크플로우
   - 자동 검증 메커니즘

5. **복잡한 연구 워크플로우인 경우**
   - 다단계 워크플로우
   - 여러 서브에이전트 조율
   - 컨텍스트 관리 자동화

---

## 7. 코드 복잡도 비교

### 7.1 라인 수 비교

| 구성 요소 | Original | DeepAgent | 차이 |
|----------|----------|-----------|------|
| **메인 파일** | 781줄 | 186줄 | **-76%** |
| **전체 파일 수** | 8개 | 20개 | +150% |
| **프롬프트** | 1개 파일 | 4개 파일 (모듈화) | - |
| **서브에이전트** | 인라인 | 4개 파일 | - |

### 7.2 복잡도 지표

| 지표 | Original | DeepAgent |
|------|----------|-----------|
| **순환 복잡도** | 높음 | 낮음 |
| **결합도** | 높음 | 낮음 |
| **응집도** | 중간 | 높음 |
| **재사용성** | 낮음 | 높음 |
| **테스트 용이성** | 중간 | 높음 |

---

## 8. 실행 흐름 비교

### 8.1 Original 실행 흐름

```
1. clarify_with_user
   ↓ (Command)
2. write_research_brief
   ↓ (Command)
3. research_supervisor (Subgraph)
   ├── supervisor
   │   ↓
   ├── supervisor_tools
   │   ├── think_tool 처리
   │   └── ConductResearch 처리
   │       └── researcher_subgraph.ainvoke() × N (병렬)
   │           ├── researcher
   │           ├── researcher_tools
   │           └── compress_research
   ↓
4. final_report_generation
```

### 8.2 DeepAgent 실행 흐름

```
1. STAGE 0: Context Restoration
   - ls /, read_file 등으로 기존 작업 확인
   
2. STAGE 1: Clarification (프롬프트 기반)
   
3. STAGE 2: Planning
   - write_file /output/research_brief.md
   - write_todos
   
4. STAGE 3: Research
   - task(subagent_type="researcher") × N (병렬)
   - 각 researcher가 /output/notes/*.md 생성
   
5. STAGE 4: Compression
   - task(subagent_type="compressor")
   - /output/compressed_research.md 생성
   
6. STAGE 5: Final Report
   - /output/final_report.md 생성
   
7. STAGE 6: Critique (선택적)
   - task(subagent_type="critic")
   - /output/feedback.md 생성
```

---

## 9. 결론

### 핵심 차이점 요약

| 측면 | Original | DeepAgent |
|------|----------|-----------|
| **접근 방식** | 명시적, 절차적 | 선언적, 추상화 |
| **코드 스타일** | 직접 구현 | 프레임워크 활용 |
| **상태 관리** | 메모리 기반 | 파일시스템 기반 |
| **확장성** | 제한적 | 높음 |
| **학습 곡선** | 낮음 | 중간 |
| **제어 수준** | 완전 제어 | 추상화된 제어 |
| **적합한 용도** | 커스터마이징, 학습 | 프로토타이핑, 프로덕션 |

### 최종 권장사항

**DeepResearch_Original 추천:**
- LangGraph 학습 중
- 세밀한 제어 필요
- 의존성 최소화 원함
- 단순한 워크플로우

**DeepResearch_DeepAgent 추천:**
- 빠른 개발 필요
- 장기 메모리 중요
- 복잡한 워크플로우
- 확장 가능한 시스템
- 품질 보증 필요

두 접근 방식 모두 강력하며, 프로젝트의 요구사항과 팀의 선호도에 따라 선택하면 됩니다.
