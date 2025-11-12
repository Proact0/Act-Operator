"""Parallel graph example - Fan-out/fan-in pattern.

This demonstrates parallel processing:
START -> Splitter -> [ProcessA, ProcessB, ProcessC] -> Combiner -> END

Use this pattern when you need:
- Parallel processing of independent tasks
- Fan-out/fan-in workflows
- Concurrent operations
- Performance optimization through parallelism
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
class ParallelState:
    """State for parallel graph."""

    query: str
    messages: Annotated[list[AnyMessage], add_messages]
    result_a: str = ""
    result_b: str = ""
    result_c: str = ""
    combined_result: str = ""


# Define nodes
class SplitterNode(BaseNode):
    """Prepares state for parallel processing."""

    def execute(self, state) -> dict:
        """Prepare for parallel processing.

        Args:
            state: Current state

        Returns:
            dict: State updates
        """
        self.log("Splitting work for parallel processing")

        return {
            "messages": [
                AIMessage(content="Preparing parallel processing of query")
            ]
        }


class ProcessANode(BaseNode):
    """Process path A - word count."""

    def execute(self, state) -> dict:
        """Count words in query.

        Args:
            state: Current state

        Returns:
            dict: State updates
        """
        self.log("Processing path A: word count")

        word_count = len(state.query.split())
        result = f"Words: {word_count}"

        return {
            "result_a": result,
            "messages": [AIMessage(content=f"Path A complete: {result}")],
        }


class ProcessBNode(BaseNode):
    """Process path B - character count."""

    def execute(self, state) -> dict:
        """Count characters in query.

        Args:
            state: Current state

        Returns:
            dict: State updates
        """
        self.log("Processing path B: character count")

        char_count = len(state.query)
        result = f"Characters: {char_count}"

        return {
            "result_b": result,
            "messages": [AIMessage(content=f"Path B complete: {result}")],
        }


class ProcessCNode(BaseNode):
    """Process path C - uppercase conversion."""

    def execute(self, state) -> dict:
        """Convert query to uppercase.

        Args:
            state: Current state

        Returns:
            dict: State updates
        """
        self.log("Processing path C: uppercase")

        result = state.query.upper()

        return {
            "result_c": result,
            "messages": [AIMessage(content=f"Path C complete: {result}")],
        }


class CombinerNode(BaseNode):
    """Combines results from parallel processing."""

    def execute(self, state) -> dict:
        """Combine all parallel results.

        Args:
            state: Current state with results from all paths

        Returns:
            dict: State updates with combined result
        """
        self.log("Combining parallel processing results")

        combined = f"Results: {state.result_a} | {state.result_b} | {state.result_c}"

        return {
            "combined_result": combined,
            "messages": [AIMessage(content=f"All paths complete: {combined}")],
        }


# Define graph
class ParallelGraph(BaseGraph):
    """Parallel graph with fan-out/fan-in pattern."""

    def __init__(self):
        """Initialize the graph."""
        super().__init__()
        self.state = ParallelState

    def build(self):
        """Build the parallel graph.

        Returns:
            Compiled graph
        """
        builder = StateGraph(self.state)

        # Add nodes
        builder.add_node("splitter", SplitterNode())
        builder.add_node("process_a", ProcessANode())
        builder.add_node("process_b", ProcessBNode())
        builder.add_node("process_c", ProcessCNode())
        builder.add_node("combiner", CombinerNode())

        # Add edges
        builder.add_edge(START, "splitter")

        # Fan-out: splitter -> all processors (these run in parallel)
        builder.add_edge("splitter", "process_a")
        builder.add_edge("splitter", "process_b")
        builder.add_edge("splitter", "process_c")

        # Fan-in: all processors -> combiner
        builder.add_edge("process_a", "combiner")
        builder.add_edge("process_b", "combiner")
        builder.add_edge("process_c", "combiner")

        # combiner -> END
        builder.add_edge("combiner", END)

        graph = builder.compile()
        graph.name = self.name
        return graph


# Usage example
if __name__ == "__main__":
    print("=== Parallel Graph Example ===\n")

    # Create graph
    graph = ParallelGraph().build()

    # Run graph
    initial_state = {
        "query": "Hello world from parallel processing",
        "messages": [],
    }

    print("Initial query:", initial_state["query"])
    print("\nExecuting graph with parallel processing...\n")

    result = graph.invoke(initial_state)

    print("\nIndividual Results:")
    print(f"  Path A: {result['result_a']}")
    print(f"  Path B: {result['result_b']}")
    print(f"  Path C: {result['result_c']}")

    print(f"\nCombined Result:")
    print(f"  {result['combined_result']}")

    print("\nAll Messages:")
    for i, msg in enumerate(result["messages"], 1):
        print(f"  {i}. {msg.content}")

    print("\n" + "=" * 60)
    print("Parallel graph pattern is ideal for:")
    print("  - Independent data enrichment from multiple sources")
    print("  - Concurrent API calls to different services")
    print("  - Multi-model inference (running multiple models)")
    print("  - Parallel validation checks")
    print("  - Feature extraction pipelines")
    print("\nNote: LangGraph automatically executes parallel branches")
    print("concurrently when possible, improving performance.")
    print("=" * 60)
