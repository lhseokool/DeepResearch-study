# LangGraph 그래프 연결 방식 상세 가이드

## 📌 개요

LangGraph에서는 **두 가지 방식**으로 노드(함수)를 연결할 수 있습니다:

1. **`Command` 방식** (동적 라우팅) - 노드 함수 내부에서 다음 노드 결정
2. **`add_edge` 방식** (정적 라우팅) - 그래프 빌드 시 미리 연결 정의

---

## 🔀 1. Command 방식 (동적 라우팅)

### 개념
노드 함수가 **실행 중에** 다음에 어디로 갈지 결정합니다. 조건에 따라 다른 노드로 이동할 수 있습니다.

### 코드 예시: `clarify_with_user` 함수

```python
async def clarify_with_user(
    state: AgentState, 
    config: RunnableConfig
) -> Command[Literal["write_research_brief", END]]:
    """사용자 질문 명확화"""
    
    # 명확화가 비활성화된 경우
    if not configurable.allow_clarification:
        # 바로 연구 계획 작성으로 이동
        return Command(goto="write_research_brief")
    
    # 명확화 필요 여부 분석
    response = await clarification_model.ainvoke([...])
    
    # 조건에 따라 다른 노드로 이동
    if response.need_clarification:
        # 명확화 질문을 하고 종료 (사용자 응답 대기)
        return Command(
            goto=END, 
            update={"messages": [AIMessage(content=response.question)]}
        )
    else:
        # 바로 연구 계획 작성으로 진행
        return Command(
            goto="write_research_brief",
            update={"messages": [AIMessage(content=response.verification)]}
        )
```

### Command 구조 분석

```python
Command(
    goto="next_node_name",  # 다음 노드 이름 또는 END
    update={...}            # 상태 업데이트 (선택사항)
)
```

#### `goto` 파라미터
- **노드 이름**: 다음에 실행할 노드 지정
- **`END`**: 그래프 종료

#### `update` 파라미터
- 다음 노드로 가기 전에 상태를 업데이트
- 딕셔너리 형태로 상태 필드 지정

### 동작 흐름 다이어그램

```
┌─────────────────────────┐
│  clarify_with_user      │
│  (명확화 노드)          │
└───────────┬─────────────┘
            │
            ▼
    [명확화 필요?]
            │
    ┌───────┴───────┐
    │               │
    ▼               ▼
[필요함]        [불필요]
    │               │
    ▼               ▼
Command(        Command(
  goto=END,       goto="write_research_brief",
  update={...}    update={...}
)                )
    │               │
    ▼               ▼
[종료]          [연구 계획 작성]
```

### 또 다른 예시: `write_research_brief`

```python
async def write_research_brief(
    state: AgentState, 
    config: RunnableConfig
) -> Command[Literal["research_supervisor"]]:
    """연구 계획서 작성"""
    
    # 연구 계획서 생성
    response = await research_model.ainvoke([...])
    
    # 항상 research_supervisor로 이동
    return Command(
        goto="research_supervisor",
        update={
            "research_brief": response.research_brief,
            "supervisor_messages": {...}
        }
    )
```

이 경우는 조건 없이 **항상** `research_supervisor`로 이동합니다.

---

## 🔗 2. add_edge 방식 (정적 라우팅)

### 개념
그래프를 **빌드할 때** 미리 노드 간 연결을 정의합니다. 조건 없이 항상 같은 경로로 이동합니다.

### 코드 예시

```python
# 그래프 빌더 생성
deep_researcher_builder = StateGraph(
    state_schema=AgentState,
    input_schema=AgentInputState,
    context_schema=Configuration,
)

# 노드 추가
deep_researcher_builder.add_node("clarify_with_user", clarify_with_user)
deep_researcher_builder.add_node("write_research_brief", write_research_brief)
deep_researcher_builder.add_node("research_supervisor", supervisor_subgraph)
deep_researcher_builder.add_node("final_report_generation", final_report_generation)

# 엣지 추가 (정적 연결)
deep_researcher_builder.add_edge(START, "clarify_with_user")  # 시작 → 명확화
deep_researcher_builder.add_edge("research_supervisor", "final_report_generation")  # 연구 → 보고서
deep_researcher_builder.add_edge("final_report_generation", END)  # 보고서 → 종료
```

### add_edge 구조

```python
builder.add_edge(
    "source_node",      # 출발 노드
    "destination_node"  # 도착 노드
)
```

