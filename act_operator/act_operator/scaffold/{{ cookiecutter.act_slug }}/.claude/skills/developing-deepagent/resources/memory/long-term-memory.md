# Long-Term Memory

Enable deep agents to persist information across threads using a CompositeBackend with StoreBackend.

## Overview

By default, the deep agent's filesystem is transient. Long-term memory uses a `CompositeBackend` to route `/memories/` to persistent storage.

```
Deep Agent ──> Path Router
                ├── /memories/*  → StoreBackend (persistent across threads)
                └── other        → StateBackend (ephemeral, single thread)
```

## Setup

```python
# casts.{cast_name}.modules.utils
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver


def get_memory_backend():
    """Backend with persistent /memories/ route."""
    return CompositeBackend(
        default=StateBackend(),
        routes={"/memories/": StoreBackend()},
    )


def create_store():
    """In-memory store. Use a DB-backed store in production."""
    return InMemoryStore()


def create_checkpointer():
    return MemorySaver()
```

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent

from .models import get_deep_agent_model
from .utils import get_memory_backend, create_store, create_checkpointer


def set_deep_agent():
    return create_deep_agent(
        model=get_deep_agent_model(),
        backend=get_memory_backend(),
        store=create_store(),
        checkpointer=create_checkpointer(),
    )
```

## How It Works

- Files under `/memories/` are saved to the LangGraph Store and **survive across threads**
- Files without the `/memories/` prefix remain in ephemeral state storage
- The agent can read/write to both areas using the same filesystem tools

## AGENTS.md Pattern

Deep agents use an `AGENTS.md` file (similar to `CLAUDE.md`) for persistent instructions:

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .utils import create_filesystem_backend

def set_deep_agent_with_memory():
    return create_deep_agent(
        backend=create_filesystem_backend("/path/to/project"),
        memory=["./AGENTS.md"],  # Agent reads this for context
    )
```

## Key Notes

- `InMemoryStore()` is good for local development; omit `store` for LangSmith Deployment
- The `/memories/` path prefix is a convention — you can use any prefix
- Longer prefixes win: `/memories/projects/` can override `/memories/`
- StoreBackend routes require the agent runtime to provide a store
