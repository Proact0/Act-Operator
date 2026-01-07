# Access Long-Term Memory in Tools

## Read from Store

```python
# casts.{cast_name}.modules.tools
from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime

@dataclass
class Context:
    user_id: str

@tool
def get_user_info(runtime: ToolRuntime[Context]) -> str:
    """Look up user info from long-term memory."""
    store = runtime.store
    user_id = runtime.context.user_id
    user_info = store.get(("users",), user_id)
    return str(user_info.value) if user_info else "Unknown user"
```

## Write to Store

```python
# casts.{cast_name}.modules.tools
from dataclasses import dataclass
from typing_extensions import TypedDict
from langchain.tools import tool, ToolRuntime

@dataclass
class Context:
    user_id: str

class UserInfo(TypedDict):
    name: str

@tool
def save_user_info(user_info: UserInfo, runtime: ToolRuntime[Context]) -> str:
    """Save user info to long-term memory."""
    store = runtime.store
    user_id = runtime.context.user_id
    store.put(("users",), user_id, user_info)
    return "Successfully saved user info."
```

## Agent Setup

```python
# casts.{cast_name}.modules.agents
from dataclasses import dataclass
from langchain.agents import create_agent
from langgraph.store.memory import InMemoryStore
from .tools import get_user_info, save_user_info

@dataclass
class Context:
    user_id: str

store = InMemoryStore()

# Pre-populate data (optional)
store.put(("users",), "user_123", {"name": "John Smith", "language": "English"})

def set_memory_store_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[get_user_info, save_user_info],
        store=store,
        context_schema=Context,
    )
```

## Node Usage

```python
# casts.{cast_name}.modules.nodes
from casts.base_node import BaseNode
from .agents import set_memory_store_agent, Context

class LongTermMemoryNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.agent = set_memory_store_agent()

    def execute(self, state):
        result = self.agent.invoke(
            {"messages": [{"role": "user", "content": state["query"]}]},
            context=Context(user_id="user_123"),
        )
        return {"messages": result["messages"]}
```
