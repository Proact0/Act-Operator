"""Simple node examples - BaseNode and function approaches.

Demonstrates basic node patterns for transforming state.
"""

from casts.base_node import BaseNode


# BaseNode Approach (Recommended)
class UppercaseNode(BaseNode):
    """Convert query to uppercase using BaseNode."""

    def execute(self, state):
        """Transform query to uppercase.

        Args:
            state: Graph state with query field

        Returns:
            dict: State update with result
        """
        result = state.query.upper()
        return {"result": result}


# Function Approach (Simpler for basic transformations)
def uppercase_node(state):
    """Convert query to uppercase using function.

    Args:
        state: Graph state with query field

    Returns:
        dict: State update with result
    """
    result = state.query.upper()
    return {"result": result}


# Usage in graph
if __name__ == "__main__":
    from dataclasses import dataclass

    @dataclass(kw_only=True)
    class State:
        query: str
        result: str = ""

    # Test BaseNode
    node_instance = UppercaseNode()
    test_state = State(query="hello world")
    result = node_instance(test_state)
    print(f"BaseNode result: {result}")

    # Test function node
    result = uppercase_node(test_state)
    print(f"Function result: {result}")
