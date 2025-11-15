# Long-Term Memory (Cross-Session)

## When to Use This Resource
Read when implementing cross-session memory, using Store API, or persisting data between conversations.

---

## Key Concepts

**Long-term memory** persists across sessions/threads - data survives beyond single conversation.

**Store API** provides the interface for cross-session storage.

**Implementations:** InMemoryStore, MongoDBStore, RedisStore

---

## Store vs Checkpointer

| Feature | Checkpointer | Store |
|---------|--------------|-------|
| **Scope** | Single thread (session) | Across threads (sessions) |
| **Data** | Conversation state | Custom data |
| **Use case** | Message history within session | User preferences, facts, topics |
| **Cleared** | When thread ends | Never (until explicitly deleted) |

**Decision:**
- Within-session memory → Checkpointer (`memory/short-term-memory.md`)
- Cross-session memory → Store (this resource)

---

## Store Types

### InMemoryStore (Development/Testing)

```python
from langgraph.store.memory import InMemoryStore

# Create Store
store = InMemoryStore()

# Data lives only while program runs
# Lost when program stops
```

**Use when:**
- ✓ Local development
- ✓ Testing
- ✗ Production (data not persisted to disk)

---

### MongoDBStore (Production)

```python
from langgraph.store.mongodb import MongoDBStore

# Create Store with MongoDB connection
store = MongoDBStore(
    connection_string="mongodb://localhost:27017/",
    database_name="myapp",
    collection_name="langgraph_store"
)

# Data persists to MongoDB
# Survives program restarts
# Supports vector search
```

**Use when:**
- ✓ Production deployments
- ✓ Need vector/semantic search
- ✓ Scaling across multiple instances

---

### RedisStore (Production)

```python
from langgraph.store.redis import RedisStore

# Create Store with Redis connection
store = RedisStore(
    redis_url="redis://localhost:6379"
)

# Data persists to Redis
# Fast, in-memory with persistence
```

**Use when:**
- ✓ Production deployments
- ✓ Need fast access
- ✓ Already using Redis

---

## Initializing Store in Graph

### Basic Initialization

```python
# In graph.py
from casts.base_graph import BaseGraph
from langgraph.graph import StateGraph
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver

class MyCastGraph(BaseGraph):
    def build(self):
        builder = StateGraph(self.state)

        # Add nodes and edges...
        builder.add_node("my_node", MyNode())
        builder.add_edge("my_node", END)

        # Initialize persistence
        store = InMemoryStore()  # Long-term memory
        checkpointer = MemorySaver()  # Short-term memory

        # Compile with BOTH
        graph = builder.compile(
            checkpointer=checkpointer,  # For conversation state
            store=store  # For cross-session data
        )

        return graph
```

**CRITICAL:** Pass `store=store` to `compile()`

---

### Production Configuration

```python
from langgraph.store.mongodb import MongoDBStore
from langgraph.checkpoint.sqlite import SqliteSaver

class MyCastGraph(BaseGraph):
    def build(self):
        builder = StateGraph(self.state)

        # ... nodes and edges ...

        # Production stores
        store = MongoDBStore(
            connection_string="mongodb://prod-server:27017/",
            database_name="myapp"
        )

        checkpointer = SqliteSaver.from_conn_string("checkpoints.db")

        graph = builder.compile(
            checkpointer=checkpointer,
            store=store
        )

        return graph
```

---

## Store Operations

### Put (Save Data)

```python
# In a node or tool
def execute(self, state: dict, runtime=None) -> dict:
    if runtime and runtime.store:
        namespace = ("my_cast", "user_data")
        key = "user_123"
        value = {
            "name": "Alice",
            "preferences": {"theme": "dark"},
            "topics": ["AI", "Python"]
        }

        runtime.store.put(namespace, key, value)

    return {}
```

**Namespace:** Tuple organizing data: `("cast_name", "category")`
**Key:** Unique identifier for this item
**Value:** Dict with your data

---

### Get (Retrieve Item)

```python
def execute(self, state: dict, runtime=None) -> dict:
    if runtime and runtime.store:
        namespace = ("my_cast", "user_data")
        key = "user_123"

        item = runtime.store.get(namespace, key)

        if item:
            user_data = item.value  # Your dict
            name = user_data.get("name")
            self.log(f"Retrieved user: {name}")

            return {"user_name": name}

    return {}
```

