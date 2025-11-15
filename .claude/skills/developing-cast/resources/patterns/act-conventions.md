# Act Project Conventions

## When to Use This Resource
**READ THIS FIRST before implementing any cast component.** Essential reference for file structure, base class requirements, and non-negotiable placement rules.

---

## Critical Rules (Non-Negotiable)

### 1. File Structure

**Cast directory structure:**
```
casts/cast_name/
  ├── state.py           # State schemas (REQUIRED)
  ├── nodes.py           # Node implementations (REQUIRED)
  ├── graph.py           # Graph definition (REQUIRED)
  ├── conditions.py      # Routing functions (if conditional edges)
  └── modules/
      └── tools/         # Tools ONLY here (STRICT - see rule #3)
          ├── __init__.py
          └── *.py       # Individual tool files
```

**NOT:**
```
❌ modules/state.py          # Wrong - state.py at cast root
❌ nodes/my_node.py          # Wrong - nodes.py at cast root
❌ tools/web_search.py       # Wrong - must be in modules/tools/
❌ graph/main.py             # Wrong - graph.py at cast root
```

---

### 2. Base Class Inheritance (REQUIRED)

#### All Nodes Must Inherit from BaseNode

```python
# ✓ CORRECT
from casts.base_node import BaseNode

class MyNode(BaseNode):
    """Node doing X."""

    def __init__(self):
        super().__init__()

    def execute(self, state: dict) -> dict:
        """Execute node logic."""
        return {"key": "value"}
```

```python
# ❌ WRONG - Standalone function
def my_node(state: dict) -> dict:
    return {"key": "value"}
```

**Why:** BaseNode provides logging, error handling, and common patterns. Always inherit.

---

#### All Graphs Must Inherit from BaseGraph

```python
# ✓ CORRECT
from casts.base_graph import BaseGraph
from langgraph.graph import StateGraph

class MyCastGraph(BaseGraph):
    """Graph for my cast."""

    def __init__(self):
        super().__init__()
        self.state = MyState

    def build(self):
        """Builds and returns compiled graph."""
        builder = StateGraph(self.state)
        # ... add nodes, edges ...
        return builder.compile()
```

```python
# ❌ WRONG - Direct StateGraph without BaseGraph
from langgraph.graph import StateGraph

def build_graph():
    builder = StateGraph(MyState)
    # ...
    return builder.compile()
```

**Why:** BaseGraph provides graph lifecycle management, naming, and Act-specific patterns.

---

### 3. Tool Placement (STRICT)

**Tools ONLY in `modules/tools/` - NO EXCEPTIONS**

```python
# ✓ CORRECT: casts/my_cast/modules/tools/web_search.py
from langchain_core.tools import tool

@tool
def web_search(query: str) -> list:
    """Searches the web."""
    return []
```

**WRONG locations:**
- ❌ `casts/my_cast/tools/` - Missing modules/ parent
- ❌ `casts/my_cast/nodes.py` - Tools not in nodes file
- ❌ `casts/my_cast/graph.py` - Tools not in graph file
- ❌ `modules/tools.py` - Must be in tools/ directory
- ❌ `casts/my_cast/modules/web_search.py` - Must be in tools/ subdirectory

**Why:** Act convention for tool organization and imports. This is strictly enforced.

---

### 4. Import Patterns

**Importing within a cast:**

```python
# In graph.py
from casts.my_cast.state import MyState
from casts.my_cast.nodes import MyNode, AnotherNode
from casts.my_cast.conditions import route_mode
from casts.my_cast.modules.tools.web_search import web_search

# NOT relative imports like:
# from .state import MyState  ❌
```

**Importing base classes:**

```python
from casts.base_node import BaseNode
from casts.base_graph import BaseGraph
```

---

## BaseNode API

### Required Methods

```python
class MyNode(BaseNode):
    def __init__(self, param=None):
        """Initialize node.

        Args:
            param: Optional configuration
        """
        super().__init__()  # REQUIRED
        self.param = param

    def execute(self, state: dict, **kwargs) -> dict:
        """Execute node logic.

        Args:
            state: Current graph state
            **kwargs: Optional runtime, config, store

        Returns:
            dict: State updates
        """
        # Your logic here
        self.log("Doing something", detail=self.param)
        return {"result": "value"}
```

### Optional Runtime Context

```python
def execute(self, state: dict, runtime=None, config=None) -> dict:
    """Execute with runtime context access."""

    # Access Store for long-term memory
    if runtime and runtime.store:
        namespace = ("my_cast", "data")
        runtime.store.put(namespace, "key", {"value": "data"})

    # Access config
    if config:
        thread_id = config.get("configurable", {}).get("thread_id")

    return {"updated": "state"}
```

### Logging

```python
def execute(self, state: dict) -> dict:
    # Use self.log() for debugging (shows when verbose=True)
    self.log("Processing started", item_count=len(state.get("items", [])))

    # ... logic ...

    self.log("Processing complete")
    return {"status": "done"}
```

---

## BaseGraph API

### Required Methods

```python
from casts.base_graph import BaseGraph
from langgraph.graph import StateGraph

class MyCastGraph(BaseGraph):
    def __init__(self):
        """Initialize graph."""
        super().__init__()  # REQUIRED
        self.state = MyState  # Set state schema

    def build(self):
        """Build and return compiled graph.

        Returns:
            CompiledStateGraph
        """
        builder = StateGraph(self.state)

        # Add nodes (as INSTANCES, not classes)
        builder.add_node("my_node", MyNode())

        # Add edges
        builder.add_edge("my_node", END)

        # Compile
        graph = builder.compile()
        graph.name = self.name  # Set from BaseGraph

        return graph
```

