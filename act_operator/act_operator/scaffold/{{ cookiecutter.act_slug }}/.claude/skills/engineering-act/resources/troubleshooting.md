# Troubleshooting Guide

Common issues and fixes for Act projects.

## Environment Issues

### Environment Out of Sync
**Symptom:** Import errors, missing packages after editing pyproject.toml

**Fix:**
```bash
uv sync --all-extras
```

**Explanation:** Environment doesn't match lockfile. `uv sync` installs missing packages and removes extras.

---

### Module Not Found After Adding Package
**Symptom:** `ModuleNotFoundError` despite running `uv add`

**Checklist:**
1. Did `uv add` complete successfully?
2. Is package in pyproject.toml dependencies?
3. Try explicit sync:
```bash
uv sync
```

---

### Virtual Environment Missing
**Symptom:** No `.venv/` directory

**Fix:**
```bash
uv sync
```

Creates `.venv/` and installs dependencies.

---

## Dependency Issues

### Dependency Conflict
**Symptom:** `uv add` fails with version conflict

**Fix 1:** Upgrade conflicting package
```bash
uv lock --upgrade-package [conflicting-package]
uv sync
```

**Fix 2:** Add with specific version
```bash
uv add "package>=1.0,<2.0"
```

**Fix 3:** Check compatibility
```bash
uv pip show [package]  # Check current version
```

---

### Orphaned Dependencies
**Symptom:** Packages in environment not in pyproject.toml

**Fix:**
```bash
uv sync  # Automatically removes orphans
```

`uv sync` in exact mode (default) removes packages not in lockfile.

---

### Lockfile Out of Date
**Symptom:** Warning about stale lockfile

**Fix:**
```bash
uv lock
uv sync
```

Or just `uv sync` (auto-updates lock if needed).

---

## Cast Issues

### Cast Not Recognized
**Symptom:** Import errors when importing cast

**Checklist:**
1. Is cast directory in `casts/`?
2. Does cast have `__init__.py` and `graph.py`?
3. Is workspace configured in pyproject.toml?

```toml
[tool.uv.workspace]
members = ["casts/*"]
```

---

### Missing Cast Modules
**Symptom:** Cast created but missing modules/

**Fix:** Use script to create complete boilerplate:
```bash
uv run python .claude/skills/engineering-act/scripts/create_cast.py "My Cast"
```

---

### Import Errors in Cast
**Symptom:** Cannot import from `..base_node` or `.modules`

**Checklist:**
1. Correct relative import syntax
   - Base classes: `from ..base_node import BaseNode`
   - Modules: `from .modules.state import MyState`
2. All directories have `__init__.py`
3. Using Python 3.11+ (required for Act)

---

## LangGraph Issues

### LangGraph Server Won't Start
**Symptom:** `langgraph dev` fails

**Fix 1:** Install LangGraph CLI
```bash
uv add --dev langgraph-cli[inmem]
```

**Fix 2:** Use uvx
```bash
uvx --from langgraph-cli langgraph dev
```

---

### Graph Compilation Error
**Symptom:** Error when calling `graph.build()`

**Common causes:**
1. **Missing state field:** Node returns field not in state schema
   - Fix: Add field to state schema
2. **Missing node:** Edge references non-existent node
   - Fix: Check all `add_edge` calls
3. **Circular dependency:** Nodes depend on each other incorrectly
   - Fix: Review node and edge definitions

---

## Python Version Issues

### Wrong Python Version
**Symptom:** Project requires Python 3.11+, but using older version

**Fix:**
```bash
# Install Python 3.11 or newer
uv python install 3.11

# Pin project to 3.11
uv python pin 3.11

# Sync environment
uv sync
```

---

### Multiple Python Versions
**Symptom:** Confusion about which Python is being used

**Check:**
```bash
uv run python --version
```

`uv run` uses project's pinned Python version.

---

## Performance Issues

### Slow Package Installation
**Symptom:** `uv sync` taking longer than expected

**Likely causes:**
1. **First install:** uv caching packages globally (subsequent installs faster)
2. **Network issues:** Downloading from PyPI
3. **Building from source:** Some packages need compilation

**Not usually a problem with uv** - it's typically 10-100x faster than pip.

---

### Large Lockfile
**Symptom:** uv.lock is very large (>10MB)

**Explanation:** Normal for projects with many dependencies. Lockfile includes full dependency tree.

**Not a problem:** uv handles large lockfiles efficiently.

---

## Configuration Issues

### Pre-commit Hooks Not Running
**Symptom:** Commits succeed without linting

**Fix:**
```bash
uv add --dev pre-commit
uv run pre-commit install
```

---

### Ruff Not Linting
**Symptom:** Code not being linted

**Checklist:**
1. Ruff installed?
```bash
uv add --dev ruff
```

2. Configuration in pyproject.toml?
```toml
[tool.ruff]
# Configuration
```

3. Run manually:
```bash
uvx ruff check .
```

---

## Debugging Workflow

**Step 1:** Check project structure
```bash
uv run python .claude/skills/engineering-act/scripts/validate_project.py
```

**Step 2:** Check project info
```bash
uv run python .claude/skills/engineering-act/scripts/project_info.py
```

**Step 3:** Force re-sync
```bash
uv sync --reinstall --all-extras
```

**Step 4:** Check for errors
```bash
uv run python -c "import [your_cast]"
```

---

## Getting Help

**Check validation:**
```bash
uv run python .claude/skills/engineering-act/scripts/validate_project.py
```

**Show project info:**
```bash
uv run python .claude/skills/engineering-act/scripts/project_info.py --packages
```

**LangGraph docs:**
- https://langchain-ai.github.io/langgraph/

**uv docs:**
- https://docs.astral.sh/uv/

---

## Prevention

✓ Run validation regularly: `validate_project.py`
✓ Keep environment synced: `uv sync` after changes
✓ Use scripts for cast creation: `create_cast.py`
✓ Check project status: `project_info.py`
✓ Commit uv.lock to version control
✓ Use `uv run` for command execution

❌ Don't manually edit uv.lock
❌ Don't use pip instead of uv
❌ Don't skip validation
❌ Don't create casts manually
