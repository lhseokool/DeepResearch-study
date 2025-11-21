# FileSystem Agent Guide

**Version**: 0.2.0  
**Last Updated**: 2024-11-20

## Overview

FileSystemAgent는 `create_deep_agent`를 사용하여 DeepAgent 패턴을 완벽하게 구현한 에이전트입니다.

---

## Architecture

### Core Implementation

```python
from deepagents import create_deep_agent

FILESYSTEM_AGENT_PROMPT = """You are an expert filesystem agent..."""

class FileSystemAgent:
    def __init__(
        self,
        work_dir: str | Path,
        model: str = "gpt-4o-mini",
        temperature: float = 0,
        max_token_output: int = 4000,
        additional_tools: list[Callable] | None = None,
    ):
        self.work_dir = Path(work_dir).resolve()
        self.max_token_output = max_token_output
        
        # Create deep agent with automatic FileSystemBackend
        self.agent = create_deep_agent(
            system_prompt=FILESYSTEM_AGENT_PROMPT,
            model=model,
            tools=additional_tools or [],
            # FileSystemBackend is automatically included
        )
```

### Key Features

1. **DeepAgent Patterns**: Planning, FileSystem, SubAgent 자동 적용
2. **FileSystemBackend**: ls, read_file, glob, grep, edit_file, write_file 자동 포함
3. **Synchronous API**: 모든 메서드는 동기(sync) 방식
4. **LLM Integration**: GPT-4o-mini 사용 (커스터마이징 가능)

---

## Capabilities

### FR-FS-01: Contextual Exploration

프로젝트 구조 파악 및 인사이트 제공

```python
agent = FileSystemAgent(work_dir=Path.cwd())

context = agent.explore_context("src")

print(context["path"])        # 탐색 경로
print(context["insights"])    # LLM 생성 인사이트
```

**기능**:
- 디렉토리 구조 분석 (ls 도구 사용)
- 프로젝트 타입 식별
- 주요 설정 파일 찾기
- 소스 코드/테스트/문서 구조 파악

---

### FR-FS-02: Pattern-based Search

glob/grep을 사용한 파일 및 코드 검색

```python
# 파일 패턴 검색
results = agent.pattern_search(pattern="**/*.py")

# 문자열 검색
results = agent.pattern_search(
    query="create_deep_agent",
    extension="py",
)

print(results["search_criteria"])  # 검색 조건
print(results["results"])           # 검색 결과 및 분석
```

**기능**:
- glob 패턴 매칭
- grep 문자열 검색
- 확장자 필터링
- LLM 기반 결과 분석 및 요약

---

### FR-FS-03: Precise Code Modification

정확한 코드 수정 및 파일 생성

```python
# 코드 수정
result = agent.modify_code(
    file_path="module.py",
    old_string="old_function_name",
    new_string="new_function_name",
)

# 새 파일 생성
result = agent.create_file(
    file_path="new_module.py",
    content="def hello(): pass",
)

print(result["success"])   # True/False
print(result["message"])   # 결과 메시지
```

**기능**:
- edit_file로 정확한 문자열 치환
- write_file로 새 파일 생성
- 자동 에러 처리
- 작업 결과 리포트

---

### FR-FS-04: Large Output Handling

대용량 파일 자동 처리

```python
# 대용량 콘텐츠 처리
result = agent.handle_large_output(
    content=large_content,
    output_path="output.txt",
)

if result["large_output"]:
    print(f"Saved to: {result['saved_to']}")
    print(f"Summary: {result['summary']}")
else:
    print(result["content"])

# 안전한 파일 읽기 (자동 대용량 처리)
result = agent.read_file_safe("large_file.py")
```

**기능**:
- 토큰 제한 자동 감지 (기본: 4000 tokens)
- 파일 시스템에 자동 저장
- LLM 기반 요약 생성
- Human-in-the-Loop 지원

---

## Integration with AdvancedCoordinator

```python
from agentic_coding_assistant.agents import AdvancedCoordinator
from pathlib import Path

coordinator = AdvancedCoordinator(project_root=Path.cwd())

# FileSystem 작업 (sync)
context = coordinator.explore_project()
results = coordinator.search_code(pattern="**/*.py")
result = coordinator.modify_code_precise(
    file_path="module.py",
    old_string="old",
    new_string="new",
)

# Self-Healing/Documentation 작업 (async)
result = await coordinator.refactor_with_healing(...)
result = await coordinator.sync_documentation(...)
```

**통합 워크플로우**:
1. FileSystemAgent로 프로젝트 탐색
2. SelfHealingAgent로 자율 코딩
3. DocumentationAgent로 문서 동기화

---

## System Prompt

FileSystemAgent는 다음 시스템 프롬프트를 사용합니다:

```
You are an expert filesystem agent specialized in code exploration and manipulation.

Your capabilities:
1. Contextual Exploration (FR-FS-01): Understand project structure and provide insights
2. Pattern Search (FR-FS-02): Find files and code patterns efficiently
3. Precise Modification (FR-FS-03): Edit code with exact string replacement
4. Large Output Handling (FR-FS-04): Summarize large files and save to disk

You have access to these filesystem tools (automatically provided by FileSystemBackend):
- ls: List directory contents
- read_file: Read file contents
- glob: Pattern-based file search (e.g., "**/*.py")
- grep: Search string in files
- edit_file: Precise string replacement in files
- write_file: Create new files

When exploring:
1. Start with ls to understand structure
2. Use glob or grep to find relevant files
3. Use read_file to examine contents
4. Provide clear, actionable insights

When modifying:
1. Always verify file exists first
2. Use exact string matching for edit_file
3. Create backups for critical changes
4. Report success/failure clearly

For large outputs (>4000 tokens):
1. Save to file using write_file
2. Provide concise summary
3. Include file path in response
```

