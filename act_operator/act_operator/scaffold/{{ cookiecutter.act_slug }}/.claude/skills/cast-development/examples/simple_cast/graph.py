"""Simple Cast Example - Basic linear flow graph.

This example demonstrates:
- Simple linear graph structure (START → Process → END)
- Basic state management
- Single node implementation
"""

from langgraph.graph import END, START, StateGraph
from casts.base_graph import BaseGraph
from examples.simple_cast.modules.nodes import GreetingNode
from examples.simple_cast.modules.state import InputState, OutputState, State


class SimpleGraph(BaseGraph):
    """Simple greeting graph - demonstrates basic Cast structure."""

    def __init__(self):
        super().__init__()
        self.input = InputState
        self.output = OutputState
        self.state = State

    def build(self):
        """Build simple linear graph."""
        builder = StateGraph(
            self.state,
            input_schema=self.input,
            output_schema=self.output
        )

        # Add single node
        builder.add_node("greeting", GreetingNode())

        # Simple linear edges
        builder.add_edge(START, "greeting")
        builder.add_edge("greeting", END)

        # Compile
        graph = builder.compile()
        graph.name = self.name
        return graph


# Export graph instance
simple_graph = SimpleGraph()
