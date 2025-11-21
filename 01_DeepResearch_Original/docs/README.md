# DeepResearch 문서

DeepResearch_Original 코드베이스에 대한 종합 분석 문서입니다.

## 📚 문서 목록

### 기본 개념
1. **[아키텍처 개요](./01_아키텍처_개요.md)**
   - 시스템 전체 구조
   - 3계층 아키텍처 (Main Graph, Supervisor, Researcher)
   - 핵심 설계 원칙
   - 실행 흐름 예시

2. **[상태 관리](./02_상태_관리.md)**
   - State 계층 구조
   - AgentState, SupervisorState, ResearcherState
   - 커스텀 Reducer (override_reducer)
   - 상태 업데이트 패턴

3. **[워크플로우 상세](./03_워크플로우_상세.md)**
   - Phase 1: 사용자 명확화
   - Phase 2: 연구 계획서 작성
   - Phase 3: 연구 수행 (Supervisor)
   - Phase 4: 개별 연구 (Researcher)
   - Phase 5: 최종 보고서 생성

### 기술 활용
4. **[LangChain 활용](./04_LangChain_활용.md)**
   - 모델 초기화 및 설정
   - 구조화된 출력 (with_structured_output)
   - 도구 바인딩 (bind_tools)
   - 재시도 로직 (with_retry)
   - 메시지 관리
   - 비동기 처리

5. **[LangGraph 활용](./05_LangGraph_활용.md)**
   - StateGraph 정의
   - Command 기반 동적 라우팅
   - Subgraph 패턴
   - Context Schema 활용
   - 병렬 실행 패턴
   - 상태 업데이트 패턴

6. **[도구 시스템](./06_도구_시스템.md)**
   - Supervisor 도구 (ConductResearch, ResearchComplete, think_tool)
   - Researcher 도구 (tavily_search, think_tool)
   - MCP 도구 통합
   - 도구 실행 패턴
   - 네이티브 웹 검색 감지

### 고급 주제
7. **[프롬프트 전략](./07_프롬프트_전략.md)**
   - 명확화 프롬프트
   - 연구 계획 프롬프트
   - Supervisor 프롬프트
   - Researcher 프롬프트
   - 압축 프롬프트
   - 최종 보고서 프롬프트
   - 프롬프트 설계 원칙

8. **[에러 처리](./08_에러_처리.md)**
   - 토큰 제한 초과 처리
   - 구조화된 출력 재시도
   - 도구 실행 에러
   - MCP 인증 에러
   - 타임아웃 처리
   - 동시성 제한

### 실용 가이드
9. **[실행 예시](./09_실행_예시.md)**
   - 기본 실행 방법
   - 설정 커스터마이징
   - 실행 흐름 예시

10. **[최적화 팁](./10_최적화_팁.md)**
    - 성능 최적화
    - 비용 최적화
    - 품질 최적화
    - 디버깅
    - 확장성

## 🎯 빠른 시작

### 핵심 개념 이해
1. [아키텍처 개요](./01_아키텍처_개요.md) - 전체 시스템 구조 파악
2. [워크플로우 상세](./03_워크플로우_상세.md) - 실행 흐름 이해

### 기술 학습
1. [LangChain 활용](./04_LangChain_활용.md) - LangChain 패턴
2. [LangGraph 활용](./05_LangGraph_활용.md) - LangGraph 패턴

### 실전 적용
1. [실행 예시](./09_실행_예시.md) - 실제 사용법
2. [최적화 팁](./10_최적화_팁.md) - 성능 개선

## 🔑 핵심 특징

### 계층적 멀티 에이전트
- **Main Graph**: 전체 워크플로우 조정
- **Supervisor**: 연구 전략 수립 및 작업 위임
- **Researcher**: 실제 연구 수행

### 병렬 처리
- 여러 Researcher 동시 실행
- `asyncio.gather()`를 통한 비동기 처리
- 동시성 제한으로 리소스 관리

### 동적 라우팅
- `Command(goto=...)` 패턴
- 조건부 흐름 제어
- 조기 종료 최적화

### 견고성
- 토큰 제한 초과 처리
- 자동 재시도 로직
- 에러 복구 메커니즘

## 📊 시스템 흐름

```
User Input
    ↓
clarify_with_user (명확화)
    ↓
write_research_brief (계획 수립)
    ↓
research_supervisor (Supervisor Subgraph)
    ├─ supervisor (전략 수립)
    └─ supervisor_tools (작업 위임)
        ├─ Researcher 1 (병렬)
        ├─ Researcher 2 (병렬)
        └─ Researcher N (병렬)
            ├─ researcher (연구 수행)
            ├─ researcher_tools (도구 실행)
            └─ compress_research (결과 압축)
    ↓
final_report_generation (최종 보고서)
    ↓
Output
```

## 🛠️ 기술 스택

- **LangChain**: LLM 통합, 도구 바인딩, 구조화된 출력
- **LangGraph**: 상태 기반 워크플로우, Subgraph, 동적 라우팅
- **Pydantic**: 타입 안전성, 데이터 검증
- **asyncio**: 비동기 병렬 처리
- **Tavily**: 웹 검색 API
- **MCP**: 외부 도구 통합 프로토콜

## 📝 참고사항

- 모든 문서는 실제 코드 구현을 기반으로 작성되었습니다
- 코드 예시는 `src/` 디렉토리의 실제 파일에서 발췌했습니다
- 추가 질문이나 개선 사항은 이슈로 등록해주세요
