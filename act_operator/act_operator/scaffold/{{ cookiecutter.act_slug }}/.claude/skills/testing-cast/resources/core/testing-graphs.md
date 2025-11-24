# Testing Graphs

## When to Use This Resource
Read this when writing tests for graph classes that inherit from `BaseGraph`.

## Basic Graph Test Pattern

```python
# tests/test_graph.py
import pytest
from langgraph.checkpoint.memory import MemorySaver
from casts.{ cast_name }.graph import MyCastGraph

class TestMyCastGraph:
    """Test suite for MyCastGraph."""

    @pytest.fixture
    def graph(self):
        """Provides a compiled graph for testing."""
        graph_builder = MyCastGraph()
        return graph_builder.build()

    def test_graph_compiles(self, graph):
        """Graph should compile without errors."""
        assert graph is not None
        assert hasattr(graph, "invoke")

    def test_graph_invoke_basic(self, graph):
        """Test basic graph invocation."""
        result = graph.invoke({"input": "test"})

        assert "result" in result
        assert result["result"] is not None

    def test_graph_with_config(self, graph):
        """Test graph with thread_id."""
        config = {"configurable": {"thread_id": "test-123"}}

        result = graph.invoke({"input": "test"}, config=config)

        assert result is not None
```

## Testing Individual Nodes in Graph

```python
class TestGraphNodes:
    def test_individual_node(self, graph):
        """Test a single node from the graph."""
        # Access node directly
        node = graph.nodes["process_input"]

        # Invoke node with state
        state = {"input": "test"}
        result = node.invoke(state)

        assert "processed" in result

    def test_node_sequence(self, graph):
        """Test nodes execute in correct order."""
        state = {"input": "test", "step": 0}

        # Execute specific nodes
        state = graph.nodes["node1"].invoke(state)
        assert state["step"] == 1

        state = graph.nodes["node2"].invoke(state)
        assert state["step"] == 2
```

## Testing Edge Routing

```python
class TestGraphRouting:
    def test_conditional_edge_true(self, graph):
        """Test conditional edge takes correct path."""
        # State that triggers specific route
        state = {"input": "test", "condition": True}

        result = graph.invoke(state)

        # Verify correct path was taken
        assert result["route_taken"] == "path_a"

    def test_conditional_edge_false(self, graph):
        state = {"input": "test", "condition": False}

        result = graph.invoke(state)

        assert result["route_taken"] == "path_b"

    @pytest.mark.parametrize("condition,expected_path", [
        (True, "path_a"),
        (False, "path_b"),
        (None, "default"),
    ])
    def test_routing_parametrized(self, graph, condition, expected_path):
        state = {"input": "test", "condition": condition}

        result = graph.invoke(state)

        assert result["route_taken"] == expected_path
```

## Testing with Checkpointer

```python
class TestGraphWithCheckpointer:
    @pytest.fixture
    def graph_with_memory(self):
        """Graph with MemorySaver for testing."""
        graph_builder = MyCastGraph()
        checkpointer = MemorySaver()
        return graph_builder.build(checkpointer=checkpointer)

    def test_multi_turn_conversation(self, graph_with_memory):
        config = {"configurable": {"thread_id": "test-123"}}

        # First turn
        result1 = graph_with_memory.invoke({"input": "Hello"}, config=config)
        assert "messages" in result1

        # Second turn - should remember first
        result2 = graph_with_memory.invoke({"input": "What did I say?"}, config=config)
        assert len(result2["messages"]) > 1

    def test_different_threads_isolated(self, graph_with_memory):
        config1 = {"configurable": {"thread_id": "user-1"}}
        config2 = {"configurable": {"thread_id": "user-2"}}

        # Different threads should be isolated
        graph_with_memory.invoke({"input": "User 1 data"}, config=config1)
        result = graph_with_memory.invoke({"input": "test"}, config=config2)

        # User 2 should not see User 1's data
        assert "User 1 data" not in str(result)
```

## Testing Graph Streaming

```python
class TestGraphStreaming:
    def test_stream_updates(self, graph):
        """Test streaming state updates."""
        chunks = list(graph.stream({"input": "test"}, stream_mode="updates"))

        assert len(chunks) > 0
        # Each chunk should be a dict with node name as key
        for chunk in chunks:
            assert isinstance(chunk, dict)

    def test_stream_values(self, graph):
        """Test streaming full state values."""
        chunks = list(graph.stream({"input": "test"}, stream_mode="values"))

        # Should get complete state after each node
        for chunk in chunks:
            assert "input" in chunk
```

## Testing Partial Graph Execution

```python
class TestPartialExecution:
    def test_execute_until_node(self, graph_with_memory):
        """Execute graph until specific node."""
        config = {"configurable": {"thread_id": "test-123"}}

        # Start execution
        graph_with_memory.update_state(
            config,
            {"input": "test"},
            as_node="__start__"
        )

        # Execute until specific node
        result = graph_with_memory.invoke(
            None,
            config=config,
            interrupt_after=["intermediate_node"]
        )

        # Check state at interrupt
        state = graph_with_memory.get_state(config)
        assert "intermediate_node" in state.next
```

## Testing Error Handling in Graph

```python
class TestGraphErrorHandling:
    def test_node_error_propagates(self, graph):
        """Errors in nodes should be handled."""
        with pytest.raises(ValueError):
            graph.invoke({"input": "trigger_error"})

    def test_error_caught_by_handler(self, graph):
        """Graph with error handler should not raise."""
        result = graph.invoke({"input": "error_input"})

        assert "error" in result
        assert result["error"] is not None
```

## Mocking in Graph Tests

```python
class TestGraphWithMocks:
    def test_with_mocked_node(self, monkeypatch):
        """Replace a node with a mock."""
        def mock_node(state):
            return {"mocked": True}

        graph_builder = MyCastGraph()
        graph = graph_builder.build()

        # Mock specific node
        monkeypatch.setattr(graph.nodes["expensive_node"], "invoke", mock_node)

        result = graph.invoke({"input": "test"})
        assert result.get("mocked") is True
```

## Common Patterns

### Pattern: Test Graph Structure
```python
def test_graph_has_expected_nodes(self, graph):
    """Verify graph contains expected nodes."""
    expected_nodes = ["input", "process", "output"]

    for node_name in expected_nodes:
        assert node_name in graph.nodes
```

### Pattern: Snapshot Testing
```python
def test_graph_output_snapshot(self, graph, snapshot):
    """Compare output with saved snapshot."""
    result = graph.invoke({"input": "consistent input"})

    # Pytest plugin pytest-snapshot
    assert result == snapshot
```

## References
- Related: `testing-nodes.md` (testing individual nodes)
- Related: `integration-testing.md` (complete workflow tests)
- Related: `mocking-strategies.md` (advanced mocking)
