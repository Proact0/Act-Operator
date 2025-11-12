"""Linear graph example - Sequential workflow.

This demonstrates the simplest graph pattern:
START -> Node1 -> Node2 -> Node3 -> END

Use this pattern when you need:
- Sequential processing steps
- Pipeline transformations
- Simple workflows without branching
"""

from dataclasses import dataclass
from typing import Annotated

from langchain_core.messages import AIMessage, AnyMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from casts.base_graph import BaseGraph
from casts.base_node import BaseNode


# Define state
@dataclass(kw_only=True)
class LinearState:
    """State for linear graph."""

    query: str
    messages: Annotated[list[AnyMessage], add_messages]
    step_count: int = 0


# Define nodes
class StepOneNode(BaseNode):
    """First step in the pipeline."""

    def execute(self, state) -> dict:
        """Execute step one.

        Args:
            state: Current state

        Returns:
            dict: State updates
        """
        self.log("Executing step one")
        
        return {
            "messages": [AIMessage(content="Step 1: Received query")],
            "step_count": state.step_count + 1,
        }


class StepTwoNode(BaseNode):
    """Second step in the pipeline."""

    def execute(self, state) -> dict:
        """Execute step two.

        Args:
            state: Current state

        Returns:
            dict: State updates
        """
        self.log("Executing step two")
        
        processed = state.query.upper()
        
        return {
            "messages": [AIMessage(content=f"Step 2: Processed as {processed}")],
            "step_count": state.step_count + 1,
        }


class StepThreeNode(BaseNode):
    """Third step in the pipeline."""

    def execute(self, state) -> dict:
        """Execute step three.

        Args:
            state: Current state

        Returns:
            dict: State updates
        """
        self.log("Executing step three")
        
        word_count = len(state.query.split())
        
        return {
            "messages": [AIMessage(content=f"Step 3: Counted {word_count} words")],
            "step_count": state.step_count + 1,
        }


# Define graph
class LinearGraph(BaseGraph):
    """Linear graph with sequential steps."""

    def __init__(self):
        """Initialize the graph."""
        super().__init__()
        self.state = LinearState

    def build(self):
        """Build the linear graph.

        Returns:
            Compiled graph
        """
        builder = StateGraph(self.state)

        # Add nodes
        builder.add_node("step_one", StepOneNode())
        builder.add_node("step_two", StepTwoNode())
        builder.add_node("step_three", StepThreeNode())

        # Add linear edges: START -> step_one -> step_two -> step_three -> END
        builder.add_edge(START, "step_one")
        builder.add_edge("step_one", "step_two")
        builder.add_edge("step_two", "step_three")
        builder.add_edge("step_three", END)

        graph = builder.compile()
        graph.name = self.name
        return graph


# Usage example
if __name__ == "__main__":
    print("=== Linear Graph Example ===\n")

    # Create graph
    graph = LinearGraph().build()

    # Run graph
    initial_state = {"query": "hello world from linear graph", "messages": []}
    
    print("Initial state:", initial_state)
    print("\nExecuting graph...\n")

    result = graph.invoke(initial_state)

    print("\nFinal state:")
    print(f"Query: {result['query']}")
    print(f"Step count: {result['step_count']}")
    print("\nMessages:")
    for msg in result["messages"]:
        print(f"  - {msg.content}")

    print("\n" + "=" * 50)
    print("Linear graph pattern is ideal for:")
    print("  - ETL pipelines")
    print("  - Data transformation chains")
    print("  - Sequential validation steps")
    print("  - Simple workflows without branching")
    print("=" * 50)
