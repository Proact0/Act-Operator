# Message Handling

Handle text deltas, reasoning content, and tool calls from `stream.messages`. All code in this file is **consumer-side** — `casts/{cast_name}/modules/` and `casts/{cast_name}/graph.py` are reserved for graph definition; place this code anywhere else (an additional cast module, an external runtime/API module, a script, or a test).

## Contents

- ChatModelStream Fields
- Text Tokens
- Reasoning Tokens
- Tool Call Argument Chunks (LLM-side)
- Tool Execution Lifecycle (stream.tool_calls)
- Final Message Object
- Complete Dispatch Pattern

## ChatModelStream Fields

`stream.messages` yields one `ChatModelStream` per LLM call. Each exposes:

| Field | Description |
|-------|-------------|
| `message.node` | The graph node that invoked the LLM (`"model"` for agent graphs) |
| `message.text` | Text deltas (iterable for live streaming, `str(...)` for final text) |
| `message.reasoning` | Reasoning deltas (only for models that emit reasoning blocks) |
| `message.tool_calls` | Tool-call argument chunks (iterable); `.get()` returns finalized list |
| `message.output` | Final `AIMessage` after the call completes |
| `message.usage` (TS) / `message.output.usage_metadata` (Python) | Token counts |

---

## Text Tokens

> **Note:** `message.node` returns the graph node that invoked the LLM. For agent-based graphs (`create_agent`, `create_deep_agent`), the LLM node is named `"model"`. For custom StateGraph, it matches your `add_node("YourNodeName", ...)` call. `stream.messages` already filters to chat-model output; you do not need to filter by node unless you have multiple LLM-emitting nodes.

```python
graph = {{ cookiecutter.cast_snake }}_graph()

stream = await graph.astream_events(inputs, config=config, version="v3")

async for message in stream.messages:
    print(f"[{message.node}] ", end="")
    async for token in message.text:
        await send_token(token)
```

---

## Reasoning Tokens

Reasoning content uses the same shape as text content, but is only emitted by models that produce reasoning blocks (e.g. Claude with extended thinking).

```python
stream = await graph.astream_events(inputs, config=config, version="v3")

async for message in stream.messages:
    async for delta in message.reasoning:
        print(f"[thinking] {delta}", end="", flush=True)

    async for delta in message.text:
        print(delta, end="", flush=True)
```

---

## Tool Call Argument Chunks (LLM-side)

`message.tool_calls` streams tool-call argument chunks **while the model is producing the tool call**:

```python
stream = await graph.astream_events(inputs, config=config, version="v3")

async for message in stream.messages:
    async for chunk in message.tool_calls:
        # chunk while the model emits the tool call
        await send_tool_call_chunk(chunk)

    finalized = message.tool_calls.get()
    if finalized:
        # final tool call objects after message-finish
        await send_finalized_tool_calls(finalized)
```

---

## Tool Execution Lifecycle (stream.tool_calls)

`stream.tool_calls` streams the lifecycle of tool execution **after the tool starts running**:

```python
stream = await graph.astream_events(inputs, config=config, version="v3")

async for call in stream.tool_calls:
    print(f"{call.tool_name}({call.input})")
    async for delta in call.output_deltas:
        print(delta, end="", flush=True)

    if call.completed and call.error is None:
        print(call.output)
    elif call.error is not None:
        print(call.error)
```

| Field | Description |
|-------|-------------|
| `call.tool_name` | Tool that was invoked |
| `call.input` | Arguments passed to the tool |
| `call.output_deltas` | Streaming tool output chunks |
| `call.output` | Final tool output (after `completed`) |
| `call.error` | Error if execution failed |
| `call.completed` | Boolean, true after `tool-finished`/`tool-error` |

---

## Final Message Object

`message.output` is the finalized `AIMessage` after the LLM call completes, including provider-specific content blocks:

```python
stream = await graph.astream_events(inputs, config=config, version="v3")

async for message in stream.messages:
    async for _ in message.text:
        pass  # drain text deltas

    full_message = message.output
    usage = full_message.usage_metadata
    if usage:
        print(f"tokens: {usage.input_tokens}/{usage.output_tokens}")
```

---

## Complete Dispatch Pattern

Full message dispatch as used in runtime endpoints. `send` is any async callable that delivers a dict to the client (SSE yield, WebSocket send, etc.):

```python
import asyncio

graph = {{ cookiecutter.cast_snake }}_graph()

stream = await graph.astream_events(inputs, config=config, version="v3")

async def dispatch_messages():
    async for message in stream.messages:
        # Text tokens
        async for token in message.text:
            await send({"type": "token", "content": token, "node": message.node})

        # Reasoning (if model emits)
        async for delta in message.reasoning:
            await send({"type": "reasoning", "content": delta, "node": message.node})

        # Tool call argument chunks during model output
        async for chunk in message.tool_calls:
            await send({"type": "tool_call_chunk", "data": chunk})

async def dispatch_tool_calls():
    async for call in stream.tool_calls:
        await send({
            "type": "tool_call",
            "name": call.tool_name,
            "args": call.input,
        })
        async for delta in call.output_deltas:
            await send({"type": "tool_output_delta", "delta": delta})

        if call.error is not None:
            await send({"type": "tool_error", "error": str(call.error)})
        elif call.completed:
            await send({"type": "tool_result", "name": call.tool_name, "output": call.output})

await asyncio.gather(dispatch_messages(), dispatch_tool_calls())
await send({"type": "done"})
```
