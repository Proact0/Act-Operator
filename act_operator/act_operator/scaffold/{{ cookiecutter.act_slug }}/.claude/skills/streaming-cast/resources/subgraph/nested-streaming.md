# Nested Streaming & Source Identification

Identify event sources in nested graphs. With v3 typed projections, prefer `stream.subgraphs` / `stream.subagents` over manual namespace parsing.

## Contents

- Built-in vs Raw Identification
- Stream Subgraphs (Built-in)
- Filter by graph_name
- Raw Namespace Path (Advanced)
- Visualization

## Built-in vs Raw Identification

| Goal | Use |
|------|-----|
| Filter events by inner graph name | `stream.subgraphs` + `subgraph.graph_name` |
| Filter events by delegated subagent name (Deep Agents) | `stream.subagents` + `subagent.name` |
| Inspect the namespace path | `subgraph.path` (already-parsed list) |
| Raw envelope access | iterate `stream`, inspect `event["params"]["namespace"]` |

Namespace parsing (custom `_parse_source` functions) is no longer required for typical use — use the typed projection's `.graph_name` or `.name` field directly.

---

## Stream Subgraphs (Built-in)

```python
graph = {{ cookiecutter.cast_snake }}_graph()

stream = await graph.astream_events(inputs, config=config, version="v3")

async for subgraph in stream.subgraphs:
    name = subgraph.graph_name
    path = subgraph.path  # list[str], e.g. ["researcher:6f4d", "tools:91ac"]

    async for message in subgraph.messages:
        async for token in message.text:
            print(f"[{name}] {token}", end="")
```

Each `subgraph` handle exposes `.messages`, `.tool_calls`, `.values`, `.output`, and `.subgraphs` for further recursion.

---

## Filter by graph_name

Set `name=` on graph compilation to get a stable label:

```python
# Custom subgraph
researcher_graph = builder.compile(name="researcher")

# Agent subgraph
researcher_agent = create_agent(model="...", tools=[...], name="researcher")

# Deep agent subagent — name on the subagent dict
deep_agent = create_deep_agent(
    model="...",
    tools=[...],
    subagents=[
        {"name": "researcher", "description": "...", "system_prompt": "...", "tools": [...]},
    ],
)
```

Then filter:

```python
stream = await graph.astream_events(inputs, config=config, version="v3")

async for subgraph in stream.subgraphs:
    if subgraph.graph_name == "researcher":
        async for message in subgraph.messages:
            async for token in message.text:
                print(f"[researcher] {token}", end="")
```

For Deep Agents, prefer `stream.subagents` (filters out internal graph nodes — see [agent-streaming.md](./agent-streaming.md)).

---

## Raw Namespace Path (Advanced)

When you need access to the raw `ProtocolEvent` namespace (e.g., to interleave with channels not exposed as a typed projection), iterate the run object directly:

```python
stream = graph.stream_events(inputs, config=config, version="v3")

for event in stream:
    namespace = event["params"]["namespace"]  # list[str]
    method = event["method"]

    # namespace path looks like ["researcher:6f4d", "tools:91ac"]
    names = [seg.split(":")[0] for seg in namespace]
    print(f"[{'/'.join(names) or 'root'}] method={method}")
```

| `namespace` value | Meaning |
|-------------------|---------|
| `[]` | Root graph |
| `["NodeName:<id>"]` | One level deep (subgraph or agent) |
| `["...", "tools:<id>"]` | Tool execution boundary |
| `["...", "tools:<id>", "subagent:<id>"]` | Subagent invoked from a tool |

The name before `:` is the stable graph/node name; the suffix is a per-invocation runtime ID.

---

## Visualization

Print a tree-structured view of streaming events using `subgraph.path`:

```python
seen_paths: set[tuple[str, ...]] = set()

stream = await graph.astream_events(inputs, config=config, version="v3")

async for subgraph in stream.subgraphs:
    path_key = tuple(subgraph.path)
    if path_key in seen_paths:
        continue
    seen_paths.add(path_key)

    depth = len(path_key)
    names = [p.split(":")[0] for p in path_key]
    prefix = "│ " * (depth - 1) + "├─ " if depth else ""
    print(f"{prefix}{names[-1] if names else 'root'}")
```

Output:
```
├─ preprocess
├─ AgentNode
│ ├─ tools
│ │ ├─ researcher
├─ postprocess
```
