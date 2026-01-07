# Long-Term Memory Storage

Long-term memory persists across sessions using LangGraph Store.

## Store Structure

Memories are organized by:
- **Namespace**: Hierarchical path (e.g., `(user_id, context)`)
- **Key**: Unique identifier within namespace

```python
# casts.{cast_name}.modules.utils
from langgraph.store.memory import InMemoryStore

def create_memory_store():
    """Create in-memory store. Use DB-backed store in production."""
    return InMemoryStore()

def create_searchable_store(embed_fn, dims: int = 1536):
    """Create store with vector search support."""
    return InMemoryStore(index={"embed": embed_fn, "dims": dims})
```

## Basic Operations

```python
# casts.{cast_name}.modules.utils
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
user_id = "user_123"
namespace = (user_id, "preferences")

# Write
store.put(namespace, "settings", {"theme": "dark", "language": "en"})

# Read
item = store.get(namespace, "settings")
value = item.value if item else None

# Search (requires index)
items = store.search(namespace, filter={"theme": "dark"}, query="user preferences")
```

## Integrate with Agent

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from .utils import create_memory_store

store = create_memory_store()

def set_agent_with_store():
    return create_agent(
        model=get_sample_model(),
        tools=[...],
        store=store,
    )
```
