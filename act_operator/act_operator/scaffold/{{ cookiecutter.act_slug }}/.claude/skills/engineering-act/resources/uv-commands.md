# UV Commands Reference

Quick reference for essential `uv` commands in Act projects.

## Project Management

```bash
# Initialize new project (rarely needed - use `act new`)
uv init my-project

# Run Python in project environment
uv run python script.py
uv run python -m module

# Run any command in project environment
uv run [command]
```

## Dependency Management

```bash
# Add production dependency
uv add package-name
uv add langchain-openai langchain-anthropic  # Multiple

# Add dev dependency
uv add --dev pytest pytest-asyncio
uv add --dev --group test pytest            # Specific group

# Remove dependency
uv remove package-name

# Upgrade dependency
uv add --upgrade package-name
uv lock --upgrade-package package-name      # Just update lock
```

## Environment Synchronization

```bash
# Sync with lockfile (installs missing, removes extra)
uv sync

# Sync with all dependency groups (dev, test, lint)
uv sync --all-extras

# Just update lockfile (no install)
uv lock

# Force reinstall
uv sync --reinstall
```

## Package Information

```bash
# List installed packages
uv pip list

# Show package details
uv pip show package-name

# Search packages
uv pip search query
```

## Python Version Management

```bash
# Install Python version
uv python install 3.12

# List available Python versions
uv python list

# Pin project to Python version
uv python pin 3.12
```

## Tool Execution

```bash
# Run tool without installing (uvx)
uvx ruff check
uvx black .
uvx pytest

# Install tool globally
uv tool install ruff
uv tool install black
```

## Common Workflows

### Fresh Environment Setup
```bash
uv sync --all-extras      # Sync all groups
uv run pre-commit install # Setup hooks
```

### After Editing pyproject.toml
```bash
uv lock    # Update lockfile
uv sync    # Sync environment
```

### Adding LangChain Integrations
```bash
uv add langchain-openai        # OpenAI
uv add langchain-anthropic     # Anthropic
uv add langchain-google-genai  # Google
uv add langchain-community     # Community tools
```

## Key Differences from pip

| Task | pip | uv |
|------|-----|-----|
| Install package | `pip install pkg` | `uv add pkg` |
| Remove package | `pip uninstall pkg` | `uv remove pkg` |
| List packages | `pip list` | `uv pip list` |
| Run in env | `python script.py` | `uv run python script.py` |
| Freeze deps | `pip freeze > requirements.txt` | `uv lock` (creates uv.lock) |

## Best Practices

✓ Use `uv add/remove` for dependency changes (auto-updates lock + sync)
✓ Use `uv sync --all-extras` for development setup
✓ Let `uv run` manage environment activation
✓ Use `uv.lock` for reproducible builds (commit to git)
✓ Use `uvx` for one-off tool execution

❌ Don't manually edit `uv.lock` (use uv commands)
❌ Don't use `pip` directly in uv projects (use `uv pip` if needed)
❌ Don't manually activate venv (use `uv run`)

## Speed Tips

- **Global cache:** uv caches packages globally, reusing across projects
- **Parallel installs:** uv installs dependencies in parallel
- **Copy-on-write:** Uses filesystem features for fast clones
- **Lock file:** uv.lock enables instant dependency resolution

## Auto-sync with uv run

`uv run` automatically checks if environment is up-to-date before running commands, so you typically don't need manual `uv sync` when using `uv run`.
