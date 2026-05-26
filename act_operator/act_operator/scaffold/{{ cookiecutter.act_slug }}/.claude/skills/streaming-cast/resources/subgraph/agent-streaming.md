# Agent & DeepAgent Streaming

Stream through `create_agent` and `create_deep_agent` that run as subgraphs within a parent graph. Use `stream.subgraphs` for nested agents and `stream.subagents` for Deep Agent task delegations.

## Contents

- Graph Topology Patterns
- create_agent as Node Subgraph
- create_agent Inside a Node
- create_deep_agent as Node Subgraph
- create_deep_agent Inside a Node
- create_deep_agent with Subagents (stream.subagents)
- Subagents vs Subgraphs

## Graph Topology Patterns

Agents compiled by `create_agent` and `create_deep_agent` are `CompiledStateGraph` instances — they are subgraphs. When added to a parent graph, they appear on `stream.subgraphs`. Deep Agent task delegations additionally appear on `stream.subagents`.

```
Pattern 1: graph → create_agent (node = subgraph)
Pattern 2: graph → node containing create_agent (node invokes subgraph internally)
Pattern 3: graph → create_deep_agent (node = subgraph)
Pattern 4: graph → node containing create_deep_agent (node invokes subgraph internally)
Pattern 5: graph → create_deep_agent → subagent (delegated subagent on stream.subagents)
Pattern 6: graph → node containing create_deep_agent → subagent (delegated subagent on stream.subagents)
```

---

## create_agent as Node Subgraph

When `create_agent` is added directly as a node, it runs as a subgraph. Pass `name=` for filtering:

```python
# casts/{cast_name}/graph.py
from langgraph.graph import StateGraph, START, END
from langchain.agents import create_agent
from casts.base_graph import BaseGraph

class AgentGraph(BaseGraph):
    def build(self):
        agent = create_agent(
            model="anthropic:claude-sonnet-4-5-20250929",
            tools=[search_tool],
            name="search_agent",
        )

        builder = StateGraph(State)
        builder.add_node("preprocess", PreprocessNode())
        builder.add_node("agent", agent)  # subgraph node
        builder.add_node("postprocess", PostprocessNode())

        builder.add_edge(START, "preprocess")
        builder.add_edge("preprocess", "agent")
        builder.add_edge("agent", "postprocess")
        builder.add_edge("postprocess", END)

        graph = builder.compile()
        graph.name = self.name
        return graph
```

Stream consumption:

```python
graph = agent_graph()

stream = await graph.astream_events(inputs, config=config, version="v3")

async for subgraph in stream.subgraphs:
    if subgraph.graph_name != "search_agent":
        continue
    async for message in subgraph.messages:
        async for token in message.text:
            print(f"[search_agent] {token}", end="")
```

---

## create_agent Inside a Node

When a node internally invokes a `create_agent` graph, the agent still surfaces on `stream.subgraphs` — pass `config` to `ainvoke()` for streaming propagation:

```python
# casts/{cast_name}/modules/nodes.py
from casts.base_node import AsyncBaseNode
from .agents import set_sample_agent

class AgentNode(AsyncBaseNode):
    def __init__(self):
        super().__init__()
        self.agent = set_sample_agent()  # create_agent(..., name="search_agent")

    async def execute(self, state, config):
        # invoke propagates streaming context automatically
        result = await self.agent.ainvoke(
            {"messages": state["messages"]}, config
        )
        return {"messages": result["messages"]}
```

> **Key:** Pass `config` to `ainvoke()` so the streaming callback chain propagates. Without config propagation, the agent's inner LLM tokens are not captured.

Stream consumption is identical — filter on the agent's `name`:

```python
stream = await graph.astream_events(inputs, config=config, version="v3")

async for subgraph in stream.subgraphs:
    if subgraph.graph_name == "search_agent":
        async for message in subgraph.messages:
            async for token in message.text:
                print(token, end="")
```

---

## create_deep_agent as Node Subgraph

`create_deep_agent` returns a `CompiledStateGraph`. Add it as a node and assign a name:

```python
# casts/{cast_name}/graph.py
from deepagents import create_deep_agent

class DeepAgentGraph(BaseGraph):
    def build(self):
        deep_agent = create_deep_agent(
            model="anthropic:claude-sonnet-4-5-20250929",
            tools=[search_tool],
            system_prompt="You are a research assistant.",
        )
        deep_agent.name = "deep_agent"

        builder = StateGraph(State)
        builder.add_node("deep_agent", deep_agent)  # subgraph node
        builder.add_edge(START, "deep_agent")
        builder.add_edge("deep_agent", END)

        graph = builder.compile()
        graph.name = self.name
        return graph
```

Stream consumption via `stream.subgraphs`:

```python
graph = deep_agent_graph()

stream = await graph.astream_events(inputs, config=config, version="v3")

async for subgraph in stream.subgraphs:
    if subgraph.graph_name != "deep_agent":
        continue
    async for message in subgraph.messages:
        async for token in message.text:
            print(f"[deep_agent] {token}", end="")
```

---

## create_deep_agent Inside a Node

When a node internally invokes a `create_deep_agent` graph, streaming works the same way as `create_agent` inside a node — pass `config` to propagate the streaming callback chain.

```python
# casts/{cast_name}/modules/nodes.py
from casts.base_node import AsyncBaseNode
from .agents import set_deep_agent

class DeepAgentNode(AsyncBaseNode):
    def __init__(self):
        super().__init__()
        self.agent = set_deep_agent()  # create_deep_agent with name set

    async def execute(self, state, config):
        result = await self.agent.ainvoke(
            {"messages": state["messages"]}, config
        )
        return {"messages": result["messages"]}
```

> **Key:** Pass `config` to `ainvoke()` so the streaming callback chain propagates.

---

## create_deep_agent with Subagents (stream.subagents)

Deep Agents add a `stream.subagents` projection on top of `stream.subgraphs`. It exposes one handle per **delegated task call** (not every internal node), making it the right projection for user-facing UI.

```python
from deepagents import create_deep_agent

class OrchestratorGraph(BaseGraph):
    def build(self):
        deep_agent = create_deep_agent(
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
        deep_agent.name = "orchestrator"

        builder = StateGraph(State)
        builder.add_node("orchestrator", deep_agent)
        builder.add_edge(START, "orchestrator")
        builder.add_edge("orchestrator", END)

        graph = builder.compile()
        graph.name = self.name
        return graph
```

Stream with subagent source separation:

```python
graph = orchestrator_graph()

stream = await graph.astream_events(inputs, config=config, version="v3")

# Coordinator messages (top-level model calls of the deep agent)
async def consume_coordinator():
    async for message in stream.messages:
        async for token in message.text:
            print(f"[coordinator] {token}", end="")

# Delegated subagent messages
async def consume_subagents():
    async for subagent in stream.subagents:
        async for message in subagent.messages:
            async for token in message.text:
                print(f"[{subagent.name}] {token}", end="")

await asyncio.gather(consume_coordinator(), consume_subagents())
```

### Subagent Handle Fields

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
| `stream.subgraphs` | Every nested `CompiledStateGraph` execution | Generic graph nesting (agents, plain subgraphs) |
| `stream.subagents` | Product-level Deep Agents task delegations only | User-facing UI; hides internal graph nodes |

For Deep Agents with subagent delegation, prefer `stream.subagents` because it filters out internal graph nodes and exposes the delegated-task concept directly. Use `stream.subgraphs` when working with plain `create_agent` or custom subgraphs.
