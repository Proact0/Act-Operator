# Subgraphs

## When to Use This Resource
Read this when needing to modularize complex graphs, reuse graph components, or build hierarchical agent systems.

## What are Subgraphs?

**Subgraph** = A graph used as a node within another graph.

**Benefits:**
- Modularity (reusable components)
- Separation of concerns
- Simplified testing
- Team collaboration (different teams own different subgraphs)

**When to use:**
- Graph logic becomes too complex
- Need to reuse a workflow across multiple graphs
- Multi-agent systems with specialized sub-agents
- Clear boundaries between different processing stages

## Communication Patterns

### Pattern 1: Shared State Keys

**When:** Parent and subgraph share same state schema or overlapping keys.

```python
# Shared state
class SharedState(TypedDict):
    messages: Annotated[list[dict], add]
    context: str

# Parent graph
parent_builder = StateGraph(SharedState)

# Subgraph with same state
sub_builder = StateGraph(SharedState)
# ... add nodes to subgraph ...
compiled_subgraph = sub_builder.compile()

# Add subgraph as node
parent_builder.add_node("subgraph_step", compiled_subgraph)
```

**How it works:**
- Parent invokes subgraph with current state
- Subgraph processes and returns state updates
- Parent merges updates back into its state

### Pattern 2: Different Schemas with Transformation

**When:** Subgraph has completely different state structure.

```python
# Parent state
class ParentState(TypedDict):
    input: str
    result: dict

# Subgraph state
class SubgraphState(TypedDict):
    query: str
    data: list[dict]

# Build subgraph
sub_builder = StateGraph(SubgraphState)
# ... add nodes ...
compiled_subgraph = sub_builder.compile()

# Transform function
from casts.base_node import BaseNode

class SubgraphWrapperNode(BaseNode):
    def __init__(self, subgraph, **kwargs):
        super().__init__(**kwargs)
        self.subgraph = subgraph

    def execute(self, state: ParentState) -> dict:
        # Transform parent state to subgraph state
        sub_input = {"query": state["input"], "data": []}

        # Invoke subgraph
        sub_result = self.subgraph.invoke(sub_input)

        # Transform subgraph result back to parent state
        return {"result": sub_result}

# Add to parent graph
wrapper = SubgraphWrapperNode(compiled_subgraph)
parent_builder.add_node("process_subgraph", wrapper)
```

## Practical Patterns

### Pattern 1: Multi-Agent with Subgraphs

```python
# Research sub-agent
class ResearchAgentGraph(BaseGraph):
    def build(self):
        builder = StateGraph(ResearchState)
        # ... research nodes ...
        return builder.compile()

# Writing sub-agent
class WritingAgentGraph(BaseGraph):
    def build(self):
        builder = StateGraph(WritingState)
        # ... writing nodes ...
        return builder.compile()

# Main orchestrator
class OrchestratorGraph(BaseGraph):
    def build(self):
        builder = StateGraph(OrchestratorState)

        # Compile subgraphs
        research_graph = ResearchAgentGraph().build()
        writing_graph = WritingAgentGraph().build()

        # Add as nodes
        builder.add_node("research", research_graph)
        builder.add_node("write", writing_graph)

        builder.add_edge(START, "research")
        builder.add_edge("research", "write")
        builder.add_edge("write", END)

        return builder.compile()
```

### Pattern 2: Reusable Processing Pipeline

```python
# Data cleaning subgraph (reusable)
class DataCleaningGraph(BaseGraph):
    def build(self):
        builder = StateGraph(CleaningState)
        builder.add_node("validate", ValidateNode())
        builder.add_node("normalize", NormalizeNode())
        builder.add_node("deduplicate", DeduplicateNode())

        builder.add_edge(START, "validate")
        builder.add_edge("validate", "normalize")
        builder.add_edge("normalize", "deduplicate")
        builder.add_edge("deduplicate", END)

        return builder.compile()

# Use in multiple parent graphs
cleaning_subgraph = DataCleaningGraph().build()

# Parent 1
builder1.add_node("clean_data", cleaning_subgraph)

# Parent 2 (reuses same subgraph)
builder2.add_node("preprocessing", cleaning_subgraph)
```

