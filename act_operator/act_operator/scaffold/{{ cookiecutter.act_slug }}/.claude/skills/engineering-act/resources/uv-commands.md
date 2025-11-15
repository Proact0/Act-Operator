# UV Commands Reference

Quick reference for essential `uv` commands in Act projects.

## Project Management

```bash
# Run Python in project environment
uv run script.py

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
uv add --group test pytest            # Specific group

# Remove dependency
uv remove package-name

# Upgrade dependency
uv add --upgrade package-name
uv lock --upgrade-package package-name      # Just update lock
```

## Environment Synchronization

```bash
# Sync with all dependency groups (dev, test, lint)
uv sync --all-packages --dev

# Just update lockfile (no install)
uv lock

# Force reinstall
uv sync --reinstall
```

## Common Workflows

### Fresh Environment Setup
```bash
uv sync --all-packages --dev      # Sync all groups
```

### After Editing pyproject.toml
```bash
uv lock    # Update lockfile
uv sync --all-packages --dev    # Sync environment
```

### Adding LangChain Integrations in Cast Package
```bash
uv add --package {cast_name} langchain-openai        # OpenAI
uv add --package {cast_name} langchain-anthropic     # Anthropic
```

## Best Practices

✓ Use `uv add/remove` for dependency changes (auto-updates lock + sync)
✓ Use `uv sync --all-pacakges --dev` for monorepo development setup
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
