# Environment Sync

## Commands

```bash
# Development (all casts + dev dependencies)
uv sync --all-packages

# Production (no dev dependencies)
uv sync --all-packages --no-dev

# Force reinstall
uv sync --reinstall --all-packages
```

## When to Sync

- After cloning repository
- After manual `pyproject.toml` edit
- When import errors occur
- Fresh environment setup

## Auto-sync

`uv run` automatically checks environment before execution.

Manual sync rarely needed when using:
- `uv add` / `uv remove` (auto-syncs)
- `uv run` commands

## Troubleshooting

**Module not found:**
```bash
uv sync --all-packages
```

**Dependency conflict:**
```bash
uv add "package>=1.0,<2.0"  # Specify version
```

**Environment broken:**
```bash
uv sync --reinstall --all-packages
```

