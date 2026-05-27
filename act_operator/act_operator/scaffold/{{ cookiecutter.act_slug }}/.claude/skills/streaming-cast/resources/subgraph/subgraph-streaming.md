# Subgraph Streaming

Stream events from nested subgraphs within the graph using `stream.subgraphs`. Each handle exposes the inner graph's own typed projections — no namespace string parsing required.

`casts/{cast_name}/modules/` and `casts/{cast_name}/graph.py` are reserved for graph definition. Stream consumption code is **consumer-side** — place it anywhere else (additional cast module, external runtime/API module, script, test). The "Set a stable `name=`" examples below show where each definition (subgraph, agent, deep agent) lives within the reserved locations.

## Contents

- Enable Subgraph Streaming
- Subgraph Handle Fields
- Filter by Graph Name
- Recurse into Nested Subgraphs
- Raw Namespace Path (Advanced)
- Visualization

## Enable Subgraph Streaming

`stream.subgraphs` is built-in; no flag required.

```python
graph = {{ cookiecutter.cast_snake }}_graph()

stream = await graph.astream_events(inputs, config=config, version="v3")

async for subgraph in stream.subgraphs:
    print(f"subgraph started: {subgraph.graph_name}")
    async for message in subgraph.messages:
        async for token in message.text:
            print(token, end="", flush=True)
```

Set a stable `name=` for filtering. The location depends on what is being compiled:

```python
# casts/{cast_name}/graph.py — custom subgraph compiled via StateGraph
researcher_graph = builder.compile(name="researcher")
```

```python
# casts/{cast_name}/modules/agents.py — agent subgraph
researcher_agent = create_agent(model="...", tools=[...], name="researcher")
```

```python
# casts/{cast_name}/modules/agents.py — deep agent with named subagents
deep_agent = create_deep_agent(
    model="...",
    tools=[...],
    subagents=[
        {"name": "researcher", "description": "...", "system_prompt": "...", "tools": [...]},
    ],
)
```

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

For Deep Agents specifically, `stream.subagents` filters out internal graph nodes and exposes only delegated subagent tasks (see the agent-streaming resource linked from SKILL.md).

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

---

## Raw Namespace Path (Advanced)

When you need raw `ProtocolEvent` namespace access (e.g., to interleave with channels not exposed as a typed projection), iterate the run object directly:

```python
stream = graph.stream_events(inputs, config=config, version="v3")

for event in stream:
    namespace = event["params"]["namespace"]  # list[str]
    method = event["method"]
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

Print a tree-structured view using `subgraph.path`:

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
