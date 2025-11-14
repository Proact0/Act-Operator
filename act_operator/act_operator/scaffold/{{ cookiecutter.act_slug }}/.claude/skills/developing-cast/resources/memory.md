---
# Memory Resource
# LangGraph 1.0 Memory Patterns
---

# Memory Patterns

## Overview

Memory in LangGraph has multiple scopes. **Choose based on persistence and scope needs.**

## Short-Term Memory (3 Types)

### 1. Session State (Graph State Schema)

**Scope:** Single graph execution
**Persists:** During one `graph.invoke()` call
**Location:** State schema definition

**When to use:** Data needed across nodes in a single execution.

```python
# modules/state.py
from typing_extensions import TypedDict

class State(TypedDict):
    """Graph state with session memory."""
    query: str
    results: list[str]
    context: dict  # Session memory
    step_count: int
```

**Usage in nodes:**
```python
def execute(self, state, runtime=None, **kwargs):
    # Read session memory
    context = state.get("context", {})
    step = state.get("step_count", 0)

    # Update session memory
    context["last_action"] = "search"

    return {
        "context": context,
        "step_count": step + 1
    }
```

**Characteristics:**
- ✅ Fast (in-memory)
- ✅ Shared across all nodes in execution
- ❌ Lost after graph completes
- ❌ Not persisted between runs

### 2. Agent Scratchpad (Agent Memory)

**Scope:** Agent reasoning within node
**Persists:** During agent execution
**Location:** `modules/agents/`

**When to use:** Agent needs to track reasoning steps, tool calls, observations.

```python
# modules/nodes.py
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from .tools import search_tool

class AgentNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
        self.agent = create_react_agent(
            self.llm,
            [search_tool],
            state_modifier="You are a helpful assistant."  # Agent system prompt
        )

    def execute(self, state, runtime=None, **kwargs):
        # Agent maintains scratchpad automatically
        # Tracks: thought → action → observation cycles
        result = self.agent.invoke({
            "messages": state["messages"]
        })

        # Scratchpad is in result["messages"]
        return {"messages": result["messages"]}
```

**Characteristics:**
- ✅ Automatic with ReAct agents
- ✅ Tracks reasoning process
- ✅ Visible in messages state
- ❌ Lost after node completes
- ❌ Agent-specific, not shared across nodes

### 3. Runtime Store (Thread-Scoped)

**Scope:** Thread (conversation)
**Persists:** Across multiple graph executions in same thread
**Location:** Runtime store

**When to use:** Memory across runs in same thread/conversation.

```python
def execute(self, state, runtime=None, **kwargs):
    if not runtime or not runtime.store:
        return {}

    # Get thread_id
    config = kwargs.get("config", {})
    thread_id = config.get("configurable", {}).get("thread_id")

    if not thread_id:
        return {}

    # Namespace for organization: (category, thread_id)
    namespace = ("conversation", thread_id)

    # Read from store
    history = runtime.store.get(namespace, "history") or []

    # Update
    history.append({"query": state.get("query"), "result": "..."})

    # Write to store
    runtime.store.put(namespace, "history", history)

    return {"thread_memory": history}
```

**Characteristics:**
- ✅ Persists across runs
- ✅ Thread-scoped (isolated per conversation)
- ✅ Can store complex objects
- ❌ Requires runtime.store
- ❌ Need to manage thread_id

**Common patterns:**
```python
# Store user preferences
runtime.store.put(("prefs", thread_id), "language", "en")

# Store conversation history
runtime.store.put(("history", thread_id), "messages", messages)

# Store context
runtime.store.put(("context", thread_id), "user_data", {"name": "Alice"})

# Retrieve
language = runtime.store.get(("prefs", thread_id), "language")
```

## Choosing Short-Term Memory Type

| Use Case | Type | Reason |
|----------|------|--------|
| Pass data between nodes (same run) | Session State | Fastest, automatic |
| Agent reasoning traces | Agent Scratchpad | Built into ReAct |
| Conversation history | Runtime Store | Persists across runs |
| User preferences | Runtime Store | Per-thread persistence |
| Temporary calculation | Session State | No persistence needed |
| Multi-step agent plan | Agent Scratchpad | Agent-managed |

## Long-Term Memory

