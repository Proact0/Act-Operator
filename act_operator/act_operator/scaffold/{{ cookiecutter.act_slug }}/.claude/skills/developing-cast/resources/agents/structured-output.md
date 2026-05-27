# Agent Structured Output

Return structured data from agents in predictable formats using Pydantic models.

## Contents

- Response Format
- Basic Usage (Auto Strategy)
- ProviderStrategy (Native, strict schema)
- ToolStrategy (Explicit, Union Types, Custom Tool Message, Error Handling)
- Node Usage

## Response Format

The `response_format` parameter accepts:

| Type | Description |
|------|-------------|
| `Schema` (Pydantic/TypedDict) | Auto-selects best strategy based on model |
| `ToolStrategy(schema)` | Force tool calling strategy |
| `ProviderStrategy(schema)` | Force provider-native strategy |

When schema is passed directly, LangChain automatically chooses:
- `ProviderStrategy` for models with native structured output (OpenAI, Anthropic, Grok)
- `ToolStrategy` for all other models

## Basic Usage (Auto Strategy)

```python
# casts.{cast_name}.modules.agents
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from .models import get_sample_model


class ContactInfo(BaseModel):
    """Contact information for a person."""
    name: str = Field(description="Person's name")
    email: str = Field(description="Email address")
    phone: str = Field(description="Phone number")


def set_structured_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[...],
        response_format=ContactInfo,  # Auto-selects strategy
    )
```

## ProviderStrategy (Native, strict schema)

`ProviderStrategy` uses the provider's native structured output (OpenAI, Anthropic, Grok, Gemini). Pass `strict=True` (langchain v1.2+) for strict schema adherence on providers that support it (e.g., OpenAI, xAI):

```python
# casts.{cast_name}.modules.agents
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from .models import get_sample_model


class ContactInfo(BaseModel):
    name: str = Field(description="Person's name")
    email: str = Field(description="Email address")
    phone: str = Field(description="Phone number")


def set_native_strict_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[...],
        response_format=ProviderStrategy(ContactInfo, strict=True),
    )
```

> Without `strict=True`, native structured output enforces only the schema's surface — providers may still emit minor deviations. `strict=True` rejects responses that don't match exactly.

### Provider support detection (langchain v1.1+)

When you pass a schema directly to `response_format`, LangChain reads the model's `.profile` (sourced from models.dev) to decide between `ProviderStrategy` (native) and `ToolStrategy`. If profile data is missing, it falls back to `ToolStrategy` — pin manually via `ProviderStrategy(...)` when you need the native path explicitly.

The "Basic Usage (Auto Strategy)" section above shows the auto-selected form.

---

## ToolStrategy (Explicit)

Use `ToolStrategy` explicitly for additional options like error handling and custom messages.

```python
# casts.{cast_name}.modules.agents
from typing import Literal
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from .models import get_sample_model


class ProductReview(BaseModel):
    """Analysis of a product review."""
    rating: int | None = Field(description="Rating 1-5", ge=1, le=5)
    sentiment: Literal["positive", "negative"] = Field(description="Review sentiment")
    key_points: list[str] = Field(description="Key points, 1-3 words each")


def set_tool_strategy_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[...],
        response_format=ToolStrategy(ProductReview),
    )
```

### Union Types

Allow model to choose appropriate schema:

```python
# casts.{cast_name}.modules.agents
from typing import Union
from pydantic import BaseModel, Field
from typing import Literal
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from .models import get_sample_model

class ProductReview(BaseModel):
    rating: int | None = Field(ge=1, le=5)
    sentiment: Literal["positive", "negative"]

class CustomerComplaint(BaseModel):
    issue_type: Literal["product", "service", "shipping", "billing"]
    severity: Literal["low", "medium", "high"]
    description: str

def set_union_structured_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[...],
        response_format=ToolStrategy(Union[ProductReview, CustomerComplaint]),
    )
```

### Custom Tool Message

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from .models import get_sample_model

def set_custom_message_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[],
        response_format=ToolStrategy(
            schema=ContactInfo,
            tool_message_content="Contact info extracted successfully!",
        ),
    )
```

### Error Handling

| Option | Description |
|--------|-------------|
| `True` (default) | Catch all errors, retry with default message |
| `"custom msg"` | Catch all errors, retry with custom message |
| `ValueError` | Only catch this exception type |
| `(ValueError, TypeError)` | Catch multiple exception types |
| `callable` | Custom error handler function |
| `False` | No retry, raise exceptions |

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from langchain.agents.structured_output import (
    ToolStrategy,
    StructuredOutputValidationError,
    MultipleStructuredOutputsError,
)
from .models import get_sample_model

def custom_error_handler(error: Exception) -> str:
    if isinstance(error, StructuredOutputValidationError):
        return "Invalid format. Please try again."
    if isinstance(error, MultipleStructuredOutputsError):
        return "Return only one response."
    return f"Error: {str(error)}"


def set_error_handling_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[],
        response_format=ToolStrategy(
            schema=ProductReview,
            handle_errors=custom_error_handler,
        ),
    )
```

---

## Node Usage

```python
# casts.{cast_name}.modules.nodes
from casts.base_node import BaseNode
from .agents import set_structured_agent

class StructuredOutputNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.agent = set_structured_agent()

    def execute(self, state):
        result = self.agent.invoke({
            "messages": [{"role": "user", "content": state["query"]}]
        })
        structured = result["structured_response"]  # Pydantic instance
        return {"result": structured.model_dump()}
```
