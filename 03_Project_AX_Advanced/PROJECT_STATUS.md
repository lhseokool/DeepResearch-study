# Project AX Advanced - 현재 상태

> 최종 업데이트: 2025-11-21

---

## 📊 프로젝트 개요

**Project AX Advanced**는 DeepAgent 프레임워크를 기반으로 한 계층적 멀티-에이전트 코드 분석 시스템입니다.

### 핵심 기술
- **프레임워크**: DeepAgents, LangGraph
- **언어**: Python 3.11+
- **LLM**: OpenAI GPT-4, Anthropic Claude
- **패키지 관리**: uv

---

## 🏗️ 현재 아키텍처

### 에이전트 구조

```
DeepCodeAnalysisAgent (Main Orchestrator)
├── Analyzer SubAgent (코드 분석)
├── Refactorer SubAgent (리팩토링)
├── Documenter SubAgent (문서화)
└── Dynamic SubAgents (런타임 생성)
```

### 핵심 컴포넌트

| 컴포넌트 | 파일 | 설명 |
|---------|------|------|
| **Main Agent** | `graph.py` | create_deep_agent 기반 메인 에이전트 |
| **State** | `state.py` | 상태 정의 및 override_reducer |
| **Configuration** | `configuration.py` | 설정 관리 |
| **Orchestrator Prompt** | `prompts/orchestrator.py` | 오케스트레이터 시스템 프롬프트 |
| **SubAgents** | `subagents/*.py` | 분석, 리팩토링, 문서화 에이전트 |
| **Skills Registry** | `skills/registry.py` | 스킬-도구 매핑 |
| **Dynamic Tools** | `tools/subagent_tools.py` | SpawnSubAgent 도구 |
| **Workspace Utils** | `utils/workspace.py` | 워크스페이스 관리 |

---

## 📁 프로젝트 구조

```
03_Project_AX_Advanced/
├── src/agentic_coding_assistant/
│   ├── graph.py                  # ✅ 메인 에이전트 (create_deep_agent)
│   ├── state.py                  # ✅ 상태 정의 (override_reducer)
│   ├── configuration.py          # ✅ 설정 관리
│   ├── prompts/
│   │   ├── __init__.py           # ✅ 프롬프트 export
│   │   └── orchestrator.py       # ✅ 오케스트레이터 프롬프트
│   ├── subagents/
│   │   ├── __init__.py
│   │   ├── analyzer.py           # ✅ 분석 서브에이전트
│   │   ├── refactorer.py         # ✅ 리팩토링 서브에이전트
│   │   └── documenter.py         # ✅ 문서화 서브에이전트
│   ├── skills/
│   │   ├── __init__.py           # ✅ 스킬 모듈
│   │   ├── registry.py           # ✅ 스킬 레지스트리
│   │   └── tool_collections.py   # ✅ 도구 컬렉션
│   ├── tools/
│   │   ├── __init__.py           # ✅ 도구 모듈
│   │   ├── subagent_tools.py     # ✅ SpawnSubAgent 도구
│   │   └── dynamic.py            # ✅ 동적 서브에이전트 팩토리
│   └── utils/
│       └── workspace.py          # ✅ 워크스페이스 관리
├── docs/
│   ├── ADVANCED_FEATURES.md      # 고급 기능
│   ├── FILESYSTEM_AGENT_GUIDE.md # 파일시스템 가이드
│   ├── IMPLEMENTATION.md         # 구현 가이드
│   ├── OPENROUTER_SETUP.md       # OpenRouter 설정
│   ├── QUICKSTART.md             # 빠른 시작
│   ├── QUICKSTART_ADVANCED.md    # 고급 시작
│   ├── architecture.excalidraw   # 아키텍처 다이어그램
│   └── architecture_detailed.md  # 상세 아키텍처
├── examples/
│   ├── complete_workflow_demo.py # 전체 워크플로우
│   ├── deep_agent_demo.py        # DeepAgent 데모
│   ├── documentation_demo.py     # 문서화 데모
│   ├── filesystem_demo.py        # 파일시스템 데모
│   └── self_healing_demo.py      # 자가 치유 데모
├── tests/
│   ├── test_advanced_agents.py
│   ├── test_coordinator.py
│   └── test_subagents.py
├── ARCHITECTURE.md               # ✅ 아키텍처 문서 (현재 상태)
├── README.md                     # ✅ 프로젝트 소개 (현재 상태)
├── PROJECT_STATUS.md             # ✅ 현재 상태 문서
└── pyproject.toml                # 의존성 관리
```

---

## ✅ 구현 완료 항목

### 1. DeepAgent 프레임워크 통합
- [x] `create_deep_agent` 기반 메인 에이전트
- [x] `SubAgent` 패턴 서브에이전트
- [x] `FilesystemBackend` 통합
- [x] 자동 미들웨어 주입

### 2. 계층적 에이전트 구조
- [x] Orchestrator (메인 에이전트)
- [x] Analyzer SubAgent (분석)
- [x] Refactorer SubAgent (리팩토링)
- [x] Documenter SubAgent (문서화)
- [x] Dynamic SubAgent Factory (동적 생성)

