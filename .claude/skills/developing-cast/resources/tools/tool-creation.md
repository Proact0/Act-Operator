# Tool Creation

## When to Use This Resource
Read when creating tools for LangGraph casts, understanding @tool decorator, or implementing tool schemas.

---

## Critical Rule: Tool Location

**Tools ONLY in `modules/tools/` - NO exceptions (Act convention)**

```
casts/my_cast/
  └── modules/
      └── tools/
          ├── __init__.py
          ├── web_search.py      # Individual tool files
          ├── calculator.py
          └── database.py
```

**NOT:** `tools/`, `nodes.py`, `graph.py`, or anywhere else

---

## Basic Tool Pattern

```python
# File: casts/my_cast/modules/tools/web_search.py

from langchain_core.tools import tool

@tool
def web_search(query: str) -> list[dict]:
    """Searches the web for information.

    Args:
        query: Search query string

    Returns:
        List of search results with title, snippet, url
    """
    # Implementation
    results = [
        {"title": "Example", "snippet": "...", "url": "https://..."}
    ]

    return results
```

**Key points:**
- `@tool` decorator creates Tool from function
- Function signature → tool schema
- Docstring → tool description (LLM sees this)
- Type hints → parameter types

---

## Tool Decorator Patterns

### Simple Tool

```python
from langchain_core.tools import tool

@tool
def calculator(expression: str) -> float:
    """Evaluates mathematical expressions.

    Args:
        expression: Math expression like "2 + 2" or "10 * 5"

    Returns:
        Calculated result
    """
    try:
        result = eval(expression)  # Use safely in production!
        return float(result)
    except Exception as e:
        return 0.0
```

---

### Tool with Multiple Parameters

```python
@tool
def search_documents(
    query: str,
    max_results: int = 5,
    filter_type: str = "all"
) -> list[dict]:
    """Searches internal document database.

    Args:
        query: Search query
        max_results: Maximum number of results (default: 5)
        filter_type: Filter by type: "all", "pdf", "doc" (default: "all")

    Returns:
        List of matching documents
    """
    # Implementation
    documents = []  # ... fetch from database
    return documents[:max_results]
```

**LLM sees all parameters and defaults in schema**

---

### Tool with Complex Return Type

```python
from typing import Dict, List, Optional

@tool
def get_weather(location: str) -> Dict[str, any]:
    """Gets current weather for location.

    Args:
        location: City name or zip code

    Returns:
        Weather data with temperature, conditions, humidity
    """
    return {
        "location": location,
        "temperature": 72,
        "conditions": "Sunny",
        "humidity": 45,
        "forecast": ["Clear", "Partly cloudy"]
    }
```

---

### Tool with Error Handling

```python
@tool
def api_call(endpoint: str) -> dict:
    """Calls external API endpoint.

    Args:
        endpoint: API endpoint path

    Returns:
        API response data or error dict
    """
    import requests

    try:
        response = requests.get(f"https://api.example.com/{endpoint}")
        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:
        return {
            "error": str(e),
            "status": "failed"
        }
```

---

## Tool with Context Access (ToolRuntime)

```python
from typing import Optional, Any

@tool
def save_user_preference(
    key: str,
    value: str,
    runtime: Optional[Any] = None
) -> str:
    """Saves user preference to long-term memory.

    Args:
        key: Preference key
        value: Preference value
        runtime: Runtime context with Store access

    Returns:
        Confirmation message
    """
    if runtime and runtime.store:
        namespace = ("user_preferences",)
        runtime.store.put(namespace, key, {"value": value})
        return f"Saved {key} = {value}"

    return "Store not available"
```

**See:** `tools/tool-runtime.md` for detailed ToolRuntime patterns

---

## Docstring Best Practices

### Good Docstring (LLM-Friendly)

```python
@tool
def web_search(query: str) -> list:
    """Searches the web for current information about any topic.

    Use this tool when you need up-to-date information from the internet.
    Returns web pages ranked by relevance to the query.

    Args:
        query: What to search for. Be specific for better results.
            Example: "latest developments in AI" or "Python tutorial"

    Returns:
        List of search results, each with title, snippet, and URL
    """
    pass
```

**Why good:**
- Clear what the tool does
- When to use it
- Example queries
- What to expect back

---

### Poor Docstring

```python
@tool
def web_search(query: str) -> list:
    """Searches."""  # Too brief, not helpful
    pass
```

---

## Tool Naming

### Good Names (Descriptive, Clear)

