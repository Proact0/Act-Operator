"""Agent node examples - LangChain agent integration.

Demonstrates how to integrate LangChain agents into LangGraph nodes.
Agents can use tools, make decisions, and interact with external systems.

Common patterns:
- Agent with tools for function calling
- Multi-agent systems
- Agent with memory and state
"""

from dataclasses import dataclass
from typing import Annotated, List

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent

from casts.base_node import BaseNode


# Define tools for the agent
@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression.

    Args:
        expression: Mathematical expression to evaluate (e.g., "2 + 2")

    Returns:
        Result of the calculation
    """
    try:
        # Note: eval is used for demo purposes only
        # In production, use a proper math parser
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def search(query: str) -> str:
    """Search for information (simulated).

    Args:
        query: Search query

    Returns:
        Search results
    """
    # Simulate search results
    return f"Search results for '{query}': [Demo result 1, Demo result 2, Demo result 3]"


@tool
def get_weather(location: str) -> str:
    """Get weather information for a location (simulated).

    Args:
        location: City or location name

    Returns:
        Weather information
    """
    # Simulate weather data
    return f"Weather in {location}: Sunny, 72°F"


# Define state
@dataclass(kw_only=True)
class AgentState:
    """State for agent graph."""

    query: str
    messages: Annotated[list[AnyMessage], add_messages]


class BasicAgentNode(BaseNode):
    """Node that wraps a LangChain agent.

    Use this pattern when you need:
    - Autonomous decision-making
    - Tool calling capabilities
    - ReAct-style reasoning
    """

    def __init__(self, model=None, tools=None, verbose: bool = False):
        """Initialize the agent node.

        Args:
            model: Language model to use (must support function calling)
            tools: List of tools available to the agent
            verbose: Enable verbose logging
        """
        super().__init__(verbose=verbose)
        
        # Use a mock model for demonstration
        # In production, replace with: ChatOpenAI(), ChatAnthropic(), etc.
        self.model = model
        self.tools = tools or []

    def execute(self, state) -> dict:
        """Execute the agent.

        Args:
            state: Current state with messages

        Returns:
            dict: State updates with agent responses
        """
        self.log(f"Agent processing query: {state.query}")

        if not self.model:
            # Return mock response if no model provided
            return {
                "messages": [
                    AIMessage(
                        content=f"Agent received: {state.query} (Mock response - configure model for real execution)"
                    )
                ]
            }

        # Create agent
        agent = create_react_agent(self.model, self.tools)

        # Prepare messages
        messages = list(state.messages) if state.messages else []
        messages.append(HumanMessage(content=state.query))

        # Run agent
        response = agent.invoke({"messages": messages})

        self.log(f"Agent completed with {len(response['messages'])} messages")

        return {"messages": response["messages"]}


class ToolCallingAgentNode(BaseNode):
    """Agent node with explicit tool calling logic.

    Use this pattern when you need:
    - Custom tool selection logic
    - Tool call filtering or validation
    - Special handling of tool results
    """

    def __init__(self, model=None, tools=None, verbose: bool = False):
        """Initialize with tools.

        Args:
            model: Language model
            tools: List of tools
            verbose: Enable verbose logging
        """
        super().__init__(verbose=verbose)
        self.model = model
        self.tools = {tool.name: tool for tool in (tools or [])}

    def execute(self, state) -> dict:
        """Execute with tool calling.

        Args:
            state: Current state

        Returns:
            dict: State updates
        """
        self.log(f"Tool-calling agent processing: {state.query}")

        # For demonstration, manually route to appropriate tool
        query_lower = state.query.lower()

        if "calculate" in query_lower or any(op in query_lower for op in ["+", "-", "*", "/"]):
            tool_name = "calculator"
            # Extract expression (simple logic for demo)
            expression = state.query.split("calculate")[-1].strip()
            result = self.tools[tool_name].invoke(expression)
            
        elif "search" in query_lower:
            tool_name = "search"
            search_query = state.query.replace("search", "").strip()
            result = self.tools[tool_name].invoke(search_query)
            
        elif "weather" in query_lower:
            tool_name = "get_weather"
            # Extract location (simple logic for demo)
            location = state.query.split("in")[-1].strip() if "in" in query_lower else "unknown"
            result = self.tools[tool_name].invoke(location)
            
        else:
            result = "I don't know how to help with that. I can calculate, search, or get weather."

        self.log(f"Tool result: {result}")

        return {
            "messages": [
                AIMessage(content=f"Used tool: {result if 'tool_name' not in locals() else tool_name}\n{result}")
            ]
        }


class MultiStepAgentNode(BaseNode):
    """Agent that can perform multi-step reasoning.

    Use this pattern when you need:
    - Chain-of-thought reasoning
    - Multi-step problem solving
    - Iterative refinement
    """

    def __init__(self, model=None, tools=None, max_iterations: int = 3, verbose: bool = False):
        """Initialize multi-step agent.

        Args:
            model: Language model
            tools: Available tools
            max_iterations: Maximum reasoning steps
            verbose: Enable verbose logging
        """
        super().__init__(verbose=verbose)
        self.model = model
        self.tools = tools or []
        self.max_iterations = max_iterations

    def execute(self, state) -> dict:
        """Execute multi-step reasoning.

        Args:
            state: Current state

        Returns:
            dict: State updates with reasoning steps
        """
        self.log(f"Multi-step agent processing: {state.query}")

        # Simulate multi-step reasoning
        steps = []
        
        steps.append("Step 1: Understanding the query...")
        self.log("Iteration 1: Understanding")
        
        steps.append(f"Step 2: Analyzing '{state.query}'...")
        self.log("Iteration 2: Analyzing")
        
        steps.append("Step 3: Formulating response...")
        self.log("Iteration 3: Formulating")

        final_response = "\n".join(steps)
        final_response += f"\n\nFinal answer: Processed '{state.query}' through {len(steps)} reasoning steps."

        return {"messages": [AIMessage(content=final_response)]}


# Usage example
if __name__ == "__main__":
    print("=== Agent Node Examples ===\n")

    # Define tools
    tools = [calculator, search, get_weather]

    # Test BasicAgentNode (without model for demo)
    print("--- BasicAgentNode ---")
    node = BasicAgentNode(model=None, tools=tools, verbose=True)
    state = AgentState(query="What's 2 + 2?", messages=[])
    result = node(state)
    print(f"Result: {result['messages'][-1].content}\n")

    # Test ToolCallingAgentNode
    print("--- ToolCallingAgentNode ---")
    node = ToolCallingAgentNode(model=None, tools=tools, verbose=True)
    
    test_queries = [
        "Calculate 10 + 5",
        "Search for LangGraph tutorials",
        "What's the weather in San Francisco?",
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        state = AgentState(query=query, messages=[])
        result = node(state)
        print(f"Result: {result['messages'][-1].content}")

    # Test MultiStepAgentNode
    print("\n--- MultiStepAgentNode ---")
    node = MultiStepAgentNode(model=None, tools=tools, max_iterations=3, verbose=True)
    state = AgentState(query="Solve a complex problem", messages=[])
    result = node(state)
    print(f"Result:\n{result['messages'][-1].content}")

    print("\n" + "=" * 70)
    print("Agent node patterns are ideal for:")
    print("  - Autonomous task completion")
    print("  - Tool and API integration")
    print("  - Complex decision-making")
    print("  - Multi-step reasoning")
    print("  - Interactive query handling")
    print("\nNote: These examples use mock responses.")
    print("For real execution, configure with ChatOpenAI, ChatAnthropic, etc.")
    print("=" * 70)
