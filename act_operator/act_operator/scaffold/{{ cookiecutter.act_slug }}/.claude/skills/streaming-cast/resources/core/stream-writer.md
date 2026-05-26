# Custom Stream Writer

Emit custom streaming events from inside nodes using `get_stream_writer()`. Consume them via a custom `StreamTransformer` that exposes a projection through `stream.extensions`.

## Contents

- Sync Nodes
- Async Nodes (Python 3.11+)
- Async Nodes (Python < 3.11)
- With BaseNode (runtime parameter)
- Custom Transformer (consumer side)
- Progress Patterns

## Sync Nodes

```python
from langgraph.config import get_stream_writer

def process_data(state):
    writer = get_stream_writer()

    writer({"status": "starting", "step": 1})
    # ... do work ...
    writer({"status": "processing", "progress": 50})
    # ... more work ...
    writer({"status": "complete", "progress": 100})

    return {"result": "done"}
```

These writes flow on the `custom` channel. A consumer must register a `StreamTransformer` that drains the channel into a projection (see [Custom Transformer](#custom-transformer-consumer-side)).

---

## Async Nodes (Python 3.11+)

```python
from langgraph.config import get_stream_writer

async def async_process(state):
    writer = get_stream_writer()
    writer({"status": "running"})
    result = await fetch_data()
    writer({"status": "done"})
    return {"data": result}
```

---

## Async Nodes (Python < 3.11)

`get_stream_writer()` is unavailable in async contexts pre-3.11. Use `StreamWriter` parameter injection:

```python
from langgraph.types import StreamWriter

async def async_process(state, writer: StreamWriter):
    # LangGraph injects writer automatically when declared as parameter
    writer({"status": "running"})
    result = await fetch_data()
    writer({"status": "done"})
    return {"data": result}
```

---

## With BaseNode (runtime parameter)

Access the stream writer via the `runtime` parameter:

```python
from casts.base_node import BaseNode

class ProcessNode(BaseNode):
    def execute(self, state, runtime):
        writer = runtime.stream_writer
        writer({"status": "processing", "node": self.name})
        # ... do work ...
        writer({"status": "complete", "node": self.name})
        return {"result": "done"}
```

Async:

```python
from casts.base_node import AsyncBaseNode

class AsyncProcessNode(AsyncBaseNode):
    async def execute(self, state, runtime):
        writer = runtime.stream_writer
        writer({"status": "processing", "node": self.name})
        result = await self.fetch()
        writer({"status": "complete", "node": self.name})
        return {"data": result}
```

---

## Custom Transformer (consumer side)

To expose writer events on `stream.extensions["progress"]`, implement a `StreamTransformer`:

```python
from typing import TypedDict

from langgraph.stream import ProtocolEvent, StreamChannel, StreamTransformer


class ProgressEvent(TypedDict):
    status: str
    progress: int


class ProgressTransformer(StreamTransformer):
    required_stream_modes = ("custom",)

    def __init__(self, scope: tuple[str, ...] = ()) -> None:
        super().__init__(scope)
        self.progress = StreamChannel[ProgressEvent]("progress")

    def init(self) -> dict:
        return {"progress": self.progress}

    def process(self, event: ProtocolEvent) -> bool:
        if event["method"] != "custom":
            return True

        data = event["params"]["data"]
        if isinstance(data, dict) and "status" in data:
            self.progress.push(data)
        return True
```

Register at call time or compile time:

```python
# Call time
stream = graph.stream_events(inputs, config=config, version="v3", transformers=[ProgressTransformer])

for activity in stream.extensions["progress"]:
    print(activity)

# Compile time (every run produces the projection)
graph = builder.compile(transformers=[ProgressTransformer])
```

| `StreamChannel` form | Effect |
|----------------------|--------|
| `StreamChannel()` | Side-channel only (exposed on `stream.extensions`, not on raw event stream) |
| `StreamChannel(name)` | Side-channel **and** flowed into the main event stream as `custom:<name>` events |

Use the named form when consumers need the projection on both the typed extensions and raw events; use unnamed for in-process handles (promises, async iterables, class instances) that can't be serialized.

---

## Progress Patterns

### Percentage Progress

```python
class BatchProcessNode(BaseNode):
    def execute(self, state, runtime):
        writer = runtime.stream_writer
        items = state["items"]

        for i, item in enumerate(items):
            progress = int((i + 1) / len(items) * 100)
            writer({"progress": progress, "current": item})
            self.process_item(item)

        return {"processed": len(items)}
```

### Streaming Non-LangChain Model Output

```python
from langgraph.config import get_stream_writer

async def stream_external_llm(state):
    writer = get_stream_writer()
    response = ""

    async for chunk in external_model.stream(state["prompt"]):
        response += chunk.text
        writer({"token": chunk.text, "role": "assistant"})

    return {"response": response}
```
