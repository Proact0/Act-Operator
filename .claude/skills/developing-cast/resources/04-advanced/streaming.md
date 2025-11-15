# Streaming

## When to Use This Resource

Read this for real-time token streaming, live state updates, or frontend integration.

## Key Concept

**Streaming:** Receive incremental outputs as graph executes, instead of waiting for completion.

## Stream Modes

### Mode: "values" (Full State)

```python
# Stream complete state after each node
for chunk in graph.stream(input, stream_mode="values"):
    print(chunk)  # Full state dict
```

**Use for:** Seeing complete state evolution

### Mode: "updates" (Node Outputs)

```python
# Stream only node updates
for chunk in graph.stream(input, stream_mode="updates"):
    print(chunk)  # {"node_name": {"updates": "..."}}
```

**Use for:** Tracking which nodes execute and their outputs

### Mode: "messages" (Token Streaming)

```python
# Stream LLM tokens
for chunk in graph.stream(input, stream_mode="messages"):
    if chunk[0] == "messages":
        print(chunk[1].content, end="", flush=True)
```

**Use for:** Real-time text generation display

## Async Streaming

```python
async def stream_graph():
    async for chunk in graph.astream(
        input,
        config=config,
        stream_mode="values"
    ):
        print(chunk)

asyncio.run(stream_graph())
```

## Common Patterns

### Frontend Token Streaming

```python
@app.post("/chat/stream")
async def chat_stream(message: str):
    async def generate():
        async for chunk in graph.astream(
            {"messages": [HumanMessage(content=message)]},
            stream_mode="messages"
        ):
            if chunk[0] == "messages":
                yield chunk[1].content

    return StreamingResponse(generate(), media_type="text/plain")
```

### State Progress Updates

```python
for chunk in graph.stream(input, stream_mode="updates"):
    for node_name, output in chunk.items():
        print(f"Node {node_name} completed: {output}")
```

## Decision Framework

```
Need LLM tokens in real-time?
  → stream_mode="messages"

Need to see state after each step?
  → stream_mode="values"

Need to track node execution?
  → stream_mode="updates"

Building chat UI?
  → Async streaming with "messages" mode
```

## References

- Graph execution: `01-core/graph.md`
