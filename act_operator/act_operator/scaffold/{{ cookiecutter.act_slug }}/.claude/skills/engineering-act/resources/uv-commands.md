# UV Commands Reference

Quick reference for essential `uv` commands in Act projects.

## Project Management

```bash
# Run Python in project environment
uv run script.py

# Run any command in project environment
uv run [command]
```

## Execution Contexts

**Act CLI Commands** (installed entrypoint)
```bash
uv run act cast -c "My Cast"
uv run act --help
```

**Project Scripts** (in project root)
```bash
uv run script.py
uv run pytest
```

**Skill Scripts** (in .claude/skills/[name]/scripts/)
```bash
python scripts/generate_claude_md.py
python scripts/validate_project.py
# Note: Use 'python', NOT 'uv run' for skill scripts
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
```

## Environment Synchronization

```bash
# Sync ALL cast packages + development dependencies
# - Installs ALL cast packages in the monorepo workspace
# - Installs dev, test, and lint dependency groups
# - Required for full development environment setup
# - Use this after cloning the repository
uv sync --all-packages

# Force reinstall
uv sync --reinstall
```

## Common Workflows

### Environment Synchronization
```bash
# Sync environment - use for:
# - Fresh environment setup after cloning
# - After editing pyproject.toml manually
# - Resolving import errors or package mismatches
uv sync --all-packages
```

**Note:** `uv add/remove` commands automatically update both `pyproject.toml` and `uv.lock`. Use these instead of manual edits.

### Adding LangChain Integrations in Cast Package
```bash
uv add --package {cast_name} langchain-openai        # OpenAI
uv add --package {cast_name} langchain-anthropic     # Anthropic
```

## Best Practices

✓ Use `uv add/remove` for dependency changes (auto-updates pyproject.toml and uv.lock)
✓ Use `uv sync --all-packages` for monorepo development setup
✓ Let `uv run` manage environment activation
✓ Use `uvx` for one-off tool execution

❌ Don't manually edit `uv.lock` (use uv commands)
❌ Don't use `pip` directly in uv projects (use `uv run` if needed)
❌ Don't manually activate venv (use `uv run`)

## Speed Tips

- **Global cache:** uv caches packages globally, reusing across projects
- **Parallel installs:** uv installs dependencies in parallel
- **Copy-on-write:** Uses filesystem features for fast clones
- **Lock file:** uv.lock enables instant dependency resolution

## Auto-sync with uv run

`uv run` automatically checks if environment is up-to-date before running commands, so you typically don't need manual `uv sync` when using `uv run`.
