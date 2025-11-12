"""Advanced Cast Tools - Example tools for the agent."""

from langchain.tools import tool


@tool
def calculator_tool(expression: str) -> str:
    """Calculate mathematical expressions.

    Args:
        expression: Math expression to evaluate (e.g., "2 + 2")

    Returns:
        str: Result of calculation
    """
    try:
        # Safe evaluation (in production, use a proper math parser)
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating: {str(e)}"


@tool
def search_tool(query: str) -> str:
    """Search for information.

    Args:
        query: Search query

    Returns:
        str: Search results (simulated)
    """
    # Simulated search results
    # In real implementation, call actual search API
    return f"Search results for '{query}': [Simulated results would appear here]"
