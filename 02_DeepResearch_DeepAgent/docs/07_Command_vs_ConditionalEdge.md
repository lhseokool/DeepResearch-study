# Command vs conditional_edge 완벽 비교

## 📌 핵심 차이 한눈에 보기

| 특징 | Command | conditional_edge |
|------|---------|------------------|
| **도입 시기** | LangGraph 최신 버전 | LangGraph 초기 버전 |
| **정의 위치** | 노드 함수 **내부** | 그래프 빌더 (외부) |
| **라우팅 로직** | 노드 함수가 직접 결정 | 별도 함수로 분리 |
| **상태 업데이트** | 동시에 가능 | 별도 처리 필요 |
| **가독성** | 높음 (로직이 한 곳에) | 낮음 (로직이 분산) |
| **권장 사용** | ✅ 최신 프로젝트 | ⚠️ 레거시 코드 |

---

## 1️⃣ Command 방식 (최신, 권장)

### 개념
노드 함수가 **직접** 다음 노드를 결정하고 상태도 업데이트합니다.

### 코드 예시

```python
async def clarify_with_user(state, config):
    """명확화 노드"""
    
    # 명확화 필요 여부 분석
    response = await model.ainvoke([...])
    
    # 🎯 노드 함수 내부에서 직접 결정
    if response.need_clarification:
        # 경로 1: 종료
        return Command(
            goto=END,
            update={"messages": [AIMessage(content=response.question)]}
        )
    else:
        # 경로 2: 다음 노드로
        return Command(
            goto="write_research_brief",
            update={"messages": [AIMessage(content=response.verification)]}
        )

# 그래프 구성 (간단!)
builder.add_node("clarify_with_user", clarify_with_user)
builder.add_edge(START, "clarify_with_user")
# Command가 알아서 라우팅하므로 추가 설정 불필요!
```

### 장점
✅ **로직이 한 곳에 집중**: 노드 함수만 보면 모든 것을 알 수 있음  
✅ **상태 업데이트 동시 처리**: `update` 파라미터로 한 번에 처리  
✅ **코드가 간결**: 별도 라우팅 함수 불필요  
✅ **디버깅 쉬움**: 한 함수 안에서 모든 로직 확인 가능

---

## 2️⃣ conditional_edge 방식 (구버전)

### 개념
노드 함수는 **상태만 반환**하고, **별도의 라우팅 함수**가 다음 노드를 결정합니다.

### 코드 예시

```python
# 1️⃣ 노드 함수: 상태만 반환
async def clarify_with_user(state, config):
    """명확화 노드"""
    
    # 명확화 필요 여부 분석
    response = await model.ainvoke([...])
    
    # ⚠️ 다음 노드를 결정하지 않음! 상태만 업데이트
    if response.need_clarification:
        return {
            "messages": [AIMessage(content=response.question)],
            "needs_clarification": True  # 플래그 설정
        }
    else:
        return {
            "messages": [AIMessage(content=response.verification)],
            "needs_clarification": False
        }

# 2️⃣ 라우팅 함수: 별도로 정의
def route_after_clarification(state):
    """명확화 후 어디로 갈지 결정하는 별도 함수"""
    if state.get("needs_clarification"):
        return END  # 종료
    else:
        return "write_research_brief"  # 다음 노드로

# 3️⃣ 그래프 구성: 복잡!
builder.add_node("clarify_with_user", clarify_with_user)
builder.add_edge(START, "clarify_with_user")

# ⚠️ conditional_edge로 라우팅 함수 연결
builder.add_conditional_edges(
    "clarify_with_user",  # 출발 노드
    route_after_clarification,  # 라우팅 함수
    {
        END: END,  # 매핑: 함수 반환값 → 실제 노드
        "write_research_brief": "write_research_brief"
    }
)
```

### 단점
❌ **로직이 분산**: 노드 함수 + 라우팅 함수 두 곳을 봐야 함  
❌ **상태 플래그 필요**: `needs_clarification` 같은 임시 플래그 추가  
❌ **코드가 복잡**: 매핑 딕셔너리 등 추가 설정 필요  
❌ **디버깅 어려움**: 여러 함수를 오가며 확인해야 함

---

## 🔄 3. 실제 비교 예제

### 시나리오: 점수에 따라 다른 경로

#### Command 방식 (권장) ✅

```python
async def evaluate_score(state):
    """점수 평가 노드"""
    score = calculate_score(state)
    
    # 🎯 한 곳에서 모든 것을 처리
    if score >= 90:
        return Command(
            goto="excellent_path",
            update={"score": score, "grade": "A"}
        )
    elif score >= 70:
        return Command(
            goto="good_path",
            update={"score": score, "grade": "B"}
        )
    else:
        return Command(
            goto="retry_path",
            update={"score": score, "grade": "F"}
        )

# 그래프 구성 (간단!)
builder.add_node("evaluate", evaluate_score)
builder.add_node("excellent_path", excellent_handler)
builder.add_node("good_path", good_handler)
builder.add_node("retry_path", retry_handler)

builder.add_edge(START, "evaluate")
# Command가 알아서 라우팅!
```

