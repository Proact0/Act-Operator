{% if cookiecutter.language == 'en' %}
# Act Template

This document provides a quick guide to understand and properly use the project generated from this scaffold (template).

- Template name: {{ cookiecutter.act_name }} (slug: {{ cookiecutter.act_slug }}, snake: {{ cookiecutter.act_snake }})
- Workspace configuration: `uv` multi-package (workspace) – `[tool.uv.workspace].members = ["casts/*"]`
- Graph registry: Graph entries are registered via the `graphs` key in `langgraph.json`

## Template Overview

- Provides a modular/hierarchical graph structure based on LangGraph.
- Individual Casts are managed as packages in the `casts/` directory (including `pyproject.toml`).
- Common base classes are imported from `casts/base_node.py` and `casts/base_graph.py`.
- Each Cast consists of `modules/` (agents/conditions/models/nodes/prompts/state/tools/utils) and `graph.py`.

### Directory Core Structure (Summary)

```
{{ cookiecutter.act_slug }}/             #Root
├── casts/
│   ├── __init__.py
│   ├── base_node.py
│   ├── base_graph.py
│   └── {{ cookiecutter.cast_snake }}/
│       ├── modules/
│       │   ├── __init__.py
│       │   ├── agents.py (optional)
│       │   ├── conditions.py (optional)
│       │   ├── middlewares.py (optional)
│       │   ├── models.py (optional)
│       │   ├── nodes.py (required)
│       │   ├── prompts.py (optional)
│       │   ├── state.py (required)
│       │   ├── tools.py (optional)
│       │   └── utils.py (optional)
│       ├── __init__.py
│       ├── graph.py
│       ├── pyproject.toml
│       └── README.md
├── tests/
│   ├── __init__.py
│   ├── cast_tests/
│   ├── node_tests/
│   ├── node_tests/
├── langgraph.json
├── pyproject.toml
└── README.md
```

## Installation and Setup

### System Requirements

- Python 3.11 or higher
- `uv` (dependency/execution/build)
- `ruff` (code quality/formatting)

### Installing uv (if not installed)

- Official guide: https://docs.astral.sh/uv/getting-started/installation/

```bash
pip install uv
```

### Installing Dependencies

- Install entire workspace (all Cast packages)

```bash
uv sync --all-packages
```

- Install specific Cast package (using workspace member name)

```bash
# Example: Install only {{ cookiecutter.cast_snake }}
uv sync --package {{ cookiecutter.cast_snake }}
```

> Member names match the `[project].name` in each `pyproject.toml` under `casts/<cast_name>`.

## Graph Registry (langgraph.json)

Declare graphs to expose in `langgraph.json`. A basic example is as follows:

```json
{
  "dependencies": ["."],
  "graphs": {
    "main": "./casts/graph.py:main_graph",
    "{{ cookiecutter.cast_snake }}": "./casts/{{ cookiecutter.cast_snake }}/graph.py:{{ cookiecutter.cast_snake }}_graph"
  },
  "env": ".env"
}
```

- If you only use specific Casts, you can keep only those Cast keys.
- The `.env` path points to the environment variable file (modify if needed).

## Running Development Server (LangGraph CLI)

Run an in-memory server for development/debugging.

```bash
uv run langgraph dev
```

- For browsers other than Chrome (tunnel mode):

```bash
uv run langgraph dev --tunnel
```

Server URLs after startup

- API: http://127.0.0.1:2024
- Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- API Documentation: http://127.0.0.1:2024/docs

> Note: This server is an in-memory server for development/testing. For production, LangGraph Cloud is recommended.

To stop: Press `Ctrl + C` (Windows) or `Cmd + C` (macOS) in the terminal

## Input/State Management

- Input schemas and state for each Cast are defined/managed in `casts/{{ cookiecutter.cast_snake }}/modules/state.py`.
- When executing, specify values in the input fields displayed in the left panel of Studio UI, then click Invoke.

## Adding a New Cast

To add a new graph/feature as a separate Cast, use the `act cast` command. Act Operator is already included in the `dev` dependency group.