### 3. 스킬 레지스트리 시스템
- [x] SkillRegistry 클래스
- [x] 스킬-도구 매핑
- [x] 도구 컬렉션 정의
- [x] 동적 도구 할당

### 4. 동적 서브에이전트
- [x] SpawnSubAgent 도구
- [x] create_dynamic_subagent 팩토리
- [x] 스킬 기반 도구 할당
- [x] 격리된 워크스페이스

### 5. 상태 관리
- [x] AgentState 정의
- [x] override_reducer 함수
- [x] 구조화된 출력 모델

### 6. 워크스페이스 관리
- [x] get_workspace_root 함수
- [x] get_agent_workspace 함수
- [x] 환경 변수 지원

### 7. 프롬프트 시스템
- [x] Orchestrator 프롬프트
- [x] Analyzer 프롬프트
- [x] Refactorer 프롬프트
- [x] Documenter 프롬프트

### 8. 문서화
- [x] README.md (현재 상태 기준)
- [x] ARCHITECTURE.md (상세 아키텍처)
- [x] PROJECT_STATUS.md (현재 상태)
- [x] 기존 docs 유지

---

## 🎯 주요 기능

### 1. 코드 분석
- 의존성 추적
- 영향도 평가
- 멀티 파일 분석

### 2. 자가 치유 리팩토링
- 자동 테스트 생성
- 반복적 오류 수정
- 변경 전 검증

### 3. 문서 동기화
- 코드-문서 불일치 감지
- 자동 문서 업데이트
- 일관성 유지

### 4. 동적 서브에이전트
- 런타임 에이전트 생성
- 스킬 기반 도구 할당
- 격리된 워크스페이스

---

## 🚀 사용 방법

### 설치

```bash
cd 03_Project_AX_Advanced
uv sync
```

### 환경 설정

```bash
cp .env.example .env
# .env 파일에 API 키 설정
```

### 기본 실행

```python
from agentic_coding_assistant.graph import create_deep_analysis_agent

agent = await create_deep_analysis_agent(
    tools=[analyze_code_tool],
    model="openai:gpt-4.1",
    enable_self_healing=True,
)

result = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "Analyze function X"}]},
    config={"configurable": {"thread_id": "analysis_001"}},
)
```

### 예시 실행

```bash
python examples/deep_agent_demo.py
python examples/complete_workflow_demo.py
```

---

## 📚 문서

| 문서 | 설명 |
|------|------|
| [README.md](README.md) | 프로젝트 소개 및 빠른 시작 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 상세 아키텍처 설명 |
| [docs/QUICKSTART.md](docs/QUICKSTART.md) | 빠른 시작 가이드 |
| [docs/ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md) | 고급 기능 |
| [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md) | 구현 가이드 |

---

## 🔧 설정

### 환경 변수

```env
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
WORKSPACE_ROOT=./workspace
```

### 에이전트 설정

```python
DeepAgentConfiguration(
    main_model="openai:gpt-4.1",
    analyzer_model="anthropic:claude-sonnet-4-5-20250929",
    max_parallel_analyzers=3,
    max_coordinator_iterations=10,
    enable_self_healing=True,
    enable_documentation_sync=True,
)
```

---

## 🎨 디자인 패턴

### 1. 계층적 에이전트
- Orchestrator → SubAgents → Tools
- 명확한 책임 분리

### 2. 파일시스템 메모리
- 모든 상태를 파일로 저장
- 세션 간 연속성

### 3. 스킬 기반 도구 관리
- 추상적 스킬 ↔ 구체적 도구
- 동적 할당

### 4. 병렬 실행
- 복잡도 기반 분석기 수 결정
- 효율적인 리소스 사용

### 5. 자동 미들웨어
- TodoList, Filesystem, SubAgent
- Summarization, PromptCaching

---

## 🔍 워크플로우

```
STAGE 0: Context Restoration
  ↓
STAGE 1: Analysis Planning
  ↓
STAGE 2: Parallel Analysis (1-5 analyzers)
  ↓
STAGE 3: Synthesis
  ↓
STAGE 4: Action (Refactoring/Documentation)
  ↓
STAGE 5: Final Report
```

---

## 📊 현재 상태 요약

✅ **완전히 구현됨**
- DeepAgent 프레임워크 통합
- 계층적 멀티-에이전트 구조
- 스킬 레지스트리 시스템
- 동적 서브에이전트 생성
- 파일시스템 백엔드
- 자동 미들웨어

✅ **문서화 완료**
- 현재 상태 기준 README
- 상세 아키텍처 문서
- 사용 예시 및 가이드

✅ **코드 정리 완료**
- 중복 문서 제거
- 불필요한 코드 삭제
- 명확한 구조

---

## 🎯 다음 단계 (선택적)

1. **실제 도구 구현**: analyze_code, refactor_code 등
2. **통합 테스트**: 전체 워크플로우 테스트
3. **성능 최적화**: 병렬 실행 벤치마크
4. **프롬프트 개선**: 각 에이전트 프롬프트 최적화
5. **추가 서브에이전트**: 테스트, 보안 분석 등

---

## 📝 라이선스

MIT License

---

**Project AX Advanced**는 DeepAgent 프레임워크를 활용한 프로덕션 레디 코드 분석 시스템입니다.
