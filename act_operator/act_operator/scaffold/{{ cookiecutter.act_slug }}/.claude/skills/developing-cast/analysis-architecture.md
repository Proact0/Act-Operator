# From Architecture to Code

Convert CLAUDE.md architecture specification into working LangGraph implementation.

## Overview

Systematic 8-step workflow for implementing casts from CLAUDE.md. **For direct implementation without CLAUDE.md**, use [SKILL.md Mode 2](../SKILL.md#mode-2-direct-implementation).

### Implementation Flow

```
CLAUDE.md → State → Dependencies → Nodes → Conditions → Graph → Install → Verify
```

**Critical:** Implement in order to avoid import/circular dependency errors.

---

## Step 1: State Schema

**Input:** CLAUDE.md State Schema tables (InputState, OutputState, OverallState)
**Output:** `modules/state.py`
**Reference:** [core/state.md](core/state.md)

### Pattern Selection

| CLAUDE.md Contains | Pattern | Docs |
|--------------------|---------|------|
| Basic fields | TypedDict | [Basic State](core/state.md) |
| `messages` + `add_messages` | MessagesState | [With Messages](core/state.md) |
| Custom update logic | Reducer functions | [Reducers](core/state.md) |
| Input/Output separation | Separate schemas | [I/O Schemas](core/state.md) |

### Conversion Rules

| CLAUDE.md Element | Code |
|-------------------|------|
| InputState table | `class InputState(TypedDict)` |
| OutputState table | `class OutputState(TypedDict)` |
| OverallState table | `class State(TypedDict)` or `MessagesState` |
| Category: Input | In InputState + State |
| Category: Output | In OutputState + State |
| Category: Internal | Only in State |
| Type: `Annotated[..., add_messages]` | Use MessagesState |

### Minimal Example

**CLAUDE.md:**
```
| Field | Type | Category |
|-------|------|----------|
| question | str | Input |
| answer | str | Output |
| messages | Annotated[list[BaseMessage], add_messages] | Internal |
```

**state.py:**
```python
from langgraph.graph import MessagesState

class InputState(MessagesState):
    question: str

class OutputState(MessagesState):
    answer: str

class State(MessagesState):
    question: str
    answer: str
```

---

## Step 2: Dependencies

**Input:** CLAUDE.md Technology Stack, Node/Tool Specifications
**Output:** `modules/{models,tools,prompts,middlewares,agents,utils,conditions}.py`

### Implementation Order & Decision Matrix

| Module | When to Implement | Cross-References |
|--------|-------------------|------------------|
| **models.py** | Tech Stack lists LLM provider | [select-chat-models.md](models/select-chat-models.md), [standalone-model.md](models/standalone-model.md) |
| **tools.py** | Tool Specifications exist OR nodes need external ops | [basic-tool.md](tools/basic-tool.md), [complex-inputs.md](tools/tool-with-complex-inputs.md) |
| **prompts.py** | Agent needs system prompts/templates | [messages.md](prompts/messages.md), [message-types.md](prompts/message-types.md) |
| **middlewares.py** | Mentions retry/validation/safety | [Middleware sections](../SKILL.md), [custom.md](middlewares/custom.md) |
| **agents.py** | Node Type is "Agent" OR uses LLM+tools | [configuration.md](agents/configuration.md), [structured-output.md](agents/structured-output.md) |
| **utils.py** | Shared helpers across modules | - |
| **conditions.py** | Edge Definitions show conditional routing | [edge.md](core/edge.md) |

**Dependency chain:** models → tools → prompts → middlewares → agents → utils → conditions

### Module Dependency Matrix

| Module | Imports | Used By |
|--------|---------|---------|
| models.py | External packages | agents, nodes |
| tools.py | External packages | agents |
| prompts.py | langchain.messages | agents, nodes |
| middlewares.py | langchain.agents.middleware | agents |
| agents.py | models, tools, prompts, middlewares | nodes |
| utils.py | - | All |
| conditions.py | State types | graph |

### Quick Implementation Guide

#### Models (`modules/models.py`)

| CLAUDE.md Dependency | Factory Pattern |
|----------------------|-----------------|
| `langchain-openai` | `get_openai_model()` |
| `langchain-anthropic` | `get_anthropic_model()` |
| Multiple providers | `get_chat_model(provider: str)` |
| Embeddings | `get_embedding_model()` |

See [models/*.md](models/) for provider-specific patterns.

#### Tools (`modules/tools.py`)

| CLAUDE.md Tool Type | Implementation |
|---------------------|----------------|
| Simple function | `@tool` with primitives |
| Complex parameters | `@tool` with Pydantic model |
| Needs state access | `@tool` with ToolRuntime |
| MCP server | MCP adapter integration |

See [tools/*.md](tools/) for tool patterns.

#### Prompts (`modules/prompts.py`)

| Use Case | Pattern |
|----------|---------|
| System prompt | `str` or `SystemMessage` |
| Conversation | `list[SystemMessage, HumanMessage, ...]` |
| Dynamic | Template with state variables |
| Few-shot | Message sequence with examples |

See [prompts/*.md](prompts/) for prompt patterns.

#### Middleware (`modules/middlewares.py`)

| Type | Built-in Options | Custom |
|------|------------------|--------|
| Reliability | ModelRetry, ToolRetry, ModelFallback | - |
| Safety | Guardrails, OpenAI Moderation | Content filters |
| Control | ModelCallLimit, ToolCallLimit, HITL | Custom limits |
| Context | ContextEditing, Summarization | Dynamic prompts |

See [middlewares/*.md](middlewares/) for middleware patterns.

#### Agents (`modules/agents.py`)

Combine models + tools + prompts + middleware. See [agents/configuration.md](agents/configuration.md) for agent construction patterns.

#### Conditions (`modules/conditions.py`)

Return `str` (node name) or `END`. See [core/edge.md](core/edge.md) for routing patterns.

---

## Step 3: Nodes

**Input:** CLAUDE.md Node Specifications (Type, Responsibility, Reads, Writes)
**Output:** `modules/nodes.py`
**Reference:** [core/node.md](core/node.md)

### Node Pattern Selection

| CLAUDE.md Node Type | Pattern | Docs |
|---------------------|---------|------|
| Sync processing | BaseNode | [Sync Node](core/node.md) |
| Async I/O | AsyncBaseNode | [Async Node](core/node.md) |
| Needs thread_id/run_id | Add config param | [Using config](core/node.md) |
| Needs runtime info | Add runtime param | [Using runtime](core/node.md) |
| Calls LLM agent | Node + Agent | [Node with Agent](core/node.md) |

### Minimal Template

```python
from casts.base_node import BaseNode

class NodeName(BaseNode):
    """Responsibility from CLAUDE.md. Reads: X, Writes: Y"""

    def execute(self, state):
        data = state["read_field"]
        result = self._process(data)
        return {"write_field": result}
```

For agent nodes, inject agent from `modules/agents.py` in `__init__`. See [agents/configuration.md](agents/configuration.md).

---

## Step 4: Routing Logic

**Input:** CLAUDE.md Edge Definitions (Conditional Edges, Routing Logic)
**Output:** `modules/conditions.py` (if needed)
**Reference:** [core/edge.md](core/edge.md)

### Template

```python
from langgraph.graph import END

def route_source_node(state) -> str:
    """Routing description from CLAUDE.md."""
    if state.get("condition"):
        return "target_node"
    return END
```

**Return type must be `str` or `END`**.

---

## Step 5: Graph Assembly

**Input:** CLAUDE.md all sections (State, Nodes, Edges)
**Output:** `graph.py`
**Reference:** [core/graph.md](core/graph.md)

### Graph Pattern Selection

| CLAUDE.md Feature | Pattern | Docs |
|-------------------|---------|------|
| Basic graph | StateGraph | [Basic Pattern](core/graph.md) |
| Conversation persistence | + checkpointer | [Checkpointing](core/graph.md) |
| Cross-thread memory | + store | [Store](core/graph.md) |
| Human approval | + interrupts | [Interrupts](core/graph.md) |
| Multi-agent | Subgraphs | [subgraph.md](core/subgraph.md) |

### Minimal Template

```python
from langgraph.graph import StateGraph, START, END
from casts.base_graph import BaseGraph
from .modules.state import State, InputState, OutputState
from .modules.nodes import Node1, Node2
from .modules.conditions import route_node

class CastGraph(BaseGraph):
    def __init__(self):
        super().__init__()
        self.input = InputState
        self.output = OutputState
        self.state = State

    def build(self):
        builder = StateGraph(self.state, input_schema=self.input, output_schema=self.output)
        builder.add_node("node1", Node1())
        builder.add_node("node2", Node2())
        builder.add_edge(START, "node1")
        builder.add_conditional_edges("node1", route_node, {"node2": "node2", END: END})
        graph = builder.compile()
        graph.name = self.name
        return graph
```

### Critical: Node Name Mapping

| CLAUDE.md | graph.py String | Class |
|-----------|-----------------|-------|
| Agent | `"agent"` | `AgentNode` |
| SearchTool | `"search_tool"` | `SearchToolNode` |

**CLAUDE.md uses CamelCase, graph.py uses lowercase strings with underscores.**

---

## Step 6: Dependencies Installation

**Input:** CLAUDE.md Technology Stack → Additional Dependencies
**Action:** Use `engineering-act` skill

```bash
uv add --package {cast_name} {package_name}
```

See [engineering-act resources](../../engineering-act/resources/).

---

## Step 7: Environment Variables

**Input:** CLAUDE.md Technology Stack → Environment Variables
**Action:** Add to `.env` (project root)

```bash
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
```

---

## Step 8: Verification

- [ ] State matches CLAUDE.md tables
- [ ] Dependencies installed per Tech Stack
- [ ] All nodes implement Node Specifications
- [ ] Routing functions for conditional edges
- [ ] Graph compiles without errors
- [ ] Environment variables set
- [ ] `uv run langgraph dev` runs successfully

---

## Common Issues

| Problem | Solution |
|---------|----------|
| Node name mismatch | Use CamelCase classes, lowercase strings in `add_node()` |
| Missing state fields | Add all OverallState fields to `State` |
| Wrong routing return | Must return `str` or `END`, not dict/list |
| Tools not binding | Pass tools to `create_agent(model, tools=[...])` |
| Import errors | Follow strict order: state → models/tools → nodes → conditions → graph |

---

## Quick Reference

| Step | File | CLAUDE.md Source | Docs |
|------|------|------------------|------|
| 1. State | `modules/state.py` | State Schema | [state.md](core/state.md) |
| 2a. Models | `modules/models.py` | Tech Stack | [models/*.md](models/) |
| 2b. Tools | `modules/tools.py` | Tool Specs | [tools/*.md](tools/) |
| 2c. Agents | `modules/agents.py` | Node specs (LLM) | [agents/*.md](agents/) |
| 3. Nodes | `modules/nodes.py` | Node Specs | [node.md](core/node.md) |
| 4. Conditions | `modules/conditions.py` | Routing Logic | [edge.md](core/edge.md) |
| 5. Graph | `graph.py` | Edge Definitions | [graph.md](core/graph.md) |

---

## Next Steps

1. **Test:** `testing-cast` skill
2. **Debug:** `uv run langgraph dev`
3. **Iterate:** Refine based on results
