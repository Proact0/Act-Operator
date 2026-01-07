# Agent Configuration

Agents combine LLMs with tools using the ReAct (Reasoning + Acting) pattern. `create_agent` executes a loop: input → model reasoning → tool execution → observation → final output.

## Contents

- Basic Structure
- Module Separation Pattern
- Model Configuration (Static, Dynamic)
- System Prompt (Static, Dynamic)
- State Extension (state_schema, middleware.state_schema)
- Key Constraints

## Basic Structure

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent

def set_sample_agent():
    return create_agent(
        model=...,           # Required: model instance
        tools=[...],         # Optional: list of tools
        middleware=[...],    # Optional: list of middleware
        system_prompt=...,   # Optional: system prompt
        response_format=..., # Optional: structured output strategy
        state_schema=...,    # Optional: custom state schema
        context_schema=...,  # Optional: runtime context schema
    )
```

## Module Separation Pattern

Separate components into modules when implementing agents:

```python
# casts.{cast_name}.modules.models
from langchain_openai import ChatOpenAI

def get_sample_model():
    return ChatOpenAI(model="gpt-4o", temperature=0.1)
```

```python
# casts.{cast_name}.modules.tools
from langchain.tools import tool

@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"
```

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from .models import get_sample_model
from .tools import search

def set_sample_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[search],
        system_prompt="You are a helpful assistant."
    )
```

```python
# casts.{cast_name}.modules.nodes
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

## Model Configuration

### Static Model

Use a model instance.

```python
# casts.{cast_name}.modules.models
from langchain_openai import ChatOpenAI

def get_basic_model():
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.1,
        max_tokens=1000,
        timeout=30
    )
```

### Dynamic Model

Use `@wrap_model_call` middleware to select model at runtime.

```python
# casts.{cast_name}.modules.middlewares
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from .models import get_basic_model, get_advanced_model

@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler) -> ModelResponse:
    """Select model based on conversation length."""
    message_count = len(request.state["messages"])
    model = get_advanced_model() if message_count > 10 else get_basic_model()
    return handler(request.override(model=model))
```

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from .models import get_basic_model
from .middlewares import dynamic_model_selection

def set_dynamic_agent():
    return create_agent(
        model=get_basic_model(),  # Default model
        tools=[...],
        middleware=[dynamic_model_selection]
    )
```

## System Prompt

### Static Prompt

```python
# casts.{cast_name}.modules.agents
def set_agent_with_prompt():
    return create_agent(
        model=get_sample_model(),
        tools=[...],
        system_prompt="You are a helpful assistant. Be concise and accurate."
    )
```

### Dynamic Prompt

Use `@dynamic_prompt` middleware to change prompt based on runtime context.

```python
# casts.{cast_name}.modules.middlewares
from langchain.agents.middleware import dynamic_prompt, ModelRequest

@dynamic_prompt
def user_role_prompt(request: ModelRequest) -> str:
    """Generate prompt based on user role."""
    user_role = request.runtime.context.get("user_role", "user")
    base = "You are a helpful assistant."
    
    if user_role == "expert":
        return f"{base} Provide detailed technical responses."
    elif user_role == "beginner":
        return f"{base} Explain concepts simply."
    return base
```

```python
# casts.{cast_name}.modules.agents
from typing import TypedDict
from langchain.agents import create_agent
from .middlewares import user_role_prompt

class Context(TypedDict):
    user_role: str

def set_dynamic_prompt_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[...],
        middleware=[user_role_prompt],
        context_schema=Context
    )
```

```python
# casts.{cast_name}.modules.nodes
class DynamicPromptNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.agent = set_dynamic_prompt_agent()

    def execute(self, state):
        result = self.agent.invoke(
            {"messages": [{"role": "user", "content": state["query"]}]},
            context={"user_role": "expert"}  # Runtime context
        )
        return {"messages": result["messages"]}
```

## State Extension

Two ways to add custom state to agents:

### Using state_schema

When custom state is only used in tools:

```python
# casts.{cast_name}.modules.agents
from langchain.agents import AgentState

class CustomState(AgentState):  # TypedDict-based
    user_preferences: dict

def set_stateful_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[...],
        state_schema=CustomState
    )
```

### Using middleware.state_schema (Recommended)

When custom state is used in middleware and tools:

```python
# casts.{cast_name}.modules.middlewares
from typing import Any
from langchain.agents import AgentState
from langchain.agents.middleware import AgentMiddleware

class CustomState(AgentState):
    user_preferences: dict

class PreferencesMiddleware(AgentMiddleware):
    state_schema = CustomState
    
    def before_model(self, state: CustomState, runtime) -> dict[str, Any] | None:
        # State-based preprocessing
        ...
```

```python
# casts.{cast_name}.modules.agents
from .middlewares import PreferencesMiddleware

def set_middleware_stateful_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[...],
        middleware=[PreferencesMiddleware()]
    )
```

Passing custom state on invocation:

```python
# casts.{cast_name}.modules.nodes
class StatefulNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.agent = set_stateful_agent()

    def execute(self, state):
        result = self.agent.invoke({
            "messages": [{"role": "user", "content": state["query"]}],
            "user_preferences": {"style": "technical"}
        })
        return {"messages": result["messages"]}
```

## Key Constraints

- Direct schema passing to `response_format` not supported → Must use `ToolStrategy` or `ProviderStrategy`
- Cannot use pre-bound models (`bind_tools`) with structured output in dynamic model selection
