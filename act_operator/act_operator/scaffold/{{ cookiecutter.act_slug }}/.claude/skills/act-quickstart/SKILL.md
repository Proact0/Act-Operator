---
name: act-setup
description: Set up and manage Act projects with uv workspace. Use when installing dependencies, managing workspace, running development commands, or understanding project structure in Act projects.
---

# Act Setup

## Overview

Act projects use uv workspace for multi-Cast management. This skill provides quick start guidance and common commands for Act project setup and development.

## When to Use This Skill

- Setting up a new Act project
- Managing uv workspace
- Installing dependencies
- Running development commands
- Understanding project structure

## Quick Start Guide

### 1. Install Dependencies

```bash
# Install all Casts with dev tools
uv sync --dev --all-packages

# Install specific Cast only
uv sync --dev --package <cast-name>
```

### 2. Create New Cast

```bash
# Interactive mode (recommended)
uv run act cast

# Or specify name directly
uv run act cast my-new-cast

# After creating, install it
uv sync --all-packages
```

### 3. Run Development Server

```bash
# Start LangGraph dev server
uv run langgraph dev
```

### 4. Run Tests

```bash
# Run all tests
uv run pytest -q

# Run with verbose output
uv run pytest -v
```

## Architecture Overview

```
my-act-project/
├── casts/                    # Cast workspace members
│   ├── cast_a/              # Independent LangGraph graph
│   │   ├── graph.py         # Graph definition
│   │   ├── modules/         # State, nodes, etc.
│   │   └── pyproject.toml   # Cast dependencies
│   └── cast_b/              # Another Cast
├── tests/                    # Shared tests
│   ├── unit_tests/
│   └── integration_tests/
├── pyproject.toml           # Root workspace config
└── langgraph.json           # LangGraph CLI config
```

## Common Commands

```bash
# Dependency management
uv sync --dev --all-packages    # Install all with dev tools
uv sync --all-packages          # Install all (no dev)
uv add <package>                # Add to root dependencies

# Development
uv run langgraph dev            # Dev server
uv run pytest -q                # Run tests
uv run act cast <name>          # Create new Cast

# Cast-specific
cd casts/<cast-name>
uv add <package>                # Add Cast-specific dependency
```

## Troubleshooting

**Issue**: Dependencies not found
- **Fix**: Run `uv sync --all-packages --dev`

**Issue**: Cast not appearing in langgraph dev
- **Fix**: Check `langgraph.json` includes Cast path

**Issue**: Import errors
- **Fix**: Ensure Cast is installed with `uv sync --all-packages`

## Resources

### References
- `references/architecture.md` - Detailed architecture guide
- `references/cli_commands.md` - Complete CLI reference

### Templates
- `templates/project_checklist.md` - Setup checklist

### Official Documentation
- uv: https://docs.astral.sh/uv/
- LangGraph CLI: https://docs.langchain.com/oss/python/langgraph/cli
