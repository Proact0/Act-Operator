---
name: engineering-act
description: Use when managing Act project dependencies, environment setup, cast scaffolding, or troubleshooting build issues - automates project operations through scripts
---

# Engineering Act Skill

Automates Act project setup, dependency management, and cast scaffolding. **Scripts do the work, not Claude.**

## Quick Commands

### Dependency Management
```bash
# Add packages
uv add langchain-openai langchain-anthropic
uv add --dev pytest-asyncio

# Remove packages
uv remove langchain-openai

# Sync environment
uv sync              # Production dependencies
uv sync --all-extras # Include dev/test/lint groups
```

### Cast Operations
```bash
# Create new cast (basic structure)
uv run act cast -c "My New Cast"

# Create cast with full boilerplate (use script)
uv run python .claude/skills/engineering-act/scripts/create_cast.py "My New Cast"
```

### Project Status
```bash
# Show project info
uv run python .claude/skills/engineering-act/scripts/project_info.py

# Validate project structure
uv run python .claude/skills/engineering-act/scripts/validate_project.py

# List installed packages
uv pip list
```

## Scripts Index

All scripts in `.claude/skills/engineering-act/scripts/`:

| Script | Purpose | Saves |
|--------|---------|-------|
| `create_cast.py` | Create cast with full boilerplate modules | ~300 tokens |
| `project_info.py` | Display project status (packages, casts, Python version) | ~150 tokens |
| `validate_project.py` | Check project structure and configuration | ~200 tokens |
| `batch_dependencies.py` | Add/remove multiple packages at once | ~100 tokens |
| `sync_check.py` | Sync environment and show changes | ~100 tokens |

**Usage Pattern:**
```bash
uv run python .claude/skills/engineering-act/scripts/[SCRIPT_NAME].py --help
```

## Quick Troubleshooting

**Environment out of sync?**
```bash
uv sync --all-extras
```

**Dependency conflict?**
```bash
uv lock --upgrade-package [package-name]
uv sync
```

**Cast not recognized?**
Check `pyproject.toml` has cast in workspace members:
```toml
[tool.uv.workspace]
members = ["casts/*"]
```

**More issues?** See `resources/troubleshooting.md`

## Resources

- **`resources/uv-commands.md`** - Essential uv command reference
- **`resources/cast-structure.md`** - Cast directory layout guide
- **`resources/troubleshooting.md`** - Common issues and fixes

## Workflow Integration

**After architecting-act (CLAUDE.md created):**
```bash
# If new dependencies needed
uv add langchain-experimental

# Create new cast for implementation
uv run python .claude/skills/engineering-act/scripts/create_cast.py "MyGraph"

# Proceed to developing-cast
/developing-cast
```

**Before developing-cast:**
- Environment synced: `uv sync --all-extras`
- Cast structure created: Use `create_cast.py`
- Dependencies installed: `uv add [packages]`

## Common Patterns

### Adding LangChain Integrations
```bash
# OpenAI
uv add langchain-openai

# Anthropic
uv add langchain-anthropic

# Google
uv add langchain-google-genai

# Community tools
uv add langchain-community
```

### Development Setup
```bash
# Sync all dependency groups
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install
```

### Running LangGraph
```bash
# Start LangGraph server
uvx --from langgraph-cli langgraph dev
```

## Best Practices

✓ **Always sync after adding dependencies**: `uv add` auto-syncs, but use `uv sync` if editing pyproject.toml manually

✓ **Use scripts for repetitive tasks**: Don't manually create cast modules - use `create_cast.py`

✓ **Check project status frequently**: `project_info.py` shows everything at a glance

✓ **Validate before committing**: Run `validate_project.py` to catch issues early

❌ **Don't manually edit uv.lock**: Always use `uv` commands

❌ **Don't create casts without scripts**: Manual setup is error-prone

❌ **Don't skip validation**: Broken structure causes runtime errors

## Anti-Patterns

### ❌ Manual Cast File Creation
**Problem:** Creating modules/state.py, modules/agents.py manually
**Solution:** `uv run python .claude/skills/engineering-act/scripts/create_cast.py "CastName"`

### ❌ Multiple uv add Commands
**Problem:** `uv add pkg1 && uv add pkg2 && uv add pkg3`
**Solution:** `uv add pkg1 pkg2 pkg3` OR use `batch_dependencies.py`

### ❌ Forgetting to Sync
**Problem:** pyproject.toml edited, environment not updated
**Solution:** `uv sync` (or use `sync_check.py` to see what changes)

---

**Remember:** This skill AUTOMATES repetitive operations. If you're typing the same thing twice, there's probably a script for it.
