# Checkpointers

## When to Use This Resource

Read this for state persistence, resuming conversations, and interrupt/resume workflows.

## Key Concept

**Checkpointer:** Saves graph state after each step, enabling resume, time-travel, and persistence.

## What Checkpointers Enable

1. **Resume conversations** - Continue from where you left off
2. **Human-in-the-loop** - Pause for approval, resume after
3. **Error recovery** - Retry from last checkpoint
4. **Time travel** - View/restore previous states
5. **Cross-session memory** - Access Store

## Checkpointer Implementations

### MemorySaver (Development)

```python
from langgraph.checkpoint.memory import MemorySaver

graph = builder.compile(checkpointer=MemorySaver())
```

**Pros:** Simple, no setup
**Cons:** Data lost on restart
**Use for:** Development, testing

### PostgresSaver (Production)

```python
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:pass@localhost:5432/dbname"
)

graph = builder.compile(checkpointer=checkpointer)
```

**Pros:** Durable, scalable, SQL queries
**Use for:** Production applications

### SqliteSaver (Local/Small Scale)

```python
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string("checkpoints.db")
graph = builder.compile(checkpointer=checkpointer)
```

**Pros:** File-based, no server
**Use for:** Desktop apps, small deployments

### MongoDBSaver (Production)

```python
from langgraph.checkpoint.mongodb import MongoDBSaver

checkpointer = MongoDBSaver.from_conn_string(
    "mongodb://user:pass@localhost:27017/"
)
graph = builder.compile(checkpointer=checkpointer)
```

## Using thread_id

### Session Management

```python
# Each conversation gets unique thread_id
config = {"configurable": {"thread_id": "user-123-session-1"}}

# First message
result1 = graph.invoke(
    {"messages": [HumanMessage(content="Hello")]},
    config=config
)

# Continue same conversation
result2 = graph.invoke(
    {"messages": [HumanMessage(content="Continue")]},
    config=config
)

# New conversation (different thread_id)
config2 = {"configurable": {"thread_id": "user-123-session-2"}}
result3 = graph.invoke(
    {"messages": [HumanMessage(content="New chat")]},
    config2
)
```

### thread_id Patterns

```python
# User-based
thread_id = f"user-{user_id}"

# Session-based
thread_id = f"user-{user_id}-session-{session_id}"

# Timestamp-based
thread_id = f"user-{user_id}-{datetime.now().isoformat()}"

# UUID
import uuid
thread_id = str(uuid.uuid4())
```

## Graph with Checkpointer Pattern

```python
from casts.base_graph import BaseGraph
from langgraph.checkpoint.memory import MemorySaver

class PersistentGraph(BaseGraph):
    def __init__(self, checkpointer=None):
        super().__init__()
        self.checkpointer = checkpointer or MemorySaver()

    def build(self):
        builder = StateGraph(MyState)

        # Add nodes and edges...

        return builder.compile(checkpointer=self.checkpointer)
```

**Usage:**
```python
# Development
graph = PersistentGraph().build()

# Production
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string(conn_string)
graph = PersistentGraph(checkpointer=checkpointer).build()
```

## Viewing State History

### Get State

```python
config = {"configurable": {"thread_id": "123"}}

# Get current state
state = graph.get_state(config)
print(state.values)  # Current state values
print(state.next)  # Next nodes to execute
```

### Get State History

```python
# Get all checkpoints for thread
history = graph.get_state_history(config)

for state in history:
    print(f"Step: {state.metadata['step']}")
    print(f"State: {state.values}")
```

## Updating State Manually

### Update and Continue

```python
# Update state without executing
graph.update_state(
    config,
    {"messages": [HumanMessage(content="Manual update")]}
)

# Resume execution
result = graph.invoke(None, config)  # Continues from updated state
```

## Common Patterns

### Web Application Session

```python
# Flask/FastAPI example
@app.post("/chat")
def chat(user_id: str, session_id: str, message: str):
    config = {
        "configurable": {
            "thread_id": f"{user_id}-{session_id}"
        }
    }

    result = graph.invoke(
        {"messages": [HumanMessage(content=message)]},
        config=config
    )

    return result
```

### Resume After Interrupt

```python
# Graph with interrupt
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_review"]
)

# First invocation (stops at interrupt)
config = {"configurable": {"thread_id": "123"}}
result = graph.invoke({"task": "Review this"}, config)

# ... human reviews, approves ...

# Resume from interrupt
graph.invoke(None, config)  # Continues execution
```

## Config Options

### Full Config

```python
config = {
    "configurable": {
        "thread_id": "session-123",  # Required for checkpoints
    },
    "tags": ["production", "user-action"],
    "metadata": {"user_id": "alice"},
    "recursion_limit": 50,
}
```

## Common Mistakes

### ❌ No thread_id

```python
# BAD: Checkpointer but no thread_id
graph = builder.compile(checkpointer=MemorySaver())
result = graph.invoke(input)  # Can't restore without thread_id
```

**Fix:**
```python
# GOOD
config = {"configurable": {"thread_id": "123"}}
result = graph.invoke(input, config)
```

### ❌ Changing thread_id Unexpectedly

```python
# BAD: New thread_id each time
thread_id = str(uuid.uuid4())  # Different every invocation!
config = {"configurable": {"thread_id": thread_id}}
```

**Fix:**
```python
# GOOD: Consistent thread_id for session
thread_id = f"user-{user_id}-session-{session_id}"
config = {"configurable": {"thread_id": thread_id}}
```

## Decision Framework

```
Need persistence?
  → Add checkpointer

Development/testing?
  → MemorySaver

Production, SQL database?
  → PostgresSaver

Production, NoSQL?
  → MongoDBSaver

Local file storage?
  → SqliteSaver

Need human-in-the-loop?
  → Checkpointer + interrupt_before/after

Multi-user application?
  → Use thread_id per user/session
```

## Act Project Conventions

⚠️ **Checkpointer in graph:**
- Accept in __init__
- Pass to compile()
- Default to MemorySaver for dev

⚠️ **thread_id:**
- Always use in production
- Consistent format across application
- Document naming convention

## References

- Interrupts: `04-advanced/interrupts.md`
- Graph compilation: `01-core/graph.md`
- Store access: `03-memory/long-term-memory.md`
