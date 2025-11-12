# UV Workspace Management Guide

## Contents

- [Overview](#overview)
- [Workspace Structure](#workspace-structure)
- [Common Commands](#common-commands)
- [Cast as Workspace Members](#cast-as-workspace-members)
- [Dependency Management](#dependency-management)
- [Development Workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)

---

## Overview

This Act project uses **uv workspace** (multi-package mode) to manage Cast modules as independent packages.

**Key Concepts:**
- **Workspace root**: Top-level `pyproject.toml` defines workspace
- **Members**: Each Cast is a workspace member with its own `pyproject.toml`
- **Shared lock**: Single `uv.lock` file for all members
- **Selective sync**: Install specific Casts or all at once

**Benefits:**
- Each Cast is independently versioned
- Shared dependency resolution across Casts
- Easy to add/remove Casts
- Clean separation of concerns

---

## Workspace Structure

```
{{ cookiecutter.act_slug }}/
├── pyproject.toml              # Workspace root configuration
├── uv.lock                     # Shared lock file
├── langgraph.json              # Graph registry
├── .venv/                      # Shared virtual environment
│
├── casts/
│   ├── __init__.py
│   ├── base_node.py            # Shared base classes
│   ├── base_graph.py
│   │
│   ├── {{ cookiecutter.cast_snake }}/     # Cast 1 (workspace member)
│   │   ├── pyproject.toml      # Member package config
│   │   ├── __init__.py
│   │   ├── graph.py
│   │   └── modules/
│   │
│   └── another_cast/           # Cast 2 (workspace member)
│       ├── pyproject.toml
│       ├── __init__.py
│       ├── graph.py
│       └── modules/
│
└── tests/                      # Workspace-level tests
```

---

## Workspace Root Configuration

**File**: `pyproject.toml` (root)

```toml
[project]
name = "{{ cookiecutter.act_slug }}"
version = "0.1.0"
description = "{{ cookiecutter.act_name }} powered by Act Operator"
requires-python = ">=3.11"
dependencies = [
    "langchain>=1.0.0",
    "langgraph>=1.0.0",
]

[tool.uv.workspace]
members = ["casts/*"]           # All casts/ subdirectories
exclude = [
    "casts/__pycache__",
    "casts/**/__pycache__",
    "casts/**/.venv",
]
```

**Key Settings:**
- `members`: Glob pattern for workspace members
- `exclude`: Patterns to ignore
- Root `dependencies`: Shared across all Casts

---

## Cast Package Configuration

**File**: `casts/{{ cookiecutter.cast_snake }}/pyproject.toml`

```toml
[project]
name = "{{ cookiecutter.cast_snake }}"
version = "0.1.0"
description = "{{ cookiecutter.cast_name }} Cast"
requires-python = ">=3.11"
dependencies = [
    # Cast-specific dependencies
    "langchain-openai>=0.1.0",
]
```

**Key Points:**
- Each Cast has its own `pyproject.toml`
- Name must match directory for workspace detection
- Dependencies can be Cast-specific
- Version is independent of root

---

## Common Commands

### Install All Casts

Install entire workspace (all Cast packages):

```bash
uv sync --all-packages
```

**When to use**: First-time setup, full development environment

### Install Specific Cast

Install only one Cast package:

```bash
uv sync --package {{ cookiecutter.cast_snake }}
```

**When to use**: Working on specific Cast, minimizing dependencies

### Install Multiple Casts

Install selected Casts:

```bash
uv sync --package cast1 --package cast2
```

### Add Dependency to Cast

Add dependency to specific Cast:

```bash
cd casts/{{ cookiecutter.cast_snake }}
uv add langchain-openai
```

This updates:
- `casts/{{ cookiecutter.cast_snake }}/pyproject.toml`
- `uv.lock` (workspace-level)

### Add Shared Dependency

Add dependency to root (shared by all Casts):

```bash
uv add langchain-community
```

This updates:
- Root `pyproject.toml`
- `uv.lock`

### Remove Dependency

Remove Cast-specific dependency:

```bash
cd casts/{{ cookiecutter.cast_snake }}
uv remove langchain-openai
```

### Run Commands in Workspace

Execute commands with uv:

```bash
# Run langgraph dev server
uv run langgraph dev

# Run tests
uv run pytest -q

# Run ruff checks
uv run ruff check .

# Run python script
uv run python scripts/my_script.py
```

---

## Cast as Workspace Members

### Adding New Cast

**Recommended: Use `act cast` command**

```bash
# Interactive mode (recommended)
uv run act cast

# Non-interactive mode
uv run act cast --path . --cast-name "New Cast"
```

When you run `act cast`, it automatically:

1. **Validates** Act project structure
   - Checks for `pyproject.toml`, `langgraph.json`
   - Verifies `casts/base_node.py` and `casts/base_graph.py` exist

2. **Creates** complete Cast structure:
   - Cast directory with all module files
   - `pyproject.toml` as workspace member
   - `graph.py`, `modules/state.py`, `modules/nodes.py` (required)
   - Optional module templates (agents, tools, prompts, etc.)

3. **Updates** `langgraph.json`:
   - Adds new graph entry automatically
   - Example: `"new-cast": "./casts/new_cast/graph.py:new_cast_graph"`

4. **Workspace integration**:
   - Cast becomes workspace member automatically
   - Ready for `uv sync --package new_cast`

**Manual steps (only if `act cast` is not available):**

```bash
# 1. Create Cast directory
mkdir casts/new_cast

# 2. Create pyproject.toml
cat > casts/new_cast/pyproject.toml <<EOF
[project]
name = "new_cast"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []
EOF

# 3. Create required files (state.py, nodes.py, graph.py)
# ... (copy from template)

# 4. Update langgraph.json
# ... (add graph entry)

# 5. Sync workspace
uv sync --package new_cast
```

### Removing Cast

To remove a Cast from workspace:

```bash
# 1. Delete Cast directory
rm -rf casts/old_cast

# 2. Remove from langgraph.json
# Edit langgraph.json and remove the Cast's graph entry

# 3. Sync workspace
uv sync --all-packages
```

---

## Dependency Management

### Dependency Layers

**1. Root dependencies** (shared by all):
```toml
# pyproject.toml (root)
[project]
dependencies = [
    "langchain>=1.0.0",
    "langgraph>=1.0.0",
]
```

**2. Cast dependencies** (specific to Cast):
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
test = ["pytest"]
lint = ["ruff", "pre-commit"]
dev = [
    "ipykernel",
    {include-group = "test"},
    {include-group = "lint"},
]
```

### Resolving Dependencies

uv resolves dependencies across entire workspace:

```bash
# Update lock file
uv lock

# Sync with lock file
uv sync --all-packages
```

If conflicts occur, uv will report them and suggest fixes.

---

## Development Workflow

### Workflow 1: Working on Single Cast

```bash
# 1. Install specific Cast
uv sync --package {{ cookiecutter.cast_snake }}

# 2. Make changes to Cast code
# Edit casts/{{ cookiecutter.cast_snake }}/modules/nodes.py

# 3. Run dev server
uv run langgraph dev

# 4. Test changes
uv run pytest tests/unit_tests/test_node.py

# 5. Add dependency if needed
cd casts/{{ cookiecutter.cast_snake }}
uv add new-package

# 6. Commit changes
git add .
git commit -m "Update {{ cookiecutter.cast_snake }} Cast"
```

### Workflow 2: Working on Multiple Casts

```bash
# 1. Install multiple Casts
uv sync --package cast1 --package cast2

# 2. Make changes to both Casts

# 3. Test all
uv run pytest -q

# 4. Commit
git add .
git commit -m "Update multiple Casts"
```

### Workflow 3: Full Workspace Development

```bash
# 1. Install everything
uv sync --all-packages

# 2. Run all tests
uv run pytest -q

# 3. Run linting
uv run ruff check . --fix
uv run ruff format .

# 4. Run dev server
uv run langgraph dev
```

---

## Troubleshooting

### Issue: Cast not recognized as workspace member

**Symptoms**: Cast doesn't install with `--package`

**Fix**:
```bash
# 1. Check pyproject.toml has [project] section
cat casts/my_cast/pyproject.toml

# 2. Ensure name matches directory
# name = "my_cast" for casts/my_cast/

# 3. Check workspace members pattern
# Root pyproject.toml: members = ["casts/*"]

# 4. Re-sync
uv sync --all-packages
```

### Issue: Import errors between Casts

**Symptoms**: `ModuleNotFoundError` when importing from another Cast

**Fix**:
```bash
# Casts are independent packages
# Don't import between Casts directly

# ❌ Bad: from casts.cast1.modules import X
# ✅ Good: Share via base classes or utils
```

### Issue: Dependency conflicts

**Symptoms**: uv reports version conflicts

**Fix**:
```bash
# 1. Check conflicting versions
uv lock

# 2. Align versions in pyproject.toml files
# Edit conflicting package versions to match

# 3. Re-lock
uv lock

# 4. Sync
uv sync --all-packages
```

### Issue: Virtual environment issues

**Symptoms**: Wrong Python version, missing packages

**Fix**:
```bash
# 1. Remove venv
rm -rf .venv

# 2. Re-create with correct Python
uv venv --python 3.11

# 3. Sync packages
uv sync --all-packages
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

---

## Best Practices

### 1. Keep Casts Independent

Casts should not import from each other:

```python
# ❌ Bad: Cross-Cast imports
from casts.cast1.modules.nodes import SomeNode

# ✅ Good: Share via base classes
from casts.base_node import BaseNode
class SomeNode(BaseNode): ...
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
uv sync --package my_active_cast
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
docs = ["mkdocs", "mkdocs-material"]
dev = [
    {include-group = "test"},
    {include-group = "lint"},
]
```

Install dev dependencies:
```bash
uv sync --all-packages --group dev
```

---

## Quick Reference

```bash
# Install
uv sync --all-packages                    # All Casts
uv sync --package <cast-name>             # Specific Cast

# Dependencies
uv add <package>                          # Add to root
cd casts/<cast> && uv add <package>       # Add to Cast
uv remove <package>                       # Remove

# Run
uv run langgraph dev                      # Dev server
uv run pytest -q                          # Tests
uv run ruff check . --fix                 # Lint

# Maintenance
uv lock                                   # Update lock file
uv sync --all-packages                    # Sync from lock
rm -rf .venv && uv sync --all-packages    # Fresh install
```
