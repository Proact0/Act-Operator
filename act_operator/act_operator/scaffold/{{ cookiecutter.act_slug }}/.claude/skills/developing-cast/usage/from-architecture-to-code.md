# From Architecture to Code

Step-by-step guide to convert CLAUDE.md architecture specification into working code.

## Overview

This guide maps each section of CLAUDE.md to implementation files:

| CLAUDE.md Section | Implementation File | Usage Reference |
|-------------------|---------------------|-----------------|
| State Schema | `modules/state.py` | [core/state.md](core/state.md) |
| Node Specifications | `modules/nodes.py` | [core/node.md](core/node.md) |
| Edge Definitions | `graph.py` (edges) | [core/edge.md](core/edge.md) |
| Technology Stack | `modules/models.py`, `modules/tools.py` | [models/](models/), [tools/](tools/) |
| Graph Assembly | `graph.py` (build method) | [core/graph.md](core/graph.md) |

---

## Step 1: Implement State Schema

**Read from CLAUDE.md:** `State Schema` section (InputState, OutputState, OverallState tables)

**Create:** `casts/{cast_name}/modules/state.py`

### Conversion Rules

| CLAUDE.md | Code |
|-----------|------|
| InputState table | `class InputState(TypedDict)` |
| OutputState table | `class OutputState(TypedDict)` |
| OverallState table | `class State(TypedDict)` (combines Input + Output + Internal) |
| Category: Input/Output | Include in both State and Input/OutputState |
| Category: Internal | Include only in State |
| Type: `Annotated[list[...], add_messages]` | Use `MessagesState` or manual annotation |

### Example

**CLAUDE.md:**
```
### OverallState
| Field | Type | Category | Description |
|-------|------|----------|-------------|
| question | str | Input | User question |
| answer | str | Output | Generated answer |
| messages | Annotated[list[BaseMessage], add_messages] | Internal | Message history |
```

**state.py:**
```python
from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class InputState(TypedDict):
    question: str

class OutputState(TypedDict):
    answer: str

class State(TypedDict):
    question: str  # Input
    answer: str  # Output
    messages: Annotated[list[BaseMessage], add_messages]  # Internal
```

**See:** [core/state.md](core/state.md) for complete patterns

---

## Step 2: Implement Nodes

