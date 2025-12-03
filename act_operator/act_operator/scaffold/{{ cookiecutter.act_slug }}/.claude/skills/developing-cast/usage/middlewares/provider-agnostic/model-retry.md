# Model Retry

Automatically retry failed model calls with exponential backoff.

## Basic Usage

```python
# casts.{cast_name}.modules.middlewares
from langchain.agents.middleware import ModelRetryMiddleware

def get_model_retry_middleware():
    return ModelRetryMiddleware(
        max_retries=3,
        backoff_factor=2.0,
        initial_delay=1.0,
    )
```

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from .middlewares import get_model_retry_middleware

def set_resilient_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[...],
        middleware=[get_model_retry_middleware()],
    )
```

## Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_retries` | 2 | Retry attempts after initial call |
| `retry_on` | `(Exception,)` | Exception types or callable filter |
| `on_failure` | "continue" | `'continue'`, `'error'`, or callable |
| `backoff_factor` | 2.0 | Exponential multiplier (0.0 = constant) |
| `initial_delay` | 1.0 | First retry delay (seconds) |
| `max_delay` | 60.0 | Maximum delay cap |
| `jitter` | True | Add ±25% random variation |

## Custom Exception Filter

```python
# casts.{cast_name}.modules.middlewares
def should_retry(error: Exception) -> bool:
    if hasattr(error, "status_code"):
        return error.status_code in (429, 503)  # Rate limit, service unavailable
    return False

def get_selective_retry_middleware():
    return ModelRetryMiddleware(
        max_retries=4,
        retry_on=should_retry,
        on_failure="error",  # Raise after exhausting retries
    )
```
