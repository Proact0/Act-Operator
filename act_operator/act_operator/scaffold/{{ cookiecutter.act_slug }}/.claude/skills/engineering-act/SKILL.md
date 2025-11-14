---
name: engineering-act
description: Use when adding dependencies, syncing environment, or creating new casts in Act projects - provides correct uv and act commands with workspace awareness
---

# Engineering Act

## Overview

Quick reference for Act project operations: dependencies, environment sync, cast creation. Use exact commands to minimize errors.

## When to Use

Use when user wants to:
- Add libraries/frameworks to project
- Sync environment after changes
- Create new casts (graphs)
- Update dependencies

**NOT for:** Architecture design (use `architecting-act`), implementation (use `developing-cast`)

## Core Operations

### Adding Dependencies

**Project-wide dependency (all casts can use):**
```bash
uv add <package-name>
uv sync
```

**Cast-specific dependency (only one cast needs it):**
```bash
uv add <package-name> --package <cast-name>
uv sync --package <cast-name>
```

**Development dependency:**
```bash
uv add --dev <package-name>
uv sync --dev
```

**ALWAYS sync after adding** - uv updates lock file and installs dependencies.

### Environment Sync

**Sync everything:**
```bash
uv sync --dev
```

**Sync specific cast:**
```bash
uv sync --package <cast-name>
```

**When to sync:**
- After adding dependencies
- After pulling changes
- When dependencies seem out of sync
- Before running tests or dev servers

### Creating New Casts

**Create new cast:**
```bash
uv run act cast -c <cast-name>
```

Example:
```bash
uv run act cast -c email-processor
# Creates: casts/email_processor/ with full structure
```

**Before creating:**
1. Check if cast already exists: `ls casts/ | grep <cast_snake>`
2. Ensure you're in project root
3. Name should be descriptive (kebab-case converts to snake_case)

**After creating:**
- Cast template at `casts/<cast_snake>/`
- Contains: graph.py, modules/, state.py, conditions.py
- Inherits from `casts/base_node.py`

## Quick Reference

| Task | Command |
|------|---------|
| Add package for all casts | `uv add <package> && uv sync` |
| Add package for one cast | `uv add <package> --package <cast> && uv sync --package <cast>` |
| Add dev dependency | `uv add --dev <package> && uv sync --dev` |
| Sync everything | `uv sync --dev` |
| Create new cast | `uv run act cast -c <name>` |
| List available casts | `ls casts/` |
| Check uv status | `uv pip list` |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Forgot to sync after uv add | Run `uv sync` or `uv sync --dev` |
| Cast creation fails | Check if cast already exists, ensure in project root |
| Package not found | Wrong cast name in `--package`, check `ls casts/` |
| Import errors | Run `uv sync --dev` to update environment |

## Act Project Structure

```
project-root/
├── pyproject.toml          # Root dependencies
├── langgraph.json          # LangGraph config
├── casts/
│   ├── base_node.py        # Base node class (extend this)
│   ├── base_graph.py       # Base graph class
│   └── <cast_snake>/       # Your cast (created by act cast)
│       ├── graph.py
│       ├── modules/
│       │   ├── agents/
│       │   ├── nodes.py
│       │   ├── state.py
│       │   ├── conditions.py
│       │   └── tools/      # Tools ONLY here
│       └── tests/
└── scripts/                # Helper scripts
```

## Workspace-Aware Commands

Act uses uv workspaces. Each cast is a workspace member.

**Benefits:**
- Shared dependencies at root (langchain, langgraph)
- Cast-specific dependencies in cast `pyproject.toml`
- Unified lock file for reproducibility

**When to use --package:**
- Cast-specific integration (e.g., only email cast needs sendgrid)
- Experimental dependency (testing in one cast first)
- Heavy dependency (don't bloat all casts)

**When NOT to use --package:**
- Core LangChain/LangGraph dependencies (add to root)
- Used by multiple casts (add to root)
- Part of standard toolkit (add to root)

## Real-World Impact

Following these patterns:
- Correct dependency scope (no bloat)
- Always in-sync environment (no "works on my machine")
- Clean cast creation (follows template structure)
- Fast operations (targeted sync vs full sync)

**Time saved:** 30 seconds correct command vs 10 minutes debugging wrong dependency scope.
