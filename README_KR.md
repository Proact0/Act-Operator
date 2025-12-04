<div align="center">
  <a href="https://www.proact0.org/">
    <picture>
      <source media="(prefers-color-scheme: light)" srcset=".github/images/light-theme.png">
      <source media="(prefers-color-scheme: dark)" srcset=".github/images/dark-theme.png">
      <img alt="Proact0 Logo" src=".github/images/light-theme.png" width="80%">
    </picture>
  </a>
</div>

<div align="center">
  <h2>Act Operator</h2>
</div>

<div align="center">
  <a href="https://www.apache.org/licenses/LICENSE-2.0" target="_blank"><img src="https://img.shields.io/pypi/l/act-operator" alt="PyPI - License"></a>
  <a href="https://pypistats.org/packages/act-operator" target="_blank"><img src="https://img.shields.io/pepy/dt/act-operator?color=deeppink" alt="PyPI - Downloads"></a>
  <a href="https://pypi.org/project/act-operator/#history" target="_blank"><img src="https://img.shields.io/pypi/v/act-operator" alt="Version"></a>
  <a href="https://www.linkedin.com/company/proact0" target="_blank">
    <img src="https://img.shields.io/badge/LinkedIn-Proact0-blue?logo=linkedin" alt="LinkedIn">
  </a>
  <a href="https://www.proact0.org/" target="_blank">
    <img src="https://img.shields.io/badge/Homepage-Proact0.org-brightgreen?logo=internet-explorer" alt="Homepage">
  </a>
</div>

Act Operator는 `cookiecutter`로 `LangChain & LangGraph >= 1.0` 기반의 “Act - AX Template” 블루프린트를 신속히 부트스트랩하기 위한 CLI 도구입니다. 

## 시작하기

```bash
uvx --from act-operator act new
```

대화형 프롬프트가 표시됩니다. `path`가 사용자 지정 디렉터리를 가리키는 경우, Act 이름은 기본적으로 해당 디렉터리 이름으로 설정됩니다.

그러면 다음 모노레포 프로젝트 구조가 셋팅됩니다.

```
your_act_name/
├── casts/
│   ├── __init__.py
│   ├── base_node.py
│   ├── base_graph.py
│   └── your_cast_name/
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

### 그리고 동기화

```bash
uv sync --all-packages
```

### 새로운 캐스트 추가

```bash
uv run act cast
```

새 캐스트를 렌더링하기 전에, `path`가 Act Template 기반 프로젝트인지 검증합니다.

## 기여하기

- 가이드 문서: [CONTRIBUTING.md](CONTRIBUTING.md)

