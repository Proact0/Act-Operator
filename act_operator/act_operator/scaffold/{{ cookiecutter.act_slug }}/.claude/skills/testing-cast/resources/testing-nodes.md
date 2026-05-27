# Testing Nodes

All test code in this file lives at `tests/node_tests/test_{cast_snake}_nodes.py` (the scaffolded initial cast uses `tests/node_tests/test_node.py`; create a new file per cast as your project grows).

## Sync Node Test

```python
# tests/node_tests/test_{cast_snake}_nodes.py
import pytest
from casts.{cast_name}.modules.nodes import ProcessNode


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
# tests/node_tests/test_{cast_snake}_nodes.py
import asyncio

import pytest

from casts.{cast_name}.modules.nodes import AsyncFetchNode, AsyncNode


class TestAsyncNode:
    @pytest.mark.asyncio
    async def test_execute(self):
        node = AsyncFetchNode()
        state = {"query": "test"}

        result = await node.execute(state)

        assert "data" in result

    @pytest.mark.asyncio
    async def test_concurrent(self):
        node = AsyncNode()

        results = await asyncio.gather(
            node.execute({"id": 1}),
            node.execute({"id": 2}),
        )

        assert len(results) == 2
```

## Testing with Config/Runtime

```python
# tests/node_tests/test_{cast_snake}_nodes.py
from casts.{cast_name}.modules.nodes import MyNode, MemoryNode


def test_with_config():
    node = MyNode()
    state = {"input": "test"}
    config = {"configurable": {"thread_id": "test-123"}}

    result = node.execute(state, config=config)

    assert result["thread_id"] == "test-123"


def test_with_store(mock_store):
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
# tests/node_tests/test_{cast_snake}_nodes.py
from casts.{cast_name}.modules.nodes import RobustNode, MyNode


def test_handles_exception():
    node = RobustNode()
    state = {"input": "trigger_error"}

    result = node.execute(state)

    assert "error" in result


def test_logs_error(caplog):
    node = MyNode(verbose=True)
    node.execute({"input": "invalid"})

    assert "error" in caplog.text.lower()
```

## Patterns

**State Updates:**

```python
# tests/node_tests/test_{cast_snake}_nodes.py
from casts.{cast_name}.modules.nodes import MyNode


def test_returns_only_updates():
    node = MyNode()
    result = node.execute({"input": "test", "existing": "data"})

    assert "existing" not in result  # Only updates returned
    assert "processed" in result
```

**Verbose Logging:**

```python
# tests/node_tests/test_{cast_snake}_nodes.py
from casts.{cast_name}.modules.nodes import MyNode


def test_verbose_output(capsys):
    node = MyNode(verbose=True)
    node.execute({"input": "test"})

    captured = capsys.readouterr()
    assert "Executing" in captured.out
```

## Testing Drain-Aware Nodes (langgraph v1.2+)

`runtime.drain_requested` lets nodes skip expensive work when a graceful shutdown is requested.

```python
# tests/node_tests/test_{cast_snake}_nodes.py
from types import SimpleNamespace

import pytest

from casts.{cast_name}.modules.nodes import ExpensiveNode


@pytest.mark.asyncio
async def test_skips_when_drain_requested():
    runtime = SimpleNamespace(drain_requested=True, drain_reason="SIGTERM")
    node = ExpensiveNode()

    result = await node.execute({"input": "test"}, runtime=runtime)

    assert result["status"].startswith("skipped:")
    assert "SIGTERM" in result["status"]


@pytest.mark.asyncio
async def test_runs_when_no_drain():
    runtime = SimpleNamespace(drain_requested=False, drain_reason=None)
    node = ExpensiveNode()

    result = await node.execute({"input": "test"}, runtime=runtime)

    assert "result" in result
```
