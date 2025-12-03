---
name: engineering-act
description: Use when creating new cast package, adding dependencies to monorepo or cast, syncing uv environment, or running langgraph dev server - handles project setup and package management
---

# Engineering Act Skill

Manage Act project setup, dependencies, and cast scaffolding.

## When NOT to Use

- Implementing casts/nodes → `developing-cast`
- Designing architectures → `architecting-act`
- Writing tests → `testing-cast`

## Operations

| Task | Resource |
|------|----------|
| Create new cast(package) | `resources/create-cast.md` |
| Add act(monorepo) dependency | `resources/add-dep-monorepo.md` |
| Add cast(package) dependency | `resources/add-dep-cast.md` |
| Sync environment | `resources/sync.md` |

## Quick Reference

```bash
# Create cast
uv run act cast -c "My Cast"

# Add dependencies
uv add langchain-openai              # Monorepo (production)
uv add --dev pytest-mock             # Monorepo (dev)
uv add --package my_cast langchain-openai  # Cast package

# Sync
uv sync --all-packages            # Development
uv sync --all-packages --no-dev   # Production

# LangGraph server
uv run langgraph dev
uv run langgraph dev --tunnel        # Non-Chrome browsers
```

## Dependency Groups

| Group | Flag | Contents |
|-------|------|----------|
| dev | `--dev` | act-operator + test + lint |
| test | `--group test` | pytest, langgraph-cli[inmem] |
| lint | `--group lint` | pre-commit, ruff |
