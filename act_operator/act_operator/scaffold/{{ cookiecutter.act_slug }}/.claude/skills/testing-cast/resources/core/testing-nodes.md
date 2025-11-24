# Testing Nodes

## When to Use This Resource
Read this when writing unit tests for node classes that inherit from `BaseNode` or `AsyncBaseNode`.

## Basic Node Test Pattern

### Testing Synchronous Nodes

```python
# tests/test_nodes.py
import pytest
from casts.{ cast_name }.nodes import ProcessInputNode
from casts.{ cast_name }.state import MyCastState

class TestProcessInputNode:
    """Test suite for ProcessInputNode."""

    def test_execute_with_valid_input(self):
        # Arrange
        node = ProcessInputNode()
        state = {"input": "test query", "messages": []}

        # Act
        result = node.execute(state)

        # Assert
        assert "processed" in result
        assert result["processed"] is True

    def test_execute_with_missing_input(self):
        node = ProcessInputNode()
        state = {"messages": []}

        result = node.execute(state)

        assert "error" in result

    @pytest.mark.parametrize("input_text,expected", [
        ("hello", {"processed": True}),
        ("", {"error": "empty input"}),
        ("test", {"processed": True}),
    ])
    def test_execute_parametrized(self, input_text, expected):
        node = ProcessInputNode()
        state = {"input": input_text}

        result = node.execute(state)

        for key, value in expected.items():
            assert result[key] == value
```

### Testing Async Nodes

```python
import pytest
from casts.{ cast_name }.nodes import FetchDataNode

class TestFetchDataNode:
    """Test suite for async FetchDataNode."""

    @pytest.mark.asyncio
    async def test_execute_success(self):
        node = FetchDataNode()
        state = {"user_id": "123"}

        result = await node.execute(state)

        assert "user_data" in result
        assert result["user_data"] is not None

    @pytest.mark.asyncio
    async def test_execute_with_error(self, monkeypatch):
        async def mock_api_call(*args):
            raise ValueError("API error")

        node = FetchDataNode()
        monkeypatch.setattr("casts.{ cast_name }.nodes.async_api_call", mock_api_call)
        state = {"user_id": "123"}

        result = await node.execute(state)

        assert "error" in result
```

## Testing Nodes with Config/Runtime

```python
class TestNodeWithRuntime:
    def test_execute_with_config(self):
        node = MyNode()
        state = {"input": "test"}
        config = {"configurable": {"thread_id": "test-123"}}

        result = node.execute(state, config=config)

        assert result["thread_id"] == "test-123"

    def test_execute_with_store(self, mock_store):
        node = MemoryNode()
        state = {"user_id": "alice"}

        # Create mock runtime with store
        class MockRuntime:
            def __init__(self, store):
                self.store = store

        runtime = MockRuntime(mock_store)
        result = node.execute(state, runtime=runtime)

        assert "preferences" in result
```

## Testing Node Initialization

```python
class TestNodeInit:
    def test_default_initialization(self):
        node = MyNode()

        assert node.name == "MyNode"
        assert node.verbose is False

    def test_custom_initialization(self):
        node = MyNode(model_name="gpt-4", verbose=True)

        assert node.model_name == "gpt-4"
        assert node.verbose is True

    def test_initialization_calls_super(self):
        """Ensure __init__ calls super().__init__(**kwargs)."""
        node = MyNode(verbose=True)

        # BaseNode features should work
        assert hasattr(node, "log")
        assert hasattr(node, "get_thread_id")
```

## Mocking Dependencies

```python
class TestNodeWithMocks:
    def test_with_mocked_llm(self, monkeypatch):
        # Mock LLM response
        class MockLLM:
            def invoke(self, messages):
                return {"content": "mocked response"}

        node = MyNode()
        monkeypatch.setattr(node, "llm", MockLLM())
        state = {"messages": [{"role": "user", "content": "hi"}]}

        result = node.execute(state)

        assert result["response"]["content"] == "mocked response"

    def test_with_mocked_tool(self, monkeypatch):
        def mock_tool_call(*args, **kwargs):
            return {"result": "mocked"}

        monkeypatch.setattr("modules.tools.my_tool.tool_function", mock_tool_call)

        node = ToolCallingNode()
        state = {"tool_args": {"query": "test"}}

        result = node.execute(state)

        assert result["result"] == "mocked"
```

## Testing Error Handling

```python
class TestNodeErrorHandling:
    def test_handles_exception_gracefully(self):
        node = RobustNode()
        state = {"input": "trigger_error"}

        result = node.execute(state)

        assert "error" in result
        assert result["error"] is not None

    def test_logs_error_in_verbose_mode(self, caplog):
        node = MyNode(verbose=True)
        state = {"input": "invalid"}

        node.execute(state)

        assert "error" in caplog.text.lower()
```

## Fixtures for Node Testing

```python
# conftest.py
import pytest

@pytest.fixture
def sample_state():
    """Provides a standard test state."""
    return {
        "input": "test input",
        "messages": [],
        "result": None
    }

@pytest.fixture
def mock_store():
    """Provides a mock Store for testing."""
    class MockStore:
        def __init__(self):
            self.data = {}

        def get(self, namespace, key):
            return self.data.get((namespace, key))

        def put(self, namespace, key, value):
            self.data[(namespace, key)] = value

    return MockStore()

@pytest.fixture
def mock_config():
    """Provides a standard test config."""
    return {"configurable": {"thread_id": "test-123"}}
```

## Common Patterns

### Pattern: Testing State Updates
```python
def test_returns_correct_state_updates():
    """Node should return only updated fields."""
    node = MyNode()
    state = {"input": "test", "existing": "data"}

    result = node.execute(state)

    # Should not include unchanged fields
    assert "existing" not in result
    # Should only have updates
    assert "processed" in result
```

### Pattern: Testing Verbose Logging
```python
def test_verbose_logging(capsys):
    node = MyNode(verbose=True)
    state = {"input": "test"}

    node.execute(state)

    captured = capsys.readouterr()
    assert "Executing" in captured.out or captured.err
```

## Anti-Patterns

❌ **Testing implementation details**
```python
# Bad - tests internal methods
def test_internal_method():
    node = MyNode()
    result = node._internal_helper("data")  # Don't test private methods
```

❌ **Not isolating tests**
```python
# Bad - depends on external state
node = MyNode()  # Created at module level

def test_something():
    result = node.execute(state)  # Shares instance
```

✅ **Good - isolated tests**
```python
def test_something():
    node = MyNode()  # Fresh instance per test
    result = node.execute(state)
```

## References
- Related: `testing-graphs.md` (integration with graphs)
- Related: `async-testing.md` (advanced async patterns)
- Related: `mocking-strategies.md` (comprehensive mocking)
- Related: `fixtures-guide.md` (reusable fixtures)
