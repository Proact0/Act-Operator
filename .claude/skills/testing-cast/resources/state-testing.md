# State Testing

## Testing State Updates

```python
from casts.my_agent.state import MyAgentState

def test_state_updates():
    """Test state updates work correctly."""
    node = ProcessNode()
    
    state: MyAgentState = {
        "messages": [],
        "count": 0,
        "data": {}
    }
    
    result = node.execute(state)
    
    # Verify update structure
    assert isinstance(result, dict)
    assert "messages" in result
    assert "count" in result
```

## Testing Reducers

```python
from operator import add

def test_reducer_accumulation():
    """Test reducer accumulates values."""
    # Simulate reducer behavior
    existing = [1, 2, 3]
    update = [4, 5]
    
    result = add(existing, update)
    
    assert result == [1, 2, 3, 4, 5]
```

## Testing State Flow

```python
def test_state_flow_through_graph():
    """Test state flows correctly through graph."""
    from langgraph.checkpoint.memory import MemorySaver
    
    graph = MyAgentGraph(checkpointer=MemorySaver()).build()
    config = {"configurable": {"thread_id": "test-123"}}
    
    # First invocation
    result1 = graph.invoke({"messages": [], "count": 1}, config)
    assert result1["count"] == 1
    
    # Second invocation - should accumulate
    result2 = graph.invoke({"count": 1}, config)
    assert result2["count"] == 2
```

## Testing State Validation

```python
def test_state_schema_validation():
    """Test state schema with Pydantic."""
    from pydantic import ValidationError
    
    # Valid state
    valid = MyAgentState(
        messages=[],
        task="test",
        count=0
    )
    assert valid.task == "test"
    
    # Invalid state
    with pytest.raises(ValidationError):
        MyAgentState(
            messages="not a list",  # Should be list
            task="test"
        )
```

## Quick Reference

**Test updates:**
```python
result = node.execute(state)
assert "key" in result
```

**Test reducers:**
```python
result = reducer(old_value, new_value)
assert result == expected
```

**Test flow:**
```python
result1 = graph.invoke(input1, config)
result2 = graph.invoke(input2, config)
assert accumulated correctly
```

## References

- Node testing: `node-testing.md`
- Graph testing: `graph-testing.md`
