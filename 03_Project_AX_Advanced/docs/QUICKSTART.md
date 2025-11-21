# Quick Start Guide

**버전**: 0.2.0  
**소요 시간**: 5-10분

## 📦 설치

```bash
# 프로젝트 디렉토리로 이동
cd project-ax-advanced

# 의존성 설치
uv sync

# 패키지 설치 (편집 가능 모드)
uv pip install -e .

# 환경 변수 설정
export OPENAI_API_KEY="your-api-key"
```

## 기본 사용법

### 1. CLI 사용

#### SPEED 모드 (빠른 분석)
```bash
.venv/bin/python -m agentic_coding_assistant.cli \
  --file src/agentic_coding_assistant/analyzers/speed_analyzer.py \
  --symbol SpeedAnalyzer \
  --mode SPEED \
  --max-depth 3
```

#### PRECISION 모드 (정밀 분석)
```bash
.venv/bin/python -m agentic_coding_assistant.cli \
  --file src/agentic_coding_assistant/analyzers/speed_analyzer.py \
  --symbol SpeedAnalyzer \
  --mode PRECISION \
  --project-root . \
  --human-in-loop
```

### 2. Python API 사용

```python
from dotenv import load_dotenv
from agentic_coding_assistant import (
    ImpactAnalysisCoordinator,
    AnalysisRequest,
    AnalysisMode
)

# 환경 변수 로드
load_dotenv()

# Coordinator 생성 (LLM 사용하지 않는 경우 생략 가능)
coordinator = ImpactAnalysisCoordinator()

# 분석 요청 생성
request = AnalysisRequest(
    mode=AnalysisMode.SPEED,
    file_path="path/to/your/file.py",
    symbol_name="function_name",
    max_depth=3
)

# 분석 실행
result = coordinator.analyze(request)

# 결과 출력
print(f"Success: {result.success}")
print(f"Dependencies: {len(result.dependencies)}")
for dep in result.dependencies:
    print(f"  - {dep.symbol_name} ({dep.impact_level.value})")
```

### 3. LLM 없이 직접 Analyzer 사용

```python
from agentic_coding_assistant.analyzers import SpeedAnalyzer
from agentic_coding_assistant.models.schema import AnalysisRequest, AnalysisMode

# Analyzer 직접 생성
analyzer = SpeedAnalyzer()

# 분석 요청
request = AnalysisRequest(
    mode=AnalysisMode.SPEED,
    file_path="path/to/file.py",
    symbol_name="function_name"
)

# 분석 실행 (LLM 불필요)
result = analyzer.analyze(request)
```

### 4. FastAPI 서버 실행

```bash
# API 서버 시작
.venv/bin/python -m agentic_coding_assistant.api

# 또는
.venv/bin/uvicorn agentic_coding_assistant.api:app --reload
```

서버 실행 후:
- API 문서: http://localhost:8000/docs
- 헬스 체크: http://localhost:8000/health

### 5. LangGraph Platform 사용

```bash
# LangGraph 서버 시작
langgraph dev
```

LangGraph Studio: http://localhost:8123

## 환경 설정

`.env` 파일에 다음 설정 추가:

```bash
# OpenAI API Key (Coordinator에서 LLM 사용 시 필요)
OPENAI_API_KEY=your-api-key-here

# 기타 설정
LANGFUSE_SECRET_KEY=your-key
LANGFUSE_PUBLIC_KEY=your-key
LANGFUSE_BASE_URL=https://us.cloud.langfuse.com
```

**참고**: SpeedAnalyzer를 직접 사용할 경우 OpenAI API Key 불필요

## 테스트 실행

```bash
# 단위 테스트
.venv/bin/pytest tests/

# 특정 테스트 파일
.venv/bin/pytest tests/test_speed_analyzer.py -v

# 커버리지 확인
.venv/bin/pytest --cov=agentic_coding_assistant tests/
```

## 예제 실행

```bash
# 전체 데모 (LLM 필요)
.venv/bin/python examples/demo.py

# 기본 테스트 (LLM 불필요)
.venv/bin/python test_basic.py
```

