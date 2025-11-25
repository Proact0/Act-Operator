# Cross-Thread Memory (Store)

## Table of Contents

- [When to Use This Resource](#when-to-use-this-resource)
- [What is Store?](#what-is-store)
- [Store Implementations](#store-implementations)
  - [InMemoryStore (Development)](#inmemorystore-development)
  - [PostgresStore (Production)](#postgresstore-production)
- [Store Operations](#store-operations)
  - [Put (Save Data)](#put-save-data)
  - [Get (Retrieve Data)](#get-retrieve-data)
  - [Search (Query by Namespace)](#search-query-by-namespace)
  - [Delete (Remove Data)](#delete-remove-data)
- [Accessing Store](#accessing-store)
  - [Pattern 1: From Nodes (via runtime)](#pattern-1-from-nodes-via-runtime)
  - [Pattern 2: From Tools (via InjectedToolRuntime)](#pattern-2-from-tools-via-injectedtoolruntime)
- [Common Patterns](#common-patterns)
  - [Pattern 1: User Profile Management](#pattern-1-user-profile-management)
  - [Pattern 2: Knowledge Accumulation](#pattern-2-knowledge-accumulation)
  - [Pattern 3: Shared Context Across Threads](#pattern-3-shared-context-across-threads)
  - [Pattern 4: Session-Specific Temp Data](#pattern-4-session-specific-temp-data)
- [LangMem Integration](#langmem-integration)
- [Configuration with user_id](#configuration-with-user_id)
- [Common Mistakes](#common-mistakes)
- [Memory Location Decision](#memory-location-decision)
- [Production Considerations](#production-considerations)
  - [Cleanup Strategy](#cleanup-strategy)
  - [Namespace Design](#namespace-design)
  - [Performance](#performance)
- [References](#references)

## When to Use This Resource
Read this when implementing memory that persists across different conversations/threads, user preferences, or shared knowledge bases.

## What is Store?

**Store** = Key-value document store for data that persists across threads and conversations.

**Key differences from checkpoints:**
- **Checkpoints:** Conversation state within a thread
- **Store:** Data shared across threads (user prefs, facts, knowledge)

## Store Implementations

### InMemoryStore (Development)
**Storage:** RAM (lost on restart).
**When to use:** Development, testing.

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
graph = builder.compile(checkpointer=checkpointer, store=store)
```

### PostgresStore (Production)
**Storage:** PostgreSQL database.
**When to use:** Production, persistent cross-thread memory.

```python
from langgraph.store.postgres import PostgresStore

store = PostgresStore.from_conn_string(
    "postgresql://user:pass@localhost/dbname"
)

# Async version
from langgraph.store.postgres import AsyncPostgresStore
store = AsyncPostgresStore.from_conn_string(conn_string)

graph = builder.compile(checkpointer=checkpointer, store=store)
```

## Store Operations

### Put (Save Data)
```python
runtime.store.put(
    namespace=("user", "alice-123"),  # Hierarchical namespace
    key="preferences",                 # Unique key within namespace
    value={"theme": "dark", "language": "en"}  # Any JSON-serializable data
)
```

**Namespace best practices:**
- User data: `("user", user_id)`
- Facts: `("facts", topic)`
- Shared knowledge: `("knowledge", domain)`
- Temp data: `("temp", session_id)`

### Get (Retrieve Data)
```python
prefs = runtime.store.get(
    namespace=("user", "alice-123"),
    key="preferences"
)

# Returns: {"theme": "dark", "language": "en"} or None if not found
```

### Search (Query by Namespace)
```python
# Get all items in namespace
user_data = runtime.store.search(
    namespace_prefix=("user", "alice-123")
)

# Returns list of all items under this namespace
for item in user_data:
    print(f"Key: {item.key}, Value: {item.value}")
```

### Delete (Remove Data)
```python
runtime.store.delete(
    namespace=("user", "alice-123"),
    key="preferences"
)
```

## Accessing Store

### Pattern 1: From Nodes (via runtime)

```python
from casts.base_node import BaseNode

class UserPreferencesNode(BaseNode):
    """Loads user preferences from Store."""

    def execute(self, state: dict, runtime=None, **kwargs) -> dict:
        if not runtime or not runtime.store:
            return {"preferences": None}

        user_id = state.get("user_id")
        prefs = runtime.store.get(
            namespace=("user", user_id),
            key="preferences"
        )

        return {"preferences": prefs}
```

**When to use:**
- Need Store access in graph logic
- Complex operations combining multiple Store calls
- State-dependent memory operations

### Pattern 2: From Tools (via InjectedToolRuntime)

```python
from langchain_core.tools import tool, InjectedToolRuntime
from typing import Annotated

@tool
def save_user_preference(
    preference_name: str,
    preference_value: str,
    runtime: Annotated[InjectedToolRuntime, ...]
) -> str:
    """Save a user preference.

    Args:
        preference_name: Name of the preference (e.g., 'theme', 'language')
        preference_value: Value to save
        runtime: Injected runtime (auto-provided by LangGraph)
    """
    if not runtime or not runtime.store:
        return "Store not available"

    # Extract user_id from runtime config
    config = runtime.config
    user_id = config.get("configurable", {}).get("user_id", "default")

    # Save to Store
    current_prefs = runtime.store.get(
        namespace=("user", user_id),
        key="preferences"
    ) or {}

    current_prefs[preference_name] = preference_value

    runtime.store.put(
        namespace=("user", user_id),
        key="preferences",
        value=current_prefs
    )

    return f"Saved {preference_name}={preference_value}"

@tool
def get_user_preference(
    preference_name: str,
    runtime: Annotated[InjectedToolRuntime, ...]
) -> str:
    """Get a user preference."""
    if not runtime or not runtime.store:
        return "Store not available"

    config = runtime.config
    user_id = config.get("configurable", {}).get("user_id", "default")

    prefs = runtime.store.get(
        namespace=("user", user_id),
        key="preferences"
    ) or {}

    return prefs.get(preference_name, "Not set")
```

**When to use:**
- LLM needs to read/write long-term memory
- Reusable across multiple graphs
- User-initiated memory operations

## Common Patterns

### Pattern 1: User Profile Management
```python
# Save user profile
runtime.store.put(
    namespace=("user", user_id),
    key="profile",
    value={
        "name": "Alice",
        "email": "alice@example.com",
        "preferences": {"theme": "dark"}
    }
)

# Update specific preference
profile = runtime.store.get(namespace=("user", user_id), key="profile")
profile["preferences"]["language"] = "es"
runtime.store.put(namespace=("user", user_id), key="profile", value=profile)
```

### Pattern 2: Knowledge Accumulation
```python
# Store facts as agent learns
runtime.store.put(
    namespace=("facts", "world-knowledge"),
    key=f"fact-{uuid4()}",
    value={
        "fact": "Paris is the capital of France",
        "source": "conversation-2024-01-15",
        "confidence": 0.95
    }
)

# Query all facts later
facts = runtime.store.search(namespace_prefix=("facts", "world-knowledge"))
```

### Pattern 3: Shared Context Across Threads
```python
# Team workspace - multiple users, shared knowledge
runtime.store.put(
    namespace=("workspace", "team-alpha"),
    key="project-status",
    value={"phase": "development", "progress": 0.6}
)

# Any team member's thread can access
status = runtime.store.get(
    namespace=("workspace", "team-alpha"),
    key="project-status"
)
```

### Pattern 4: Session-Specific Temp Data
```python
# Temporary data that should persist longer than state but not forever
runtime.store.put(
    namespace=("temp", session_id),
    key="processing-results",
    value=large_intermediate_results
)

# Clean up after session ends
runtime.store.delete(namespace=("temp", session_id), key="processing-results")
```

## LangMem Integration

**LangMem** = Pre-built tools for managing semantic, episodic, and procedural memories.

```python
from langmem import create_langmem_memory

# Create memory instance with Store
memory = create_langmem_memory(store=store)

# Add to tools list
tools = [memory.add_memory, memory.search_memory, other_tools...]
```

**See:** LangMem docs for complete patterns.

## Configuration with user_id

Pass user context via config:

```python
config = {
    "configurable": {
        "thread_id": f"user-{user_id}-{session_id}",  # For checkpoints
        "user_id": user_id  # For Store namespace
    }
}

result = graph.invoke({"input": "..."}, config=config)
```

**In tools:**
```python
user_id = runtime.config.get("configurable", {}).get("user_id")
```

## Common Mistakes

❌ **Confusing Store with checkpoints**
```python
# ❌ Using checkpoints for user preferences (wrong tool)
# Checkpoints are for conversation state, not long-term data

# ✅ Use Store for preferences
runtime.store.put(namespace=("user", user_id), key="prefs", value=...)
```

❌ **Not checking if Store exists**
```python
# ❌ Will crash if Store not configured
prefs = runtime.store.get(...)

# ✅ Check first
if runtime and runtime.store:
    prefs = runtime.store.get(...)
```

❌ **Flat namespace structure**
```python
# ❌ Hard to query/organize
runtime.store.put(namespace=("data",), key="user-123-prefs", value=...)

# ✅ Hierarchical
runtime.store.put(namespace=("user", "123"), key="prefs", value=...)
```

❌ **Storing non-JSON-serializable data**
```python
# ❌ Can't serialize Python objects directly
runtime.store.put(..., value=some_python_object)

# ✅ Convert to dict/list/primitives
runtime.store.put(..., value=obj.to_dict())
```

## Memory Location Decision

**Where should memory logic live?**

```
Simple get/put operations?
└─ Tool (reusable, LLM-accessible)

Complex memory logic + state interaction?
└─ Node (can combine state + Store)

Memory needed by multiple casts?
└─ Tool in casts/[cast]/modules/tools.py

Memory specific to one cast?
└─ Node in casts/[cast_name]/nodes.py
```

## Production Considerations

### Cleanup Strategy
```python
# Periodic cleanup of temp data
def cleanup_temp_data(store, older_than_days=7):
    cutoff = datetime.now() - timedelta(days=older_than_days)
    # Search and delete old temp namespaces
    for item in store.search(namespace_prefix=("temp",)):
        if item.created_at < cutoff:
            store.delete(namespace=item.namespace, key=item.key)
```

### Namespace Design
- **User-scoped:** `("user", user_id, category)`
- **Org-scoped:** `("org", org_id, category)`
- **Global:** `("global", category)`
- **Temp:** `("temp", session_id)`

### Performance
- Use search sparingly (can be slow with many items)
- Cache frequently accessed data in state
- Consider partitioning large namespaces

