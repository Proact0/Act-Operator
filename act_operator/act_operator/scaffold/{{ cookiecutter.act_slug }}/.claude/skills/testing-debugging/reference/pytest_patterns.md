# Pytest Patterns for LangGraph

Comprehensive guide to unit testing, integration testing, and test patterns for LangGraph applications.

## Table of Contents

1. [Introduction](#introduction)
2. [Test Environment Setup](#test-environment-setup)
3. [Unit Testing Nodes](#unit-testing-nodes)
4. [Integration Testing Graphs](#integration-testing-graphs)
5. [Fixtures and Test Data](#fixtures-and-test-data)
6. [Mocking Patterns](#mocking-patterns)
7. [Async Testing](#async-testing)
8. [State Testing](#state-testing)
9. [Test Organization](#test-organization)
10. [Best Practices](#best-practices)
11. [Common Patterns](#common-patterns)
12. [Troubleshooting](#troubleshooting)

---

## Introduction

Testing LangGraph applications requires understanding nodes, state management, and graph execution patterns. This guide covers comprehensive testing strategies.

**What to test:**
- Node execution logic
- State transformations
- Routing functions
- Graph integration
- Error handling

**Testing pyramid:**
```
        /\
       /  \     E2E Tests
      /----\
     /      \   Integration Tests
    /--------\
   /          \  Unit Tests
  /____________\
```

---

## Test Environment Setup

### Basic Setup

```python
# tests/conftest.py
import pytest
from dataclasses import dataclass

@dataclass(kw_only=True)
class TestState:
    """Test state class."""
    input: str
    output: str = None
    count: int = 0

@pytest.fixture
def sample_state():
    """Fixture for sample state."""
    return TestState(input="test input")

@pytest.fixture
def sample_config():
    """Fixture for config."""
    from langgraph.graph import RunnableConfig
    return RunnableConfig(
        configurable={"thread_id": "test-thread"}
    )
```

### Project Structure

```
project/
├── src/
│   ├── nodes/
│   │   ├── __init__.py
│   │   └── process_node.py
│   ├── graphs/
│   │   └── my_graph.py
│   └── utils/
│       └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_nodes.py
│   │   └── test_utils.py
│   ├── integration/
│   │   └── test_graphs.py
│   └── fixtures/
│       └── data.py
├── pyproject.toml
└── pytest.ini
```

### Pytest Configuration

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=term
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    asyncio: Async tests
```

---

## Unit Testing Nodes

### Basic Node Testing

```python
# tests/unit/test_nodes.py
import pytest
from src.nodes.process_node import ProcessNode

def test_process_node_basic():
    """Test basic node execution."""
    node = ProcessNode()
    
    state = {"input": "test"}
    result = node(state)
    
    assert "output" in result
    assert result["output"] == "processed: test"

def test_process_node_empty_input():
    """Test node with empty input."""
    node = ProcessNode()
    
    state = {"input": ""}
    result = node(state)
    
    assert result["output"] == ""

def test_process_node_with_config():
    """Test node with config parameter."""
    node = ProcessNode()
    
    from langgraph.graph import RunnableConfig
    config = RunnableConfig(configurable={"thread_id": "test"})
    
    state = {"input": "test"}
    result = node(state, config=config)
    
    assert "output" in result
```

### Testing Node Initialization

```python
def test_node_initialization():
    """Test node initialization."""
    node = ProcessNode(multiplier=3, verbose=True)
    
    assert node.multiplier == 3
    assert node.verbose is True

def test_node_default_initialization():
    """Test default initialization."""
    node = ProcessNode()
    
    assert node.multiplier == 2  # Default value
    assert node.verbose is False
```

### Testing State Updates

```python
def test_state_update():
    """Test that node updates state correctly."""
    node = ProcessNode()
    
    state = {"input": "test", "count": 0}
    result = node(state)
    
    # Node should return update dict
    assert isinstance(result, dict)
    
    # Should contain expected updates
    assert "output" in result
    assert "count" in result
    assert result["count"] == 1
```

### Testing Error Handling

```python
def test_node_error_handling():
    """Test node error handling."""
    node = ProcessNode()
    
    state = {"input": "invalid"}
    result = node(state)
    
    # Node should catch error and return error field
    assert "error" in result
    assert result["error"] is not None
    assert result["output"] is None

def test_node_exception_propagation():
    """Test that exceptions can propagate."""
    node = FailFastNode()  # Node that doesn't catch errors
    
    state = {"input": "bad"}
    
    with pytest.raises(ValueError) as exc_info:
        node(state)
    
    assert "invalid input" in str(exc_info.value)
```

---

## Integration Testing Graphs

### Basic Graph Testing

```python
# tests/integration/test_graphs.py
import pytest
from src.graphs.my_graph import MyGraph

def test_graph_execution():
    """Test complete graph execution."""
    graph = MyGraph()
    compiled = graph.build()
    
    result = compiled.invoke({"input": "test"})
    
    assert "output" in result
    assert result["output"] is not None

def test_graph_with_config():
    """Test graph with configuration."""
    from langgraph.graph import RunnableConfig
    from langgraph.checkpoint.memory import MemorySaver
    
    graph = MyGraph()
    checkpointer = MemorySaver()
    compiled = graph.build(checkpointer=checkpointer)
    
    config = RunnableConfig(
        configurable={"thread_id": "test-123"}
    )
    
    result = compiled.invoke({"input": "test"}, config=config)
    
    assert result is not None
```

### Testing Graph Routing

```python
def test_conditional_routing():
    """Test conditional edge routing."""
    graph = MyGraph()
    compiled = graph.build()
    
    # Test success path
    result_success = compiled.invoke({"input": "valid"})
    assert result_success["path"] == "success"
    
    # Test error path
    result_error = compiled.invoke({"input": "invalid"})
    assert result_error["path"] == "error"
```

### Testing Multi-Step Execution

```python
def test_multi_step_execution():
    """Test multi-step graph execution."""
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.graph import RunnableConfig
    
    graph = MyGraph()
    checkpointer = MemorySaver()
    compiled = graph.build(checkpointer=checkpointer)
    
    config = RunnableConfig(
        configurable={"thread_id": "test-multi"}
    )
    
    # First invocation
    result1 = compiled.invoke({"query": "Hello"}, config=config)
    assert len(result1["messages"]) == 2  # Human + AI
    
    # Second invocation - continues conversation
    result2 = compiled.invoke({"query": "Follow-up"}, config=config)
    assert len(result2["messages"]) == 4  # Previous + new
```

---

## Fixtures and Test Data

### State Fixtures

```python
# tests/conftest.py
import pytest
from dataclasses import dataclass

@dataclass(kw_only=True)
class State:
    input: str
    output: str = None

@pytest.fixture
def empty_state():
    """Empty state."""
    return State(input="")

@pytest.fixture
def basic_state():
    """Basic valid state."""
    return State(input="test input")

@pytest.fixture
def error_state():
    """State that causes errors."""
    return State(input="ERROR")
```

### Node Fixtures

```python
@pytest.fixture
def process_node():
    """ProcessNode instance."""
    from src.nodes.process_node import ProcessNode
    return ProcessNode()

@pytest.fixture
def verbose_node():
    """Node with verbose logging."""
    from src.nodes.process_node import ProcessNode
    return ProcessNode(verbose=True)
```

### Graph Fixtures

```python
@pytest.fixture
def compiled_graph():
    """Compiled graph."""
    from src.graphs.my_graph import MyGraph
    graph = MyGraph()
    return graph.build()

@pytest.fixture
def graph_with_checkpointer():
    """Graph with memory checkpointer."""
    from src.graphs.my_graph import MyGraph
    from langgraph.checkpoint.memory import MemorySaver
    
    graph = MyGraph()
    checkpointer = MemorySaver()
    return graph.build(checkpointer=checkpointer)
```

### Test Data Fixtures

```python
@pytest.fixture
def sample_messages():
    """Sample message list."""
    from langchain_core.messages import HumanMessage, AIMessage
    return [
        HumanMessage(content="Hello"),
        AIMessage(content="Hi there!"),
    ]

@pytest.fixture
def test_data_dir(tmp_path):
    """Temporary directory for test data."""
    data_dir = tmp_path / "test_data"
    data_dir.mkdir()
    return data_dir
```

---

## Mocking Patterns

### Mocking External APIs

```python
import pytest
from unittest.mock import Mock, patch

def test_node_with_mock_api():
    """Test node with mocked API."""
    node = APINode()
    
    # Mock the API call
    with patch.object(node, 'call_api') as mock_api:
        mock_api.return_value = {"data": "mocked"}
        
        state = {"query": "test"}
        result = node(state)
        
        assert result["data"] == "mocked"
        mock_api.assert_called_once_with("test")

def test_node_with_mock_response():
    """Test with mocked HTTP response."""
    import aiohttp
    
    node = HTTPNode()
    
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {"result": "success"}
        mock_get.return_value.__aenter__.return_value = mock_response
        
        state = {"url": "http://example.com"}
        result = node(state)
        
        assert result["result"] == "success"
```

### Mocking LLM Calls

```python
def test_llm_node_mock():
    """Test LLM node with mocked model."""
    from langchain_core.messages import AIMessage
    
    node = LLMNode()
    
    # Mock the LLM
    with patch.object(node.llm, 'invoke') as mock_llm:
        mock_llm.return_value = AIMessage(content="Mocked response")
        
        state = {"messages": [HumanMessage(content="Hello")]}
        result = node(state)
        
        assert result["messages"][-1].content == "Mocked response"
```

### Mocking Store Operations

```python
def test_node_with_mock_store():
    """Test node with mocked store."""
    node = StoreNode()
    
    # Create mock runtime with store
    mock_runtime = Mock()
    mock_runtime.store.get.return_value = {"cached": True}
    
    state = {"query": "test"}
    result = node(state, runtime=mock_runtime)
    
    assert result["cached"] is True
    mock_runtime.store.get.assert_called_once()
```

---

## Async Testing

### Basic Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_node():
    """Test async node."""
    from src.nodes.async_node import AsyncNode
    
    node = AsyncNode()
    
    state = {"input": "test"}
    result = await node(state)
    
    assert "output" in result

@pytest.mark.asyncio
async def test_async_graph():
    """Test async graph execution."""
    from src.graphs.async_graph import AsyncGraph
    
    graph = AsyncGraph()
    compiled = graph.build()
    
    result = await compiled.ainvoke({"input": "test"})
    
    assert result is not None
```

### Testing Concurrent Operations

```python
@pytest.mark.asyncio
async def test_concurrent_node():
    """Test node with concurrent operations."""
    import asyncio
    
    node = ConcurrentNode()
    
    state = {"items": [1, 2, 3]}
    result = await node(state)
    
    # Should complete faster than sequential
    assert "results" in result
    assert len(result["results"]) == 3

@pytest.mark.asyncio
async def test_async_timeout():
    """Test async operation with timeout."""
    node = SlowNode()
    
    state = {"input": "test"}
    
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(node(state), timeout=1.0)
```

---

## State Testing

### Testing State Transformations

```python
def test_state_accumulation():
    """Test state accumulation pattern."""
    from typing import Annotated
    from dataclasses import dataclass
    
    def accumulate(old: list, new: list) -> list:
        return old + new if old else new
    
    @dataclass(kw_only=True)
    class State:
        items: Annotated[list, accumulate] = None
    
    node = AccumulateNode()
    
    state = State(items=[1, 2])
    result = node(state)
    
    # Result should have accumulated items
    assert result["items"] == [3, 4]  # New items to add

def test_state_reducer():
    """Test custom state reducer."""
    node = CounterNode()
    
    state = {"count": 5}
    result = node(state)
    
    # Should increment count
    assert result["count"] == 6
```

### Testing State Validation

```python
def test_state_validation():
    """Test state validation."""
    from pydantic import ValidationError
    
    node = ValidatingNode()
    
    # Valid state
    state = {"value": 10}
    result = node(state)
    assert result["valid"] is True
    
    # Invalid state
    with pytest.raises(ValidationError):
        invalid_state = {"value": "not a number"}
        node(invalid_state)
```

---

## Test Organization

### Test Classes

```python
class TestProcessNode:
    """Test suite for ProcessNode."""
    
    def test_basic_processing(self):
        """Test basic processing."""
        node = ProcessNode()
        state = {"input": "test"}
        result = node(state)
        assert "output" in result
    
    def test_error_handling(self):
        """Test error handling."""
        node = ProcessNode()
        state = {"input": "ERROR"}
        result = node(state)
        assert "error" in result
    
    def test_edge_cases(self):
        """Test edge cases."""
        node = ProcessNode()
        
        # Empty input
        assert node({"input": ""})["output"] == ""
        
        # None input
        assert node({"input": None})["error"] is not None
```

### Parameterized Tests

```python
@pytest.mark.parametrize("input_val,expected", [
    ("test", "processed: test"),
    ("hello", "processed: hello"),
    ("", ""),
])
def test_process_various_inputs(input_val, expected):
    """Test node with various inputs."""
    node = ProcessNode()
    
    state = {"input": input_val}
    result = node(state)
    
    assert result["output"] == expected

@pytest.mark.parametrize("score,expected_route", [
    (95, "excellent"),
    (85, "good"),
    (75, "satisfactory"),
    (65, "passing"),
    (45, "failing"),
])
def test_routing_function(score, expected_route):
    """Test routing with various scores."""
    from src.graphs.my_graph import route_by_score
    
    state = {"score": score}
    route = route_by_score(state)
    
    assert route == expected_route
```

---

## Best Practices

### 1. Test One Thing

```python
# ✅ Good - tests one thing
def test_node_processes_input():
    """Test that node processes input."""
    node = ProcessNode()
    state = {"input": "test"}
    result = node(state)
    assert "output" in result

# ❌ Bad - tests multiple things
def test_node_everything():
    """Test everything about node."""
    node = ProcessNode()
    # Tests initialization
    assert node.multiplier == 2
    # Tests execution
    result = node({"input": "test"})
    assert "output" in result
    # Tests error handling
    error_result = node({"input": "ERROR"})
    assert "error" in error_result
```

### 2. Use Descriptive Names

```python
# ✅ Good
def test_node_returns_error_for_invalid_input():
    """Test that node returns error for invalid input."""
    pass

# ❌ Bad
def test_node_1():
    """Test node."""
    pass
```

### 3. Arrange-Act-Assert

```python
def test_with_aaa_pattern():
    """Test using AAA pattern."""
    # Arrange
    node = ProcessNode()
    state = {"input": "test"}
    
    # Act
    result = node(state)
    
    # Assert
    assert result["output"] == "processed: test"
```

### 4. Use Fixtures

```python
# ✅ Good - use fixtures
def test_with_fixture(process_node, basic_state):
    """Test using fixtures."""
    result = process_node(basic_state)
    assert "output" in result

# ❌ Bad - create in every test
def test_without_fixture():
    """Test without fixtures."""
    node = ProcessNode()
    state = {"input": "test"}
    result = node(state)
    assert "output" in result
```

### 5. Test Edge Cases

```python
def test_edge_cases():
    """Test edge cases."""
    node = ProcessNode()
    
    # Empty input
    assert node({"input": ""})
    
    # None input
    assert node({"input": None})
    
    # Very long input
    long_input = "x" * 10000
    assert node({"input": long_input})
    
    # Special characters
    assert node({"input": "!@#$%^&*()"})
```

---

## Common Patterns

### Testing Retry Logic

```python
def test_retry_logic():
    """Test retry mechanism."""
    node = RetryNode()
    
    # First attempt - fails
    state1 = {"input": "test", "retry_count": 0}
    result1 = node(state1)
    assert result1["retry_count"] == 1
    assert result1["error"] is not None
    
    # Second attempt - succeeds
    state2 = {"input": "test", "retry_count": 1}
    result2 = node(state2)
    assert result2["error"] is None
```

### Testing Stateful Operations

```python
def test_stateful_node():
    """Test node that maintains state."""
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.graph import RunnableConfig
    
    graph = build_stateful_graph()
    checkpointer = MemorySaver()
    compiled = graph.build(checkpointer=checkpointer)
    
    config = RunnableConfig(
        configurable={"thread_id": "test-stateful"}
    )
    
    # First call
    result1 = compiled.invoke({"input": "first"}, config=config)
    assert result1["count"] == 1
    
    # Second call - state persists
    result2 = compiled.invoke({"input": "second"}, config=config)
    assert result2["count"] == 2
```

---

## Troubleshooting

### Common Issues

**Issue: Async tests not running**

```python
# Fix: Add @pytest.mark.asyncio
@pytest.mark.asyncio
async def test_async():
    """Async test."""
    await async_operation()
```

**Issue: Fixtures not found**

```python
# Fix: Ensure conftest.py in correct location
# tests/conftest.py
@pytest.fixture
def my_fixture():
    return "value"
```

**Issue: Mocks not working**

```python
# Fix: Patch correct path
# Patch where it's used, not where it's defined
with patch('src.nodes.process_node.api_call') as mock:
    mock.return_value = "mocked"
```

---

## Summary

**Testing pyramid:**
- Unit tests: Test individual nodes
- Integration tests: Test complete graphs
- E2E tests: Test full workflows

**Key practices:**
- Use fixtures for reusable test data
- Mock external dependencies
- Test edge cases and errors
- Organize tests logically
- Use descriptive names

**References:**
- Pytest: https://docs.pytest.org/
- Pytest-asyncio: https://pytest-asyncio.readthedocs.io/
- Python unittest.mock: https://docs.python.org/3/library/unittest.mock.html
