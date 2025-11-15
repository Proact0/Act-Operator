# Cast Structure Guide

Directory layout and file organization for Act casts.

## Standard Cast Structure

```
casts/
├── base_node.py           # BaseNode and AsyncBaseNode classes
├── base_graph.py          # BaseGraph class
├── __init__.py           # Export base classes
└── my_cast/              # Individual cast directory
    ├── __init__.py       # Export graph
    ├── graph.py          # Main graph implementation
    ├── pyproject.toml    # Cast-specific dependencies (optional)
    ├── README.md         # Cast documentation
    └── modules/          # Cast modules
        ├── __init__.py
        ├── state.py      # State schema (TypedDict)
        ├── agents.py     # Agent node implementations
        ├── tools.py      # Tool definitions
        ├── models.py     # LLM configurations
        ├── prompts.py    # Prompt templates
        ├── middlewares.py # Middleware functions
        └── utils.py      # Utility functions
```

## File Purposes

### Base Files (shared across all casts)

**`base_node.py`**
- `BaseNode`: Synchronous node base class
- `AsyncBaseNode`: Async node base class
- Provides `.execute()` abstraction
- Handles config and runtime injection

**`base_graph.py`**
- `BaseGraph`: Graph base class
- Provides `.build()` abstraction
- Returns `CompiledStateGraph`

### Cast Files

**`graph.py`** (required)
- Main graph implementation
- Extends `BaseGraph`
- Defines state schema, nodes, edges
- Example:
```python
from langgraph.graph import StateGraph
from ..base_graph import BaseGraph
from .modules.state import MyState

class MyGraph(BaseGraph):
    def build(self):
        builder = StateGraph(MyState)
        # Add nodes and edges
        return builder.compile()
```

**`__init__.py`** (required)
- Exports the graph
- Example:
```python
from .graph import MyGraph

__all__ = ["MyGraph"]
```

**`pyproject.toml`** (optional)
- Cast-specific dependencies
- Separate from root project deps
- Used when cast needs unique packages

### Module Files

**`modules/state.py`**
- State schema definition (TypedDict or Pydantic)
- Reducers for accumulating fields
- Input/output state schemas
- Example:
```python
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph import add_messages

class MyState(TypedDict):
    messages: Annotated[list, add_messages]
    result: str | None
```

**`modules/agents.py`**
- Node implementations extending BaseNode
- Agent logic (LLM calls, decisions)
- Example:
```python
from ...base_node import BaseNode

class MyAgentNode(BaseNode):
    def execute(self, state):
        # Agent logic
        return {"result": "..."}
```

**`modules/tools.py`**
- LangChain tools using `@tool` decorator
- TOOLS list for agent binding
- Example:
```python
from langchain_core.tools import tool

@tool
def my_tool(query: str) -> str:
    """Tool description."""
    return f"Result: {query}"

TOOLS = [my_tool]
```

**`modules/models.py`**
- LLM model configurations
- Factory functions for models
- Example:
```python
from langchain_anthropic import ChatAnthropic

def get_model():
    return ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        temperature=0.7
    )
```

**`modules/prompts.py`**
- Prompt templates
- System prompts
- Example:
```python
from langchain_core.prompts import ChatPromptTemplate

SYSTEM_PROMPT = "You are a helpful assistant."

def get_prompt():
    return ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("placeholder", "{messages}"),
    ])
```

**`modules/middlewares.py`**
- Middleware functions
- Logging, validation, transformations
- Applied to graph execution

**`modules/utils.py`**
- Helper functions
- Data transformations
- Shared utilities

## Workspace Configuration

Root `pyproject.toml` includes casts in workspace:

```toml
[tool.uv.workspace]
members = ["casts/*"]
exclude = [
    "casts/__pycache__",
    "casts/**/__pycache__",
]
```

This allows:
- Cast-specific dependencies
- Independent versioning
- Shared base classes

## Minimal vs Full Structure

**Minimal** (for simple graphs):
```
my_cast/
├── __init__.py
├── graph.py
└── modules/
    └── state.py
```

**Full** (for complex graphs):
```
my_cast/
├── __init__.py
├── graph.py
├── pyproject.toml
├── README.md
└── modules/
    ├── state.py
    ├── agents.py
    ├── tools.py
    ├── models.py
    ├── prompts.py
    ├── middlewares.py
    └── utils.py
```

## Creating Casts

### Manual (minimal structure)
```bash
uv run act cast -c "My Cast"
```

### Automated (full boilerplate)
```bash
uv run python .claude/skills/engineering-act/scripts/create_cast.py "My Cast"
```

## Import Patterns

### From cast modules
```python
from .modules.state import MyState
from .modules.agents import MyAgentNode
from .modules.tools import TOOLS
from .modules.models import get_model
```

### From base classes
```python
from ..base_node import BaseNode, AsyncBaseNode
from ..base_graph import BaseGraph
```

### External imports
```python
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from langchain_anthropic import ChatAnthropic
```

## Best Practices

✓ One graph per cast directory
✓ Use modules/ for organization
✓ Extend base classes (BaseNode, BaseGraph)
✓ Keep state.py focused on schema only
✓ Separate concerns (agents, tools, models, prompts)
✓ Document each module's purpose

❌ Don't mix multiple graphs in one cast
❌ Don't put logic in __init__.py
❌ Don't duplicate base class code
❌ Don't skip type hints
❌ Don't forget docstrings
