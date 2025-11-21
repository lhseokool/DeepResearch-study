# Documentation Index

**Version**: 0.2.0  
**Last Updated**: 2024-11-20

## 📚 문서 구조

### 시작하기
1. **[README.md](../README.md)** - 프로젝트 개요 및 주요 기능
2. **[QUICKSTART.md](QUICKSTART.md)** - 빠른 시작 가이드 (5분 안에 시작)
3. **[QUICKSTART_ADVANCED.md](QUICKSTART_ADVANCED.md)** - 고급 기능 빠른 시작

### 아키텍처
4. **[architecture.excalidraw](architecture.excalidraw)** - 시스템 아키텍처 다이어그램
5. **[architecture_detailed.md](architecture_detailed.md)** - 상세 아키텍처 (Mermaid 다이어그램)

### 기능 문서
6. **[ADVANCED_FEATURES.md](ADVANCED_FEATURES.md)** - 고급 기능 상세 가이드
   - FR-FS: 파일 시스템 탐색
   - FR-AC: 자율 코딩 및 복구
   - FR-DS: 문서화 동기화
7. **[FILESYSTEM_AGENT_GUIDE.md](FILESYSTEM_AGENT_GUIDE.md)** - FileSystem Agent 사용 가이드 (create_deep_agent)
8. **[OPENROUTER_SETUP.md](OPENROUTER_SETUP.md)** - OpenRouter API 설정 및 사용 가이드

### 구현 문서
9. **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - 전체 구현 세부사항
10. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - 프로젝트 요약 및 요구사항 충족 여부

### 추가 문서
11. **[CHANGELOG.md](../CHANGELOG.md)** - 버전별 변경 이력
12. **[REQUIREMENTS_CHECKLIST.md](../REQUIREMENTS_CHECKLIST.md)** - 요구사항 체크리스트
13. **[FINAL_VERIFICATION.md](../FINAL_VERIFICATION.md)** - 최종 검증 보고서
14. **[IMPLEMENTATION_SUMMARY.md](../IMPLEMENTATION_SUMMARY.md)** - 구현 요약

---

## 🎯 목적별 문서 가이드

### 처음 사용하는 경우
1. [README.md](../README.md) - 프로젝트 이해
2. [QUICKSTART.md](QUICKSTART.md) - 설치 및 기본 사용법
3. [architecture_detailed.md](architecture_detailed.md) - 구조 파악

### 고급 기능 사용
1. [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md) - 기능 상세 설명
2. [QUICKSTART_ADVANCED.md](QUICKSTART_ADVANCED.md) - 고급 기능 예제
3. [examples/](../examples/) - 데모 코드

### 개발/기여
1. [IMPLEMENTATION.md](IMPLEMENTATION.md) - 구현 세부사항
2. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 프로젝트 구조
3. [tests/](../tests/) - 테스트 코드

### 요구사항 검증
1. [REQUIREMENTS_CHECKLIST.md](../REQUIREMENTS_CHECKLIST.md) - 요구사항 체크리스트
2. [FINAL_VERIFICATION.md](../FINAL_VERIFICATION.md) - 검증 보고서
3. [CHANGELOG.md](../CHANGELOG.md) - 변경 이력

---

## 📋 주요 기능별 문서

