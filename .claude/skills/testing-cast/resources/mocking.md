# Mocking Strategies

## When to Use

Mock external dependencies to make tests fast, deterministic, and independent.

## Mock LLM

### Simple Mock

```python
from langchain_core.messages import AIMessage

class MockLLM:
    """Simple mock LLM."""
    def invoke(self, messages):
        return AIMessage(content="Mock response")
    
    def bind_tools(self, tools):
        return self

@pytest.fixture
def mock_llm():
    return MockLLM()
```

### Mock with Tool Calls

```python
class MockLLMWithTools:
    """Mock LLM that returns tool calls."""
    def invoke(self, messages):
        return AIMessage(
            content="",
            tool_calls=[{
                "name": "calculator",
                "args": {"operation": "add", "a": 5, "b": 3},
                "id": "call_123"
            }]
        )
    
    def bind_tools(self, tools):
        return self
```

### GenericFakeChatModel (LangChain)

```python
from langchain_core.language_models import GenericFakeChatModel

@pytest.fixture
def fake_llm():
    """LangChain's fake LLM."""
    return GenericFakeChatModel(messages=iter([
        AIMessage(content="First response"),
        AIMessage(content="Second response"),
    ]))
```

## Mock Store (Long-term Memory)

```python
class MockStore:
    """Mock Store for memory testing."""
    def __init__(self):
        self._data = {}
    
    def get(self, namespace, key):
        return self._data.get((tuple(namespace), key))
    
    def put(self, namespace, key, value):
        self._data[(tuple(namespace), key)] = value
    
    def search(self, namespace, query=None):
        # Simple search implementation
        items = [
            v for (ns, k), v in self._data.items()
            if tuple(ns) == tuple(namespace)
        ]
        return items
    
    def list(self, namespace):
        return [
            v for (ns, k), v in self._data.items()
            if tuple(ns) == tuple(namespace)
        ]
    
    def delete(self, namespace, key):
        self._data.pop((tuple(namespace), key), None)

@pytest.fixture
def mock_store():
    return MockStore()
```

## Mock Runtime

```python
class MockRuntime:
    """Mock Runtime for testing."""
    def __init__(self, store=None):
        self.store = store or MockStore()
        self.stream_writer = None

@pytest.fixture
def mock_runtime(mock_store):
    return MockRuntime(store=mock_store)
```

## Mock External APIs

### Using unittest.mock

```python
from unittest.mock import patch, MagicMock

def test_with_mocked_api(monkeypatch):
    """Test with mocked API using monkeypatch."""
    def mock_api_call(*args, **kwargs):
        return {"status": "success", "data": "test"}
    
    monkeypatch.setattr("module.api.call", mock_api_call)
    
    result = module.api.call("endpoint")
    assert result["status"] == "success"
```

### Using requests-mock

```python
import requests_mock

def test_with_requests_mock():
    """Test with requests mocked."""
    with requests_mock.Mocker() as m:
        m.get("https://api.example.com/data", json={"data": "test"})
        
        response = requests.get("https://api.example.com/data")
        assert response.json()["data"] == "test"
```

### Async API Mocking

```python
import pytest
from aioresponses import aioresponses

@pytest.mark.asyncio
async def test_async_api():
    """Test async API with aioresponses."""
    with aioresponses() as mocked:
        mocked.get(
            "https://api.example.com/data",
            payload={"data": "test"}
        )
        
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.example.com/data")
            assert response.json()["data"] == "test"
```

## Mock Database

```python
class MockDatabase:
    """Mock database for testing."""
    def __init__(self):
        self._records = []
    
    def insert(self, record):
        self._records.append(record)
    
    def query(self, filter_func=None):
        if filter_func:
            return [r for r in self._records if filter_func(r)]
        return self._records.copy()
    
    def delete(self, filter_func):
        self._records = [r for r in self._records if not filter_func(r)]

@pytest.fixture
def mock_db():
    return MockDatabase()
```

## Mock File Operations

```python
from unittest.mock import mock_open, patch

def test_file_read():
    """Test file reading with mock."""
    mock_file_content = "test content"
    
    with patch("builtins.open", mock_open(read_data=mock_file_content)):
        with open("test.txt") as f:
            content = f.read()
        
        assert content == "test content"
```

## Mock Environment Variables

```python
def test_with_env_vars(monkeypatch):
    """Test with environment variables."""
    monkeypatch.setenv("API_KEY", "test-key-123")
    
    import os
    assert os.getenv("API_KEY") == "test-key-123"
```

## Recording Real Responses (VCR)

```python
import pytest
import vcr

@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": ["authorization"],
        "record_mode": "once",  # "once", "new_episodes", "none", "all"
    }

@vcr.use_cassette("tests/fixtures/cassettes/api_call.yaml")
def test_with_vcr():
    """Test with VCR cassette (records real API)."""
    response = requests.get("https://api.example.com/data")
    assert response.status_code == 200
```

## pytest-recording

```python
@pytest.mark.vcr
def test_with_pytest_recording():
    """Test with pytest-recording (simpler VCR)."""
    response = requests.get("https://api.example.com/data")
    assert response.status_code == 200
```

## Choosing Mocking Strategy

**Fast unit tests?**
→ Mock everything external (LLM, API, DB, files)

**Integration tests?**
→ Use real dependencies (with test instances)

**Slow external API?**
→ Use VCR/pytest-recording to record once

**Non-deterministic LLM?**
→ Always mock LLM (set temperature=0 if must use real)

**Database tests?**
→ Use test database or in-memory alternative

## Common Mistakes

❌ **Mocking too much** - tests don't reflect reality
✓ Balance mocks with integration tests

❌ **Brittle mocks** - return hardcoded values that break easily
✓ Make mocks realistic and flexible

❌ **No mock cleanup** - mocks persist between tests
✓ Use fixtures with proper teardown

❌ **Mocking what you own** - testing mock, not code
✓ Mock external dependencies, test your code

## Quick Reference

**Mock LLM:**
```python
def test_node(mock_llm):
    node = MyNode(mock_llm)
    ...
```

**Mock Store:**
```python
def test_memory(mock_runtime):
    node.execute(state, runtime=mock_runtime)
    ...
```

**Mock API:**
```python
def test_api(monkeypatch):
    monkeypatch.setattr("module.api", mock_api)
    ...
```

**Mock file:**
```python
with patch("builtins.open", mock_open(read_data="...")):
    ...
```

## References

- Node testing: `node-testing.md`
- Graph testing: `graph-testing.md`
- Fixtures: `fixtures-guide.md`
