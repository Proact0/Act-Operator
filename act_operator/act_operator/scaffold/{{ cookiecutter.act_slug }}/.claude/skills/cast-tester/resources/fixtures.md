# Fixtures

## conftest.py Template

```python
# tests/conftest.py
import pytest
from langgraph.checkpoint.memory import MemorySaver

# State Fixtures

@pytest.fixture
def empty_state():
    return {"input": "", "messages": [], "result": None}

@pytest.fixture
def populated_state():
    return {
        "input": "test query",
        "messages": [{"role": "user", "content": "hello"}],
        "context": {},
    }

@pytest.fixture
def mock_config():
    return {"configurable": {"thread_id": "test-123"}}

# Mock Fixtures

@pytest.fixture
def mock_llm():
    class MockLLM:
        def __init__(self, response="mocked"):
            self.response = response
            self.calls = []
        
        def invoke(self, messages):
            self.calls.append(messages)
            return {"content": self.response}
        
        def bind_tools(self, tools):
            return self
    
    return MockLLM()

@pytest.fixture
def mock_store():
    class MockStore:
        def __init__(self):
            self.data = {}
        
        def get(self, namespace, key):
            return self.data.get((tuple(namespace), key))
        
        def put(self, namespace, key, value):
            self.data[(tuple(namespace), key)] = value
    
    return MockStore()

@pytest.fixture
def mock_runtime(mock_store):
    class MockRuntime:
        def __init__(self, store):
            self.store = store
    
    return MockRuntime(mock_store)

@pytest.fixture
def memory_saver():
    return MemorySaver()

# Factory Fixtures

@pytest.fixture
def make_state():
    def _make(**kwargs):
        default = {"input": "", "messages": [], "result": None}
        default.update(kwargs)
        return default
    return _make

@pytest.fixture
def make_config():
    def _make(thread_id="test-123", **kwargs):
        config = {"configurable": {"thread_id": thread_id}}
        config["configurable"].update(kwargs)
        return config
    return _make
```

## Usage Examples

### State Fixtures
```python
def test_with_empty_state(empty_state):
    node = MyNode()
    result = node.execute(empty_state)
    assert result is not None

def test_with_populated_state(populated_state):
    node = MyNode()
    result = node.execute(populated_state)
    assert "processed" in result
```

### Mock Fixtures
```python
def test_with_mock_llm(mock_llm):
    node = LLMNode()
    node.llm = mock_llm
    
    node.execute({"messages": []})
    
    assert len(mock_llm.calls) == 1

def test_with_runtime(mock_runtime):
    node = MemoryNode()
    result = node.execute({"user_id": "123"}, runtime=mock_runtime)
    assert result is not None
```

### Factory Fixtures
```python
def test_with_custom_state(make_state):
    state = make_state(input="custom", extra="data")
    node = MyNode()
    result = node.execute(state)
    assert result is not None

def test_with_custom_config(make_config):
    config = make_config(thread_id="custom-123", user_id="alice")
    # Use config...
```

## Fixture Scopes

```python
@pytest.fixture(scope="session")
def expensive_resource():
    """Setup once per test session."""
    resource = setup_expensive()
    yield resource
    teardown(resource)

@pytest.fixture(scope="module")
def module_resource():
    """Setup once per module."""
    return create_resource()

@pytest.fixture  # scope="function" is default
def test_resource():
    """Setup for each test."""
    return create_resource()
```