### 특수 노드
- **`START`**: 그래프의 시작점
- **`END`**: 그래프의 종료점

### 동작 흐름 다이어그램

```
START
  │
  │ (add_edge)
  ▼
clarify_with_user
  │
  │ (Command - 동적)
  ▼
write_research_brief
  │
  │ (Command - 동적)
  ▼
research_supervisor
  │
  │ (add_edge - 정적)
  ▼
final_report_generation
  │
  │ (add_edge - 정적)
  ▼
END
```

---

## 🔄 3. 혼합 사용: Command + add_edge

이 프로젝트에서는 **두 방식을 함께** 사용합니다!

### 전체 그래프 구조

```python
# 1. 노드 정의
deep_researcher_builder.add_node("clarify_with_user", clarify_with_user)
deep_researcher_builder.add_node("write_research_brief", write_research_brief)
deep_researcher_builder.add_node("research_supervisor", supervisor_subgraph)
deep_researcher_builder.add_node("final_report_generation", final_report_generation)

# 2. 정적 엣지 (add_edge)
deep_researcher_builder.add_edge(START, "clarify_with_user")
deep_researcher_builder.add_edge("research_supervisor", "final_report_generation")
deep_researcher_builder.add_edge("final_report_generation", END)

# 3. 동적 라우팅 (Command)
# clarify_with_user 내부에서:
#   - END로 갈 수도 있고
#   - write_research_brief로 갈 수도 있음
# write_research_brief 내부에서:
#   - research_supervisor로 이동
```

### 실제 실행 흐름

#### 시나리오 1: 명확화 필요
```
START
  ↓ (add_edge)
clarify_with_user
  ↓ (Command: goto=END)
END (사용자 응답 대기)
```

#### 시나리오 2: 명확화 불필요
```
START
  ↓ (add_edge)
clarify_with_user
  ↓ (Command: goto="write_research_brief")
write_research_brief
  ↓ (Command: goto="research_supervisor")
research_supervisor
  ↓ (add_edge)
final_report_generation
  ↓ (add_edge)
END
```

---

## 📊 4. Command vs add_edge 비교

| 특징 | Command | add_edge |
|------|---------|----------|
| **정의 시점** | 런타임 (실행 중) | 빌드 타임 (그래프 생성 시) |
| **유연성** | 높음 (조건부 분기) | 낮음 (고정 경로) |
| **사용 위치** | 노드 함수 내부 | 그래프 빌더 |
| **조건 분기** | 가능 | 불가능 |
| **상태 업데이트** | 가능 (`update` 파라미터) | 불가능 |
| **가독성** | 코드 내부 확인 필요 | 그래프 구조 한눈에 파악 |

### 언제 무엇을 사용할까?

#### Command 사용 (동적 라우팅)
```python
# ✅ 조건에 따라 다른 경로
if condition:
    return Command(goto="path_a")
else:
    return Command(goto="path_b")

# ✅ 상태 업데이트와 함께 이동
return Command(
    goto="next_node",
    update={"field": value}
)

# ✅ 조기 종료
if error:
    return Command(goto=END)
```

#### add_edge 사용 (정적 라우팅)
```python
# ✅ 항상 같은 경로
builder.add_edge("node_a", "node_b")

# ✅ 시작/종료 연결
builder.add_edge(START, "first_node")
builder.add_edge("last_node", END)

# ✅ 단순한 순차 실행
builder.add_edge("step1", "step2")
builder.add_edge("step2", "step3")
```

---

## 🎯 5. 실전 예제

### 예제 1: 간단한 순차 실행

```python
# 그래프 생성
builder = StateGraph(state_schema=MyState)

# 노드 추가
builder.add_node("step1", step1_function)
builder.add_node("step2", step2_function)
builder.add_node("step3", step3_function)

# 정적 연결 (항상 같은 순서)
builder.add_edge(START, "step1")
builder.add_edge("step1", "step2")
builder.add_edge("step2", "step3")
builder.add_edge("step3", END)

graph = builder.compile()
```

**흐름**: START → step1 → step2 → step3 → END

### 예제 2: 조건부 분기