## 일반적인 문제 해결

### 1. ModuleNotFoundError: 'agentic_coding_assistant'
```bash
# 패키지 재설치
uv pip install -e .
```

### 2. OpenAI API Error
```bash
# .env 파일 확인
cat .env | grep OPENAI_API_KEY

# 환경 변수 로드 확인
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY'))"
```

### 3. Pyright Not Found (PRECISION 모드)
```bash
# Pyright 설치
uv pip install pyright

# 또는
npm install -g pyright
```

### 4. Tree-sitter 빌드 에러
```bash
# 시스템 컴파일러 확인
gcc --version  # Linux/macOS
cl.exe         # Windows

# 필요시 컴파일러 설치
# macOS: xcode-select --install
# Linux: sudo apt install build-essential
```

---

## 🚀 고급 기능 (v0.2.0)

### 6. 자율 코딩 with Self-Healing
```python
from agentic_coding_assistant.agents import SelfHealingAgent
from pathlib import Path

agent = SelfHealingAgent(work_dir=Path.cwd())

# Self-Healing (최대 3회 재시도)
result = await agent.self_heal(
    code=buggy_code,
    file_path="module.py",
    test_command="pytest tests/test_module.py",
)

print(f"성공: {result['success']}")
print(f"재시도 횟수: {result.get('healing_attempts', 0)}")
```

**데모 실행**:
```bash
python examples/self_healing_demo.py
```

### 7. 파일 시스템 탐색
```python
from agentic_coding_assistant.agents import FileSystemAgent

agent = FileSystemAgent(work_dir=Path.cwd())

# 프로젝트 컨텍스트 파악
context = agent.explore_context()
print(context["insights"])

# 패턴 검색
results = agent.pattern_search(
    pattern="**/*.py",
    query="def test_",
)
```

**데모 실행**:
```bash
python examples/filesystem_demo.py
```

### 8. 문서화 동기화
```python
from agentic_coding_assistant.agents import DocumentationAgent

agent = DocumentationAgent()

# 문서 동기화
result = await agent.synchronize_documentation(
    old_code=old_code,
    new_code=new_code,
    file_path="module.py",
    auto_apply=False,  # 제안만 생성
)
```

**데모 실행**:
```bash
python examples/documentation_demo.py
```

### 9. 완전한 워크플로우
```python
from agentic_coding_assistant.agents import AdvancedCoordinator

coordinator = AdvancedCoordinator(project_root=Path.cwd())

# 통합 워크플로우 (탐색 + 코딩 + 문서화)
result = await coordinator.refactor_with_healing(
    code=code,
    file_path="module.py",
    human_callback=lambda msg: True,
)
```

**데모 실행**:
```bash
python examples/complete_workflow_demo.py
```

---

## 📚 다음 단계

### 상세 문서
1. **기능 상세**: [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md)
2. **구현 세부사항**: [IMPLEMENTATION.md](IMPLEMENTATION.md)
3. **아키텍처**: [architecture_detailed.md](architecture_detailed.md)
4. **고급 빠른 시작**: [QUICKSTART_ADVANCED.md](QUICKSTART_ADVANCED.md)

### 예제 코드
- `examples/self_healing_demo.py` - 자율 코딩
- `examples/filesystem_demo.py` - 파일 시스템
- `examples/documentation_demo.py` - 문서화
- `examples/complete_workflow_demo.py` - 통합 워크플로우

### 문서 인덱스
- [docs/INDEX.md](INDEX.md) - 전체 문서 목록

---

## 🎯 주요 기능 요약

| 기능 | 설명 | 파일 |
|------|------|------|
| **영향도 분석** | SPEED/PRECISION 모드 | `coordinator.py` |
| **자율 코딩** | Self-Healing (Max 3 retries) | `self_healing_agent.py` |
| **문서 동기화** | Docstring + README + Swagger | `documentation_agent.py` |
| **파일 시스템** | FileSystemBackend 활용 | `filesystem_agent.py` |

---

**버전**: 0.2.0  
**최종 업데이트**: 2024-11-20  
**문서 인덱스**: [INDEX.md](INDEX.md)
