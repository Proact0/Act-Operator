# MCP Adapter Integration

## Table of Contents

- [When to Use This Resource](#when-to-use-this-resource)
- [What is MCP?](#what-is-mcp)
- [Installing MCP Adapters](#installing-mcp-adapters)
- [Basic MCP Integration](#basic-mcp-integration)
  - [Single MCP Server](#single-mcp-server)
  - [Multiple MCP Servers](#multiple-mcp-servers)
- [Transport Protocols](#transport-protocols)
  - [1. stdio (Local Subprocess)](#1-stdio-local-subprocess)
  - [2. HTTP/HTTPS (Remote Server)](#2-httphttps-remote-server)
  - [3. SSE (Server-Sent Events)](#3-sse-server-sent-events)
- [Using MCP Tools in Nodes](#using-mcp-tools-in-nodes)
- [Agent Pattern with MCP Tools](#agent-pattern-with-mcp-tools)
- [Dynamic Tool Selection](#dynamic-tool-selection)
- [Configuration Management](#configuration-management)
  - [Act Project Pattern](#act-project-pattern)
- [Error Handling](#error-handling)
- [Common Use Cases](#common-use-cases)
  - [1. Filesystem Access](#1-filesystem-access)
  - [2. Database Queries](#2-database-queries)
  - [3. External APIs](#3-external-apis)
- [Common Mistakes](#common-mistakes)
- [References](#references)

## When to Use This Resource
Read this when integrating Model Context Protocol (MCP) servers to access tools from external MCP-compatible services.

## What is MCP?

**Model Context Protocol (MCP)** = Anthropic's standard for connecting LLM applications to external tools and data sources.

**MCP Server** = Service providing tools via MCP protocol.
**MCP Adapter** = LangChain component that converts MCP tools to LangChain tools.

**Key distinction:**
- **MCP Server:** You're consuming tools FROM an MCP server
- **MCP Adapter:** Converts MCP tools to use in LangGraph

⚠️ **Act projects use MCP Adapter, NOT MCP Server implementation.**

## Installing MCP Adapters

```bash
uv add --package {cast-slug-name} langchain-mcp-adapters
```

## Basic MCP Integration

### Single MCP Server

```python
from langchain_mcp_adapters import MultiServerMCPClient

# Configure MCP server connection
mcp_config = {
    "my_server": {
        "transport": "stdio",  # Local subprocess
        "command": "python",
        "args": ["-m", "mcp_server_module"],
        "env": {}  # Optional environment variables
    }
}

# Create MCP client
mcp_client = MultiServerMCPClient(mcp_config)

# Get tools from MCP server
tools = mcp_client.get_tools()

# Use tools in LangGraph
from langgraph.prebuilt import ToolNode

tool_node = ToolNode(tools)
builder.add_node("tools", tool_node)
```

### Multiple MCP Servers

```python
mcp_config = {
    "filesystem": {
        "transport": "stdio",
        "command": "mcp-server-filesystem",
        "args": ["--root", "/data"]
    },
    "database": {
        "transport": "http",
        "url": "http://localhost:8000/mcp"
    },
    "search": {
        "transport": "sse",  # Server-sent events
        "url": "https://search-mcp.example.com/sse"
    }
}

mcp_client = MultiServerMCPClient(mcp_config)

# Get all tools from all servers
all_tools = mcp_client.get_tools()

# Or get tools from specific server
fs_tools = mcp_client.get_tools(server_name="filesystem")
```

## Transport Protocols

### 1. stdio (Local Subprocess)
**When:** MCP server runs as local subprocess.

```python
{
    "local_server": {
        "transport": "stdio",
        "command": "python",
        "args": ["-m", "my_mcp_server"],
        "env": {"API_KEY": "xyz"}
    }
}
```

### 2. HTTP/HTTPS (Remote Server)
**When:** MCP server is HTTP endpoint.

```python
{
    "remote_server": {
        "transport": "http",
        "url": "https://mcp-server.example.com/api"
    }
}
```

### 3. SSE (Server-Sent Events)
**When:** Real-time streaming from MCP server.

```python
{
    "streaming_server": {
        "transport": "sse",
        "url": "https://mcp-server.example.com/sse"
    }
}
```

## Using MCP Tools in Nodes

```python
from casts.base_node import BaseNode
from langchain_mcp_adapters import MultiServerMCPClient

class MCPToolNode(BaseNode):
    """Calls MCP tools based on state."""

    def __init__(self, mcp_config: dict, **kwargs):
        super().__init__(**kwargs)
        self.mcp_client = MultiServerMCPClient(mcp_config)
        self.tools = {t.name: t for t in self.mcp_client.get_tools()}

    def execute(self, state) -> dict:
        tool_name = state.get("tool_to_call")
        tool_args = state.get("tool_args", {})

        if tool_name not in self.tools:
            return {"error": f"Tool {tool_name} not found"}

        try:
            result = self.tools[tool_name].invoke(tool_args)
            return {"tool_result": result}
        except Exception as e:
            return {"error": str(e)}
```

## Agent Pattern with MCP Tools

```python
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_mcp_adapters import MultiServerMCPClient

# Setup MCP
mcp_config = {
    "my_server": {
        "transport": "stdio",
        "command": "mcp-server",
        "args": []
    }
}

mcp_client = MultiServerMCPClient(mcp_config)
tools = mcp_client.get_tools()

# Create agent
llm = ChatOpenAI(model="gpt-4").bind_tools(tools)
tool_node = ToolNode(tools)

# Build graph
class AgentState(TypedDict):
    messages: Annotated[list[dict], add]

builder = StateGraph(AgentState)

# Agent node
def agent_node(state: AgentState) -> dict:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

builder.add_node("agent", agent_node)
builder.add_node("tools", tool_node)

# Routing
def should_continue(state: AgentState) -> str:
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tools"
    return END

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
builder.add_edge("tools", "agent")

graph = builder.compile()
```

## Dynamic Tool Selection

```python
class DynamicMCPNode(BaseNode):
    """Dynamically selects and calls MCP tools."""

    def __init__(self, mcp_config: dict, **kwargs):
        super().__init__(**kwargs)
        self.mcp_client = MultiServerMCPClient(mcp_config)

    def execute(self, state) -> dict:
        # Get tools matching criteria
        required_capability = state.get("required_capability")

        relevant_tools = [
            t for t in self.mcp_client.get_tools()
            if required_capability in t.description.lower()
        ]

        if not relevant_tools:
            return {"error": "No suitable tools found"}

        # Use first matching tool
        tool = relevant_tools[0]
        result = tool.invoke(state.get("tool_args", {}))

        return {"result": result, "tool_used": tool.name}
```

## Configuration Management

### Act Project Pattern

```python
# config/mcp_config.yaml
mcp_servers:
  filesystem:
    transport: stdio
    command: mcp-server-filesystem
    args:
      - --root
      - /data

  search:
    transport: http
    url: ${SEARCH_MCP_URL}  # From environment
```

```python
# casts/{ cast_name }/graph.py
import yaml
from pathlib import Path

class MyGraph(BaseGraph):
    def build(self):
        # Load MCP config
        config_path = Path("config/mcp_config.yaml")
        with open(config_path) as f:
            mcp_config = yaml.safe_load(f)["mcp_servers"]

        # Create MCP client
        mcp_client = MultiServerMCPClient(mcp_config)
        tools = mcp_client.get_tools()

        # Build graph with tools
        builder = StateGraph(MyState)
        # ...
```

## Error Handling

```python
class RobustMCPNode(BaseNode):
    def __init__(self, mcp_config: dict, **kwargs):
        super().__init__(**kwargs)
        try:
            self.mcp_client = MultiServerMCPClient(mcp_config)
            self.tools = self.mcp_client.get_tools()
        except Exception as e:
            self.log(f"MCP initialization failed: {e}")
            self.tools = []

    def execute(self, state) -> dict:
        if not self.tools:
            return {"error": "MCP tools not available"}

        tool_name = state.get("tool_name")
        tool = next((t for t in self.tools if t.name == tool_name), None)

        if not tool:
            return {"error": f"Tool {tool_name} not found"}

        try:
            result = tool.invoke(state.get("args", {}))
            return {"result": result}
        except Exception as e:
            self.log(f"MCP tool error: {e}")
            return {"error": str(e), "tool_name": tool_name}
```

## Common Use Cases

### 1. Filesystem Access
```python
mcp_config = {
    "filesystem": {
        "transport": "stdio",
        "command": "mcp-server-filesystem",
        "args": ["--root", "/workspace"]
    }
}

# Agent can now read/write files via MCP tools
```

### 2. Database Queries
```python
mcp_config = {
    "database": {
        "transport": "stdio",
        "command": "mcp-server-postgres",
        "args": ["--connection-string", conn_str]
    }
}

# Agent can query database via MCP tools
```

### 3. External APIs
```python
mcp_config = {
    "api_gateway": {
        "transport": "http",
        "url": "https://api-mcp.example.com"
    }
}

# Agent can call external APIs via MCP
```

## Common Mistakes

❌ **Confusing MCP Server vs MCP Adapter**
```python
# ❌ Act projects don't implement MCP servers
# ✅ Act projects USE MCP adapters to consume tools
```

❌ **Not handling MCP initialization errors**
```python
# ❌ Will crash if MCP server unavailable
mcp_client = MultiServerMCPClient(config)

# ✅ Handle errors
try:
    mcp_client = MultiServerMCPClient(config)
except Exception as e:
    logger.error(f"MCP init failed: {e}")
    # Use fallback or disable MCP features
```

❌ **Hardcoding MCP config**
```python
# ❌ Config in code
mcp_config = {"server": {"command": "/usr/bin/mcp-server"}}

# ✅ External configuration
mcp_config = load_config("config/mcp_config.yaml")
```

