# Add Cast Package Dependency

Dependencies specific to a single cast.

## Before Adding

**Check CLAUDE.md files:**
- **Root `/CLAUDE.md`**: Review Casts table to verify cast exists
- **Cast `/casts/{cast_slug}/CLAUDE.md`**: Check Technology Stack section
  - Verify dependency isn't already listed
  - Understand current dependencies before adding new ones

## When to Use

- Cast needs a specific provider (OpenAI, Anthropic, etc.)
- Cast uses external tools (Tavily, SerpAPI, etc.)
- Avoid adding to monorepo if only one cast needs it

## Command

```bash
uv add --package {cast_name} langchain-openai
uv add --package {cast_name} langchain-openai langchain-anthropic  # Multiple
```

## After Adding

1. Verify installation: `uv sync --all-packages`
2. Update `/casts/{cast_slug}/CLAUDE.md` Technology Stack section
3. Commit both the dependency file and CLAUDE.md update

## Example

```bash
# Check technology stack first
cat casts/my_graph/CLAUDE.md | grep -A 10 "Technology Stack"

# Add to my_graph cast
uv add --package my_graph langchain-openai
uv add --package my_graph tavily-python

# Sync environment
uv sync --all-packages

# Update casts/my_graph/CLAUDE.md Technology Stack section
```

## Remove

```bash
uv remove --package {cast_name} langchain-openai
```