```python
@tool
def search_web(query: str):  # Clear action
    pass

@tool
def calculate_mortgage(principal: float, rate: float, years: int):  # Specific
    pass

@tool
def get_user_profile(user_id: str):  # Clear what it gets
    pass
```

### Poor Names (Vague)

```python
@tool
def search(query: str):  # Search what?
    pass

@tool
def calc(a, b):  # Calculate what?
    pass

@tool
def get(id):  # Get what?
    pass
```

---

## Invoking Tools

### Direct Invocation (in Nodes)

```python
# In a node
from casts.my_cast.modules.tools.web_search import web_search

class SearchNode(BaseNode):
    def execute(self, state: dict) -> dict:
        query = state.get("query")

        # Invoke tool directly
        results = web_search.invoke({"query": query})

        return {"search_results": results}
```

---

### With bind_tools (LLM decides)

```python
# In a node
from langchain_openai import ChatOpenAI
from casts.my_cast.modules.tools.web_search import web_search
from casts.my_cast.modules.tools.calculator import calculator

model = ChatOpenAI(model="gpt-4")

# Bind tools to model
model_with_tools = model.bind_tools([web_search, calculator])

# LLM can now decide to call these tools
response = model_with_tools.invoke(messages)
```

**LLM decides when/how to use tools based on conversation**

---

### With ToolNode (Automatic Execution)

```python
from langgraph.prebuilt import ToolNode
from casts.my_cast.modules.tools.web_search import web_search

# Create ToolNode
tools = [web_search, calculator]
tool_node = ToolNode(tools)

# In graph
builder.add_node("tools", tool_node)

# ToolNode automatically executes tool calls from LLM
```

**See:** `core/edge-patterns.md` for tool routing patterns

---

## Tool Organization

### Single Tool Per File (Recommended)

```
modules/tools/
  ├── __init__.py
  ├── web_search.py     # One tool
  ├── calculator.py     # One tool
  └── database.py       # One tool
```

```python
# In web_search.py
from langchain_core.tools import tool

@tool
def web_search(query: str) -> list:
    """Searches the web."""
    pass
```

---

### Multiple Related Tools Per File

```python
# modules/tools/math_tools.py

from langchain_core.tools import tool

@tool
def add(a: float, b: float) -> float:
    """Adds two numbers."""
    return a + b

@tool
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers."""
    return a * b

@tool
def divide(a: float, b: float) -> float:
    """Divides a by b."""
    return a / b if b != 0 else 0.0
```

---

## Anti-Patterns

### ❌ Tools Outside modules/tools/

```python
# ❌ WRONG: casts/my_cast/tools.py
@tool
def my_tool():
    pass

# ❌ WRONG: casts/my_cast/nodes.py
@tool
def my_tool():
    pass
```

```python
# ✓ CORRECT: casts/my_cast/modules/tools/my_tool.py
@tool
def my_tool():
    pass
```

---

### ❌ Missing Docstring

```python
@tool
def web_search(query: str):
    # ❌ No docstring - LLM won't know what this does
    return []
```

```python
@tool
def web_search(query: str) -> list:
    """Searches the web for information."""  # ✓ Clear description
    return []
```

---

### ❌ Vague Parameters

```python
@tool
def process(data):  # ❌ What type? What data?
    pass
```

```python
@tool
def process_user_data(user_id: str) -> dict:  # ✓ Clear types and purpose
    """Processes data for specific user."""
    pass
```

---

## Decision Framework

**Q: One tool per file or multiple?**
- Related tools (math operations) → Multiple in one file
- Independent tools → Separate files
- Default → One per file (clearer)

**Q: Direct invoke or bind_tools?**
- Know when to call tool → Direct invoke in node
- LLM decides when to call → bind_tools
- Automatic execution → ToolNode

**Q: How detailed should docstring be?**
- LLM uses it to decide when to call
- More detail = better tool selection
- Include examples for complex tools

---

## Importing Tools

```python
# In graph.py or nodes.py
from casts.my_cast.modules.tools.web_search import web_search
from casts.my_cast.modules.tools.calculator import calculator

# Use in nodes
class MyNode(BaseNode):
    def execute(self, state: dict) -> dict:
        result = web_search.invoke({"query": "test"})
        return {"result": result}
```

---

## References
- patterns/act-conventions.md (tool location rules)
- tools/tool-runtime.md (ToolRuntime and Store access)
- core/node-patterns.md (using tools in nodes)
