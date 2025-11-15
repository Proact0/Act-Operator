# Async Testing

## When to Use

Testing async nodes and graphs. Use when nodes/graphs use `async def` or `await`.

## Setup

```python
# Install pytest-asyncio
# pip install pytest-asyncio

# Configure in pytest.ini or pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"  # Auto-detect async tests
```

## Basic Async Node Test

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

## Async Fixtures

```python
import pytest_asyncio

@pytest_asyncio.fixture
async def async_client():
    """Async fixture for HTTP client."""
    async with httpx.AsyncClient() as client:
        yield client

@pytest.mark.asyncio
async def test_with_async_fixture(async_client):
    """Test using async fixture."""
    response = await async_client.get("https://api.example.com")
    assert response.status_code == 200
```

## Testing Async Graph

```python
@pytest.mark.asyncio
async def test_async_graph():
    """Test async graph execution."""
    graph = MyAsyncGraph(checkpointer=MemorySaver()).build()
    
    result = await graph.ainvoke({"task": "test"})
    
    assert result["status"] == "completed"
```

## Mocking Async Functions

```python
from unittest.mock import AsyncMock

@pytest.fixture
def mock_async_api():
    """Mock async API call."""
    mock = AsyncMock(return_value={"data": "test"})
    return mock

@pytest.mark.asyncio
async def test_with_mock(mock_async_api):
    """Test with mocked async function."""
    result = await mock_async_api()
    assert result["data"] == "test"
```

## Testing Concurrent Operations

```python
import asyncio

@pytest.mark.asyncio
async def test_concurrent_execution():
    """Test concurrent async operations."""
    node1 = AsyncNode1()
    node2 = AsyncNode2()
    
    state = {"data": "test"}
    
    # Run concurrently
    results = await asyncio.gather(
        node1.execute(state),
        node2.execute(state)
    )
    
    assert len(results) == 2
    assert all(r is not None for r in results)
```

## Testing Timeouts

```python
@pytest.mark.asyncio
async def test_timeout():
    """Test async operation timeout."""
    node = SlowAsyncNode()
    
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(
            node.execute({"data": "test"}),
            timeout=1.0  # 1 second
        )
```

## Async Streaming Tests

```python
@pytest.mark.asyncio
async def test_async_streaming():
    """Test async graph streaming."""
    graph = MyAsyncGraph().build()
    
    chunks = []
    async for chunk in graph.astream({"task": "test"}):
        chunks.append(chunk)
    
    assert len(chunks) > 0
```

## Common Patterns

**Async node with mock:**
```python
@pytest.mark.asyncio
async def test_async_node(mock_async_api):
    node = MyAsyncNode(api=mock_async_api)
    result = await node.execute(state)
    assert result is not None
```

**Async graph:**
```python
@pytest.mark.asyncio
async def test_async_graph():
    graph = MyGraph().build()
    result = await graph.ainvoke(input)
    assert result["status"] == "completed"
```

**Concurrent execution:**
```python
@pytest.mark.asyncio
async def test_concurrent():
    results = await asyncio.gather(*[
        async_func(i) for i in range(10)
    ])
    assert len(results) == 10
```

## Common Mistakes

❌ **Forgetting @pytest.mark.asyncio** - test fails with "coroutine was never awaited"
✓ Always mark async tests

❌ **Using sync fixtures with async tests** - hangs or errors
✓ Use @pytest_asyncio.fixture

❌ **Not awaiting async calls** - returns coroutine, not result
✓ Always use `await`

## References

- Node testing: `node-testing.md`
- Graph testing: `graph-testing.md`
- Mocking: `mocking.md`
