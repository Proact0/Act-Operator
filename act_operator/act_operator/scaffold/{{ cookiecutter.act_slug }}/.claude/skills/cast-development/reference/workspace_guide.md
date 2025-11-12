# UV Workspace Guide for Act-Operator

Comprehensive guide to UV workspace mode, multi-cast projects, dependencies, and package management.

## Table of Contents

1. [Introduction](#introduction)
2. [UV Workspace Mode](#uv-workspace-mode)
   - [What is a Workspace](#what-is-a-workspace)
   - [Benefits](#benefits)
   - [Workspace Configuration](#workspace-configuration)
3. [Multi-Cast Project Structure](#multi-cast-project-structure)
   - [Directory Layout](#directory-layout)
   - [Adding New Casts](#adding-new-casts)
   - [Workspace Members](#workspace-members)
4. [Managing Dependencies](#managing-dependencies)
   - [External Dependencies](#external-dependencies)
   - [Workspace Dependencies](#workspace-dependencies)
   - [Dependency Groups](#dependency-groups)
   - [Version Constraints](#version-constraints)
5. [Package Management with UV](#package-management-with-uv)
   - [Installing Packages](#installing-packages)
   - [Updating Packages](#updating-packages)
   - [Removing Packages](#removing-packages)
   - [Lock Files](#lock-files)
6. [pyproject.toml Configuration](#pyprojecttoml-configuration)
   - [Workspace Root](#workspace-root)
   - [Cast Configuration](#cast-configuration)
   - [Sources](#sources)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [References](#references)

---

## Introduction

UV workspace mode enables managing multiple Casts in a single repository with shared dependencies and virtual environment.

**Key benefits:**
- Single virtual environment
- Shared dependencies
- Local package references
- Faster installs

---

## UV Workspace Mode

### What is a Workspace

A workspace is a collection of related Python packages managed together:

```
workspace/
├── pyproject.toml       # Workspace config
├── uv.lock             # Shared lockfile
├── .venv/              # Single virtual environment
├── cast-1/
│   └── pyproject.toml
├── cast-2/
│   └── pyproject.toml
└── act-operator-lib/
    └── pyproject.toml
```

### Benefits

1. **Single virtual environment**: All packages share .venv
2. **Dependency deduplication**: Shared packages installed once
3. **Local development**: Reference local packages directly
4. **Consistency**: All packages use same versions
5. **Faster installs**: UV's speed + caching

### Workspace Configuration

**Root pyproject.toml:**
```toml
[tool.uv.workspace]
members = [
    "casts/*",
    "act-operator-lib"
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.0",
    "ruff>=0.1.0",
]
```

---

## Multi-Cast Project Structure

### Directory Layout

```
my-workspace/
├── pyproject.toml           # Workspace root
├── uv.lock                  # Lockfile
├── .venv/                   # Shared venv
├── .gitignore
├── README.md
├── casts/
│   ├── weather-agent/
│   │   ├── weather_agent/
│   │   │   ├── graph.py
│   │   │   └── nodes/
│   │   ├── tests/
│   │   └── pyproject.toml
│   ├── customer-support/
│   │   ├── customer_support/
│   │   │   ├── graph.py
│   │   │   └── nodes/
│   │   ├── tests/
│   │   └── pyproject.toml
│   └── data-analyzer/
│       ├── data_analyzer/
│       │   ├── graph.py
│       │   └── nodes/
│       ├── tests/
│       └── pyproject.toml
└── act-operator-lib/
    ├── act_operator_lib/
    │   ├── __init__.py
    │   └── base_node.py
    └── pyproject.toml
```

### Adding New Casts

```bash
# Create new Cast in workspace
cd my-workspace
act-operator cast create casts/new-cast

# UV automatically detects it as workspace member
uv sync

# Cast can now reference other workspace packages
```

### Workspace Members

**Glob patterns:**
```toml
[tool.uv.workspace]
members = [
    "casts/*",           # All casts
    "act-operator-lib",  # Specific package
    "tools/*/",         # Nested packages
]

# Exclude patterns
exclude = [
    "casts/archived/*",
    "experiments/*",
]
```

---

## Managing Dependencies

### External Dependencies

**Add to specific Cast:**
```bash
cd casts/weather-agent
uv add langchain-openai

# Updates casts/weather-agent/pyproject.toml:
# dependencies = ["langchain-openai"]
```

**Add to multiple Casts:**
```bash
# Option 1: Add to each
cd casts/weather-agent && uv add pydantic
cd ../customer-support && uv add pydantic

# Option 2: Add to workspace root (shared)
cd ../..
uv add pydantic
```

### Workspace Dependencies

**Reference local packages:**

```toml
# casts/weather-agent/pyproject.toml
[project]
dependencies = [
    "act-operator-lib",  # From workspace
]

[tool.uv.sources]
act-operator-lib = { workspace = true }
```

**Usage in code:**
```python
# In casts/weather-agent/weather_agent/nodes/agent.py
from act_operator_lib.base_node import BaseNode

class AgentNode(BaseNode):
    def execute(self, state):
        return {"result": "value"}
```

### Dependency Groups

**Development dependencies:**

```toml
# Root pyproject.toml
[dependency-groups]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "ruff>=0.1.0",
]

# Install dev dependencies
uv sync --group dev
```

**Optional dependencies:**
```toml
# casts/weather-agent/pyproject.toml
[project.optional-dependencies]
openai = ["langchain-openai"]
anthropic = ["langchain-anthropic"]

# Install with extras
uv sync --extra openai
```

### Version Constraints

```toml
dependencies = [
    "langgraph>=0.2.0,<0.3.0",    # Range
    "langchain-core==0.3.0",       # Exact
    "pydantic>=2.0",               # Minimum
]
```

---

## Package Management with UV

### Installing Packages

```bash
# Install all workspace packages
uv sync

# Install specific Cast
cd casts/weather-agent
uv sync

# Add package
uv add langchain-openai

# Add dev dependency
uv add --dev pytest

# Install with extras
uv sync --extra openai
```

### Updating Packages

```bash
# Update all packages
uv lock --upgrade

# Update specific package
uv lock --upgrade-package langchain-core

# Sync after update
uv sync
```

### Removing Packages

```bash
# Remove package
uv remove langchain-openai

# Remove dev dependency
uv remove --dev pytest
```

### Lock Files

**uv.lock:**
- Generated from pyproject.toml
- Locks all dependencies to specific versions
- Ensures reproducible installs
- Shared across workspace

```bash
# Generate/update lock file
uv lock

# Sync from lock file
uv sync

# Check if lock file is up to date
uv lock --check
```

---

## pyproject.toml Configuration

### Workspace Root

```toml
[tool.uv.workspace]
members = ["casts/*", "act-operator-lib"]

[dependency-groups]
dev = [
    "pytest>=7.0",
    "ruff>=0.1.0",
]
```

### Cast Configuration

```toml
[project]
name = "weather-agent"
version = "0.1.0"
description = "Weather agent Cast"
requires-python = ">=3.11"
dependencies = [
    "langgraph>=0.2.0",
    "langchain-anthropic>=0.1.0",
    "act-operator-lib",
]

[tool.uv.sources]
act-operator-lib = { workspace = true }

[dependency-groups]
dev = [
    "pytest>=7.0",
]
```

### Sources

**Workspace packages:**
```toml
[tool.uv.sources]
act-operator-lib = { workspace = true }
```

**Git repositories:**
```toml
[tool.uv.sources]
my-package = { git = "https://github.com/user/repo.git" }
```

**Local paths:**
```toml
[tool.uv.sources]
local-package = { path = "../other-package" }
```

---

## Best Practices

1. **One workspace per repository**: Keep related Casts together
2. **Shared utilities in workspace**: Common code in act-operator-lib
3. **Lock file in version control**: Commit uv.lock
4. **Consistent Python version**: Specify in root pyproject.toml
5. **Dev dependencies in root**: Share across all Casts
6. **Regular updates**: `uv lock --upgrade` periodically
7. **Test before commit**: `uv run pytest` in CI
8. **Document dependencies**: README with setup instructions

---

## Troubleshooting

### Workspace not detected

```bash
# Check workspace config
cat pyproject.toml

# Verify members paths
ls casts/

# Force sync
uv sync --refresh
```

### Dependency conflicts

```bash
# Check what's installed
uv pip list

# Inspect lock file
uv tree

# Update conflicting package
uv lock --upgrade-package problematic-package
```

### Import errors

```bash
# Ensure workspace synced
uv sync

# Check package installed
uv pip show act-operator-lib

# Verify path
python -c "import act_operator_lib; print(act_operator_lib.__file__)"
```

---

## References

- UV Documentation: https://docs.astral.sh/uv/
- UV Workspaces: https://docs.astral.sh/uv/concepts/workspaces/
- Python Packaging: https://packaging.python.org/