### With Checkpointer and Store

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

class MyCastGraph(BaseGraph):
    def build(self):
        builder = StateGraph(self.state)
        # ... nodes and edges ...

        # Add persistence
        checkpointer = MemorySaver()
        store = InMemoryStore()

        graph = builder.compile(
            checkpointer=checkpointer,
            store=store
        )
        graph.name = self.name

        return graph
```

---

## File Content Guidelines

### state.py

```python
"""State schema for MyCast."""

from typing_extensions import TypedDict
from typing import Annotated
import operator

class MyState(TypedDict):
    """State for my cast.

    Attributes:
        messages: Conversation history (append-only)
        result: Processing result (overwrite)
    """
    messages: Annotated[list, operator.add]  # Reducer
    result: str  # Plain field
```

---

### nodes.py

```python
"""Node implementations for MyCast."""

from casts.base_node import BaseNode

class MyNode(BaseNode):
    """Does X."""

    def __init__(self):
        super().__init__()

    def execute(self, state: dict) -> dict:
        return {"result": "done"}

class AnotherNode(BaseNode):
    """Does Y."""

    def __init__(self, model=None):
        super().__init__()
        self.model = model

    def execute(self, state: dict) -> dict:
        return {"result": "done"}
```

---

### conditions.py

```python
"""Routing functions for MyCast."""

def route_mode(state: dict) -> str:
    """Route based on mode.

    Args:
        state: Current state

    Returns:
        Next node name
    """
    mode = state.get("mode", "default")

    if mode == "search":
        return "SearchNode"
    else:
        return "ChatNode"
```

---

### graph.py

```python
"""Graph definition for MyCast."""

from casts.base_graph import BaseGraph
from langgraph.graph import StateGraph, END
from casts.my_cast.state import MyState
from casts.my_cast.nodes import MyNode, AnotherNode

class MyCastGraph(BaseGraph):
    """Graph for MyCast."""

    def __init__(self):
        super().__init__()
        self.state = MyState

    def build(self):
        builder = StateGraph(self.state)

        builder.add_node("my_node", MyNode())
        builder.add_node("another_node", AnotherNode())

        builder.add_edge("my_node", "another_node")
        builder.add_edge("another_node", END)
        builder.set_entry_point("my_node")

        return builder.compile()

# Export instance
my_cast_graph = MyCastGraph()
```

---

## Anti-Patterns

### ❌ Don't: Tools Outside modules/tools/

```python
# ❌ WRONG: casts/my_cast/tools.py
from langchain_core.tools import tool

@tool
def my_tool():
    pass
```

### ❌ Don't: Nodes as Functions

```python
# ❌ WRONG: Standalone function
def my_node(state):
    return {"result": "value"}
```

### ❌ Don't: Graph Without BaseGraph

```python
# ❌ WRONG: Direct StateGraph
def create_graph():
    builder = StateGraph(MyState)
    return builder.compile()
```

---

## Decision Framework

**Q: Where do I put X?**

| Component | Location | Base Class |
|-----------|----------|------------|
| State schema | `state.py` (cast root) | TypedDict |
| Nodes | `nodes.py` (cast root) | BaseNode |
| Tools | `modules/tools/*.py` | @tool |
| Routing | `conditions.py` (cast root) | None (functions) |
| Graph | `graph.py` (cast root) | BaseGraph |

**Q: Do I need BaseNode/BaseGraph?**
- ✓ YES - Always required for Act projects

**Q: Can I put tools in nodes.py?**
- ✗ NO - Tools ONLY in modules/tools/

**Q: Can I use standalone functions for nodes?**
- ✗ NO - Must inherit from BaseNode

---

## Verification Checklist

Before considering cast complete:

**File Structure:**
- [ ] state.py at cast root
- [ ] nodes.py at cast root
- [ ] graph.py at cast root
- [ ] conditions.py at cast root (if needed)
- [ ] All tools in modules/tools/

**OOP Compliance:**
- [ ] All nodes inherit from BaseNode
- [ ] Graph inherits from BaseGraph
- [ ] All nodes implement execute(self, state)
- [ ] super().__init__() called in all __init__ methods

**Imports:**
- [ ] Absolute imports (casts.my_cast.X)
- [ ] Base classes imported correctly
- [ ] No relative imports

**Functionality:**
- [ ] Graph compiles without errors
- [ ] Nodes return dict with state updates
- [ ] Tools are importable and working

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Tools in wrong location | Move to modules/tools/ |
| Forgot to inherit BaseNode | Add `(BaseNode)` to class |
| Forgot to inherit BaseGraph | Add `(BaseGraph)` to class |
| Relative imports | Use absolute: `from casts.X.Y` |
| Standalone node functions | Convert to BaseNode class |
| Missing super().__init__() | Add in __init__ method |
| State in modules/ | Move to cast root |

---

## Key Takeaways

1. **File structure is strict** - Follow the pattern exactly
2. **Always inherit base classes** - BaseNode, BaseGraph required
3. **Tools ONLY in modules/tools/** - No exceptions
4. **Use absolute imports** - from casts.X.Y pattern
5. **OOP throughout** - Classes, not functions

**When in doubt, check this resource first.**
