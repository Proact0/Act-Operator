# Async Event Streaming

Consume graph output asynchronously using `graph.astream_events(..., version="v3")`. Used in runtime endpoints and API handlers.

## Contents

- Basic Pattern
- With Config
- Python < 3.11 Workaround
- Parallel Streaming

## Basic Pattern

```python
from casts.{{ cookiecutter.cast_snake }}.graph import {{ cookiecutter.cast_snake }}_graph

graph = {{ cookiecutter.cast_snake }}_graph()

config = {"configurable": {"thread_id": "session-1"}}

stream = await graph.astream_events(
    {"messages": [HumanMessage(content="hello")]},
    config=config,
    version="v3",
)

async for message in stream.messages:
    async for token in message.text:
        print(token, end="", flush=True)

final_state = await stream.output
```

---

## With Config

Pass `config` with `configurable` for thread/actor scoping:

```python
graph = {{ cookiecutter.cast_snake }}_graph()

config = {
    "configurable": {
        "actor_id": user_id,
        "thread_id": session_id,
    },
    "recursion_limit": 2000,
}

stream = await graph.astream_events(inputs, config=config, version="v3")

async for message in stream.messages:
    async for token in message.text:
        # ... dispatch to transport
        await send_token(token)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input` | dict \| Command \| None | — | Input state (or `Command` for resume) |
| `config` | dict \| None | `None` | Execution config (thread_id, actor_id, recursion_limit) |
| `version` | `"v3"` | required | Always pass `"v3"` for the typed-projection event stream |
| `transformers` | list | `[]` | Custom `StreamTransformer` classes for `stream.extensions` projections |
| `context` | ContextT \| None | `None` | Static context for the run |
| `durability` | `"sync"` \| `"async"` \| `"exit"` \| None | `None` | Checkpoint persistence timing. Requires checkpointer |
| `interrupt_before` | list \| `"*"` \| None | `None` | Nodes to interrupt before execution |
| `interrupt_after` | list \| `"*"` \| None | `None` | Nodes to interrupt after execution |

---

## Python < 3.11 Workaround

Python < 3.11 asyncio doesn't propagate context automatically. Pass `config` explicitly to `astream_events()` **and** to LLM calls inside async nodes:

```python
from casts.base_node import AsyncBaseNode

class LLMNode(AsyncBaseNode):
    async def execute(self, state, config):
        # Explicit config propagation ensures streaming callbacks work
        response = await self.model.ainvoke(state["messages"], config)
        return {"response": response}
```

**Recommendation:** Upgrade to Python 3.11+.

---

## Parallel Streaming

Stream from multiple graphs concurrently:

```python
import asyncio
from casts.{{ cookiecutter.cast_snake }}.graph import {{ cookiecutter.cast_snake }}_graph
from casts.another_cast.graph import another_cast_graph

async def stream_both(inputs, config):
    async def consume(graph, name):
        stream = await graph.astream_events(inputs, config=config, version="v3")
        async for message in stream.messages:
            async for token in message.text:
                print(f"[{name}] {token}", end="")

    await asyncio.gather(
        consume({{ cookiecutter.cast_snake }}_graph(), "{{ cookiecutter.cast_snake }}"),
        consume(another_cast_graph(), "another_cast"),
    )
```

---

## Multiple Projections Concurrently

Use `asyncio.gather` to consume independent projections concurrently:

```python
import asyncio

stream = await graph.astream_events(inputs, config=config, version="v3")

async def consume_messages():
    async for message in stream.messages:
        async for token in message.text:
            await send_token(token)

async def consume_tool_calls():
    async for call in stream.tool_calls:
        await send_tool_call(call.tool_name, call.input)

async def consume_subagents():
    async for subagent in stream.subgraphs:
        async for message in subagent.messages:
            async for token in message.text:
                await send_token(token, source=subagent.graph_name)

await asyncio.gather(
    consume_messages(),
    consume_tool_calls(),
    consume_subagents(),
)
```
