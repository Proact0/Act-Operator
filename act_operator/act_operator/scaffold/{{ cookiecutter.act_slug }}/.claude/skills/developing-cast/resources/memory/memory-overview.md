# Memory Overview

## When to Use This Resource
Read this when deciding what type of memory your graph needs and where to implement it.

## Memory Types in LangGraph

### 1. In-Session Memory (State)
**What:** Data that exists only during graph execution.
**How:** Store in graph state.
**Lifetime:** Single graph run.

```python
class GraphState(TypedDict):
    conversation_history: list[dict]  # Lost after invoke() completes
    current_context: str
```

**When to use:**
- Temporary working data
- Current conversation turn
- Intermediate processing results

### 2. Short-Term Memory (Checkpoints)
**What:** Conversation state persisted across runs within same thread.
**How:** Checkpointer (MemorySaver, SqliteSaver).
**Lifetime:** Thread/conversation session.

```python
# Same thread_id = shared memory
config = {"configurable": {"thread_id": "user-123-session-1"}}
graph.invoke({"input": "Hello"}, config)
graph.invoke({"input": "What did I just say?"}, config)  # Remembers "Hello"
```

**When to use:**
- Multi-turn conversations
- Resume after interrupts
- User session persistence

**See:** `checkpoints-persistence.md`

### 3. Long-Term Memory (Store)
**What:** Data persisted across threads/conversations.
**How:** Store API (InMemoryStore, PostgresStore).
**Lifetime:** Permanent (until explicitly deleted).

```python
# Different threads, shared memory via Store
runtime.store.put(namespace=("user", "123"), key="preferences", value={"theme": "dark"})
# Later, different conversation:
prefs = runtime.store.get(namespace=("user", "123"), key="preferences")
```

**When to use:**
- User preferences/profile
- Knowledge base
- Cross-conversation learning
- Facts to remember permanently

**See:** `cross-thread-memory.md`

## Decision Matrix

| Need | Solution | Implementation |
|------|----------|----------------|
| Temporary data during execution | State | Add to state schema |
| Multi-turn conversation | Checkpointer | `compile(checkpointer=SqliteSaver(...))` |
| Resume after interrupt | Checkpointer | Same as above + interrupts |
| Remember across conversations | Store | Access via `runtime.store` in nodes/tools |
| User profiles/preferences | Store | Namespace by user ID |
| Shared knowledge base | Store | Common namespace across users |

## Where to Implement Memory

### State (In GraphState)
```python
# casts/{ cast_name }/modules/state.py
class MyCastState(TypedDict):
    messages: Annotated[list[dict], add]  # Short-term in-session
    current_step: str
```

### Checkpoints (In graph.py compilation)
```python
# casts/{ cast_name }/graph.py
from langgraph.checkpoint.sqlite import SqliteSaver

class MyGraph(BaseGraph):
    def build(self):
        builder = StateGraph(MyCastState)
        # ... add nodes/edges ...
        return builder.compile(
            checkpointer=SqliteSaver.from_conn_string("memory.db")
        )
```

### Store (In nodes or tools)
```python
# In node
from casts.base_node import BaseNode

class UserPrefsNode(BaseNode):
    def execute(self, state: dict, runtime=None, **kwargs) -> dict:
        if runtime and runtime.store:
            prefs = runtime.store.get(
                namespace=("user", state["user_id"]),
                key="preferences"
            )
            return {"preferences": prefs}
        return {}

# In tool
from langchain_core.tools import tool, InjectedToolRuntime
from typing import Annotated

@tool
def save_preference(
    key: str,
    value: str,
    runtime: Annotated[InjectedToolRuntime, ...]
) -> str:
    """Save a user preference."""
    if runtime and runtime.store:
        runtime.store.put(
            namespace=("user_prefs",),
            key=key,
            value=value
        )
    return f"Saved {key}={value}"
```

## Common Patterns

### Pattern 1: Conversation with History
**Need:** Multi-turn chat with memory.
**Solution:** Checkpointer + messages in state.

```python
class ChatState(TypedDict):
    messages: Annotated[list[dict], add]

# Compile with checkpointer
graph = builder.compile(checkpointer=SqliteSaver(...))

# Each conversation has unique thread_id
config = {"configurable": {"thread_id": f"user-{user_id}"}}
```

### Pattern 2: Personalized Agent
**Need:** Remember user preferences across sessions.
**Solution:** Store for preferences + checkpointer for conversations.

```python
# Store user profile (permanent)
runtime.store.put(
    namespace=("user", user_id),
    key="profile",
    value={"name": "Alice", "preferences": {...}}
)

# Checkpointer for conversation (session)
config = {"configurable": {"thread_id": f"{user_id}-{session_id}"}}
```

### Pattern 3: Knowledge Accumulation
**Need:** Learn facts over time.
**Solution:** Store with searchable namespaces.

```python
# Save facts as they're learned
runtime.store.put(
    namespace=("facts", "user-123"),
    key=f"fact-{timestamp}",
    value={"fact": "...", "source": "..."}
)

# Search facts later
facts = runtime.store.search(namespace_prefix=("facts", "user-123"))
```

## Decision Framework

```
Data needed for...
├─ Just this execution → State
├─ This conversation (multi-turn) → Checkpointer
└─ Across all conversations → Store

Data scope...
├─ User-specific → Store with namespace ("user", user_id)
├─ Shared knowledge → Store with common namespace
└─ Session-specific → Checkpointer with unique thread_id

Implementation location...
├─ Simple data access → Node with runtime param
├─ Reusable across casts → Tool with InjectedToolRuntime
└─ Complex logic → Dedicated memory node
```

## Common Mistakes

❌ **Using state for persistent data**
```python
# ❌ State is cleared after invoke()
class State(TypedDict):
    user_preferences: dict  # Lost after execution

# ✅ Use Store for persistence
def execute(self, state, runtime=None, **kwargs):
    prefs = runtime.store.get(...)
```

❌ **Not using thread_id with checkpointer**
```python
# ❌ Without thread_id, each run starts fresh
graph.invoke({"input": "Hi"}, checkpointer=saver)

# ✅ thread_id enables conversation memory
config = {"configurable": {"thread_id": "user-123"}}
graph.invoke({"input": "Hi"}, config=config)
```

❌ **Mixing Store and checkpointer concerns**
- **Checkpointer:** For conversation state (messages, current step)
- **Store:** For facts, preferences, knowledge base

