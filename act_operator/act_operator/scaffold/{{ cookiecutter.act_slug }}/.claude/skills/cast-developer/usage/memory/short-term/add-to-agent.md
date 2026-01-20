# Add Short-Term Memory to Agent

Short-term memory enables thread-level persistence within a single conversation.

## Enable with Checkpointer

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from .models import get_sample_model

def set_memory_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[...],
        checkpointer=InMemorySaver(),
    )
```

## Invoke with Thread ID

```python
# casts.{cast_name}.modules.nodes
from casts.base_node import BaseNode
from .agents import set_memory_agent

class MemoryNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.agent = set_memory_agent()

    def execute(self, state, config):
        thread_id = self.get_thread_id(config) or "default"
        result = self.agent.invoke(
            {"messages": [{"role": "user", "content": state["query"]}]},
            {"configurable": {"thread_id": thread_id}},
        )
        return {"messages": result["messages"]}
```

## Production Checkpointer

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from langgraph.checkpoint.postgres import PostgresSaver

DB_URI = "postgresql://user:pass@localhost:5432/db"

def set_production_memory_agent():
    with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
        checkpointer.setup()  # Auto create tables
        return create_agent(
            model=get_sample_model(),
            tools=[...],
            checkpointer=checkpointer,
        )
```
