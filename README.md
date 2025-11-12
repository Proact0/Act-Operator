# Act Operator

Act Operator는 `cookiecutter`로 `LangChain & LangGraph >= 1.0` 기반의 “Act - AX Template” 블루프린트를 신속히 부트스트랩하기 위한 Proact0의 CLI입니다. 이 도구는 Act 프로젝트를 생성하는 `act new`와, 기존 블루프린트에 추가 캐스트를 스캐폴딩하는 `act cast` 명령을 제공합니다.

## 주요 기능

- Typer로 구현된 CLI로 `act` 명령 제공
- Act/Cast 이름에 대해 slug/snake/title 변형을 지원하는 `cookiecutter` 렌더링
- 비어 있지 않은 폴더를 덮어쓰지 않도록 하는 안전한 디렉터리 검사
- 기존 Act 프로젝트에 추가 캐스트를 손쉽게 추가하는 내장 명령
- `pytest`로 충분히 검증된 테스트

## 설치

```bash
uv add act-operator
```

Act Operator는 Python 3.12 이상을 요구합니다. 프로젝트에는 `pyproject.toml`이 포함되어 있어 `uv`가 의존성을 재현 가능하게 관리합니다.

## 사용법

### 새 Act 프로젝트 생성

```bash
uv run act new --path ./my-act --act-name "My Act" --cast-name "Main Cast"
```

어떤 옵션이든 생략하면 대화형 프롬프트가 표시됩니다. `--path`가 사용자 지정 디렉터리를 가리키는 경우, Act 이름은 기본적으로 해당 디렉터리 이름으로 설정됩니다.

### 추가 캐스트 추가

```bash
uv run act cast --path ./my-act --cast-name "Sub Cast"
```

새 캐스트를 렌더링하기 전에, 명령은 `--path`가 Act 프로젝트인지 검증합니다(`pyproject.toml`, `langgraph.json`, `casts/base_node.py`, `casts/base_graph.py`의 존재 확인).

### 생성 결과 구조

```
my-act/
├── pyproject.toml
├── README.md
├── langgraph.json
└── casts/
    ├── __init__.py
    ├── base_node.py
    ├── base_graph.py
    └── main-cast/
        ├── modules/
        │   ├── chains.py
        │   ├── conditions.py
        │   ├── models.py
        │   ├── nodes.py
        │   ├── prompts.py
        │   ├── tools.py
        │   └── utils.py
        ├── state.py
        └── graph.py
```

## uv로 개발하기

```bash
uv sync --dev
uv run pytest
uv run act new
uv run act cast
uv build
```

- `uv sync --dev`: 로컬 가상환경에 런타임/테스트 의존성 설치
- `uv run pytest`: 관리되는 환경에서 테스트 스위트 실행
- `uv run act new ...`: 실제 사용자 경험과 동일하게 CLI 동작 검증
- `uv build`: wheel과 sdist 아티팩트 생성

## 테스트

```bash
uv run pytest
```

테스트 스위트는 `act new`와 `act cast`가 기대한 구조를 생성하는지, 디렉터리 검증이 정상 동작하는지, 오류 메시지가 명확한지를 보장합니다.

## 기여하기

- 가이드 문서: [CONTRIBUTING.md](CONTRIBUTING.md) (KR), [CONTRIBUTING_EN.md](CONTRIBUTING_EN.md) (EN)
- 이슈 템플릿:
  - 기능 제안: [.github/ISSUE_TEMPLATE/backlog-kr.md](.github/ISSUE_TEMPLATE/backlog-kr.md), [.github/ISSUE_TEMPLATE/backlog-en.md](.github/ISSUE_TEMPLATE/backlog-en.md)
  - 버그 제보: [.github/ISSUE_TEMPLATE/bug-report-kr.md](.github/ISSUE_TEMPLATE/bug-report-kr.md), [.github/ISSUE_TEMPLATE/bug-report-en.md](.github/ISSUE_TEMPLATE/bug-report-en.md)
- PR 템플릿: [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
