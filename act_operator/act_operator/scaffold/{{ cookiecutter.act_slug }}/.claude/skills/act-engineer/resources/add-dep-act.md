# Add Act(Mono-repo) Dependency

Dependencies shared across all casts.

## Production

```bash
uv add langchain-openai
uv add langchain-openai langchain-anthropic  # Multiple
```

## Development Groups

```bash
uv add --dev my-package           # General dev
uv add --group test pytest-mock   # Test specific
uv add --group lint mypy          # Lint specific
```

## Remove

```bash
uv remove langchain-openai
```

## Notes

- `uv add` auto-syncs environment
- Add multiple packages at once for efficiency
- Don't manually edit `uv.lock`

