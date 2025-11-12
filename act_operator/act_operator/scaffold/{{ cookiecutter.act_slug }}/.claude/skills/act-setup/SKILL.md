---
name: act-setup
description: Set up and manage Act projects - use when installing dependencies, managing workspace, configuring development environment, or understanding project structure.
---

# Act Setup

**Use this skill when:**
- Setting up a new Act project
- Installing dependencies
- Managing uv workspace and packages
- Configuring development environment
- Understanding project structure
- Troubleshooting setup issues

## Quick Start

### Initial Setup

```bash
# Install all dependencies (includes dev tools)
uv sync --dev

# Or install production dependencies only
uv sync

# Start development server
uv run langgraph dev
```

### Project Structure

```
{{ cookiecutter.act_slug }}/
├── pyproject.toml          # Workspace root config
├── uv.lock                 # Shared dependency lock
├── langgraph.json          # Graph registry
├── .venv/                  # Shared virtual environment
├── README.md
├── TEMPLATE_README.md      # Detailed documentation
│
├── casts/                  # Cast modules
│   ├── __init__.py
│   ├── base_node.py        # Base classes
│   ├── base_graph.py
│   └── {{ cookiecutter.cast_snake }}/   # Example Cast
│       ├── pyproject.toml  # Cast package config
│       ├── graph.py
│       └── modules/
│
├── tests/                  # Test suite
│   ├── integration_tests/
│   └── unit_tests/
│
└── .claude/                # Claude skills
    └── skills/
```

## UV Workspace Management

This project uses **uv workspace** (multi-package mode) where each Cast is an independent package.

### Key Concepts

- **Workspace root**: Top-level `pyproject.toml` defines workspace
- **Members**: Each Cast is a workspace member with its own `pyproject.toml`
- **Shared lock**: Single `uv.lock` file for all members
- **Selective sync**: Install specific Casts or all at once

### Common Commands

#### Install All Packages

```bash
# Install all Casts and dependencies
uv sync --all-packages

# With dev dependencies
uv sync --dev --all-packages
```

#### Install Specific Cast

```bash
# Install only one Cast
uv sync --package {{ cookiecutter.cast_snake }}

# With dev dependencies
uv sync --dev --package {{ cookiecutter.cast_snake }}
```

#### Install Dev Dependencies

```bash
# Install dev tools (pytest, ruff, act-operator, etc.)
uv sync --dev

# Without dev dependencies
uv sync
```

## Dependency Management

### Dependency Layers

**1. Root dependencies** (shared by all Casts):
```toml
# pyproject.toml (root)
[project]
dependencies = [
    "langchain>=1.0.0",
    "langgraph>=1.0.0",
]
```

**2. Cast dependencies** (specific to each Cast):
```toml
# casts/my_cast/pyproject.toml
[project]
dependencies = [
    "langchain-openai>=0.1.0",
    "httpx>=0.25.0",
]
```

**3. Dev dependencies** (development tools):
```toml
# pyproject.toml (root)
[dependency-groups]
test = ["pytest", "langgraph-cli[inmem]"]
lint = ["pre-commit", "ruff"]
dev = [
    "ipykernel",
    "act_operator>=0.1.0",
    {include-group = "test"},
    {include-group = "lint"},
]
```

### Adding Dependencies

#### Add to Root (Shared)

```bash
# Add shared dependency
uv add langchain-community

# Updates: root pyproject.toml + uv.lock
```

#### Add to Cast (Specific)

```bash
# Navigate to Cast directory
cd casts/{{ cookiecutter.cast_snake }}

# Add Cast-specific dependency
uv add langchain-openai

# Updates: Cast pyproject.toml + root uv.lock
```

#### Remove Dependency

```bash
# Remove Cast-specific
cd casts/{{ cookiecutter.cast_snake }}
uv remove langchain-openai

# Remove shared
uv remove langchain-community
```

### Lock File Management

```bash
# Update lock file after manual pyproject.toml edits
uv lock

# Sync from updated lock
uv sync --all-packages
```

## Development Workflow

### Workflow 1: Working on Single Cast

```bash
# Install specific Cast
uv sync --dev --package {{ cookiecutter.cast_snake }}

# Make changes to Cast code

# Run dev server
uv run langgraph dev

# Test changes
uv run pytest tests/unit_tests/

# Add dependency if needed
cd casts/{{ cookiecutter.cast_snake }}
uv add new-package
```

### Workflow 2: Working on Multiple Casts

```bash
# Install multiple Casts
uv sync --dev --package cast1 --package cast2

# Make changes to both Casts

# Test all
uv run pytest -q

# Run server
uv run langgraph dev
```

### Workflow 3: Full Workspace Development

```bash
# Install everything
uv sync --dev --all-packages

# Run all tests
uv run pytest -q

# Run linting
uv run ruff check . --fix
uv run ruff format .

# Run dev server
uv run langgraph dev
```

## Running Commands

### Development Server

```bash
# Start LangGraph dev server
uv run langgraph dev

# With tunnel (for non-Chrome browsers)
uv run langgraph dev --tunnel

# Server URLs:
# - API: http://127.0.0.1:2024
# - Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
# - API Docs: http://127.0.0.1:2024/docs
```

