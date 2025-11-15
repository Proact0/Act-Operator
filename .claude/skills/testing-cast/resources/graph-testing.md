# Graph Testing

## When to Use

Testing complete graphs (integration tests). Validates node connections, routing, and state flow.

## Basic Pattern

```python
from casts.my_agent.graph import MyAgentGraph
from langgraph.checkpoint.memory import MemorySaver

def test_graph_execution():
    """Test complete graph execution."""
    graph = MyAgentGraph(checkpointer=MemorySaver()).build()
    
    result = graph.invoke({
        "messages": [],
        "task": "test task"
    })
    
    assert "results" in result
    assert result["status"] == "completed"
```

## Testing with Config

```python
def test_graph_with_config():
    """Test graph with thread_id."""
    graph = MyAgentGraph(checkpointer=MemorySaver()).build()
    
    config = {"configurable": {"thread_id": "test-123"}}
    
    result = graph.invoke(
        {"messages": [], "task": "test"},
        config=config
    )
    
    assert result is not None
    
    # Verify state was saved
    state = graph.get_state(config)
    assert state.values["task"] == "test"
```

## Testing Edge Routing

```python
def test_conditional_routing():
    """Test conditional edges route correctly."""
    graph = MyAgentGraph(checkpointer=MemorySaver()).build()
    
    # Test route to "continue"
    result1 = graph.invoke({"action": "continue", "messages": []})
    assert result1["next_step"] == "process"
    
    # Test route to "end"
    result2 = graph.invoke({"action": "end", "messages": []})
    assert result2["status"] == "completed"
```

## Testing State Flow

```python
def test_state_accumulation():
    """Test state accumulates correctly through graph."""
    graph = MyAgentGraph(checkpointer=MemorySaver()).build()
    config = {"configurable": {"thread_id": "test-123"}}
    
    # First invocation
    result1 = graph.invoke({"messages": [], "count": 1}, config)
    assert result1["count"] == 1
    
    # Second invocation - should accumulate
    result2 = graph.invoke({"count": 1}, config)
    assert result2["count"] == 2  # Accumulated
```

## Testing Multi-Step Workflows

```python
def test_complete_workflow():
    """Test multi-step graph workflow."""
    graph = MyAgentGraph(checkpointer=MemorySaver()).build()
    
    result = graph.invoke({
        "messages": [],
        "task": "multi-step task"
    })
    
    # Verify all steps completed
    assert result["step1_completed"] is True
    assert result["step2_completed"] is True
    assert result["step3_completed"] is True
    assert result["status"] == "completed"
```

## Testing with Streaming

```python
def test_graph_streaming():
    """Test graph streaming output."""
    graph = MyAgentGraph().build()
    
    chunks = []
    for chunk in graph.stream({"task": "test"}):
        chunks.append(chunk)
    
    assert len(chunks) > 0
    # Verify each node output present
    node_names = [list(chunk.keys())[0] for chunk in chunks]
    assert "start" in node_names
    assert "process" in node_names
```

## Testing Interrupts

```python
def test_graph_with_interrupt():
    """Test graph pauses at interrupt."""
    from langgraph.types import Command
    
    graph = MyAgentGraph(checkpointer=MemorySaver()).build()
    config = {"configurable": {"thread_id": "test-123"}}
    
    # First call stops at interrupt
    result1 = graph.invoke({"requires_approval": True}, config)
    
    # Check state
    state = graph.get_state(config)
    assert state.next  # Should be waiting
    
    # Resume with approval
    result2 = graph.invoke(Command(resume="approved"), config)
    assert result2["status"] == "approved"
```

## Testing Error Propagation

```python
def test_graph_error_handling():
    """Test graph handles node errors."""
    graph = MyAgentGraph(checkpointer=MemorySaver()).build()
    
    # Trigger error condition
    result = graph.invoke({"trigger_error": True})
    
    assert "error" in result
    assert result["error"] is not None
```

## Testing with Mock Dependencies

```python
@pytest.fixture
def test_graph(mock_llm):
    """Fixture providing graph with mocked dependencies."""
    from langchain_anthropic import ChatAnthropic
    
    # Replace real LLM with mock
    graph = MyAgentGraph(model=mock_llm, checkpointer=MemorySaver())
    return graph.build()

def test_with_mocked_graph(test_graph):
    """Test using mocked graph fixture."""
    result = test_graph.invoke({"task": "test"})
    assert result is not None
```

