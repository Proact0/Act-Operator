# Node Testing

## When to Use

Testing individual nodes in isolation (unit tests). Fast tests with mocked dependencies.

## Basic Pattern

```python
import pytest
from casts.my_agent.nodes import ProcessNode
from casts.my_agent.state import MyAgentState

def test_process_node():
    """Test ProcessNode executes correctly."""
    node = ProcessNode()
    
    state: MyAgentState = {
        "messages": [],
        "task": "test task",
    }
    
    result = node.execute(state)
    
    assert "results" in result
    assert result["results"] is not None
    assert "messages" in result
```

## Testing with Mock LLM

```python
from langchain_core.messages import AIMessage

class MockLLM:
    """Mock LLM for testing."""
    def invoke(self, messages):
        return AIMessage(content="Mock response")
    
    def bind_tools(self, tools):
        return self

@pytest.fixture
def mock_llm():
    return MockLLM()

def test_agent_node(mock_llm):
    """Test node with mocked LLM."""
    from casts.my_agent.nodes import AgentNode
    
    node = AgentNode(mock_llm)
    state = {"messages": []}
    
    result = node.execute(state)
    
    assert len(result["messages"]) == 1
    assert result["messages"][0].content == "Mock response"
```

## Testing Node with Dependencies

```python
@pytest.fixture
def process_node(mock_llm):
    """Fixture providing configured node."""
    return ProcessNode(model=mock_llm, verbose=False)

def test_node_with_fixture(process_node):
    """Test using node fixture."""
    state = {"task": "test"}
    result = process_node.execute(state)
    assert "result" in result
```

## Testing State Updates

```python
def test_node_updates_state_correctly():
    """Test node returns correct state updates."""
    node = ProcessNode()
    
    initial_state = {
        "messages": [],
        "count": 0,
        "data": {}
    }
    
    result = node.execute(initial_state)
    
    # Verify returned updates
    assert isinstance(result, dict)
    assert "messages" in result  # Should add messages
    assert "count" in result      # Should increment count
```

## Testing Error Handling

```python
def test_node_handles_errors():
    """Test node handles errors gracefully."""
    node = ProcessNode()
    
    # Invalid state
    state = {"invalid": "state"}
    
    result = node.execute(state)
    
    assert "error" in result
    assert result["error"] is not None
```

## Parametrized Tests

```python
@pytest.mark.parametrize("input_task,expected_status", [
    ("simple task", "completed"),
    ("complex task", "in_progress"),
    ("", "error"),
])
def test_node_with_different_inputs(input_task, expected_status):
    """Test node with various inputs."""
    node = ProcessNode()
    state = {"task": input_task}
    
    result = node.execute(state)
    
    assert result["status"] == expected_status
```

## Testing Node with Runtime

```python
class MockRuntime:
    """Mock Runtime for testing."""
    def __init__(self):
        self.store = MockStore()

class MockStore:
    """Mock Store for testing."""
    def __init__(self):
        self._data = {}
    
    def get(self, namespace, key):
        return self._data.get((namespace, key))
    
    def put(self, namespace, key, value):
        self._data[(namespace, key)] = value

@pytest.fixture
def mock_runtime():
    return MockRuntime()

def test_node_with_runtime(mock_runtime):
    """Test node that accesses runtime."""
    from casts.my_agent.nodes import MemoryNode
    
    node = MemoryNode()
    state = {"user_id": "test-user"}
    
    result = node.execute(state, runtime=mock_runtime)
    
    assert "memories" in result
```

## Testing Node Logging

```python
import logging

def test_node_logging(caplog):
    """Test node logs correctly when verbose."""
    node = ProcessNode(verbose=True)
    
    with caplog.at_level(logging.DEBUG):
        node.execute({"task": "test"})
    
    assert "Executing" in caplog.text
    assert "Completed" in caplog.text
```

## Testing Base Class Behavior

```python
def test_node_inherits_from_base():
    """Test node inherits from BaseNode."""
    from casts.base_node import BaseNode
    
    node = ProcessNode()
    
    assert isinstance(node, BaseNode)
    assert hasattr(node, "execute")
    assert hasattr(node, "log")
    assert hasattr(node, "get_thread_id")
```

## Common Assertions

```python
def test_comprehensive_assertions():
    """Example of common assertions."""
    node = ProcessNode()
    state = {"task": "test"}
    
    result = node.execute(state)
    
    # Type assertions
    assert isinstance(result, dict)
    
    # Presence assertions
    assert "result" in result
    assert result.get("error") is None
    
    # Value assertions
    assert result["status"] == "completed"
    assert len(result["messages"]) > 0
    
    # Structure assertions
    assert all(k in result for k in ["result", "status"])
```

## Testing Tools in Nodes

```python
def test_node_with_tools():
    """Test node that uses tools."""
    from modules.tools import calculator
    
    node = ToolCallingNode(tools=[calculator])
    state = {"query": "What is 5 + 3?"}
    
    result = node.execute(state)
    
    assert "tool_results" in result
    assert result["tool_results"][0] == 8
```

## Test Organization

```python
class TestProcessNode:
    """Group tests for ProcessNode."""
    
    def test_basic_execution(self):
        """Test basic execution."""
        node = ProcessNode()
        result = node.execute({"task": "test"})
        assert result is not None
    
    def test_error_handling(self):
        """Test error handling."""
        node = ProcessNode()
        result = node.execute({})
        assert "error" in result
    
    def test_with_dependencies(self, mock_llm):
        """Test with mocked dependencies."""
        node = ProcessNode(mock_llm)
        result = node.execute({"task": "test"})
        assert "messages" in result
```

## Quick Reference

**Basic test:**
```python
def test_node():
    node = MyNode()
    result = node.execute(state)
    assert condition
```

**With fixture:**
```python
def test_node(mock_llm):
    node = MyNode(mock_llm)
    result = node.execute(state)
    assert condition
```

**Parametrized:**
```python
@pytest.mark.parametrize("input,expected", cases)
def test_node(input, expected):
    result = node.execute({"data": input})
    assert result["output"] == expected
```

## Common Mistakes

❌ **Not mocking LLM** - leads to slow tests, API costs
✓ Use mock_llm fixture

❌ **Not asserting anything** - test runs but validates nothing
✓ Always include assertions

❌ **Testing implementation details** - tests break with refactoring
✓ Test behavior and outputs

❌ **No test isolation** - tests affect each other
✓ Use function-scoped fixtures

## References

- Graph testing: `graph-testing.md`
- Async testing: `async-testing.md`
- Mocking: `mocking.md`
