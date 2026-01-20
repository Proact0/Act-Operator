# Subgraphs

A subgraph is a graph used as a node in another graph.

## Contents

- Communication Methods
- Method 1: Invoke from Node (different state schemas)
- Method 2: Add as Node (shared state keys)
- Persistence
- Streaming Subgraph Outputs
- Decision Framework

**Use cases:**
- Multi-agent systems
- Reusable node sets
- Team-based distributed development

## Communication Methods

| Method | Use When |
|--------|----------|
| Invoke from node | Different state schemas (no shared keys) |
| Add as node | Shared state keys between parent and child |

---

## Method 1: Invoke from Node

Use when parent and subgraph have **different state schemas**.

```python
# casts/{cast_name}/modules/nodes.py
from casts.base_node import BaseNode
from .subgraphs import analysis_subgraph

class AnalysisNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.subgraph = analysis_subgraph

    def execute(self, state):
        # Transform parent state → subgraph state
        subgraph_input = {"query": state["user_input"]}
        
        # Invoke subgraph
        subgraph_output = self.subgraph.invoke(subgraph_input)
        
        # Transform subgraph output → parent state
        return {"analysis_result": subgraph_output["result"]}
```

### Define Subgraph

```python
# casts/{cast_name}/modules/subgraphs.py
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class AnalysisState(TypedDict):
    query: str
    result: str

def analyze(state: AnalysisState):
    return {"result": f"Analyzed: {state['query']}"}

def summarize(state: AnalysisState):
    return {"result": state["result"] + " [summarized]"}

# Build subgraph
builder = StateGraph(AnalysisState)
builder.add_node("analyze", analyze)
builder.add_node("summarize", summarize)
builder.add_edge(START, "analyze")
builder.add_edge("analyze", "summarize")
builder.add_edge("summarize", END)

analysis_subgraph = builder.compile()
```

---

## Method 2: Add as Node

Use when parent and subgraph **share state keys**.

```python
# casts/{cast_name}/graph.py
from langgraph.graph import StateGraph, START, END
from casts.base_graph import BaseGraph
from casts.{cast_name}.modules.subgraphs import shared_subgraph

class ParentGraph(BaseGraph):
    def build(self):
        builder = StateGraph(State)
        
        builder.add_node("preprocess", PreprocessNode())
        builder.add_node("subgraph", shared_subgraph)  # Add compiled graph directly
        builder.add_node("postprocess", PostprocessNode())
        
        builder.add_edge(START, "preprocess")
        builder.add_edge("preprocess", "subgraph")
        builder.add_edge("subgraph", "postprocess")
        builder.add_edge("postprocess", END)
        
        graph = builder.compile()
        graph.name = self.name
        return graph
```

### Shared State Subgraph

```python
# casts/{cast_name}/modules/subgraphs.py
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class SharedState(TypedDict):
    messages: list  # Shared with parent
    internal_data: str  # Private to subgraph

def process(state: SharedState):
    return {"internal_data": "processed"}

def respond(state: SharedState):
    return {"messages": state["messages"] + ["Response based on " + state["internal_data"]]}

builder = StateGraph(SharedState)
builder.add_node("process", process)
builder.add_node("respond", respond)
builder.add_edge(START, "process")
builder.add_edge("process", "respond")
builder.add_edge("respond", END)

shared_subgraph = builder.compile()
```

---

## Persistence

Only provide checkpointer when compiling **parent graph**. LangGraph automatically propagates to subgraphs.

```python
# casts/{cast_name}/graph.py
from langgraph.checkpoint.memory import MemorySaver

class ParentGraph(BaseGraph):
    def build(self):
        builder = StateGraph(State)
        builder.add_node("subgraph", child_subgraph)
        # ...
        
        # Checkpointer propagates to subgraph
        graph = builder.compile(checkpointer=MemorySaver())
        graph.name = self.name
        return graph
```

### Subgraph with Own Memory

For multi-agent systems where agents need private message history:

```python
# casts/{cast_name}/modules/subgraphs.py
builder = StateGraph(AgentState)
# ... add nodes ...
agent_subgraph = builder.compile(checkpointer=True)  # Own memory
```

---

## Streaming Subgraph Outputs

```python
# Include subgraph outputs in stream
for chunk in graph.stream(
    {"input": "data"},
    subgraphs=True,  # Stream from subgraphs too
    stream_mode="updates",
):
    print(chunk)
```

---

## Decision Framework

```
Do parent and subgraph share state keys?
├─ Yes → Add compiled graph as node directly
│        builder.add_node("name", subgraph)
└─ No  → Invoke from within a node function
         Transform state in → invoke → transform out
```
