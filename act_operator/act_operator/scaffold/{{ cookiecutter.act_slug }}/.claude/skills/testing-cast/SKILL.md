---
name: testing-cast
description: Use when writing pytest tests for LangGraph nodes and casts - provides patterns for mocking, fixtures, state testing, and graph integration tests
---

# Testing Cast

## Overview

**Test nodes and graphs with pytest.** Use mocking for LLMs, fixtures for reusability, and integration tests for full graph flows.

## When to Use

Use when:
- Writing tests for nodes
- Testing graph integration
- Mocking LLMs and external services
- Testing routing logic
- Validating state updates

**Prerequisite:** Node/graph implementation with `developing-cast` skill

## Core Workflow

### 1. Node Unit Tests

Test individual nodes in isolation:

```python
# tests/test_nodes.py
import pytest
from unittest.mock import Mock
from langchain_core.messages import AIMessage
from modules.nodes import AnalyzerNode

@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    llm = Mock()
    llm.invoke.return_value = AIMessage(content="Test analysis")
    return llm

@pytest.fixture
def analyzer_node(mock_llm):
    """Node with mocked LLM."""
    return AnalyzerNode(llm=mock_llm)

def test_node_executes(analyzer_node):
    """Test basic node execution."""
    state = {"query": "test query"}
    result = analyzer_node.execute(state)

    assert "analysis" in result
    assert result["analysis"] == "Test analysis"

def test_node_calls_llm(analyzer_node, mock_llm):
    """Verify LLM is called correctly."""
    state = {"query": "test"}
    analyzer_node.execute(state)

    mock_llm.invoke.assert_called_once()
```

### 2. State Testing

Verify state updates:

```python
def test_state_updates(analyzer_node):
    """Test state update structure."""
    state = {"query": "test", "other": "value"}

    result = analyzer_node.execute(state)

    # Returns dict with updates
    assert isinstance(result, dict)

    # Contains expected key
    assert "analysis" in result

    # Doesn't mutate input state
    assert state == {"query": "test", "other": "value"}
```

### 3. Graph Integration Tests

Test complete graph flows:

```python
# tests/test_graph.py
import pytest
from graph import MyGraph

@pytest.fixture
def graph():
    """Compiled graph instance."""
    return MyGraph().build()

def test_graph_end_to_end(graph):
    """Test full graph execution."""
    input_state = {
        "query": "test query",
        "user_id": "123"
    }

    result = graph.invoke(input_state)

    # Verify output schema
    assert "result" in result
    assert "status" in result
    assert result["status"] == "complete"

def test_graph_routing(graph):
    """Test conditional routing."""
    # Test success path
    result = graph.invoke({"status": "valid"})
    assert "success" in result

    # Test error path
    result = graph.invoke({"status": "invalid"})
    assert "error" in result
```

## Mocking Patterns

### Mock LLMs

```python
@pytest.fixture
def mock_llm():
    """Standard LLM mock."""
    llm = Mock()
    llm.invoke.return_value = AIMessage(content="Response")
    return llm

@pytest.fixture
def mock_llm_error():
    """LLM that raises errors."""
    llm = Mock()
    llm.invoke.side_effect = Exception("API Error")
    return llm
```

### Mock Tools

```python
@pytest.fixture
def mock_search_tool():
    """Mock search tool."""
    tool = Mock()
    tool.invoke.return_value = "Search results"
    return tool

def test_node_with_tool(mock_search_tool):
    """Test node that uses tool."""
    node = SearchNode(tool=mock_search_tool)
    result = node.execute({"query": "test"})

    mock_search_tool.invoke.assert_called_with("test")
    assert "results" in result
```

### Mock Runtime

```python
@pytest.fixture
def mock_runtime():
    """Mock runtime with store."""
    runtime = Mock()
    runtime.store = Mock()
    runtime.store.get.return_value = {"cached": "data"}
    runtime.store.put.return_value = None
    return runtime

def test_node_with_runtime(mock_runtime):
    """Test node using runtime store."""
    node = MemoryNode()
    config = {"configurable": {"thread_id": "test-thread"}}

    result = node.execute(
        {"query": "test"},
        runtime=mock_runtime,
        config=config
    )

    # Verify store was accessed
    runtime.store.get.assert_called_once()
```

## Fixture Patterns

### Node Fixtures

```python
@pytest.fixture
def simple_node():
    """Basic node without dependencies."""
    return TransformNode()

@pytest.fixture
def node_with_deps(mock_llm, mock_tool):
    """Node with dependencies injected."""
    return ComplexNode(llm=mock_llm, tool=mock_tool)
```

### State Fixtures

```python
@pytest.fixture
def valid_state():
    """Valid input state."""
    return {
        "query": "test query",
        "user_id": "user123",
        "session_id": "session456"
    }

@pytest.fixture
def empty_state():
    """Empty state for error testing."""
    return {}

@pytest.fixture
def invalid_state():
    """State with invalid data."""
    return {
        "query": "",  # Empty query
        "user_id": None
    }
```

### Parametrized Tests

```python
@pytest.mark.parametrize("query,expected", [
    ("simple query", "simple"),
    ("UPPERCASE", "UPPERCASE"),
    ("with symbols !@#", "with symbols"),
])
def test_query_processing(analyzer_node, query, expected):
    """Test multiple query types."""
    result = analyzer_node.execute({"query": query})
    assert expected in result["analysis"]
```

## Testing Routing Logic

```python
# tests/test_conditions.py
from modules.conditions import route_by_status

def test_success_route():
    """Test routing to success."""
    state = {"status": "success"}
    route = route_by_status(state)
    assert route == "success_handler"

def test_error_route():
    """Test routing to error."""
    state = {"status": "error"}
    route = route_by_status(state)
    assert route == "error_handler"

def test_default_route():
    """Test default routing."""
    state = {"status": "unknown"}
    route = route_by_status(state)
    assert route == "default_handler"
```

