# Multiple Projections

Consume multiple projections from one event stream for comprehensive event coverage. All code in this file is **consumer-side** — `casts/{cast_name}/modules/` and `casts/{cast_name}/graph.py` are reserved for graph definition; place this code anywhere else (an additional cast module, an external runtime/API module, a script, or a test).

## Contents

- Async: asyncio.gather
- Sync: stream.interleave
- Common Combinations
- Dispatch Pattern
- Performance

## Async: asyncio.gather

Each projection iterator independently drains from the underlying event stream — multiple consumers do not interfere:

```python
import asyncio

graph = {{ cookiecutter.cast_snake }}_graph()

stream = await graph.astream_events(inputs, config=config, version="v3")

async def consume_messages():
    async for message in stream.messages:
        async for token in message.text:
            print(token, end="", flush=True)

async def consume_tool_calls():
    async for call in stream.tool_calls:
        print(f"\n[tool] {call.tool_name}({call.input})")

async def consume_subagents():
    async for subagent in stream.subagents:
        print(f"\n[subagent] {subagent.name}")

await asyncio.gather(
    consume_messages(),
    consume_tool_calls(),
    consume_subagents(),
)
```

---

## Sync: stream.interleave

For synchronous code, `stream.interleave(...)` returns `(projection_name, item)` tuples in strict arrival order:

```python
stream = graph.stream_events(inputs, config=config, version="v3")

for name, item in stream.interleave("messages", "tool_calls", "values"):
    if name == "messages":
        for token in item.text:
            print(token, end="", flush=True)
    elif name == "tool_calls":
        print(f"\n[tool] {item.tool_name}")
    elif name == "values":
        print(f"\n[state] keys={list(item)}")
```

---

## Common Combinations

### Messages + Tool Calls (Most Common)

Token streaming + tool execution visibility:

```python
import asyncio

stream = await graph.astream_events(inputs, config=config, version="v3")

async def messages_task():
    async for message in stream.messages:
        async for token in message.text:
            print(token, end="", flush=True)

async def tools_task():
    async for call in stream.tool_calls:
        print(f"\n--- {call.tool_name} ---")
        async for delta in call.output_deltas:
            print(delta, end="", flush=True)

await asyncio.gather(messages_task(), tools_task())
```

### Messages + Values (Progress + Tokens)

Token streaming + per-step state visibility:

```python
async def values_task():
    async for snapshot in stream.values:
        print(f"\n[state] {list(snapshot)}")

await asyncio.gather(messages_task(), values_task())
```

### Messages + Subagents (Full Visibility — DeepAgent)

```python
async def coordinator_task():
    async for message in stream.messages:
        async for token in message.text:
            print(f"[coordinator] {token}", end="")

async def subagent_task():
    async for subagent in stream.subagents:
        async for message in subagent.messages:
            async for token in message.text:
                print(f"[{subagent.name}] {token}", end="")

await asyncio.gather(coordinator_task(), subagent_task())
```

---

## Dispatch Pattern

Clean handler dispatch for multi-projection streams. Each projection consumer is a wrapper coroutine that iterates its async source and dispatches per item; `asyncio.gather` runs the three consumers concurrently:

```python
import asyncio

stream = await graph.astream_events(inputs, config=config, version="v3")

async def dispatch_message(message):
    async for token in message.text:
        await send({"type": "token", "content": token, "node": message.node})

async def dispatch_tool_call(call):
    await send({"type": "tool_call", "name": call.tool_name, "args": call.input})
    async for delta in call.output_deltas:
        await send({"type": "tool_delta", "delta": delta})
    if call.completed:
        await send({"type": "tool_result", "name": call.tool_name, "output": call.output})

async def dispatch_subagent(subagent):
    await send({"type": "subagent_started", "name": subagent.name})
    async for message in subagent.messages:
        async for token in message.text:
            await send({"type": "token", "content": token, "source": subagent.name})

async def consume_messages():
    async for message in stream.messages:
        await dispatch_message(message)

async def consume_tool_calls():
    async for call in stream.tool_calls:
        await dispatch_tool_call(call)

async def consume_subagents():
    async for subagent in stream.subagents:
        await dispatch_subagent(subagent)

await asyncio.gather(consume_messages(), consume_tool_calls(), consume_subagents())
```

> **Why not `*(dispatch_x(x) async for x in stream.x)`?** Async generator expressions cannot be unpacked with `*` (raises `TypeError: 'async_generator' object is not iterable`). Wrapping each projection consumer in its own coroutine preserves streaming semantics: each handler dispatches items as they arrive, instead of buffering the entire stream before `gather` starts.

---

## Performance

| Projection Set | Volume | Use Case |
|----------------|--------|----------|
| `stream.messages` | High | Token display (production) |
| `stream.messages + stream.tool_calls` | High | Interactive UI with tool calls |
| `stream.messages + stream.subagents` | Medium-High | DeepAgent UI with subagent attribution |
| `stream.messages + stream.values` | Medium | Token display + state debugging |
| `stream.output` alone | Low | Final result only |

Multiple consumers reading the same projections concurrently is safe — reading `stream.messages` does not consume events needed by `stream.values`, `stream.subgraphs`, or `stream.output`.
