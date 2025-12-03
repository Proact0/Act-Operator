# Basic Tool Definition

Create tools using the `@tool` decorator. The function's docstring becomes the tool description.

## Simple Tool

```python
# casts.{cast_name}.modules.tools
from langchain.tools import tool

@tool
def search_database(query: str, limit: int = 10) -> str:
    """Search the customer database for records matching the query.

    Args:
        query: Search terms to look for
        limit: Maximum number of results to return
    """
    return f"Found {limit} results for '{query}'"
```

**Requirements:**
- Type hints are **required** (define input schema)
- Docstring should be concise and informative

## Custom Name & Description

```python
# casts.{cast_name}.modules.tools
from langchain.tools import tool

@tool("web_search")
def search(query: str) -> str:
    """Search the web for information."""
    return f"Results for: {query}"

@tool("calculator", description="Performs arithmetic calculations. Use for math problems.")
def calc(expression: str) -> str:
    """Evaluate mathematical expressions."""
    return str(eval(expression))
```

## Reserved Parameter Names

| Name | Purpose |
|------|---------|
| `config` | Reserved for `RunnableConfig` |
| `runtime` | Reserved for `ToolRuntime` (state, context, store access) |

---

## Agent Usage

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from .models import get_sample_model
from .tools import search_database, calc

def set_tool_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[search_database, calc],
    )
```
