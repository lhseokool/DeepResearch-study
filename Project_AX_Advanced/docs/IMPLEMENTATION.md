# Implementation Details

**버전**: 0.2.0  
**최종 업데이트**: 2024-11-20

## 프로젝트 개요

Agentic Coding Assistant는 AI 기반 자율 코딩 및 영향도 분석 시스템입니다. DeepAgent 패턴을 활용하여 4대 기능을 제공합니다:

1. **영향도 분석** (FR-IA): SPEED/PRECISION 모드
2. **자율 코딩 및 복구** (FR-AC): Self-Healing Loop
3. **문서화 동기화** (FR-DS): Docstring + README + Swagger
4. **파일 시스템 탐색** (FR-FS): DeepAgents FileSystemBackend

## 핵심 구현 사항

### 1. DeepAgent 패턴 구현

#### Planning (계획 수립)
- `ImpactAnalysisCoordinator._create_plan()`: LLM을 활용한 분석 계획 수립
- 분석 모드 적절성 평가
- 잠재적 문제점 식별
- Fallback 준비 여부 결정

#### FileSystem (파일 시스템 접근)
- `ImpactAnalysisCoordinator._verify_file_access()`: 파일 접근성 검증
- `file_utils.py`: 파일 탐색 및 안전한 읽기 유틸리티
- 가상 환경 및 숨김 디렉토리 자동 제외

#### SubAgent (하위 에이전트)
- `ImpactAnalysisCoordinator._execute_with_subagent()`: 적절한 분석기에 작업 위임
- SpeedAnalyzer 또는 PrecisionAnalyzer로 라우팅
- 결과 통합 및 후처리

### 2. SPEED Mode (FR-IA-02)

**구현 파일**: `analyzers/speed_analyzer.py`

**핵심 기술**:
- **Tree-sitter**: Python AST 파싱
- **NetworkX**: 의존성 그래프 구축 및 탐색

**작동 방식**:
1. 프로젝트 내 모든 Python 파일 파싱
2. 함수/클래스 정의 추출
3. 함수 호출 관계 분석
4. Directed Graph 생성
5. BFS로 역방향 의존성 탐색
6. In-degree 기반 영향도 순위 산정

**성능**:
- 목표: 10k 라인 기준 5초 이내
- 빌드 환경 불필요
- False Positive 가능성 있음 (동적 타이핑)

**영향도 레벨 산정**:
```python
in_degree >= 5 → CRITICAL
in_degree >= 3 → HIGH
in_degree >= 1 → MEDIUM
else → LOW
```

### 3. PRECISION Mode (FR-IA-03)

**구현 파일**: `analyzers/precision_analyzer.py`

**핵심 기술**:
- **LSP (Language Server Protocol)**: Pyright 활용
- **컴파일러 수준 분석**: 정확한 타입 추론

**작동 방식**:
1. Pyright 가용성 확인
2. 심볼 위치 파악
3. Pyright CLI 실행
4. JSON 출력 파싱
5. 참조 위치 추출
6. 파일별 참조 빈도 기반 영향도 산정

**요구사항**:
- Pyright 설치 필요: `pip install pyright`
- 프로젝트 빌드 환경 필요
- 의존성 패키지 설치 필요

**영향도 레벨 산정**:
```python
reference_count >= 10 → CRITICAL
reference_count >= 5 → HIGH
reference_count >= 2 → MEDIUM
else → LOW
```

### 4. LangGraph 워크플로우 (FR-IA-01)

**구현 파일**: `graph.py`, `nodes/analysis_nodes.py`

**워크플로우 구조**:
```
validate_input → decide_mode → execute_analysis → [fallback?]
                                                 ↓
                                         handle_fallback → END
```

**노드 설명**:

1. **validate_input**: 입력 검증
   - file_path 존재 확인
   - symbol_name 검증
   - 초기 상태 설정

2. **decide_mode**: 모드 결정
   - 요청된 모드 확인
   - PRECISION 모드 가용성 체크
   - 필요시 SPEED로 자동 전환

3. **execute_analysis**: 분석 실행
   - Coordinator를 통한 분석 수행
   - 결과 저장
   - 에러 발생 시 fallback 플래그 설정

4. **handle_fallback**: Fallback 처리
   - SPEED 모드로 재시도
   - Metadata에 fallback 정보 기록
   - 무한 루프 방지 (최대 2회 시도)

### 5. Human-in-the-Loop (FR-IA-04)

