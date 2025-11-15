# MCP Adapter

## When to Use This Resource

Read this for integrating Model Context Protocol (MCP) tools into LangGraph casts.

## Key Concept

**MCP:** Protocol for exposing tools, prompts, and resources from external servers.

**MCP Adapter:** Converts MCP server tools into LangChain tools usable in LangGraph.

**Note:** This is MCP **client/adapter**, not MCP server creation.

## Installation

```bash
pip install langchain-mcp-adapters
```

## Basic Usage

```python
from langchain_mcp import MultiServerMCPClient

# Connect to MCP servers
client = MultiServerMCPClient()

# Add servers (stdio, http, or sse transports)
await client.add_server(
    "filesystem",
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"]
)

await client.add_server(
    "weather",
    url="http://localhost:3000/mcp"
)

# Get tools from all servers
mcp_tools = await client.get_tools()

# Use in LangGraph
model = ChatAnthropic(model="claude-sonnet-4").bind_tools(mcp_tools)
```

## Integration with LangGraph

```python
from langchain_mcp import MultiServerMCPClient
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import ToolNode

class MCPGraph(BaseGraph):
    def __init__(self):
        super().__init__()
        self.client = MultiServerMCPClient()

    async def setup_mcp(self):
        """Initialize MCP connections."""
        await self.client.add_server(
            "tools",
            command="npx",
            args=["-y", "mcp-server-package"]
        )

    def build(self):
        builder = StateGraph(AgentState)

        # Get MCP tools (must call setup_mcp first)
        # In practice, setup in async context before build
        mcp_tools = []  # Retrieved from self.client.get_tools()

        model = ChatAnthropic(model="claude-sonnet-4").bind_tools(mcp_tools)

        builder.add_node("agent", AgentNode(model))
        builder.add_node("tools", ToolNode(mcp_tools))

        # Standard ReAct pattern
        builder.add_conditional_edges(
            "agent",
            should_continue,
            {"continue": "tools", "end": END}
        )
        builder.add_edge("tools", "agent")

        return builder.compile()
```

## MCP Server Types

### Stdio Transport

```python
await client.add_server(
    "filesystem",
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"]
)
```

### HTTP Transport

```python
await client.add_server(
    "api",
    url="http://localhost:3000/mcp"
)
```

### SSE Transport

```python
await client.add_server(
    "events",
    url="http://localhost:3000/sse",
    transport="sse"
)
```

## Common Patterns

### Multiple MCP Servers

```python
# Combine tools from multiple MCP servers
client = MultiServerMCPClient()

await client.add_server("filesystem", command="...", args=[...])
await client.add_server("database", command="...", args=[...])
await client.add_server("api", url="http://...")

# All tools available
all_tools = await client.get_tools()
```

### MCP + Local Tools

```python
from modules.tools import local_tool

# Combine MCP and local tools
mcp_tools = await client.get_tools()
all_tools = [local_tool] + mcp_tools

model = model.bind_tools(all_tools)
```

## Decision Framework

```
Need tools from external MCP server?
  → Use MultiServerMCPClient

Multiple MCP servers?
  → Add each with client.add_server()

Combine with local tools?
  → Merge lists: local_tools + mcp_tools

Need to create MCP server?
  → See MCP server documentation (not LangGraph)
```

## Common Mistakes

### ❌ Not Awaiting Async Methods

```python
# BAD
client.add_server(...)  # Missing await!
```

**Fix:**
```python
# GOOD
await client.add_server(...)
```

## Act Project Conventions

⚠️ **MCP setup:**
- Initialize client in graph __init__
- Setup servers in async method
- Use in build() after setup

⚠️ **Local tools still in modules/tools:**
- MCP tools are external
- Local tools follow Act conventions

## References

- Tools: `02-tools/creating-tools.md`
- Tool patterns: `02-tools/tool-patterns.md`
- MCP docs: https://docs.langchain.com/oss/python/langchain/mcp
