# Fixtures Guide

## What are Fixtures?

Reusable test setup code. Define once, use in multiple tests.

## Basic Fixture

```python
import pytest

@pytest.fixture
def sample_state():
    """Provide test state."""
    return {
        "messages": [],
        "task": "test task",
        "count": 0
    }

def test_with_fixture(sample_state):
    """Use fixture in test."""
    assert sample_state["task"] == "test task"
```

## Fixture Scopes

```python
@pytest.fixture(scope="function")  # Default: new for each test
def function_scoped():
    return {"data": "new each time"}

@pytest.fixture(scope="class")  # Shared within test class
def class_scoped():
    return {"data": "shared in class"}

@pytest.fixture(scope="module")  # Shared within module
def module_scoped():
    return {"data": "shared in module"}

@pytest.fixture(scope="session")  # Shared across all tests
def session_scoped():
    return {"data": "shared everywhere"}
```

## Fixture Composition

```python
@pytest.fixture
def mock_llm():
    """Mock LLM fixture."""
    return MockLLM()

@pytest.fixture
def test_node(mock_llm):
    """Node fixture using another fixture."""
    return MyNode(model=mock_llm)

def test_composed(test_node):
    """Test using composed fixture."""
    result = test_node.execute({"task": "test"})
    assert result is not None
```

## Fixture Teardown

```python
@pytest.fixture
def database():
    """Fixture with setup and teardown."""
    # Setup
    db = Database.connect("test.db")
    yield db
    # Teardown
    db.close()
    os.remove("test.db")
```

## Parametrized Fixtures

```python
@pytest.fixture(params=["option1", "option2", "option3"])
def parametrized_fixture(request):
    """Fixture with multiple values."""
    return request.param

def test_with_params(parametrized_fixture):
    """Runs 3 times with different values."""
    assert parametrized_fixture in ["option1", "option2", "option3"]
```

## conftest.py Organization

```python
# casts/my_agent/tests/conftest.py
"""Cast-specific fixtures."""

import pytest
from casts.my_agent.nodes import ProcessNode
from casts.my_agent.graph import MyAgentGraph

@pytest.fixture
def process_node():
    """Provide ProcessNode for tests."""
    return ProcessNode()

@pytest.fixture
def test_graph():
    """Provide test graph."""
    return MyAgentGraph(checkpointer=MemorySaver()).build()
```

## Importing Project Fixtures

```python
# casts/my_agent/tests/conftest.py
"""Import project-level fixtures."""

pytest_plugins = ["fixtures.conftest"]

# Now tests can use fixtures from fixtures/conftest.py
```

## Common Fixtures

**Mock LLM:**
```python
@pytest.fixture
def mock_llm():
    class Mock:
        def invoke(self, msgs):
            return AIMessage(content="Mock")
        def bind_tools(self, tools):
            return self
    return Mock()
```

**Test Config:**
```python
@pytest.fixture
def test_config():
    return {"configurable": {"thread_id": "test-123"}}
```

**Test Graph:**
```python
@pytest.fixture
def test_graph():
    return MyGraph(checkpointer=MemorySaver()).build()
```

## Quick Reference

**Basic:**
```python
@pytest.fixture
def my_fixture():
    return value
```

**With teardown:**
```python
@pytest.fixture
def my_fixture():
    setup()
    yield value
    teardown()
```

**Composition:**
```python
@pytest.fixture
def composed(other_fixture):
    return build(other_fixture)
```

**Scope:**
```python
@pytest.fixture(scope="module")
def shared():
    return value
```

## References

- Node testing: `node-testing.md`
- Mocking: `mocking.md`
