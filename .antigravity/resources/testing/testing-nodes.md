# Testing Nodes

## Sync Node Test

```python
# tests/test_nodes.py
import pytest
from casts.{cast_name}.nodes import ProcessNode

class TestProcessNode:
    def test_execute_basic(self):
        node = ProcessNode()
        state = {"input": "test"}
        
        result = node.execute(state)
        
        assert "output" in result

    def test_execute_with_missing_input(self):
        node = ProcessNode()
        state = {}
        
        result = node.execute(state)
        
        assert "error" in result

    @pytest.mark.parametrize("input_val,expected", [
        ("hello", {"processed": True}),
        ("", {"error": "empty"}),
    ])
    def test_parametrized(self, input_val, expected):
        node = ProcessNode()
        result = node.execute({"input": input_val})
        
        for key, value in expected.items():
            assert result[key] == value
```

## Async Node Test

```python
import pytest

class TestAsyncNode:
    @pytest.mark.asyncio
    async def test_execute(self):
        node = AsyncFetchNode()
        state = {"query": "test"}
        
        result = await node.execute(state)
        
        assert "data" in result

    @pytest.mark.asyncio
    async def test_concurrent(self):
        import asyncio
        node = AsyncNode()
        
        results = await asyncio.gather(
            node.execute({"id": 1}),
            node.execute({"id": 2}),
        )
        
        assert len(results) == 2
```

## Testing with Config/Runtime

```python
def test_with_config(self):
    node = MyNode()
    state = {"input": "test"}
    config = {"configurable": {"thread_id": "test-123"}}
    
    result = node.execute(state, config=config)
    
    assert result["thread_id"] == "test-123"

def test_with_store(self, mock_store):
    class MockRuntime:
        def __init__(self, store):
            self.store = store
    
    node = MemoryNode()
    runtime = MockRuntime(mock_store)
    result = node.execute({"user_id": "alice"}, runtime=runtime)
    
    assert "preferences" in result
```

## Testing Error Handling

```python
def test_handles_exception(self):
    node = RobustNode()
    state = {"input": "trigger_error"}
    
    result = node.execute(state)
    
    assert "error" in result

def test_logs_error(self, caplog):
    node = MyNode(verbose=True)
    node.execute({"input": "invalid"})
    
    assert "error" in caplog.text.lower()
```

## Patterns

**State Updates:**
```python
def test_returns_only_updates():
    node = MyNode()
    result = node.execute({"input": "test", "existing": "data"})
    
    assert "existing" not in result  # Only updates returned
    assert "processed" in result
```

**Verbose Logging:**
```python
def test_verbose_output(capsys):
    node = MyNode(verbose=True)
    node.execute({"input": "test"})
    
    captured = capsys.readouterr()
    assert "Executing" in captured.out
```

