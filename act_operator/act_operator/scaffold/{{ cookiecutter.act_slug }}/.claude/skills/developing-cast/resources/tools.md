---
# Tools Resource
# LangGraph 1.0 Tool Implementation Patterns
---

# Implementing Tools

## Critical Rule

**Tools MUST be implemented in `modules/tools/` directory. Never in nodes/, agents/, or anywhere else.**

## Core Pattern

Use `@tool` decorator from LangChain:

```python
# modules/tools/__init__.py or modules/tools/my_tools.py
from langchain_core.tools import tool

@tool
def my_tool(query: str) -> str:
    """Tool description that LLM sees.

    Args:
        query: Description of the parameter.

    Returns:
        Description of return value.
    """
    # Implementation
    result = process(query)
    return result
```

## Tool Location Structure

```
casts/<cast_name>/
└── modules/
    └── tools/
        ├── __init__.py         # Export tools here
        ├── search_tools.py     # Group related tools
        ├── data_tools.py
        └── api_tools.py
```

**Export in `__init__.py`:**
```python
# modules/tools/__init__.py
from .search_tools import wikipedia_search, web_search
from .data_tools import process_data, validate_data

__all__ = [
    "wikipedia_search",
    "web_search",
    "process_data",
    "validate_data",
]
```

## Using Tools in Nodes

Import from tools module:

```python
# modules/nodes.py
from casts.base_node import BaseNode
from .tools import my_tool

class MyNode(BaseNode):
    def execute(self, state, runtime=None, **kwargs):
        query = state.get("query")
        result = my_tool.invoke(query)
        return {"result": result}
```

## Accessing Context with ToolRuntime

For tools that need runtime context (config, store, etc.):

```python
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedToolArg
from typing import Annotated

@tool
def context_aware_tool(
    query: str,
    runtime: Annotated[dict, InjectedToolArg]
) -> str:
    """Tool that accesses runtime context.

    Args:
        query: The search query.
        runtime: Injected runtime context (not provided by LLM).

    Returns:
        Search results.
    """
    # Access runtime
    store = runtime.get("store")
    config = runtime.get("config", {})
    thread_id = config.get("configurable", {}).get("thread_id")

    # Use context
    if store and thread_id:
        history = store.get(("history", thread_id), "searches")

    # Process with context
    result = search_with_context(query, history)
    return result
```

**InjectedToolArg:** Tells LangGraph to inject context, not request from LLM.

## Tool Examples

### Simple Function Tool

```python
@tool
def calculate_area(length: float, width: float) -> float:
    """Calculate rectangle area.

    Args:
        length: Rectangle length in meters.
        width: Rectangle width in meters.

    Returns:
        Area in square meters.
    """
    return length * width
```

### Tool with External API

```python
import requests

@tool
def fetch_weather(city: str) -> str:
    """Fetch current weather for a city.

    Args:
        city: City name.

    Returns:
        Weather description.
    """
    try:
        response = requests.get(
            f"https://api.weather.com/v1/current",
            params={"city": city}
        )
        data = response.json()
        return f"Weather in {city}: {data['description']}, {data['temp']}°C"
    except Exception as e:
        return f"Error fetching weather: {e}"
```

### Tool with LangChain Integration

```python
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

def create_wikipedia_tool():
    """Factory function for Wikipedia tool."""
    api_wrapper = WikipediaAPIWrapper(
        top_k_results=2,
        doc_content_chars_max=500
    )
    return WikipediaQueryRun(api_wrapper=api_wrapper)

# In nodes.py:
# wikipedia_tool = create_wikipedia_tool()
# result = wikipedia_tool.invoke("LangGraph")
```

### Tool with Validation

```python
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    """Input schema for search tool."""
    query: str = Field(description="Search query")
    max_results: int = Field(default=5, description="Max results", ge=1, le=10)

@tool(args_schema=SearchInput)
def search_tool(query: str, max_results: int = 5) -> str:
    """Search with validated inputs.

    Args:
        query: Search query.
        max_results: Maximum results (1-10).

    Returns:
        Search results.
    """
    # Inputs automatically validated by Pydantic
    results = perform_search(query, limit=max_results)
    return "\n".join(results[:max_results])
```

