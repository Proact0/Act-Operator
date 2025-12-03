# Add Cast Package Dependency

Dependencies specific to a single cast.

## When to Use

- Cast needs a specific provider (OpenAI, Anthropic, etc.)
- Cast uses external tools (Tavily, SerpAPI, etc.)
- Avoid adding to monorepo if only one cast needs it

## Command

```bash
uv add --package {cast_name} langchain-openai
uv add --package {cast_name} langchain-openai langchain-anthropic  # Multiple
```

## Example

```bash
# Add to my_graph cast
uv add --package my_graph langchain-openai
uv add --package my_graph tavily-python
```

## Remove

```bash
uv remove --package {cast_name} langchain-openai
```
