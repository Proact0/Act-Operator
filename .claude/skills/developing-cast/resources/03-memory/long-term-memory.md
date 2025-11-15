# Long-Term Memory (Store)

## When to Use This Resource

Read this for cross-session memory (user preferences, learned facts, persistent knowledge).

## Key Concept

**Store:** Persistent document store accessible across different graph runs and threads.

**Namespace:** Organizational structure for memories (e.g., `("user", user_id)`).

## Accessing Store

### In Node (via Runtime)

```python
from casts.base_node import BaseNode
from langgraph.runtime import Runtime

class MemoryNode(BaseNode):
    def execute(
        self,
        state: AgentState,
        runtime: Runtime = None,
        **kwargs
    ) -> dict:
        if not runtime or not runtime.store:
            return {}

        user_id = state.get("user_id")
        namespace = ("user", user_id)

        # Get memories
        memories = runtime.store.search(namespace, query="preferences")

        # Save new memory
        runtime.store.put(
            namespace,
            key="preference_123",
            value={"preference": "dark_mode", "timestamp": "2025-11-15"}
        )

        return {"memories": memories}
```

## Store Operations

### Put (Save)

```python
runtime.store.put(
    namespace=("user", "alice"),
    key="pref_theme",
    value={"theme": "dark", "saved_at": "2025-11-15"}
)
```

### Get (Retrieve)

```python
item = runtime.store.get(
    namespace=("user", "alice"),
    key="pref_theme"
)
# Returns: {"theme": "dark", "saved_at": "2025-11-15"}
```

### Search (Query)

```python
results = runtime.store.search(
    namespace=("user", "alice"),
    query="theme preferences"
)
```

### List (All in Namespace)

```python
all_items = runtime.store.list(namespace=("user", "alice"))
```

### Delete

```python
runtime.store.delete(
    namespace=("user", "alice"),
    key="pref_theme"
)
```

## Namespace Patterns

### User-Scoped

```python
namespace = ("user", user_id)
# Memories specific to one user
```

### Session-Scoped

```python
thread_id = self.get_thread_id(config)
namespace = ("session", thread_id)
# Memories for one conversation thread
```

### Organization-Scoped

```python
namespace = ("org", org_id, "team", team_id)
# Multi-level organization
```

### Global

```python
namespace = ("global",)
# Shared across all users
```

## Store Implementations

### InMemoryStore (Development)

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()  # Includes in-memory store
```

**Use for:** Testing, development
**Not for:** Production (data lost on restart)

### PostgreSQL Store (Production)

```python
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:pass@host:5432/db"
)
```

**Use for:** Production deployments

### MongoDB Store (Production)

```python
from langgraph.checkpoint.mongodb import MongoDBSaver

checkpointer = MongoDBSaver.from_conn_string(
    "mongodb://user:pass@host:27017/"
)
```

### Redis Store (Production)

```python
from langgraph_redis import RedisSaver

checkpointer = RedisSaver.from_conn_string(
    "redis://host:6379"
)
```

## Common Patterns

### User Preferences

```python
def execute(self, state, runtime=None, **kwargs):
    if runtime and runtime.store:
        user_id = state["user_id"]
        namespace = ("user", user_id)

        # Load preferences
        prefs = runtime.store.get(namespace, "preferences")

        if not prefs:
            # Default preferences
            prefs = {"theme": "light", "language": "en"}
            runtime.store.put(namespace, "preferences", prefs)

        return {"preferences": prefs}
    return {}
```

### Learning from Feedback

```python
def execute(self, state, runtime=None, **kwargs):
    if runtime and runtime.store:
        feedback = state.get("user_feedback")
        namespace = ("global", "feedback")

        # Store feedback
        runtime.store.put(
            namespace,
            key=f"feedback_{state['session_id']}",
            value={"feedback": feedback, "context": state["context"]}
        )

    return {}
```

## Decision Framework

```
Need data across sessions?
  → Long-term memory (Store)

User-specific data?
  → namespace = ("user", user_id)

Session-specific data?
  → namespace = ("session", thread_id)

Shared knowledge?
  → namespace = ("global",)

Testing only?
  → InMemoryStore

Production?
  → PostgreSQL/MongoDB/Redis Store
```

## Act Project Conventions

⚠️ **Accessing Store:**
- Add `runtime: Runtime = None` to execute()
- Check `if runtime and runtime.store:`
- Always handle None case

⚠️ **Namespaces:**
- Use tuples: `("user", user_id)`
- Be consistent across application
- Document namespace structure

## Common Mistakes

### ❌ Not Checking for Store

```python
# BAD
memories = runtime.store.get(...)  # May fail if None
```

**Fix:**
```python
# GOOD
if runtime and runtime.store:
    memories = runtime.store.get(...)
```

### ❌ Hardcoded Namespace

```python
# BAD
namespace = ("user", "alice")  # Always alice!
```

**Fix:**
```python
# GOOD
namespace = ("user", state["user_id"])
```

## References

- Short-term: `03-memory/short-term-memory.md`
- Checkpointers: `03-memory/checkpointers.md`
- Runtime access: `01-core/nodes.md`