### Pattern 3: Private Subgraph State

**When:** Subgraph needs internal state not visible to parent.

```python
class SubgraphState(TypedDict):
    # Shared with parent
    input: str
    result: str

    # Private to subgraph (not in parent state)
    internal_counter: int
    intermediate_data: list

# Parent only sees input/result, not internal fields
```

## Act Project Structure

```
casts/
├── main_cast/
│   ├── graph.py          # Main orchestrator
│   ├── state.py
│   └── nodes.py
├── research_agent/       # Subgraph 1
│   ├── graph.py
│   ├── state.py
│   └── nodes.py
└── writing_agent/        # Subgraph 2
    ├── graph.py
    ├── state.py
    └── nodes.py
```

**In main_cast/graph.py:**
```python
from casts.research_agent.graph import ResearchAgentGraph
from casts.writing_agent.graph import WritingAgentGraph

class MainCastGraph(BaseGraph):
    def build(self):
        builder = StateGraph(MainState)

        research = ResearchAgentGraph().build()
        writing = WritingAgentGraph().build()

        builder.add_node("research", research)
        builder.add_node("write", writing)
        # ...
```

## Nested Subgraphs

Subgraphs can contain other subgraphs:

```python
# Level 3: Data processor
data_processor = DataProcessorGraph().build()

# Level 2: Analysis pipeline (uses data processor)
class AnalysisPipeline(BaseGraph):
    def build(self):
        builder = StateGraph(AnalysisState)
        builder.add_node("process", data_processor)  # Nested subgraph
        # ...
        return builder.compile()

# Level 1: Main graph (uses analysis pipeline)
class MainGraph(BaseGraph):
    def build(self):
        builder = StateGraph(MainState)
        analysis = AnalysisPipeline().build()  # Contains nested subgraph
        builder.add_node("analyze", analysis)
        # ...
```

**Limit nesting depth** to 2-3 levels for maintainability.

## Checkpointing with Subgraphs

**Checkpoints are hierarchical:**

```python
# Parent with checkpointer
parent_graph = parent_builder.compile(checkpointer=SqliteSaver(...))

# Subgraph inherits parent's checkpointer
# Each subgraph execution creates checkpoints under parent's thread
```

**Access subgraph checkpoints:**
```python
config = {"configurable": {"thread_id": "main-123"}}
parent_graph.invoke({"input": "..."}, config=config)

# Get checkpoint history includes subgraph steps
history = parent_graph.get_state_history(config)
```

## Error Handling with Subgraphs

```python
class SafeSubgraphWrapper(BaseNode):
    def __init__(self, subgraph, **kwargs):
        super().__init__(**kwargs)
        self.subgraph = subgraph

    def execute(self, state: dict) -> dict:
        try:
            result = self.subgraph.invoke(state)
            return {"subgraph_result": result, "error": None}
        except Exception as e:
            self.log(f"Subgraph error: {e}")
            return {"subgraph_result": None, "error": str(e)}
```

## Performance Considerations

**Pros:**
- ✅ Modular code
- ✅ Reusable components
- ✅ Easier testing

**Cons:**
- ❌ State transformation overhead
- ❌ More complex debugging
- ❌ Potential performance impact (context switching)

**When NOT to use:**
- Graph is already simple
- No clear module boundaries
- Performance is critical

## Common Mistakes

❌ **Circular subgraph dependencies**
```python
# ❌ Graph A uses Graph B, Graph B uses Graph A
```

❌ **Forgetting state transformation**
```python
# ❌ Parent and subgraph have different state, no transformation
parent_builder.add_node("sub", subgraph)  # Will fail

# ✅ Use wrapper with transformation
parent_builder.add_node("sub", SubgraphWrapperNode(subgraph))
```

❌ **Too many levels of nesting**
```python
# ❌ Hard to debug and maintain
main -> sub1 -> sub2 -> sub3 -> sub4 -> sub5
```

## References
- LangGraph Subgraphs: https://docs.langchain.com/oss/python/langgraph/use-subgraphs
- Related: `../core/graph-compilation.md` (building subgraphs)
- Related: `error-handling-retry.md` (error handling across subgraphs)
