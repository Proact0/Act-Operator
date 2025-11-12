# Act-Operator Architecture Reference

Comprehensive guide to Act-Operator architecture, Cast structure, UV workspace concepts, and project organization.

## Table of Contents

1. [Introduction](#introduction)
2. [Overall Architecture](#overall-architecture)
   - [System Components](#system-components)
   - [Act-Operator Framework](#act-operator-framework)
   - [Cast Lifecycle](#cast-lifecycle)
3. [Cast Structure](#cast-structure)
   - [Directory Layout](#directory-layout)
   - [Core Components](#core-components)
   - [Configuration Files](#configuration-files)
4. [UV Workspace Concepts](#uv-workspace-concepts)
   - [What is UV](#what-is-uv)
   - [Workspace Mode](#workspace-mode)
   - [Package Management](#package-management)
5. [Project Layout](#project-layout)
   - [Multi-Cast Projects](#multi-cast-projects)
   - [Dependencies](#dependencies)
   - [Virtual Environments](#virtual-environments)
6. [Design Principles](#design-principles)
   - [Modularity](#modularity)
   - [Reusability](#reusability)
   - [Testability](#testability)
7. [Scaffolding with Cookiecutter](#scaffolding-with-cookiecutter)
8. [References](#references)

---

## Introduction

Act-Operator is a framework for building LangGraph-based AI agents ("Casts"). This guide explains the architecture and design principles.

**Key concepts:**
- **Act-Operator**: Framework for building Casts
- **Cast**: A LangGraph application
- **UV**: Fast Python package manager
- **Workspace**: Multi-package project structure

---

## Overall Architecture

```
┌─────────────────────────────────────────┐
│           Act-Operator CLI              │
│  (cast create, cast serve, etc.)        │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│        UV Workspace (Repository)        │
│  ┌─────────────────────────────────┐   │
│  │  Cast 1 (weather-agent)         │   │
│  │  ├─ graph.py                    │   │
│  │  ├─ nodes/                      │   │
│  │  └─ pyproject.toml              │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  Cast 2 (customer-support)      │   │
│  │  ├─ graph.py                    │   │
│  │  ├─ nodes/                      │   │
│  │  └─ pyproject.toml              │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  act-operator-lib               │   │
│  │  (shared utilities)             │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### System Components

1. **Act-Operator CLI**: Command-line tool for Cast management
2. **act-operator-lib**: Shared library (BaseNode, utilities)
3. **Casts**: Individual LangGraph applications
4. **UV Workspace**: Manages all packages together

---

## Cast Structure

### Directory Layout

```
my-cast/
├── .claude/               # Claude skills for development
│   └── skills/
│       ├── act-quickstart/
│       ├── cast-development/
│       ├── graph-composition/
│       ├── modules-integration/
│       ├── node-implementation/
│       ├── state-management/
│       └── testing-debugging/
├── my_cast/              # Python package
│   ├── __init__.py
│   ├── graph.py          # Graph definition
│   ├── state.py          # State class
│   ├── nodes/            # Node implementations
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   └── tools.py
│   └── tools/            # Tool definitions
│       ├── __init__.py
│       └── my_tools.py
├── tests/                # Tests
│   ├── __init__.py
│   ├── test_graph.py
│   └── test_nodes.py
├── .env                  # Environment variables
├── .env.example          # Example environment
├── .gitignore
├── langgraph.json        # LangGraph configuration
├── pyproject.toml        # Package configuration
└── README.md
```

### Core Components

**graph.py:**
```python
from langgraph.graph import StateGraph, END
from .state import State
from .nodes.agent import AgentNode

# Build graph
builder = StateGraph(State)
builder.add_node("agent", AgentNode())
builder.set_entry_point("agent")
builder.add_edge("agent", END)

# Compile
graph = builder.compile()
```

**state.py:**
```python
from dataclasses import dataclass
from typing import Annotated
from langgraph.graph.message import add_messages

@dataclass(kw_only=True)
class State:
    messages: Annotated[list, add_messages]
    query: str
```

**nodes/agent.py:**
```python
from act_operator_lib.base_node import BaseNode

class AgentNode(BaseNode):
    def execute(self, state):
        # Node logic
        return {"result": "value"}
```

### Configuration Files

**pyproject.toml:**
```toml
[project]
name = "my-cast"
version = "0.1.0"
dependencies = [
    "langgraph>=0.2.0",
    "langchain-anthropic>=0.1.0",
    "act-operator-lib",
]

[tool.uv.sources]
act-operator-lib = { workspace = true }
```

**langgraph.json:**
```json
{
  "dependencies": ["."],
  "graphs": {
    "my_cast": "./my_cast/graph.py:graph"
  },
  "env": ".env"
}
```

---

## UV Workspace Concepts

### What is UV

UV is a fast Python package manager and project manager:

- **Fast**: Written in Rust, 10-100x faster than pip
- **Reliable**: Lock files for reproducible installs
- **Universal**: Manages Python versions, packages, projects
- **Workspace-aware**: Multi-package projects

### Workspace Mode

**pyproject.toml (root):**
```toml
[tool.uv.workspace]
members = [
    "casts/*",
    "act-operator-lib"
]
```

**Benefits:**
- Single virtual environment for all packages
- Shared dependencies
- Local package references
- Consistent versions

### Package Management

```bash
# Add dependency to Cast
cd my-cast
uv add langchain-openai

# Sync all workspace packages
uv sync

# Run command in workspace
uv run langgraph dev

# Add dev dependency
uv add --dev pytest
```

---

## Project Layout

### Multi-Cast Projects

```
act-operator-workspace/
├── pyproject.toml        # Workspace config
├── uv.lock              # Lockfile
├── .venv/               # Shared venv
├── casts/
│   ├── weather-agent/
│   │   └── pyproject.toml
│   ├── customer-support/
│   │   └── pyproject.toml
│   └── data-analyzer/
│       └── pyproject.toml
└── act-operator-lib/
    └── pyproject.toml
```

### Dependencies

**Three types:**

1. **External** (from PyPI):
```toml
dependencies = [
    "langgraph>=0.2.0",
    "langchain-anthropic>=0.1.0",
]
```

2. **Workspace** (local packages):
```toml
[tool.uv.sources]
act-operator-lib = { workspace = true }
```

3. **Dev** (testing, linting):
```toml
[dependency-groups]
dev = [
    "pytest>=7.0",
    "ruff>=0.1.0",
]
```

### Virtual Environments

```bash
# UV manages .venv automatically
uv sync  # Creates .venv if needed

# Activate manually (usually not needed)
source .venv/bin/activate

# Run without activating
uv run python script.py
uv run pytest
```

---

## Design Principles

### Modularity

- **Separation of concerns**: Nodes, state, tools separate
- **Reusable components**: act-operator-lib for common code
- **Independent Casts**: Each Cast is standalone package

### Reusability

- **BaseNode**: Shared base class for all nodes
- **Common utilities**: Logging, validation, etc.
- **Tool libraries**: Shared tools across Casts

### Testability

- **Unit testable nodes**: Test execute() directly
- **Mockable dependencies**: Inject dependencies
- **Integration tests**: Test full graph execution

---

## Scaffolding with Cookiecutter

Act-Operator uses cookiecutter for Cast creation:

```bash
act-operator cast create my-new-cast
```

**Template variables:**
- `act_slug`: Directory name (my-new-cast)
- `python_package`: Package name (my_new_cast)
- `act_name`: Display name (My New Cast)
- `description`: Cast description

**Generated structure** follows best practices automatically.

---

## References

- UV Documentation: https://docs.astral.sh/uv/
- LangGraph: https://langchain-ai.github.io/langgraph/
- Cookiecutter: https://cookiecutter.readthedocs.io/
- Python Packaging: https://packaging.python.org/