#### conditional_edge 방식 (구버전) ⚠️

```python
# 1️⃣ 노드 함수
async def evaluate_score(state):
    """점수 평가 노드"""
    score = calculate_score(state)
    
    # ⚠️ 상태만 업데이트, 라우팅은 안 함
    return {
        "score": score,
        "grade": "A" if score >= 90 else "B" if score >= 70 else "F"
    }

# 2️⃣ 라우팅 함수 (별도!)
def route_by_score(state):
    """점수에 따라 경로 결정"""
    score = state.get("score", 0)
    
    if score >= 90:
        return "excellent"
    elif score >= 70:
        return "good"
    else:
        return "retry"

# 3️⃣ 그래프 구성 (복잡!)
builder.add_node("evaluate", evaluate_score)
builder.add_node("excellent_path", excellent_handler)
builder.add_node("good_path", good_handler)
builder.add_node("retry_path", retry_handler)

builder.add_edge(START, "evaluate")

# ⚠️ conditional_edges로 연결
builder.add_conditional_edges(
    "evaluate",
    route_by_score,
    {
        "excellent": "excellent_path",
        "good": "good_path",
        "retry": "retry_path"
    }
)
```

---

## 📊 4. 상세 비교표

### 코드 구조

| 측면 | Command | conditional_edge |
|------|---------|------------------|
| **함수 개수** | 1개 (노드 함수만) | 2개 (노드 + 라우팅) |
| **반환 타입** | `Command` 객체 | 상태 딕셔너리 |
| **라우팅 로직** | 노드 함수 내부 | 별도 라우팅 함수 |
| **상태 업데이트** | `Command.update` | 노드 함수 반환값 |

### 그래프 빌더 설정

#### Command
```python
# 간단!
builder.add_node("node_name", node_function)
builder.add_edge(START, "node_name")
# 끝!
```

#### conditional_edge
```python
# 복잡!
builder.add_node("node_name", node_function)
builder.add_edge(START, "node_name")
builder.add_conditional_edges(
    "node_name",
    routing_function,
    {
        "path1": "destination1",
        "path2": "destination2",
        # ...
    }
)
```

---

## 🎯 5. 언제 무엇을 사용할까?

### Command 사용 (권장) ✅

```python
# ✅ 새 프로젝트
# ✅ 조건부 라우팅 필요
# ✅ 상태 업데이트와 라우팅을 동시에
# ✅ 코드 가독성 중요

async def my_node(state):
    result = process(state)
    
    if result.success:
        return Command(
            goto="success_node",
            update={"result": result.data}
        )
    else:
        return Command(
            goto="error_node",
            update={"error": result.error}
        )
```

### conditional_edge 사용 ⚠️

```python
# ⚠️ 레거시 코드 유지보수
# ⚠️ 기존 프로젝트 호환성
# ⚠️ LangGraph 구버전 사용

# 새 프로젝트에서는 사용하지 마세요!
```

---

## 🔄 6. 마이그레이션 가이드

### conditional_edge → Command 변환

#### Before (conditional_edge)

```python
# 노드 함수
async def process_data(state):
    result = analyze(state["data"])
    return {
        "analysis_result": result,
        "status": "success" if result.valid else "failed"
    }

# 라우팅 함수
def route_after_process(state):
    if state.get("status") == "success":
        return "next_step"
    else:
        return "error_handler"

# 그래프 구성
builder.add_node("process", process_data)
builder.add_conditional_edges(
    "process",
    route_after_process,
    {
        "next_step": "next_step",
        "error_handler": "error_handler"
    }
)
```

#### After (Command) ✅

```python
# 노드 함수 (통합!)
async def process_data(state):
    result = analyze(state["data"])
    
    if result.valid:
        return Command(
            goto="next_step",
            update={"analysis_result": result}
        )
    else:
        return Command(
            goto="error_handler",
            update={"analysis_result": result, "error": "Analysis failed"}
        )

# 그래프 구성 (간단!)
builder.add_node("process", process_data)
# 끝!
```

**변화**:
- ✅ 2개 함수 → 1개 함수
- ✅ `status` 플래그 제거
- ✅ `add_conditional_edges` 제거
- ✅ 로직이 한 곳에 집중

---

## 💡 7. 실전 팁

### Tip 1: Command 타입 힌트 활용

```python
from typing import Literal
from langgraph.types import Command

async def my_node(
    state: MyState
) -> Command[Literal["path_a", "path_b", END]]:
    """타입 힌트로 가능한 경로 명시"""
    
    if condition:
        return Command(goto="path_a")
    else:
        return Command(goto="path_b")
```

