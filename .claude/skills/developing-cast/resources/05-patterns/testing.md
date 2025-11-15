# Testing LangGraph Casts

## When to Use This Resource

Read this for writing unit tests, integration tests, or mocking LLMs in tests.

## Test Structure

```
casts/
  my_agent/
    tests/
      __init__.py
      conftest.py
      test_nodes.py
      test_graph.py
      test_integration.py
```

## Unit Testing Nodes

```python
# tests/test_nodes.py
import pytest
from casts.my_agent.nodes import ProcessNode
from casts.my_agent.state import MyAgentState

def test_process_node():
    """Test ProcessNode executes correctly."""
    node = ProcessNode()

    state: MyAgentState = {
        "messages": [],
        "current_task": "test task",
    }

    result = node.execute(state)

    assert "results" in result
    assert result["results"] is not None
```

## Mocking LLMs

```python
# tests/conftest.py
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


# tests/test_nodes.py
def test_agent_node_with_mock(mock_llm):
    from casts.my_agent.nodes import AgentNode

    node = AgentNode(mock_llm)
    state = {"messages": []}

    result = node.execute(state)

    assert len(result["messages"]) == 1
    assert result["messages"][0].content == "Mock response"
```

## Testing Graphs

```python
# tests/test_graph.py
from casts.my_agent.graph import MyAgentGraph
from langgraph.checkpoint.memory import MemorySaver

def test_graph_execution():
    """Test full graph execution."""
    graph = MyAgentGraph(checkpointer=MemorySaver()).build()

    result = graph.invoke({
        "messages": [],
        "current_task": "test",
    })

    assert "results" in result
    assert "messages" in result
```

## Testing with Fixtures

```python
# tests/conftest.py
import pytest
from casts.my_agent.graph import MyAgentGraph
from langgraph.checkpoint.memory import MemorySaver

@pytest.fixture
def graph():
    """Provide test graph."""
    return MyAgentGraph(checkpointer=MemorySaver()).build()

@pytest.fixture
def config():
    """Provide test config with thread_id."""
    return {"configurable": {"thread_id": "test-123"}}


# tests/test_graph.py
def test_with_fixtures(graph, config):
    result = graph.invoke({"task": "test"}, config)
    assert result is not None
```

## Integration Tests

```python
# tests/test_integration.py
import pytest
from casts.my_agent.graph import MyAgentGraph
from langchain_anthropic import ChatAnthropic

@pytest.mark.integration
def test_with_real_llm():
    """Integration test with real LLM."""
    model = ChatAnthropic(model="claude-sonnet-4", temperature=0)
    # ... test with real model

# Run: pytest -m integration
```

## Testing Tools

```python
# tests/test_tools.py
from modules.tools.calculator import calculator

def test_calculator_tool():
    """Test calculator tool."""
    result = calculator.invoke({
        "operation": "add",
        "a": 5,
        "b": 3
    })

    assert result == 8
```

## Async Testing

```python
import pytest
from casts.my_agent.nodes import AsyncFetchNode

@pytest.mark.asyncio
async def test_async_node():
    """Test async node."""
    node = AsyncFetchNode()

    state = {"query": "test"}
    result = await node.execute(state)

    assert "data" in result
```

## Common Patterns

### Test State Transitions

```python
def test_state_updates(graph, config):
    # First invocation
    result1 = graph.invoke({"messages": [], "step": 1}, config)

    # Verify state updated
    state = graph.get_state(config)
    assert state.values["step"] == 1

    # Second invocation
    result2 = graph.invoke({"step": 2}, config)

    state = graph.get_state(config)
    assert state.values["step"] == 3  # Accumulated
```

### Test Conditional Routing

```python
def test_routing():
    from casts.my_agent.conditions import should_continue

    # Test "continue" path
    state = {"messages": [AIMessage(content="", tool_calls=[...])]}
    assert should_continue(state) == "continue"

    # Test "end" path
    state = {"messages": [AIMessage(content="Done")]}
    assert should_continue(state) == "end"
```

## pytest Configuration

```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
markers = [
    "unit: Unit tests (fast)",
    "integration: Integration tests (slow, require API keys)",
]
asyncio_mode = "auto"
```

**Run tests:**
```bash
# All tests
pytest

# Unit tests only
pytest -m unit

# Integration tests
pytest -m integration

# Specific file
pytest tests/test_nodes.py

# Verbose
pytest -v
```

## Decision Framework

```
Testing individual nodes?
  → Unit tests with mock LLM

Testing full graph?
  → Integration tests with MemorySaver

Testing tool functions?
  → Direct tool invocation tests

Testing routing logic?
  → Test condition functions directly

Need real LLM responses?
  → Integration tests, mark with @pytest.mark.integration
```

## Common Mistakes

### ❌ Not Using MemorySaver in Tests

```python
# BAD: No checkpointer
graph = MyGraph().build()
```

**Fix:**
```python
# GOOD: Use MemorySaver
from langgraph.checkpoint.memory import MemorySaver
graph = MyGraph(checkpointer=MemorySaver()).build()
```

### ❌ Not Setting temperature=0

```python
# BAD: Random outputs
model = ChatAnthropic(model="claude-sonnet-4")
```

**Fix:**
```python
# GOOD: Deterministic for testing
model = ChatAnthropic(model="claude-sonnet-4", temperature=0)
```

## Act Project Conventions

⚠️ **Test organization:**
- Tests in: `casts/[cast_name]/tests/`
- conftest.py for shared fixtures
- Separate unit and integration tests

⚠️ **Fixtures:**
- Provide mock LLM
- Provide test graph with MemorySaver
- Provide test config with thread_id

## References

- Nodes: `01-core/nodes.md`
- Graphs: `01-core/graph.md`
- Tools: `02-tools/creating-tools.md`