```bash
# Ensure dev dependencies are installed
uv sync --all-packages

# Add a new Cast (interactive mode)
uv run act cast

# Or specify cast name directly
uv run act cast my-new-cast

# Or with full options
uv run act cast --path . --cast-name "New Cast Name"
```

**What happens:**
- Validates Act project structure
- Creates complete Cast directory with all required files
- Updates `langgraph.json` automatically
- Configures Cast as workspace member

**After creating:**
```bash
# Install all packages (includes new Cast)
uv sync --all-packages
```

## Testing and Quality Management

### Testing (pytest)

```bash
uv run pytest -q
```

### Quality Management (ruff)

```bash
uv run ruff check . --fix
uv run ruff format .
```

### pre-commit

This template includes pre-commit configuration.

- `ruff`: Code quality checks/formatting/import organization
- `uv-lock`: Dependency lock file synchronization

> If checks fail, the commit will be blocked. All hooks must pass for the commit to complete.

## License
The structure and tooling of this monorepo template are licensed under the Proact0's [Apache 2.0 License](LICENSE).

## Frequently Asked Questions (FAQ)

- Q. Can I minimize dependency installation when developing only specific Casts?
  - A. Use `uv sync --package <package_name>` to install only the required Casts.
- Q. I added a new graph key, but it doesn't appear in Studio UI.
  - A. Check that it's registered with the correct path (`path:callable`) in the `graphs` section of `langgraph.json`, and restart the server.
- Q. Where can I check the format/lint standards?
  - A. Check the `[tool.ruff]` settings in `pyproject.toml`.

## References

- LangGraph: https://docs.langchain.com/oss/python/langgraph/overview
- Claude Agent Skills: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- uv: https://docs.astral.sh/uv/

{% else %}
# Act Template

이 문서는 본 스캐폴드(템플릿)로 생성된 프로젝트를 빠르게 이해하고, 올바르게 사용하는 방법을 안내합니다.

- 템플릿 이름: {{ cookiecutter.act_name }} (slug: {{ cookiecutter.act_slug }}, snake: {{ cookiecutter.act_snake }})
- 워크스페이스 구성: `uv` 멀티 패키지(workspace) – `[tool.uv.workspace].members = ["casts/*"]`
- 그래프 레지스트리: `langgraph.json`의 `graphs` 키를 통해 그래프 엔트리 등록

## 템플릿 개요

- LangGraph 기반의 모듈화/계층화된 그래프 구조를 제공합니다.
- `casts/` 디렉터리에 개별 Cast를 패키지로 관리합니다(`pyproject.toml` 포함).
- 공통 베이스는 `casts/base_node.py`, `casts/base_graph.py`에서 가져옵니다.
- 각 Cast는 `modules/`(에이전트/조건/모델/노드/프롬프트/상태/툴/유틸), `graph.py`로 구성됩니다.

### 디렉터리 구조(요약)

```
{{ cookiecutter.act_slug }}/
├── pyproject.toml
├── README.md
├── langgraph.json
└── casts/
    ├── __init__.py
    ├── base_node.py
    ├── base_graph.py
    └── {{ cookiecutter.cast_snake }}/
        ├── modules/
        │   ├── agents.py (선택)
        │   ├── conditions.py (선택)
        │   ├── models.py (선택)
        │   ├── nodes.py (필수)
        │   ├── prompts.py (선택)
        │   ├── state.py (필수)
        │   ├── tools.py (선택)
        │   └── utils.py (선택)
        └── graph.py
```

## 설치 및 준비

### 시스템 요구사항

- Python 3.11 이상
- `uv` (의존성/실행/빌드)
- `ruff` (코드 품질/포맷)

### uv 설치(미설치 시)

- 공식 가이드: https://docs.astral.sh/uv/getting-started/installation/

```bash
pip install uv
```

### 의존성 설치

- 전체 워크스페이스(모든 Cast 패키지) + 개발 의존성 설치

```bash
uv sync --all-packages
```

- 특정 Cast 패키지 설치(워크스페이스 멤버명 사용)

```bash
# 예: {{ cookiecutter.cast_snake }} 만 설치
uv sync --package {{ cookiecutter.cast_snake }}
```

> 멤버명은 `casts/<cast_name>` 하위의 각 `pyproject.toml`의 `[project].name`과 일치합니다.