**Read from CLAUDE.md:** `Node Specifications` section (each node's Type, Responsibility, Reads, Writes)

**Create:** `casts/{cast_name}/modules/nodes.py`

### Conversion Rules

| Node Type | Base Class | Pattern |
|-----------|------------|---------|
| Input/Process/Output | `BaseNode` | Sync processing |
| Decision | `BaseNode` | Return routing key in state |
| Tool | `BaseNode` or use `ToolNode` | External API/tool calls |
| Agent (with LLM) | `BaseNode` | Use agent from `modules/agents.py` |

### Template

```python
from casts.base_node import BaseNode

class {NodeName}(BaseNode):
    """
    {Responsibility from CLAUDE.md}

    Reads: {fields from CLAUDE.md}
    Writes: {fields from CLAUDE.md}
    """

    def __init__(self):
        super().__init__(verbose=True)  # Enable logging if needed

    def execute(self, state):
        # Read fields
        input_data = state.get("{read_field}")

        # Process
        result = self._process(input_data)

        # Write fields
        return {"{write_field}": result}

    def _process(self, data):
        # Implementation logic
        return data
```

### Agent Nodes

**If Node Specification mentions LLM/Agent:**

1. Check Technology Stack for LLM provider
2. Create agent in `modules/agents.py`
3. Use agent in node

```python
# modules/agents.py
from langchain_openai import ChatOpenAI

def create_search_agent():
    model = ChatOpenAI(model="gpt-4")
    # Bind tools if specified in CLAUDE.md
    return model

# modules/nodes.py
from casts.base_node import BaseNode
from .agents import create_search_agent

class AgentNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.agent = create_search_agent()

    def execute(self, state):
        result = self.agent.invoke(state["messages"])
        return {"messages": [result]}
```

**See:** [core/node.md](core/node.md), [agents/configuration.md](agents/configuration.md)

---

## Step 3: Implement Tools (if specified)

**Read from CLAUDE.md:** `Tool Specifications` section (if exists)

**Create:** `casts/{cast_name}/modules/tools.py`

### Conversion Rules

Each tool specification becomes a `@tool` decorated function:

```python
from langchain_core.tools import tool

@tool
def {tool_name}({parameters}) -> {return_type}:
    """
    {Description from CLAUDE.md}
    """
    # Implementation
    return result
```

### Example

**CLAUDE.md:**
```
### search_web
| Attribute | Value |
|-----------|-------|
| Description | Performs web search |
| Parameters | query: str |
| Returns | str (search results) |
```

**tools.py:**
```python
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults

@tool
def search_web(query: str) -> str:
    """Performs web search."""
    search = TavilySearchResults(max_results=3)
    results = search.invoke(query)
    return str(results)
```

**See:** [tools/basic-tool.md](tools/basic-tool.md)

---

## Step 4: Implement Models

**Read from CLAUDE.md:** `Technology Stack` ’ `Additional Dependencies`

**Create:** `casts/{cast_name}/modules/models.py`

### Conversion Rules

| Dependency | Implementation |
|------------|----------------|
| `langchain-openai` | Create `ChatOpenAI` instance |
| `langchain-anthropic` | Create `ChatAnthropic` instance |
| `langchain-google-genai` | Create `ChatGoogleGenerativeAI` instance |

### Template

```python
# modules/models.py
from langchain_openai import ChatOpenAI

def get_chat_model():
    """Get configured chat model."""
    return ChatOpenAI(
        model="gpt-4",
        temperature=0.7,
        # Add other config from CLAUDE.md if specified
    )
```

**See:** [models/select-chat-models.md](models/select-chat-models.md)

---

## Step 5: Implement Routing Logic

**Read from CLAUDE.md:** `Edge Definitions` ’ `Conditional Edges` and `Routing Logic`

**Create:** `casts/{cast_name}/modules/conditions.py`

### Conversion Rules

Each conditional edge needs a routing function:

```python
# modules/conditions.py
from langgraph.graph import END

def route_{source_node}(state) -> str:
    """
    Routing logic for {source_node}.

    {Copy routing description from CLAUDE.md}
    """
    # Implement condition from CLAUDE.md
    if {condition}:
        return "{target_node}"
    return END
```

### Example

**CLAUDE.md:**
```
### Routing Logic
- "If message contains tool_calls, route to ToolNode"
- "Otherwise, route to END"
```

**conditions.py:**
```python
from langgraph.graph import END

def route_agent(state) -> str:
    """Route based on tool calls."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END
```

**See:** [core/edge.md](core/edge.md)

---

## Step 6: Assemble Graph

**Read from CLAUDE.md:** All sections combined

**Create:** `casts/{cast_name}/graph.py`

### Conversion Template

```python
# graph.py
from langgraph.graph import StateGraph, START, END
from casts.base_graph import BaseGraph

from casts.{cast_name}.modules.state import State, InputState, OutputState
from casts.{cast_name}.modules.nodes import {NodeA}, {NodeB}, ...
from casts.{cast_name}.modules.conditions import route_{node}

class {CastName}Graph(BaseGraph):
    def __init__(self):
        super().__init__()
        self.input = InputState
        self.output = OutputState
        self.state = State

    def build(self):
        builder = StateGraph(
            self.state,
            input_schema=self.input,
            output_schema=self.output
        )

        # Add nodes (from Node Specifications)
        builder.add_node("{node_a}", {NodeA}())
        builder.add_node("{node_b}", {NodeB}())

        # Add edges (from Edge Definitions)
        # Normal edges
        builder.add_edge(START, "{first_node}")
        builder.add_edge("{node_a}", "{node_b}")

        # Conditional edges
        builder.add_conditional_edges(
            "{source}",
            route_{source},
            {
                "{target_a}": "{target_a}",
                "{target_b}": "{target_b}",
                END: END
            }
        )

        graph = builder.compile()
        graph.name = self.name
        return graph

# Create instance
{cast_name}_graph = {CastName}Graph()
```

### Node Name Mapping

**CRITICAL:** CLAUDE.md uses CamelCase node names, graph.py uses lowercase strings:

| CLAUDE.md Node Name | graph.py String |
|---------------------|-----------------|
| `Agent` | `"agent"` |
| `SearchTool` | `"search_tool"` |
| `ResponseGenerator` | `"response_generator"` |

**See:** [core/graph.md](core/graph.md)

---

## Step 7: Add Dependencies

**Read from CLAUDE.md:** `Technology Stack` ’ `Additional Dependencies`

**Action:** Install packages using `engineering-act` skill

```bash
uv add --package {cast_name} {package_name}
```

**Example:**
- `langchain-openai` ’ `uv add --package my_cast langchain-openai`
- `langchain-community` ’ `uv add --package my_cast langchain-community`

---

## Step 8: Set Environment Variables

**Read from CLAUDE.md:** `Technology Stack` ’ `Environment Variables`

**Action:** Add to `.env` file (project root or cast-specific)

```bash
# .env
OPENAI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

---

## Verification Checklist

- [ ] `modules/state.py` - InputState, OutputState, State defined
- [ ] `modules/nodes.py` - All nodes from Node Specifications implemented
- [ ] `modules/tools.py` - Tools from Tool Specifications implemented (if any)
- [ ] `modules/models.py` - LLM models configured (if any)
- [ ] `modules/conditions.py` - Routing functions for conditional edges
- [ ] `graph.py` - All nodes added, all edges connected, graph compiled
- [ ] Dependencies installed via `uv add`
- [ ] Environment variables set in `.env`
- [ ] Graph runs: `uv run langgraph dev`

---

## Common Issues

### Issue: Node names don't match

**Problem:** CLAUDE.md has `Agent`, code has `"agent"` string

**Solution:** Use lowercase snake_case strings in `add_node()`:
- `Agent` ’ `"agent"`
- `SearchTool` ’ `"search_tool"`

### Issue: Missing fields in state

**Problem:** Node tries to read field not in State

**Solution:** Check OverallState table in CLAUDE.md, add missing fields to `State` in `state.py`

### Issue: Routing function returns wrong type

**Problem:** Conditional edge expects string, getting dict/list

**Solution:** Routing functions must return `str` (node name) or `END`

### Issue: Tools not binding to agent

**Problem:** Agent doesn't call tools even though they exist

**Solution:** Bind tools to model:
```python
from .tools import search_web
model = ChatOpenAI(model="gpt-4").bind_tools([search_web])
```

---

## Next Steps

After implementation:
1. **Test:** Use `testing-cast` skill to write tests
2. **Debug:** Use `uv run langgraph dev` to test graph interactively
3. **Refine:** Iterate based on test results

**For general coding tasks without CLAUDE.md:** Refer directly to individual usage guides in `usage/` directory.