## Testing Iteration Limits

```python
def test_iteration_limit():
    """Test graph respects iteration limit."""
    graph = MyAgentGraph(checkpointer=MemorySaver()).build()
    
    config = {
        "configurable": {"thread_id": "test-123"},
        "recursion_limit": 5
    }
    
    result = graph.invoke({"loop_forever": True}, config)
    
    # Should stop after limit
    assert result["iteration_count"] <= 5
```

## Parametrized Graph Tests

```python
@pytest.mark.parametrize("task,expected_result", [
    ("simple", "success"),
    ("complex", "in_progress"),
    ("invalid", "error"),
])
def test_graph_scenarios(task, expected_result):
    """Test graph with different scenarios."""
    graph = MyAgentGraph(checkpointer=MemorySaver()).build()
    
    result = graph.invoke({"task": task})
    
    assert result["status"] == expected_result
```

## Testing Subgraphs

```python
def test_with_subgraph():
    """Test graph that uses subgraphs."""
    graph = MainGraph(checkpointer=MemorySaver()).build()
    
    result = graph.invoke({"use_subgraph": True})
    
    # Verify subgraph executed
    assert result["subgraph_result"] is not None
    assert result["status"] == "completed"
```

## Performance Testing

```python
import time

@pytest.mark.slow
def test_graph_performance():
    """Test graph completes within time limit."""
    graph = MyAgentGraph(checkpointer=MemorySaver()).build()
    
    start = time.time()
    result = graph.invoke({"task": "test"})
    duration = time.time() - start
    
    assert result["status"] == "completed"
    assert duration < 5.0  # Should complete in < 5 seconds
```

## Testing State History

```python
def test_state_history():
    """Test retrieving state history."""
    graph = MyAgentGraph(checkpointer=MemorySaver()).build()
    config = {"configurable": {"thread_id": "test-123"}}
    
    # Execute multiple steps
    graph.invoke({"task": "step1"}, config)
    graph.invoke({"task": "step2"}, config)
    
    # Get history
    history = list(graph.get_state_history(config))
    
    assert len(history) >= 2
    # Verify state progression
    assert history[0].values["task"] == "step2"  # Most recent
```

## Integration Test Organization

```python
class TestMyAgentGraph:
    """Integration tests for MyAgent graph."""
    
    @pytest.fixture
    def graph(self):
        """Provide test graph."""
        return MyAgentGraph(checkpointer=MemorySaver()).build()
    
    def test_basic_workflow(self, graph):
        """Test basic workflow."""
        result = graph.invoke({"task": "test"})
        assert result["status"] == "completed"
    
    def test_error_workflow(self, graph):
        """Test error handling workflow."""
        result = graph.invoke({"trigger_error": True})
        assert "error" in result
    
    @pytest.mark.slow
    def test_complex_workflow(self, graph):
        """Test complex multi-step workflow."""
        result = graph.invoke({"task": "complex"})
        assert result["steps_completed"] >= 3
```

## Quick Reference

**Basic test:**
```python
def test_graph():
    graph = MyGraph(checkpointer=MemorySaver()).build()
    result = graph.invoke(input)
    assert condition
```

**With config:**
```python
config = {"configurable": {"thread_id": "test-123"}}
result = graph.invoke(input, config)
```

**Test routing:**
```python
result = graph.invoke({"route": "path_a"})
assert result["next"] == "expected_node"
```

**Test streaming:**
```python
chunks = list(graph.stream(input))
assert len(chunks) > 0
```

## Common Mistakes

❌ **No checkpointer** - state not persisted, interrupts fail
✓ Always use MemorySaver() for tests

❌ **Forgetting thread_id** - can't test state persistence
✓ Use config with thread_id

❌ **Testing with real LLM** - slow, costs money
✓ Mock LLM in graph constructor

❌ **Not testing edge cases** - only happy path
✓ Test errors, limits, edge conditions

## References

- Node testing: `node-testing.md`
- Async testing: `async-testing.md`
- State testing: `state-testing.md`
