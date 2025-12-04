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

Act Operator is Proact0’s CLI for bootstrapping `LangChain & LangGraph >= 1.0 based` “Act - AX Template” blueprints with `cookiecutter`. The tool exposes `act new` to build an Act project and `act cast` to scaffold additional casts inside an existing blueprint.

## Key Features

- Typer-powered CLI exposed as `act`
- `cookiecutter` rendering with slug/snake/title variants for Act and Cast names
- Safe directory checks to avoid overwriting non-empty folders
- Built-in command to add extra casts to an existing Act project
- Fully tested with `pytest`

## Get Started

```bash
uvx --from act-operator act new
```

Act Operator requires Python 3.12 or newer. The project ships with `pyproject.toml` so `uv` manages dependencies reproducibly.

## Usage

### Create a new Act project

```bash
uv run act new
```

You can omit any option to trigger interactive prompts. When `path` points to a custom directory, the Act name defaults to that directory name.

### Add an additional cast

```bash
uv run act cast
```

The command validates that `path` is an Act project before rendering the new cast.

### Resulting layout

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


## Contributing

- Read the guides: [CONTRIBUTING_EN.md](CONTRIBUTING_EN.md) (EN)
