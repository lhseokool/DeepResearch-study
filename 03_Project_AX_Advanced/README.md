# Project AX Advanced

> DeepAgent 기반 계층적 멀티-에이전트 코드 분석 시스템

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![DeepAgents](https://img.shields.io/badge/framework-DeepAgents-green.svg)](https://github.com/deepagents/deepagents)
[![LangGraph](https://img.shields.io/badge/powered%20by-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)

## 개요

Project AX Advanced는 DeepAgent 프레임워크를 사용하는 지능형 코드 분석 시스템입니다. 계층적 멀티-에이전트 아키텍처를 통해 코드 분석, 영향도 평가, 리팩토링, 문서 동기화를 수행합니다.

### 핵심 기능

- **🔍 심층 코드 분석**: 멀티-레벨 영향도 분석
- **🤖 계층적 에이전트**: 분석, 리팩토링, 문서화 전문 서브에이전트
- **🔄 자가 치유 리팩토링**: 자동 오류 감지 및 수정
- **📚 문서 동기화**: 코드 변경에 따른 자동 문서 업데이트
- **🎯 동적 서브에이전트**: 런타임에 특화 에이전트 생성
- **💾 파일시스템 백엔드**: 세션 간 상태 보존

## 빠른 시작

### 설치

```bash
# 저장소 클론
git clone <repository-url>
cd 03_Project_AX_Advanced

# uv로 의존성 설치
uv sync

# 또는 pip 사용
pip install -e .
```

### 환경 설정

`.env` 파일 생성:

```env
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
WORKSPACE_ROOT=./workspace
```

### 기본 사용법

```python
from agentic_coding_assistant.graph import create_deep_analysis_agent, run_analysis

# 에이전트 생성
agent = await create_deep_analysis_agent(
    tools=[analyze_code_tool, refactor_tool],
    model="openai:gpt-4.1",
    enable_self_healing=True,
    enable_documentation_sync=True,
)

# 분석 실행
result = await run_analysis(
    request="함수 X 변경의 영향도 분석",
    tools=[analyze_code_tool],
    model="anthropic:claude-sonnet-4-5-20250929",
)

# 결과 확인
final_report = result["files"]["/output/final_report.md"]["content"]
print(final_report)
```

## 아키텍처

### 계층적 구조

```
DeepCodeAnalysisAgent (메인 오케스트레이터)
├── Analyzer SubAgent (코드 분석 및 영향도 감지)
├── Refactorer SubAgent (자가 치유 리팩토링)
├── Documenter SubAgent (문서 동기화)
└── Dynamic SubAgents (런타임 생성 전문가)
```

### 핵심 컴포넌트

1. **Orchestrator**: 워크플로우 관리 및 서브에이전트 조율
2. **SubAgents**: 특화된 작업 수행 에이전트
3. **Skills Registry**: 추상적 스킬과 구체적 도구 매핑
4. **Filesystem Backend**: 상태 관리용 가상 파일시스템
5. **Dynamic Agent Factory**: 온디맨드 전문 에이전트 생성

### 자동 미들웨어

DeepAgent는 다음 미들웨어를 자동으로 주입합니다:

- **TodoListMiddleware**: 계획 수립 및 추적
- **FilesystemMiddleware**: 파일 작업 (ls, read_file, write_file)
- **SubAgentMiddleware**: 서브에이전트 동적 할당
- **SummarizationMiddleware**: 컨텍스트 압축
- **AnthropicPromptCachingMiddleware**: 비용 최적화
- **PatchToolCallsMiddleware**: 도구 호출 수정

## 프로젝트 구조

```
03_Project_AX_Advanced/
├── src/agentic_coding_assistant/
│   ├── graph.py              # 메인 에이전트 생성
│   ├── state.py              # 상태 정의
│   ├── configuration.py      # 설정 관리
│   ├── prompts/              # 시스템 프롬프트
│   │   └── orchestrator.py   # 오케스트레이터 프롬프트
│   ├── subagents/            # 서브에이전트 설정
│   │   ├── analyzer.py       # 분석 에이전트
│   │   ├── refactorer.py     # 리팩토링 에이전트
│   │   └── documenter.py     # 문서화 에이전트
│   ├── skills/               # 스킬 레지스트리
│   │   ├── registry.py       # 스킬-도구 매핑
│   │   └── tool_collections.py
│   ├── tools/                # 동적 에이전트 도구
│   │   ├── subagent_tools.py # SpawnSubAgent 도구
│   │   └── dynamic.py        # 동적 에이전트 팩토리
│   └── utils/                # 유틸리티 함수
│       └── workspace.py      # 워크스페이스 관리
├── docs/                     # 문서
├── examples/                 # 사용 예시
└── tests/                    # 테스트
```

## 주요 기능

### 1. 코드 분석

- 의존성 추적을 포함한 정적 분석
- 코드 변경 영향도 평가
- 멀티 파일 분석 지원

### 2. 자가 치유 리팩토링

- 자동 테스트 생성
- 반복적 오류 수정
- 변경 적용 전 검증

### 3. 문서 동기화

- 코드-문서 불일치 감지
- 업데이트된 문서 생성
- 코드베이스 전체 일관성 유지

### 4. 동적 서브에이전트

- 런타임에 전문 에이전트 생성
- 스킬 기반 도구 할당
- 각 에이전트별 격리된 워크스페이스

## 워크스페이스 구조

```
workspace/
├── main_agent/              # 메인 에이전트 워크스페이스
│   ├── status/
│   │   ├── current_stage.txt
│   │   └── analysis_plan.md
│   └── output/
│       ├── analysis_results/
│       ├── refactoring_results/
│       └── final_report.md
├── analyzer_01/             # 개별 분석기 워크스페이스
└── test_analyzer/           # 동적 서브에이전트 워크스페이스
```

## 문서

- [아키텍처 상세](DEEPAGENT_ARCHITECTURE_UPDATE.md)
- [빠른 시작](docs/QUICKSTART.md)
- [고급 기능](docs/ADVANCED_FEATURES.md)
- [구현 가이드](docs/IMPLEMENTATION.md)

## 예시

```bash
# 예시 실행
python examples/deep_agent_demo.py
python examples/complete_workflow_demo.py
python examples/self_healing_demo.py
```

## 기술 스택

- **프레임워크**: DeepAgents, LangGraph
- **LLM**: OpenAI GPT-4, Anthropic Claude
- **언어**: Python 3.11+
- **패키지 관리**: uv

## 라이선스

MIT License

## 감사의 말

- [DeepAgents](https://github.com/deepagents/deepagents) 프레임워크 사용
- [LangGraph](https://github.com/langchain-ai/langgraph) 기반
- [DeepResearch](https://github.com/deepresearch/deepresearch) 아키텍처 참조
