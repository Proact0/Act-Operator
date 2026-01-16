# LLM Tool Emulator

Emulate tool execution using an LLM for testing purposes.

## Basic Usage

```python
# casts.{cast_name}.modules.middlewares
from langchain.agents.middleware import LLMToolEmulator

def get_tool_emulator_middleware():
    return LLMToolEmulator()  # Emulate all tools
```

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from .middlewares import get_tool_emulator_middleware

def set_test_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[get_weather, send_email],
        middleware=[get_tool_emulator_middleware()],
    )
```

## Selective Emulation

```python
# casts.{cast_name}.modules.middlewares
def get_selective_emulator():
    return LLMToolEmulator(
        tools=["get_weather"],              # Only emulate these
        model="claude-3-5-sonnet-20241022", # Custom emulation model
    )
```

## Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `tools` | None | Tools to emulate (None = all, [] = none) |
| `model` | Agent's model | Model for generating responses |

Use for testing agent behavior without executing real tools.
