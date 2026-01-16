# Customize Agent Memory

Extend `AgentState` to add custom fields to short-term memory.

```python
# casts.{cast_name}.modules.state
from langchain.agents import AgentState

class CustomAgentState(AgentState):
    user_id: str
    preferences: dict
```

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from .state import CustomAgentState

def set_custom_state_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[...],
        state_schema=CustomAgentState,
        checkpointer=InMemorySaver(),
    )
```

```python
# casts.{cast_name}.modules.nodes
from casts.base_node import BaseNode
from .agents import set_custom_state_agent

class CustomStateNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.agent = set_custom_state_agent()

    def execute(self, state, config):
        thread_id = self.get_thread_id(config) or "default"
        result = self.agent.invoke(
            {
                "messages": [{"role": "user", "content": state["query"]}],
                "user_id": "user_123",
                "preferences": {"theme": "dark"},
            },
            {"configurable": {"thread_id": thread_id}},
        )
        return {"messages": result["messages"]}
```
