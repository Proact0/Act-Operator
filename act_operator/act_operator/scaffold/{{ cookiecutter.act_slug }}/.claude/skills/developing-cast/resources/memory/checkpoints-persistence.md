# Checkpoints & Persistence

## When to Use This Resource
Read this when implementing conversation memory, enabling interrupts, or adding persistence to your graph.

## What Are Checkpoints?

**Checkpoints** = Snapshots of graph state saved at each step, enabling:
- Multi-turn conversations (remembering context)
- Resuming after interrupts
- Time-travel debugging
- Replaying from any point

## Checkpointer Types

### MemorySaver (Development/Testing)
**Storage:** In-memory (lost on restart).
**When to use:** Local development, testing, demos.

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)
```

**Pros:**
- ✅ Fast
- ✅ Zero setup
- ✅ Perfect for testing

**Cons:**
- ❌ Lost on restart
- ❌ Not for production

### SqliteSaver (Small-Scale Production)
**Storage:** SQLite database file.
**When to use:** Single-server deployments, prototypes, small user bases.

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# File-based
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")

# In-memory SQLite (testing)
checkpointer = SqliteSaver.from_conn_string(":memory:")

graph = builder.compile(checkpointer=checkpointer)
```

**Pros:**
- ✅ Persists across restarts
- ✅ Simple file-based storage
- ✅ Good for local/prototype deployments

**Cons:**
- ❌ Not suitable for distributed systems
- ❌ Limited concurrency

### PostgresSaver (Production)
**Storage:** PostgreSQL database.
**When to use:** Production, multiple servers, high concurrency.

```python
from langgraph.checkpoint.postgres import PostgresSaver

# Connection string
conn_string = "postgresql://user:pass@localhost/dbname"
checkpointer = PostgresSaver.from_conn_string(conn_string)

# Or async version
from langgraph.checkpoint.postgres import AsyncPostgresSaver
checkpointer = AsyncPostgresSaver.from_conn_string(conn_string)

graph = builder.compile(checkpointer=checkpointer)
```

**Pros:**
- ✅ Production-ready
- ✅ Distributed support
- ✅ High concurrency
- ✅ Scalable

**Cons:**
- ❌ Requires PostgreSQL setup
- ❌ More complex than SQLite

## Using Thread IDs

**thread_id** = Identifier for a conversation/session. Each unique thread_id gets its own checkpoint history.

```python
# User 1's conversation
config_user1 = {"configurable": {"thread_id": "user-1-session-abc"}}
graph.invoke({"input": "Hello"}, config=config_user1)
graph.invoke({"input": "How are you?"}, config=config_user1)  # Remembers "Hello"

# User 2's separate conversation
config_user2 = {"configurable": {"thread_id": "user-2-session-xyz"}}
graph.invoke({"input": "Hi there"}, config=config_user2)  # Separate history
```

**Best practices:**
- Include user ID: `f"user-{user_id}-session-{session_id}"`
- Use UUIDs for sessions: `f"user-{user_id}-{uuid4()}"`
- Keep thread_id consistent within conversation

## Viewing Checkpoint History

```python
# Get all checkpoints for a thread
config = {"configurable": {"thread_id": "user-123"}}
checkpoints = graph.get_state_history(config)

for checkpoint in checkpoints:
    print(f"Step: {checkpoint.metadata.get('step')}")
    print(f"State: {checkpoint.values}")
    print(f"Next: {checkpoint.next}")
```

## Time-Travel: Replaying from Checkpoint

```python
# Get checkpoint history
checkpoints = list(graph.get_state_history(config))

# Replay from specific checkpoint (e.g., 3 steps ago)
past_checkpoint = checkpoints[2]

# Resume from that point
graph.invoke(
    None,  # No new input needed if resuming
    config={
        **config,
        "configurable": {
            **config["configurable"],
            "checkpoint_id": past_checkpoint.config["configurable"]["checkpoint_id"]
        }
    }
)
```

**Use cases:**
- Debugging failed runs
- Testing different paths
- Undoing steps
- A/B testing decisions

## Checkpointer with Interrupts

**Interrupts** require checkpointers to save state when pausing.

```python
graph = builder.compile(
    checkpointer=SqliteSaver.from_conn_string("checkpoints.db"),
    interrupt_before=["approval_node"]  # Pause before this node
)

# First invoke - will pause at approval_node
config = {"configurable": {"thread_id": "user-123"}}
result = graph.invoke({"input": "Request data"}, config=config)

# Inspect state at interrupt
state = graph.get_state(config)
print(f"Next node: {state.next}")  # ['approval_node']

# Resume after human approval
graph.invoke(None, config=config)  # Continues from pause point
```

**See:** `../advanced/interrupts-hitl.md` for complete patterns.

## State Updates During Interrupts

Update state before resuming:

```python
# Graph is interrupted
state = graph.get_state(config)

# Modify state
graph.update_state(
    config,
    {"approved": True, "notes": "Approved by manager"}
)

# Resume with updated state
graph.invoke(None, config=config)
```

## Production Patterns

### Pattern 1: User Session Management
```python
class SessionManager:
    def __init__(self, checkpointer):
        self.checkpointer = checkpointer
        self.graph = build_graph(checkpointer)

    def create_session(self, user_id: str) -> str:
        session_id = str(uuid4())
        thread_id = f"user-{user_id}-{session_id}"
        return thread_id

    def invoke(self, thread_id: str, input_data: dict):
        config = {"configurable": {"thread_id": thread_id}}
        return self.graph.invoke(input_data, config=config)

# Usage
manager = SessionManager(PostgresSaver.from_conn_string(...))
thread = manager.create_session("alice-123")
result = manager.invoke(thread, {"input": "Hello"})
```

### Pattern 2: Checkpoint Cleanup
Old checkpoints can accumulate. Clean them periodically:

```python
from datetime import datetime, timedelta

def cleanup_old_checkpoints(checkpointer, days=30):
    """Remove checkpoints older than specified days."""
    cutoff = datetime.now() - timedelta(days=days)
    # Implementation depends on checkpointer type
    # For SQLite: DELETE FROM checkpoints WHERE timestamp < cutoff
```

### Pattern 3: Checkpoint Namespacing
```python
# Different graphs, same database
user_graph = builder_user.compile(
    checkpointer=PostgresSaver.from_conn_string(conn, namespace="user_graph")
)

admin_graph = builder_admin.compile(
    checkpointer=PostgresSaver.from_conn_string(conn, namespace="admin_graph")
)
```

## Common Mistakes

❌ **Not using thread_id**
```python
# ❌ Each run creates new thread
graph.invoke({"input": "..."})

# ✅ Consistent thread_id for conversation
config = {"configurable": {"thread_id": "user-123"}}
graph.invoke({"input": "..."}, config=config)
```

❌ **Using same thread_id for different conversations**
```python
# ❌ All users share history!
thread_id = "conversation"

# ✅ Unique per user + session
thread_id = f"user-{user_id}-{session_id}"
```

❌ **Forgetting checkpointer for interrupts**
```python
# ❌ Can't interrupt without checkpointer
graph = builder.compile(interrupt_before=["node"])

# ✅ Checkpointer required for interrupts
graph = builder.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["node"]
)
```

## References
- LangGraph Persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- Related: `memory-overview.md` (when to use checkpoints vs Store)
- Related: `cross-thread-memory.md` (long-term memory)
- Related: `../advanced/interrupts-hitl.md` (using checkpoints with interrupts)