**Scope:** Cross-thread, cross-user
**Persists:** Indefinitely (database)
**Location:** External storage integration

**When to use:** Knowledge base, user profiles, historical data.

**Pattern:**
```python
# Requires external integration (database, vector store)
from modules.memory import KnowledgeBase

class ResearchNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.knowledge_base = KnowledgeBase()  # Your DB integration

    def execute(self, state, runtime=None, **kwargs):
        query = state.get("query")

        # Query long-term memory
        relevant_docs = self.knowledge_base.search(query)

        # Optionally store new knowledge
        result = self.process(query)
        self.knowledge_base.add(result)

        return {"context": relevant_docs, "result": result}
```

**Common implementations:**
- Vector databases (Pinecone, Weaviate)
- SQL databases (PostgreSQL)
- Document stores (MongoDB)
- LangChain memory classes

## LangMem Integration

**LangMem:** LangChain's memory management library.

**Setup:**
```python
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage

class MemoryNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )

    def execute(self, state, runtime=None, **kwargs):
        messages = state.get("messages", [])

        # Load memory
        chat_history = self.memory.load_memory_variables({})["chat_history"]

        # Process with memory
        context = {"history": chat_history, "current": messages}

        # Save to memory
        if messages:
            last_msg = messages[-1]
            if isinstance(last_msg, HumanMessage):
                self.memory.save_context(
                    {"input": last_msg.content},
                    {"output": "..."}  # Your response
                )

        return {"context": context}
```

**LangMem options:**
- `ConversationBufferMemory`: Full history
- `ConversationBufferWindowMemory`: Last N messages
- `ConversationSummaryMemory`: Summarized history
- `VectorStoreRetrieverMemory`: Semantic search

## Memory Decision Tree

```
What do you need to remember?
│
├─ During this run only?
│  └─ Use Session State (state schema)
│
├─ Agent reasoning steps?
│  └─ Use Agent Scratchpad (automatic with ReAct)
│
├─ Across runs in same thread?
│  └─ Use Runtime Store (thread-scoped)
│
└─ Across all threads/users?
   └─ Use Long-Term Memory (database integration)
```

## Example: Multi-Level Memory

```python
class SmartNode(BaseNode):
    """Node using all memory types."""

    def __init__(self):
        super().__init__()
        self.knowledge_base = KnowledgeBase()  # Long-term

    def execute(self, state, runtime=None, **kwargs):
        query = state.get("query")

        # 1. Session state (this run)
        session_context = state.get("context", {})

        # 2. Runtime store (this thread)
        thread_history = []
        if runtime and runtime.store:
            config = kwargs.get("config", {})
            thread_id = self.get_thread_id(config)
            if thread_id:
                thread_history = runtime.store.get(
                    ("history", thread_id),
                    "queries"
                ) or []

        # 3. Long-term (all threads)
        knowledge = self.knowledge_base.search(query)

        # Combine memories
        full_context = {
            "session": session_context,
            "thread": thread_history,
            "knowledge": knowledge
        }

        # Process
        result = self.process_with_context(query, full_context)

        # Update memories
        session_context["last_result"] = result
        thread_history.append(query)

        if runtime and runtime.store and thread_id:
            runtime.store.put(("history", thread_id), "queries", thread_history)

        return {
            "context": session_context,
            "result": result
        }
```

## Common Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| Using session state for thread memory | Use runtime store |
| Storing long-term in runtime store | Use database |
| Forgetting thread_id for store | Always get from config |
| Mutating state directly | Return updates |
| Not checking runtime.store exists | Check before using |
| Wrong namespace structure | Use (category, thread_id) tuple |

## Performance Tips

**Session State:**
- ✅ Fastest option
- ✅ Use for temporary data
- ❌ Don't store large objects

**Runtime Store:**
- ✅ Good for thread-scoped data
- ⚠️ Check existence before use
- ❌ Not for heavy read/write

**Long-Term:**
- ✅ For persistent knowledge
- ⚠️ Add caching layer
- ⚠️ Index for fast retrieval

## Next Steps

- **Using memory in nodes:** See `resources/nodes.md`
- **Agent patterns:** See `resources/agents.md` (if created)
- **State management:** See `resources/state.md`
