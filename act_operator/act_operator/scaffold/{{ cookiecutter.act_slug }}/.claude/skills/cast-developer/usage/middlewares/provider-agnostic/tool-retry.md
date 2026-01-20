# Tool Retry

Automatically retry failed tool calls with exponential backoff.

## Basic Usage

```python
# casts.{cast_name}.modules.middlewares
from langchain.agents.middleware import ToolRetryMiddleware

def get_tool_retry_middleware():
    return ToolRetryMiddleware(
        max_retries=3,
        backoff_factor=2.0,
        initial_delay=1.0,
    )
```

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from .middlewares import get_tool_retry_middleware

def set_resilient_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[...],
        middleware=[get_tool_retry_middleware()],
    )
```

## Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_retries` | 2 | Retry attempts after initial call |
| `tools` | None | Specific tools to apply (None = all) |
| `retry_on` | `(Exception,)` | Exception types or callable filter |
| `on_failure` | "return_message" | `'return_message'`, `'raise'`, or callable |
| `backoff_factor` | 2.0 | Exponential multiplier |
| `initial_delay` | 1.0 | First retry delay (seconds) |
| `max_delay` | 60.0 | Maximum delay cap |
| `jitter` | True | Add ±25% random variation |

## Selective Tool Retry

```python
# casts.{cast_name}.modules.middlewares
def get_api_retry_middleware():
    return ToolRetryMiddleware(
        max_retries=3,
        tools=["api_tool", "external_service"],  # Only these tools
        retry_on=(ConnectionError, TimeoutError),
        on_failure="return_message",
    )
```
