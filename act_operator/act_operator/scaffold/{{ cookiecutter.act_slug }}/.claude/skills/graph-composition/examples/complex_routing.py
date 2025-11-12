"""Complex routing example - Multi-way conditional routing.

This demonstrates advanced routing patterns:
- Multi-level conditional routing
- Loops and cycles
- Dynamic routing based on multiple conditions
- Retry logic

Use this pattern when you need:
- Complex decision trees
- Iterative processing with conditions
- Advanced workflow logic
- Retry and error handling patterns
"""

from dataclasses import dataclass
from typing import Annotated, Literal

from langchain_core.messages import AIMessage, AnyMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from casts.base_graph import BaseGraph
from casts.base_node import BaseNode


# Define state
@dataclass(kw_only=True)
class ComplexState:
    """State for complex routing graph."""

    query: str
    messages: Annotated[list[AnyMessage], add_messages]
    complexity: str = ""  # simple, medium, complex
    retry_count: int = 0
    max_retries: int = 3
    processing_complete: bool = False
    quality_score: float = 0.0


# Define nodes
class AnalyzerNode(BaseNode):
    """Analyzes query complexity."""

    def execute(self, state) -> dict:
        """Analyze query complexity.

        Args:
            state: Current state

        Returns:
            dict: State updates with complexity assessment
        """
        self.log(f"Analyzing query: {state.query}")

        # Determine complexity based on word count and content
        word_count = len(state.query.split())

        if word_count > 20 or "complex" in state.query.lower():
            complexity = "complex"
        elif word_count > 10 or "medium" in state.query.lower():
            complexity = "medium"
        else:
            complexity = "simple"

        self.log(f"Complexity: {complexity}")

        return {
            "complexity": complexity,
            "messages": [AIMessage(content=f"Complexity assessed: {complexity}")],
        }


class SimpleProcessorNode(BaseNode):
    """Processes simple queries."""

    def execute(self, state) -> dict:
        """Process simple query.

        Args:
            state: Current state

        Returns:
            dict: State updates
        """
        self.log("Processing simple query")

        return {
            "processing_complete": True,
            "quality_score": 0.95,
            "messages": [AIMessage(content="Simple processing complete")],
        }


class MediumProcessorNode(BaseNode):
    """Processes medium complexity queries."""

    def execute(self, state) -> dict:
        """Process medium query.

        Args:
            state: Current state

        Returns:
            dict: State updates
        """
        self.log("Processing medium complexity query")

        # Simulate quality check - might need retry
        quality = 0.7 + (state.retry_count * 0.1)

        return {
            "processing_complete": quality >= 0.8,
            "quality_score": quality,
            "messages": [
                AIMessage(
                    content=f"Medium processing: quality={quality:.2f}"
                )
            ],
        }


class ComplexProcessorNode(BaseNode):
    """Processes complex queries."""

    def execute(self, state) -> dict:
        """Process complex query.

        Args:
            state: Current state

        Returns:
            dict: State updates
        """
        self.log("Processing complex query")

        # Simulate quality check - might need retry
        quality = 0.5 + (state.retry_count * 0.15)

        return {
            "processing_complete": quality >= 0.8,
            "quality_score": quality,
            "messages": [
                AIMessage(
                    content=f"Complex processing: quality={quality:.2f}"
                )
            ],
        }


class QualityCheckNode(BaseNode):
    """Checks processing quality and decides on retry."""

    def execute(self, state) -> dict:
        """Check quality and update retry count.

        Args:
            state: Current state

        Returns:
            dict: State updates
        """
        self.log(f"Quality check: {state.quality_score:.2f}")

        if state.processing_complete:
            return {
                "messages": [
                    AIMessage(content=f"Quality check passed: {state.quality_score:.2f}")
                ]
            }
        else:
            new_retry_count = state.retry_count + 1
            return {
                "retry_count": new_retry_count,
                "messages": [
                    AIMessage(
                        content=f"Quality check failed, retry {new_retry_count}/{state.max_retries}"
                    )
                ],
            }


class FinalizerNode(BaseNode):
    """Finalizes processing."""

    def execute(self, state) -> dict:
        """Finalize the result.

        Args:
            state: Current state

        Returns:
            dict: State updates
        """
        self.log("Finalizing result")

        if state.processing_complete:
            status = "Success"
        else:
            status = f"Incomplete after {state.retry_count} retries"

        return {
            "messages": [
                AIMessage(
                    content=f"Final result: {status} (quality: {state.quality_score:.2f})"
                )
            ]
        }


