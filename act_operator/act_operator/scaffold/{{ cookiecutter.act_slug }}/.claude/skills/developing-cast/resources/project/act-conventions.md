# Act Project Conventions

## Table of Contents

- [Directory Structure](#directory-structure)
- [CRITICAL Conventions](#critical-conventions)
- [File Templates](#file-templates)
- [Import Patterns](#import-patterns)
- [Memory Location Guidelines](#memory-location-guidelines)
- [Common Violations](#common-violations)

## When to Use This Resource
Read this for Act-specific file placement, naming conventions, and project structure requirements.

## Directory Structure

```
{{ cookiecutter.act_slug }}/
├── casts/
│   ├── __init__.py
│   ├── base_node.py              # BaseNode and AsyncBaseNode (DO NOT MODIFY)
│   ├── base_graph.py             # BaseGraph (DO NOT MODIFY)
│   │
│   └── { cast_name }/                  # Your cast implementation
│       ├── __init__.py
│       ├── graph.py              # REQUIRED: Graph class inheriting BaseGraph
│       ├── pyproject.toml
│       ├── README.md
│       │
│       └── modules/              # All cast modules live here
│           ├── __init__.py
│           ├── state.py          # REQUIRED: State schema (TypedDict/Pydantic)
│           ├── nodes.py          # REQUIRED: Node classes
│           ├── agents.py         # Optional: Agent implementations
│           ├── conditions.py     # Optional: Routing functions
│           ├── middlewares.py    # Optional: Custom middleware
│           ├── models.py         # Optional: LLM model configuration
│           ├── prompts.py        # Optional: Prompt templates
│           ├── tools.py          # Optional: Cast-specific tools
│           └── utils.py          # Optional: Utilities
│
├── tests/
│   ├── cast_tests/
│   │   └── { cast_name }_test.py
│   └── node_tests/
│       └── test_node.py
│
├── .env.example
├── langgraph.json
├── pyproject.toml
└── README.md
```

## CRITICAL Conventions

### 1. Base Class Inheritance

⚠️ **ALL nodes MUST inherit from BaseNode or AsyncBaseNode**

```python
# ✅ CORRECT
from casts.base_node import BaseNode

class MyNode(BaseNode):
    def execute(self, state) -> dict:
        ...
```

```python
# ❌ WRONG
class MyNode:  # Not inheriting from BaseNode
    def execute(self, state) -> dict:
        ...
```

⚠️ **ALL graphs MUST inherit from BaseGraph**

```python
# ✅ CORRECT
from casts.base_graph import BaseGraph

class { CastName }Graph(BaseGraph):
    def build(self) -> CompiledStateGraph:
        ...
```

### 2. Required Files Per Cast

Each cast MUST have:
- `graph.py` - Graph class (in cast root)
- `modules/state.py` - State schema
- `modules/nodes.py` - Node implementations

Optional files in `modules/`:
- `conditions.py` - Routing functions
- `agents.py` - Agent implementations
- `prompts.py` - Prompt templates
- `tools.py` - Cast-specific tools
- `models.py` - LLM configuration
- `middlewares.py` - Custom middleware
- `utils.py` - Utilities

### 3. Naming Conventions

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
- ✅ `PrivateState`
- ❌ `Private`, `private_state`

**Graph:** `PascalCase` ending in `Graph`
- ✅ `{ CastName }Graph`
- ❌ `{ CastName }`, `{ cast_name }_graph`

## File Templates

### graph.py Template

```python
"""Graph definition for { CastName }."""
from langgraph.graph import StateGraph, START, END
from casts.base_graph import BaseGraph

from casts.{ cast_name }.modules.state import State
from casts.{ cast_name }.modules.nodes import Node1, Node2, Node3
from casts.{ cast_name }.modules.conditions import should_continue

class { CastName }Graph(BaseGraph):
    """Main graph for { CastName }."""

    def build(self) -> CompiledStateGraph:
        """Build and compile the graph."""
        builder = StateGraph(State)

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
"""State schema."""
from typing import TypedDict, Annotated
from langgraph.graph import add

class State(TypedDict):
    """State for graph."""
    input: str
    messages: Annotated[list[dict], add]
    result: str | None
```

### nodes.py Template

```python
"""Node implementations for { CastName }."""
from casts.base_node import BaseNode, AsyncBaseNode

class WritingAgentTeam(BaseNode):
    """First processing node."""

    def execute(self, state) -> dict:
        """Process input."""
        return {"processed": True}

class Retriever(AsyncBaseNode):
    """Async second node."""

    async def execute(self, state) -> dict:
        """Async processing."""
        result = await async_operation()
        return {"result": result}
```

### conditions.py Template

```python
"""Routing functions for { CastName }."""
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

### In graph.py (Absolute Imports)
```python
# casts/{ cast_name }/graph.py
from langgraph.graph import END, START, StateGraph

from casts.base_graph import BaseGraph
from casts.{ cast_name }.modules.state import State
from casts.{ cast_name }.modules.nodes import Node1, Node2
from casts.{ cast_name }.modules.conditions import should_continue
```

**In modules/*.py (Mixed Imports):**
```python
# Base classes (absolute imports)
from casts.base_node import BaseNode
from casts.base_graph import BaseGraph

# Sibling modules (relative imports)
from .tools import my_tool
from .models import get_llm
from .prompts import SYSTEM_PROMPT
```

## Memory Location Guidelines

**Checkpointer:** Always in graph.py compilation
```python
# casts/{ cast_name }/graph.py
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
# casts/{ cast_name }/modules/state.py
class State(TypedDict):
    conversation_history: list[dict]  # In-session memory
```

## Configuration Management

**Environment variables:**
```python
import os

api_key = os.getenv("API_KEY")
```

Use `.env` file for local development and environment variables in production.

## Common Violations

❌ **State/nodes not in modules directory**
```
casts/{ cast_name }/state.py  # ❌ WRONG
casts/{ cast_name }/modules/state.py  # ✓ CORRECT
```

❌ **Not inheriting from base classes**
```python
class MyNode:  # ❌ Missing BaseNode
```

❌ **Missing required files**
```
casts/{ cast_name }/
├── graph.py  # ✓
└── modules/
    └── (missing state.py and nodes.py)  # ❌
```

❌ **Using relative imports in graph.py**
```python
# casts/{ cast_name }/graph.py
from .modules.state import State  # ❌ WRONG
from casts.{ cast_name }.modules.state import State  # ✓ CORRECT
```