**Returns:** Item object with `.value` attribute, or None if not found

---

### Search (Find Multiple Items)

```python
def execute(self, state: dict, runtime=None) -> dict:
    if runtime and runtime.store:
        namespace = ("research", "topics")

        # Get all items in namespace
        items = runtime.store.search(namespace)

        # Extract values
        topics = [item.value.get("topic") for item in items]

        self.log(f"Found {len(topics)} topics")

        return {"all_topics": topics}

    return {}
```

**Returns:** List of Item objects

---

### Search with Filters

```python
# Search with query/filter
items = runtime.store.search(
    namespace,
    query="research topics about AI"  # Semantic search if using MongoDBStore
)

# Or search with metadata filters
items = runtime.store.search(
    namespace,
    filter={"category": "AI", "status": "active"}
)
```

---

### Delete (Remove Item)

```python
def execute(self, state: dict, runtime=None) -> dict:
    if runtime and runtime.store:
        namespace = ("my_cast", "user_data")
        key = "user_123"

        runtime.store.delete(namespace, key)

        self.log(f"Deleted {key}")

    return {}
```

---

## Namespace Conventions

### Recommended Structure

```python
# Format: (cast_name, data_category)

namespace = ("chat", "user_preferences")       # User settings
namespace = ("research", "topics")             # Research topics
namespace = ("workflow", "templates")          # Saved templates
namespace = ("analytics", "events")            # Event logs
```

**Best practices:**
- First element: Cast name or domain
- Second element: Data category
- Be specific: "user_preferences" not "data"
- Keep consistent across your cast

---

### Multi-Level Namespaces

```python
# Can use more levels if needed
namespace = ("my_cast", "users", "preferences")
namespace = ("my_cast", "research", "ai_topics")
```

**But:** Keep simple when possible (2 levels usually enough)

---

## Common Patterns

### User Preferences

```python
from casts.base_node import BaseNode

class PreferenceNode(BaseNode):
    """Manages user preferences."""

    def execute(self, state: dict, runtime=None) -> dict:
        user_id = state.get("user_id", "default")

        if not runtime or not runtime.store:
            return {}

        namespace = ("chat", "user_preferences")

        # Get existing preferences
        item = runtime.store.get(namespace, user_id)

        if item:
            prefs = item.value
        else:
            prefs = {"theme": "light", "language": "en"}

        # Update preference
        new_pref = state.get("new_preference", {})
        prefs.update(new_pref)

        # Save back
        runtime.store.put(namespace, user_id, prefs)

        return {"preferences": prefs}
```

---

### Accumulating Research Topics

```python
class ResearchNode(BaseNode):
    """Tracks research topics over time."""

    def execute(self, state: dict, runtime=None) -> dict:
        topic = state.get("topic")

        if not runtime or not runtime.store:
            return {"topics": [topic]}

        namespace = ("research", "topics")

        # Save new topic
        runtime.store.put(
            namespace,
            topic,
            {
                "topic": topic,
                "timestamp": "2025-01-15",  # Use actual timestamp
                "source": "user_query"
            }
        )

        # Get all topics
        items = runtime.store.search(namespace)
        all_topics = [item.value.get("topic") for item in items]

        self.log(f"Total topics: {len(all_topics)}")

        return {"all_topics": all_topics}
```

---

### Semantic Search (MongoDBStore)

```python
# With MongoDBStore and vector search enabled
class SemanticSearchNode(BaseNode):
    def execute(self, state: dict, runtime=None) -> dict:
        query = state.get("query")

        if not runtime or not runtime.store:
            return {}

        namespace = ("knowledge", "documents")

        # Semantic search
        results = runtime.store.search(
            namespace,
            query=query  # Finds semantically similar content
        )

        docs = [item.value for item in results]

        return {"relevant_docs": docs}
```

**Requires:** MongoDB Atlas with vector search configured

---

### Caching Expensive Computations

```python
class CachedComputationNode(BaseNode):
    """Caches computation results."""

    def execute(self, state: dict, runtime=None) -> dict:
        input_key = state.get("input_key")

        if runtime and runtime.store:
            namespace = ("computation", "cache")

            # Check cache
            cached = runtime.store.get(namespace, input_key)
            if cached:
                self.log("Cache hit")
                return {"result": cached.value.get("result")}

        # Compute (expensive)
        result = self.expensive_computation(input_key)

        # Save to cache
        if runtime and runtime.store:
            runtime.store.put(
                namespace,
                input_key,
                {"result": result, "computed_at": "now"}
            )

        return {"result": result}

    def expensive_computation(self, key):
        # Simulate expensive operation
        return f"result_for_{key}"
```

