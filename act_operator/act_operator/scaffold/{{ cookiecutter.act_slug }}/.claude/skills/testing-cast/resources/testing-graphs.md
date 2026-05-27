# Testing Graphs

All test code in this file lives in `casts/{cast_name}/tests/test_graph.py`.

## Basic Graph Test

```python
# casts/{cast_name}/tests/test_graph.py
import pytest
from langgraph.checkpoint.memory import MemorySaver

from casts.{cast_name}.graph import MyGraph


class TestMyGraph:
    @pytest.fixture
    def graph(self):
        return MyGraph().build()

    @pytest.fixture
    def graph_with_memory(self):
        checkpointer = MemorySaver()
        return MyGraph(checkpointer=checkpointer).build()

    def test_compiles(self, graph):
        assert graph is not None
        assert hasattr(graph, "invoke")

    def test_invoke_basic(self, graph):
        result = graph.invoke({"input": "test"})

        assert result is not None
        assert isinstance(result, dict)

    def test_with_config(self, graph_with_memory):
        config = {"configurable": {"thread_id": "test-123"}}
        result = graph_with_memory.invoke({"input": "test"}, config=config)

        assert result is not None
```

## Testing Routing

```python
# casts/{cast_name}/tests/test_graph.py
import pytest


class TestGraphRouting:
    def test_conditional_true(self, graph):
        result = graph.invoke({"input": "test", "condition": True})
        assert result["path"] == "path_a"

    def test_conditional_false(self, graph):
        result = graph.invoke({"input": "test", "condition": False})
        assert result["path"] == "path_b"

    @pytest.mark.parametrize("condition,expected", [
        (True, "path_a"),
        (False, "path_b"),
        (None, "default"),
    ])
    def test_routing_parametrized(self, graph, condition, expected):
        result = graph.invoke({"condition": condition})
        assert result["path"] == expected
```

## Testing with Checkpointer

```python
# casts/{cast_name}/tests/test_graph.py
def test_multi_turn(graph_with_memory):
    config = {"configurable": {"thread_id": "test-123"}}

    # First turn
    result1 = graph_with_memory.invoke({"input": "Hello"}, config=config)

    # Second turn - should remember
    result2 = graph_with_memory.invoke({"input": "What did I say?"}, config=config)

    assert len(result2["messages"]) > 1


def test_threads_isolated(graph_with_memory):
    config1 = {"configurable": {"thread_id": "user-1"}}
    config2 = {"configurable": {"thread_id": "user-2"}}

    graph_with_memory.invoke({"input": "User 1"}, config=config1)
    result = graph_with_memory.invoke({"input": "test"}, config=config2)

    assert "User 1" not in str(result)
```

## Testing Event Streaming (v3)

Tests consume the same typed-projection API used in production. See the `streaming-cast` skill for projection details.

```python
# casts/{cast_name}/tests/test_graph.py
import pytest


def test_stream_values(graph):
    stream = graph.stream_events({"input": "test"}, version="v3")
    snapshots = list(stream.values)

    assert len(snapshots) > 0
    for snapshot in snapshots:
        assert "input" in snapshot


def test_stream_messages_tokens(graph):
    stream = graph.stream_events(
        {"messages": [{"role": "user", "content": "hi"}]},
        version="v3",
    )

    collected_text = ""
    for message in stream.messages:
        for token in message.text:
            collected_text += token

    assert collected_text


def test_stream_tool_calls(graph):
    stream = graph.stream_events({"input": "use a tool"}, version="v3")

    tool_names = [call.tool_name for call in stream.tool_calls]
    assert "expected_tool" in tool_names


@pytest.mark.asyncio
async def test_astream_messages(graph):
    stream = await graph.astream_events({"input": "test"}, version="v3")

    text = ""
    async for message in stream.messages:
        async for token in message.text:
            text += token

    assert text
```

## Testing Error Handling

```python
# casts/{cast_name}/tests/test_graph.py
import pytest


def test_error_propagates(graph):
    with pytest.raises(ValueError):
        graph.invoke({"input": "trigger_error"})


def test_error_handled(graph):
    result = graph.invoke({"input": "error_input"})

    assert "error" in result
```

## Testing Graph Structure

```python
# casts/{cast_name}/tests/test_graph.py
def test_has_expected_nodes(graph):
    expected = ["input", "process", "output"]

    for node_name in expected:
        assert node_name in graph.nodes
```

## Testing Node Timeouts (langgraph v1.2+)

`timeout=` on `add_node` raises `NodeTimeoutError` (subclass of `TimeoutError`). Async nodes only.

```python
# casts/{cast_name}/tests/test_graph.py
import pytest
from langgraph.errors import NodeTimeoutError


@pytest.mark.asyncio
async def test_node_timeout_raises(slow_graph):
    # slow_graph builds a graph with timeout=1 on a node that sleeps 5s
    with pytest.raises(NodeTimeoutError) as exc_info:
        await slow_graph.ainvoke({"input": "test"})

    assert exc_info.value.node == "slow_node"
    assert exc_info.value.kind in ("run", "idle")
```

## Testing Error Handlers (langgraph v1.2+)

`error_handler=` runs after all retries are exhausted and returns a `Command` to update state and route to a compensation branch.

```python
# casts/{cast_name}/tests/test_graph.py
def test_error_handler_routes_to_compensation(graph_with_handler):
    # Node raises ConnectionError; retry exhausts; error_handler routes to "finalize"
    result = graph_with_handler.invoke({"input": "trigger_payment_error"})

    assert result["status"].startswith("compensated:")
    assert "finalize_executed" in result
```

## Testing Graceful Shutdown (langgraph v1.2+)

```python
# casts/{cast_name}/tests/test_graph.py
import asyncio

import pytest
from langgraph.errors import GraphDrained
from langgraph.types import Command, RunControl


@pytest.mark.asyncio
async def test_graceful_drain_resumes(graph_with_checkpointer):
    control = RunControl()
    config = {"configurable": {"thread_id": "drain-test"}}

    async def drain_after_first_step():
        await asyncio.sleep(0.01)  # let one superstep start
        control.request_drain(reason="test")

    drain_task = asyncio.create_task(drain_after_first_step())

    try:
        with pytest.raises(GraphDrained):
            stream = await graph_with_checkpointer.astream_events(
                {"input": "test"}, config=config, version="v3", control=control,
            )
            async for _ in stream.messages:
                pass
    finally:
        await drain_task

    # Resume — same config, same thread
    stream = await graph_with_checkpointer.astream_events(
        Command(resume=None), config=config, version="v3",
    )
    final = await stream.output
    assert final is not None
```
