# Context Editing

Clears older tool call outputs when token limits are reached, preserving recent results.

## Basic Usage

```python
# casts.{cast_name}.modules.middlewares
from langchain.agents.middleware import ContextEditingMiddleware, ClearToolUsesEdit

def get_context_editing_middleware():
    return ContextEditingMiddleware(
        edits=[
            ClearToolUsesEdit(
                trigger=100000,  # Token count threshold
                keep=3,          # Keep recent N tool results
            ),
        ],
    )
```

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from .middlewares import get_context_editing_middleware

def set_agent_with_context_editing():
    return create_agent(
        model=get_sample_model(),
        tools=[...],
        middleware=[get_context_editing_middleware()],
    )
```

## Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `trigger` | 100000 | Token count that triggers clearing |
| `keep` | 3 | Recent tool results to preserve |
| `clear_at_least` | 0 | Minimum tokens to reclaim |
| `clear_tool_inputs` | False | Clear tool call arguments too |
| `exclude_tools` | () | Tool names to never clear |
| `placeholder` | "[cleared]" | Replacement text for cleared outputs |
| `token_count_method` | "approximate" | `'approximate'` or `'model'` |
