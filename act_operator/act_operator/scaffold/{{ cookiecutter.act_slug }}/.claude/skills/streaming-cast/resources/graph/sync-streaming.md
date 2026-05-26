# Sync Event Streaming

Consume graph output synchronously using `graph.stream_events(..., version="v3")`. Useful for scripts, CLI tools, and tests.

## Contents

- Basic Pattern
- Parameters
- Single Projection
- Multiple Projections (interleave)

## Basic Pattern

```python
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

In sync code, `message.text` is iterable for token-by-token output, and `str(message.text)` drains the iterator and returns the full text. `stream.output` blocks until the run finishes.

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

---

## Single Projection

```python
graph = {{ cookiecutter.cast_snake }}_graph()

stream = graph.stream_events(inputs, config=config, version="v3")

# Token-by-token
for message in stream.messages:
    for token in message.text:
        print(token, end="", flush=True)
```

```python
# State snapshots
stream = graph.stream_events(inputs, config=config, version="v3")

for snapshot in stream.values:
    print(snapshot)
```

```python
# Tool execution
stream = graph.stream_events(inputs, config=config, version="v3")

for call in stream.tool_calls:
    print(f"{call.tool_name}({call.input})")
    for delta in call.output_deltas:
        print(delta, end="", flush=True)
    print(call.output, call.error)
```

---

## Multiple Projections (interleave)

For sync code, `stream.interleave(...)` returns `(projection_name, item)` tuples in strict arrival order:

```python
stream = graph.stream_events(inputs, config=config, version="v3")

for name, item in stream.interleave("messages", "tool_calls", "values"):
    if name == "messages":
        for token in item.text:
            print(token, end="", flush=True)
    elif name == "tool_calls":
        print(f"\n[tool] {item.tool_name}({item.input})")
    elif name == "values":
        print(f"\n[state] keys={list(item)}")
```

For concurrent (non-arrival-order) consumption in sync code, drain projections sequentially — each projection iterator independently reads from the underlying event stream.
