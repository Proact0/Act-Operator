# Cross-Thread Persistence

Share state between agent threads and between the main agent and its subagents.

## Contents

- Thread-to-Thread Persistence
- Agent-to-Subagent State Sharing
- Pre-seeding Persistent Store
- Multiple Persistent Routes
- Persistence Lifecycle
- Key Notes

## Thread-to-Thread Persistence

Using `CompositeBackend` with `StoreBackend`, files stored under the persistent route survive across threads.

```python
# casts.{cast_name}.modules.utils
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore


def get_persistent_backend():
    """Backend with persistent /memories/ route."""
    return CompositeBackend(
        default=StateBackend(),
        routes={"/memories/": StoreBackend()},
    )


def create_store():
    return InMemoryStore()
```

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent

from .utils import get_persistent_backend, create_store, create_checkpointer


def set_deep_agent():
    return create_deep_agent(
        backend=get_persistent_backend(),
        store=create_store(),
        checkpointer=create_checkpointer(),
    )
```

## Agent-to-Subagent State Sharing

By default, subagents have their own isolated context. To share state, use middleware:

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .tools import web_search
from .middlewares import shared_state_middleware

def get_subagents():
    return [
        {
            "name": "researcher",
            "description": "Research specialist",
            "system_prompt": "You are a researcher.",
            "tools": [web_search],
            "middleware": [shared_state_middleware],  # Enables state sharing
        }
    ]

def set_deep_agent():
    return create_deep_agent(
        model=get_deep_agent_model(),
        subagents=get_subagents(),
    )
```

## Pre-seeding Persistent Store

```python
# casts.{cast_name}.modules.utils
from deepagents.backends.utils import create_file_data
from langgraph.store.memory import InMemoryStore

def create_seeded_store():
    """Create store with pre-seeded persistent data."""
    store = InMemoryStore()
    store.put(
        namespace=("filesystem",),
        key="/memories/project-context.md",
        value=create_file_data("# Project Context\n\nThis project uses FastAPI..."),
    )
    return store
```

## Multiple Persistent Routes

```python
# casts.{cast_name}.modules.utils
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend, FilesystemBackend


def get_multi_route_backend():
    """Route different data types to different backends."""
    return CompositeBackend(
        default=StateBackend(),
        routes={
            "/memories/": StoreBackend(),
            "/knowledge/": StoreBackend(),
            "/project/": FilesystemBackend(root_dir=".", virtual_mode=True),
        },
    )
```

## Persistence Lifecycle

```
Thread 1                          Thread 2
─────────                         ─────────
Write /workspace/temp.md          /workspace/temp.md → NOT FOUND
Write /memories/prefs.md          /memories/prefs.md → FOUND ✓
Thread ends                       Thread ends
```

## Key Notes

- Only files under persistent routes (e.g., `/memories/`) survive across threads
- Ephemeral files (under `StateBackend`) are lost when the thread ends
- The `store` parameter must be provided to `create_deep_agent` for `StoreBackend` to work
- For LangSmith Deployment, omit `store` — the platform provides one automatically
