# To-Do List

Equip agents with task planning and tracking for multi-step tasks.

## Basic Usage

```python
# casts.{cast_name}.modules.middlewares
from langchain.agents.middleware import TodoListMiddleware

def get_todo_middleware():
    return TodoListMiddleware()
```

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from .middlewares import get_todo_middleware

def set_planning_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[read_file, write_file, run_tests],
        middleware=[get_todo_middleware()],
    )
```

Automatically provides agents with a `write_todos` tool and system prompts for task planning.

## Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `system_prompt` | Built-in | Custom guidance for todo usage |
| `tool_description` | Built-in | Custom `write_todos` tool description |
