---
name: testing-debugging
description: Test and debug LangGraph applications - use when writing tests, debugging graphs, troubleshooting issues, or validating Cast structure.
---

# Testing & Debugging

**Use this skill when:**
- Writing unit tests for nodes
- Writing integration tests for graphs
- Running tests with pytest
- Debugging graph execution
- Using LangGraph dev server
- Validating Cast structure
- Troubleshooting issues

## Overview

Act projects use pytest for testing and LangGraph dev server for debugging. Tests are organized into unit tests (individual nodes) and integration tests (full graphs).

**Test structure:**
- `tests/unit_tests/` - Unit tests for nodes and components
- `tests/integration_tests/` - Integration tests for graphs

**Tools:**
- `pytest` - Test runner
- `langgraph dev` - Development server with UI
- `validate_cast.py` - Cast structure validator

## Running Tests

### Basic Test Execution

```bash
# Run all tests
uv run pytest -q

# Run specific test file
uv run pytest tests/unit_tests/test_nodes.py

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=casts --cov-report=html
```

### Test Filtering

```bash
# Run tests by name
uv run pytest -k "test_sample_node"

# Run tests in directory
uv run pytest tests/unit_tests/

# Run integration tests only
uv run pytest tests/integration_tests/

# Run failed tests from last run
uv run pytest --lf
```

### Test Output Options

```bash
# Quiet mode (less output)
uv run pytest -q

# Verbose mode (more output)
uv run pytest -v

# Show print statements
uv run pytest -s

# Stop on first failure
uv run pytest -x

# Run N tests in parallel
uv run pytest -n 4
```

## Unit Testing Nodes

### Basic Node Test

```python
"""Test nodes in unit_tests/test_nodes.py"""

import pytest
from casts.my_cast.modules.nodes import ProcessNode
from casts.my_cast.modules.state import State

def test_process_node():
    """Test ProcessNode execution."""
    # Create node
    node = ProcessNode()

    # Create test state
    state = State(query="test input")

    # Execute node
    result = node(state)

    # Assert result
    assert "result" in result
    assert result["result"] == "expected output"
```

### Testing with Fixtures

```python
import pytest

@pytest.fixture
def sample_state():
    """Fixture for sample state."""
    return State(
        query="test query",
        messages=[],
        count=0
    )

@pytest.fixture
def process_node():
    """Fixture for ProcessNode."""
    return ProcessNode(verbose=False)

def test_with_fixtures(process_node, sample_state):
    """Test using fixtures."""
    result = process_node(sample_state)

    assert "result" in result
```

### Testing Node Errors

```python
def test_node_error_handling():
    """Test node handles errors gracefully."""
    node = ProcessNode()
    state = State(query=None)  # Invalid input

    result = node(state)

    # Check error is captured
    assert "error" in result
    assert "Invalid input" in result["error"]
```

### Testing Async Nodes

```python
import pytest

@pytest.mark.asyncio
async def test_async_node():
    """Test async node execution."""
    node = AsyncFetchNode()
    state = State(url="https://example.com")

    result = await node(state)

    assert "data" in result
    assert result["data"] is not None
```

### Mocking External Calls

```python
from unittest.mock import Mock, patch

def test_node_with_mock():
    """Test node with mocked external call."""
    node = FetchNode()
    state = State(url="https://api.example.com")

    # Mock external API call
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {"result": "mocked"}

        result = node(state)

        assert result["data"] == {"result": "mocked"}
        mock_get.assert_called_once()
```

## Integration Testing Graphs

### Basic Graph Test

```python
"""Test graphs in integration_tests/test_graph.py"""

from casts.my_cast.graph import my_cast_graph

def test_graph_execution():
    """Test full graph execution."""
    # Get compiled graph
    graph = my_cast_graph()

    # Invoke graph
    result = graph.invoke({
        "query": "test input"
    })

    # Assert output
    assert "messages" in result
    assert len(result["messages"]) > 0
```

### Testing Graph Flow

```python
def test_graph_node_sequence():
    """Test nodes execute in correct order."""
    graph = my_cast_graph()

    # Track execution order
    executed_nodes = []

    # Invoke and collect node names
    for event in graph.stream({"query": "test"}):
        for node_name in event.keys():
            executed_nodes.append(node_name)

    # Verify sequence
    assert executed_nodes == ["validate", "process", "format"]
```

### Testing Conditional Routing

```python
def test_graph_routing():
    """Test conditional routing works."""
    graph = my_cast_graph()

    # Test route A
    result_a = graph.invoke({"category": "math"})
    assert "math_result" in result_a

    # Test route B
    result_b = graph.invoke({"category": "search"})
    assert "search_result" in result_b
```

### Testing with Checkpointer

