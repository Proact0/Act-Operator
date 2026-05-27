# Transport Integration

Stream graph events to external consumers via SSE or WebSocket using v3 typed projections.

## Contents

- SSE (Recommended)
- WebSocket
- SSE Protocol

## SSE (Recommended)

Server-Sent Events — LangChain/LangGraph ecosystem recommended pattern for HTTP-based streaming. This generator is **consumer-side** — `casts/{cast_name}/modules/` and `casts/{cast_name}/graph.py` are reserved for graph definition; place this generator anywhere else (an additional cast module such as `runtime.py`, an external API endpoint module, etc.):

```python
# stream consumer — location flexible
import asyncio
import json
import logging

from langchain_core.messages import HumanMessage

from casts.{{ cookiecutter.cast_snake }}.graph import {{ cookiecutter.cast_snake }}_graph

logger = logging.getLogger(__name__)


async def event_generator(query: str, config: dict):
    """SSE event generator. Framework-agnostic async generator."""
    graph = {{ cookiecutter.cast_snake }}_graph()
    inputs = {"messages": [HumanMessage(content=query)]}

    stream = await graph.astream_events(inputs, config=config, version="v3")
    queue: asyncio.Queue = asyncio.Queue()
    sentinel = object()

    async def dispatch_messages():
        async for message in stream.messages:
            async for token in message.text:
                await queue.put({
                    "event": "token",
                    "data": {"content": token, "node": message.node, "source": "{{ cookiecutter.cast_snake }}"},
                })

    async def dispatch_tool_calls():
        async for call in stream.tool_calls:
            await queue.put({
                "event": "tool_call",
                "data": {"name": call.tool_name, "args": call.input, "source": "{{ cookiecutter.cast_snake }}"},
            })
            async for delta in call.output_deltas:
                await queue.put({
                    "event": "tool_delta",
                    "data": {"delta": delta, "name": call.tool_name},
                })
            await queue.put({
                "event": "tool_result",
                "data": {
                    "name": call.tool_name,
                    # success → stringify the output (None stays None, not "None"); failure → no content
                    "content": (
                        str(call.output)
                        if call.error is None and call.output is not None
                        else None
                    ),
                    "error": str(call.error) if call.error else None,
                },
            })

    async def dispatch_subagents():
        async for subagent in stream.subagents:
            async for message in subagent.messages:
                async for token in message.text:
                    await queue.put({
                        "event": "token",
                        "data": {"content": token, "node": message.node, "source": subagent.name},
                    })

    async def run():
        try:
            await asyncio.gather(
                dispatch_messages(),
                dispatch_tool_calls(),
                dispatch_subagents(),
            )
        finally:
            await queue.put(sentinel)

    task = asyncio.create_task(run())

    try:
        while True:
            item = await queue.get()
            if item is sentinel:
                break
            yield f"event: {item['event']}\ndata: {json.dumps(item['data'])}\n\n"
        yield "event: done\ndata: {}\n\n"
    finally:
        task.cancel()
```

The `event_generator` is a plain async generator — integrate with any Python web framework (FastAPI, Starlette, aiohttp, Django Channels, etc.) by wiring it to an SSE response.

---

## WebSocket

WebSocket pattern — use when bidirectional communication or real-time push is required. This handler is **consumer-side** — `casts/{cast_name}/modules/` and `casts/{cast_name}/graph.py` are reserved for graph definition; place this handler anywhere else (an additional cast module such as `runtime.py`, an external WebSocket endpoint module, etc.):

```python
# stream consumer — location flexible
import asyncio
import logging

from langchain_core.messages import HumanMessage

from casts.{{ cookiecutter.cast_snake }}.graph import {{ cookiecutter.cast_snake }}_graph

logger = logging.getLogger(__name__)


async def handle_websocket_message(send_json, data: dict) -> None:
    """Handle a single WebSocket message. Framework-agnostic.

    Args:
        send_json: Callable that sends a JSON-serializable dict to the client.
        data: Parsed JSON message from the client.
    """
    graph = {{ cookiecutter.cast_snake }}_graph()
    inputs = {
        "messages": [HumanMessage(content=data.get("query", ""))],
    }
    config = {
        "configurable": {
            "actor_id": data.get("user_id", "anonymous"),
            "thread_id": data.get("session_id", "default"),
        },
        "recursion_limit": 2000,
    }

    stream = await graph.astream_events(inputs, config=config, version="v3")

    async def messages_task():
        async for message in stream.messages:
            async for token in message.text:
                await send_json({
                    "type": "token",
                    "content": token,
                    "node": message.node,
                    "source": "{{ cookiecutter.cast_snake }}",
                })

    async def tool_calls_task():
        async for call in stream.tool_calls:
            await send_json({
                "type": "tool_call",
                "name": call.tool_name,
                "args": call.input,
                "source": "{{ cookiecutter.cast_snake }}",
            })
            async for delta in call.output_deltas:
                await send_json({"type": "tool_delta", "delta": delta, "name": call.tool_name})
            await send_json({
                "type": "tool_result",
                "name": call.tool_name,
                # success → stringify the output (None stays None, not "None"); failure → no content
                "content": (
                    str(call.output)
                    if call.error is None and call.output is not None
                    else None
                ),
                "error": str(call.error) if call.error else None,
            })

    async def subagents_task():
        async for subagent in stream.subagents:
            async for message in subagent.messages:
                async for token in message.text:
                    await send_json({
                        "type": "token",
                        "content": token,
                        "node": message.node,
                        "source": subagent.name,
                    })

    await asyncio.gather(messages_task(), tool_calls_task(), subagents_task())
    await send_json({"type": "done"})
```

---

## SSE Protocol

| Direction | Event | Data |
|-----------|-------|------|
| S→C | `token` | `{content, node, source}` |
| S→C | `tool_call` | `{name, args, source}` |
| S→C | `tool_delta` | `{delta, name}` |
| S→C | `tool_result` | `{name, content, error}` |
| S→C | `done` | `{}` |
