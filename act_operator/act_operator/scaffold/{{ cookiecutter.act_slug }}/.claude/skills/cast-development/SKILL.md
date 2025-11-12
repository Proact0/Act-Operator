---
name: cast-development
description: Develop LangGraph Cast modules - use when creating/modifying Cast, implementing nodes, building graphs, working with Cast modules (state, nodes, agents, tools, etc.), or scaffolding new Cast components.
---

# Cast Development

**Use this skill when:**
- Creating a new Cast
- Modifying existing Cast structure
- Understanding Cast architecture
- Working with Cast modules
- Implementing nodes, state, or graph logic

## Quick Start

A Cast is an independent LangGraph graph module with:
- **graph.py**: Graph definition (extends `BaseGraph`)
- **modules/**: 8 modular components
  - **state.py** (required): State schema
  - **nodes.py** (required): Node implementations
  - agents.py, conditions.py, models.py, prompts.py, tools.py, utils.py (optional)

## Workflow

Copy this checklist and track your progress:

**Cast Development Progress:**
- [ ] Step 1: Define State schema (state.py)
- [ ] Step 2: Implement Nodes (nodes.py)
- [ ] Step 3: Build Graph structure (graph.py)
- [ ] Step 4: Add optional modules (agents, tools, prompts, etc.)
- [ ] Step 5: Write tests
- [ ] Step 6: Validate structure

### Step 1: Define State Schema

State defines the data structure passed between nodes.

```python
# modules/state.py
from dataclasses import dataclass
from typing import Annotated
from langchain.messages import AnyMessage
from langgraph.graph.message import add_messages

@dataclass(kw_only=True)
class InputState:
    """Input schema for the graph."""
    query: str

@dataclass(kw_only=True)
class OutputState:
    """Output schema for the graph."""
    messages: Annotated[list[AnyMessage], add_messages]

@dataclass(kw_only=True)
class State:
    """Internal graph state."""
    query: str
    messages: Annotated[list[AnyMessage], add_messages]
```

**For detailed state patterns**, use the `state-management` skill.

### Step 2: Implement Nodes

Nodes are the processing units in the graph. Each node extends `BaseNode` and implements `execute()`.

```python
# modules/nodes.py
from casts.base_node import BaseNode
from langchain_core.messages import AIMessage

class SampleNode(BaseNode):
    """Simple synchronous node."""

    def execute(self, state):
        """Process state and return updates."""
        return {"messages": [AIMessage(content="Processed")]}
```

**For detailed node patterns**, use the `node-implementation` skill.

### Step 3: Build Graph Structure

Graph orchestrates nodes using edges and conditional routing.

```python
# graph.py
from langgraph.graph import END, START, StateGraph
from casts.base_graph import BaseGraph
from casts.{{ cookiecutter.cast_snake }}.modules.nodes import SampleNode
from casts.{{ cookiecutter.cast_snake }}.modules.state import InputState, OutputState, State

class {{ cookiecutter.cast_pascal }}Graph(BaseGraph):
    """Graph definition for {{ cookiecutter.cast_name }}."""

    def __init__(self):
        super().__init__()
        self.input = InputState
        self.output = OutputState
        self.state = State

    def build(self):
        """Build and compile the graph."""
        builder = StateGraph(self.state, input_schema=self.input, output_schema=self.output)

        # Register nodes as instances
        builder.add_node("SampleNode", SampleNode())

        # Define edges
        builder.add_edge(START, "SampleNode")
        builder.add_edge("SampleNode", END)

        graph = builder.compile()
        graph.name = self.name
        return graph

{{ cookiecutter.cast_snake }}_graph = {{ cookiecutter.cast_pascal }}Graph()
```

**For detailed graph patterns**, use the `graph-composition` skill.

### Step 4: Add Optional Modules

Add modules as needed:
- **agents.py**: LangChain agents
- **tools.py**: LLM tools or MCP tools
- **prompts.py**: Prompt templates
- **models.py**: LLM model configurations
- **conditions.py**: Conditional routing logic
- **utils.py**: Helper functions

**For module integration**, use the `modules-integration` skill.

### Step 5: Write Tests

Create unit and integration tests.

```python
# tests/unit_tests/test_node.py
from casts.{{ cookiecutter.cast_snake }}.modules.nodes import SampleNode

def test_sample_node():
    node = SampleNode()
    result = node({"query": "test"})
    assert "messages" in result
```

**For testing patterns**, use the `testing-debugging` skill.

### Step 6: Validate Structure

Run validation to ensure proper structure:

```bash
python scripts/validate_cast.py casts/{{ cookiecutter.cast_snake }}
```

If validation fails, review errors and fix issues before continuing.

## Common Patterns

### Pattern 1: Simple Linear Graph
START → Node1 → Node2 → END

```python
builder.add_edge(START, "Node1")
builder.add_edge("Node1", "Node2")
builder.add_edge("Node2", END)
```

### Pattern 2: Conditional Routing
Use conditional edges for branching logic.

```python
def should_continue(state):
    return "continue" if state.get("retry") else "end"

builder.add_conditional_edges(
    "Node1",
    should_continue,
    {"continue": "Node2", "end": END}
)
```

### Pattern 3: Agent with Tools
Combine agents and tools for LLM interactions.

```python
# modules/tools.py
from langchain.tools import tool

@tool
def search_tool(query: str) -> str:
    """Search for information."""
    return f"Results for {query}"

# modules/nodes.py
class AgentNode(BaseNode):
    def execute(self, state):
        agent = create_agent(model, tools=[search_tool])
        response = agent.invoke(state["query"])
        return {"messages": [response]}
```

## Cast Structure

```
casts/{{ cookiecutter.cast_snake }}/
├── __init__.py
├── graph.py                    # Graph definition (required)
├── modules/
│   ├── __init__.py
│   ├── state.py                # State schema (required)
│   ├── nodes.py                # Node implementations (required)
│   ├── agents.py               # Agents (optional)
│   ├── conditions.py           # Routing conditions (optional)
│   ├── models.py               # LLM models (optional)
│   ├── prompts.py              # Prompt templates (optional)
│   ├── tools.py                # Tools (optional)
│   └── utils.py                # Utilities (optional)
├── pyproject.toml              # Package metadata
└── README.md                   # Cast documentation
```

## Troubleshooting

**Issue**: Graph doesn't appear in LangGraph Studio
- Check `langgraph.json` has correct path: `"cast-name": "./casts/cast_name/graph.py:cast_graph"`
- Restart dev server: `uv run langgraph dev`

**Issue**: Import errors for base classes
- Ensure `casts/base_node.py` and `casts/base_graph.py` exist
- Check import paths are correct

**Issue**: State updates not working
- Nodes must return `dict` with state updates
- Use proper type annotations in state dataclass

## References

**Detailed documentation:**
- Base classes API: [references/base_classes.md]
- LangGraph patterns: [references/langgraph_patterns.md]
- Workspace management: [references/workspace_guide.md]

**Complete examples:**
- Simple Cast: [examples/simple_cast/]
- Advanced Cast with agent: [examples/advanced_cast/]

**Tools:**
- Validation: `python scripts/validate_cast.py <cast-path>`

## Next Steps

- State design patterns: Use `state-management` skill
- Node implementation: Use `node-implementation` skill
- Graph composition: Use `graph-composition` skill
- Module integration: Use `modules-integration` skill
- Testing: Use `testing-debugging` skill
