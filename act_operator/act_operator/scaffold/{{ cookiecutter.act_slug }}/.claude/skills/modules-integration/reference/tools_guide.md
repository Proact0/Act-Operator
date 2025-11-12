# Tools Guide for LangGraph Applications

Comprehensive guide to implementing, using, and managing tools in LangGraph applications with Act-Operator.

## Table of Contents

1. [Introduction](#introduction)
2. [Tool Fundamentals](#tool-fundamentals)
   - [What is a Tool](#what-is-a-tool)
   - [Tool Components](#tool-components)
   - [Tool vs Function](#tool-vs-function)
3. [Using @tool Decorator](#using-tool-decorator)
   - [Basic Tool Definition](#basic-tool-definition)
   - [Tool with Type Hints](#tool-with-type-hints)
   - [Tool with Docstrings](#tool-with-docstrings)
   - [Tool with Multiple Parameters](#tool-with-multiple-parameters)
4. [Tool Definitions and Schemas](#tool-definitions-and-schemas)
   - [JSON Schema Generation](#json-schema-generation)
   - [Pydantic Models](#pydantic-models)
   - [Custom Schemas](#custom-schemas)
   - [Schema Validation](#schema-validation)
5. [MCP (Model Context Protocol) Tools](#mcp-model-context-protocol-tools)
   - [What is MCP](#what-is-mcp)
   - [MCP Tool Integration](#mcp-tool-integration)
   - [Available MCP Tools](#available-mcp-tools)
   - [Custom MCP Tools](#custom-mcp-tools)
6. [ToolNode from langgraph.prebuilt](#toolnode-from-langgraphprebuilt)
   - [Basic ToolNode Usage](#basic-toolnode-usage)
   - [ToolNode Configuration](#toolnode-configuration)
   - [Error Handling in ToolNode](#error-handling-in-toolnode)
   - [Custom ToolNode](#custom-toolnode)
7. [Custom Tool Implementation](#custom-tool-implementation)
   - [Tool Base Class](#tool-base-class)
   - [Async Tools](#async-tools)
   - [Stateful Tools](#stateful-tools)
   - [Tools with Dependencies](#tools-with-dependencies)
8. [Tool Error Handling](#tool-error-handling)
   - [Try-Catch in Tools](#try-catch-in-tools)
   - [Error Messages](#error-messages)
   - [Fallback Strategies](#fallback-strategies)
   - [Timeout Handling](#timeout-handling)
9. [Advanced Tool Patterns](#advanced-tool-patterns)
   - [Tool Composition](#tool-composition)
   - [Conditional Tools](#conditional-tools)
   - [Tool Chaining](#tool-chaining)
   - [Tool Caching](#tool-caching)
10. [Integration with Act-Operator](#integration-with-act-operator)
11. [Best Practices](#best-practices)
12. [Common Pitfalls](#common-pitfalls)
13. [Troubleshooting](#troubleshooting)
14. [References](#references)

---

## Introduction

Tools are functions that LLMs can call to perform specific actions. In LangGraph, tools enable agents to interact with external systems, perform computations, and access real-time data.

**What you'll learn:**
- Creating tools with @tool decorator
- Tool schemas and validation
- MCP tool integration
- ToolNode usage
- Custom tool implementation
- Error handling patterns

**Key concepts:**
- **Tool**: Function with schema that LLM can call
- **Schema**: JSON definition of tool parameters
- **ToolNode**: Pre-built node for executing tools
- **MCP**: Protocol for standardized tool integration

---

## Tool Fundamentals

### What is a Tool

**Definition:**
```python
# A tool is a function + schema + description

def get_weather(location: str) -> str:
    """Get weather for a location."""  # Description for LLM
    return f"Weather in {location}: 72°F"

# Schema (auto-generated):
{
    "name": "get_weather",
    "description": "Get weather for a location.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {"type": "string"}
        },
        "required": ["location"]
    }
}
```

### Tool Components

**Essential parts:**
```python
from langchain_core.tools import tool

@tool
def example_tool(param1: str, param2: int = 0) -> str:
    """
    Tool description for LLM.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
    """
    # Tool implementation
    result = f"{param1}: {param2}"
    return result

# Components:
# 1. Name: "example_tool"
# 2. Description: Docstring
# 3. Parameters: Type-hinted arguments
# 4. Return type: Type hint
# 5. Implementation: Function body
```

### Tool vs Function

**Regular function:**
```python
def regular_function(x: int) -> int:
    return x * 2

# Just a function, LLM can't call it
```

**Tool:**
```python
@tool
def tool_function(x: int) -> int:
    """Multiply number by 2."""
    return x * 2

# Now LLM can:
# 1. See it's available
# 2. Read description
# 3. Understand parameters
# 4. Call it with correct arguments
```

---

## Using @tool Decorator

### Basic Tool Definition

```python
from langchain_core.tools import tool

@tool
def get_weather(location: str) -> str:
    """Get current weather for a location."""
    # Mock implementation
    return f"Weather in {location}: 72°F, sunny"

# Use in agent
tools = [get_weather]
llm_with_tools = llm.bind_tools(tools)
```

### Tool with Type Hints

```python
from typing import List, Dict, Optional

@tool
def search_emails(
    sender: str,
    subject: Optional[str] = None,
    days_ago: int = 7,
    max_results: int = 10
) -> List[Dict[str, str]]:
    """
    Search emails by sender and subject.
    
    Args:
        sender: Email address of sender
        subject: Optional subject line to match
        days_ago: Search emails from last N days
        max_results: Maximum number of results
        
    Returns:
        List of matching emails with sender, subject, date
    """
    # Implementation
    results = [
        {
            "sender": sender,
            "subject": subject or "Sample",
            "date": "2024-01-15"
        }
    ]
    return results[:max_results]
```

### Tool with Docstrings

```python
@tool
def calculate_mortgage(
    principal: float,
    annual_rate: float,
    years: int
) -> Dict[str, float]:
    """
    Calculate monthly mortgage payment.
    
    This tool calculates the monthly payment for a mortgage loan
    using the principal amount, annual interest rate, and loan term.
    
    Args:
        principal: Loan amount in dollars
        annual_rate: Annual interest rate as percentage (e.g., 5.5 for 5.5%)
        years: Loan term in years
        
    Returns:
        Dictionary with monthly_payment, total_paid, total_interest
        
    Examples:
        >>> calculate_mortgage(300000, 5.5, 30)
        {
            "monthly_payment": 1703.37,
            "total_paid": 613212.00,
            "total_interest": 313212.00
        }
    """
    monthly_rate = annual_rate / 100 / 12
    num_payments = years * 12
    
    monthly_payment = (
        principal * monthly_rate * (1 + monthly_rate) ** num_payments
    ) / ((1 + monthly_rate) ** num_payments - 1)
    
    total_paid = monthly_payment * num_payments
    total_interest = total_paid - principal
    
    return {
        "monthly_payment": round(monthly_payment, 2),
        "total_paid": round(total_paid, 2),
        "total_interest": round(total_interest, 2)
    }
```

### Tool with Multiple Parameters

```python
from datetime import datetime, timedelta
from typing import Literal

@tool
def create_calendar_event(
    title: str,
    start_time: str,
    duration_minutes: int,
    attendees: List[str],
    location: Optional[str] = None,
    reminder_minutes: int = 15,
    priority: Literal["low", "medium", "high"] = "medium"
) -> str:
    """
    Create a calendar event.
    
    Args:
        title: Event title
        start_time: Start time in ISO format (YYYY-MM-DD HH:MM)
        duration_minutes: Event duration in minutes
        attendees: List of attendee email addresses
        location: Optional event location
        reminder_minutes: Reminder before event (default: 15)
        priority: Event priority level
        
    Returns:
        Confirmation message with event ID
    """
    import uuid
    event_id = str(uuid.uuid4())
    
    return f"""Event created successfully!
ID: {event_id}
Title: {title}
Start: {start_time}
Duration: {duration_minutes} minutes
Attendees: {', '.join(attendees)}
Location: {location or 'Not specified'}
Reminder: {reminder_minutes} minutes before
Priority: {priority}
"""
```

---

## Tool Definitions and Schemas

### JSON Schema Generation

```python
@tool
def example_tool(name: str, age: int) -> str:
    """Example tool."""
    return f"{name} is {age}"

# Access schema
print(example_tool.get_schema())

# Output:
{
    "name": "example_tool",
    "description": "Example tool.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "title": "Name"
            },
            "age": {
                "type": "integer",
                "title": "Age"
            }
        },
        "required": ["name", "age"]
    }
}
```

### Pydantic Models

```python
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class SearchParams(BaseModel):
    """Parameters for search tool."""
    query: str = Field(description="Search query")
    max_results: int = Field(default=10, description="Maximum results")
    include_snippets: bool = Field(default=True, description="Include snippets")

@tool(args_schema=SearchParams)
def search(params: SearchParams) -> str:
    """Search the web."""
    return f"Searching for: {params.query}"

# Or with separate args
@tool
def search_alt(
    query: str = Field(description="Search query"),
    max_results: int = Field(default=10, description="Max results")
) -> str:
    """Search the web."""
    return f"Results for: {query}"
```

### Custom Schemas

```python
from langchain_core.tools import Tool

def get_stock_price(symbol: str) -> float:
    """Get stock price."""
    return 150.25

# Create tool with custom schema
stock_tool = Tool(
    name="get_stock_price",
    func=get_stock_price,
    description="Get current stock price for a symbol",
    args_schema={
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": "Stock ticker symbol (e.g., AAPL)",
                "pattern": "^[A-Z]{1,5}$"
            }
        },
        "required": ["symbol"]
    }
)
```

### Schema Validation

```python
from pydantic import BaseModel, Field, validator

class EmailParams(BaseModel):
    """Email parameters with validation."""
    to: str = Field(description="Recipient email")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body")
    
    @validator("to")
    def validate_email(cls, v):
        if "@" not in v:
            raise ValueError("Invalid email address")
        return v
    
    @validator("subject")
    def validate_subject(cls, v):
        if len(v) > 100:
            raise ValueError("Subject too long (max 100 chars)")
        return v

@tool(args_schema=EmailParams)
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email."""
    return f"Email sent to {to}"
```

---

## MCP (Model Context Protocol) Tools

### What is MCP

MCP is a protocol for standardized tool/context integration:

```
┌──────────┐                   ┌──────────────┐
│   LLM    │ ←── MCP Protocol ───→│  MCP Server  │
└──────────┘                   └──────────────┘
                                      │
                                      ├── File System
                                      ├── Database
                                      ├── APIs
                                      └── Other Resources
```

### MCP Tool Integration

```python
# Example MCP tool usage (conceptual)
from langgraph.prebuilt import MCPClient

# Connect to MCP server
mcp_client = MCPClient(
    server_url="http://localhost:3000",
    api_key="your-api-key"
)

# Get available tools
mcp_tools = mcp_client.get_tools()

# Use in agent
llm_with_tools = llm.bind_tools(mcp_tools)
```

### Available MCP Tools

```python
# Filesystem MCP tools
filesystem_tools = [
    "read_file",
    "write_file",
    "list_directory",
    "create_directory",
    "delete_file"
]

# Database MCP tools
database_tools = [
    "query_database",
    "insert_record",
    "update_record",
    "delete_record"
]

# API MCP tools
api_tools = [
    "http_get",
    "http_post",
    "http_put",
    "http_delete"
]
```

### Custom MCP Tools

```python
# Implement custom MCP tool server (conceptual)
from mcp import MCPServer, Tool

server = MCPServer()

@server.tool(
    name="custom_search",
    description="Search custom knowledge base"
)
def custom_search(query: str, limit: int = 10) -> list:
    """Search implementation."""
    return search_knowledge_base(query, limit)

# Start server
server.run(port=3000)
```

---

## ToolNode from langgraph.prebuilt

### Basic ToolNode Usage

```python
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool

@tool
def get_weather(location: str) -> str:
    """Get weather."""
    return f"72°F in {location}"

@tool
def calculator(expression: str) -> float:
    """Calculate expression."""
    return eval(expression)

tools = [get_weather, calculator]

# Create ToolNode
tool_node = ToolNode(tools)

# Use in graph
from langgraph.graph import StateGraph

builder = StateGraph(State)
builder.add_node("tools", tool_node)

# Tool node automatically executes tool calls from state
```

### ToolNode Configuration

```python
# With error handling
tool_node = ToolNode(
    tools,
    handle_tool_errors=True  # Return errors instead of raising
)

# With custom error messages
def handle_error(error: Exception) -> str:
    return f"Tool error: {str(error)}"

tool_node = ToolNode(
    tools,
    handle_tool_errors=handle_error
)
```

### Error Handling in ToolNode

```python
from langgraph.prebuilt import ToolNode

# Default: Errors raise exceptions
tool_node = ToolNode(tools)

# Return errors as strings
tool_node = ToolNode(tools, handle_tool_errors=True)

# Custom error handler
def custom_error_handler(error: Exception, tool_call: dict) -> str:
    tool_name = tool_call.get("name", "unknown")
    return f"Error in {tool_name}: {str(error)}"

tool_node = ToolNode(
    tools,
    handle_tool_errors=custom_error_handler
)
```

### Custom ToolNode

```python
from act_operator_lib.base_node import BaseNode
from langchain_core.messages import ToolMessage

class CustomToolNode(BaseNode):
    """Custom tool execution node."""
    
    def __init__(self, tools, **kwargs):
        super().__init__(**kwargs)
        self.tools_map = {tool.name: tool for tool in tools}
    
    def execute(self, state):
        # Get last message with tool calls
        last_message = state.messages[-1]
        
        if not last_message.tool_calls:
            return {"messages": []}
        
        # Execute each tool call
        tool_messages = []
        
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]
            
            try:
                # Execute tool
                result = self.tools_map[tool_name].invoke(tool_args)
                
                # Create tool message
                tool_messages.append(ToolMessage(
                    content=str(result),
                    tool_call_id=tool_id
                ))
                
            except Exception as e:
                self.logger.error(f"Tool error: {e}")
                tool_messages.append(ToolMessage(
                    content=f"Error: {str(e)}",
                    tool_call_id=tool_id
                ))
        
        return {"messages": tool_messages}
```

---

## Custom Tool Implementation

### Tool Base Class

```python
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

class WeatherInput(BaseModel):
    location: str = Field(description="Location name")

class WeatherTool(BaseTool):
    name: str = "get_weather"
    description: str = "Get current weather for a location"
    args_schema: type[BaseModel] = WeatherInput
    
    def _run(self, location: str) -> str:
        """Synchronous implementation."""
        return f"Weather in {location}: 72°F"
    
    async def _arun(self, location: str) -> str:
        """Async implementation."""
        return self._run(location)

# Use
tool = WeatherTool()
result = tool.invoke({"location": "SF"})
```

### Async Tools

```python
import asyncio
import aiohttp
from langchain_core.tools import tool

@tool
async def fetch_url(url: str) -> str:
    """Fetch content from URL asynchronously."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

# Use
result = await fetch_url.ainvoke({"url": "https://example.com"})

# In async node
class AsyncToolNode(AsyncBaseNode):
    async def execute(self, state):
        last_message = state.messages[-1]
        
        tool_messages = []
        for tool_call in last_message.tool_calls:
            result = await self.tools_map[tool_call["name"]].ainvoke(
                tool_call["args"]
            )
            tool_messages.append(ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"]
            ))
        
        return {"messages": tool_messages}
```

### Stateful Tools

```python
class StatefulTool(BaseTool):
    name: str = "counter"
    description: str = "Increment and return counter"
    
    def __init__(self):
        super().__init__()
        self.count = 0
    
    def _run(self) -> int:
        self.count += 1
        return self.count

# Or with state parameter
@tool
def stateful_search(query: str, state: dict) -> str:
    """Search with state."""
    # Access state
    user_id = state.get("user_id")
    history = state.get("search_history", [])
    
    # Update state
    history.append(query)
    state["search_history"] = history
    
    return f"Search results for {query}"
```

### Tools with Dependencies

```python
class DatabaseTool(BaseTool):
    """Tool with database dependency."""
    
    name: str = "query_database"
    description: str = "Query the database"
    
    def __init__(self, db_connection):
        super().__init__()
        self.db = db_connection
    
    def _run(self, query: str) -> list:
        return self.db.execute(query)

# Initialize with dependencies
db = connect_to_database()
tool = DatabaseTool(db_connection=db)

# Use in graph
tools = [tool]
tool_node = ToolNode(tools)
```

---

## Tool Error Handling

### Try-Catch in Tools

```python
@tool
def safe_division(a: float, b: float) -> str:
    """Divide two numbers safely."""
    try:
        result = a / b
        return f"Result: {result}"
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def api_call(endpoint: str) -> str:
    """Call external API with error handling."""
    import requests
    
    try:
        response = requests.get(endpoint, timeout=10)
        response.raise_for_status()
        return response.json()
        
    except requests.Timeout:
        return "Error: Request timed out"
    except requests.HTTPError as e:
        return f"Error: HTTP {e.response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"
```

### Error Messages

```python
@tool
def validated_tool(email: str) -> str:
    """Tool with validation and clear errors."""
    # Validate input
    if not email or "@" not in email:
        return "Error: Invalid email address. Please provide a valid email."
    
    try:
        # Process
        result = send_email(email)
        return f"Success: Email sent to {email}"
        
    except Exception as e:
        # User-friendly error
        return f"Error: Failed to send email. {str(e)}"
```

### Fallback Strategies

```python
@tool
def search_with_fallback(query: str) -> str:
    """Search with multiple fallback strategies."""
    # Try primary search
    try:
        return primary_search(query)
    except Exception as e:
        logger.warning(f"Primary search failed: {e}")
    
    # Try backup search
    try:
        return backup_search(query)
    except Exception as e:
        logger.warning(f"Backup search failed: {e}")
    
    # Final fallback
    return f"No results found for: {query}"
```

### Timeout Handling

```python
import asyncio
from langchain_core.tools import tool

@tool
async def search_with_timeout(query: str, timeout: int = 30) -> str:
    """Search with timeout."""
    try:
        result = await asyncio.wait_for(
            perform_search(query),
            timeout=timeout
        )
        return result
        
    except asyncio.TimeoutError:
        return f"Error: Search timed out after {timeout} seconds"
    except Exception as e:
        return f"Error: {str(e)}"
```

---

## Advanced Tool Patterns

### Tool Composition

```python
@tool
def get_user_data(user_id: str) -> dict:
    """Get user data."""
    return {"name": "Alice", "email": "alice@example.com"}

@tool
def send_notification(email: str, message: str) -> str:
    """Send notification."""
    return f"Sent to {email}: {message}"

# Composite tool
@tool
def notify_user(user_id: str, message: str) -> str:
    """Get user and send notification."""
    # Use other tools
    user = get_user_data.invoke({"user_id": user_id})
    result = send_notification.invoke({
        "email": user["email"],
        "message": message
    })
    return result
```

### Conditional Tools

```python
@tool
def conditional_search(
    query: str,
    search_type: Literal["web", "database", "files"]
) -> str:
    """Search using different backends."""
    if search_type == "web":
        return web_search(query)
    elif search_type == "database":
        return database_search(query)
    elif search_type == "files":
        return file_search(query)
    else:
        return "Error: Unknown search type"
```

### Tool Chaining

```python
class ToolChain:
    """Chain multiple tools together."""
    
    def __init__(self, tools: list):
        self.tools = {t.name: t for t in tools}
    
    @tool
    def execute_chain(self, steps: List[Dict[str, any]]) -> str:
        """
        Execute multiple tools in sequence.
        
        Args:
            steps: List of {tool: str, args: dict}
        """
        results = []
        
        for step in steps:
            tool_name = step["tool"]
            tool_args = step["args"]
            
            result = self.tools[tool_name].invoke(tool_args)
            results.append(result)
        
        return results
```

### Tool Caching

```python
from functools import lru_cache
from langchain_core.tools import tool

class CachedTool:
    """Tool with caching."""
    
    def __init__(self):
        self.cache = {}
    
    @tool
    def cached_search(self, query: str) -> str:
        """Search with caching."""
        # Check cache
        if query in self.cache:
            return f"[Cached] {self.cache[query]}"
        
        # Perform search
        result = expensive_search(query)
        
        # Cache result
        self.cache[query] = result
        
        return result

# Or with lru_cache
@lru_cache(maxsize=100)
def search_cached(query: str) -> str:
    return expensive_search(query)

@tool
def search(query: str) -> str:
    """Cached search tool."""
    return search_cached(query)
```

---

## Integration with Act-Operator

**Tool organization in Cast:**

```python
# {{ cookiecutter.python_package }}/tools/__init__.py
from .weather import get_weather
from .calculator import calculator
from .search import search

__all__ = ["get_weather", "calculator", "search"]

# {{ cookiecutter.python_package }}/tools/weather.py
from langchain_core.tools import tool

@tool
def get_weather(location: str) -> str:
    """Get weather for location."""
    # Cast-specific implementation
    return f"Weather in {location}"

# {{ cookiecutter.python_package }}/graph.py
from langgraph.prebuilt import ToolNode
from .tools import get_weather, calculator, search

tools = [get_weather, calculator, search]

builder = StateGraph(State)
builder.add_node("tools", ToolNode(tools))
```

---

## Best Practices

1. **Clear descriptions** - LLM decides based on description
2. **Type hints** - Enable proper schema generation
3. **Handle errors** - Return error messages, don't raise
4. **Validate inputs** - Check arguments before processing
5. **Keep focused** - One tool = one purpose
6. **Document parameters** - Clear arg descriptions
7. **Test independently** - Unit test each tool
8. **Async when possible** - For I/O operations
9. **Cache expensive calls** - Avoid duplicate work
10. **Log tool usage** - Track what tools are called

---

## Common Pitfalls

1. **Poor descriptions** - LLM doesn't know when to use
2. **Missing type hints** - Schema generation fails
3. **Too complex** - LLM struggles with complex tools
4. **Unhandled errors** - Crashes agent execution
5. **Side effects** - Tools should be idempotent when possible
6. **Missing validation** - Accept invalid inputs
7. **Sync in async** - Blocking async execution
8. **No caching** - Repeated expensive calls
9. **Too many tools** - LLM gets confused (max 10-15)
10. **Unclear return** - LLM can't interpret results

---

## Troubleshooting

**Tool not being called:**
- Check description is clear and relevant
- Verify tool is in tools list
- Ensure LLM supports tool calling
- Check if query actually needs tool

**Wrong arguments:**
- Add type hints
- Improve parameter descriptions
- Use Pydantic for validation
- Add examples in docstring

**Tool errors:**
- Add try-catch
- Return error messages
- Use ToolNode error handling
- Log errors for debugging

**Slow tool execution:**
- Use async tools
- Add caching
- Set timeouts
- Parallelize when possible

---

## References

- LangChain Tools: https://python.langchain.com/docs/modules/agents/tools/
- @tool decorator: https://python.langchain.com/docs/modules/agents/tools/custom_tools
- ToolNode: https://langchain-ai.github.io/langgraph/reference/prebuilt/#toolnode
- Pydantic: https://docs.pydantic.dev/
