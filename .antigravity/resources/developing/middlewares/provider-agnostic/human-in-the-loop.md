# Human-in-the-Loop

Pause execution for human approval before sensitive tool calls.

## Basic Usage

```python
# casts.{cast_name}.modules.middlewares
from langchain.agents.middleware import HumanInTheLoopMiddleware

def get_hitl_middleware():
    return HumanInTheLoopMiddleware(
        interrupt_on={
            "send_email": True,                                    # All decisions allowed
            "execute_sql": {"allowed_decisions": ["approve", "reject"]},  # No editing
            "read_data": False,                                    # Auto-approve
        },
        description_prefix="Tool execution pending approval",
    )
```

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from .middlewares import get_hitl_middleware

def set_hitl_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[...],
        middleware=[get_hitl_middleware()],
        checkpointer=InMemorySaver(),  # Required for HITL
    )
```

## Decision Types

| Type | Description |
|------|-------------|
| `approve` | Execute tool call as-is |
| `edit` | Modify arguments before execution |
| `reject` | Reject with feedback message |

## Invoking with HITL

```python
# casts.{cast_name}.modules.nodes
from langgraph.types import Command
from casts.base_node import BaseNode
from .agents import set_hitl_agent

class HITLNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.agent = set_hitl_agent()

    def execute(self, state, config):
        thread_id = self.get_thread_id(config) or "default"
        agent_config = {"configurable": {"thread_id": thread_id}}
        
        result = self.agent.invoke(
            {"messages": [{"role": "user", "content": state["query"]}]},
            config=agent_config
        )
        
        # Check for interrupt
        if "__interrupt__" in result:
            # Return interrupt info for external handling
            return {"interrupt": result["__interrupt__"]}
        
        return {"messages": result["messages"]}
```

## Resuming After Interrupt

```python
from langgraph.types import Command

# Approve
agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), config=config)

# Edit
agent.invoke(
    Command(resume={"decisions": [{
        "type": "edit",
        "edited_action": {"name": "tool_name", "args": {"param": "new_value"}}
    }]}),
    config=config
)

# Reject
agent.invoke(
    Command(resume={"decisions": [{"type": "reject", "message": "Reason for rejection"}]}),
    config=config
)
```