**구현 파일**: `agents/coordinator.py`

**메서드**: `analyze_with_human_in_loop()`

**작동 방식**:
1. 초기 분석 시도
2. 실패 시 fallback_suggested 확인
3. 콜백 함수 호출로 사용자 확인
4. 승인 시 SPEED 모드로 재분석
5. Metadata에 human_approved_fallback 기록

**사용 예시**:
```python
def human_callback(message: str) -> bool:
    response = input(f"{message} (yes/no): ")
    return response.lower() == "yes"

result = coordinator.analyze_with_human_in_loop(
    request, 
    human_callback
)
```

### 6. API 인터페이스

**구현 파일**: `api.py`

**엔드포인트**:

1. **POST /analyze**: 영향도 분석 수행
   ```json
   {
     "mode": "SPEED",
     "file_path": "/path/to/file.py",
     "symbol_name": "function_name",
     "max_depth": 3
   }
   ```

2. **GET /modes**: 사용 가능한 모드 조회
   - SPEED/PRECISION 가용성 확인
   - 각 모드 설명 반환

3. **GET /health**: 헬스 체크

### 7. CLI 인터페이스

**구현 파일**: `cli.py`

**주요 기능**:
- 명령줄 인자 파싱
- 파일 존재 확인
- 분석 실행 및 결과 출력
- JSON 파일로 결과 저장
- Human-in-the-loop 지원

**사용 예시**:
```bash
python -m agentic_coding_assistant.cli \
  --file path/to/file.py \
  --symbol function_name \
  --mode SPEED \
  --max-depth 3 \
  --human-in-loop \
  --output results.json
```

## 데이터 모델

### AnalysisMode
```python
class AnalysisMode(str, Enum):
    SPEED = "SPEED"
    PRECISION = "PRECISION"
```

### AnalysisRequest
- mode: 분석 모드
- file_path: 분석 대상 파일
- symbol_name: 분석 대상 심볼
- project_root: 프로젝트 루트 (선택)
- max_depth: 최대 탐색 깊이

### AnalysisResult
- mode: 사용된 모드
- success: 성공 여부
- dependencies: 의존성 목록
- error_message: 에러 메시지
- execution_time: 실행 시간
- metadata: 추가 정보
- fallback_suggested: Fallback 제안 여부

### DependencyNode
- file_path: 파일 경로
- symbol_name: 심볼 이름
- line_number: 라인 번호
- node_type: 노드 타입 (function/class/variable)
- impact_level: 영향도 레벨

### ImpactLevel
```python
class ImpactLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
```

## 테스트

### 단위 테스트

**파일**: `tests/test_speed_analyzer.py`
- 기본 분석 기능
- 파일 존재하지 않을 때 처리
- 메타데이터 확인

**파일**: `tests/test_coordinator.py`
- Coordinator 기본 동작
- 파일 접근 검증
- Human-in-the-loop 기능

### 통합 테스트

**파일**: `examples/demo.py`
- SPEED 모드 데모
- PRECISION 모드 데모
- Human-in-the-loop 데모

## 성능 최적화

### SPEED Mode
1. **파일 캐싱**: 동일 프로젝트 재분석 시 파싱 결과 재사용 가능
2. **병렬 처리**: 여러 파일 동시 파싱 (미구현, 향후 개선)
3. **그래프 프루닝**: 불필요한 노드 제거

### PRECISION Mode
1. **LSP 서버 재사용**: 프로세스 재시작 없이 여러 쿼리 수행
2. **인덱스 캐싱**: Pyright 인덱스 재활용
3. **타임아웃 설정**: 무한 대기 방지 (30초)

## 에러 처리

### 일반적인 에러
1. **FileNotFoundError**: 파일이 존재하지 않을 때
2. **PermissionError**: 파일 접근 권한 없을 때
3. **TimeoutError**: LSP 서버 응답 지연
4. **ParseError**: 파일 파싱 실패

### Fallback 메커니즘
1. PRECISION 모드 실패 → fallback_suggested = True
2. Human-in-the-loop으로 사용자 확인
3. 승인 시 SPEED 모드로 재시도
4. 실패 이력 metadata에 기록

## 확장 가능성

### 추가 언어 지원
- Tree-sitter 언어 파서 추가
- LSP 서버 통합 (예: jdtls for Java)

### 추가 분석 모드
- HYBRID: SPEED + PRECISION 조합
- CACHE: 캐시된 결과 재사용

