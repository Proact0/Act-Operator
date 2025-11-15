# Prebuilt Components

## When to Use This Resource

Read this for shortcuts using LangGraph's prebuilt nodes and agent patterns.

## create_react_agent

**Quick ReAct agent setup:**

```python
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from modules.tools import calculator, search_database

# Create model and tools
model = ChatAnthropic(model="claude-sonnet-4")
tools = [calculator, search_database]

# One-line agent creation
app = create_react_agent(model, tools)

# Use it
result = app.invoke({
    "messages": [{"role": "user", "content": "What's 5 + 3?"}]
})
```

**What it creates:**
- StateGraph with messages state
- Agent node (LLM with tools)
- ToolNode for tool execution
- Conditional routing (agent ↔ tools)
- Compiled graph ready to use

**When to use:**
- Quick prototypes
- Standard ReAct pattern
- No custom state needed

**When NOT to use:**
- Custom state schema required
- Need custom nodes/edges
- Act project structure (use BaseGraph)

## ToolNode

**Executes tool calls from AI messages:**

```python
from langgraph.prebuilt import ToolNode
from modules.tools import tool1, tool2

# Create tool executor
tool_node = ToolNode([tool1, tool2])

# Add to graph
builder.add_node("tools", tool_node)
```

**What it does:**
- Receives AIMessage with tool_calls
- Executes each tool
- Returns ToolMessages
- Handles errors automatically

## In Act Projects

⚠️ **Prebuilt vs Act patterns:**

```python
# ❌ DON'T USE: create_react_agent in Act projects
app = create_react_agent(model, tools)

# ✅ DO USE: Custom graph with BaseGraph
class MyAgentGraph(BaseGraph):
    def build(self):
        builder = StateGraph(MyAgentState)
        builder.add_node("agent", AgentNode(model))
        builder.add_node("tools", ToolNode(tools))  # ToolNode OK!
        # ... rest of graph
        return builder.compile()
```

**Why:** Act projects use BaseGraph pattern for consistency, but ToolNode is fine to use.

## Decision Framework

```
Quick prototype?
  → create_react_agent

Production Act project?
  → Custom graph with BaseGraph
  → Use ToolNode for tool execution

Need custom state?
  → Don't use create_react_agent

Standard tool execution?
  → Use ToolNode
```

## References

- Custom graphs: `01-core/graph.md`
- Tools: `02-tools/tool-patterns.md`