### Testing

```bash
# Run all tests
uv run pytest -q

# Run specific test file
uv run pytest tests/unit_tests/test_node.py

# Run with coverage
uv run pytest --cov
```

### Code Quality

```bash
# Check code quality
uv run ruff check .

# Fix issues automatically
uv run ruff check . --fix

# Format code
uv run ruff format .
```

### Adding New Cast

```bash
# Ensure dev dependencies installed (act-operator)
uv sync --dev

# Create new Cast
uv run act cast my-new-cast

# Install new Cast
uv sync --all-packages
```

## Workspace Configuration

### Root pyproject.toml

```toml
[project]
name = "{{ cookiecutter.act_slug }}"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "langchain>=1.0.0",
    "langgraph>=1.0.0",
]

[tool.uv.workspace]
members = ["casts/*"]
exclude = [
    "casts/__pycache__",
    "casts/**/__pycache__",
    "casts/**/.venv",
]
```

**Key settings:**
- `members`: Glob pattern for workspace members
- `exclude`: Patterns to ignore

### Cast pyproject.toml

```toml
# casts/my_cast/pyproject.toml
[project]
name = "my_cast"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    # Cast-specific dependencies
]
```

**Important:**
- Name must match directory for workspace detection
- Each Cast can have independent version
- Dependencies can be Cast-specific

## Troubleshooting

### Issue: Cast not recognized as workspace member

**Symptoms**: Cast doesn't install with `uv sync --package`

**Fix**:
```bash
# Check pyproject.toml has [project] section
cat casts/my_cast/pyproject.toml

# Ensure name matches directory
# name = "my_cast" for casts/my_cast/

# Check workspace members pattern
# Root pyproject.toml: members = ["casts/*"]

# Re-sync
uv sync --all-packages
```

### Issue: Dependency conflicts

**Symptoms**: uv reports version conflicts

**Fix**:
```bash
# Check conflicting versions
uv lock

# Align versions in pyproject.toml files
# Edit conflicting package versions to match

# Re-lock
uv lock

# Sync
uv sync --all-packages
```

### Issue: Virtual environment issues

**Symptoms**: Wrong Python version, missing packages

**Fix**:
```bash
# Remove venv
rm -rf .venv

# Re-create with correct Python
uv venv --python 3.11

# Sync packages
uv sync --dev --all-packages
```

### Issue: Lock file out of sync

**Symptoms**: "uv.lock is out of date"

**Fix**:
```bash
# Update lock file
uv lock

# Sync from updated lock
uv sync --all-packages
```

### Issue: Import errors between Casts

**Symptoms**: `ModuleNotFoundError` when importing from another Cast

**Fix**:
Casts are independent packages. Don't import between Casts directly.

```python
# ❌ Bad: Cross-Cast imports
from casts.cast1.modules import X

# ✅ Good: Share via base classes or utils
from casts.base_node import BaseNode
class MyNode(BaseNode): ...
```

## Best Practices

### 1. Keep Casts Independent

Casts should not import from each other:

```python
# ✅ Good: Share via base classes
from casts.base_node import BaseNode

# ❌ Bad: Cross-Cast imports
from casts.other_cast.modules.nodes import SomeNode
```

### 2. Use Shared Dependencies Wisely

Add to root only if used by multiple Casts:

```bash
# Used by all Casts → Root
uv add langchain

# Used by one Cast → Cast-specific
cd casts/my_cast
uv add langchain-openai
```

### 3. Install What You Need

During development, install only required Casts:

```bash
# Faster sync, fewer dependencies
uv sync --dev --package my_active_cast
```

### 4. Keep Lock File Updated

After dependency changes:

```bash
uv lock
git add uv.lock
git commit -m "Update dependencies"
```

### 5. Use Dev Groups

Organize development tools:

```toml
[dependency-groups]
test = ["pytest", "pytest-cov"]
lint = ["ruff", "pre-commit"]
dev = [
    "act_operator>=0.1.0",
    {include-group = "test"},
    {include-group = "lint"},
]
```

## Quick Reference

```bash
# Installation
uv sync --dev --all-packages        # All Casts + dev tools
uv sync --all-packages              # All Casts (no dev)
uv sync --dev --package <cast>      # Specific Cast + dev
uv sync --package <cast>            # Specific Cast (no dev)

# Dependencies
uv add <package>                    # Add to root
cd casts/<cast> && uv add <pkg>     # Add to Cast
uv remove <package>                 # Remove
uv lock                             # Update lock file

# Development
uv run langgraph dev                # Dev server
uv run pytest -q                    # Tests
uv run ruff check . --fix           # Lint + fix
uv run ruff format .                # Format
uv run act cast <name>              # New Cast

# Maintenance
rm -rf .venv && uv sync --dev --all-packages  # Fresh install
```

## References

**Official documentation:**
- uv: https://docs.astral.sh/uv/
- LangGraph: https://docs.langchain.com/oss/python/langgraph/overview
- LangGraph CLI: https://docs.langchain.com/oss/python/langgraph/cli

**Related skills:**
- Cast development: Use `cast-development` skill
- Testing: Use `testing-debugging` skill