```python
async def decision_node(state):
    """조건에 따라 다른 경로 선택"""
    if state["score"] > 80:
        return Command(goto="success_path")
    else:
        return Command(goto="retry_path")

# 그래프 생성
builder = StateGraph(state_schema=MyState)

builder.add_node("decision", decision_node)
builder.add_node("success_path", success_function)
builder.add_node("retry_path", retry_function)

# 시작은 정적
builder.add_edge(START, "decision")

# decision 노드에서 동적으로 분기
# (Command로 처리)

# 종료는 정적
builder.add_edge("success_path", END)
builder.add_edge("retry_path", END)

graph = builder.compile()
```

**흐름**:
- START → decision
- decision → success_path (score > 80) → END
- decision → retry_path (score ≤ 80) → END

### 예제 3: 복잡한 워크플로우 (DeepResearch 스타일)

```python
async def validate_input(state):
    """입력 검증"""
    if state["input_valid"]:
        return Command(goto="process")
    else:
        return Command(
            goto=END,
            update={"error": "Invalid input"}
        )

async def process(state):
    """처리"""
    # 항상 review로 이동
    return Command(goto="review")

async def review(state):
    """검토"""
    if state["needs_revision"]:
        return Command(goto="process")  # 재처리
    else:
        return Command(goto="finalize")

# 그래프 구성
builder = StateGraph(state_schema=MyState)

builder.add_node("validate", validate_input)
builder.add_node("process", process)
builder.add_node("review", review)
builder.add_node("finalize", finalize_function)

# 정적 연결
builder.add_edge(START, "validate")
builder.add_edge("finalize", END)

# 동적 연결은 Command로 처리
# validate → process or END
# process → review
# review → process or finalize

graph = builder.compile()
```

**흐름**:
```
START → validate
         ├─→ END (invalid)
         └─→ process → review
                        ├─→ process (재처리)
                        └─→ finalize → END
```

---

## 🔍 6. DeepResearch Original 그래프 분석

### 전체 구조

```python
# 노드 정의
add_node("clarify_with_user", clarify_with_user)
add_node("write_research_brief", write_research_brief)
add_node("research_supervisor", supervisor_subgraph)
add_node("final_report_generation", final_report_generation)

# 정적 엣지
add_edge(START, "clarify_with_user")                    # 1
add_edge("research_supervisor", "final_report_generation")  # 2
add_edge("final_report_generation", END)                # 3

# 동적 라우팅 (Command)
# clarify_with_user:
#   - goto=END (명확화 필요)
#   - goto="write_research_brief" (명확화 불필요)
# write_research_brief:
#   - goto="research_supervisor" (항상)
```

### 시각화

```
                    START
                      │
                      │ add_edge (정적)
                      ▼
            ┌──────────────────┐
            │ clarify_with_user│
            └────────┬──────────┘
                     │
                     │ Command (동적)
                     │
         ┌───────────┴───────────┐
         │                       │
    [명확화 필요]           [명확화 불필요]
         │                       │
         ▼                       ▼
        END              write_research_brief
                                 │
                                 │ Command (동적)
                                 ▼
                        research_supervisor
                                 │
                                 │ add_edge (정적)
                                 ▼
                      final_report_generation
                                 │
                                 │ add_edge (정적)
                                 ▼
                                END
```

---

## 💡 7. 핵심 요약

### Command 방식
- **위치**: 노드 함수 내부
- **시점**: 런타임 (실행 중)
- **특징**: 조건부 분기 가능
- **문법**: `return Command(goto="node_name", update={...})`

### add_edge 방식
- **위치**: 그래프 빌더
- **시점**: 빌드 타임 (컴파일 전)
- **특징**: 고정 경로
- **문법**: `builder.add_edge("source", "destination")`

### 혼합 사용
- **정적 부분**: `add_edge`로 기본 골격 구성
- **동적 부분**: `Command`로 조건부 분기 처리
- **장점**: 유연성과 명확성의 균형

---

## 🎓 학습 팁

1. **그래프 구조 먼저 파악**: `add_edge` 호출을 보고 기본 흐름 이해
2. **노드 함수 분석**: `Command` 반환을 보고 동적 분기 파악
3. **시각화 그리기**: 직접 다이어그램을 그려보면 이해가 쉬움
4. **디버깅**: 어느 노드에서 어디로 가는지 로그 출력

---

## 📚 추가 자료

- LangGraph 공식 문서: https://langchain-ai.github.io/langgraph/
- Command API 레퍼런스
- StateGraph 가이드

이제 LangGraph의 그래프 연결 방식을 완벽히 이해하셨을 것입니다! 🚀
