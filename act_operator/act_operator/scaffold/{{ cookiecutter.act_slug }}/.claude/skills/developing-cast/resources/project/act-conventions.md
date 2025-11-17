# Act Project Conventions

## When to Use This Resource
Read this for Act-specific file placement, naming conventions, and project structure requirements.

## Directory Structure

```
act_project/
├── casts/
│   ├── base_node.py              # BaseNode and AsyncBaseNode (DO NOT MODIFY)
│   ├── base_graph.py             # BaseGraph (DO NOT MODIFY)
│   │
│   └── my_cast/                  # Your cast implementation
│       ├── __init__.py
│       ├── graph.py              # REQUIRED: Graph class inheriting BaseGraph
│       ├── state.py              # REQUIRED: State schema (TypedDict/Pydantic)
│       ├── nodes.py              # REQUIRED: Node classes
│       ├── conditions.py         # Routing functions for conditional edges
│       ├── tools.py              # ❌ NO! Tools go in modules/tools/
│       │
│       ├── agents/               # Optional: If using multiple agents
│       │   ├── research_agent.py
│       │   └── writing_agent.py
│       │
│       ├── prompts/              # Optional: Prompt templates
│       │   └── system_prompts.py
│       │
│       └── middlewares/          # Optional: Custom middleware
│           └── logging_middleware.py
│
├── modules/
│   ├── tools/                    # ⚠️ ALL tools MUST live here
│   │   ├── search_tools.py
│   │   ├── data_tools.py
│   │   └── memory_tools.py
│   │
│   ├── clients/                  # Optional: API clients
│   │   └── example_api.py
│   │
│   └── utils/                    # Optional: Utilities
│       └── helpers.py
│
└── config/                       # Optional: Configuration
    ├── mcp_config.yaml
    └── settings.py
```

## CRITICAL Conventions

### 1. Tools Location

⚠️ **MUST:** All tools in `modules/tools/`
❌ **NEVER:** Tools in `casts/[cast_name]/tools.py`

**Why:** Tools should be reusable across multiple casts.

```python
# ✅ CORRECT
# modules/tools/search_tools.py
from langchain_core.tools import tool

@tool
def web_search(query: str) -> str:
    """Search the web."""
    ...
```

```python
# ❌ WRONG
# casts/my_cast/tools.py
```

### 2. Base Class Inheritance

⚠️ **ALL nodes MUST inherit from BaseNode or AsyncBaseNode**

```python
# ✅ CORRECT
from casts.base_node import BaseNode

class MyNode(BaseNode):
    def execute(self, state: dict) -> dict:
        ...
```

```python
# ❌ WRONG
class MyNode:  # Not inheriting from BaseNode
    def execute(self, state: dict) -> dict:
        ...
```

⚠️ **ALL graphs MUST inherit from BaseGraph**

```python
# ✅ CORRECT
from casts.base_graph import BaseGraph

class MyCastGraph(BaseGraph):
    def build(self) -> CompiledStateGraph:
        ...
```

### 3. Required Files Per Cast

Each cast MUST have:
- `graph.py` - Graph class
- `state.py` - State schema
- `nodes.py` - Node implementations

Optional files:
- `conditions.py` - Routing functions
- `agents/` - Multi-agent implementations
- `prompts/` - Prompt templates
- `middlewares/` - Custom middleware

### 4. Naming Conventions

**Files:** `snake_case.py`
- ✅ `research_agent.py`
- ❌ `ResearchAgent.py`

**Classes:** `PascalCase`
- ✅ `ResearchNode`
- ❌ `research_node`

**Functions:** `snake_case`
- ✅ `route_by_intent`
- ❌ `routeByIntent`

**State:** `PascalCase` ending in `State`
- ✅ `MyCastState`
- ❌ `MyState`, `my_cast_state`

**Graph:** `PascalCase` ending in `Graph`
- ✅ `MyCastGraph`
- ❌ `MyCast`, `my_cast_graph`

## File Templates

### graph.py Template

