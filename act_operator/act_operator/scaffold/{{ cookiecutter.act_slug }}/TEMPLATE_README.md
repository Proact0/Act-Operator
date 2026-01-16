{% if cookiecutter.language == 'en' %}# Act Template

This document provides a quick guide to understand and properly use the project generated from this scaffold (template).

- Template name: {{ cookiecutter.act_name }} (slug: {{ cookiecutter.act_slug }}, snake: {{ cookiecutter.act_snake }})
- Workspace configuration: `uv` multi-package (workspace) – `[tool.uv.workspace].members = ["casts/*"]`
- Graph registry: Graph entries are registered via the `graphs` key in `langgraph.json`

## Template Overview

- Provides a modular/hierarchical graph structure based on LangGraph.
- Individual Casts are managed as packages in the `casts/` directory (including `pyproject.toml`).
- Common base classes are imported from `casts/base_node.py` and `casts/base_graph.py`.
- Each Cast consists of `modules/` (agents/conditions/middlewares/models/nodes/prompts/state/tools/utils) and `graph.py`.
- State management uses separate schemas: `InputState` for inputs, `OutputState` for outputs, and `State` for internal processing.

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
│   └── node_tests/
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

- Each Cast uses three distinct state schemas defined in `casts/{{ cookiecutter.cast_snake }}/modules/state.py`:
  - **InputState**: Defines the input schema for graph invocation
  - **OutputState**: Defines the output schema returned by the graph
  - **State**: The main state container (inherits from `MessagesState` for message handling)
- When executing, specify values in the input fields displayed in the left panel of Studio UI, then click Invoke.
- The graph automatically validates input against `InputState` and formats output according to `OutputState`.

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

## Agent Skills

Agent Skills are folders of instructions that enable AI agents to **discover** capabilities, **activate** relevant context, and **execute** tasks. This project includes pre-configured skills in `.claude/skills/`.

> **Tool Compatibility**: The `.claude` folder name is optimized for Claude Code. If you are using other Agent Skills-compatible tools (e.g., Cursor, Gemini CLI), please rename the folder to match your tool's convention.

### Available Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `@architecting-act` | Design architecture | Planning new cast, unclear about structure, need CLAUDE.md |
| `@developing-cast` | Implement code | Building nodes/agents/tools, need LangGraph patterns |
| `@engineering-act` | Project setup | Creating cast package, adding dependencies, syncing env |
| `@testing-cast` | Write tests | Creating pytest tests, mocking strategies, fixtures |

### How to Use

Skills can be invoked in three ways:

1. **Manual invocation**: Type `@skill-name` in your prompt to explicitly load context.
   ```
   @architecting-act Help me design a RAG pipeline
   ```
2. **Programmatic invocation**: The agent automatically calls the skill via tool use.
3. **Automatic discovery**: The agent reads the Skill’s description and loads it when relevant to the conversation.

### Skill Workflow

Skills guide you through their specific domain:
- `architecting-act`: Interactive Q&A → generates `CLAUDE.md`
- `developing-cast`: Reads `CLAUDE.md` (Optional) → implements code
- `engineering-act`: Manages packages and dependencies
- `testing-cast`: Creates pytest test files

### Recommended Development Flow

```
1. @architecting-act  →  Design & create CLAUDE.md
        ↓
2. @engineering-act   →  Create cast, add dependencies
        ↓
3. @developing-cast   →  Implement nodes, agents, graphs
        ↓
4. @testing-cast      →  Write and run tests
```

## Architecture Diagram Kit

