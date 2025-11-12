# Graph Compilation in LangGraph

Comprehensive guide to compiling, checkpointing, and configuring LangGraph graphs.

## Table of Contents

1. [Introduction](#introduction)
2. [Basic Compilation](#basic-compilation)
   - [Simple Compilation](#simple-compilation)
   - [Compilation Process](#compilation-process)
   - [Compiled Graph Interface](#compiled-graph-interface)
3. [Checkpointing](#checkpointing)
   - [What is Checkpointing](#what-is-checkpointing)
   - [Memory Checkpointer](#memory-checkpointer)
   - [SQLite Checkpointer](#sqlite-checkpointer)
   - [PostgreSQL Checkpointer](#postgresql-checkpointer)
   - [Custom Checkpointers](#custom-checkpointers)
4. [Store Configuration](#store-configuration)
   - [What is Store](#what-is-store)
   - [In-Memory Store](#in-memory-store)
   - [PostgreSQL Store](#postgresql-store)
   - [Store Operations](#store-operations)
5. [Interrupts](#interrupts)
   - [Before Node Interrupts](#before-node-interrupts)
   - [After Node Interrupts](#after-node-interrupts)
   - [Resuming from Interrupts](#resuming-from-interrupts)
   - [Human-in-the-Loop](#human-in-the-loop)
6. [Streaming](#streaming)
   - [Stream Modes](#stream-modes)
   - [Streaming Values](#streaming-values)
   - [Streaming Updates](#streaming-updates)
   - [Streaming Messages](#streaming-messages)
   - [Custom Streaming](#custom-streaming)
7. [Advanced Configuration](#advanced-configuration)
   - [Recursion Limit](#recursion-limit)
   - [Debug Mode](#debug-mode)
   - [Custom Config](#custom-config)
   - [Retry Policy](#retry-policy)
8. [Execution Modes](#execution-modes)
   - [invoke() - Synchronous](#invoke---synchronous)
   - [ainvoke() - Asynchronous](#ainvoke---asynchronous)
   - [stream() - Streaming](#stream---streaming)
   - [astream() - Async Streaming](#astream---async-streaming)
9. [Thread Management](#thread-management)
   - [Thread IDs](#thread-ids)
   - [Thread State](#thread-state)
   - [Multi-User Support](#multi-user-support)
10. [Best Practices](#best-practices)
11. [Common Patterns](#common-patterns)
12. [Performance Optimization](#performance-optimization)
13. [Troubleshooting](#troubleshooting)
14. [Examples](#examples)

---

## Introduction

Graph compilation transforms your graph definition into an executable workflow with persistence, streaming, and interruption capabilities.

**Key features:**
- **Checkpointing**: Save and restore graph state
- **Store**: Persistent cross-run storage
- **Interrupts**: Pause for human input
- **Streaming**: Real-time output
- **Thread management**: Multi-user support

---

## Basic Compilation

### Simple Compilation

Minimal compilation:

```python
from langgraph.graph import StateGraph, START, END
from dataclasses import dataclass

@dataclass(kw_only=True)
class State:
    input: str
    output: str = None

def build_graph():
    """Build and compile simple graph."""
    builder = StateGraph(State)

    builder.add_node("process", ProcessNode())

    builder.add_edge(START, "process")
    builder.add_edge("process", END)

    # Simple compilation
    graph = builder.compile()

    return graph

# Usage
graph = build_graph()
result = graph.invoke({"input": "test"})
print(result["output"])
```

### Compilation Process

What happens during compilation:

```
StateGraph Definition
    ↓
builder.compile()
    ↓
1. Validate graph structure
    - Check all nodes defined
    - Verify edge connections
    - Ensure START and END reachable
    ↓
2. Create execution plan
    - Determine node order
    - Set up conditional routing
    - Prepare parallel execution
    ↓
3. Initialize components
    - Set up checkpointer (if provided)
    - Initialize store (if provided)
    - Configure streaming
    ↓
4. Return CompiledGraph
    - Ready for invoke/stream
    - Supports checkpointing
    - Thread-safe execution
```

### Compiled Graph Interface

Methods available on compiled graph:

```python
graph = builder.compile()

# Synchronous execution
result = graph.invoke(input_data, config=config)

# Asynchronous execution
result = await graph.ainvoke(input_data, config=config)

# Streaming execution
for chunk in graph.stream(input_data, config=config):
    process(chunk)

# Async streaming
async for chunk in graph.astream(input_data, config=config):
    await process(chunk)

# Get graph structure
graph_dict = graph.get_graph()

# Get graph visualization (Mermaid)
mermaid = graph.get_graph().draw_mermaid()
```

---

## Checkpointing

### What is Checkpointing

Checkpointing saves graph state at each step:

**Benefits:**
- Resume interrupted executions
- Time travel debugging
- Conversation memory
- Error recovery

**How it works:**
```
Step 1: Execute node A
    ↓
Save checkpoint
    ↓
Step 2: Execute node B
    ↓
Save checkpoint
    ↓
Step 3: Execute node C
    ↓
Save checkpoint
    ↓
Complete
```

### Memory Checkpointer

For development and testing:

```python
from langgraph.checkpoint.memory import MemorySaver

def build_with_memory():
    """Build graph with memory checkpointer."""
    builder = StateGraph(State)

    # Add nodes and edges
    builder.add_node("process", ProcessNode())
    builder.add_edge(START, "process")
    builder.add_edge("process", END)

    # Compile with memory checkpointer
    checkpointer = MemorySaver()
    graph = builder.compile(checkpointer=checkpointer)

    return graph

# Usage with thread_id
from langgraph.graph import RunnableConfig

graph = build_with_memory()

config = RunnableConfig(
    configurable={"thread_id": "thread-123"}
)

# First call
result1 = graph.invoke({"input": "Hello"}, config=config)

# Second call - resumes from checkpoint
result2 = graph.invoke({"input": "Follow-up"}, config=config)
```

**Characteristics:**
- In-memory storage (lost on restart)
- Fast and simple
- Good for development
- Not for production

### SQLite Checkpointer

For single-machine persistence:

```python
from langgraph.checkpoint.sqlite import SqliteSaver

def build_with_sqlite():
    """Build graph with SQLite checkpointer."""
    builder = StateGraph(State)

    builder.add_node("process", ProcessNode())
    builder.add_edge(START, "process")
    builder.add_edge("process", END)

    # SQLite checkpointer
    checkpointer = SqliteSaver.from_conn_string("checkpoints.db")

    graph = builder.compile(checkpointer=checkpointer)

    return graph

# Async version
from langgraph.checkpoint.sqlite import AsyncSqliteSaver

async def build_with_async_sqlite():
    """Async SQLite checkpointer."""
    builder = StateGraph(State)

    builder.add_node("process", ProcessNode())
    builder.add_edge(START, "process")
    builder.add_edge("process", END)

    checkpointer = await AsyncSqliteSaver.from_conn_string("checkpoints.db")

    graph = builder.compile(checkpointer=checkpointer)

    return graph
```

**Characteristics:**
- File-based persistence
- Single-machine deployment
- Simple setup
- Good for small-medium scale

### PostgreSQL Checkpointer

For production deployments:

```python
from langgraph.checkpoint.postgres import PostgresSaver

def build_with_postgres():
    """Build graph with PostgreSQL checkpointer."""
    builder = StateGraph(State)

    builder.add_node("process", ProcessNode())
    builder.add_edge(START, "process")
    builder.add_edge("process", END)

    # PostgreSQL checkpointer
    checkpointer = PostgresSaver.from_conn_string(
        "postgresql://user:password@localhost/dbname"
    )

    graph = builder.compile(checkpointer=checkpointer)

    return graph

# Async version
from langgraph.checkpoint.postgres import AsyncPostgresSaver

async def build_with_async_postgres():
    """Async PostgreSQL checkpointer."""
    checkpointer = await AsyncPostgresSaver.from_conn_string(
        "postgresql://user:password@localhost/dbname"
    )

    graph = builder.compile(checkpointer=checkpointer)

    return graph
```

**Characteristics:**
- Production-ready
- Multi-machine deployment
- Scalable
- Reliable

### Custom Checkpointers

Implement custom checkpointer:

```python
from langgraph.checkpoint import BaseCheckpointSaver

class CustomCheckpointer(BaseCheckpointSaver):
    """Custom checkpointer implementation."""

    def __init__(self, connection_string):
        self.connection = connect(connection_string)

    def get(self, config):
        """Load checkpoint for thread."""
        thread_id = config["configurable"]["thread_id"]
        # Load from custom storage
        return self.connection.load(thread_id)

    def put(self, config, checkpoint, metadata):
        """Save checkpoint for thread."""
        thread_id = config["configurable"]["thread_id"]
        # Save to custom storage
        self.connection.save(thread_id, checkpoint, metadata)

    def list(self, config):
        """List all checkpoints for thread."""
        thread_id = config["configurable"]["thread_id"]
        return self.connection.list(thread_id)
```

---

## Store Configuration

### What is Store

Persistent storage across runs:

**Checkpointer vs Store:**
- **Checkpointer**: Saves graph execution state
- **Store**: Persistent key-value storage

**Use cases:**
- User preferences
- Caching
- Session data
- Cross-thread data

### In-Memory Store

For development:

```python
from langgraph.store.memory import InMemoryStore

def build_with_store():
    """Build graph with in-memory store."""
    builder = StateGraph(State)

    builder.add_node("process", ProcessNode())
    builder.add_edge(START, "process")
    builder.add_edge("process", END)

    checkpointer = MemorySaver()
    store = InMemoryStore()

    graph = builder.compile(
        checkpointer=checkpointer,
        store=store
    )

    return graph
```

### PostgreSQL Store

For production:

```python
from langgraph.store.postgres import PostgresStore

def build_with_postgres_store():
    """Build graph with PostgreSQL store."""
    builder = StateGraph(State)

    builder.add_node("process", ProcessNode())
    builder.add_edge(START, "process")
    builder.add_edge("process", END)

    checkpointer = PostgresSaver.from_conn_string(
        "postgresql://user:password@localhost/dbname"
    )
    store = PostgresStore.from_conn_string(
        "postgresql://user:password@localhost/dbname"
    )

    graph = builder.compile(
        checkpointer=checkpointer,
        store=store
    )

    return graph
```

### Store Operations

Using store in nodes:

```python
class StoreNode(BaseNode):
    def execute(self, state, runtime):
        """Use store in node."""
        if runtime and runtime.store:
            # Put data
            runtime.store.put(
                namespace=("users", "123"),
                key="preferences",
                value={"theme": "dark"}
            )

            # Get data
            prefs = runtime.store.get(
                namespace=("users", "123"),
                key="preferences"
            )

            # Search namespace
            items = runtime.store.search(
                namespace_prefix=("users", "123")
            )

            # Delete data
            runtime.store.delete(
                namespace=("users", "123"),
                key="old_data"
            )

        return {"processed": True}
```

---

## Interrupts

### Before Node Interrupts

Pause before node execution:

```python
def build_with_interrupt_before():
    """Build graph with interrupt before node."""
    builder = StateGraph(State)

    builder.add_node("process", ProcessNode())
    builder.add_node("sensitive", SensitiveNode())

    builder.add_edge(START, "process")
    builder.add_edge("process", "sensitive")
    builder.add_edge("sensitive", END)

    # Interrupt before "sensitive" node
    graph = builder.compile(
        checkpointer=MemorySaver(),
        interrupt_before=["sensitive"]
    )

    return graph

# Usage
graph = build_with_interrupt_before()
config = RunnableConfig(configurable={"thread_id": "thread-123"})

# First invocation - stops before "sensitive"
result1 = graph.invoke({"input": "test"}, config=config)
# Graph paused at "sensitive"

# Resume execution
result2 = graph.invoke(None, config=config)
# Continues from "sensitive"
```

### After Node Interrupts

Pause after node execution:

```python
def build_with_interrupt_after():
    """Build graph with interrupt after node."""
    builder = StateGraph(State)

    builder.add_node("process", ProcessNode())
    builder.add_node("review", ReviewNode())
    builder.add_node("finalize", FinalizeNode())

    builder.add_edge(START, "process")
    builder.add_edge("process", "review")
    builder.add_edge("review", "finalize")
    builder.add_edge("finalize", END)

    # Interrupt after "review" node
    graph = builder.compile(
        checkpointer=MemorySaver(),
        interrupt_after=["review"]
    )

    return graph

# Usage
graph = build_with_interrupt_after()
config = RunnableConfig(configurable={"thread_id": "thread-123"})

# Executes "process" and "review", then pauses
result1 = graph.invoke({"input": "test"}, config=config)

# Can inspect state
print(result1)  # Contains review output

# Resume to finish
result2 = graph.invoke(None, config=config)
```

### Resuming from Interrupts

Resume with modified state:

```python
# First execution - interrupted
result1 = graph.invoke({"input": "test"}, config=config)

# Modify state before resuming
modified_state = result1.copy()
modified_state["user_approved"] = True

# Resume with modified state
result2 = graph.invoke(modified_state, config=config)
```

### Human-in-the-Loop

Implement human approval:

```python
def build_hitl_graph():
    """Build human-in-the-loop graph."""
    builder = StateGraph(State)

    builder.add_node("generate", GenerateNode())
    builder.add_node("execute", ExecuteNode())

    builder.add_edge(START, "generate")
    builder.add_edge("generate", "execute")
    builder.add_edge("execute", END)

    # Interrupt before execution
    graph = builder.compile(
        checkpointer=MemorySaver(),
        interrupt_before=["execute"]
    )

    return graph

# Usage
graph = build_hitl_graph()
config = RunnableConfig(configurable={"thread_id": "thread-123"})

# Generate plan
result1 = graph.invoke({"input": "task"}, config=config)

# Show to human
print("Proposed action:", result1["action"])
approval = input("Approve? (y/n): ")

if approval == "y":
    # Execute
    result2 = graph.invoke(None, config=config)
else:
    # Cancel or modify
    print("Action cancelled")
```

---

## Streaming

### Stream Modes

Different streaming modes:

```python
# Stream modes:
# - "values": Full state after each node
# - "updates": Only updates from each node
# - "messages": Message updates only

graph = builder.compile()

# Stream values (full state)
for chunk in graph.stream(
    {"input": "test"},
    stream_mode="values"
):
    print(chunk)  # Full state

# Stream updates (deltas)
for chunk in graph.stream(
    {"input": "test"},
    stream_mode="updates"
):
    print(chunk)  # Only updates

# Stream messages (for chat)
for chunk in graph.stream(
    {"messages": [HumanMessage(content="Hello")]},
    stream_mode="messages"
):
    print(chunk)  # Message updates
```

### Streaming Values

Stream full state:

```python
def stream_values_example():
    """Stream full state after each node."""
    graph = build_graph()

    for state in graph.stream({"input": "test"}):
        print(f"Current state: {state}")
        # state contains all fields

# Example output:
# Current state: {"input": "test", "step": "processed"}
# Current state: {"input": "test", "step": "processed", "result": "final"}
```

### Streaming Updates

Stream only updates:

```python
def stream_updates_example():
    """Stream only node updates."""
    graph = build_graph()

    for node_name, updates in graph.stream(
        {"input": "test"},
        stream_mode="updates"
    ):
        print(f"Node {node_name} updated: {updates}")

# Example output:
# Node process updated: {"step": "processed"}
# Node finalize updated: {"result": "final"}
```

### Streaming Messages

Stream message updates:

```python
def stream_messages_example():
    """Stream message updates for chat."""
    graph = build_chat_graph()

    for message_chunk in graph.stream(
        {"messages": [HumanMessage(content="Hello")]},
        stream_mode="messages"
    ):
        print(message_chunk.content, end="", flush=True)

# Example output:
# Hello! How can I help you today?
```

### Custom Streaming

Implement custom streaming:

```python
class StreamingNode(BaseNode):
    def execute(self, state, runtime):
        """Node with custom streaming."""
        if runtime and runtime.stream:
            # Stream intermediate results
            for i in range(10):
                result = process_chunk(i)
                runtime.stream.send(result)

        return {"complete": True}
```

---

## Advanced Configuration

### Recursion Limit

Limit graph iterations:

```python
def build_with_recursion_limit():
    """Build graph with recursion limit."""
    builder = StateGraph(State)

    # Add nodes with potential loop
    builder.add_node("process", ProcessNode())

    builder.add_edge(START, "process")

    builder.add_conditional_edges(
        "process",
        should_continue,
        {
            "continue": "process",  # Loop
            "end": END
        }
    )

    # Compile with recursion limit
    graph = builder.compile(
        checkpointer=MemorySaver()
    )

    return graph

# Usage with recursion limit in config
config = RunnableConfig(
    recursion_limit=100  # Max 100 iterations
)

result = graph.invoke({"input": "test"}, config=config)
```

### Debug Mode

Enable debug output:

```python
# Enable debug mode
graph = builder.compile(debug=True)

# Or in config
config = RunnableConfig(
    tags=["debug"],
    metadata={"debug": True}
)

result = graph.invoke({"input": "test"}, config=config)
```

### Custom Config

Custom configuration values:

```python
# Set custom config
config = RunnableConfig(
    configurable={
        "thread_id": "thread-123",
        "model_name": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1000
    }
)

result = graph.invoke({"input": "test"}, config=config)

# Access in nodes
class ConfigAwareNode(BaseNode):
    def execute(self, state, config):
        if config:
            model_name = config.get("configurable", {}).get("model_name")
            temperature = config.get("configurable", {}).get("temperature")
            # Use configuration
        return {}
```

### Retry Policy

Implement retry policy:

```python
from langgraph.graph import RetryPolicy

# Configure retry policy
retry_policy = RetryPolicy(
    max_attempts=3,
    backoff_factor=2.0,
    initial_delay=1.0
)

# Use in compilation (feature may vary)
# Check LangGraph documentation for current retry configuration
```

---

## Execution Modes

### invoke() - Synchronous

Synchronous execution:

```python
graph = builder.compile()

# Basic invocation
result = graph.invoke({"input": "test"})

# With config
config = RunnableConfig(
    configurable={"thread_id": "thread-123"}
)
result = graph.invoke({"input": "test"}, config=config)

# Returns final state
print(result["output"])
```

### ainvoke() - Asynchronous

Asynchronous execution:

```python
graph = builder.compile()

async def run_async():
    # Async invocation
    result = await graph.ainvoke({"input": "test"})

    # With config
    config = RunnableConfig(
        configurable={"thread_id": "thread-123"}
    )
    result = await graph.ainvoke({"input": "test"}, config=config)

    return result

# Run
import asyncio
result = asyncio.run(run_async())
```

### stream() - Streaming

Synchronous streaming:

```python
graph = builder.compile()

# Stream execution
for chunk in graph.stream({"input": "test"}):
    print(chunk)

# With config
config = RunnableConfig(
    configurable={"thread_id": "thread-123"}
)
for chunk in graph.stream({"input": "test"}, config=config):
    process(chunk)

# Stream with mode
for chunk in graph.stream(
    {"input": "test"},
    stream_mode="updates"
):
    print(chunk)
```

### astream() - Async Streaming

Asynchronous streaming:

```python
graph = builder.compile()

async def run_stream():
    # Async streaming
    async for chunk in graph.astream({"input": "test"}):
        print(chunk)

    # With config
    config = RunnableConfig(
        configurable={"thread_id": "thread-123"}
    )
    async for chunk in graph.astream({"input": "test"}, config=config):
        await process(chunk)

# Run
import asyncio
asyncio.run(run_stream())
```

---

## Thread Management

### Thread IDs

Manage conversation threads:

```python
# Create thread for user
def create_user_thread(user_id):
    """Create thread for user."""
    thread_id = f"user-{user_id}"
    return thread_id

# Use thread
config = RunnableConfig(
    configurable={"thread_id": create_user_thread("123")}
)

result = graph.invoke({"input": "Hello"}, config=config)
```

### Thread State

Access thread state:

```python
from langgraph.checkpoint import Checkpoint

def get_thread_state(graph, thread_id):
    """Get current state of thread."""
    config = RunnableConfig(
        configurable={"thread_id": thread_id}
    )

    # Get current checkpoint
    state = graph.get_state(config)

    return state

# Usage
state = get_thread_state(graph, "thread-123")
print(state)
```

### Multi-User Support

Support multiple users:

```python
def handle_user_request(user_id, message):
    """Handle request from user."""
    # Create thread for user
    thread_id = f"user-{user_id}"

    config = RunnableConfig(
        configurable={"thread_id": thread_id},
        metadata={"user_id": user_id}
    )

    # Execute for this user's thread
    result = graph.invoke(
        {"messages": [HumanMessage(content=message)]},
        config=config
    )

    return result

# Handle multiple users concurrently
user1_result = handle_user_request("user-1", "Hello")
user2_result = handle_user_request("user-2", "Hi")
```

---

## Best Practices

### 1. Always use checkpointer in production

```python
# ✅ Production
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver.from_conn_string(connection_string)
graph = builder.compile(checkpointer=checkpointer)

# ❌ Development only
graph = builder.compile()  # No persistence
```

### 2. Use appropriate store

```python
# ✅ Production - persistent store
from langgraph.store.postgres import PostgresStore

store = PostgresStore.from_conn_string(connection_string)

# ❌ Development only
from langgraph.store.memory import InMemoryStore
store = InMemoryStore()  # Lost on restart
```

### 3. Set recursion limits

```python
# ✅ Prevent infinite loops
config = RunnableConfig(
    recursion_limit=100
)
result = graph.invoke(input_data, config=config)
```

### 4. Use thread IDs consistently

```python
# ✅ Consistent thread IDs
thread_id = f"user-{user_id}-session-{session_id}"

# ❌ Random thread IDs
import uuid
thread_id = str(uuid.uuid4())  # Can't resume
```

### 5. Handle interrupts gracefully

```python
# ✅ Check for interrupts
result = graph.invoke(input_data, config=config)

if result.get("interrupted"):
    # Handle interrupt
    pass
else:
    # Process result
    pass
```

---

## Common Patterns

### Pattern: Chat Application

```python
def build_chat():
    """Build chat application with memory."""
    builder = StateGraph(State)

    builder.add_node("chat", ChatNode())

    builder.add_edge(START, "chat")
    builder.add_edge("chat", END)

    checkpointer = PostgresSaver.from_conn_string(connection_string)
    graph = builder.compile(checkpointer=checkpointer)

    return graph

def chat_with_memory(user_id, message):
    """Chat with memory."""
    graph = build_chat()

    config = RunnableConfig(
        configurable={"thread_id": f"user-{user_id}"}
    )

    result = graph.invoke(
        {"messages": [HumanMessage(content=message)]},
        config=config
    )

    return result["messages"][-1].content
```

### Pattern: Human-in-the-Loop

```python
def build_hitl():
    """Human-in-the-loop pattern."""
    builder = StateGraph(State)

    builder.add_node("plan", PlanNode())
    builder.add_node("execute", ExecuteNode())

    builder.add_edge(START, "plan")
    builder.add_edge("plan", "execute")
    builder.add_edge("execute", END)

    graph = builder.compile(
        checkpointer=MemorySaver(),
        interrupt_before=["execute"]
    )

    return graph

# Usage
graph = build_hitl()
config = RunnableConfig(configurable={"thread_id": "thread-1"})

# Generate plan
result1 = graph.invoke({"task": "task"}, config=config)

# Human reviews and approves
if human_approves(result1):
    result2 = graph.invoke(None, config=config)
```

---

## Performance Optimization

### 1. Use connection pooling

```python
# Connection pool for checkpointer
checkpointer = PostgresSaver.from_conn_string(
    connection_string,
    pool_size=20,
    max_overflow=10
)
```

### 2. Batch checkpoint writes

```python
# Configure checkpoint batching
# (Check LangGraph docs for current options)
```

### 3. Use async for I/O

```python
# Use async graph for I/O-bound operations
graph = builder.compile(checkpointer=async_checkpointer)

result = await graph.ainvoke(input_data)
```

---

## Troubleshooting

### Issue: "No checkpointer provided"

**Cause:** Trying to use thread_id without checkpointer

**Fix:**
```python
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)
```

### Issue: State not persisting

**Cause:** Using MemorySaver or no checkpointer

**Fix:**
```python
# Use persistent checkpointer
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")
graph = builder.compile(checkpointer=checkpointer)
```

### Issue: "Recursion limit exceeded"

**Cause:** Infinite loop in graph

**Fix:**
```python
# Set recursion limit
config = RunnableConfig(recursion_limit=100)
result = graph.invoke(input_data, config=config)

# Or fix loop condition
def should_continue(state):
    if state.iteration >= MAX_ITER:
        return "end"
    return "continue"
```

---

## Examples

### Complete Example: Production Graph

```python
from langgraph.graph import StateGraph, START, END, RunnableConfig
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from dataclasses import dataclass

@dataclass(kw_only=True)
class State:
    messages: list
    result: str = None

def build_production_graph():
    """Build production-ready graph."""
    builder = StateGraph(State)

    builder.add_node("process", ProcessNode())
    builder.add_node("review", ReviewNode())
    builder.add_node("finalize", FinalizeNode())

    builder.add_edge(START, "process")
    builder.add_edge("process", "review")
    builder.add_edge("review", "finalize")
    builder.add_edge("finalize", END)

    # Production configuration
    checkpointer = PostgresSaver.from_conn_string(
        "postgresql://user:password@localhost/dbname"
    )
    store = PostgresStore.from_conn_string(
        "postgresql://user:password@localhost/dbname"
    )

    graph = builder.compile(
        checkpointer=checkpointer,
        store=store,
        interrupt_before=["finalize"]  # Human review
    )

    return graph

# Usage
def handle_request(user_id, request):
    """Handle user request with full features."""
    graph = build_production_graph()

    config = RunnableConfig(
        configurable={
            "thread_id": f"user-{user_id}",
        },
        metadata={
            "user_id": user_id,
            "request_time": time.time()
        },
        recursion_limit=100
    )

    # Execute
    result = graph.invoke(
        {"messages": [HumanMessage(content=request)]},
        config=config
    )

    return result
```

---

## Summary

**Key components:**
- **Checkpointer**: Saves execution state
- **Store**: Persistent key-value storage
- **Interrupts**: Pause for human input
- **Streaming**: Real-time output
- **Thread management**: Multi-user support

**Production checklist:**
- [ ] Use persistent checkpointer (PostgreSQL)
- [ ] Configure persistent store
- [ ] Set recursion limits
- [ ] Implement error handling
- [ ] Use thread IDs for users
- [ ] Enable appropriate streaming
- [ ] Configure interrupts for HITL
- [ ] Set up monitoring

**References:**
- LangGraph Persistence: https://langchain-ai.github.io/langgraph/concepts/low_level/#persistence
- Checkpointers: https://langchain-ai.github.io/langgraph/reference/checkpoints/
- Streaming: https://langchain-ai.github.io/langgraph/how-tos/streaming/