---

## Using Store in Tools

### Tool with Store Access

```python
# File: casts/my_cast/modules/tools/save_fact.py

from langchain_core.tools import tool
from typing import Optional, Any

@tool
def save_fact(
    fact: str,
    category: str = "general",
    runtime: Optional[Any] = None
) -> str:
    """Saves a fact to long-term memory.

    Args:
        fact: The fact to save
        category: Fact category
        runtime: Runtime context

    Returns:
        Confirmation message
    """
    if not runtime or not runtime.store:
        return "Store not available"

    namespace = ("facts", category)
    key = fact[:50]  # Use first 50 chars as key (or better: UUID)

    runtime.store.put(
        namespace,
        key,
        {"fact": fact, "category": category}
    )

    return f"Saved fact in {category}"
```

**See:** `tools/tool-runtime.md` for detailed tool patterns

---

## Anti-Patterns

### ❌ Not Initializing Store

```python
# ❌ WRONG - Forgot to pass store to compile()
graph = builder.compile(checkpointer=checkpointer)
# runtime.store will be None!
```

```python
# ✓ CORRECT
store = InMemoryStore()
graph = builder.compile(checkpointer=checkpointer, store=store)
```

---

### ❌ Not Checking for Store

```python
def execute(self, state, runtime=None):
    # ❌ WRONG - Crashes if store not available
    runtime.store.put(namespace, key, value)
```

```python
def execute(self, state, runtime=None):
    # ✓ CORRECT - Check first
    if runtime and runtime.store:
        runtime.store.put(namespace, key, value)
```

---

### ❌ String Namespace

```python
# ❌ WRONG - String instead of tuple
namespace = "my_cast"
runtime.store.put(namespace, key, value)
```

```python
# ✓ CORRECT - Tuple
namespace = ("my_cast", "data")
runtime.store.put(namespace, key, value)
```

---

### ❌ Not Handling Missing Items

```python
# ❌ WRONG - Crashes if item doesn't exist
item = runtime.store.get(namespace, key)
data = item.value  # item might be None!
```

```python
# ✓ CORRECT - Check if item exists
item = runtime.store.get(namespace, key)
if item:
    data = item.value
else:
    data = {}  # Default
```

---

## Decision Framework

**Q: Which Store type?**
- Development/testing → InMemoryStore
- Production, need vector search → MongoDBStore
- Production, fast access → RedisStore

**Q: Where to use Store?**
- Tools → Add `runtime` parameter, access via `runtime.store`
- Nodes → Add `runtime` parameter to `execute()`

**Q: What to put in Store?**
- ✓ User preferences, settings
- ✓ Knowledge facts, research topics
- ✓ Cached computations
- ✗ Conversation state (use checkpointer instead)

**Q: Store or checkpointer?**
- Single session → Checkpointer
- Across sessions → Store

---

## Complete Example

```python
# graph.py
from casts.base_graph import BaseGraph
from langgraph.graph import StateGraph, END
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver

class MyCastGraph(BaseGraph):
    def __init__(self):
        super().__init__()
        self.state = MyState

    def build(self):
        builder = StateGraph(self.state)

        from casts.my_cast.nodes import PreferenceNode, ChatNode

        builder.add_node("preferences", PreferenceNode())
        builder.add_node("chat", ChatNode())

        builder.add_edge("preferences", "chat")
        builder.add_edge("chat", END)
        builder.set_entry_point("preferences")

        # Initialize stores
        store = InMemoryStore()  # Cross-session
        checkpointer = MemorySaver()  # Within-session

        graph = builder.compile(
            checkpointer=checkpointer,
            store=store
        )

        return graph


# Usage
my_graph = MyCastGraph().build()

config = {
    "configurable": {
        "thread_id": "user_123"  # For checkpointer
    }
}

result = my_graph.invoke(
    {"user_id": "user_123", "query": "hello"},
    config=config
)
```

---

## References
- tools/tool-runtime.md (using Store in tools)
- memory/short-term-memory.md (checkpointers for within-session)
- core/node-patterns.md (runtime parameter in nodes)
- [LangGraph Store Docs](https://docs.langchain.com/oss/python/langgraph/)