The `drawkit.xml` file included in the root directory contains pre-defined shapes for designing Act architecture in [draw.io](https://app.diagrams.net/).

> **Note**: This kit is intended for **human-to-human communication**.
> - For **agent-to-agent communication**, use the Mermaid charts in `CLAUDE.md` generated by the `@architecting-act` skill.
> - For **Developers**, inspect the actual graph execution flow via the LangGraph Development Server (LangSmith).

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset=".github/images/drawkit-dark-en-theme.png">
    <img alt="Drawkit Preview" src=".github/images/drawkit-light-en-theme.png" width="800">
  </picture>
</p>

### How to Import

1. Open [draw.io](https://app.diagrams.net/).
2. Expand the **Scratchpad** panel on the left sidebar.
3. Click the **Edit** (pencil icon) button on the Scratchpad header.
4. Copy the contents of `drawkit.xml` and paste them into the dialog, or use the **Import** button.
5. Click **Save**. The Act components will appear in your Scratchpad for drag-and-drop use.

### Example Act Flowchart

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset=".github/images/sample-flowchart-en-dark-theme.png">
    <img alt="Sample Flowchart" src=".github/images/sample-flowchart-en-light-theme.png" width="1000">
  </picture>
</p>

## Node Implementation

### Creating Nodes

Each Cast includes two types of base nodes for different use cases:

- **BaseNode**: For synchronous operations (file I/O, database queries)
- **AsyncBaseNode**: For asynchronous operations (API calls, concurrent tasks)

### Node Signatures

Choose the appropriate signature based on what your node needs:

```python
# Simple - only needs state
def execute(self, state):
    return {"result": "value"}

# With config - needs thread_id, tags, etc.
def execute(self, state, config):
    thread_id = config.get("configurable", {}).get("thread_id")
    return {"result": "value"}

# With runtime - needs store, stream capabilities
def execute(self, state, runtime):
    runtime.store.put(("memories", "1"), {"key": "value"})
    return {"result": "value"}

# Full - needs everything
def execute(self, state, config, runtime):
    # Access all capabilities
    return {"result": "value"}
```

### Example Implementation

See `casts/{{ cookiecutter.cast_snake }}/modules/nodes.py` for working examples of both `SampleNode` (sync) and `AsyncSampleNode` (async).

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

---

**This template is powered by [Proact0](https://www.proact0.org/)**
{% else %}# Act Template

이 문서는 본 스캐폴드(템플릿)로 생성된 프로젝트를 빠르게 이해하고, 올바르게 사용하는 방법을 안내합니다.

- 템플릿 이름: {{ cookiecutter.act_name }} (slug: {{ cookiecutter.act_slug }}, snake: {{ cookiecutter.act_snake }})
- 워크스페이스 구성: `uv` 멀티 패키지(workspace) – `[tool.uv.workspace].members = ["casts/*"]`
- 그래프 레지스트리: `langgraph.json`의 `graphs` 키를 통해 그래프 엔트리 등록

## 템플릿 개요

- LangGraph 기반의 모듈화/계층화된 그래프 구조를 제공합니다.
- `casts/` 디렉터리에 개별 Cast를 패키지로 관리합니다(`pyproject.toml` 포함).
- 공통 베이스는 `casts/base_node.py`, `casts/base_graph.py`에서 가져옵니다.
- 각 Cast는 `modules/`(에이전트/조건/미들웨어/모델/노드/프롬프트/상태/툴/유틸), `graph.py`로 구성됩니다.
- 상태 관리는 분리된 스키마를 사용합니다: 입력용 `InputState`, 출력용 `OutputState`, 내부 처리용 `State`.

### 디렉터리 구조(요약)

```
{{ cookiecutter.act_slug }}/
├── casts/
│   ├── __init__.py
│   ├── base_node.py
│   ├── base_graph.py
│   └── {{ cookiecutter.cast_snake }}/
│       ├── modules/
│       │   ├── __init__.py
│       │   ├── agents.py (선택)
│       │   ├── conditions.py (선택)
│       │   ├── middlewares.py (선택)
│       │   ├── models.py (선택)
│       │   ├── nodes.py (필수)
│       │   ├── prompts.py (선택)
│       │   ├── state.py (필수)
│       │   ├── tools.py (선택)
│       │   └── utils.py (선택)
│       ├── __init__.py
│       ├── graph.py
│       ├── pyproject.toml
│       └── README.md
├── tests/
│   ├── __init__.py
│   ├── cast_tests/
│   └── node_tests/
├── langgraph.json
├── pyproject.toml
└── README.md
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

- 각 Cast는 `casts/{{ cookiecutter.cast_snake }}/modules/state.py`에서 세 가지 구분된 상태 스키마를 사용합니다:
  - **InputState**: 그래프 호출을 위한 입력 스키마 정의
  - **OutputState**: 그래프가 반환하는 출력 스키마 정의
  - **State**: 메인 상태 컨테이너 (메시지 처리를 위해 `MessagesState`를 상속)
- 실행 시 Studio UI 좌측 패널에 표시되는 입력 필드에 값을 지정한 뒤 Invoke 하십시오.
- 그래프는 자동으로 `InputState`에 대해 입력을 검증하고 `OutputState`에 따라 출력 형식을 지정합니다.

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

## Agent Skills

Agent Skills는 AI 에이전트가 기능을 **발견(Discover)** 하고, 관련 컨텍스트를 **활성화(Activate)** 하며, 작업을 **실행(Execute)** 할 수 있게 해주는 지침 폴더입니다. 이 프로젝트는 `.claude/skills/`에 사전 구성된 스킬을 포함하고 있습니다.

> **도구 호환성**: `.claude` 폴더명은 Claude Code에 최적화되어 있습니다. 다른 Agent Skills 호환 도구(예: Cursor, Gemini CLI)를 사용하는 경우, 해당 도구의 관례에 맞춰 폴더 이름을 변경해 주세요.

### 사용 가능한 스킬

| 스킬 | 목적 | 사용 시점 |
|------|------|----------|
| `@architecting-act` | 아키텍처 설계 | 새 cast 계획, 구조 불명확, CLAUDE.md 필요 시 |
| `@engineering-act` | 프로젝트 설정 | cast 패키지 생성, 의존성 추가, 환경 동기화 |
| `@developing-cast` | 코드 구현 | 노드/에이전트/툴 구현, LangGraph 패턴 필요 시 |
| `@testing-cast` | 테스트 작성 | pytest 테스트 생성, 모킹 전략, 픽스처 |

### 사용 방법

스킬은 세 가지 방식으로 호출할 수 있습니다:

1. **수동 호출**: 프롬프트에 `@skill-name`을 입력하여 명시적으로 컨텍스트를 로드합니다.
   ```
   @architecting-act RAG 파이프라인 설계를 도와줘
   ```
2. **프로그램적 호출**: 에이전트가 도구 사용을 통해 스킬을 자동으로 호출합니다.
3. **자동 발견**: 대화와 관련이 있을 때 에이전트가 스킬의 설명을 읽고 자동으로 로드합니다.

### 스킬 워크플로우

각 스킬은 해당 도메인에 맞게 안내합니다:
- `architecting-act`: 대화형 Q&A → `CLAUDE.md` 생성
- `developing-cast`: `CLAUDE.md` 읽기(선택) → 코드 구현
- `engineering-act`: 패키지 및 의존성 관리
- `testing-cast`: pytest 테스트 파일 생성

### 권장 개발 흐름

```
1. @architecting-act  →  설계 & CLAUDE.md 생성
        ↓
2. @engineering-act   →  (필요 시) cast 생성, 의존성 추가
        ↓
3. @developing-cast   →  노드, 에이전트, 그래프, 기타 모듈 구현
        ↓
4. @testing-cast      →  테스트 작성 및 실행
```

## 아키텍처 다이어그램 키트

루트 디렉터리에 포함된 `drawkit.xml` 파일은 [draw.io](https://app.diagrams.net/)에서 Act 아키텍처를 설계할 때 사용할 수 있는 사전 정의된 쉐이프 모음을 포함하고 있습니다.

> **참고**: 이 키트는 **사람 간의 소통**을 위해 제작되었습니다.
> - **에이전트 간의 소통**: `architecting-act` 스킬로 생성된 `CLAUDE.md`의 Mermaid 차트를 사용하세요.
> - **개발자 확인**: LangGraph 개발 서버(LangSmith)를 통해 실제 그래프 실행 흐름을 확인하세요.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset=".github/images/drawkit-kr-dark-theme.png">
    <img alt="Drawkit 미리보기" src=".github/images/drawkit-kr-light-theme.png" width="800">
  </picture>
</p>

### 가져오는 방법

1. [draw.io](https://app.diagrams.net/)에 접속합니다.
2. 좌측 사이드바에서 **스크래치패드(Scratchpad)** 패널을 펼칩니다.
3. 스크래치패드 헤더의 **수정(Edit)** 버튼(연필 아이콘)을 클릭합니다.
4. `drawkit.xml` 파일의 내용을 복사하여 대화 상자에 붙여넣거나 **가져오기(Import)** 버튼을 사용합니다.
5. **저장(Save)**을 클릭하면 스크래치패드에 Act 컴포넌트가 추가되어 드래그 앤 드롭으로 사용할 수 있습니다.

### 사용 예시

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset=".github/images/sample-flowchart-kr-dark-theme.png">
    <img alt="예시 플로우차트" src=".github/images/sample-flowchart-kr-light-theme.png" width="1000">
  </picture>
</p>

## 노드 구현

### 노드 생성

각 Cast는 서로 다른 사용 사례를 위한 두 가지 유형의 베이스 노드를 포함합니다:

- **BaseNode**: 동기 작업용 (파일 I/O, 데이터베이스 쿼리)
- **AsyncBaseNode**: 비동기 작업용 (API 호출, 동시 작업)

### 노드 시그니처

노드에 필요한 것에 따라 적절한 시그니처를 선택하세요:

```python
# 단순 - state만 필요
def execute(self, state):
    return {"result": "value"}

# config 포함 - thread_id, tags 등이 필요
def execute(self, state, config):
    thread_id = config.get("configurable", {}).get("thread_id")
    return {"result": "value"}

# runtime 포함 - store, stream 기능이 필요
def execute(self, state, runtime):
    runtime.store.put(("memories", "1"), {"key": "value"})
    return {"result": "value"}

# 전체 - 모든 기능이 필요
def execute(self, state, config, runtime):
    # 모든 기능에 접근
    return {"result": "value"}
```

### 구현 예제

`Node` (동기) 및 `AsyncNode` (비동기)의 실제 예제는 `casts/{{ cookiecutter.cast_snake }}/modules/nodes.py`를 참조하세요.

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
이 모노레포 템플릿의 구조와 도구는 Proact0의 [Apache 2.0 라이선스](LICENSE)에 따라 라이선스가 부여됩니다.

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

---

**본 템플릿은 [Proact0](https://www.proact0.org/)에서 관리하고 있습니다.**
{% endif %}