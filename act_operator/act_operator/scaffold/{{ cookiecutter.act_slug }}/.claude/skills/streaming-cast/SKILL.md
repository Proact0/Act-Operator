---
name: streaming-cast
description: Implements LangGraph v3 event streaming for graphs with subgraphs and agents. Use when adding streaming to runtime/API endpoint, need token streaming, custom stream projections, subagent streaming, or ask "add streaming", "stream tokens", "stream graph".
version: "2026.05.26"
author: Proact0
allowed-tools:
  - Read
  - Write
  - Edit
  - AskUserQuestion
---
# Streaming {{ cookiecutter.act_name }}'s Casts (v3)

Implement v3 event streaming to consume `{{ cookiecutter.cast_snake }}_graph()` output in runtime, API endpoints, or other consumers. Event streaming returns a run stream object with typed projections (`stream.messages`, `stream.values`, `stream.subgraphs`, `stream.output`, `stream.tool_calls`, ...) for independent consumption.

## When to Use

- Adding streaming output to a runtime or API endpoint
- Need token-by-token LLM output, tool call lifecycle, or final output streaming
- Custom progress events from nodes via stream writer (with custom transformers)
- Subagent/subgraph projection for source identification
- Transport integration (SSE recommended, WebSocket optional)

## When NOT to Use

- Building graph structure (nodes, edges, state) → `developing-cast`
- DeepAgent harness (create_deep_agent, backends) → `developing-deepagent`
- Architecture design → `architecting-act`
- Testing → `testing-cast`

---

## Quick Start

```python
from langchain_core.messages import HumanMessage

from casts.{{ cookiecutter.cast_snake }}.graph import {{ cookiecutter.cast_snake }}_graph

graph = {{ cookiecutter.cast_snake }}_graph()

config = {
    "configurable": {
        "actor_id": "user-123",
        "thread_id": "session-1",
    },
    "recursion_limit": 2000,
}

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

## Implementation Workflow

### Step 1: Choose Projection(s)

See [core/projections.md](./resources/core/projections.md).

| Goal | Projection |
|------|------------|
| LLM token-by-token output | `stream.messages` |
| Track state snapshots after each step | `stream.values` |
| Final agent state | `stream.output` |
| Nested subgraph/subagent discovery | `stream.subgraphs` |
| Tool execution lifecycle | `stream.tool_calls` |
| Custom transformer projections | `stream.extensions` |
| Interrupt handling (HITL) | `stream.interrupts` / `stream.interrupted` |

Multiple projections are consumed concurrently via `asyncio.gather` (async) or `stream.interleave(...)` (sync).

### Step 2: Open the Event Stream

Import the graph, call `stream_events()` (sync) or `await graph.astream_events()` (async).

```python
graph = {{ cookiecutter.cast_snake }}_graph()
stream = await graph.astream_events(inputs, config=config, version="v3")
```

### Step 3: Consume Typed Projections

Dispatch on projection properties:
- Token → `message.text` (async iterator of text deltas)
- Reasoning → `message.reasoning`
- Tool-call argument chunks → `message.tool_calls`
- Tool execution lifecycle → `stream.tool_calls` (`call.tool_name`, `call.input`, `call.output_deltas`, `call.output`, `call.error`)
- Nested graphs/subagents → `stream.subgraphs` (each handle exposes `.messages`, `.tool_calls`, `.values`, `.output`)

See [graph/message-handling.md](./resources/graph/message-handling.md).

### Step 4: Filter by Subgraph / Subagent

`stream.subgraphs` yields a handle per nested graph execution. Filter by `subgraph.graph_name`. No namespace string parsing required.

See [subgraph/nested-streaming.md](./resources/subgraph/nested-streaming.md).

### Step 5: Wire to Transport (SSE or WebSocket)

See [patterns/integration.md](./resources/patterns/integration.md). SSE is the LangChain ecosystem recommended transport.

---

## Component Reference

### Core Concepts

| Use when | Resource |
|----------|----------|
| choosing which projection(s) to use | [core/projections.md](./resources/core/projections.md) |
| understanding ProtocolEvent envelope and channels (raw events) | [core/protocol-events.md](./resources/core/protocol-events.md) |
| emitting custom events from nodes (get_stream_writer + StreamTransformer) | [core/stream-writer.md](./resources/core/stream-writer.md) |

### Stream Consumption

| Use when | Resource |
|----------|----------|
| sync streaming (scripts, tests) | [graph/sync-streaming.md](./resources/graph/sync-streaming.md) |
| async streaming (runtime, API endpoints) | [graph/async-streaming.md](./resources/graph/async-streaming.md) |
| handling tokens, reasoning, tool calls, tool results | [graph/message-handling.md](./resources/graph/message-handling.md) |

### Subgraph & Subagent

| Use when | Resource |
|----------|----------|
| streaming through subgraphs (stream.subgraphs) | [subgraph/subgraph-streaming.md](./resources/subgraph/subgraph-streaming.md) |
| filtering nested subgraphs by graph_name | [subgraph/nested-streaming.md](./resources/subgraph/nested-streaming.md) |
| streaming create_agent/create_deep_agent (subagents projection) | [subgraph/agent-streaming.md](./resources/subgraph/agent-streaming.md) |

### Patterns

| Use when | Resource |
|----------|----------|
| filtering by node name, tag, or graph_name | [patterns/filtering.md](./resources/patterns/filtering.md) |
| combining multiple projections (gather / interleave) | [patterns/multiple-modes.md](./resources/patterns/multiple-modes.md) |
| SSE / WebSocket transport integration | [patterns/integration.md](./resources/patterns/integration.md) |

---

## Verification

- [ ] Projection(s) chosen for use case
- [ ] `version="v3"` passed to `stream_events()`/`astream_events()` calls
- [ ] Message text/reasoning/tool_calls iterated via projection properties (no manual namespace parsing)
- [ ] Subgraphs consumed via `stream.subgraphs`, filtered by `graph_name`
- [ ] Tool execution consumed via `stream.tool_calls`
- [ ] Interrupts handled via `stream.interrupted` and `stream.interrupts`
- [ ] Transport layer tested end-to-end (SSE / WebSocket)
