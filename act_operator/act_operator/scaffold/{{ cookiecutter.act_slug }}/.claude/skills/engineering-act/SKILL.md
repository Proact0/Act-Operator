---
name: engineering-act
description: Automates Act project operations - dependency management with uv, environment setup, cast scaffolding, and build troubleshooting. Use when setting up projects, adding packages, creating casts, or resolving build issues.
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
uv sync              # Production dependencies only
uv sync --all-packages --dev # Syncs all casts + dev dependencies
```

### Cast Operations
```bash
# Create new cast (basic structure)
uv run act cast -c "My New Cast"

# Create cast with full boilerplate (use script)
python scripts/create_cast.py "My New Cast"
```

### Project Status
```bash
# Show project info
python scripts/project_info.py

# Validate project structure
python scripts/validate_project.py

# List installed packages
uv pip list
```

## Scripts Index

All scripts in `.claude/skills/engineering-act/scripts/`:

| Script | Purpose |
|--------|---------|
| `create_cast.py` | Create cast with full boilerplate modules |
| `project_info.py` | Display project status (packages, casts, version) |
| `validate_project.py` | Check project structure and configuration |
| `batch_dependencies.py` | Add/remove multiple packages at once |
| `sync_check.py` | Sync environment and show changes |

**Usage Pattern:**
```bash
python scripts/[SCRIPT_NAME].py --help
```

## Quick Troubleshooting

**Symptom:** Import errors, missing packages after editing pyproject.toml

**Fix:**
```bash
uv sync --all-packages
```

**Explanation:** Environment doesn't match lockfile. `uv sync` installs missing packages and removes extras.

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
python scripts/create_cast.py "MyGraph"

# Proceed to developing-cast
/developing-cast
```

**Before developing-cast:**
- Environment synced: `uv sync --all-packages --dev` # Syncs all casts + dev dependencies
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
# Sync all dependency groups (all casts + dev dependencies)
uv sync --all-packages --dev

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
**Solution:** `python scripts/create_cast.py "CastName"`

### ❌ Multiple uv add Commands
**Problem:** `uv add pkg1 && uv add pkg2 && uv add pkg3`
**Solution:** `uv add pkg1 pkg2 pkg3` OR use `batch_dependencies.py`

### ❌ Forgetting to Sync
**Problem:** pyproject.toml edited, environment not updated
**Solution:** `uv sync` (or use `sync_check.py` to see what changes)

---

**Remember:** This skill AUTOMATES repetitive operations. If you're typing the same thing twice, there's probably a script for it.
