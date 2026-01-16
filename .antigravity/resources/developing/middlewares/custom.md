# Custom Middleware

Build custom middleware by implementing hooks that run at specific points in the agent execution flow.

## Contents

- Hook Types
- Basic Class Structure
- Node-style Hooks (Message Limit Example)
- Wrap-style Hooks (Retry, Tool Monitoring)
- Custom State Schema
- Agent Jumps
- Dynamic Model Selection
- Dynamic Tool Selection
- System Message Modification
- Execution Order
- Best Practices

## Hook Types

| Type | Hooks | Description |
|------|-------|-------------|
| **Node-style** | `before_agent`, `before_model`, `after_model`, `after_agent` | Run sequentially at execution points |
| **Wrap-style** | `wrap_model_call`, `wrap_tool_call` | Run around each model/tool call |

## Basic Class Structure

```python
# casts.{cast_name}.modules.middlewares
from typing import Any, Callable
from langchain.agents.middleware import AgentMiddleware, AgentState, ModelRequest, ModelResponse, hook_config
from langgraph.runtime import Runtime

class CustomMiddleware(AgentMiddleware):
    def __init__(self, config_value: int = 10):
        super().__init__()
        self.config_value = config_value

    # Node-style hooks
    def before_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        """Once per invocation, before agent starts."""
        return None

    def before_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        """Before each model call."""
        return None

    def after_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        """After each model response."""
        return None

    def after_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        """Once per invocation, after agent completes."""
        return None

    # Wrap-style hooks
    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """Around each model call."""
        return handler(request)

    def wrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
    ) -> ToolMessage | Command:
        """Around each tool call."""
        return handler(request)
```

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from .middlewares import CustomMiddleware

def set_agent_with_custom_middleware():
    return create_agent(
        model=get_sample_model(),
        tools=[...],
        middleware=[CustomMiddleware(config_value=20)],
    )
```

---

## Node-style Hooks

### Message Limit Example

```python
# casts.{cast_name}.modules.middlewares
from typing import Any
from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langchain.messages import AIMessage
from langgraph.runtime import Runtime

class MessageLimitMiddleware(AgentMiddleware):
    def __init__(self, max_messages: int = 50):
        super().__init__()
        self.max_messages = max_messages

    @hook_config(can_jump_to=["end"])
    def before_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        if len(state["messages"]) >= self.max_messages:
            return {
                "messages": [AIMessage("Conversation limit reached.")],
                "jump_to": "end"
            }
        return None

    def after_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        print(f"Model returned: {state['messages'][-1].content}")
        return None
```

---

## Wrap-style Hooks

### Retry Example

```python
# casts.{cast_name}.modules.middlewares
from typing import Callable
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse

class RetryMiddleware(AgentMiddleware):
    def __init__(self, max_retries: int = 3):
        super().__init__()
        self.max_retries = max_retries

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        for attempt in range(self.max_retries):
            try:
                return handler(request)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                print(f"Retry {attempt + 1}/{self.max_retries}: {e}")
```

### Tool Monitoring Example

```python
# casts.{cast_name}.modules.middlewares
from typing import Callable
from langchain.agents.middleware import AgentMiddleware
from langchain.tools.tool_node import ToolCallRequest
from langchain.messages import ToolMessage
from langgraph.types import Command

class ToolMonitoringMiddleware(AgentMiddleware):
    def wrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
    ) -> ToolMessage | Command:
        print(f"Tool: {request.tool_call['name']}, Args: {request.tool_call['args']}")
        try:
            result = handler(request)
            print("Tool completed")
            return result
        except Exception as e:
            print(f"Tool failed: {e}")
            raise
```

---

## Custom State Schema

Extend agent state with custom properties.

```python
# casts.{cast_name}.modules.middlewares
from typing import Any
from typing_extensions import NotRequired
from langchain.agents.middleware import AgentMiddleware, AgentState

class CustomState(AgentState):
    model_call_count: NotRequired[int]
    user_id: NotRequired[str]

class CallCounterMiddleware(AgentMiddleware[CustomState]):
    state_schema = CustomState

    def before_model(self, state: CustomState, runtime) -> dict[str, Any] | None:
        if state.get("model_call_count", 0) > 10:
            return {"jump_to": "end"}
        return None

    def after_model(self, state: CustomState, runtime) -> dict[str, Any] | None:
        return {"model_call_count": state.get("model_call_count", 0) + 1}
```

```python
# casts.{cast_name}.modules.nodes
from casts.base_node import BaseNode
from langchain.messages import HumanMessage
from .agents import set_agent_with_counter

class CounterNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.agent = set_agent_with_counter()

    def execute(self, state):
        result = self.agent.invoke({
            "messages": [HumanMessage(state["query"])],
            "model_call_count": 0,
            "user_id": "user-123",
        })
        return {"messages": result["messages"]}
```

---

## Agent Jumps

Return `jump_to` to exit early. Requires `@hook_config(can_jump_to=[...])`.

| Target | Description |
|--------|-------------|
| `"end"` | End agent execution |
| `"tools"` | Jump to tools node |
| `"model"` | Jump to model node |

```python
# casts.{cast_name}.modules.middlewares
from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langchain.messages import AIMessage

class BlockedContentMiddleware(AgentMiddleware):
    @hook_config(can_jump_to=["end"])
    def after_model(self, state: AgentState, runtime) -> dict[str, Any] | None:
        if "BLOCKED" in state["messages"][-1].content:
            return {
                "messages": [AIMessage("Cannot respond to that request.")],
                "jump_to": "end"
            }
        return None
```

---

## Dynamic Model Selection

```python
# casts.{cast_name}.modules.middlewares
from typing import Callable
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain.chat_models import init_chat_model

class DynamicModelMiddleware(AgentMiddleware):
    def __init__(self):
        super().__init__()
        self.complex_model = init_chat_model("gpt-4o")
        self.simple_model = init_chat_model("gpt-4o-mini")

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        model = self.complex_model if len(request.messages) > 10 else self.simple_model
        return handler(request.override(model=model))
```

---

## Dynamic Tool Selection

```python
# casts.{cast_name}.modules.middlewares
from typing import Callable
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse

class ToolSelectorMiddleware(AgentMiddleware):
    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        relevant_tools = self._select_tools(request.state, request.runtime)
        return handler(request.override(tools=relevant_tools))

    def _select_tools(self, state, runtime):
        # Implement tool selection logic
        return [...]
```

---

## System Message Modification

```python
# casts.{cast_name}.modules.middlewares
from typing import Callable
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain.messages import SystemMessage

class ContextMiddleware(AgentMiddleware):
    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        new_content = list(request.system_message.content_blocks) + [
            {"type": "text", "text": "Additional context."}
        ]
        new_system_message = SystemMessage(content=new_content)
        return handler(request.override(system_message=new_system_message))
```

---

## Execution Order

```python
middleware=[middleware1, middleware2, middleware3]
```

| Phase | Order |
|-------|-------|
| `before_*` | 1 → 2 → 3 (first to last) |
| `wrap_*` | 1 wraps 2 wraps 3 wraps call |
| `after_*` | 3 → 2 → 1 (last to first) |

---

## Best Practices

1. Keep middleware focused on single responsibility
2. Handle errors gracefully
3. Use node-style for logging/validation, wrap-style for retry/caching
4. Document custom state properties
5. Test middleware independently
6. Place critical middleware first in list
