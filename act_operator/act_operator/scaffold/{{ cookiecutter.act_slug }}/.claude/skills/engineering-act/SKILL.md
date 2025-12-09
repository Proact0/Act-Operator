---
name: engineering-act
description: Use when creating new cast package, installing/managing dependencies (monorepo or cast-level), resolving dependency conflicts or packages out of sync, or launching langgraph dev server - checks CLAUDE.md first for context, then handles all uv-based project setup and package management (dev/test/lint groups)
---

# Engineering {{ cookiecutter.act_name }} Act

Manage {{ cookiecutter.act_name }} Act project setup, dependencies, and cast scaffolding.

## When NOT to Use

- Implementing casts/nodes → `developing-cast`
- Designing architectures → `architecting-act`
- Writing tests → `testing-cast`

## Workflow

**Before any operation:**
1. Check CLAUDE.md files if they exist
   - **Root `/CLAUDE.md`**: Review Act overview and Casts table
   - **Cast `/casts/{cast_slug}/CLAUDE.md`**: Review cast-specific dependencies and tech stack
2. Proceed with operation below

## Operations

| Task | Resource |
|------|----------|
| Create new cast(package) | `resources/create-cast.md` |
| Add act(monorepo) dependency | `resources/add-dep-act.md` |
| Add cast(package) dependency | `resources/add-dep-cast.md` |
| Sync environment | `resources/sync.md` |

## Quick Reference

```bash
# 1. Check CLAUDE.md files (if exist)
#    Root /CLAUDE.md: Review existing Casts in table
#    Cast /casts/{cast_slug}/CLAUDE.md: Check Technology Stack section

# 2. Create cast
uv run act cast -c "My Cast"

# 3. Add dependencies (refer to cast's CLAUDE.md Technology Stack)
uv add langchain-openai              # Monorepo (production)
uv add --dev pytest-mock             # Monorepo (dev)
uv add --package my_cast langchain-openai  # Cast package

# 4. Sync
uv sync --all-packages            # Development
uv sync --all-packages --no-dev   # Production

# 5. LangGraph server
uv run langgraph dev
uv run langgraph dev --tunnel        # Non-Chrome browsers
```

## Dependency Groups

| Group | Flag | Contents |
|-------|------|----------|
| dev | `--dev` | act-operator + test + lint |
| test | `--group test` | pytest, langgraph-cli[inmem] |
| lint | `--group lint` | pre-commit, ruff |