```python
from langgraph.checkpoint.memory import MemorySaver

def test_graph_with_persistence():
    """Test graph with checkpointer."""
    checkpointer = MemorySaver()
    graph = my_cast_graph.build()

    # Note: Need to recompile with checkpointer
    # This is a simplified example

    config = {"configurable": {"thread_id": "test-thread"}}

    # First invocation
    graph.invoke({"input": "step 1"}, config=config)

    # Second invocation (continues from checkpoint)
    result = graph.invoke({"input": "step 2"}, config=config)

    assert result is not None
```

## LangGraph Dev Server

### Starting Dev Server

```bash
# Start dev server
uv run langgraph dev

# With tunnel (for non-Chrome browsers)
uv run langgraph dev --tunnel

# URLs:
# - API: http://127.0.0.1:2024
# - Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
# - API Docs: http://127.0.0.1:2024/docs
```

### Using LangGraph Studio

**Features:**
- Visual graph topology
- Step-through execution
- State inspection at each node
- Message history visualization
- Interactive debugging

**Workflow:**
1. Start dev server: `uv run langgraph dev`
2. Open Studio UI in browser
3. Select graph from dropdown
4. Enter input and run
5. Step through execution
6. Inspect state at each node

### Testing via API

```python
import requests

def test_via_dev_server():
    """Test graph via dev server API."""
    response = requests.post(
        "http://127.0.0.1:2024/invoke",
        json={
            "graph_id": "my_cast",
            "input": {"query": "test"}
        }
    )

    assert response.status_code == 200
    result = response.json()
    assert "output" in result
```

## Validating Cast Structure

### Using validate_cast.py

```bash
# Validate Cast structure
uv run python scripts/validate_cast.py casts/my_cast

# With verbose output
uv run python scripts/validate_cast.py casts/my_cast --verbose
```

**Checks performed:**
- Required files exist (graph.py, state.py, nodes.py)
- BaseGraph and BaseNode are used correctly
- Python syntax is valid
- pyproject.toml is configured correctly

### Expected Output

```
🔍 Validating Cast: my_cast
============================================================

📁 Checking required files...
  ✅ Graph definition file: graph.py
  ✅ Modules directory: modules/
  ✅ State schema file: modules/state.py
  ✅ Node implementations file: modules/nodes.py

📄 Checking graph.py...
  ✅ Imports BaseGraph
  ✅ Defines class extending BaseGraph
  ✅ Implements build() method

============================================================
📊 Validation Summary
============================================================
✅ All checks passed! Cast structure is valid.
```

## Debugging Techniques

### Print Debugging in Nodes

```python
class DebugNode(BaseNode):
    def execute(self, state):
        # Use self.log() for conditional logging
        self.log("Processing query", query=state.query)

        result = process(state.query)

        self.log("Processing complete", result=result)

        return {"result": result}

# Enable logging
node = DebugNode(verbose=True)
```

### State Inspection

```python
def test_state_at_each_step():
    """Inspect state after each node."""
    graph = my_cast_graph()

    states = []
    for event in graph.stream({"query": "test"}):
        for node_name, node_state in event.items():
            states.append({
                "node": node_name,
                "state": node_state
            })

    # Inspect collected states
    for s in states:
        print(f"After {s['node']}: {s['state']}")
```

### Breakpoint Debugging

```python
def test_with_breakpoint():
    """Use debugger breakpoint."""
    node = ProcessNode()
    state = State(query="test")

    # Set breakpoint
    breakpoint()

    result = node(state)
```

### Graph Visualization

```python
def test_visualize_graph():
    """Generate graph visualization."""
    graph = my_cast_graph()

    # Get graph structure
    graph_def = graph.get_graph()

    # Print nodes and edges
    print("Nodes:", graph_def.nodes)
    print("Edges:", graph_def.edges)

    # Or use graphviz to create diagram
    # graph_def.draw_png("graph.png")
```

## Common Testing Patterns

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("test", "TEST"),
])
def test_uppercase(input, expected):
    """Test with multiple inputs."""
    node = UppercaseNode()
    state = State(text=input)

    result = node(state)

    assert result["text"] == expected
```

### Testing Message History

```python
from langchain.messages import HumanMessage, AIMessage

def test_message_accumulation():
    """Test messages accumulate correctly."""
    graph = my_cast_graph()

    # First turn
    result1 = graph.invoke({
        "messages": [HumanMessage(content="Hello")]
    })

    assert len(result1["messages"]) == 2  # Human + AI

    # Second turn (with history)
    result2 = graph.invoke({
        "messages": result1["messages"] + [HumanMessage(content="How are you?")]
    })

    assert len(result2["messages"]) == 4  # Previous 2 + new Human + AI
