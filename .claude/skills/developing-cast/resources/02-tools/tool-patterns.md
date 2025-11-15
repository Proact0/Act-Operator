# Tool Patterns

## When to Use This Resource

Read this when integrating tools into graphs, using ToolNode, or accessing tool execution context.

## Key Concepts

**ToolNode:** Prebuilt node that executes tool calls from LLM messages.

**ToolRuntime:** Context available during tool execution (deprecated in 1.0, use Runtime).

**Tool Binding:** Attaching tools to LLM for function calling.

**Tool Calls:** LLM's requests to invoke specific tools.

## Tool Integration Patterns

### Pattern 1: Using ToolNode (Recommended)

**When to use:** Standard tool execution in agent loops

```python
from langgraph.prebuilt import ToolNode
from langchain_anthropic import ChatAnthropic
from modules.tools import calculator, search_database

# In graph build()
tools = [calculator, search_database]
model = ChatAnthropic(model="claude-sonnet-4").bind_tools(tools)

builder.add_node("agent", AgentNode(model))
builder.add_node("tools", ToolNode(tools))  # Handles tool execution

# Conditional edge from agent
builder.add_conditional_edges(
    "agent",
    should_continue,
    {"continue": "tools", "end": END}
)

# Loop back to agent after tools
builder.add_edge("tools", "agent")
```

**What ToolNode does:**
- Receives AIMessage with tool_calls
- Executes each tool
- Returns ToolMessage with results
- Handles errors automatically

### Pattern 2: Custom Tool Execution Node

**When to use:** Need custom logic around tool execution

```python
from casts.base_node import BaseNode
from langchain_core.messages import AIMessage, ToolMessage
from modules.tools import calculator, search_database

class CustomToolNode(BaseNode):
    """Custom tool execution with logging."""

    def __init__(self, tools: list, **kwargs):
        super().__init__(**kwargs)
        self.tools_by_name = {t.name: t for t in tools}

    def execute(self, state: AgentState) -> dict:
        """Execute tool calls from last message."""
        last_message = state["messages"][-1]

        if not isinstance(last_message, AIMessage):
            return {}

        if not last_message.tool_calls:
            return {}

        tool_messages = []

        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            self.log(f"Executing tool: {tool_name}", args=tool_args)

            try:
                tool = self.tools_by_name[tool_name]
                result = tool.invoke(tool_args)

                tool_messages.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"],
                    )
                )

            except Exception as e:
                self.log(f"Tool error: {tool_name}", error=str(e))
                tool_messages.append(
                    ToolMessage(
                        content=f"Error: {str(e)}",
                        tool_call_id=tool_call["id"],
                        is_error=True,
                    )
                )

        return {"messages": tool_messages}
```

### Pattern 3: Tool Binding to LLM

**When to use:** Agent needs to decide which tools to call

```python
from langchain_anthropic import ChatAnthropic
from modules.tools import calculator, search_database, fetch_url

# Create LLM with tools
tools = [calculator, search_database, fetch_url]
model = ChatAnthropic(model="claude-sonnet-4")

# Bind tools
model_with_tools = model.bind_tools(tools)

# Use in node
class AgentNode(BaseNode):
    def __init__(self, model, **kwargs):
        super().__init__(**kwargs)
        self.model = model

    def execute(self, state: AgentState) -> dict:
        messages = state["messages"]
        response = self.model.invoke(messages)  # May include tool_calls
        return {"messages": [response]}
```

### Pattern 4: Selective Tool Binding

**When to use:** Different nodes need different tools

```python
from modules.tools import calculator, search_database, admin_tool

# Research node: search + calculator
research_tools = [search_database, calculator]
research_model = model.bind_tools(research_tools)

# Admin node: admin tools only
admin_tools = [admin_tool]
admin_model = model.bind_tools(admin_tools)

# Different nodes
builder.add_node("research", AgentNode(research_model))
builder.add_node("admin", AgentNode(admin_model))
```

## Tool Execution Flow

```
Agent Node
  ↓
Invokes LLM with bound tools
  ↓
LLM returns AIMessage with tool_calls
  ↓
Conditional edge checks tool_calls
  ↓
Routes to ToolNode if tools needed
  ↓
ToolNode executes each tool
  ↓
ToolNode returns ToolMessages
  ↓
Edge loops back to Agent
  ↓
Agent processes ToolMessages
  ↓
Continues or ends
```

## should_continue Pattern

### Standard Implementation

```python
# File: casts/my_agent/conditions.py
from casts.my_agent.state import AgentState
from langchain_core.messages import AIMessage

def should_continue(state: AgentState) -> str:
    """Check if agent wants to call tools.

    Returns:
        'continue' if tools to call, 'end' otherwise
    """
    last_message = state["messages"][-1]

    # Check if last message has tool calls
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "continue"
    else:
        return "end"
```

### With Iteration Limit

```python
def should_continue(state: AgentState) -> str:
    """Check continuation with iteration limit."""
    last_message = state["messages"][-1]
    iterations = state.get("iteration_count", 0)

    # Max iterations reached
    if iterations >= 10:
        return "end"

    # Has tool calls
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "continue"
    else:
        return "end"
```

