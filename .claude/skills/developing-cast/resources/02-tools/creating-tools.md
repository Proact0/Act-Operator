# Creating Tools

## When to Use This Resource

Read this when creating new tools, defining tool schemas, or troubleshooting tool creation issues.

## Key Concepts

**Tool:** Function that agents can call to perform actions or retrieve data.

**@tool Decorator:** Converts function into LangChain tool with schema.

**Tool Schema:** Defines parameters, types, descriptions for LLM.

**modules/tools:** ONLY location for tools in Act projects.

## Act Project Convention (CRITICAL)

⚠️ **Tools MUST be in:** `modules/tools/[tool_name].py`

⚠️ **NEVER put tools in:** `casts/` directory

**Why:** Tools are reusable across casts, not cast-specific.

## Tool Creation Patterns

### Pattern 1: Simple Tool (Most Common)

**When to use:** Basic tool with straightforward parameters

```python
# File: modules/tools/calculator.py
from langchain_core.tools import tool

@tool
def calculator(operation: str, a: float, b: float) -> float:
    """Perform basic arithmetic operations.

    Args:
        operation: Operation to perform (add, subtract, multiply, divide)
        a: First number
        b: Second number

    Returns:
        Result of operation
    """
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    else:
        raise ValueError(f"Unknown operation: {operation}")
```

**Key points:**
- @tool decorator above function
- Descriptive docstring (LLM reads this)
- Type hints (creates schema automatically)
- Return value typed

### Pattern 2: Tool with Complex Types

**When to use:** Tool needs structured input

```python
# File: modules/tools/search.py
from langchain_core.tools import tool
from typing import List, Dict, Optional

@tool
def search_database(
    query: str,
    filters: Optional[Dict[str, str]] = None,
    limit: int = 10,
) -> List[Dict[str, str]]:
    """Search database for matching records.

    Args:
        query: Search query string
        filters: Optional dict of field:value filters
        limit: Maximum number of results

    Returns:
        List of matching records as dicts
    """
    # Implementation
    results = perform_search(query, filters, limit)
    return results
```

### Pattern 3: Tool with Pydantic Model

**When to use:** Complex validation, nested data structures

```python
# File: modules/tools/api_client.py
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import List

class APIRequest(BaseModel):
    """Request schema for API call."""
    endpoint: str = Field(description="API endpoint path")
    method: str = Field(default="GET", description="HTTP method")
    params: dict = Field(default_factory=dict, description="Query parameters")

@tool(args_schema=APIRequest)
def call_api(endpoint: str, method: str = "GET", params: dict = None) -> dict:
    """Make HTTP API request.

    This tool calls external APIs with specified parameters.
    """
    # Pydantic validates inputs automatically
    response = make_request(endpoint, method, params or {})
    return response
```

**Benefits:**
- Automatic validation
- Better error messages
- Complex nested schemas
- Default values

### Pattern 4: Tool with Custom Name

**When to use:** Function name isn't descriptive enough for LLM

```python
from langchain_core.tools import tool

@tool("search_knowledge_base")
def search_kb(query: str) -> str:
    """Search the company knowledge base for information.

    Args:
        query: Search query

    Returns:
        Relevant information from knowledge base
    """
    return search_implementation(query)
```

**Tool will be called:** `search_knowledge_base` (not `search_kb`)

## Tool Documentation Best Practices

### Docstring Format

```python
@tool
def my_tool(param1: str, param2: int) -> str:
    """[One-line summary of what tool does]

    [Optional longer description if needed]

    Args:
        param1: [What this parameter is for]
        param2: [What this parameter is for]

    Returns:
        [What the return value represents]

    Raises:
        ValueError: [When this error occurs]
    """
```

**LLM reads:**
- First line of docstring (most important)
- Parameter descriptions from Args section
- Return description

**Write for LLM understanding:**
- Clear, concise descriptions
- Explain *when* to use tool
- Describe *what* parameters mean
- Avoid technical jargon

### Example: Good vs Bad Docstrings

```python
# ❌ BAD
@tool
def fetch(url: str) -> str:
    """Fetches stuff."""
    pass

# ✅ GOOD
@tool
def fetch_webpage(url: str) -> str:
    """Retrieve the HTML content of a webpage.

    Use this tool when you need to read the contents of a specific URL.

    Args:
        url: Full URL of the webpage to fetch (must include http:// or https://)

    Returns:
        HTML content of the webpage as a string
    """
    pass
```

## Tool Organization in Act Projects

### File Structure

```
modules/
  tools/
    __init__.py
    calculator.py
    search.py
    api_client.py
    file_operations.py
```

### `__init__.py` Pattern

```python
# File: modules/tools/__init__.py
"""Tools for Act Operator casts."""

from modules.tools.calculator import calculator
from modules.tools.search import search_database
from modules.tools.api_client import call_api

# Export list for easy import
__all__ = [
    "calculator",
    "search_database",
    "call_api",
]

# Optional: tool list for convenience
ALL_TOOLS = [calculator, search_database, call_api]
```

### Import in Casts

```python
# In cast graph or nodes
from modules.tools import calculator, search_database

# Or import list
from modules.tools import ALL_TOOLS

# Or import from specific file
from modules.tools.calculator import calculator
```

## Tool Return Types

### Pattern: Return String (Simple)

```python
@tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"Weather in {city}: 72°F, sunny"
```

### Pattern: Return Dict (Structured)

