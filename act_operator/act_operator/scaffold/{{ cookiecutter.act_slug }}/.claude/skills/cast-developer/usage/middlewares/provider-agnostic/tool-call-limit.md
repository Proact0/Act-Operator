# Tool Call Limit

Limit tool calls globally or per specific tool.

## Basic Usage

```python
# casts.{cast_name}.modules.middlewares
from langchain.agents.middleware import ToolCallLimitMiddleware

def get_tool_limit_middlewares():
    return [
        ToolCallLimitMiddleware(thread_limit=20, run_limit=10),  # Global
        ToolCallLimitMiddleware(tool_name="search", thread_limit=5, run_limit=3),  # Specific
    ]
```

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from .middlewares import get_tool_limit_middlewares

def set_limited_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[...],
        middleware=get_tool_limit_middlewares(),
    )
```

## Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `tool_name` | None | Specific tool (None = all tools) |
| `thread_limit` | None | Max across all runs in thread |
| `run_limit` | None | Max per invocation |
| `exit_behavior` | "continue" | `'continue'`, `'error'`, `'end'` |

**Note:** At least one of `thread_limit` or `run_limit` must be specified.

## Exit Behaviors

| Behavior | Description |
|----------|-------------|
| `continue` | Block exceeded calls with error, let agent continue |
| `error` | Raise `ToolCallLimitExceededError` immediately |
| `end` | Stop with ToolMessage (single-tool only) |
