# ProtocolEvent Envelope

Every raw event from `stream_events(..., version="v3")` is a `ProtocolEvent` dict. Iterate the run stream object directly to access raw events; use typed projections (`stream.messages`, etc.) for normal application code.

All code in this file is **consumer-side** — `casts/{cast_name}/modules/` and `casts/{cast_name}/graph.py` are reserved for graph definition; place this code anywhere else (an additional cast module, an external runtime/API module, a script, or a test).

## Contents

- Structure
- Channels
- Namespace Path
- Messages Channel (Content Blocks)
- Tools Channel
- Lifecycle Channel
- Iterating Raw Events
- Import Types

## Structure

```python
class ProtocolEvent(TypedDict):
    seq: int                    # strictly increasing within a run; use for ordering
    method: str                 # channel name (see Channels)
    params: ProtocolEventParams


class ProtocolEventParams(TypedDict):
    namespace: list[str]        # path of "<name>:<runtime_id>" segments from the root graph; [] is the root
    timestamp: int              # wall-clock milliseconds; can drift, don't rely on for ordering
    data: Any                   # channel-specific payload; shape depends on `method`
```

| Field | Type | Description |
|-------|------|-------------|
| `seq` | `int` | Strictly increasing event sequence; use for ordering |
| `method` | `str` | Channel name. Determines `params.data` shape |
| `params.namespace` | `list[str]` | Path from root to source scope. `[]` = root |
| `params.timestamp` | `int` | Wall-clock ms (drifts; do not order with this) |
| `params.data` | `Any` | Channel-specific payload |

---

## Channels

| Channel | Purpose |
|---------|---------|
| `values` | Full graph state snapshots |
| `updates` | Per-node state deltas |
| `messages` | Content-block-centric chat model output |
| `tools` | Tool call start, streamed output, finish, error events |
| `lifecycle` | Run, subgraph, and subagent status changes |
| `checkpoints` | Lightweight checkpoint envelopes for branching and time travel |
| `input` | Human-in-the-loop input requests and responses |
| `tasks` | Pregel task creation and result events |
| `custom` | User-defined payloads from `get_stream_writer()` |
| `custom:<name>` | Application-defined stream transformer output (named `StreamChannel`) |

Typed projections (`stream.messages`, `stream.values`, ...) are derived from these channels.

---

## Namespace Path

Namespace is a path from the root graph to the scope that emitted the event. The root is `[]`. Each child execution appends one `"<name>:<runtime_id>"` segment.

```
root graph                         []
└─ subagent                        ["researcher:6f4d"]
   └─ tool call inside subagent    ["researcher:6f4d", "tools:91ac"]
```

- The name before `:` is the stable graph or node name.
- The suffix after `:` is the per-invocation runtime ID.

Filter raw events by namespace yourself when you only care about a specific subtree. For nested graph executions, `stream.subgraphs` already does this — prefer that projection over manual filtering.

---

## Messages Channel (Content Blocks)

The `messages` channel models output as content blocks. The data's `event` field is one of:

| Event | Meaning |
|-------|---------|
| `message-start` | New message begins |
| `content-block-start` | A new block (text, reasoning, tool_call, ...) begins |
| `content-block-delta` | Streaming delta within the current block |
| `content-block-finish` | Block closes |
| `message-finish` | Message complete; may include token usage |

Content blocks have explicit boundaries: a block starts, emits zero or more deltas, then finishes before the next block starts. This makes text streaming, reasoning blocks, tool-call blocks, and multimodal content explicit without requiring provider-specific formats.

To consume raw content-block events directly instead of using `stream.messages`:

```python
stream = graph.stream_events(inputs, config=config, version="v3")

for event in stream:
    if event["method"] != "messages":
        continue

    data = event["params"]["data"][0]
    if not isinstance(data, dict):
        continue
    if data.get("event") != "content-block-delta":
        continue

    block = data.get("delta") or {}
    if block.get("type") == "text-delta":
        print(block.get("text", ""), end="", flush=True)
    elif block.get("type") == "reasoning-delta":
        print(f"[thinking]{block.get('reasoning', '')}", end="", flush=True)
```

---

## Tools Channel

The `tools` channel exposes tool execution. The data's `event` field is one of:

| Event | Meaning |
|-------|---------|
| `tool-started` | Tool execution begins |
| `tool-output-delta` | Streaming tool output chunk |
| `tool-finished` | Tool execution completes successfully |
| `tool-error` | Tool execution failed |

Tool events are correlated by tool-call ID, so a tool execution can be joined back to its originating tool-call content block on the `messages` channel.

---

## Lifecycle Channel

The `lifecycle` channel tracks root run, subgraph, and subagent status. The data's `event` field is one of:

| Event | Meaning |
|-------|---------|
| `started` | Scope begins execution |
| `running` | Periodic running status |
| `completed` | Scope finished successfully |
| `failed` | Scope failed |
| `interrupted` | Scope paused (HITL) |

Lifecycle data may include `graph_name`, `error`, and `cause` describing why a child scope started (parent tool call, fan-out send, edge transition).

---

## Iterating Raw Events

```python
from casts.{{ cookiecutter.cast_snake }}.graph import {{ cookiecutter.cast_snake }}_graph

graph = {{ cookiecutter.cast_snake }}_graph()

stream = graph.stream_events(inputs, config=config, version="v3")

for event in stream:
    namespace = event["params"]["namespace"]
    method = event["method"]
    print(namespace, method, event["params"]["data"])
```

Use the run object directly when you need:
- A channel not exposed as a typed projection
- Exact arrival order across all sources
- Full event envelope inspection (seq, namespace, timestamp)

---

## Import Types

```python
from langgraph.stream import (
    ProtocolEvent,
    StreamChannel,
    StreamTransformer,
)
```