```python
"""Graph definition for MyCast."""
from langgraph.graph import StateGraph, START, END
from casts.base_graph import BaseGraph

from .state import MyCastState
from .nodes import Node1, Node2, Node3
from .conditions import should_continue

class MyCastGraph(BaseGraph):
    """Main graph for MyCast."""

    def build(self) -> CompiledStateGraph:
        """Build and compile the graph."""
        builder = StateGraph(MyCastState)

        # Instantiate nodes
        node1 = Node1()
        node2 = Node2()
        node3 = Node3()

        # Add nodes
        builder.add_node("node1", node1)
        builder.add_node("node2", node2)
        builder.add_node("node3", node3)

        # Add edges
        builder.add_edge(START, "node1")
        builder.add_conditional_edges("node1", should_continue, {...})
        builder.add_edge("node2", "node3")
        builder.add_edge("node3", END)

        return builder.compile()
```

### state.py Template

```python
"""State schema for MyCast."""
from typing import TypedDict, Annotated
from langgraph.graph import add

class MyCastState(TypedDict):
    """State for MyCast graph."""
    input: str
    messages: Annotated[list[dict], add]
    result: str | None
```

### nodes.py Template

```python
"""Node implementations for MyCast."""
from casts.base_node import BaseNode, AsyncBaseNode

class Node1(BaseNode):
    """First processing node."""

    def execute(self, state: dict) -> dict:
        """Process input."""
        return {"processed": True}

class Node2(AsyncBaseNode):
    """Async second node."""

    async def execute(self, state: dict) -> dict:
        """Async processing."""
        result = await async_operation()
        return {"result": result}
```

### conditions.py Template

```python
"""Routing functions for MyCast."""
from langgraph.graph import END

def should_continue(state: dict) -> str:
    """Decides next node based on state."""
    if state.get("complete"):
        return END
    elif state.get("error"):
        return "error_handler"
    else:
        return "next_step"

def route_by_intent(state: dict) -> str:
    """Routes based on detected intent."""
    intent = state.get("intent", "unknown")

    if intent == "search":
        return "search_node"
    elif intent == "summarize":
        return "summarize_node"
    else:
        return "default_node"
```

## Import Patterns

**Within cast:**
```python
# In casts/my_cast/graph.py
from .state import MyCastState  # Relative import within cast
from .nodes import Node1, Node2
from .conditions import should_continue
```

**From other modules:**
```python
# Importing base classes
from casts.base_node import BaseNode
from casts.base_graph import BaseGraph

# Importing tools
from modules.tools.search_tools import web_search

# Importing clients
from modules.clients.example_api import ExampleAPIClient
```

## Memory Location Guidelines

**Checkpointer:** Always in graph.py compilation
```python
# casts/my_cast/graph.py
return builder.compile(checkpointer=SqliteSaver(...))
```

**Store:** Compile-time or runtime
```python
# Option 1: Compile with store
return builder.compile(store=PostgresStore(...), checkpointer=...)

# Option 2: Access via runtime in nodes
def execute(self, state, runtime=None, **kwargs):
    if runtime and runtime.store:
        data = runtime.store.get(...)
```

**In-session memory:** In state schema
```python
# casts/my_cast/state.py
class MyCastState(TypedDict):
    conversation_history: list[dict]  # In-session memory
```

## Configuration Management

**Environment variables:**
```python
import os

api_key = os.getenv("API_KEY")
```

**Config files:**
```python
# config/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str
    model_name: str = "gpt-4"

    class Config:
        env_file = ".env"
```

## Common Violations

❌ **Tools in cast directory**
```
casts/my_cast/tools.py  # ❌ WRONG
```

❌ **Not inheriting from base classes**
```python
class MyNode:  # ❌ Missing BaseNode
```

❌ **Missing required files**
```
casts/my_cast/
├── graph.py  # ✓
└── (missing state.py and nodes.py)  # ❌
```

## References
- BaseNode: `casts/base_node.py`
- BaseGraph: `casts/base_graph.py`
- Related: `../core/implementing-nodes.md`
- Related: `../core/graph-compilation.md`
- Related: `../core/tools-integration.md`