### 대기능1: 영향도 분석 (FR-IA)
- [IMPLEMENTATION.md - Section 2~5](IMPLEMENTATION.md#2-speed-mode-fr-ia-02)
- [PROJECT_SUMMARY.md - FR-IA](PROJECT_SUMMARY.md#-fr-ia-01-dual-mode-selection)
- [QUICKSTART.md](QUICKSTART.md)

### 대기능2: 자율 코딩 및 복구 (FR-AC)
- [ADVANCED_FEATURES.md - FR-AC](ADVANCED_FEATURES.md#fr-ac-autonomous-coding--recovery)
- [QUICKSTART_ADVANCED.md - Self-Healing](QUICKSTART_ADVANCED.md#1-self-healing-agent)
- [examples/self_healing_demo.py](../examples/self_healing_demo.py)

### 대기능3: 문서화 동기화 (FR-DS)
- [ADVANCED_FEATURES.md - FR-DS](ADVANCED_FEATURES.md#fr-ds-documentation-synchronization)
- [QUICKSTART_ADVANCED.md - Documentation](QUICKSTART_ADVANCED.md#3-documentation-agent)
- [examples/documentation_demo.py](../examples/documentation_demo.py)

### 대기능4: 파일 시스템 탐색 (FR-FS)
- [ADVANCED_FEATURES.md - FR-FS](ADVANCED_FEATURES.md#fr-fs-deep-file-system-exploration)
- [QUICKSTART_ADVANCED.md - FileSystem](QUICKSTART_ADVANCED.md#2-filesystem-agent)
- [examples/filesystem_demo.py](../examples/filesystem_demo.py)

---

## 🔍 주제별 검색

### DeepAgents 패턴
- [IMPLEMENTATION.md - DeepAgent 패턴](IMPLEMENTATION.md#1-deepagent-패턴-구현)
- [architecture_detailed.md - DeepAgent Pattern](architecture_detailed.md#deepagent-pattern-implementation)
- [REQUIREMENTS_CHECKLIST.md - DeepAgent](../REQUIREMENTS_CHECKLIST.md#-deepagent-패턴-활용)

### Self-Healing Loop
- [ADVANCED_FEATURES.md - Self-Healing](ADVANCED_FEATURES.md#self-healing-loop-max-3-retries)
- [FINAL_VERIFICATION.md - FR-AC-02](../FINAL_VERIFICATION.md#fr-ac-02-self-healing-loop)
- [src/.../self_healing_agent.py](../src/agentic_coding_assistant/agents/self_healing_agent.py)

### Human-in-the-Loop
- [IMPLEMENTATION.md - Human-in-the-Loop](IMPLEMENTATION.md#5-human-in-the-loop-fr-ia-04)
- [ADVANCED_FEATURES.md - Human Approval](ADVANCED_FEATURES.md#human-in-the-loop)
- [FINAL_VERIFICATION.md - Human-in-Loop](../FINAL_VERIFICATION.md#-human-in-the-loop-모든-단계)

### FileSystemBackend & create_deep_agent
- [FILESYSTEM_AGENT_GUIDE.md](FILESYSTEM_AGENT_GUIDE.md) - 완전한 사용 가이드 ✨
- [ADVANCED_FEATURES.md - FileSystem](ADVANCED_FEATURES.md#fr-fs-01-contextual-exploration)
- [REQUIREMENTS_CHECKLIST.md - FileSystemBackend](../REQUIREMENTS_CHECKLIST.md#deepagents-library-필수-사용)
- [src/.../filesystem_agent.py](../src/agentic_coding_assistant/agents/filesystem_agent.py)

---

## 📊 다이어그램 목록

### 시스템 아키텍처
- [architecture.excalidraw](architecture.excalidraw) - Excalidraw 형식
- [architecture_detailed.md - System Architecture](architecture_detailed.md#system-architecture)

### 워크플로우
- [architecture_detailed.md - Component Flow](architecture_detailed.md#component-flow-diagram)
- [architecture_detailed.md - Data Flow](architecture_detailed.md#data-flow-diagram)

### 내부 구조
- [architecture_detailed.md - SPEED Mode](architecture_detailed.md#speed-mode-internal-flow)
- [architecture_detailed.md - PRECISION Mode](architecture_detailed.md#precision-mode-internal-flow)
- [architecture_detailed.md - DeepAgent Pattern](architecture_detailed.md#deepagent-pattern-implementation)

---

## 🔗 외부 참고 자료

### 공식 문서
- [DeepAgents Documentation](https://docs.langchain.com/oss/python/deepagents/overview)
- [DeepAgents Blog](https://blog.langchain.com/doubling-down-on-deepagents/)
- [FileSystemBackend](https://docs.langchain.com/oss/python/deepagents/backends#filesystembackend-local-disk)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

### 템플릿 참고
- [FastAPI LangGraph Template](https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template)

---

## 📝 문서 작성 가이드

### 문서 업데이트 시
1. 버전 번호 확인 (현재: 0.2.0)
2. 날짜 업데이트
3. 관련 문서 링크 확인
4. 코드 예제 동작 확인

### 새 문서 추가 시
1. 이 INDEX.md에 항목 추가
2. README.md의 문서 섹션 업데이트
3. 관련 문서에 상호 링크 추가

---

**마지막 업데이트**: 2024-11-20  
**버전**: 0.2.0  
**유지보수**: Agentic Coding Assistant Team