## Passing Tools to Agents

Tools are passed to agents/LLMs for agent pattern:

```python
# modules/nodes.py
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from .tools import wikipedia_search, calculator

class AgentNode(BaseNode):
    def __init__(self):
        super().__init__()
        self.llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
        self.tools = [wikipedia_search, calculator]

    def execute(self, state, runtime=None, **kwargs):
        # Create agent with tools
        agent = create_react_agent(self.llm, self.tools)

        # Run agent
        result = agent.invoke({"messages": state["messages"]})
        return {"messages": result["messages"]}
```

## Tool Documentation

**LLM sees the docstring** - make it clear:

```python
@tool
def good_tool(query: str, limit: int = 5) -> str:
    """Search Wikipedia for information.

    Use this when you need factual information from Wikipedia.

    Args:
        query: The search query (e.g., "Python programming").
        limit: Maximum number of results to return (default: 5).

    Returns:
        Formatted search results with titles and summaries.

    Example:
        search("LangGraph", limit=3) returns top 3 Wikipedia articles.
    """
    ...
```

## Common Patterns

### Tool with State

```python
class ToolWithState:
    """Tool that maintains internal state."""

    def __init__(self):
        self.call_count = 0

    @tool
    def stateful_tool(self, input: str) -> str:
        """Tool with internal state."""
        self.call_count += 1
        return f"Called {self.call_count} times with: {input}"

# Usage:
# tool_instance = ToolWithState()
# result = tool_instance.stateful_tool.invoke("query")
```

### Async Tool

```python
import asyncio

@tool
async def async_tool(query: str) -> str:
    """Async tool for concurrent operations.

    Args:
        query: Search query.

    Returns:
        Results.
    """
    result = await async_fetch(query)
    return result

# Usage with await:
# result = await async_tool.ainvoke("query")
```

### Tool Error Handling

```python
@tool
def robust_tool(input: str) -> str:
    """Tool with error handling.

    Args:
        input: Input data.

    Returns:
        Result or error message.
    """
    try:
        result = risky_operation(input)
        return f"Success: {result}"
    except ValueError as e:
        return f"Validation error: {e}"
    except Exception as e:
        return f"Error: {e}"
```

## Tool Discovery (MCP)

For MCP tool integration, see `resources/mcp-adapter.md`.

## Common Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| Tool in modules/nodes.py | Move to modules/tools/ |
| Tool in modules/agents/ | Move to modules/tools/ |
| Missing docstring | LLM needs description |
| Unclear arg descriptions | Be specific for LLM |
| Not handling errors | Return error strings |
| Complex tool logic | Break into helper functions |
| Missing type hints | Add for validation |

## Testing Tools

See `testing-cast` skill for comprehensive patterns.

**Basic test:**
```python
def test_tool():
    from modules.tools import my_tool
    result = my_tool.invoke("test query")
    assert "expected" in result
```

**Test with runtime:**
```python
def test_context_tool():
    from modules.tools import context_aware_tool
    runtime = {"store": mock_store, "config": {}}
    result = context_aware_tool.invoke(
        {"query": "test"},
        runtime=runtime
    )
    assert result
```

## Performance Considerations

**Lazy initialization:**
```python
_wikipedia_tool = None

def get_wikipedia_tool():
    """Lazy load tool."""
    global _wikipedia_tool
    if _wikipedia_tool is None:
        _wikipedia_tool = create_wikipedia_tool()
    return _wikipedia_tool
```

**Caching:**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_lookup(key: str) -> str:
    """Cached expensive lookup."""
    return expensive_operation(key)

@tool
def cached_tool(key: str) -> str:
    """Tool with caching."""
    return cached_lookup(key)
```

## Next Steps

- **Using tools in nodes:** See `resources/nodes.md`
- **Agent patterns with tools:** See `resources/agents.md`
- **MCP tool integration:** See `resources/mcp-adapter.md`