```

### Testing Tool Calls

```python
def test_tool_calling():
    """Test LLM tool calling."""
    node = AgentNode()
    state = State(
        messages=[HumanMessage(content="What's 2+2?")]
    )

    result = node(state)

    last_message = result["messages"][-1]

    # Check tool was called
    assert hasattr(last_message, 'tool_calls')
    assert len(last_message.tool_calls) > 0
    assert last_message.tool_calls[0]['name'] == 'calculator'
```

## Troubleshooting

### Issue: Tests fail with import errors

**Symptoms**: `ModuleNotFoundError` when running tests

**Fix**:
```bash
# Ensure all packages are installed
uv sync --all-packages --dev

# Check PYTHONPATH includes project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Issue: Async tests not running

**Symptoms**: Async tests skipped or fail

**Fix**:
```bash
# Install pytest-asyncio
uv add --dev pytest-asyncio

# Mark async tests
@pytest.mark.asyncio
async def test_async():
    pass
```

### Issue: Graph hangs during test

**Symptoms**: Test times out

**Fix**:
```python
# Set timeout in pytest
@pytest.mark.timeout(10)
def test_graph():
    graph.invoke(input)

# Or check for infinite loops in routing
def should_continue(state):
    # ❌ Bad: Can loop forever
    return "process"

    # ✅ Good: Has exit condition
    if state.iterations >= 10:
        return END
    return "process"
```

### Issue: State not updating in tests

**Symptoms**: Node executes but state unchanged

**Fix**:
```python
# ❌ Bad: Mutation doesn't work
def test_bad():
    node = ProcessNode()
    state = State(count=0)
    node(state)
    assert state.count == 1  # Fails! State unchanged

# ✅ Good: Check return value
def test_good():
    node = ProcessNode()
    state = State(count=0)
    result = node(state)
    assert result["count"] == 1  # Passes!
```

### Issue: Fixtures not working

**Symptoms**: Fixture undefined or reused incorrectly

**Fix**:
```python
# Ensure conftest.py exists
# tests/conftest.py
import pytest

@pytest.fixture
def sample_state():
    return State(query="test")

# Use in test files
def test_with_fixture(sample_state):
    # sample_state available
    pass
```

## Best Practices

### 1. Test One Thing Per Test

```python
# ✅ Good: Focused test
def test_node_returns_result():
    result = node(state)
    assert "result" in result

def test_node_result_correct():
    result = node(state)
    assert result["result"] == "expected"

# ❌ Bad: Tests multiple things
def test_node():
    result = node(state)
    assert "result" in result
    assert result["result"] == "expected"
    assert result["count"] == 1
    # Too many assertions
```

### 2. Use Descriptive Test Names

```python
# ✅ Good: Clear intent
def test_process_node_uppercases_input():
    pass

def test_graph_routes_to_math_solver_for_math_queries():
    pass

# ❌ Bad: Vague names
def test_node():
    pass

def test_graph():
    pass
```

### 3. Test Edge Cases

```python
def test_node_with_empty_input():
    """Test with empty input."""
    result = node(State(query=""))
    assert "error" in result or "result" in result

def test_node_with_none_input():
    """Test with None input."""
    result = node(State(query=None))
    assert "error" in result

def test_node_with_large_input():
    """Test with large input."""
    result = node(State(query="x" * 10000))
    assert "result" in result
```

### 4. Keep Tests Independent

```python
# ✅ Good: Each test is independent
def test_a():
    node = ProcessNode()
    # Test...

def test_b():
    node = ProcessNode()
    # Test...

# ❌ Bad: Tests depend on each other
shared_state = None

def test_a():
    global shared_state
    shared_state = node(State())

def test_b():
    # Depends on test_a running first
    result = node(shared_state)
```

### 5. Use Setup and Teardown

```python
class TestProcessNode:
    def setup_method(self):
        """Run before each test."""
        self.node = ProcessNode()
        self.state = State(query="test")

    def teardown_method(self):
        """Run after each test."""
        # Cleanup if needed
        pass

    def test_execution(self):
        result = self.node(self.state)
        assert "result" in result
```

## Quick Reference

```bash
# Run tests
uv run pytest -q                              # All tests, quiet
uv run pytest -v                              # All tests, verbose
uv run pytest tests/unit_tests/              # Unit tests only
uv run pytest -k "test_node"                 # Tests matching name
uv run pytest --cov                          # With coverage

# Dev server
uv run langgraph dev                         # Start server
# Open: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

# Validate Cast
uv run python scripts/validate_cast.py casts/my_cast
```

## Related Skills

- **node-implementation**: Nodes being tested
- **graph-composition**: Graphs being tested
- **cast-development**: Overall Cast structure
- **act-setup**: Test environment setup

## References

**Official documentation:**
- Pytest: https://docs.pytest.org/
- LangGraph Testing: https://docs.langchain.com/oss/python/langgraph/testing
- LangGraph CLI: https://docs.langchain.com/oss/python/langgraph/cli
