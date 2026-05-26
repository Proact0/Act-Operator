# Subgraph Streaming

Stream events from nested subgraphs within the graph using `stream.subgraphs`. Each handle exposes the inner graph's own typed projections.

## Contents

- Enable Subgraph Streaming
- Subgraph Handle Fields
- Filter by Graph Name
- Recurse into Nested Subgraphs

## Enable Subgraph Streaming

`stream.subgraphs` is built-in; no flag required. Open the event stream and iterate the projection:

```python
graph = {{ cookiecutter.cast_snake }}_graph()

stream = await graph.astream_events(inputs, config=config, version="v3")

async for subgraph in stream.subgraphs:
    print(f"subgraph started: {subgraph.graph_name}")
    async for message in subgraph.messages:
        async for token in message.text:
            print(token, end="", flush=True)
```

Set `name=` on `.compile(name=...)` (StateGraph) or `create_agent(name=...)` to get a stable label in `subgraph.graph_name`.

---

## Subgraph Handle Fields

Each handle in `stream.subgraphs` exposes:

| Field | Description |
|-------|-------------|
| `subgraph.graph_name` | Compiled graph name. Use to filter. |
| `subgraph.path` | Namespace path from root to this subgraph |
| `subgraph.status` | Lifecycle status (`started`, `running`, `completed`, `failed`, `interrupted`) |
| `subgraph.messages` | Chat-model messages emitted within the subgraph |
| `subgraph.values` | State snapshots within the subgraph |
| `subgraph.tool_calls` | Tool calls scoped to this subgraph |
| `subgraph.output` | Final state of the subgraph |
| `subgraph.subgraphs` | Recursively nested subgraphs |

---

## Filter by Graph Name

```python
stream = await graph.astream_events(inputs, config=config, version="v3")

async for subgraph in stream.subgraphs:
    if subgraph.graph_name != "researcher":
        continue
    async for message in subgraph.messages:
        async for token in message.text:
            print(f"[researcher] {token}", end="")
```

For Deep Agents specifically, use `stream.subagents` instead — it filters out internal graph nodes and exposes only delegated subagent tasks. See [agent-streaming.md](./agent-streaming.md).

---

## Recurse into Nested Subgraphs

```python
stream = await graph.astream_events(inputs, config=config, version="v3")

async for subgraph in stream.subgraphs:
    print(f"subgraph {subgraph.graph_name}: {subgraph.status}")

    async for call in subgraph.tool_calls:
        print(f"  {call.tool_name}({call.input})")

    async for nested in subgraph.subgraphs:
        print(f"  nested subgraph {nested.graph_name}: {nested.status}")
        async for message in nested.messages:
            async for token in message.text:
                print(f"    {token}", end="")
```

The `subgraph.subgraphs` recursion mirrors `stream.subgraphs` at the inner scope, allowing arbitrary nesting without manual namespace parsing.
