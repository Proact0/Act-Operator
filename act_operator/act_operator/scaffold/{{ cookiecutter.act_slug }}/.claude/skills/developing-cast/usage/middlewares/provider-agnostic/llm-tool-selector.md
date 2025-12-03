# LLM Tool Selector

Use an LLM to select relevant tools before calling the main model.

## Basic Usage

```python
# casts.{cast_name}.modules.middlewares
from langchain.agents.middleware import LLMToolSelectorMiddleware

def get_tool_selector_middleware():
    return LLMToolSelectorMiddleware(
        model="gpt-4o-mini",       # Selection model
        max_tools=3,               # Max tools to select
        always_include=["search"], # Always available
    )
```

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from .middlewares import get_tool_selector_middleware

def set_agent_with_tool_selection():
    return create_agent(
        model=get_sample_model(),
        tools=[tool1, tool2, tool3, tool4, tool5, ...],  # Many tools
        middleware=[get_tool_selector_middleware()],
    )
```

## Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `model` | Agent's model | Model for tool selection |
| `max_tools` | None | Max tools to select |
| `always_include` | [] | Tools always included (don't count against max) |
| `system_prompt` | Built-in | Custom selection instructions |

Best for agents with 10+ tools where most aren't relevant per query.
