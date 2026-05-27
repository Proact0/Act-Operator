# create_deep_agent

Factory function that creates a compiled deep agent graph.

## Contents

- Signature
- Module Separation Pattern
- Basic Agent Setup
- Full Configuration
- Key Constraints

## Signature

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent

create_deep_agent(
    name: str | None = None,
    model: str | BaseChatModel | None = None,
    tools: Sequence[BaseTool | Callable | dict[str, Any]] | None = None,
    *,
    system_prompt: str | SystemMessage | None = None,
    middleware: list[Middleware] | None = None,
    subagents: list[dict | CompiledSubAgent] | None = None,
    backend: BackendProtocol | None = None,
    interrupt_on: dict[str, bool | dict] | None = None,
    skills: list[str] | None = None,
    store: BaseStore | None = None,
    checkpointer: BaseCheckpointSaver | None = None,
) -> CompiledStateGraph
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str \| None` | `None` | Agent name for tracing and identification |
| `model` | `str \| BaseChatModel \| None` | `None` | LLM model string (e.g. `"claude-sonnet-4-5-20250929"`) or initialized model instance |
| `tools` | `Sequence[BaseTool \| Callable \| dict]` | `None` | Custom tools the agent can use |
| `system_prompt` | `str \| SystemMessage \| None` | `None` | Custom instructions prepended to built-in prompt |
| `middleware` | `list[Middleware] \| None` | `None` | Middleware for retry, guardrails, limits, etc. |
| `subagents` | `list[dict \| CompiledSubAgent]` | `None` | Custom subagents for task delegation |
| `backend` | `BackendProtocol \| None` | `StateBackend()` | Virtual filesystem backend instance (v0.5+ direct instantiation) |
| `interrupt_on` | `dict[str, bool \| dict]` | `None` | HITL configuration per tool |
| `skills` | `list[str]` | `None` | Skill source paths (relative to backend root) |
| `store` | `BaseStore \| None` | `None` | LangGraph Store for persistent storage |
| `checkpointer` | `BaseCheckpointSaver \| None` | `None` | Required for HITL and thread persistence |

## Module Separation Pattern

Separate components into dedicated modules:

```python
# casts.{cast_name}.modules.models
from langchain_anthropic import ChatAnthropic

def get_deep_agent_model():
    return ChatAnthropic(model="claude-sonnet-4-5-20250929")
```

```python
# casts.{cast_name}.modules.tools
from langchain.tools import tool

@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"
```

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .models import get_deep_agent_model
from .tools import search

def set_deep_agent():
    return create_deep_agent(
        name="{{ cookiecutter.cast_slug }}",
        model=get_deep_agent_model(),
        tools=[search],
        system_prompt="You are a helpful assistant.",
    )
```

## Basic Agent Setup

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .models import get_deep_agent_model

def set_deep_agent():
    return create_deep_agent(
        model=get_deep_agent_model(),
        system_prompt="You are a helpful research assistant.",
    )
```

## Full Configuration

Backends, store, and checkpointer are direct instances (deepagents v0.5+):

```python
# casts.{cast_name}.modules.utils
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver


def get_composite_backend():
    """Backend with ephemeral workspace + persistent memory."""
    return CompositeBackend(
        default=StateBackend(),
        routes={"/memories/": StoreBackend()},
    )


def create_store():
    """In-memory store. Use a DB-backed store in production."""
    return InMemoryStore()


def create_checkpointer():
    """In-memory checkpointer. Use PostgresSaver in production."""
    return MemorySaver()
```

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent

from .models import get_deep_agent_model
from .tools import get_tools
from .utils import get_composite_backend, create_store, create_checkpointer


def get_subagents():
    return [
        {
            "name": "writer",
            "description": "Writes polished reports",
            "system_prompt": "You are a technical writer.",
            "tools": [],
        }
    ]


def set_deep_agent():
    return create_deep_agent(
        name="{{ cookiecutter.cast_slug }}",
        model=get_deep_agent_model(),
        tools=get_tools(),
        system_prompt="You are an expert researcher.",
        middleware=[],
        subagents=get_subagents(),
        backend=get_composite_backend(),
        interrupt_on={
            "write_file": True,
            "my_search_tool": {"allowed_decisions": ["approve", "reject"]},
        },
        skills=["./skills/"],
        store=create_store(),
        checkpointer=create_checkpointer(),
    )
```

## Key Constraints

- `system_prompt` is prepended to the built-in deep agent prompt (planning, filesystem, subagent instructions)
- `backend` accepts a direct instance: `StateBackend()`, `StoreBackend()`, `CompositeBackend(...)`, `FilesystemBackend(...)`, or a custom backend instance.
- `checkpointer` is **required** when using `interrupt_on` or when you need thread persistence
- `store` is **required** when using `StoreBackend` for persistent cross-thread storage
- When deploying to LangSmith Deployment, omit `store` — the platform provisions one automatically
