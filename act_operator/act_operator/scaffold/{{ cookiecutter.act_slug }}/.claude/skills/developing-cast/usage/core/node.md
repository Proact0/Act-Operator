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

## Node with Agent

```python
# casts/{cast_name}/modules/nodes.py
from casts.base_node import BaseNode
from .agents import set_sample_agent

class AgentNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.agent = set_sample_agent()

    def execute(self, state):
        result = self.agent.invoke({
            "messages": [{"role": "user", "content": state["query"]}]
        })
        return {"messages": result["messages"]}
```

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
