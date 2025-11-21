# Project AX Advanced 아키텍처

> DeepAgent 프레임워크 기반 계층적 멀티-에이전트 코드 분석 시스템

---

## 📋 목차

1. [전체 구조](#1-전체-구조)
2. [에이전트 패턴](#2-에이전트-패턴)
3. [핵심 컴포넌트](#3-핵심-컴포넌트)
4. [워크플로우](#4-워크플로우)
5. [디자인 패턴](#5-디자인-패턴)

---

## 1. 전체 구조

### 1.1 디렉토리 구조

```
03_Project_AX_Advanced/
├── src/agentic_coding_assistant/
│   ├── graph.py                  # 메인 에이전트 생성
│   ├── state.py                  # 상태 정의
│   ├── configuration.py          # 설정 관리
│   ├── prompts/
│   │   └── orchestrator.py       # 오케스트레이터 프롬프트
│   ├── subagents/
│   │   ├── analyzer.py           # 분석 서브에이전트
│   │   ├── refactorer.py         # 리팩토링 서브에이전트
│   │   └── documenter.py         # 문서화 서브에이전트
│   ├── skills/
│   │   ├── registry.py           # 스킬-도구 레지스트리
│   │   └── tool_collections.py   # 도구 컬렉션
│   ├── tools/
│   │   ├── subagent_tools.py     # SpawnSubAgent 도구
│   │   └── dynamic.py            # 동적 서브에이전트 팩토리
│   └── utils/
│       └── workspace.py          # 워크스페이스 관리
└── workspace/                    # 에이전트 작업 공간
```

### 1.2 아키텍처 다이어그램

```
DeepCodeAnalysisAgent (Main Orchestrator)
├── Analyzer SubAgent (병렬 실행 가능)
├── Refactorer SubAgent (선택적)
├── Documenter SubAgent (선택적)
└── Dynamic SubAgents (런타임 생성)
```

### 1.3 워크플로우 단계

| Stage | 이름 | 설명 |
|-------|------|------|
| 0 | Context Restoration | 기존 작업 확인 |
| 1 | Analysis Planning | 분석 계획 수립 |
| 2 | Parallel Analysis | 병렬 분석 수행 |
| 3 | Synthesis | 결과 종합 |
| 4 | Action | 리팩토링/문서화 |
| 5 | Final Report | 보고서 작성 |

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
    name="DeepCodeAnalysisAgent",
)
```

### 2.2 서브에이전트 타입

**1. Analyzer** - 코드 분석 및 영향도 감지
- 도구: analyze_code, find_references, get_symbol_info
- 출력: /output/analysis_results/
- 용도: 코드 구조 이해, 의존성 추적, 영향도 평가

**2. Refactorer** - 자가 치유 리팩토링
- 도구: 파일시스템 도구만 (미들웨어 제공)
- 출력: /output/refactoring_results/
- 용도: 코드 개선, 테스트 생성, 오류 수정

**3. Documenter** - 문서 동기화
- 도구: 파일시스템 도구만 (미들웨어 제공)
- 출력: /output/documentation_updates/
- 용도: 문서 업데이트, 일관성 유지

**4. Dynamic SubAgent** - 런타임 생성
- 도구: 스킬에 따라 동적 할당
- 출력: workspace/{agent_name}/
- 용도: 특화된 복잡한 작업 처리

### 2.3 병렬 실행 전략

| 복잡도 | 분석기 수 | 예시 |
|--------|----------|------|
| Simple | 1 | 단일 함수 분석 |
| Moderate | 2-3 | 모듈 간 의존성 분석 |
| Complex | 4-5 | 전체 시스템 영향도 평가 |

---

## 3. 핵심 컴포넌트

### 3.1 State (상태)

```python
class AgentState(MessagesState):
    coordinator_messages: Annotated[list, override_reducer]
    analysis_goal: str | None
    analysis_results: Annotated[list[dict], override_reducer]
    impact_notes: Annotated[list[str], override_reducer]
    final_report: str
    analysis_iterations: int

def override_reducer(current_value, new_value):
    """리스트 추가 또는 완전 교체 지원"""
    if isinstance(new_value, dict) and new_value.get("type") == "override":
        return new_value.get("value", new_value)
    else:
        return operator.add(current_value, new_value)
```

### 3.2 Configuration (설정)

```python
class DeepAgentConfiguration(BaseModel):
    main_model: str = "openai:gpt-4.1"
    analyzer_model: Optional[str] = None
    default_analysis_mode: AnalysisMode = AnalysisMode.AUTO
    max_parallel_analyzers: int = 3
    max_coordinator_iterations: int = 10
    enable_self_healing: bool = True
    enable_documentation_sync: bool = True
```

### 3.3 Skills Registry

```python
class SkillRegistry:
    _skills = {
        "code_analysis": ["analyze_code", "find_references"],
        "impact_detection": ["detect_impact", "analyze_dependencies"],
        "refactoring": ["refactor_code", "apply_changes"],
        "documentation": ["sync_documentation", "update_docstrings"],
    }
    
    def get_tools_for_skill(self, skill):
        return [self._tools[name] for name in self._skills[skill]]
```

### 3.4 Prompts

각 에이전트는 상세한 시스템 프롬프트를 가집니다:

- **Orchestrator**: 워크플로우 관리, 서브에이전트 조율, 단계별 진행
- **Analyzer**: 코드 분석, 의존성 추적, 영향도 평가
- **Refactorer**: 코드 개선, 테스트 생성, 자가 치유
- **Documenter**: 문서 동기화, 일관성 유지

---

## 4. 워크플로우

### 전체 실행 흐름

```python
# 1. 에이전트 생성
agent = await create_deep_analysis_agent(
    tools=[analyze_code_tool, refactor_tool],
    model="openai:gpt-4.1",
    enable_self_healing=True,
    enable_documentation_sync=True,
)

# 2. 실행
result = await run_analysis(
    request="함수 X 변경의 영향도 분석",
    tools=[analyze_code_tool],
    model="anthropic:claude-sonnet-4-5-20250929",
)

# 3. 결과 확인
final_report = result["files"]["/output/final_report.md"]["content"]
```

### 단계별 실행

**STAGE 0: Context Restoration**
```python
ls /
read_file /status/current_stage.txt
# 작업 모드 결정: NEW/CONTINUING/REVISING
```

**STAGE 1: Analysis Planning**
```python
write_file /status/analysis_plan.md
write_todos
# 복잡도 평가 → 분석기 수 결정
```

**STAGE 2: Parallel Analysis**
```python
task(description="Analyze module A", subagent_type="analyzer")
task(description="Analyze module B", subagent_type="analyzer")
task(description="Analyze module C", subagent_type="analyzer")
```

**STAGE 3: Synthesis**
```python
read_file /output/analysis_results/module_a.md
read_file /output/analysis_results/module_b.md
# 결과 종합 및 패턴 식별
```

**STAGE 4: Action (선택적)**
```python
task(description="Refactor code", subagent_type="refactorer")
task(description="Update docs", subagent_type="documenter")
```

**STAGE 5: Final Report**
```python
write_file /output/final_report.md
# 종합 보고서 작성
```

---

## 5. 디자인 패턴

### 5.1 계층적 에이전트 구조
- Orchestrator → SubAgents → Tools
- 명확한 책임 분리
- 독립적인 워크스페이스

### 5.2 파일시스템 기반 메모리
- 모든 상태를 파일로 저장
- 세션 간 컨텍스트 보존
- 투명하고 디버깅 가능

### 5.3 스킬 기반 도구 관리
- 추상적 스킬 ↔ 구체적 도구 분리
- 동적 도구 할당
- 확장 가능한 구조

### 5.4 병렬 실행 최적화
- 여러 분석기 동시 실행
- 복잡도 기반 동적 할당
- 효율적인 리소스 사용

### 5.5 자동 미들웨어
- TodoListMiddleware: 계획 수립
- FilesystemMiddleware: 파일 작업
- SubAgentMiddleware: 서브에이전트 할당
- SummarizationMiddleware: 컨텍스트 압축
- AnthropicPromptCachingMiddleware: 비용 최적화

### 5.6 컨텍스트 관리
- 요약을 통한 압축
- 토큰 제한 관리
- 프롬프트 캐싱

---

## 6. 핵심 강점

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

## 7. 사용 예시

```python
# examples/deep_agent_demo.py
import asyncio
from agentic_coding_assistant.graph import create_deep_analysis_agent

async def main():
    request = "Analyze impact of changing function X"
    
    tools = [analyze_code_tool, refactor_tool]
    
    agent = await create_deep_analysis_agent(
        tools=tools,
        model="openai:gpt-4.1",
        max_analysis_iterations=10,
        enable_self_healing=True,
    )
    
    config = {
        "configurable": {"thread_id": "analysis_001"},
        "recursion_limit": 100,
    }
    
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": request}]},
        config=config,
    )
    
    # 결과 확인
    final_report = result["files"]["/output/final_report.md"]["content"]
    print(final_report)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 8. 결론

Project AX Advanced는 **DeepAgent 프레임워크**를 활용하여 복잡한 코드 분석 작업을 수행하는 **계층적 멀티-에이전트 시스템**입니다.

**핵심 기술 스택:**
- DeepAgents: 서브에이전트, 미들웨어, 백엔드
- LangGraph: 상태 관리, 체크포인터, 그래프 실행
- LangChain: 도구, 모델, 구조화된 출력

**주요 특징:**
- 계층적 에이전트 구조
- 파일시스템 기반 장기 메모리
- 스킬 기반 도구 관리
- 병렬 실행 최적화
- 자동 미들웨어 주입

이 아키텍처는 확장 가능하고, 유지보수가 쉬우며, 복잡한 코드 분석 워크플로우를 효과적으로 처리합니다.