---

## Configuration Options

### Basic Configuration

```python
agent = FileSystemAgent(
    work_dir=Path.cwd(),              # 작업 디렉토리
    model="gpt-4o-mini",              # LLM 모델
    temperature=0,                     # LLM temperature
    max_token_output=4000,            # 대용량 파일 임계값
)
```

### Advanced Configuration

```python
# 커스텀 도구 추가
def custom_tool(arg: str):
    """Custom filesystem tool."""
    return f"Result: {arg}"

agent = FileSystemAgent(
    work_dir=Path.cwd(),
    model="gpt-4o",                   # 더 강력한 모델 사용
    max_token_output=8000,            # 더 큰 파일 허용
    additional_tools=[custom_tool],   # 커스텀 도구 추가
)
```

---

## API Reference

### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `explore_context()` | `target_path: str \| None` | `dict[str, Any]` | 프로젝트 구조 탐색 |
| `pattern_search()` | `pattern, query, extension` | `dict[str, Any]` | 파일/코드 검색 |
| `modify_code()` | `file_path, old_string, new_string` | `dict[str, Any]` | 코드 수정 |
| `create_file()` | `file_path, content` | `dict[str, Any]` | 파일 생성 |
| `handle_large_output()` | `content, output_path` | `dict[str, Any]` | 대용량 처리 |
| `read_file_safe()` | `file_path` | `dict[str, Any]` | 안전한 파일 읽기 |

### Return Format

모든 메서드는 다음 형식의 딕셔너리를 반환합니다:

```python
{
    "success": bool,              # 성공 여부 (해당시)
    "agent_used": "create_deep_agent",
    # ... 메서드별 추가 필드
}
```

---

## Examples

### Complete Workflow

```python
from pathlib import Path
from agentic_coding_assistant.agents import FileSystemAgent

# 1. 초기화
agent = FileSystemAgent(work_dir=Path.cwd())

# 2. 프로젝트 탐색
context = agent.explore_context("src")
print(f"Insights: {context['insights']}")

# 3. 파일 검색
search_results = agent.pattern_search(
    pattern="**/*.py",
    query="DeepAgent",
)
print(f"Results: {search_results['results']}")

# 4. 코드 수정
modification = agent.modify_code(
    file_path="module.py",
    old_string="def old():",
    new_string="def new():",
)
print(f"Modified: {modification['success']}")

# 5. 새 파일 생성
creation = agent.create_file(
    file_path="test.py",
    content="# Test file\n",
)
print(f"Created: {creation['success']}")
```

### Demo Script

전체 기능 데모:

```bash
python examples/filesystem_demo.py
```

---

## Technical Details

### DeepAgent Patterns Applied

1. **Planning**: create_deep_agent가 자동으로 작업 분해
2. **FileSystem**: FileSystemBackend 도구 자동 포함
3. **SubAgent**: 복잡한 작업 시 서브 에이전트 생성 가능

### FileSystemBackend Tools

자동으로 포함되는 도구들:

- **ls**: 디렉토리 목록
- **read_file**: 파일 읽기
- **glob**: 패턴 매칭
- **grep**: 문자열 검색
- **edit_file**: 파일 수정
- **write_file**: 파일 생성

### Synchronous Design

create_deep_agent는 `.invoke()` 메서드를 사용하므로 모든 작업이 동기 방식입니다:

```python
# Synchronous call
result = self.agent.invoke({
    "messages": [{"role": "user", "content": prompt}]
})
```

내부적으로는 async 작업을 처리하지만, 외부 API는 sync로 제공됩니다.

---

## Performance Considerations

### Token Limits

- 기본 임계값: 4000 tokens
- 초과 시 자동 저장 및 요약
- `max_token_output` 파라미터로 조정 가능

### LLM Selection

- **gpt-4o-mini**: 빠르고 경제적 (기본값)
- **gpt-4o**: 더 높은 품질, 복잡한 작업용

### Best Practices

1. 작업 디렉토리 명확히 설정
2. 패턴 검색 시 구체적인 조건 사용
3. 대용량 파일은 `read_file_safe()` 사용
4. 중요한 수정 전 백업 권장

---

## Troubleshooting

### Common Issues

**Q: "FileSystemBackend tools not available"**
```python
# create_deep_agent가 자동으로 포함하므로 수동 설정 불필요
# additional_tools에 커스텀 도구만 추가
```

**Q: "Large file not summarized"**
```python
# max_token_output 값 조정
agent = FileSystemAgent(max_token_output=8000)
```

**Q: "Modification failed"**
```python
# old_string이 파일에 정확히 존재하는지 확인
# 공백, 들여쓰기 포함 완전 일치 필요
```

---

## Related Documentation

- **Advanced Features**: [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md)
- **Implementation Details**: [IMPLEMENTATION.md](IMPLEMENTATION.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **DeepAgents Docs**: https://docs.langchain.com/oss/python/deepagents/overview

---

## Version History

- **0.2.0** (2024-11-20): create_deep_agent 적용, sync API로 변경
- **0.1.0** (2024-11-15): 초기 구현

---

**Last Updated**: 2024-11-20  
**Version**: 0.2.0  
**Status**: Production Ready ✅
