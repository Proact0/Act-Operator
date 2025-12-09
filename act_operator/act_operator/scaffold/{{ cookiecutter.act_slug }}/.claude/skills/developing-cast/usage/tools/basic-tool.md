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
- Google docstring should be concise and informative

## Custom Name

```python
# casts.{cast_name}.modules.tools
from langchain.tools import tool

@tool("web_search")
def search(query: str) -> str:
    """Search the web for information.

    Args:
        query: Search terms to look for
    """
    return f"Results for: {query}"
```

---

## Agent Usage

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from .models import get_model
from .tools import search_database, calc

def set_tool_agent():
    return create_agent(
        model=get_model(),
        tools=[search_database, calc],
    )
```

## Model(Standalone) Usage

```python
# casts.{cast_name}.modules.models
from langchain_openai import ChatOpenAI
from .tools import search_database, calc

def get_tool_model():
    model = ChatOpenAI(model="gpt-4o")
    model.bind_tools([search_database, calc])
    return model
```