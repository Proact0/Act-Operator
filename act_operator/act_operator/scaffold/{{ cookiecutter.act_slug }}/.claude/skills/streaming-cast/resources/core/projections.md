# Projections

LangGraph v3 event streaming returns a run stream object with typed projections. Pass `version="v3"` to `stream_events()` / `astream_events()`.

## Contents

- All Projections
- Decision Framework
- Multi-Projection Consumption

## All Projections

### `stream.messages` — Chat Model Message Streams

Yields one `ChatModelStream` per LLM call. Each exposes `.text`, `.reasoning`, `.tool_calls`, and `.output`. **Most commonly used for token streaming.**

```python
from casts.{{ cookiecutter.cast_snake }}.graph import {{ cookiecutter.cast_snake }}_graph

graph = {{ cookiecutter.cast_snake }}_graph()

stream = await graph.astream_events(inputs, config=config, version="v3")

async for message in stream.messages:
    async for token in message.text:
        print(token, end="", flush=True)
```

**Use when:** Displaying LLM output token-by-token in real time.

---

### `stream.values` — State Snapshots

Iterates the full state after each step.

```python
stream = await graph.astream_events(inputs, config=config, version="v3")

async for snapshot in stream.values:
    print(snapshot)
```

**Use when:** State debugging, full state inspection at every step.

---

### `stream.output` — Final State Awaitable

Awaits the final agent/graph state. Drains the stream if not already finalized.

```python
stream = await graph.astream_events(inputs, config=config, version="v3")
final_state = await stream.output
```

**Use when:** Need only the final result; ignore intermediate events.

---

### `stream.subgraphs` — Nested Graph Discovery

Each handle exposes the inner graph's own `.messages`, `.values`, `.tool_calls`, `.output`, and recursive `.subagents`/`.subgraphs`. Filter by `subgraph.graph_name`.

```python
stream = await graph.astream_events(inputs, config=config, version="v3")

async for subgraph in stream.subgraphs:
    print(subgraph.graph_name, subgraph.path)
    async for message in subgraph.messages:
        async for token in message.text:
            print(token, end="", flush=True)
```

**Use when:** Observing nested graph or subagent executions without parsing namespace strings.

---

### `stream.tool_calls` — Tool Execution Lifecycle

Streams tool execution: inputs, output deltas, finished/error states.

```python
stream = await graph.astream_events(inputs, config=config, version="v3")

async for call in stream.tool_calls:
    print(call.tool_name, call.input)
    async for delta in call.output_deltas:
        print(delta, end="", flush=True)
    print(call.output, call.error)
```

**Use when:** Tracking tool call lifecycle and inspecting tool outputs.

---

### `stream.interrupts` / `stream.interrupted` — Human-in-the-Loop

After consuming the stream, `stream.interrupted` is `True` when the run paused for HITL input. Inspect `stream.interrupts` for payloads.

```python
from langgraph.types import Command

stream = await graph.astream_events(inputs, config=config, version="v3")

async for message in stream.messages:
    async for token in message.text:
        print(token, end="", flush=True)

if stream.interrupted:
    for interrupt in stream.interrupts:
        print(interrupt)

# Resume with Command
stream = await graph.astream_events(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config,
    version="v3",
)
final_state = await stream.output
```

**Use when:** Graph compiled with checkpointer for HITL interrupts.

---

### `stream.extensions[<name>]` — Custom Transformer Projections

User-defined transformer projections appear here. See [stream-writer.md](./stream-writer.md) for custom transformer authoring.

```python
stream = await graph.astream_events(
    inputs,
    config=config,
    version="v3",
    transformers=[ToolActivityTransformer],
)

for activity in stream.extensions["tool_activity"]:
    print(activity)
```

**Use when:** Application needs a projection shape not provided by built-in projections.

---

### Iterating Raw Protocol Events

Iterate the `stream` object directly to receive the underlying `ProtocolEvent` envelopes. Each event has `seq`, `method` (channel: `messages`, `values`, `updates`, `custom`, `tools`, `lifecycle`, `checkpoints`, `input`, `tasks`), `params.namespace`, `params.timestamp`, and `params.data`. See [protocol-events.md](./protocol-events.md).

**Use when:** Application needs raw channel access (no projection covers the channel) or exact arrival order across sources.

---

## Decision Framework

```
What do you need?
├─ Token-by-token LLM output         → stream.messages → message.text
├─ Reasoning/thinking output         → stream.messages → message.reasoning
├─ Tool call argument chunks (LLM)   → stream.messages → message.tool_calls
├─ Tool execution lifecycle          → stream.tool_calls
├─ Per-node state changes            → stream.values
├─ Final state only                  → stream.output
├─ Nested subgraphs / subagents      → stream.subgraphs (+ subagent.messages etc.)
├─ Custom progress events            → stream.extensions["<name>"] + StreamTransformer
└─ Raw channel/protocol events       → iterate the stream object directly
```

| Projection | Yields | Volume | Use Case |
|------------|--------|--------|----------|
| `stream.messages` | `ChatModelStream` | High | Token-by-token display |
| `stream.values` | state dict | Medium | Per-step state tracking |
| `stream.output` | final state | One | Final result only |
| `stream.subgraphs` | subgraph handle | Per-call | Nested graph filtering |
| `stream.tool_calls` | tool-call lifecycle | Per-tool | Tool monitoring |
| `stream.interrupts` | interrupt payloads | Rare | HITL inspection |
| `stream.extensions[name]` | custom payload | Variable | Application-specific |

---

## Multi-Projection Consumption

**Async (concurrent via `asyncio.gather`):**

```python
import asyncio

stream = await graph.astream_events(inputs, config=config, version="v3")

async def consume_messages():
    async for message in stream.messages:
        print(f"[llm] node={message.node}")

async def consume_tool_calls():
    async for call in stream.tool_calls:
        print(f"[tool] {call.tool_name}({call.input})")

await asyncio.gather(consume_messages(), consume_tool_calls())
```

**Sync (arrival order via `stream.interleave`):**

```python
stream = graph.stream_events(inputs, config=config, version="v3")

for name, item in stream.interleave("messages", "tool_calls", "values"):
    if name == "messages":
        print(f"[llm] {item.node}")
    elif name == "tool_calls":
        print(f"[tool] {item.tool_name}")
    elif name == "values":
        print(f"[state] {list(item)}")
```

Multiple consumers can read projections concurrently — reading `stream.messages` does not consume events needed by `stream.values`, `stream.subgraphs`, or `stream.output`.
