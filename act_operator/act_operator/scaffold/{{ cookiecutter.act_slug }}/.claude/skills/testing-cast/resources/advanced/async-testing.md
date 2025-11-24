# Async Testing

## When to Use This Resource
Read this when testing async nodes, async graph execution, or concurrent operations.

## Basic Async Test

```python
import pytest

class TestAsyncNode:
    @pytest.mark.asyncio
    async def test_async_node(self):
        from casts.{ cast_name }.nodes import AsyncFetchNode

        node = AsyncFetchNode()
        state = {"query": "test"}

        result = await node.execute(state)

        assert "data" in result
```

## Testing Concurrent Operations

```python
import asyncio

class TestConcurrent:
    @pytest.mark.asyncio
    async def test_multiple_async_calls(self):
        node = AsyncNode()

        # Execute multiple calls concurrently
        results = await asyncio.gather(
            node.execute({"id": 1}),
            node.execute({"id": 2}),
            node.execute({"id": 3})
        )

        assert len(results) == 3
        assert all("result" in r for r in results)
```

## Async Fixtures

```python
@pytest.fixture
async def async_resource():
    """Async fixture setup/teardown."""
    resource = await setup_resource()
    yield resource
    await teardown_resource(resource)

class TestWithAsyncFixture:
    @pytest.mark.asyncio
    async def test_uses_async_fixture(self, async_resource):
        result = await async_resource.query("test")
        assert result is not None
```

## Mocking Async Functions

```python
class TestAsyncMocking:
    @pytest.mark.asyncio
    async def test_mock_async_call(self, monkeypatch):
        async def mock_api(*args):
            return {"mocked": True}

        monkeypatch.setattr("module.async_api_call", mock_api)

        node = MyAsyncNode()
        result = await node.execute({"query": "test"})

        assert result["mocked"] is True
```

## Testing Timeouts

```python
class TestTimeouts:
    @pytest.mark.asyncio
    async def test_operation_completes_in_time(self):
        node = AsyncNode()

        # Should complete within 5 seconds
        result = await asyncio.wait_for(
            node.execute({"query": "test"}),
            timeout=5.0
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_handles_timeout(self):
        node = SlowAsyncNode()

        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                node.execute({"query": "test"}),
                timeout=0.1
            )
```

## Testing Error Handling in Async

```python
class TestAsyncErrors:
    @pytest.mark.asyncio
    async def test_async_error_handled(self):
        async def failing_op():
            raise ValueError("Async error")

        node = RobustAsyncNode()
        monkeypatch.setattr(node, "_async_op", failing_op)

        result = await node.execute({"input": "test"})

        assert "error" in result
```

## pytest-asyncio Configuration

```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"  # Auto-detect async tests
```

## References
- Related: `testing-nodes.md` (sync node patterns)
- Related: `mocking-strategies.md` (mocking async operations)
