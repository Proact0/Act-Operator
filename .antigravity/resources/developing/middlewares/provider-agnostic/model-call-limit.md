# Model Call Limit

Limit model calls to prevent infinite loops or excessive costs.

## Basic Usage

```python
# casts.{cast_name}.modules.middlewares
from langchain.agents.middleware import ModelCallLimitMiddleware

def get_model_limit_middleware():
    return ModelCallLimitMiddleware(
        thread_limit=10,      # Max across all runs in thread
        run_limit=5,          # Max per single invocation
        exit_behavior="end",  # 'end' or 'error'
    )
```

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from .middlewares import get_model_limit_middleware

def set_limited_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[...],
        middleware=[get_model_limit_middleware()],
    )
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `thread_limit` | None | Max calls across all runs in thread |
| `run_limit` | None | Max calls per invocation |
| `exit_behavior` | "end" | `'end'` (graceful) or `'error'` (exception) |
