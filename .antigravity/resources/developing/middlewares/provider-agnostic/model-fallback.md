# Model Fallback

Automatically fallback to alternative models when primary model fails.

## Basic Usage

```python
# casts.{cast_name}.modules.middlewares
from langchain.agents.middleware import ModelFallbackMiddleware

def get_model_fallback_middleware():
    return ModelFallbackMiddleware(
        "gpt-4o-mini",                    # First fallback
        "claude-3-5-sonnet-20241022",     # Second fallback
    )
```

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from .middlewares import get_model_fallback_middleware

def set_resilient_agent():
    return create_agent(
        model=get_sample_model(),  # Primary model
        tools=[...],
        middleware=[get_model_fallback_middleware()],
    )
```

## Parameters

| Parameter | Description |
|-----------|-------------|
| `first_model` | First fallback model (string or BaseChatModel) |
| `*additional_models` | Additional fallbacks in order |