### 고급 기능
- 변경 영향도 시뮬레이션
- 리팩토링 제안
- 순환 의존성 감지
- 코드 복잡도 분석

## 의존성

### 핵심 의존성
- `tree-sitter`: AST 파싱
- `tree-sitter-python`: Python 언어 지원
- `networkx`: 그래프 분석
- `pyright`: LSP 서버
- `langgraph`: 워크플로우 관리
- `langchain`: LLM 통합
- `fastapi`: API 서버

### 선택적 의존성
- `pytest`: 테스트
- `uvicorn`: ASGI 서버
- `ruff`: 코드 린팅

## 배포

### 로컬 개발
```bash
uv sync
uv pip install -e .
```

### LangGraph Platform
```bash
langgraph dev
```

### Docker (미구현)
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install .
CMD ["uvicorn", "agentic_coding_assistant.api:app", "--host", "0.0.0.0"]
```

---

## 대기능2: 자율 코딩 및 복구 (FR-AC)

### FR-AC-01~03 구현

**구현 파일**: `agents/self_healing_agent.py`

### Self-Healing Loop (FR-AC-02)

**핵심 설정**:
```python
MAX_RETRIES = 3  # 최대 재시도 횟수
```

**Process Flow**:
1. **Execute**: 코드 실행 또는 테스트
2. **Analyze**: 에러 타입 분류 (7가지)
3. **Prompting**: LLM에 코드 + 에러 + 문서 전달
4. **Patch**: LLM 생성 수정분 적용
5. **Retry**: 재시도 (최대 3회)

**에러 타입 분류**:
- SYNTAX_ERROR: 구문 오류
- IMPORT_ERROR: import 오류
- TYPE_ERROR: 타입 오류
- NAME_ERROR: 이름 오류
- ATTRIBUTE_ERROR: 속성 오류
- TEST_FAILURE: 테스트 실패
- RUNTIME_ERROR: 런타임 오류
- UNKNOWN: 알 수 없음

**최대 횟수 도달 시**:
```python
return {
    "success": False,
    "attempts": MAX_RETRIES,
    "message": f"Failed after {MAX_RETRIES} attempts",
    "healing_history": history,  # 전체 히스토리 제공
}
```

### Test Generation (FR-AC-03)

**기능**:
- pytest/unittest 자동 생성
- Happy path, Edge case, Error condition 커버
- 테스트 자동 실행 및 검증

**메서드**:
- `generate_unit_tests()`: 테스트 코드 생성
- `refactor_with_tests()`: 리팩토링 + 테스트 통합

---

## 대기능3: 문서화 동기화 (FR-DS)

### FR-DS-01 구현

**구현 파일**: `agents/documentation_agent.py`

### 핵심 기능

**1. Docstring 생성 및 업데이트**:
```python
async def generate_docstring(self, code, function_name, context):
    # LLM을 사용하여 고품질 docstring 생성
    # Google/NumPy 스타일 지원
```

**2. README 동기화**:
```python
async def update_readme(self, code_changes, readme_path):
    # 코드 변경 사항을 README에 반영
    # 새 기능, API 변경 등 자동 업데이트
```

**3. Swagger/API 문서 업데이트**:
```python
async def update_api_documentation(self, api_changes):
    # FastAPI/Swagger 문서 자동 생성
```

### AST 기반 변경 감지

**작동 방식**:
1. Old code와 New code를 AST로 파싱
2. 함수/클래스 추가/수정/삭제 감지
3. Docstring 변경 여부 판단
4. 관련 문서 파일 식별

### Human-in-the-Loop

```python
async def synchronize_documentation(
    self, old_code, new_code,
    auto_apply=False  # False일 경우 제안만 반환
):
    # 제안 생성
    updates = await self.detect_documentation_needs(...)
    
    if auto_apply:
        # 자동 적용
    else:
        # 사용자 승인 대기
        return {"proposed_updates": updates}
```

---

## 대기능4: 파일 시스템 탐색 (FR-FS)

### FileSystemBackend 필수 사용

**구현 파일**: `agents/filesystem_agent.py`

**핵심 import**:
```python
from deepagents.backends import FileSystemBackend  # 필수

class FileSystemAgent:
    def __init__(self, work_dir: str | Path, ...):
        self.fs_backend = FileSystemBackend(root_path=str(work_dir))