## 그래프 레지스트리(langgraph.json)

`langgraph.json`에서 노출할 그래프를 선언합니다. 기본 예시는 다음과 같습니다.

```json
{
  "dependencies": ["."],
  "graphs": {
    "main": "./casts/graph.py:main_graph",
    "{{ cookiecutter.cast_snake }}": "./casts/{{ cookiecutter.cast_snake }}/graph.py:{{ cookiecutter.cast_snake }}_graph"
  },
  "env": ".env"
}
```

- 특정 Cast만 사용한다면 해당 Cast 키만 남겨도 됩니다.
- `.env` 경로는 환경변수 파일을 가리킵니다(필요 시 수정).

## 개발 서버 실행(LangGraph CLI)

개발/디버깅을 위해 인메모리 서버를 실행합니다.

```bash
uv run langgraph dev
```

- 크롬 이외 브라우저 사용 시(터널 모드):

```bash
uv run langgraph dev --tunnel
```

서버 실행 후 접속 URL

- API: http://127.0.0.1:2024
- Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- API 문서: http://127.0.0.1:2024/docs

> 참고: 본 서버는 개발/테스트용 인메모리 서버입니다. 프로덕션은 LangGraph Cloud 사용을 권장합니다.

종료 방법: 터미널에서 `Ctrl + C`(Windows), `Cmd + C`(macOS)

## 입력/상태 관리

- 각 Cast의 입력 스키마 및 상태는 `casts/{{ cookiecutter.cast_snake }}/modules/state.py`에서 정의/관리됩니다.
- 실행 시 Studio UI 좌측 패널에 표시되는 입력 필드에 값을 지정한 뒤 Invoke 하십시오.

## 새 Cast 추가

새로운 그래프/기능을 별도 Cast로 추가하려면 `act cast` 명령을 사용합니다. Act Operator는 이미 `dev` 의존성 그룹에 포함되어 있습니다.

```bash
# 의존성이 설치되어 있는지 확인
uv sync --all-packages

# 새 Cast 추가 (대화형 모드)
uv run act cast

# 또는 Cast 이름을 직접 지정
uv run act cast my-new-cast

# 또는 전체 옵션과 함께
uv run act cast --path . --cast-name "새 Cast 이름"
```

**수행 내용:**
- Act 프로젝트 구조 검증
- 필수 파일이 포함된 완전한 Cast 디렉터리 생성
- `langgraph.json` 자동 업데이트
- Cast를 workspace member로 구성

**Cast 생성 후:**
```bash
# 모든 패키지 설치 (새 Cast 포함)
uv sync --all-packages
```

## 테스트 및 품질 관리

### 테스트(pytest)

```bash
uv run pytest -q
```

### 품질 관리(ruff)

```bash
uv run ruff check . --fix
uv run ruff format .
```

### pre-commit

본 템플릿은 pre-commit 구성을 포함합니다.

- `ruff`: 코드 품질 점검/포맷/임포트 정리
- `uv-lock`: 의존성 락 파일 동기화

> 검사 실패 시 커밋이 차단됩니다. 모든 훅을 통과해야 커밋이 완료됩니다.

## 라이선스
이 모노레포 템플릿의 구조와 도구는 Proact0의 [Apache 2.0 라이선스](LICENCE)에 따라 라이선스가 부여됩니다.

## 자주 하는 질문(FAQ)

- Q. 특정 Cast만 개발하려는데 의존성 설치를 최소화할 수 있나요?
  - A. `uv sync --package <패키지명>`으로 필요한 Cast만 설치하세요.
- Q. 새 그래프 키를 추가했는데 Studio UI에 보이지 않습니다.
  - A. `langgraph.json`의 `graphs`에 올바른 경로(`path:callable`)로 등록되어 있는지 확인하고, 서버를 재시작하세요.
- Q. 포맷/린트 기준은 어디서 확인하나요?
  - A. `pyproject.toml`의 `[tool.ruff]` 설정을 확인하세요.

## 참고

- LangGraph: https://docs.langchain.com/oss/python/langgraph/overview
- Claude Agent Skills: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- uv: https://docs.astral.sh/uv/
{% endif %}