## Accessing Tool Results in Agent

### Pattern: Agent Processes Tool Results

```python
class AgentNode(BaseNode):
    def execute(self, state: AgentState) -> dict:
        messages = state["messages"]

        # LLM sees full conversation including ToolMessages
        response = self.model.invoke(messages)

        # Response may:
        # 1. Call more tools (if tool results suggest it)
        # 2. Provide final answer based on tool results
        # 3. Ask clarifying question

        return {
            "messages": [response],
            "iteration_count": state.get("iteration_count", 0) + 1,
        }
```

## Tool Error Handling

### Pattern: Graceful Error Handling

```python
from langchain_core.messages import ToolMessage

class RobustToolNode(BaseNode):
    def __init__(self, tools, **kwargs):
        super().__init__(**kwargs)
        self.tools_by_name = {t.name: t for t in tools}

    def execute(self, state: AgentState) -> dict:
        last_message = state["messages"][-1]
        tool_messages = []

        for tool_call in last_message.tool_calls:
            try:
                tool = self.tools_by_name[tool_call["name"]]
                result = tool.invoke(tool_call["args"])

                tool_messages.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"],
                    )
                )

            except KeyError:
                # Tool not found
                tool_messages.append(
                    ToolMessage(
                        content=f"Error: Unknown tool '{tool_call['name']}'",
                        tool_call_id=tool_call["id"],
                        is_error=True,
                    )
                )

            except Exception as e:
                # Tool execution error
                tool_messages.append(
                    ToolMessage(
                        content=f"Error executing tool: {str(e)}",
                        tool_call_id=tool_call["id"],
                        is_error=True,
                    )
                )

        return {"messages": tool_messages}
```

## Common Patterns

### Pattern: ReAct Agent with Tools

```python
# Complete ReAct implementation
from langgraph.prebuilt import ToolNode

class ReactGraph(BaseGraph):
    def build(self):
        builder = StateGraph(AgentState)

        tools = [calculator, search_database]
        model = ChatAnthropic(model="claude-sonnet-4").bind_tools(tools)

        builder.add_node("agent", AgentNode(model))
        builder.add_node("tools", ToolNode(tools))

        builder.set_entry_point("agent")

        builder.add_conditional_edges(
            "agent",
            should_continue,
            {"continue": "tools", "end": END}
        )

        builder.add_edge("tools", "agent")

        return builder.compile()
```

### Pattern: Multi-Step Tool Pipeline

```python
# Sequential tool execution
builder.add_node("fetch", FetchToolNode())
builder.add_node("process", ProcessToolNode())
builder.add_node("save", SaveToolNode())

builder.add_edge("fetch", "process")
builder.add_edge("process", "save")
```

## Common Mistakes

### ❌ Forgetting to Bind Tools

```python
# BAD
model = ChatAnthropic(model="claude-sonnet-4")
# Model doesn't know about tools!
```

**Fix:**
```python
# GOOD
model = ChatAnthropic(model="claude-sonnet-4").bind_tools(tools)
```

### ❌ Wrong Message Type Check

```python
# BAD
if state["messages"][-1].tool_calls:  # May fail if not AIMessage
    return "continue"
```

**Fix:**
```python
# GOOD
last_message = state["messages"][-1]
if isinstance(last_message, AIMessage) and last_message.tool_calls:
    return "continue"
```

### ❌ No Loop Back to Agent

```python
# BAD
builder.add_conditional_edges("agent", should_continue, {"continue": "tools", "end": END})
# No edge from tools back to agent - dead end!
```

**Fix:**
```python
# GOOD
builder.add_conditional_edges("agent", should_continue, {"continue": "tools", "end": END})
builder.add_edge("tools", "agent")  # Loop back
```

## Decision Framework

```
Need standard tool execution?
  → Use ToolNode (prebuilt)

Need custom tool logic?
  → Create custom tool node

Agent needs different tools per branch?
  → Bind tools selectively per node

Need tool error handling?
  → Use ToolMessage with is_error=True

Need iteration limit?
  → Add counter in should_continue

Tools in agent loop?
  → Use ReAct pattern (agent ↔ tools)
```

## Act Project Conventions

⚠️ **Tools location:**
- Import from: `modules.tools`
- Never create tools in cast directory

⚠️ **Tool binding:**
- Bind tools to LLM before passing to node
- Store bound model in node instance

⚠️ **Conditional edges:**
- Define should_continue in conditions.py
- Check isinstance(AIMessage) before accessing tool_calls

## Anti-Patterns

- ❌ **Creating tools inline** → Define in modules/tools
- ❌ **Binding all tools to all nodes** → Bind selectively
- ❌ **No error handling in ToolNode** → Handle exceptions
- ❌ **Infinite tool loops** → Add iteration limit
- ❌ **Not checking message type** → Use isinstance()

## References

- Tool creation: `02-tools/creating-tools.md`
- Related: `01-core/edges.md`, `01-core/nodes.md`
- Prebuilt components: `05-patterns/prebuilt-components.md`
