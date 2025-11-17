# Streaming

## When to Use This Resource
Read this when implementing real-time updates, progress indicators, or responsive UIs that need incremental results.

## Why Stream?

**Streaming** provides real-time visibility into graph execution:
- Show progress to users (don't wait for entire graph to finish)
- Display LLM token-by-token (better UX)
- Debug execution flow
- Respond to events as they happen

## Stream Modes

### Mode 1: "values" (Full State)
**What:** Emits complete state after each node execution.
**When:** Need to see full state evolution.

```python
for chunk in graph.stream({"input": "..."}, stream_mode="values"):
    print(f"Current state: {chunk}")
    # chunk = entire state dict after each node
```

**Output:**
```
{'input': 'hello', 'step': 1}  # After node 1
{'input': 'hello', 'step': 1, 'processed': True}  # After node 2
{'input': 'hello', 'step': 1, 'processed': True, 'result': 'done'}  # After node 3
```

**Use for:**
- Debugging state changes
- UI updates showing full context
- Monitoring all state fields

### Mode 2: "updates" (State Deltas)
**What:** Emits only changes to state after each node.
**When:** Interested in what changed, not full state.

```python
for chunk in graph.stream({"input": "..."}, stream_mode="updates"):
    print(f"Node: {list(chunk.keys())[0]}, Updates: {list(chunk.values())[0]}")
    # chunk = {node_name: {updated_fields}}
```

**Output:**
```
{'node1': {'step': 1}}  # Node1 added step
{'node2': {'processed': True}}  # Node2 added processed
{'node3': {'result': 'done'}}  # Node3 added result
```

**Use for:**
- Incremental updates to UI
- Event logging
- Change tracking

### Mode 3: "messages" (LLM Tokens)
**What:** Streams LLM message tokens as they're generated.
**When:** Want to show LLM responses token-by-token.

```python
for chunk in graph.stream({"messages": [...]}, stream_mode="messages"):
    print(chunk.content, end="", flush=True)
    # Streams each token from LLM
```

**Use for:**
- ChatGPT-style streaming responses
- Real-time LLM output
- Better perceived latency

### Mode 4: "custom" (Custom Events)
**What:** Stream custom data you define in nodes.
**When:** Need to emit progress, metrics, or custom notifications.

```python
from langgraph.graph import interrupt
from casts.base_node import BaseNode

class ProgressNode(BaseNode):
    def execute(self, state: dict, runtime=None, **kwargs) -> dict:
        if runtime and runtime.stream_writer:
            # Emit custom progress event
            runtime.stream_writer({"progress": 0.5, "message": "Halfway done"})

        # Continue processing
        result = do_work(state)

        if runtime and runtime.stream_writer:
            runtime.stream_writer({"progress": 1.0, "message": "Complete"})

        return {"result": result}

# Stream custom events
for chunk in graph.stream({"input": "..."}, stream_mode="custom"):
    print(f"Progress: {chunk.get('progress')}, {chunk.get('message')}")
```

**Use for:**
- Progress indicators
- Metrics/telemetry
- Status updates
- Custom UI notifications

### Multiple Modes Simultaneously

```python
# Combine multiple stream modes
for chunk in graph.stream({"input": "..."}, stream_mode=["values", "custom"]):
    # chunk contains data from both modes
    if "progress" in chunk:  # Custom event
        update_progress_bar(chunk["progress"])
    else:  # Values mode
        update_state_display(chunk)
```

## Async Streaming

```python
async for chunk in graph.astream({"input": "..."}, stream_mode="values"):
    await send_to_websocket(chunk)
```

**When to use:**
- Async frameworks (FastAPI, async web apps)
- WebSocket connections
- High-concurrency scenarios

## Event-Based Streaming (Fine-Grained)

**astream_events** provides detailed execution events:

```python
async for event in graph.astream_events({"input": "..."}, version="v2"):
    kind = event["event"]

    if kind == "on_chain_start":
        print(f"Started: {event['name']}")
    elif kind == "on_chain_end":
        print(f"Finished: {event['name']}")
    elif kind == "on_chat_model_stream":
        print(event["data"]["chunk"].content, end="", flush=True)
    elif kind == "on_tool_start":
        print(f"Tool: {event['name']}")
```

**Events include:**
- `on_chain_start/end` - Graph/node execution
- `on_chat_model_stream` - LLM tokens
- `on_tool_start/end` - Tool execution
- `on_retriever_start/end` - Retriever calls

**Use for:**
- Detailed execution tracking
- Performance profiling
- Complex UI updates
- Observability

## Streaming with Interrupts

```python
# Stream until interrupt
for chunk in graph.stream({"input": "..."}, config=config, stream_mode="values"):
    print(chunk)
    # Stops streaming when interrupt is hit

# Check if interrupted
state = graph.get_state(config)
if state.next:  # Has next nodes = interrupted
    print(f"Interrupted before: {state.next}")

# Resume and continue streaming
for chunk in graph.stream(None, config=config, stream_mode="values"):
    print(chunk)
```

## Production Patterns

### Pattern 1: WebSocket Real-Time Updates

```python
from fastapi import WebSocket

async def stream_to_websocket(websocket: WebSocket, graph, input_data, config):
    async for chunk in graph.astream(input_data, config=config, stream_mode="values"):
        await websocket.send_json(chunk)

    # Send completion signal
    await websocket.send_json({"status": "complete"})
```

### Pattern 2: Server-Sent Events (SSE)

```python
from fastapi.responses import StreamingResponse

async def sse_stream(graph, input_data, config):
    async def event_generator():
        async for chunk in graph.astream(input_data, config=config, stream_mode="updates"):
            yield f"data: {json.dumps(chunk)}\n\n"
        yield "data: {\"status\": \"done\"}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

### Pattern 3: Progress Bar

```python
from tqdm import tqdm

total_steps = 5
with tqdm(total=total_steps) as pbar:
    for chunk in graph.stream({"input": "..."}, stream_mode="updates"):
        node_name = list(chunk.keys())[0]
        pbar.set_description(f"Processing: {node_name}")
        pbar.update(1)
```

### Pattern 4: Token-by-Token LLM Display

```python
async def stream_llm_response(graph, messages, config):
    """Stream LLM tokens to user interface."""
    full_response = ""

    async for chunk in graph.astream(
        {"messages": messages},
        config=config,
        stream_mode="messages"
    ):
        if hasattr(chunk, "content"):
            token = chunk.content
            full_response += token
            yield token  # Send to UI

    return full_response
```

## Debugging with Streaming

```python
# Verbose streaming for debugging
for chunk in graph.stream({"input": "..."}, stream_mode="values"):
    print(f"\n{'='*50}")
    print(f"State after update:")
    for key, value in chunk.items():
        print(f"  {key}: {value}")
    print(f"{'='*50}\n")
```

## Common Mistakes

❌ **Not handling stream completion**
```python
# ❌ No indication when stream ends
for chunk in graph.stream(...):
    display(chunk)

# ✅ Signal completion
for chunk in graph.stream(...):
    display(chunk)
print("Stream complete")  # Or send event
```

❌ **Blocking async streams**
```python
# ❌ Using sync in async context
for chunk in graph.stream(...):  # Blocks event loop
    await send(chunk)

# ✅ Use astream
async for chunk in graph.astream(...):
    await send(chunk)
```

❌ **Wrong stream mode for use case**
```python
# ❌ Using "values" when only need changes
for chunk in graph.stream(..., stream_mode="values"):
    # Sends entire state every time (wasteful)

# ✅ Use "updates" for deltas
for chunk in graph.stream(..., stream_mode="updates"):
    # Only sends changes
```

## Performance Considerations

**Stream modes overhead:**
- `values`: Most data (full state each time)
- `updates`: Less data (only changes)
- `messages`: Minimal (token-by-token)
- `custom`: Depends on your events

**Best practices:**
- Use `updates` or `custom` for high-frequency updates
- Use `values` for low-frequency or debugging
- Consider network bandwidth with WebSocket/SSE
- Batch custom events if emitting many

## References
- LangGraph Streaming: https://docs.langchain.com/oss/python/langgraph/streaming
- Related: `interrupts-hitl.md` (streaming with interrupts)
- Related: `../core/graph-compilation.md` (graphs that stream)
