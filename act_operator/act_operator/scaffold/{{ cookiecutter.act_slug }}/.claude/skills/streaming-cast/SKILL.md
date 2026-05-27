---
name: streaming-cast
description: Implements LangGraph v3 event streaming for graphs with subgraphs and agents. Use when adding streaming to runtime/API endpoint, need token streaming, custom stream projections, subagent streaming, or ask "add streaming", "stream tokens", "stream graph".
version: "2026.05.27"
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

`casts/{{ cookiecutter.cast_snake }}/modules/` and `casts/{{ cookiecutter.cast_snake }}/graph.py` are reserved for graph definition. **Stream consumer code lives anywhere else** — pick the entry point that fits the project (an additional module within the cast such as `runtime.py`, an external API endpoint module, a script, or a test).

```python
# stream consumer — location flexible
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

1. **Choose projection(s)** for the use case (see table below).
2. **Open the event stream** with `stream_events()` (sync) or `astream_events()` (async).
3. **Consume projections** — token, reasoning, tool-call argument chunks, tool execution lifecycle, subgraph/subagent handles.
4. **Filter by `subgraph.graph_name`** or `subagent.name` when multi-source attribution is needed.
5. **Wire to transport** (SSE recommended; WebSocket optional).

| Goal | Projection |
|------|------------|
| LLM token-by-token output | `stream.messages` → `message.text` |
| LLM reasoning deltas | `stream.messages` → `message.reasoning` |
| Tool-call argument chunks (LLM-side) | `stream.messages` → `message.tool_calls` |
| Tool execution lifecycle | `stream.tool_calls` |
| Per-step state snapshots | `stream.values` |
| Final state only | `stream.output` |
| Nested subgraph/agent | `stream.subgraphs` |
| Deep Agent delegated task | `stream.subagents` |
| Custom transformer projections | `stream.extensions["<name>"]` |
| HITL interrupts | `stream.interrupts` / `stream.interrupted` |
| Raw protocol events | iterate the stream object |

Multiple projections are consumed concurrently via `asyncio.gather` (async) or `stream.interleave(...)` (sync). Each projection iterator independently reads from the underlying event stream.

---

## Component Reference

### Core Concepts

| Use when | Resource |
|----------|----------|
| choosing which projection(s) to use, decision framework | [core/projections.md](./resources/core/projections.md) |
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
| streaming through nested subgraphs, namespace path access, tree visualization | [subgraph/subgraph-streaming.md](./resources/subgraph/subgraph-streaming.md) |
| streaming create_agent / create_deep_agent (incl. subagents projection) | [subgraph/agent-streaming.md](./resources/subgraph/agent-streaming.md) |

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
