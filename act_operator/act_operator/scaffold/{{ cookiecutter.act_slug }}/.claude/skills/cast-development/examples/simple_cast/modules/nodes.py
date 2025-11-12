"""Simple Cast Nodes - Basic node implementation."""

from langchain_core.messages import AIMessage

from casts.base_node import BaseNode


class GreetingNode(BaseNode):
    """Simple greeting node.

    Takes a name from state and generates a greeting message.
    """

    def execute(self, state):
        """Generate greeting message.

        Args:
            state: Graph state with 'name' field

        Returns:
            dict: State update with greeting message
        """
        name = state["name"]
        greeting = f"Hello, {name}! Welcome to the Act!"

        return {
            "messages": [AIMessage(content=greeting)]
        }
