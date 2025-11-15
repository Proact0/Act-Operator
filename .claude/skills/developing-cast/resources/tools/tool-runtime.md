# Tool Runtime (Act-Specific)

## When to Use This Resource
Read when tools need access to Store, config, or runtime context - especially for long-term memory in tools.

---

## What is ToolRuntime?

**ToolRuntime** provides tools and nodes access to:
- **Store**: Long-term, cross-session memory
- **Config**: Invocation configuration (thread_id, etc.)
- **Runtime context**: Graph execution environment

**Act-specific pattern** for context access in tools and nodes.

---

## Accessing Runtime in Tools

### Tool with Store Access

```python
# File: casts/my_cast/modules/tools/save_preference.py

from langchain_core.tools import tool
from typing import Optional, Any

@tool
def save_user_preference(
    key: str,
    value: str,
    runtime: Optional[Any] = None
) -> str:
    """Saves user preference to long-term memory.

    Args:
        key: Preference key (e.g., "theme", "language")
        value: Preference value
        runtime: Runtime context with Store access

    Returns:
        Confirmation message
    """
    if runtime and runtime.store:
        namespace = ("user_preferences",)
        runtime.store.put(namespace, key, {"value": value})
        return f"Saved preference: {key} = {value}"

    return "Store not available - preference not saved"
```

**Key points:**
- Add `runtime` parameter (optional, defaults to None)
- Check `if runtime and runtime.store` before using
- Access Store via `runtime.store`

---

### Tool Retrieving from Store

```python
@tool
def get_user_preference(
    key: str,
    runtime: Optional[Any] = None
) -> str:
    """Retrieves user preference from long-term memory.

    Args:
        key: Preference key to retrieve
        runtime: Runtime context with Store access

    Returns:
        Preference value or "not found"
    """
    if runtime and runtime.store:
        namespace = ("user_preferences",)

        try:
            item = runtime.store.get(namespace, key)
            if item:
                return item.value.get("value", "not found")
        except Exception as e:
            return f"Error: {e}"

    return "not found"
```

**See:** `memory/long-term-memory.md` for comprehensive Store patterns

---

## Runtime in Nodes

### Node with Store Access

```python
from casts.base_node import BaseNode

class MemoryNode(BaseNode):
    """Node that uses long-term memory."""

    def __init__(self):
        super().__init__()

    def execute(self, state: dict, runtime=None) -> dict:
        """Execute with Store access.

        Args:
            state: Graph state
            runtime: Runtime context

        Returns:
            State updates
        """
        topic = state.get("topic")

        if runtime and runtime.store:
            namespace = ("research", "topics")

            # Save current topic
            runtime.store.put(
                namespace,
                topic,
                {"topic": topic, "timestamp": "now"}
            )

            # Retrieve all topics
            items = runtime.store.search(namespace)
            all_topics = [item.value["topic"] for item in items]

            self.log(f"Stored {len(all_topics)} topics")

            return {"topics": all_topics}

        return {"topics": [topic]}  # Fallback without Store
```

---

### Node with Config Access

```python
class ThreadAwareNode(BaseNode):
    """Node that uses thread_id from config."""

    def execute(self, state: dict, config=None) -> dict:
        """Execute with config access.

        Args:
            state: Graph state
            config: Invocation config

        Returns:
            State updates
        """
        thread_id = "unknown"

        if config:
            thread_id = config.get("configurable", {}).get("thread_id", "unknown")

        self.log(f"Running in thread: {thread_id}")

        return {"thread_id": thread_id}
```

---

## Store Operations

### Put (Save Data)

```python
if runtime and runtime.store:
    namespace = ("cast_name", "data_type")
    key = "unique_key"
    value = {"field": "data", "count": 5}

    runtime.store.put(namespace, key, value)
```

**Namespaces organize data** - tuple like `("cast_name", "category")`

---

### Get (Retrieve Single Item)

```python
if runtime and runtime.store:
    namespace = ("cast_name", "data_type")
    key = "unique_key"

    item = runtime.store.get(namespace, key)

    if item:
        data = item.value  # dict you stored
        field_value = data.get("field")
```

---

### Search (Retrieve Multiple Items)

```python
if runtime and runtime.store:
    namespace = ("cast_name", "data_type")

    # Get all items in namespace
    items = runtime.store.search(namespace)

    # Extract values
    all_data = [item.value for item in items]

    # Process
    for data in all_data:
        topic = data.get("topic")
```

---

### Delete (Remove Data)

```python
if runtime and runtime.store:
    namespace = ("cast_name", "data_type")
    key = "unique_key"

    runtime.store.delete(namespace, key)
```

---

## Namespace Conventions

### Recommended Structure

```python
# Cast-specific data
namespace = ("cast_name", "data_category")

# Examples:
("research_assistant", "topics")          # Research topics
("chat", "user_preferences")              # User preferences
("workflow", "saved_states")              # Saved workflow states
("analytics", "events")                   # Event tracking
```

**Best practices:**
- First element: cast name or domain
- Second element: data category
- Keep consistent across cast
- Use specific names ("topics" not "data")

---

## Complete Tool Example

