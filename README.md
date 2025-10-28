# Act Operator

Act Operator is Proact0’s CLI for bootstrapping LangGraph-based “Act” blueprints with `cookiecutter`. The tool exposes `act new` to build an Act project and `act cast` to scaffold additional casts inside an existing blueprint.

## Key Features

- Typer-powered CLI exposed as `act`
- `cookiecutter` rendering with slug/snake/title variants for Act and Cast names
- Safe directory checks to avoid overwriting non-empty folders
- Built-in command to add extra casts to an existing Act project
- Fully tested with `pytest`

## Installation

```bash
uv add act-operator
```

Act Operator requires Python 3.12 or newer. The project ships with `pyproject.toml` so `uv` manages dependencies reproducibly.

## Usage

### Create a new Act project

```bash
uv run act new --path ./my-act --act-name "My Act" --cast-name "Main Cast"
```

You can omit any option to trigger interactive prompts. When `--path` points to a custom directory, the Act name defaults to that directory name.

### Add an additional cast

```bash
uv run act cast --path ./my-act --cast-name "Sub Cast"
```

The command validates that `--path` is an Act project (presence of `pyproject.toml`, `langgraph.json`, `casts/base_node.py`, and `casts/base_graph.py`) before rendering the new cast.

### Resulting layout

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

## Development with uv

```bash
uv sync --dev
uv run pytest
uv run act new
uv run act cast
uv build
```

- `uv sync --dev` installs runtime and test dependencies into a local virtualenv.
- `uv run pytest` executes the suite against the managed environment.
- `uv run act new ...` exercises the CLI exactly as users would experience it.
- `uv build` produces the wheel and sdist artifacts.

## Testing

```bash
uv run pytest
```

The suite ensures `act new` and `act cast` render the expected structure, validate directories, and surface clear error messages.

## Contributing

- Read the guides: [CONTRIBUTING.md](CONTRIBUTING.md) (KR), [CONTRIBUTING_EN.md](CONTRIBUTING_EN.md) (EN)
- Issue templates:
  - Feature Request: [.github/ISSUE_TEMPLATE/backlog-kr.md](.github/ISSUE_TEMPLATE/backlog-kr.md), [.github/ISSUE_TEMPLATE/backlog-en.md](.github/ISSUE_TEMPLATE/backlog-en.md)
  - Bug Report: [.github/ISSUE_TEMPLATE/bug-report-kr.md](.github/ISSUE_TEMPLATE/bug-report-kr.md), [.github/ISSUE_TEMPLATE/bug-report-en.md](.github/ISSUE_TEMPLATE/bug-report-en.md)
- PR template: [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