**장점**: IDE가 자동완성 지원, 오타 방지

### Tip 2: 복잡한 조건은 헬퍼 함수로

```python
async def complex_node(state):
    """복잡한 조건 처리"""
    
    # 헬퍼 함수로 조건 판단
    next_node = determine_next_node(state)
    updates = prepare_updates(state)
    
    return Command(goto=next_node, update=updates)

def determine_next_node(state):
    """다음 노드 결정 로직"""
    if state["score"] > 90:
        return "excellent"
    elif state["score"] > 70:
        return "good"
    else:
        return "retry"

def prepare_updates(state):
    """상태 업데이트 준비"""
    return {
        "processed": True,
        "timestamp": get_timestamp()
    }
```

### Tip 3: 디버깅 로그 추가

```python
async def my_node(state):
    """디버깅이 쉬운 노드"""
    
    result = process(state)
    
    if result.success:
        next_node = "success_path"
        print(f"✅ Success! Going to {next_node}")
    else:
        next_node = "error_path"
        print(f"❌ Failed! Going to {next_node}")
    
    return Command(
        goto=next_node,
        update={"result": result}
    )
```

---

## 🎓 8. 실습 예제

### 예제: 사용자 인증 시스템

#### Command 방식 (권장)

```python
async def authenticate_user(state):
    """사용자 인증"""
    username = state["username"]
    password = state["password"]
    
    # 인증 시도
    auth_result = check_credentials(username, password)
    
    if auth_result.success:
        # 성공: 메인 페이지로
        return Command(
            goto="main_page",
            update={
                "user": auth_result.user,
                "token": auth_result.token,
                "authenticated": True
            }
        )
    elif auth_result.retry_available:
        # 실패하지만 재시도 가능
        return Command(
            goto="retry_login",
            update={
                "error": auth_result.error,
                "attempts": state.get("attempts", 0) + 1
            }
        )
    else:
        # 완전 실패: 에러 페이지로
        return Command(
            goto="error_page",
            update={
                "error": "Authentication failed",
                "locked": True
            }
        )

# 그래프 구성
builder.add_node("auth", authenticate_user)
builder.add_node("main_page", show_main_page)
builder.add_node("retry_login", show_retry_page)
builder.add_node("error_page", show_error_page)

builder.add_edge(START, "auth")
# Command가 자동으로 라우팅!
```

#### conditional_edge 방식 (비교용)

```python
# 노드 함수
async def authenticate_user(state):
    """사용자 인증"""
    username = state["username"]
    password = state["password"]
    
    auth_result = check_credentials(username, password)
    
    # 상태만 업데이트
    if auth_result.success:
        return {
            "user": auth_result.user,
            "token": auth_result.token,
            "authenticated": True,
            "auth_status": "success"
        }
    elif auth_result.retry_available:
        return {
            "error": auth_result.error,
            "attempts": state.get("attempts", 0) + 1,
            "auth_status": "retry"
        }
    else:
        return {
            "error": "Authentication failed",
            "locked": True,
            "auth_status": "failed"
        }

# 라우팅 함수 (별도!)
def route_after_auth(state):
    """인증 후 라우팅"""
    status = state.get("auth_status")
    
    if status == "success":
        return "main"
    elif status == "retry":
        return "retry"
    else:
        return "error"

# 그래프 구성
builder.add_node("auth", authenticate_user)
builder.add_node("main_page", show_main_page)
builder.add_node("retry_login", show_retry_page)
builder.add_node("error_page", show_error_page)

builder.add_edge(START, "auth")
builder.add_conditional_edges(
    "auth",
    route_after_auth,
    {
        "main": "main_page",
        "retry": "retry_login",
        "error": "error_page"
    }
)
```

**비교**:
- Command: 1개 함수, 명확한 로직
- conditional_edge: 2개 함수, `auth_status` 플래그 필요

---

## 🎯 핵심 요약

### Command (최신, 권장) ✅
```python
# 노드 함수가 모든 것을 처리
return Command(
    goto="next_node",
    update={"field": value}
)
```
- ✅ 간결하고 명확
- ✅ 로직이 한 곳에
- ✅ 상태 업데이트 동시 처리

### conditional_edge (구버전) ⚠️
```python
# 노드 함수
return {"field": value, "flag": status}

# 라우팅 함수 (별도)
def route(state):
    return "next_node"

# 그래프 빌더
builder.add_conditional_edges(...)
```
- ❌ 복잡하고 분산
- ❌ 플래그 필요
- ❌ 유지보수 어려움

### 결론
**새 프로젝트는 무조건 Command를 사용하세요!** 🚀

---

## 📚 참고 자료

- LangGraph Command API 문서
- LangGraph 마이그레이션 가이드
- Best Practices for Graph Design
