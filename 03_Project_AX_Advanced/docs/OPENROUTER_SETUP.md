# OpenRouter Setup Guide

**Version**: 0.2.0  
**Last Updated**: 2024-11-21

## Overview

이 프로젝트는 **OpenRouter API**를 사용하여 여러 LLM 제공자(OpenAI, Anthropic, Google, etc.)의 모델을 통합적으로 사용합니다.

---

## 🔑 API Key 발급

### 1. OpenRouter 계정 생성

1. [OpenRouter](https://openrouter.ai/) 접속
2. 계정 생성 또는 로그인
3. [API Keys 페이지](https://openrouter.ai/keys) 이동
4. **Create Key** 클릭하여 API 키 발급

### 2. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집
OPENROUTER_API_KEY=your_actual_api_key_here
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
```

---

## 🎯 사용 가능한 모델

### Chat Models (대화형 LLM)

| Provider | Model | 용도 | 비용 |
|----------|-------|------|------|
| OpenAI | `openai/gpt-4.1` | 고급 작업 (코디네이터, 문서화) | $$$ |
| OpenAI | `openai/gpt-4.1-mini` | 일반 작업 (분석, 탐색) | $ |
| OpenAI | `openai/gpt-5` | 최신 모델 | $$$$ |
| OpenAI | `openai/gpt-5-mini` | 최신 경량 모델 | $$ |
| Anthropic | `anthropic/claude-sonnet-4.5` | 복잡한 추론 | $$$ |
| Anthropic | `anthropic/claude-haiku-4.5` | 빠른 응답 | $ |
| Google | `google/gemini-2.5-flash-preview` | 빠른 처리 | $ |
| Google | `google/gemini-pro-2.5` | 고급 처리 | $$ |

### Embedding Models (임베딩)

| Provider | Model | 차원 | 용도 |
|----------|-------|------|------|
| OpenAI | `openai/text-embedding-3-small` | 1536 | 일반 임베딩 |
| OpenAI | `openai/text-embedding-3-large` | 3072 | 고품질 임베딩 |
| Qwen | `qwen/qwen3-embedding-0.6b` | 768 | 경량 임베딩 |

---

## 📦 프로젝트 적용

### 기본 사용법

```python
from agentic_coding_assistant.utils import create_openrouter_llm

# LLM 생성
llm = create_openrouter_llm(
    model="openai/gpt-4.1-mini",
    temperature=0.3,
)

# 사용
response = llm.invoke("Hello, world!")
print(response.content)
```

### Agent에서 사용

모든 Agent는 자동으로 OpenRouter를 사용합니다:

```python
from agentic_coding_assistant.agents import (
    ImpactAnalysisCoordinator,
    AdvancedCoordinator,
    FileSystemAgent,
    SelfHealingAgent,
    DocumentationAgent,
)

# 기본 모델 사용 (openai/gpt-4.1-mini)
coordinator = ImpactAnalysisCoordinator()

# 커스텀 모델 사용
coordinator = AdvancedCoordinator(
    project_root=".",
    model="anthropic/claude-sonnet-4.5",  # Anthropic 모델 사용
)

# FileSystemAgent
fs_agent = FileSystemAgent(
    work_dir=".",
    model="google/gemini-2.5-flash-preview",  # Google 모델 사용
)
```

---

## 🔧 모델 선택 가이드

### 작업별 권장 모델

#### 1. Impact Analysis (영향도 분석)
```python
# SPEED/PRECISION 모드 - 빠른 분석
coordinator = ImpactAnalysisCoordinator(
    model="openai/gpt-4.1-mini",  # 경제적
)
```

#### 2. Self-Healing (자율 코딩)
```python
# 코드 생성 및 수정 - 정확성 중요
healing_agent = SelfHealingAgent(
    model="openai/gpt-4.1",  # 고품질
)
```

#### 3. Documentation (문서화)
```python
# 문서 생성 - 자연스러운 언어
doc_agent = DocumentationAgent(
    model="anthropic/claude-sonnet-4.5",  # 뛰어난 글쓰기
)
```

#### 4. FileSystem Exploration (파일 탐색)
```python
# 빠른 탐색 및 검색
fs_agent = FileSystemAgent(
    work_dir=".",
    model="google/gemini-2.5-flash-preview",  # 빠름
)
```

---

## 💰 비용 최적화

### 전략 1: 작업별 모델 차별화

```python
# 간단한 작업: mini 모델
simple_llm = create_openrouter_llm(model="openai/gpt-4.1-mini")

# 복잡한 작업: 고급 모델
advanced_llm = create_openrouter_llm(model="openai/gpt-4.1")
```

### 전략 2: Temperature 조정

```python
# 결정론적 작업 (코드 생성)
llm = create_openrouter_llm(
    model="openai/gpt-4.1-mini",
    temperature=0,  # 일관된 출력
)

# 창의적 작업 (문서 작성)
llm = create_openrouter_llm(
    model="anthropic/claude-sonnet-4.5",
    temperature=0.7,  # 다양한 출력
)
```

### 전략 3: Max Tokens 제한

```python
llm = create_openrouter_llm(
    model="openai/gpt-4.1",
    max_tokens=1000,  # 출력 길이 제한
)
```

---

## 🔍 모델 정보 확인

### 사용 가능한 모델 목록

```python
from agentic_coding_assistant.utils import get_available_model_types

models = get_available_model_types()

print("Chat Models:")
for model in models["chat"]:
    print(f"  - {model}")

print("\nEmbedding Models:")
for model in models["embedding"]:
    print(f"  - {model}")
```

### API 엔드포인트 확인

```bash
# FastAPI 서버 실행
uvicorn agentic_coding_assistant.api:app --reload

# 모델 정보 확인
curl http://localhost:8000/modes
```

---

## 🚨 Troubleshooting

### 1. API Key 오류

**문제**: `RuntimeError: OPENROUTER_API_KEY가 필요합니다.`

**해결**:
```bash
# .env 파일 확인
cat .env

# 환경 변수 설정 확인
echo $OPENROUTER_API_KEY

# 환경 변수 직접 설정
export OPENROUTER_API_KEY=your_key_here
```

### 2. 모델 사용 불가

**문제**: 특정 모델이 작동하지 않음

**해결**:
```python
# 다른 모델로 전환
llm = create_openrouter_llm(
    model="openai/gpt-4.1-mini",  # 안정적인 기본 모델
)
```

### 3. Rate Limit 초과

**문제**: `429 Too Many Requests`

**해결**:
- OpenRouter 대시보드에서 사용량 확인
- 요청 간격 조정
- 더 높은 tier로 업그레이드

---

## 📊 모니터링

### OpenRouter Dashboard

1. [OpenRouter Dashboard](https://openrouter.ai/activity) 접속
2. API 사용량 확인
3. 비용 모니터링
4. 모델별 성능 확인

### 로컬 로깅

```python
import logging

logging.basicConfig(level=logging.INFO)

# LLM 호출 시 자동 로깅
llm = create_openrouter_llm(
    model="openai/gpt-4.1-mini",
    verbose=True,  # 상세 로그 출력
)
```

---

## 🔗 참고 자료

- [OpenRouter 공식 문서](https://openrouter.ai/docs)
- [OpenRouter 모델 목록](https://openrouter.ai/models)
- [OpenRouter API 레퍼런스](https://openrouter.ai/docs/api-reference)
- [가격 정보](https://openrouter.ai/models)

---

## 🆕 업데이트 내역

### v0.2.0 (2024-11-21)
- ✅ OpenRouter API 통합
- ✅ 모든 Agent에 OpenRouter 적용
- ✅ 다중 모델 제공자 지원
- ✅ 비용 최적화 가이드 추가

---

**Last Updated**: 2024-11-21  
**Version**: 0.2.0  
**Status**: Production Ready ✅
