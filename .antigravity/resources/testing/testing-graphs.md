# Testing Graphs

## Basic Graph Test

```python
# tests/test_graph.py
import pytest
from langgraph.checkpoint.memory import MemorySaver
from casts.{cast_name}.graph import MyGraph

class TestMyGraph:
    @pytest.fixture
    def graph(self):
        return MyGraph().build()

    @pytest.fixture
    def graph_with_memory(self):
        checkpointer = MemorySaver()
        return MyGraph().build(checkpointer=checkpointer)

    def test_compiles(self, graph):
        assert graph is not None
        assert hasattr(graph, "invoke")

    def test_invoke_basic(self, graph):
        result = graph.invoke({"input": "test"})
        
        assert result is not None
        assert isinstance(result, dict)

    def test_with_config(self, graph_with_memory):
        config = {"configurable": {"thread_id": "test-123"}}
        result = graph_with_memory.invoke({"input": "test"}, config=config)
        
        assert result is not None
```

## Testing Routing

```python
class TestGraphRouting:
    def test_conditional_true(self, graph):
        result = graph.invoke({"input": "test", "condition": True})
        assert result["path"] == "path_a"

    def test_conditional_false(self, graph):
        result = graph.invoke({"input": "test", "condition": False})
        assert result["path"] == "path_b"

    @pytest.mark.parametrize("condition,expected", [
        (True, "path_a"),
        (False, "path_b"),
        (None, "default"),
    ])
    def test_routing_parametrized(self, graph, condition, expected):
        result = graph.invoke({"condition": condition})
        assert result["path"] == expected
```

## Testing with Checkpointer

```python
def test_multi_turn(self, graph_with_memory):
    config = {"configurable": {"thread_id": "test-123"}}
    
    # First turn
    result1 = graph_with_memory.invoke({"input": "Hello"}, config=config)
    
    # Second turn - should remember
    result2 = graph_with_memory.invoke({"input": "What did I say?"}, config=config)
    
    assert len(result2["messages"]) > 1

def test_threads_isolated(self, graph_with_memory):
    config1 = {"configurable": {"thread_id": "user-1"}}
    config2 = {"configurable": {"thread_id": "user-2"}}
    
    graph_with_memory.invoke({"input": "User 1"}, config=config1)
    result = graph_with_memory.invoke({"input": "test"}, config=config2)
    
    assert "User 1" not in str(result)
```

## Testing Streaming

```python
def test_stream_updates(self, graph):
    chunks = list(graph.stream({"input": "test"}, stream_mode="updates"))
    
    assert len(chunks) > 0
    for chunk in chunks:
        assert isinstance(chunk, dict)

def test_stream_values(self, graph):
    chunks = list(graph.stream({"input": "test"}, stream_mode="values"))
    
    for chunk in chunks:
        assert "input" in chunk
```

## Testing Error Handling

```python
def test_error_propagates(self, graph):
    with pytest.raises(ValueError):
        graph.invoke({"input": "trigger_error"})

def test_error_handled(self, graph):
    result = graph.invoke({"input": "error_input"})
    
    assert "error" in result
```

## Testing Graph Structure

```python
def test_has_expected_nodes(self, graph):
    expected = ["input", "process", "output"]
    
    for node_name in expected:
        assert node_name in graph.nodes
```

