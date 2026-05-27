# Agent & DeepAgent Streaming

`create_agent` and `create_deep_agent` are `CompiledStateGraph` instances — they appear on `stream.subgraphs`. Deep Agent **delegated task calls** additionally surface on `stream.subagents`.

Code blocks below show explicit file paths for reserved locations: agent definitions live in `casts/{cast_name}/modules/agents.py`, graph wiring lives in `casts/{cast_name}/graph.py`. Stream consumption code is **consumer-side** — place it anywhere outside those reserved locations (additional cast module, external runtime/API module, script, test).

## Contents

- Topology Variants
- Stream Consumption (create_agent / create_deep_agent)
- Stream Consumption (create_deep_agent with subagents)
- Subagent Handle Fields
- Subagents vs Subgraphs

## Topology Variants

Two ways to embed an agent in a parent graph:

### A. As a node (compiled agent directly)

```python
# casts/{cast_name}/modules/agents.py — agent definitions
from langchain.agents import create_agent
from deepagents import create_deep_agent

def set_search_agent():
    return create_agent(model="...", tools=[search_tool], name="search_agent")

def set_deep_agent():
    agent = create_deep_agent(model="...", tools=[search_tool])
    agent.name = "deep_agent"
    return agent
```

```python
# casts/{cast_name}/graph.py — wire agents as subgraph nodes
from .modules.agents import set_search_agent, set_deep_agent

builder.add_node("agent", set_search_agent())
builder.add_node("deep_agent", set_deep_agent())
```

### B. Invoked inside a custom node

```python
# casts/{cast_name}/modules/nodes.py
from casts.base_node import AsyncBaseNode

class AgentNode(AsyncBaseNode):
    def __init__(self):
        super().__init__()
        self.agent = set_sample_agent()  # create_agent(..., name="search_agent")

    async def execute(self, state, config):
        # config propagation is critical for streaming
        result = await self.agent.ainvoke({"messages": state["messages"]}, config)
        return {"messages": result["messages"]}
```

> **Key:** When invoking an agent inside a node, pass `config` to `ainvoke()` so the streaming callback chain propagates. Without it, inner LLM tokens are not captured.

Both topologies surface on `stream.subgraphs` with the same `graph_name`. Pick the topology based on whether you need custom pre/post-processing around the agent (B) or a clean black-box subgraph (A).

---

## Stream Consumption (create_agent / create_deep_agent)

For both topology A and B, filter by `graph_name`:

```python
stream = await graph.astream_events(inputs, config=config, version="v3")

async for subgraph in stream.subgraphs:
    if subgraph.graph_name != "search_agent":
        continue
    async for message in subgraph.messages:
        async for token in message.text:
            print(f"[{subgraph.graph_name}] {token}", end="")
```

---

## Stream Consumption (create_deep_agent with subagents)

When `create_deep_agent` has `subagents=[...]`, each delegated task call appears on `stream.subagents`. Use this projection for user-facing UI — it hides internal graph nodes and exposes only the delegated-task concept.

```python
# casts/{cast_name}/modules/agents.py — deep agent + subagent definitions
from deepagents import create_deep_agent

def set_orchestrator_agent():
    agent = create_deep_agent(
        model="anthropic:claude-sonnet-4-5-20250929",
        tools=[search_tool],
        subagents=[
            {
                "name": "researcher",
                "description": "Research specialist",
                "system_prompt": "You are a researcher.",
                "tools": [web_search],
            },
            {
                "name": "writer",
                "description": "Report writer",
                "system_prompt": "You write reports.",
                "tools": [],
            },
        ],
    )
    agent.name = "orchestrator"
    return agent
```

```python
# casts/{cast_name}/graph.py — wire as subgraph node
from .modules.agents import set_orchestrator_agent

builder.add_node("orchestrator", set_orchestrator_agent())
```

Consume coordinator and subagent messages concurrently:

```python
import asyncio

stream = await graph.astream_events(inputs, config=config, version="v3")

async def consume_coordinator():
    async for message in stream.messages:
        async for token in message.text:
            print(f"[coordinator] {token}", end="")

async def consume_subagents():
    async for subagent in stream.subagents:
        async for message in subagent.messages:
            async for token in message.text:
                print(f"[{subagent.name}] {token}", end="")

await asyncio.gather(consume_coordinator(), consume_subagents())
```

---

## Subagent Handle Fields

Each handle in `stream.subagents` exposes:

| Field | Description |
|-------|-------------|
| `subagent.name` | Subagent name (`"researcher"`, `"writer"`, ...) |
| `subagent.path` | Namespace path |
| `subagent.status` | Lifecycle (`started`, `completed`, `failed`, `interrupted`) |
| `subagent.messages` | Subagent's chat-model messages |
| `subagent.tool_calls` | Tool calls within the subagent |
| `subagent.values` | Subagent state snapshots |
| `subagent.subagents` | Nested subagent delegations |
| `subagent.output` | Final subagent state / delegated-task result |

---

## Subagents vs Subgraphs

| Projection | Shows | Use For |
|------------|-------|---------|
| `stream.subgraphs` | Every nested `CompiledStateGraph` execution | Generic graph nesting (`create_agent`, plain subgraphs) |
| `stream.subagents` | Deep Agents delegated task calls only | User-facing UI; hides internal graph nodes |

For Deep Agents with subagent delegation, prefer `stream.subagents`. Use `stream.subgraphs` when working with plain `create_agent` or custom subgraphs.
