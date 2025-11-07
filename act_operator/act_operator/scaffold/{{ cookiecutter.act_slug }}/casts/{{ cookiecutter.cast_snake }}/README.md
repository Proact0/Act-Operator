{% if cookiecutter.language == 'en' %}
# {{ cookiecutter.cast_name }} Module

## Overview
This module defines the {{ cookiecutter.cast_name }} LangGraph graph responsible for running and extracting insights.

## Structure
```
{{ cookiecutter.cast_snake }}/
├── modules/
│   ├── nodes.py       # Graph nodes (required)
│   ├── state.py       # State definition (required)
│   ├── tools.py       # Tools (optional)
│   ├── chains.py      # Chains (optional)
│   ├── prompts.py     # Prompts (optional)
│   ├── models.py      # Models (optional)
│   └── utils.py       # Utilities (optional)
├── pyproject.toml     # Package metadata
├── README.md          # This document
└── graph.py           # Graph definition
```

## Usage
```python
from casts.{{ cookiecutter.cast_snake }}.graph import {{ cookiecutter.cast_snake }}_graph

initial_state = {
    "query": "Hello, Act"
}

result = {{ cookiecutter.cast_snake }}_graph().invoke(initial_state)
```

## Extending
1. Add new node classes in `modules/nodes.py`
2. Define chains/tools/prompts/models if needed
3. Wire nodes into the graph in `graph.py`

{% else %}
# {{ cookiecutter.cast_name }} 모듈 ({{ cookiecutter.cast_name }} Module)

## 개요
이 모듈은 {{ cookiecutter.act_name }} 의 {{ cookiecutter.cast_name }} 진행 및 통찰 추출을 담당하는 LangGraph Graph입니다.

## 구조
```
{{ cookiecutter.cast_snake }}/
├── modules/
│   ├── nodes.py       # Graph 노드 클래스들 정의 (필수)
│   ├── state.py       # 상태 정의 (필수)
│   ├── tools.py       # 도구 함수 (선택)
│   ├── chains.py      # LangChain 체인 정의 (선택)
│   ├── prompts.py     # 프롬프트 템플릿 (선택)
│   ├── models.py      # LLM/모델 설정 (선택)
│   └── utils.py       # 유틸리티 함수 (선택)
├── pyproject.toml     # 패키지 메타데이터
├── README.md          # 본 문서
└── graph.py           # Graph 정의
```

## 사용 방법
```python
from casts.{{ cookiecutter.cast_snake }}.graph import {{ cookiecutter.cast_snake }}_graph

initial_state = {
    "query": "Hello, Act"
}

result = {{ cookiecutter.cast_snake }}_graph().invoke(initial_state)
```

## 확장 방법
1. `modules/nodes.py`에 새 노드 클래스를 추가
2. 필요시 chains/tools/prompts/models 정의
3. `graph.py`에서 Graph에 연결
{% endif %}
