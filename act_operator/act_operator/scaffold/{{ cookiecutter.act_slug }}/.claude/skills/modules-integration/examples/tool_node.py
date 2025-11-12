"""Tool node examples - LangChain tool integration.

Demonstrates how to use LangChain tools and ToolNode in LangGraph.
Tools enable agents and nodes to interact with external systems.

Common patterns:
- Direct tool execution
- Tool result processing
- Error handling with tools
"""

from dataclasses import dataclass
from typing import Annotated, List

from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    ToolCall,
    ToolMessage,
)
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from casts.base_node import BaseNode


# Define example tools
@tool
def add(a: int, b: int) -> int:
    """Add two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b
    """
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Product of a and b
    """
    return a * b


@tool
def format_text(text: str, style: str = "upper") -> str:
    """Format text in different styles.

    Args:
        text: Text to format
        style: Style to apply (upper, lower, title)

    Returns:
        Formatted text
    """
    if style == "upper":
        return text.upper()
    elif style == "lower":
        return text.lower()
    elif style == "title":
        return text.title()
    else:
        return text


# Define state
@dataclass(kw_only=True)
class ToolState:
    """State for tool examples."""

    query: str
    messages: Annotated[list[AnyMessage], add_messages]
    tool_calls: List[ToolCall] = None

    def __post_init__(self):
        if self.tool_calls is None:
            self.tool_calls = []


class SimpleToolNode(BaseNode):
    """Node that directly executes a tool.

    Use this pattern when you need:
    - Direct tool execution without agent reasoning
    - Deterministic tool calling
    - Simple function invocation
    """

    def __init__(self, tool_func, verbose: bool = False):
        """Initialize with a tool function.

        Args:
            tool_func: Tool function to execute
            verbose: Enable verbose logging
        """
        super().__init__(verbose=verbose)
        self.tool = tool_func

    def execute(self, state) -> dict:
        """Execute the tool directly.

        Args:
            state: Current state

        Returns:
            dict: State updates with tool result
        """
        self.log(f"Executing tool: {self.tool.name}")

        # Parse arguments from query (simplified for demo)
        # In production, use proper argument parsing or agent-generated calls
        try:
            if self.tool.name == "add":
                # Example: "add 5 and 3"
                numbers = [int(s) for s in state.query.split() if s.isdigit()]
                if len(numbers) >= 2:
                    result = self.tool.invoke({"a": numbers[0], "b": numbers[1]})
                else:
                    result = "Error: Need two numbers"
                    
            elif self.tool.name == "format_text":
                # Example: "format hello as upper"
                parts = state.query.lower().split()
                if "as" in parts:
                    idx = parts.index("as")
                    text = " ".join(parts[1:idx])
                    style = parts[idx + 1] if idx + 1 < len(parts) else "upper"
                    result = self.tool.invoke({"text": text, "style": style})
                else:
                    result = "Error: Invalid format command"
            else:
                result = self.tool.invoke(state.query)

            self.log(f"Tool result: {result}")

            return {
                "messages": [
                    AIMessage(content=f"Tool '{self.tool.name}' result: {result}")
                ]
            }

        except Exception as e:
            self.log(f"Tool execution error: {e}", level="error")
            return {"messages": [AIMessage(content=f"Error executing tool: {str(e)}")]}


class LangGraphToolNode(BaseNode):
    """Node that uses LangGraph's built-in ToolNode.

    Use this pattern when you need:
    - Standard tool execution
    - Integration with agent tool calls
    - Multiple tool support
    """

    def __init__(self, tools, verbose: bool = False):
        """Initialize with multiple tools.

        Args:
            tools: List of tool functions
            verbose: Enable verbose logging
        """
        super().__init__(verbose=verbose)
        self.tool_node = ToolNode(tools)
        self.tools = {tool.name: tool for tool in tools}

    def execute(self, state) -> dict:
        """Execute tools based on tool calls in messages.

        Args:
            state: Current state with messages containing tool calls

        Returns:
            dict: State updates with tool results
        """
        self.log("Processing tool calls from messages")

        # Check if there are any tool calls in messages
        has_tool_calls = any(
            hasattr(msg, "tool_calls") and msg.tool_calls
            for msg in (state.messages or [])
        )

        if not has_tool_calls:
            self.log("No tool calls found in messages", level="warning")
            return {
                "messages": [
                    AIMessage(content="No tool calls to execute")
                ]
            }

        # Execute tool node
        result = self.tool_node.invoke(state)
        self.log(f"Executed {len(result.get('messages', []))} tool calls")

        return result


class ErrorHandlingToolNode(BaseNode):
    """Tool node with error handling and fallbacks.

    Use this pattern when you need:
    - Robust error handling
    - Fallback behavior
    - Tool execution validation
    """

    def __init__(self, tools, fallback_message: str = None, verbose: bool = False):
        """Initialize with error handling.

        Args:
            tools: List of tools
            fallback_message: Message to return on error
            verbose: Enable verbose logging
        """
        super().__init__(verbose=verbose)
        self.tools = {tool.name: tool for tool in tools}
        self.fallback_message = fallback_message or "Tool execution failed"

    def execute(self, state) -> dict:
        """Execute tool with error handling.

        Args:
            state: Current state

        Returns:
            dict: State updates with result or fallback
        """
        self.log("Executing tool with error handling")

        # Simulate tool selection and execution
        query_lower = state.query.lower()

        try:
            if "add" in query_lower:
                numbers = [int(s) for s in state.query.split() if s.isdigit()]
                if len(numbers) < 2:
                    raise ValueError("Need at least two numbers")
                result = self.tools["add"].invoke({"a": numbers[0], "b": numbers[1]})
                
            elif "multiply" in query_lower:
                numbers = [int(s) for s in state.query.split() if s.isdigit()]
                if len(numbers) < 2:
                    raise ValueError("Need at least two numbers")
                result = self.tools["multiply"].invoke({"a": numbers[0], "b": numbers[1]})
                
            elif "format" in query_lower:
                # Extract text and style
                parts = state.query.lower().split()
                if "as" in parts:
                    idx = parts.index("as")
                    text = " ".join(parts[1:idx])
                    style = parts[idx + 1] if idx + 1 < len(parts) else "upper"
                    result = self.tools["format_text"].invoke({"text": text, "style": style})
                else:
                    raise ValueError("Invalid format command")
            else:
                raise ValueError(f"No tool found for query: {state.query}")

            self.log(f"Tool executed successfully: {result}")
            return {"messages": [AIMessage(content=f"Success: {result}")]}

        except ValueError as e:
            self.log(f"Validation error: {e}", level="warning")
            return {
                "messages": [
                    AIMessage(content=f"Validation error: {str(e)}")
                ]
            }
        except Exception as e:
            self.log(f"Tool execution error: {e}", level="error")
            return {
                "messages": [
                    AIMessage(content=f"{self.fallback_message}: {str(e)}")
                ]
            }


# Usage example
if __name__ == "__main__":
    print("=== Tool Node Examples ===\n")

    # Test SimpleToolNode
    print("--- SimpleToolNode ---")
    node = SimpleToolNode(tool_func=add, verbose=True)
    state = ToolState(query="add 5 and 3", messages=[])
    result = node(state)
    print(f"Result: {result['messages'][-1].content}\n")

    # Test with format tool
    node = SimpleToolNode(tool_func=format_text, verbose=True)
    state = ToolState(query="format hello world as title", messages=[])
    result = node(state)
    print(f"Result: {result['messages'][-1].content}\n")

    # Test ErrorHandlingToolNode
    print("--- ErrorHandlingToolNode ---")
    tools = [add, multiply, format_text]
    node = ErrorHandlingToolNode(tools=tools, verbose=True)

    test_queries = [
        "add 10 and 20",
        "multiply 5 and 7",
        "format hello world as upper",
        "invalid command",
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        state = ToolState(query=query, messages=[])
        result = node(state)
        print(f"Result: {result['messages'][-1].content}")

    print("\n" + "=" * 70)
    print("Tool node patterns are ideal for:")
    print("  - Function calling and execution")
    print("  - External API integration")
    print("  - Database operations")
    print("  - File system operations")
    print("  - Data transformations")
    print("\nBest practices:")
    print("  - Always validate tool inputs")
    print("  - Implement proper error handling")
    print("  - Use type hints for tool parameters")
    print("  - Provide clear tool descriptions for agents")
    print("=" * 70)
