# Summarization

Automatically summarize conversation history when approaching token limits.

## Basic Usage

```python
# casts.{cast_name}.modules.middlewares
from langchain.agents.middleware import SummarizationMiddleware

def get_summarization_middleware():
    return SummarizationMiddleware(
        model="gpt-4o-mini",           # Model for summarization
        trigger={"tokens": 4000},       # When to trigger
        keep={"messages": 20},          # What to preserve
    )
```

## Trigger Conditions

Single condition (AND logic) or list of conditions (OR logic):

```python
# Single: trigger if tokens >= 4000 AND messages >= 10
trigger={"tokens": 4000, "messages": 10}

# Multiple: trigger if (tokens >= 5000 AND messages >= 3) OR (tokens >= 3000 AND messages >= 6)
trigger=[
    {"tokens": 5000, "messages": 3},
    {"tokens": 3000, "messages": 6},
]

# Fractional: trigger at 80% of model's context size
trigger={"fraction": 0.8}
```

## Keep Conditions

Specify exactly one:

```python
keep={"messages": 20}    # Keep last 20 messages
keep={"tokens": 2000}    # Keep ~2000 tokens
keep={"fraction": 0.3}   # Keep 30% of context
```

## Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `model` | Required | Model for generating summaries |
| `trigger` | None | Conditions to trigger summarization |
| `keep` | `{messages: 20}` | What to preserve after summarization |
| `summary_prompt` | Built-in | Custom summarization prompt |
| `trim_tokens_to_summarize` | 4000 | Max tokens for summary generation |
