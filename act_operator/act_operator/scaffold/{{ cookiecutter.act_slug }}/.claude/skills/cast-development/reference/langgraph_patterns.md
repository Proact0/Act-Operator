# LangGraph Patterns Catalog

## Contents

- [Graph Structure Patterns](#graph-structure-patterns)
- [Edge Patterns](#edge-patterns)
- [State Management Patterns](#state-management-patterns)
- [Node Communication Patterns](#node-communication-patterns)
- [Error Handling Patterns](#error-handling-patterns)
- [Testing Patterns](#testing-patterns)

---

## Graph Structure Patterns

### Pattern 1: Linear Flow

**When to use**: Sequential processing without branching.

**Structure**: START → Node1 → Node2 → Node3 → END

```python
def build(self):
    builder = StateGraph(State)

    builder.add_node("fetch", FetchNode())
    builder.add_node("process", ProcessNode())
    builder.add_node("save", SaveNode())

    builder.add_edge(START, "fetch")
    builder.add_edge("fetch", "process")
    builder.add_edge("process", "save")
    builder.add_edge("save", END)

    return builder.compile()
```

**Use cases**: Data pipelines, ETL processes, simple workflows

---

### Pattern 2: Conditional Branching

**When to use**: Different paths based on state conditions.

**Structure**: START → Check → [Path A | Path B] → END

```python
def should_retry(state):
    """Routing function for conditional edges."""
    if state.get("error"):
        return "retry"
    return "success"

def build(self):
    builder = StateGraph(State)

    builder.add_node("process", ProcessNode())
    builder.add_node("retry", RetryNode())
    builder.add_node("success", SuccessNode())

    builder.add_edge(START, "process")

    # Conditional routing
    builder.add_conditional_edges(
        "process",
        should_retry,
        {
            "retry": "retry",
            "success": "success"
        }
    )

    builder.add_edge("retry", "process")  # Loop back
    builder.add_edge("success", END)

    return builder.compile()
```

**Use cases**: Retry logic, validation workflows, A/B paths

---

### Pattern 3: Parallel Fan-Out/Fan-In

**When to use**: Multiple nodes process independently, then merge.

**Structure**: START → Split → [Node A, Node B, Node C] → Merge → END

```python
def build(self):
    builder = StateGraph(State)

    builder.add_node("split", SplitNode())
    builder.add_node("process_a", ProcessANode())
    builder.add_node("process_b", ProcessBNode())
    builder.add_node("process_c", ProcessCNode())
    builder.add_node("merge", MergeNode())

    builder.add_edge(START, "split")

    # Fan-out: Split to multiple nodes
    builder.add_edge("split", "process_a")
    builder.add_edge("split", "process_b")
    builder.add_edge("split", "process_c")

    # Fan-in: All converge to merge
    builder.add_edge("process_a", "merge")
    builder.add_edge("process_b", "merge")
    builder.add_edge("process_c", "merge")

    builder.add_edge("merge", END)

    return builder.compile()
```

**Use cases**: Parallel processing, aggregation, multi-source data collection

---

### Pattern 4: Loop with Exit Condition

**When to use**: Iterative processing until condition is met.

**Structure**: START → Process → Check → [Loop | Exit] → END

```python
def should_continue(state):
    """Check if should continue looping."""
    max_iterations = 5
    current = state.get("iteration", 0)

    if current >= max_iterations:
        return "exit"

    if state.get("is_complete"):
        return "exit"

    return "loop"

def build(self):
    builder = StateGraph(State)

    builder.add_node("init", InitNode())
    builder.add_node("process", ProcessNode())
    builder.add_node("check", CheckNode())
    builder.add_node("finalize", FinalizeNode())

    builder.add_edge(START, "init")
    builder.add_edge("init", "process")
    builder.add_edge("process", "check")

    # Conditional loop
    builder.add_conditional_edges(
        "check",
        should_continue,
        {
            "loop": "process",  # Loop back
            "exit": "finalize"
        }
    )

    builder.add_edge("finalize", END)

    return builder.compile()
```

**Use cases**: Iterative refinement, retry with backoff, progressive enhancement

---

### Pattern 5: Agent with Tool Calling

**When to use**: LLM agent that calls tools based on context.

**Structure**: START → Agent → [Tool Calls | Continue | Finish] → END

```python
from langgraph.prebuilt import ToolNode

def should_continue(state):
    """Route based on agent's last message."""
    messages = state["messages"]
    last_message = messages[-1]

    # If agent used tools, continue
    if last_message.tool_calls:
        return "tools"

    # Otherwise finish
    return "end"

def build(self):
    builder = StateGraph(State)

    # Prebuilt tool node handles tool execution
    tools = [search_tool, calculator_tool]
    tool_node = ToolNode(tools)

    builder.add_node("agent", AgentNode())
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "agent")

    # Conditional routing
    builder.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )

    # After tools, go back to agent
    builder.add_edge("tools", "agent")

    return builder.compile()
```

**Use cases**: LLM agents, tool-augmented workflows, ReAct patterns

---

## Edge Patterns

### Simple Edge

Direct connection between nodes.

```python
builder.add_edge("node_a", "node_b")
```

### Conditional Edge

Branch based on routing function.

```python
def route_func(state):
    return "path_a" if state["condition"] else "path_b"

builder.add_conditional_edges(
    "source_node",
    route_func,
    {
        "path_a": "target_a",
        "path_b": "target_b"
    }
)
```

### Multi-Path Conditional Edge

Route to multiple possible destinations.

```python
def complex_route(state):
    score = state["score"]

    if score > 90:
        return "excellent"
    elif score > 70:
        return "good"
    elif score > 50:
        return "fair"
    else:
        return "poor"

builder.add_conditional_edges(
    "evaluate",
    complex_route,
    {
        "excellent": "reward_node",
        "good": "continue_node",
        "fair": "review_node",
        "poor": "retry_node"
    }
)
```

---

## State Management Patterns

### Append-Only State

For lists that accumulate values.

```python
from typing import Annotated
from dataclasses import dataclass

def append_messages(existing: list, new: list) -> list:
    """Append new messages to existing."""
    return existing + new

@dataclass(kw_only=True)
class State:
    messages: Annotated[list, append_messages]
```

### Override State

Default behavior - new value replaces old.

```python
@dataclass(kw_only=True)
class State:
    query: str         # Overrides on update
    result: str        # Overrides on update
    count: int = 0     # Overrides on update
```

### Merge State (Dict)

For nested dictionaries that merge.

```python
from typing import Annotated

def merge_dicts(existing: dict, new: dict) -> dict:
    """Deep merge dictionaries."""
    result = existing.copy()
    result.update(new)
    return result

@dataclass(kw_only=True)
class State:
    metadata: Annotated[dict, merge_dicts]
```

---

## Node Communication Patterns

### Pattern 1: Direct State Updates

Nodes communicate via state updates.

```python
class ProducerNode(BaseNode):
    def execute(self, state):
        data = fetch_data()
        return {"data": data, "status": "fetched"}

class ConsumerNode(BaseNode):
    def execute(self, state):
        data = state["data"]  # Access data from previous node
        processed = process(data)
        return {"result": processed}
```

### Pattern 2: Message Passing

Nodes communicate via message list.

```python
from langchain_core.messages import AIMessage, HumanMessage

class QueryNode(BaseNode):
    def execute(self, state):
        query = state["query"]
        return {"messages": [HumanMessage(content=query)]}

class ResponseNode(BaseNode):
    def execute(self, state):
        messages = state["messages"]
        last_query = messages[-1].content
        response = generate_response(last_query)
        return {"messages": [AIMessage(content=response)]}
```

### Pattern 3: Shared Context

Nodes share context through state dict.

```python
class ContextBuilderNode(BaseNode):
    def execute(self, state):
        context = {
            "user_id": "123",
            "session_id": "abc",
            "timestamp": now()
        }
        return {"context": context}

class ContextConsumerNode(BaseNode):
    def execute(self, state):
        context = state["context"]
        user_id = context["user_id"]
        # Use context...
        return {"result": "processed"}
```

---

## Error Handling Patterns

### Pattern 1: Try-Catch in Node

Handle errors within node execution.

```python
class RobustNode(BaseNode):
    def execute(self, state):
        try:
            result = risky_operation(state["input"])
            return {"result": result, "error": None}
        except Exception as e:
            self.log("Error occurred", error=str(e))
            return {"result": None, "error": str(e)}
```

### Pattern 2: Error Recovery Flow

Use conditional routing to handle errors.

```python
def has_error(state):
    return "retry" if state.get("error") else "success"

def build(self):
    builder = StateGraph(State)

    builder.add_node("process", ProcessNode())
    builder.add_node("retry", RetryNode())
    builder.add_node("success", SuccessNode())
    builder.add_node("failure", FailureNode())

    builder.add_edge(START, "process")

    builder.add_conditional_edges(
        "process",
        has_error,
        {"retry": "retry", "success": "success"}
    )

    # Retry with counter
    def should_retry_again(state):
        retries = state.get("retry_count", 0)
        return "process" if retries < 3 else "failure"

    builder.add_conditional_edges(
        "retry",
        should_retry_again,
        {"process": "process", "failure": "failure"}
    )

    builder.add_edge("success", END)
    builder.add_edge("failure", END)

    return builder.compile()
```

### Pattern 3: Graceful Degradation

Provide fallback behavior on error.

```python
class FallbackNode(BaseNode):
    def execute(self, state):
        try:
            # Try primary method
            result = primary_method(state["input"])
            return {"result": result, "method": "primary"}
        except Exception:
            # Fall back to secondary method
            result = fallback_method(state["input"])
            return {"result": result, "method": "fallback"}
```

---

## Testing Patterns

### Pattern 1: Unit Test Nodes

Test nodes independently.

```python
def test_process_node():
    node = ProcessNode()

    # Mock state
    state = {"input": "test data"}

    # Execute
    result = node(state)

    # Assert
    assert "output" in result
    assert result["output"] == "processed: test data"
```

### Pattern 2: Integration Test Graph

Test complete graph execution.

```python
def test_complete_graph():
    graph = MyGraph()
    compiled = graph.build()

    # Invoke with input
    result = compiled.invoke({"query": "test query"})

    # Assert final state
    assert "result" in result
    assert result["result"] is not None
```

### Pattern 3: Test Conditional Routing

Test routing logic.

```python
def test_routing():
    # Test success path
    state_success = {"error": None}
    assert should_retry(state_success) == "success"

    # Test retry path
    state_error = {"error": "Something failed"}
    assert should_retry(state_error) == "retry"
```

---

## Best Practices

### 1. Keep Graphs Simple
- Prefer multiple simple graphs over one complex graph
- Each graph should have a single clear purpose

### 2. Use Descriptive Node Names
```python
# ✅ Good
builder.add_node("fetch_user_data", FetchUserNode())
builder.add_node("validate_input", ValidateNode())

# ❌ Bad
builder.add_node("node1", Node1())
builder.add_node("n2", Node2())
```

### 3. Document Routing Logic
```python
def route_by_score(state):
    """
    Route based on quality score.

    Returns:
        - "high": score > 0.8
        - "medium": 0.5 < score <= 0.8
        - "low": score <= 0.5
    """
    score = state["quality_score"]
    if score > 0.8:
        return "high"
    elif score > 0.5:
        return "medium"
    return "low"
```

### 4. Avoid Deeply Nested Conditions
```python
# ✅ Good: Flat routing
def route_clear(state):
    if state["type"] == "A":
        return "handler_a"
    if state["type"] == "B":
        return "handler_b"
    return "default"

# ❌ Bad: Nested conditions
def route_complex(state):
    if state["type"] == "A":
        if state["priority"] == "high":
            return "urgent_a"
        else:
            return "normal_a"
    else:
        if state["priority"] == "high":
            return "urgent_other"
        else:
            return "normal_other"
```

### 5. Use Meaningful State Keys
```python
# ✅ Good
return {
    "user_query": query,
    "search_results": results,
    "processing_status": "complete"
}

# ❌ Bad
return {
    "q": query,
    "r": results,
    "s": "complete"
}
```
