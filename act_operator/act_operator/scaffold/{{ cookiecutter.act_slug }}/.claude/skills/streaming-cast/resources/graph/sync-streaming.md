# Sync Event Streaming

Consume graph output synchronously using `graph.stream_events(..., version="v3")`. `casts/{cast_name}/modules/` and `casts/{cast_name}/graph.py` are reserved for graph definition; **stream consumer code lives anywhere else** — pick the entry point that fits the project (an additional cast module such as `runtime.py`, an external script or CLI tool, or a test).

## Contents

- Basic Pattern
- Sync-Specific Behavior
- Parameters

## Basic Pattern

```python
# stream consumer — location flexible
from casts.{{ cookiecutter.cast_snake }}.graph import {{ cookiecutter.cast_snake }}_graph

graph = {{ cookiecutter.cast_snake }}_graph()

config = {"configurable": {"thread_id": "session-1"}}

stream = graph.stream_events(
    {"messages": [HumanMessage(content="hello")]},
    config=config,
    version="v3",
)

for message in stream.messages:
    for token in message.text:
        print(token, end="", flush=True)

final_state = stream.output
```

For projection-specific patterns (state snapshots, tool calls, subgraphs) and multi-projection consumption with `stream.interleave(...)`, see the projections and multiple-modes resources linked from SKILL.md.

---

## Sync-Specific Behavior

| Aspect | Sync | Async equivalent |
|--------|------|------------------|
| Iteration | `for x in stream.messages:` | `async for x in stream.messages:` |
| Text iteration | `for token in message.text:` | `async for token in message.text:` |
| Drain to final text | `str(message.text)` | `await message.text.text()` |
| Final state | `stream.output` (blocks until done) | `await stream.output` |

---

## Parameters

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
| `control` | `RunControl` \| None | `None` | Graceful shutdown handle (langgraph v1.2+) |
