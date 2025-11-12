# LangChain Agents Guide for LangGraph

Comprehensive guide to implementing LangChain agents in LangGraph applications, covering agent patterns, tool-calling, and integration with Cast development.

## Table of Contents

1. [Introduction](#introduction)
2. [Agent Fundamentals](#agent-fundamentals)
   - [What is an Agent](#what-is-an-agent)
   - [Agent vs Chain](#agent-vs-chain)
   - [Agent Components](#agent-components)
   - [Agent Lifecycle](#agent-lifecycle)
3. [Agent Types](#agent-types)
   - [ReAct Agents](#react-agents)
   - [OpenAI Functions Agents](#openai-functions-agents)
   - [Structured Chat Agents](#structured-chat-agents)
   - [Tool-Calling Agents](#tool-calling-agents)
4. [Tool-Calling Agents with LLMs](#tool-calling-agents-with-llms)
   - [Native Tool Calling](#native-tool-calling)
   - [bind_tools Method](#bind_tools-method)
   - [Tool Call Format](#tool-call-format)
   - [Processing Tool Results](#processing-tool-results)
5. [Creating Agent Nodes in LangGraph](#creating-agent-nodes-in-langgraph)
   - [Basic Agent Node](#basic-agent-node)
   - [Agent with State](#agent-with-state)
   - [Agent with Tools](#agent-with-tools)
   - [Multi-Step Agent](#multi-step-agent)
6. [Agent Executor Patterns](#agent-executor-patterns)
   - [Simple Executor](#simple-executor)
   - [Iterative Executor](#iterative-executor)
   - [Conditional Executor](#conditional-executor)
   - [Parallel Tool Execution](#parallel-tool-execution)
7. [Integration with Act-Operator](#integration-with-act-operator)
   - [Agent Node in Cast](#agent-node-in-cast)
   - [State Management](#state-management)
   - [Tool Integration](#tool-integration)
   - [Error Handling](#error-handling)
8. [Advanced Patterns](#advanced-patterns)
   - [Multi-Agent Systems](#multi-agent-systems)
   - [Hierarchical Agents](#hierarchical-agents)
   - [Agent with Memory](#agent-with-memory)
   - [Streaming Agents](#streaming-agents)
9. [Best Practices](#best-practices)
10. [Common Pitfalls](#common-pitfalls)
11. [Troubleshooting](#troubleshooting)
12. [References](#references)

---

## Introduction

Agents in LangChain are systems that use LLMs to decide which tools to call and what actions to take. In LangGraph, agents become nodes that can reason about state and make decisions about graph execution flow.

**What you'll learn:**
- Different agent types and when to use them
- Implementing tool-calling agents with modern LLMs
- Creating agent nodes in LangGraph
- Best practices for agent design
- Integration with Act-Operator Casts

**Key concepts:**
- **Agent**: LLM-powered decision maker
- **Tools**: Functions the agent can call
- **Action**: Decision to call a tool
- **Observation**: Result from tool execution

---

## Agent Fundamentals

### What is an Agent

**Definition:**
```
Agent = LLM + Tools + Decision Loop

1. Receive input/state
2. LLM decides: What tool to call? What arguments?
3. Execute tool(s)
4. LLM processes results
5. Repeat or return final answer
```

**Simple agent:**
```python
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool

# Define tools
def get_weather(location: str) -> str:
    return f"Weather in {location}: 72°F, sunny"

tools = [
    Tool(
        name="get_weather",
        func=get_weather,
        description="Get current weather for a location"
    )
]

# Create agent
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)

# Run
result = agent_executor.invoke({"input": "What's the weather in SF?"})
```

### Agent vs Chain

**Chain:**
```python
# Predefined steps, always the same
chain = prompt | llm | output_parser
result = chain.invoke({"query": "..."})

# Flow: Input → Prompt → LLM → Parse → Output
```

**Agent:**
```python
# Dynamic steps, decided by LLM
agent_executor = AgentExecutor(agent=agent, tools=tools)
result = agent_executor.invoke({"input": "..."})

# Flow: Input → LLM decides → Call tool(s) → LLM processes → ...
```

**When to use:**
- **Chain**: Fixed workflow, no decision making needed
- **Agent**: Dynamic decisions, tool selection, iterative problem solving

### Agent Components

**Components:**
```python
# 1. LLM: Decision maker
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")

# 2. Tools: Available functions
tools = [weather_tool, calculator_tool, search_tool]

# 3. Prompt: Instructions for agent
prompt = PromptTemplate.from_template(
    "You are a helpful assistant. Use tools when needed.\n"
    "Question: {input}\n"
    "Thought:"
)

# 4. Agent: Combines LLM + Prompt + Tool definitions
agent = create_react_agent(llm, tools, prompt)

# 5. Executor: Runs agent loop
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
```

### Agent Lifecycle

**Execution flow:**
```
1. Input received
   ↓
2. LLM generates thought + action
   ↓
3. Action parsed (tool name + args)
   ↓
4. Tool executed
   ↓
5. Observation added to history
   ↓
6. LLM processes observation
   ↓
7. Decision: Continue (go to 2) or Finish
   ↓
8. Return final answer
```

**Example execution:**
```
Input: "What's 25 * 4 and what's the weather in that many degrees north?"

Step 1:
  Thought: I need to calculate 25 * 4
  Action: calculator(25 * 4)
  Observation: 100

Step 2:
  Thought: Now I need weather at 100 degrees north
  Action: get_weather("100°N")
  Observation: Invalid location (out of range)

Step 3:
  Thought: 100 degrees is invalid. Let me interpret differently.
  Final Answer: 25 * 4 = 100. However, 100 degrees north latitude is invalid...
```

---

## Agent Types

### ReAct Agents

**ReAct = Reasoning + Acting**

```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate

# ReAct prompt template
template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

prompt = PromptTemplate.from_template(template)

# Create ReAct agent
agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Execute
result = executor.invoke({"input": "What's the weather in SF?"})
```

**When to use:**
- General purpose reasoning
- Complex multi-step problems
- Need explicit reasoning traces
- Works with most LLMs

### OpenAI Functions Agents

**Uses OpenAI's function calling:**

```python
from langchain.agents import create_openai_functions_agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4", temperature=0)

# Create functions agent
agent = create_openai_functions_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

# Tools automatically converted to function schemas
result = executor.invoke({"input": "Get weather in NYC"})
```

**Features:**
- Clean function calling format
- Better tool argument parsing
- Works with OpenAI models
- Structured outputs

### Structured Chat Agents

**For multi-input tools:**

```python
from langchain.agents import create_structured_chat_agent

# Tool with multiple parameters
@tool
def search_emails(sender: str, subject: str, days_ago: int) -> str:
    """Search emails by sender, subject, and date."""
    return f"Found 3 emails from {sender} about {subject}"

tools = [search_emails]

# Create structured chat agent
agent = create_structured_chat_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

result = executor.invoke({
    "input": "Find emails from john@example.com about project updates from last 7 days"
})
```

### Tool-Calling Agents

**Modern approach with native tool calling:**

```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")

# Bind tools to LLM
llm_with_tools = llm.bind_tools(tools)

# Use directly (no AgentExecutor needed)
response = llm_with_tools.invoke([
    {"role": "user", "content": "What's the weather in Boston?"}
])

# Check if tool calls present
if response.tool_calls:
    for tool_call in response.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        # Execute tool...
```

---

## Tool-Calling Agents with LLMs

### Native Tool Calling

**Modern LLMs support native tool calling:**

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool

@tool
def get_weather(location: str) -> str:
    """Get current weather for a location."""
    return f"Weather in {location}: 72°F, sunny"

@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    return str(eval(expression))

tools = [get_weather, calculator]

# Bind tools
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
llm_with_tools = llm.bind_tools(tools)

# Invoke
response = llm_with_tools.invoke("What's 25 * 4?")

# Response contains tool_calls
print(response.tool_calls)
# [{"name": "calculator", "args": {"expression": "25 * 4"}, "id": "..."}]
```

### bind_tools Method

**Binding tools to LLM:**

```python
from langchain_core.tools import tool

@tool
def get_user_info(user_id: str) -> dict:
    """Get user information by ID."""
    return {"name": "Alice", "email": "alice@example.com"}

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email."""
    return f"Email sent to {to}"

tools = [get_user_info, send_email]

# Bind all tools
llm_with_tools = llm.bind_tools(tools)

# Or bind specific tools
llm_with_limited_tools = llm.bind_tools([get_user_info])

# With tool_choice
llm_must_use_tool = llm.bind_tools(
    tools,
    tool_choice="required"  # Must call at least one tool
)

llm_specific_tool = llm.bind_tools(
    tools,
    tool_choice="get_weather"  # Must call this specific tool
)
```

### Tool Call Format

**Tool call structure:**

```python
# Response from LLM with tool call
response = llm_with_tools.invoke("Get weather in SF")

# AIMessage with tool_calls
response.tool_calls
# [
#   {
#     "name": "get_weather",
#     "args": {"location": "San Francisco"},
#     "id": "call_abc123"
#   }
# ]

# Accessing tool call details
for tool_call in response.tool_calls:
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]
    tool_id = tool_call["id"]

    # Execute tool
    result = execute_tool(tool_name, tool_args)

    # Create tool message with result
    from langchain_core.messages import ToolMessage
    tool_message = ToolMessage(
        content=str(result),
        tool_call_id=tool_id
    )
```

### Processing Tool Results

**Execute tools and continue:**

```python
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

def run_agent_step(messages, tools_map):
    """Run one agent step."""
    # Get LLM response
    response = llm_with_tools.invoke(messages)

    # Check for tool calls
    if not response.tool_calls:
        # No tools, return final answer
        return response

    # Execute tools
    messages.append(response)

    for tool_call in response.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_id = tool_call["id"]

        # Execute
        tool_result = tools_map[tool_name].invoke(tool_args)

        # Add tool message
        messages.append(ToolMessage(
            content=str(tool_result),
            tool_call_id=tool_id
        ))

    # Continue with tool results
    return run_agent_step(messages, tools_map)

# Use
tools_map = {tool.name: tool for tool in tools}
messages = [HumanMessage(content="What's the weather in SF?")]
final_response = run_agent_step(messages, tools_map)
```

---

## Creating Agent Nodes in LangGraph

### Basic Agent Node

**Simple agent as LangGraph node:**

```python
from act_operator_lib.base_node import BaseNode
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, ToolMessage
from dataclasses import dataclass
from typing import Annotated
from langgraph.graph.message import add_messages

@dataclass(kw_only=True)
class State:
    messages: Annotated[list, add_messages]

class AgentNode(BaseNode):
    def __init__(self, tools=None, **kwargs):
        super().__init__(**kwargs)
        self.llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
        self.tools = tools or []
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def execute(self, state):
        # Get LLM response with tool calls
        response = self.llm_with_tools.invoke(state.messages)

        # Return as message to add to state
        return {"messages": [response]}
```

### Agent with State

**Agent that works with custom state:**

```python
@dataclass(kw_only=True)
class AgentState:
    messages: Annotated[list, add_messages]
    query: str
    iteration: int = 0
    max_iterations: int = 5

class StatefulAgentNode(BaseNode):
    def __init__(self, tools=None, **kwargs):
        super().__init__(**kwargs)
        self.llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
        self.tools = tools or []
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def execute(self, state):
        self.log(f"Agent iteration {state.iteration}")

        # Check iteration limit
        if state.iteration >= state.max_iterations:
            return {
                "messages": [AIMessage(content="Max iterations reached")],
                "iteration": state.iteration
            }

        # Get response
        response = self.llm_with_tools.invoke(state.messages)

        return {
            "messages": [response],
            "iteration": state.iteration + 1
        }
```

### Agent with Tools

**Complete agent with tool execution:**

```python
from langchain_core.tools import tool

@tool
def get_weather(location: str) -> str:
    """Get current weather for a location."""
    return f"Weather in {location}: 72°F, sunny"

@tool
def calculator(expression: str) -> float:
    """Evaluate a math expression."""
    return eval(expression)

tools = [get_weather, calculator]

class ToolCallingAgentNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
        self.tools = tools
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # Create tools map for execution
        self.tools_map = {tool.name: tool for tool in self.tools}

    def execute(self, state):
        # Get LLM response
        response = self.llm_with_tools.invoke(state.messages)

        # Check if response has tool calls
        if not response.tool_calls:
            # No tools, just return response
            return {"messages": [response]}

        # Has tool calls - these will be processed by separate tool node
        return {"messages": [response]}
```

### Multi-Step Agent

**Agent that runs multiple iterations:**

```python
class MultiStepAgentNode(BaseNode):
    def __init__(self, max_iterations=5, **kwargs):
        super().__init__(**kwargs)
        self.llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
        self.tools = tools
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.tools_map = {tool.name: tool for tool in self.tools}
        self.max_iterations = max_iterations

    def execute(self, state):
        messages = list(state.messages)
        iteration = 0

        while iteration < self.max_iterations:
            # Get LLM response
            response = self.llm_with_tools.invoke(messages)
            messages.append(response)

            # Check if done (no tool calls)
            if not response.tool_calls:
                break

            # Execute tools
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]

                # Execute tool
                result = self.tools_map[tool_name].invoke(tool_args)

                # Add tool message
                messages.append(ToolMessage(
                    content=str(result),
                    tool_call_id=tool_id
                ))

            iteration += 1

        return {"messages": messages}
```

---

## Agent Executor Patterns

### Simple Executor

**Basic agent loop:**

```python
class SimpleAgentExecutor(BaseNode):
    def execute(self, state):
        # Single agent call
        response = self.llm_with_tools.invoke(state.messages)
        return {"messages": [response]}

# In graph
builder.add_node("agent", SimpleAgentExecutor())
builder.add_node("tools", ToolNode(tools))

# Route: agent -> tools if tool_calls, else end
def should_continue(state):
    last_message = state.messages[-1]
    if last_message.tool_calls:
        return "tools"
    return "end"

builder.add_conditional_edges("agent", should_continue)
builder.add_edge("tools", "agent")
```

### Iterative Executor

**Run until completion:**

```python
class IterativeAgentExecutor(BaseNode):
    def __init__(self, max_iterations=10, **kwargs):
        super().__init__(**kwargs)
        self.max_iterations = max_iterations

    def execute(self, state):
        messages = list(state.messages)

        for i in range(self.max_iterations):
            # Agent step
            response = self.llm_with_tools.invoke(messages)
            messages.append(response)

            # Done?
            if not response.tool_calls:
                return {"messages": messages}

            # Execute tools
            for tool_call in response.tool_calls:
                result = self.execute_tool(tool_call)
                messages.append(result)

        # Max iterations reached
        messages.append(AIMessage(content="Max iterations reached"))
        return {"messages": messages}
```

### Conditional Executor

**Different behavior based on state:**

```python
class ConditionalAgentExecutor(BaseNode):
    def execute(self, state):
        # Check if error occurred
        if state.get("error"):
            # Use error-recovery agent
            response = self.recovery_llm.invoke(state.messages)
        elif state.iteration > 5:
            # Use more capable model
            response = self.strong_llm.invoke(state.messages)
        else:
            # Use standard model
            response = self.llm.invoke(state.messages)

        return {"messages": [response]}
```

### Parallel Tool Execution

**Execute multiple tools concurrently:**

```python
import asyncio
from act_operator_lib.base_node import AsyncBaseNode

class ParallelToolAgentNode(AsyncBaseNode):
    async def execute(self, state):
        # Get response with tool calls
        response = await self.llm_with_tools.ainvoke(state.messages)

        if not response.tool_calls:
            return {"messages": [response]}

        # Execute tools in parallel
        async def execute_tool_call(tool_call):
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            result = await self.tools_map[tool_name].ainvoke(tool_args)

            return ToolMessage(
                content=str(result),
                tool_call_id=tool_id
            )

        # Run all tools concurrently
        tool_messages = await asyncio.gather(
            *[execute_tool_call(tc) for tc in response.tool_calls]
        )

        return {"messages": [response] + tool_messages}
```

---

## Integration with Act-Operator

### Agent Node in Cast

**Complete Cast with agent:**

```python
# {{ cookiecutter.python_package }}/nodes/agent.py
from act_operator_lib.base_node import BaseNode
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool

@tool
def get_weather(location: str) -> str:
    """Get weather for location."""
    return f"Weather in {location}: 72°F"

class AgentNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0
        )
        self.tools = [get_weather]
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def execute(self, state):
        response = self.llm_with_tools.invoke(state.messages)
        return {"messages": [response]}

# {{ cookiecutter.python_package }}/graph.py
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from .nodes.agent import AgentNode, get_weather

# Build graph
builder = StateGraph(State)
builder.add_node("agent", AgentNode())
builder.add_node("tools", ToolNode([get_weather]))

# Routing
def should_continue(state):
    last_message = state.messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

builder.set_entry_point("agent")
builder.add_conditional_edges("agent", should_continue)
builder.add_edge("tools", "agent")

graph = builder.compile()
```

### State Management

**Agent with Cast state:**

```python
from typing import Annotated
from dataclasses import dataclass
from langgraph.graph.message import add_messages

@dataclass(kw_only=True)
class CastState:
    messages: Annotated[list, add_messages]
    query: str
    user_id: str
    iteration: int = 0
    max_iterations: int = 10

class CastAgentNode(BaseNode):
    def execute(self, state):
        self.log(f"Iteration {state.iteration}/{state.max_iterations}")

        # Add context to messages if needed
        messages = list(state.messages)

        # Get response
        response = self.llm_with_tools.invoke(messages)

        return {
            "messages": [response],
            "iteration": state.iteration + 1
        }
```

### Tool Integration

**Tools specific to Cast:**

```python
# {{ cookiecutter.python_package }}/tools/cast_tools.py
from langchain_core.tools import tool

@tool
def query_database(query: str) -> str:
    """Query the Cast's database."""
    # Cast-specific logic
    return "Database results"

@tool
def call_api(endpoint: str, params: dict) -> str:
    """Call external API."""
    # Cast-specific API integration
    return "API response"

@tool
def process_data(data: str) -> str:
    """Process data using Cast logic."""
    # Cast-specific processing
    return "Processed data"

# Use in agent
class CastAgentNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
        self.tools = [query_database, call_api, process_data]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
```

### Error Handling

**Robust agent with error handling:**

```python
class RobustAgentNode(BaseNode):
    def execute(self, state):
        try:
            response = self.llm_with_tools.invoke(state.messages)

            # Validate response
            if not response.content and not response.tool_calls:
                self.logger.warning("Empty response from LLM")
                return {
                    "messages": [AIMessage(content="I apologize, I couldn't generate a response.")],
                    "error": "empty_response"
                }

            return {"messages": [response]}

        except Exception as e:
            self.logger.error(f"Agent error: {e}", exc_info=True)
            return {
                "messages": [AIMessage(content=f"An error occurred: {str(e)}")],
                "error": str(e)
            }
```

---

## Advanced Patterns

### Multi-Agent Systems

**Multiple agents working together:**

```python
class SpecialistAgentNode(BaseNode):
    """Agent specialized for specific domain."""

    def __init__(self, specialty, tools, **kwargs):
        super().__init__(**kwargs)
        self.specialty = specialty
        self.llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
        self.llm_with_tools = self.llm.bind_tools(tools)

    def execute(self, state):
        # Add specialty context
        messages = list(state.messages)
        messages.insert(0, SystemMessage(
            content=f"You are a {self.specialty} specialist."
        ))

        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}

# Create specialists
weather_agent = SpecialistAgentNode(
    "weather",
    [get_weather, get_forecast]
)

finance_agent = SpecialistAgentNode(
    "finance",
    [get_stock_price, calculate_returns]
)

# Router decides which agent
def route_to_specialist(state):
    query = state.messages[-1].content.lower()
    if "weather" in query or "forecast" in query:
        return "weather_agent"
    elif "stock" in query or "finance" in query:
        return "finance_agent"
    return "general_agent"

builder.add_node("weather_agent", weather_agent)
builder.add_node("finance_agent", finance_agent)
builder.add_conditional_edges("router", route_to_specialist)
```

### Hierarchical Agents

**Manager agent coordinates worker agents:**

```python
class ManagerAgentNode(BaseNode):
    """Delegates tasks to worker agents."""

    def execute(self, state):
        # Manager decides what to delegate
        response = self.llm.invoke([
            SystemMessage(content="You are a manager. Delegate tasks to workers."),
            *state.messages
        ])

        # Parse delegation
        if "delegate to researcher" in response.content.lower():
            return {"next_agent": "researcher", "messages": [response]}
        elif "delegate to writer" in response.content.lower():
            return {"next_agent": "writer", "messages": [response]}
        else:
            return {"next_agent": "end", "messages": [response]}

class WorkerAgentNode(BaseNode):
    """Executes specific tasks."""

    def __init__(self, role, tools, **kwargs):
        super().__init__(**kwargs)
        self.role = role
        self.llm_with_tools = llm.bind_tools(tools)

    def execute(self, state):
        response = self.llm_with_tools.invoke(state.messages)
        return {"messages": [response]}

# Build hierarchy
builder.add_node("manager", ManagerAgentNode())
builder.add_node("researcher", WorkerAgentNode("researcher", research_tools))
builder.add_node("writer", WorkerAgentNode("writer", writing_tools))
```

### Agent with Memory

**Agent with persistent memory:**

```python
class MemoryAgentNode(BaseNode):
    def execute(self, state, runtime):
        # Load memory from store
        memory = []
        if runtime and runtime.store:
            stored = runtime.store.get(("user", state.user_id), "memory")
            if stored:
                memory = stored.get("messages", [])

        # Combine with current messages
        full_context = memory + state.messages

        # Get response
        response = self.llm_with_tools.invoke(full_context)

        # Save to memory
        if runtime and runtime.store:
            memory.append(state.messages[-1])  # User message
            memory.append(response)  # Agent response
            runtime.store.put(
                ("user", state.user_id),
                "memory",
                {"messages": memory[-10:]}  # Keep last 10
            )

        return {"messages": [response]}
```

### Streaming Agents

**Agent that streams responses:**

```python
from act_operator_lib.base_node import AsyncBaseNode

class StreamingAgentNode(AsyncBaseNode):
    async def execute(self, state, runtime):
        chunks = []

        # Stream response
        async for chunk in self.llm_with_tools.astream(state.messages):
            chunks.append(chunk)

            # Stream to runtime if available
            if runtime and runtime.stream:
                runtime.stream.send(chunk.content)

        # Combine chunks
        full_response = chunks[-1]  # Last chunk has complete message

        return {"messages": [full_response]}
```

---

## Best Practices

1. **Use native tool calling** - Modern LLMs support it natively
2. **Limit tool count** - Too many tools confuse the agent (max 10-15)
3. **Clear tool descriptions** - Agent decides based on descriptions
4. **Set max iterations** - Prevent infinite loops
5. **Handle errors gracefully** - Tool execution can fail
6. **Log agent decisions** - Track tool calls and reasoning
7. **Validate tool arguments** - Check before execution
8. **Use typed tools** - Type hints help LLM generate correct args
9. **Test tools independently** - Ensure tools work before agent use
10. **Monitor costs** - Multiple LLM calls can be expensive

---

## Common Pitfalls

1. **Too many tools** - Agent gets confused
2. **Poor tool descriptions** - Agent doesn't know when to use
3. **Missing error handling** - Tools fail, crash agent
4. **No iteration limit** - Infinite loops
5. **Complex tool arguments** - Agent struggles with complex types
6. **Insufficient context** - Agent makes wrong decisions
7. **Not validating tool calls** - Execute invalid operations
8. **Forgetting tool messages** - Break conversation flow
9. **Mixing agent types** - Stick to one pattern
10. **Over-engineering** - Simple problems don't need agents

---

## Troubleshooting

### Agent not calling tools

**Check:**
1. Tools bound to LLM: `llm.bind_tools(tools)`
2. Tool descriptions clear and relevant
3. User query requires tool use
4. Model supports tool calling (Claude 3, GPT-4, etc.)

### Tool calls with wrong arguments

**Fix:**
1. Add type hints to tool functions
2. Improve tool descriptions
3. Add examples in description
4. Use Pydantic models for complex args

### Infinite loops

**Solutions:**
1. Set `max_iterations` limit
2. Check routing logic
3. Ensure termination condition
4. Add iteration counter to state

### Empty responses

**Debug:**
1. Check if tools returned None
2. Verify message formatting
3. Ensure proper tool message creation
4. Check for LLM API errors

---

## References

**Official Documentation:**
- LangChain Agents: https://python.langchain.com/docs/modules/agents
- Tool Calling: https://python.langchain.com/docs/modules/model_io/tool_calling
- LangGraph Agents: https://langchain-ai.github.io/langgraph/how-tos/agent/

**Related Guides:**
- `tools_guide.md`: Detailed tool implementation
- `prompts_guide.md`: Agent prompt engineering
- `models_guide.md`: LLM configuration

**Examples:**
- LangGraph Quickstart: https://langchain-ai.github.io/langgraph/tutorials/quickstart/
- Agent Templates: https://python.langchain.com/docs/templates#agent-templates
