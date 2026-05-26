# Node Implementation

Nodes are implemented in `casts/{cast_name}/modules/nodes.py` by extending `BaseNode` (sync) or `AsyncBaseNode` (async).

## Contents

- Import
- execute() Signatures
- Sync Node
- Async Node
- Using config
- Using runtime
- verbose Mode
- Helper Methods
- Node with Agent
- Node Timeouts (langgraph v1.2+)
- Node Error Handlers (langgraph v1.2+)
- Graceful Drain Inside Nodes (langgraph v1.2+)
- Recursion Handling

## Import

```python
# casts/{cast_name}/modules/nodes.py
from casts.base_node import BaseNode, AsyncBaseNode
```

## execute() Signatures

Subclasses **must** implement `execute()`. The `state` parameter is required; `config` and `runtime` are optional:

```python
def execute(self, state): ...
def execute(self, state, config): ...
def execute(self, state, runtime): ...
def execute(self, state, config, runtime): ...
```

**Rules:**
- Must return a `dict` (state updates)
- Only `config` and `runtime` are allowed as optional parameters

---

## Sync Node

```python
# casts/{cast_name}/modules/nodes.py
from casts.base_node import BaseNode

class ProcessNode(BaseNode):
    def __init__(self):
        super().__init__()

    def execute(self, state):
        result = process_data(state["input"])
        return {"output": result}
```

## Async Node

```python
# casts/{cast_name}/modules/nodes.py
from casts.base_node import AsyncBaseNode

class FetchNode(AsyncBaseNode):
    def __init__(self):
        super().__init__()

    async def execute(self, state):
        data = await fetch_external_api(state["url"])
        return {"data": data}
```

---

## Using config

Access `thread_id`, `tags`, `metadata`:

```python
# casts/{cast_name}/modules/nodes.py
from langchain_core.runnables import RunnableConfig
from casts.base_node import BaseNode

class ConfigAwareNode(BaseNode):
    def execute(self, state, config: RunnableConfig):
        thread_id = self.get_thread_id(config)  # helper method
        tags = self.get_tags(config)            # helper method
        step = config["metadata"]["langgraph_step"]
        return {"thread_id": thread_id, "step": step}
```

## Using runtime

Access `context`, `store`, `stream_writer`:

```python
# casts/{cast_name}/modules/nodes.py
from langgraph.runtime import Runtime
from casts.base_node import BaseNode

class RuntimeNode(BaseNode):
    def execute(self, state, runtime: Runtime):
        user_id = runtime.context.user_id
        store = runtime.store
        return {"user_id": user_id}
```

---

## verbose Mode

Enable debug logging:

```python
# casts/{cast_name}/modules/nodes.py
from casts.base_node import BaseNode

class DebugNode(BaseNode):
    def __init__(self):
        super().__init__(verbose=True)

    def execute(self, state):
        self.log("Processing", input=state.get("input"))
        return {"done": True}
```

---

## Helper Methods

| Method | Description |
|--------|-------------|
| `self.log(msg, **ctx)` | Debug log (verbose only) |
| `self.get_thread_id(config)` | Extract thread_id from config |
| `self.get_tags(config)` | Extract tags list from config |

---

## Node with Agent (Call Inside Node)

Invoke a `create_agent` subgraph inside a custom node. Use this when the parent and subgraph have **different state schemas** or when custom pre/post-processing is needed around the agent call.

For adding a compiled agent **directly as a graph node** (shared state), see subgraph.md § "Method 2: Add as Node".

```python
# casts/{cast_name}/modules/nodes.py
from casts.base_node import BaseNode
from .agents import set_sample_agent

class AgentNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.agent = set_sample_agent()

    def execute(self, state):
        # Transform parent state → agent input
        result = self.agent.invoke({
            "messages": [{"role": "user", "content": state["query"]}]
        })
        # Transform agent output → parent state update
        return {"messages": result["messages"]}
```

---

## Node Timeouts (langgraph v1.2+)

Cap how long a single async attempt may run. **Async nodes only** — sync nodes raise at compile time.