# Define routing functions
def route_by_complexity(
    state: ComplexState,
) -> Literal["simple_processor", "medium_processor", "complex_processor"]:
    """Route based on query complexity.

    Args:
        state: Current state with complexity

    Returns:
        Name of the next node
    """
    if state.complexity == "simple":
        return "simple_processor"
    elif state.complexity == "medium":
        return "medium_processor"
    else:
        return "complex_processor"


def route_after_quality_check(
    state: ComplexState,
) -> Literal["retry", "finalizer"]:
    """Route based on quality check result.

    Args:
        state: Current state with quality score

    Returns:
        Name of the next node
    """
    if state.processing_complete:
        return "finalizer"
    elif state.retry_count >= state.max_retries:
        # Max retries reached, go to finalizer anyway
        return "finalizer"
    else:
        # Retry by going back to appropriate processor
        return "retry"


def route_retry(
    state: ComplexState,
) -> Literal["simple_processor", "medium_processor", "complex_processor"]:
    """Route retry back to appropriate processor.

    Args:
        state: Current state

    Returns:
        Name of the processor node
    """
    # Route back to the same processor for retry
    return route_by_complexity(state)


# Define graph
class ComplexRoutingGraph(BaseGraph):
    """Complex routing graph with multi-way conditionals and loops."""

    def __init__(self):
        """Initialize the graph."""
        super().__init__()
        self.state = ComplexState

    def build(self):
        """Build the complex routing graph.

        Returns:
            Compiled graph
        """
        builder = StateGraph(self.state)

        # Add nodes
        builder.add_node("analyzer", AnalyzerNode())
        builder.add_node("simple_processor", SimpleProcessorNode())
        builder.add_node("medium_processor", MediumProcessorNode())
        builder.add_node("complex_processor", ComplexProcessorNode())
        builder.add_node("quality_check", QualityCheckNode())
        builder.add_node("retry", lambda state: {})  # Dummy node for routing
        builder.add_node("finalizer", FinalizerNode())

        # Add edges
        builder.add_edge(START, "analyzer")

        # Route from analyzer to appropriate processor
        builder.add_conditional_edges(
            "analyzer",
            route_by_complexity,
            {
                "simple_processor": "simple_processor",
                "medium_processor": "medium_processor",
                "complex_processor": "complex_processor",
            },
        )

        # All processors go to quality check
        builder.add_edge("simple_processor", "quality_check")
        builder.add_edge("medium_processor", "quality_check")
        builder.add_edge("complex_processor", "quality_check")

        # Route from quality check
        builder.add_conditional_edges(
            "quality_check",
            route_after_quality_check,
            {"retry": "retry", "finalizer": "finalizer"},
        )

        # Route retry back to appropriate processor (creates a loop)
        builder.add_conditional_edges(
            "retry",
            route_retry,
            {
                "simple_processor": "simple_processor",
                "medium_processor": "medium_processor",
                "complex_processor": "complex_processor",
            },
        )

        # Finalizer goes to END
        builder.add_edge("finalizer", END)

        graph = builder.compile()
        graph.name = self.name
        return graph


# Usage example
if __name__ == "__main__":
    print("=== Complex Routing Graph Example ===\n")

    # Create graph
    graph = ComplexRoutingGraph().build()

    # Test different complexity levels
    test_queries = [
        "Hello",  # Simple
        "This is a medium length query that needs more processing",  # Medium
        "This is a very complex query with many words and intricate details that require sophisticated processing and careful handling of the content",  # Complex
    ]

    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"Query: {query}")
        print('='*70)

        initial_state = {"query": query, "messages": []}
        result = graph.invoke(initial_state)

        print(f"\nComplexity: {result['complexity']}")
        print(f"Retry Count: {result['retry_count']}")
        print(f"Quality Score: {result['quality_score']:.2f}")
        print(f"Processing Complete: {result['processing_complete']}")

        print("\nExecution Flow:")
        for i, msg in enumerate(result["messages"], 1):
            print(f"  {i}. {msg.content}")

    print("\n" + "=" * 70)
    print("Complex routing pattern is ideal for:")
    print("  - Multi-stage approval workflows")
    print("  - Iterative refinement with quality checks")
    print("  - Retry logic with backoff")
    print("  - State machines with complex transitions")
    print("  - Error handling and recovery patterns")
    print("\nKey features demonstrated:")
    print("  - Multi-way conditional routing")
    print("  - Loops (retry logic)")
    print("  - Quality gates")
    print("  - Max retry limits")
    print("=" * 70)