```python
# File: casts/research/modules/tools/manage_topics.py

from langchain_core.tools import tool
from typing import Optional, Any, List

@tool
def save_research_topic(
    topic: str,
    description: str = "",
    runtime: Optional[Any] = None
) -> str:
    """Saves a research topic to long-term memory.

    Args:
        topic: Research topic name
        description: Optional topic description
        runtime: Runtime context

    Returns:
        Confirmation message
    """
    if not runtime or not runtime.store:
        return "Store not available"

    namespace = ("research_assistant", "topics")

    # Save with metadata
    runtime.store.put(
        namespace,
        topic,
        {
            "topic": topic,
            "description": description,
            "timestamp": "now"  # Use actual timestamp in production
        }
    )

    return f"Saved topic: {topic}"


@tool
def get_all_research_topics(
    runtime: Optional[Any] = None
) -> List[str]:
    """Retrieves all saved research topics.

    Args:
        runtime: Runtime context

    Returns:
        List of research topics
    """
    if not runtime or not runtime.store:
        return []

    namespace = ("research_assistant", "topics")

    items = runtime.store.search(namespace)
    topics = [item.value.get("topic", "") for item in items]

    return topics


@tool
def delete_research_topic(
    topic: str,
    runtime: Optional[Any] = None
) -> str:
    """Deletes a research topic from memory.

    Args:
        topic: Topic to delete
        runtime: Runtime context

    Returns:
        Confirmation message
    """
    if not runtime or not runtime.store:
        return "Store not available"

    namespace = ("research_assistant", "topics")

    try:
        runtime.store.delete(namespace, topic)
        return f"Deleted topic: {topic}"
    except Exception as e:
        return f"Error deleting: {e}"
```

---

## Passing Runtime to Tools

### Automatic (LLM + ToolNode)

```python
from langgraph.prebuilt import ToolNode
from casts.my_cast.modules.tools.manage_topics import save_research_topic

# Create ToolNode
tools = [save_research_topic]
tool_node = ToolNode(tools)

# In graph
builder.add_node("tools", tool_node)

# ToolNode automatically passes runtime to tools
```

**ToolNode handles runtime automatically** - you don't need to pass it.

---

### Manual (Direct Invoke in Node)

```python
from casts.my_cast.modules.tools.save_preference import save_user_preference

class PreferenceNode(BaseNode):
    def execute(self, state: dict, runtime=None) -> dict:
        # Manually pass runtime to tool
        result = save_user_preference.invoke({
            "key": "theme",
            "value": "dark",
            "runtime": runtime  # Pass explicitly
        })

        return {"result": result}
```

**When invoking directly, pass runtime explicitly**

---

## Runtime vs Config vs Store

### Runtime

**Contains:** Store, config, and other graph context

```python
def execute(self, state: dict, runtime=None) -> dict:
    if runtime:
        store = runtime.store  # Access Store
        # May contain other context
```

---

### Config

**Contains:** Invocation-specific configuration

```python
def execute(self, state: dict, config=None) -> dict:
    if config:
        thread_id = config.get("configurable", {}).get("thread_id")
        # Other config values
```

---

### Store

**Contains:** Long-term memory interface

```python
def execute(self, state: dict, runtime=None) -> dict:
    if runtime and runtime.store:
        runtime.store.put(namespace, key, value)
        runtime.store.get(namespace, key)
        runtime.store.search(namespace)
```

---

## Anti-Patterns

### ❌ Assuming Runtime Exists

```python
@tool
def my_tool(key: str, runtime) -> str:  # ❌ Not optional
    # Will fail if runtime not passed
    runtime.store.put(...)
```

```python
@tool
def my_tool(key: str, runtime: Optional[Any] = None) -> str:  # ✓
    if runtime and runtime.store:  # ✓ Check before use
        runtime.store.put(...)
```

---

### ❌ Not Handling Missing Store

```python
@tool
def my_tool(runtime=None):
    runtime.store.put(...)  # ❌ Crashes if runtime/store missing
```

```python
@tool
def my_tool(runtime=None):
    if not runtime or not runtime.store:  # ✓ Check first
        return "Store not available"

    runtime.store.put(...)  # ✓ Safe
```

---

### ❌ Wrong Namespace Type

```python
namespace = "my_cast"  # ❌ String, should be tuple
runtime.store.put(namespace, key, value)
```

```python
namespace = ("my_cast", "data")  # ✓ Tuple
runtime.store.put(namespace, key, value)
```

---

## Decision Framework

**Q: When to use runtime in tools?**
- Tool needs Store (long-term memory) → Yes
- Tool needs config → Yes
- Tool is stateless → No (don't need runtime)

**Q: Runtime or config parameter?**
- Need Store → runtime
- Need thread_id or config → config
- Need both → runtime (contains config)

**Q: How to pass runtime to tools?**
- Using ToolNode → Automatic
- Direct invoke in node → Manual (pass explicitly)

---

## Initializing Store

### In graph.py

```python
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver

class MyCastGraph(BaseGraph):
    def build(self):
        builder = StateGraph(self.state)

        # Add nodes...

        # Initialize Store and checkpointer
        store = InMemoryStore()  # Or MongoDBStore, RedisStore
        checkpointer = MemorySaver()

        graph = builder.compile(
            checkpointer=checkpointer,
            store=store  # Pass Store here
        )

        return graph
```

**See:** `memory/long-term-memory.md` for Store types and configuration

---

## References
- memory/long-term-memory.md (comprehensive Store patterns)
- tools/tool-creation.md (basic tool creation)
- core/node-patterns.md (runtime in nodes)
- patterns/act-conventions.md (Act-specific patterns)