```python
@tool
def get_weather(city: str) -> dict:
    """Get current weather for a city."""
    return {
        "city": city,
        "temperature": 72,
        "condition": "sunny",
        "humidity": 45,
    }
```

### Pattern: Return List

```python
@tool
def search_products(query: str) -> List[dict]:
    """Search for products matching query."""
    return [
        {"id": 1, "name": "Product A", "price": 29.99},
        {"id": 2, "name": "Product B", "price": 39.99},
    ]
```

**LLM can handle any JSON-serializable return type.**

## Error Handling in Tools

### Pattern: Validate and Raise

```python
@tool
def divide_numbers(a: float, b: float) -> float:
    """Divide two numbers.

    Args:
        a: Numerator
        b: Denominator (cannot be zero)

    Returns:
        Result of a / b

    Raises:
        ValueError: If b is zero
    """
    if b == 0:
        raise ValueError("Cannot divide by zero. Please provide a non-zero denominator.")

    return a / b
```

**LLM will see error message and can retry with different inputs.**

### Pattern: Try-Except with Helpful Message

```python
@tool
def fetch_url(url: str) -> str:
    """Fetch content from URL.

    Args:
        url: URL to fetch

    Returns:
        Content from URL
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text

    except requests.Timeout:
        raise TimeoutError(f"Request to {url} timed out after 10 seconds")

    except requests.HTTPError as e:
        raise ValueError(f"HTTP error fetching {url}: {e}")

    except Exception as e:
        raise RuntimeError(f"Failed to fetch {url}: {e}")
```

## Common Tool Patterns

### Pattern: Search/Retrieval

```python
@tool
def search_documents(query: str, max_results: int = 5) -> List[dict]:
    """Search document database for relevant information."""
    results = vector_db.search(query, limit=max_results)
    return [{"title": r.title, "content": r.content} for r in results]
```

### Pattern: Calculation/Transformation

```python
@tool
def calculate_roi(investment: float, return_value: float) -> dict:
    """Calculate return on investment percentage."""
    roi = ((return_value - investment) / investment) * 100
    return {
        "investment": investment,
        "return": return_value,
        "roi_percent": round(roi, 2),
    }
```

### Pattern: External API Call

```python
@tool
def get_stock_price(symbol: str) -> dict:
    """Get current stock price for a ticker symbol."""
    api_key = os.getenv("STOCK_API_KEY")
    response = requests.get(
        f"https://api.example.com/quote/{symbol}",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    response.raise_for_status()
    return response.json()
```

### Pattern: File Operations

```python
@tool
def read_file(filepath: str) -> str:
    """Read contents of a file.

    Args:
        filepath: Path to file to read

    Returns:
        File contents as string
    """
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
```

## Common Mistakes

### ❌ Tool in Wrong Location

```python
# BAD: Tool in cast directory
# casts/my_agent/tools.py
@tool
def my_tool():
    pass
```

**Fix:**
```python
# GOOD: Tool in modules/tools/
# modules/tools/my_tool.py
@tool
def my_tool():
    pass
```

### ❌ Missing Docstring

```python
# BAD
@tool
def search(query: str) -> str:
    return do_search(query)
```

**Fix:**
```python
# GOOD
@tool
def search(query: str) -> str:
    """Search the database for information matching the query."""
    return do_search(query)
```

### ❌ No Type Hints

```python
# BAD
@tool
def calculate(a, b):
    return a + b
```

**Fix:**
```python
# GOOD
@tool
def calculate(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b
```

### ❌ Vague Parameter Names

```python
# BAD
@tool
def fetch(x: str, y: int) -> str:
    """Fetch data."""
    pass
```

**Fix:**
```python
# GOOD
@tool
def fetch_records(query: str, limit: int) -> str:
    """Fetch database records matching query."""
    pass
```

## Decision Framework

```
Tool does one simple thing?
  → Use Pattern 1 (simple function)

Tool needs structured input?
  → Use Pattern 2 (complex types)

Tool needs validation?
  → Use Pattern 3 (Pydantic model)

Tool makes external API calls?
  → Add error handling with try-except

Tool reads/writes files?
  → Handle FileNotFoundError, permissions

Tool can fail?
  → Raise ValueError/RuntimeError with helpful message

Tool name not clear?
  → Use Pattern 4 (custom name)
```

## Act Project Conventions

⚠️ **Location:**
- Tools ONLY in: `modules/tools/[tool_name].py`
- Never in casts directory
- One tool per file (or related tools grouped)

⚠️ **Naming:**
- File: `modules/tools/calculator.py`
- Function: `def calculator(...)` or `@tool("calculator")`
- Exported in `modules/tools/__init__.py`

⚠️ **Documentation:**
- Always include docstring
- Type hint all parameters
- Type hint return value
- Describe when to use tool

## Anti-Patterns

- ❌ **Tools with side effects without description** → Document what changes
- ❌ **Generic tool names** → Be specific (search_kb not search)
- ❌ **Returning complex objects** → Return JSON-serializable types
- ❌ **No error handling** → Validate inputs, handle exceptions
- ❌ **Unused parameters** → Remove or document why needed

## References

- Related: `02-tools/tool-patterns.md`, `01-core/nodes.md`
- Tool usage in graphs: `05-patterns/prebuilt-components.md`
- LangChain tool docs: https://docs.langchain.com/oss/python/langchain/tools