## Testing Error Handling

```python
def test_node_handles_missing_field():
    """Test graceful handling of missing data."""
    node = ProcessorNode()
    state = {}  # Missing required field

    with pytest.raises(ValueError, match="Missing required field"):
        node.execute(state)

def test_node_handles_llm_error(mock_llm_error):
    """Test LLM error handling."""
    node = AnalyzerNode(llm=mock_llm_error)
    state = {"query": "test"}

    result = node.execute(state)

    # Node catches error and returns error state
    assert "error" in result
    assert result["error"] is not None
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_nodes.py

# Run with coverage
uv run pytest --cov=modules --cov-report=html

# Run specific test
uv run pytest tests/test_nodes.py::test_node_executes

# Verbose output
uv run pytest -v

# Show print statements
uv run pytest -s
```

## Test Organization

```
casts/<cast_name>/
└── tests/
    ├── __init__.py
    ├── conftest.py          # Shared fixtures
    ├── test_nodes.py        # Node unit tests
    ├── test_conditions.py   # Routing tests
    ├── test_graph.py        # Integration tests
    └── test_tools.py        # Tool tests (if applicable)
```

**conftest.py for shared fixtures:**
```python
# tests/conftest.py
import pytest
from unittest.mock import Mock
from langchain_core.messages import AIMessage

@pytest.fixture
def mock_llm():
    """Shared LLM mock."""
    llm = Mock()
    llm.invoke.return_value = AIMessage(content="Test")
    return llm

@pytest.fixture
def valid_state():
    """Shared valid state."""
    return {"query": "test", "user_id": "123"}
```

## Best Practices

### DO

✅ Use fixtures for reusability
✅ Mock external dependencies (LLMs, APIs)
✅ Test state updates, not internals
✅ Test both happy and error paths
✅ Use parametrize for multiple cases
✅ Write descriptive test names
✅ Keep tests independent
✅ Test integration flows

### DON'T

❌ Call real LLMs in tests
❌ Test implementation details
❌ Share state between tests
❌ Write tests that depend on order
❌ Skip error case testing
❌ Mock what you don't own (LangGraph internals)
❌ Over-mock (test real logic where possible)

## Common Patterns

### Test Node with Messages

```python
from langchain_core.messages import HumanMessage, AIMessage

def test_messages_state(node):
    """Test node with messages."""
    state = {
        "messages": [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there")
        ]
    }

    result = node.execute(state)

    assert "messages" in result
    assert len(result["messages"]) > 0
```

### Test Async Nodes

```python
import pytest

@pytest.mark.asyncio
async def test_async_node():
    """Test async node execution."""
    node = AsyncProcessorNode()
    state = {"query": "test"}

    result = await node.async_execute(state)

    assert "result" in result
```

### Test with Temporary Files

```python
import tempfile
from pathlib import Path

def test_file_processor():
    """Test node that processes files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("test content")

        node = FileProcessorNode()
        result = node.execute({"file_path": str(test_file)})

        assert result["processed"] is True
```

## Quick Reference

| Test Type | Pattern | Fixture |
|-----------|---------|---------|
| Node unit test | Test execute() | mock_llm, valid_state |
| State updates | Assert dict returned | valid_state |
| Routing logic | Test condition functions | state fixtures |
| Error handling | pytest.raises | invalid_state |
| Graph integration | graph.invoke() | compiled graph |
| Tool usage | Mock tool.invoke | mock_tool |
| Memory | Mock runtime.store | mock_runtime |

## Example Test Suite

```python
# tests/test_analyzer_node.py
import pytest
from unittest.mock import Mock
from langchain_core.messages import AIMessage
from modules.nodes import AnalyzerNode

# Fixtures
@pytest.fixture
def mock_llm():
    llm = Mock()
    llm.invoke.return_value = AIMessage(content="Analysis result")
    return llm

@pytest.fixture
def analyzer_node(mock_llm):
    return AnalyzerNode(llm=mock_llm)

@pytest.fixture
def valid_state():
    return {"query": "test query", "user_id": "123"}

# Tests
class TestAnalyzerNode:
    """Test suite for AnalyzerNode."""

    def test_basic_execution(self, analyzer_node, valid_state):
        """Test node executes successfully."""
        result = analyzer_node.execute(valid_state)
        assert "analysis" in result

    def test_llm_called(self, analyzer_node, mock_llm, valid_state):
        """Verify LLM is invoked."""
        analyzer_node.execute(valid_state)
        mock_llm.invoke.assert_called_once()

    def test_state_not_mutated(self, analyzer_node, valid_state):
        """Ensure input state unchanged."""
        original = valid_state.copy()
        analyzer_node.execute(valid_state)
        assert valid_state == original

    def test_empty_query_error(self, analyzer_node):
        """Test error on empty query."""
        with pytest.raises(ValueError):
            analyzer_node.execute({"query": ""})

    @pytest.mark.parametrize("query", [
        "simple query",
        "complex query with details",
        "query with symbols !@#"
    ])
    def test_various_queries(self, analyzer_node, query):
        """Test different query types."""
        result = analyzer_node.execute({"query": query})
        assert result["analysis"]
```

## Real-World Impact

Good testing practices:
- Catch bugs before production
- Enable confident refactoring
- Document expected behavior
- Faster development with quick feedback
- Lower maintenance costs

**Time investment:** 30 min writing tests → Saves hours debugging production issues

## Next Steps

- **Implementing nodes:** See `developing-cast` skill
- **Architecture design:** See `architecting-act` skill
- **Running tests:** `uv run pytest` in project directory