Pass `timeout=` to `add_node`. Either pass seconds / `datetime.timedelta` for a wall-clock limit, or a `TimeoutPolicy` for fine-grained control:

```python
# casts/{cast_name}/graph.py
from datetime import timedelta
from langgraph.types import TimeoutPolicy

builder.add_node("fetch", FetchNode(), timeout=30)                  # 30s wall-clock
builder.add_node("fetch", FetchNode(), timeout=timedelta(minutes=2))

builder.add_node(
    "fetch",
    FetchNode(),
    timeout=TimeoutPolicy(
        run_timeout=120,     # hard wall-clock limit (seconds)
        idle_timeout=20,     # resets on each progress signal
    ),
)
```

### Behavior

- On timeout, LangGraph raises `NodeTimeoutError` (subclass of `TimeoutError`).
- Buffered writes from the timed-out attempt are cleared — no state leakage.
- If the node has a `retry_policy` that retries `TimeoutError`/`NodeTimeoutError`, it retries with the timer reset per attempt.

### NodeTimeoutError fields

| Attribute | Type | Description |
|-----------|------|-------------|
| `node` | `str` | Name of the node that timed out |
| `elapsed` | `float` | Seconds before timeout fired |
| `kind` | `Literal["idle", "run"]` | Which timer fired |
| `idle_timeout` | `float \| None` | Configured idle timeout |
| `run_timeout` | `float \| None` | Configured run timeout |

### Idle timeout refresh

When using `idle_timeout`, signal progress from inside the node to reset the timer:

```python
# casts/{cast_name}/modules/nodes.py
from langgraph.runtime import Runtime
from casts.base_node import AsyncBaseNode

class StreamingNode(AsyncBaseNode):
    async def execute(self, state, runtime: Runtime):
        async for chunk in long_stream():
            await process_chunk(chunk)
            runtime.heartbeat()  # resets idle_timeout
        return {"result": "done"}
```

---

## Node Error Handlers (langgraph v1.2+)

Run a recovery function **after all retries are exhausted** to update state and route to a compensation branch. Useful for Saga / compensation patterns.

Pass `error_handler=` to `add_node`:

```python
# casts/{cast_name}/modules/nodes.py
from langgraph.errors import NodeError
from langgraph.types import Command, RetryPolicy

def payment_error_handler(state: State, error: NodeError) -> Command:
    return Command(
        update={"status": f"compensated: {error.error}"},
        goto="finalize",
    )
```

```python
# casts/{cast_name}/graph.py
builder.add_node(
    "charge_payment",
    ChargePaymentNode(),
    retry_policy=RetryPolicy(max_attempts=3, retry_on=ConnectionError),
    error_handler=payment_error_handler,
)
```

The handler receives a typed `NodeError` and returns a `Command` to update state and route execution.

---

## Graceful Drain Inside Nodes (langgraph v1.2+)

When a graceful shutdown is requested (see graph.md § "Graceful Shutdown"), nodes can read drain state from `runtime.drain_requested` and skip expensive work before the next superstep boundary:

```python
# casts/{cast_name}/modules/nodes.py
from langgraph.runtime import Runtime
from casts.base_node import AsyncBaseNode

class ExpensiveNode(AsyncBaseNode):
    async def execute(self, state, runtime: Runtime):
        if runtime.drain_requested:
            # Skip the heavy work — return early so the run can drain
            return {"status": f"skipped: {runtime.drain_reason}"}

        result = await expensive_operation(state)
        return {"result": result}
```

| Property | Type | Description |
|----------|------|-------------|
| `runtime.drain_requested` | `bool` | True if `RunControl.request_drain()` was called |
| `runtime.drain_reason` | `str \| None` | Reason passed to `request_drain()`, or `None` |

---

## Recursion Handling

Check step counter to handle limits proactively:

```python
# casts/{cast_name}/modules/nodes.py
from casts.base_node import BaseNode

class SafeNode(BaseNode):
    def execute(self, state, config):
        step = config["metadata"]["langgraph_step"]
        limit = config["recursion_limit"]  # default: 25

        if step >= limit * 0.8:
            return {"route_to": "fallback"}
        return {"result": "ok"}
```