```

### FR-FS-01: Contextual Exploration

**구현**:
```python
def explore_context(self, target_path: str | None = None):
    # ls로 디렉토리 구조 파악
    dir_listing = self.fs_backend.ls(path)
    
    # LLM으로 인사이트 생성
    insights = self.llm.invoke([...])
    
    return {
        "structure": dir_listing,
        "insights": insights,
    }
```

### FR-FS-02: Pattern-based Search

**도구**:
- `glob`: 패턴 매칭 (`**/*.py`)
- `grep`: 문자열 검색

**구현**:
```python
def pattern_search(self, pattern, query, extension):
    glob_results = self.fs_backend.glob(pattern)
    grep_results = self.fs_backend.grep(query, file_pattern)
    return {"glob_results": glob_results, "grep_results": grep_results}
```

### FR-FS-03: Precise Code Modification

**도구**:
- `edit_file`: 정확한 문자열 치환
- `write_file`: 새 파일 생성

**구현**:
```python
def modify_code(self, file_path, old_string, new_string):
    self.fs_backend.edit_file(
        path=file_path,
        old_content=old_string,
        new_content=new_string,
    )

def create_file(self, file_path, content):
    self.fs_backend.write_file(path=file_path, content=content)
```

### FR-FS-04: Large Output Handling

**토큰 제한 처리**:
```python
def handle_large_output(self, content, output_path=None):
    estimated_tokens = len(content.split())
    
    if estimated_tokens > self.max_token_output:
        # 1. 파일 저장
        self.create_file(output_path, content)
        
        # 2. LLM 요약 생성
        summary = self.llm.invoke([...])
        
        # 3. Human-in-Loop + SubAgent 호출 가능
        return {
            "saved_to": output_path,
            "summary": summary,
            "human_in_loop_required": True,
        }
```

**SubAgent 호출**:
```python
# AdvancedCoordinator에서
async def handle_large_file(self, file_path, human_callback):
    result = self.fs_agent.read_file_safe(file_path)
    
    if result.get("human_in_loop_required"):
        if human_callback and human_callback("Process large file?"):
            # SubAgent로 처리 위임
            await self.process_with_subagent(result)
```

---

## 통합 코디네이터

### AdvancedCoordinator

**구현 파일**: `agents/advanced_coordinator.py`

**역할**:
- Planning: 워크플로우 계획
- FileSystem: 파일 작업 통합
- SubAgent: 전문 에이전트 위임

**통합 워크플로우**:
```python
async def refactor_with_healing(self, code, file_path, human_callback):
    # 1. 파일 시스템 탐색
    context = await self.fs_agent.explore_context()
    
    # 2. 자율 코딩 with Self-Healing
    healing_result = await self.healing_agent.self_heal(code, file_path)
    
    # 3. 문서화 동기화
    if healing_result["success"]:
        doc_result = await self.doc_agent.synchronize_documentation(
            old_code, healing_result["healed_code"]
        )
    
    return {
        "success": healing_result["success"],
        "code": healing_result["healed_code"],
        "tests": healing_result["test_code"],
        "docs": doc_result,
    }
```

---

## 의존성

### 핵심 의존성
- `deepagents` (0.2.5+): **FileSystemBackend 필수 사용**
- `tree-sitter`: AST 파싱
- `tree-sitter-python`: Python 언어 지원
- `networkx`: 그래프 분석
- `pyright`: LSP 서버
- `langgraph`: 워크플로우 관리
- `langchain`: LLM 통합
- `fastapi`: API 서버

### LLM 모델
- `gpt-4o`: 코드 생성, 패치 생성, 문서화
- `gpt-4o-mini`: 빠른 작업 (분석, 탐색, 요약)

---

## 테스트

### 통합 테스트
**파일**: `tests/test_advanced_agents.py`

- FileSystemAgent 테스트
- SelfHealingAgent 테스트
- DocumentationAgent 테스트
- AdvancedCoordinator 통합 테스트

### 데모
**위치**: `examples/`

- `self_healing_demo.py`: FR-AC 데모
- `filesystem_demo.py`: FR-FS 데모
- `documentation_demo.py`: FR-DS 데모
- `complete_workflow_demo.py`: 전체 워크플로우

---

## 라이센스 및 크레딧

- DeepAgents: LangChain
- Tree-sitter: GitHub
- Pyright: Microsoft
- NetworkX: NetworkX Developers
- LangGraph: LangChain
- OpenAI: GPT-4o/GPT-4o-mini

---

**문서 버전**: 0.2.0  
**마지막 업데이트**: 2024-11-20  
**상세 문서**: [docs/INDEX.md](INDEX.md)
