# StoreBackend

Persistent filesystem backend that stores files in a LangGraph Store, enabling cross-thread persistence.

## Usage (deepagents v0.5+)

`StoreBackend()` is instantiated directly — no factory required.

```python
# casts.{cast_name}.modules.utils
from deepagents.backends import StoreBackend
from langgraph.store.memory import InMemoryStore

def create_store():
    """Create in-memory store. Use DB-backed store in production."""
    return InMemoryStore()

def get_store_backend():
    """Direct StoreBackend instance."""
    return StoreBackend()
```

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .models import get_deep_agent_model
from .utils import create_store, get_store_backend

def set_deep_agent():
    return create_deep_agent(
        model=get_deep_agent_model(),
        backend=get_store_backend(),
        store=create_store(),
    )
```

## How It Works

- Files are stored in the LangGraph Store (key-value persistence layer)
- Persists across threads — files survive when the conversation ends
- Requires a `store` to be passed to `create_deep_agent` (the harness injects it into the backend at runtime)

## Pre-seeding Files

```python
# casts.{cast_name}.modules.utils
from deepagents.backends.utils import create_file_data
from langgraph.store.memory import InMemoryStore

def create_seeded_store():
    """Create store with pre-seeded files."""
    store = InMemoryStore()
    store.put(
        namespace=("filesystem",),
        key="/skills/my-skill/SKILL.md",
        value=create_file_data("---\nname: my-skill\n---\n# Instructions"),
    )
    return store
```

### Binary Files (v0.5+)

StoreBackend supports binary file persistence for PDFs, images, audio, and video:

```python
# casts.{cast_name}.modules.utils
from deepagents.backends.utils import create_file_data
from langgraph.store.memory import InMemoryStore

def create_seeded_store_with_binary():
    """Create store with binary files."""
    store = InMemoryStore()
    with open("reference.pdf", "rb") as f:
        store.put(
            namespace=("filesystem",),
            key="/docs/reference.pdf",
            value=create_file_data(f.read()),
        )
    return store
```

## When to Use

- Files need to persist across multiple threads/conversations
- Storing long-term memories, instructions, or knowledge
- Deployed agents that accumulate knowledge over time
- As a route in `CompositeBackend` for selective persistence

## When NOT to Use

- Ephemeral single-thread tasks → use `StateBackend`
- Need real disk access → use `FilesystemBackend`
- Need code execution → use a sandbox backend
