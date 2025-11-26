# Fixtures Guide

## When to Use This Resource
Read this for reusable pytest fixtures patterns and best practices.

## Common Fixtures

### State Fixtures

```python
# conftest.py
import pytest

@pytest.fixture
def empty_state():
    return {"input": "", "messages": [], "result": None}

@pytest.fixture
def populated_state():
    return {
        "input": "test query",
        "messages": [{"role": "user", "content": "hi"}],
        "context": {"user_id": "123"}
    }
```

### Node Fixtures

```python
@pytest.fixture
def my_node():
    """Fresh node instance."""
    from casts.{ cast_name }.nodes import MyNode
    return MyNode()

@pytest.fixture
def configured_node():
    """Pre-configured node."""
    from casts.{ cast_name }.nodes import ConfiguredNode
    return ConfiguredNode(model="gpt-4", verbose=True)
```

### Graph Fixtures

```python
@pytest.fixture
def graph():
    """Compiled graph."""
    from casts.{ cast_name }.graph import { CastName }Graph
    return { CastName }Graph().build()

@pytest.fixture
def graph_with_memory():
    """Graph with checkpointer."""
    from langgraph.checkpoint.memory import MemorySaver
    from casts.{ cast_name }.graph import { CastName }Graph

    checkpointer = MemorySaver()
    return { CastName }Graph().build(checkpointer=checkpointer)
```

### Mock Fixtures

```python
@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    class MockLLM:
        def invoke(self, messages):
            return {"content": "mocked response"}
    return MockLLM()

@pytest.fixture
def mock_store():
    """Mock Store for testing."""
    class MockStore:
        def __init__(self):
            self.data = {}
        def get(self, namespace, key):
            return self.data.get((tuple(namespace), key))
        def put(self, namespace, key, value):
            self.data[(tuple(namespace), key)] = value
    return MockStore()

@pytest.fixture
def mock_config():
    """Standard test config."""
    return {"configurable": {"thread_id": "test-123"}}
```

## Parametrized Fixtures

```python
@pytest.fixture(params=["gpt-3.5-turbo", "gpt-4", "claude-3"])
def llm_model(request):
    """Test with multiple LLM models."""
    return request.param

def test_works_with_all_models(llm_model):
    node = LLMNode(model=llm_model)
    result = node.execute({"input": "test"})
    assert "result" in result
```

## Fixture Scopes

```python
@pytest.fixture(scope="session")
def expensive_resource():
    """Setup once per test session."""
    resource = setup_expensive_resource()
    yield resource
    teardown_expensive_resource(resource)

@pytest.fixture(scope="module")
def module_resource():
    """Setup once per test module."""
    return create_resource()

@pytest.fixture(scope="function")  # Default
def test_resource():
    """Setup for each test function."""
    return create_resource()
```

## Fixture Factories

```python
@pytest.fixture
def make_node():
    """Factory fixture for creating nodes."""
    def _make_node(**kwargs):
        from casts.{ cast_name }.nodes import MyNode
        return MyNode(**kwargs)
    return _make_node

def test_with_custom_node(make_node):
    node1 = make_node(verbose=True)
    node2 = make_node(model="gpt-4")

    assert node1.verbose is True
    assert node2.model == "gpt-4"
```

## Async Fixtures

```python
@pytest.fixture
async def async_client():
    """Async fixture with setup/teardown."""
    import httpx
    async with httpx.AsyncClient() as client:
        yield client
```

## Fixture Composition

```python
@pytest.fixture
def runtime_with_store(mock_store):
    """Compose fixtures."""
    class MockRuntime:
        def __init__(self, store):
            self.store = store
    return MockRuntime(mock_store)

def test_with_composed_fixture(runtime_with_store):
    # Uses both runtime and store
    assert runtime_with_store.store is not None
```

## Conditional Fixtures

```python
@pytest.fixture
def conditional_resource(request):
    """Fixture that adapts based on test marker."""
    if "slow" in request.keywords:
        return RealResource()
    return MockResource()
```

## References
- Related: `testing-nodes.md` (using fixtures in tests)
- Related: `mocking-strategies.md` (mock fixtures)
