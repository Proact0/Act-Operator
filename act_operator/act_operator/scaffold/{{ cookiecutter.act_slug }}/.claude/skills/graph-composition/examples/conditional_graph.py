"""Conditional graph example - Branching workflow.

This demonstrates conditional routing:
START -> Classifier -> [PathA or PathB or PathC] -> END

Use this pattern when you need:
- Conditional branching based on state
- Different processing paths
- Dynamic routing decisions
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
class ConditionalState:
    """State for conditional graph."""

    query: str
    messages: Annotated[list[AnyMessage], add_messages]
    category: str = ""
    confidence: float = 0.0


# Define nodes
class ClassifierNode(BaseNode):
    """Classifies the query into categories."""

    def execute(self, state) -> dict:
        """Classify the query.

        Args:
            state: Current state

        Returns:
            dict: State updates with category
        """
        self.log(f"Classifying query: {state.query}")

        # Simple classification logic
        query_lower = state.query.lower()
        
        if "urgent" in query_lower or "emergency" in query_lower:
            category = "urgent"
            confidence = 0.95
        elif "help" in query_lower or "question" in query_lower:
            category = "support"
            confidence = 0.85
        else:
            category = "general"
            confidence = 0.75

        self.log(f"Classified as: {category} (confidence: {confidence})")

        return {
            "category": category,
            "confidence": confidence,
            "messages": [
                AIMessage(content=f"Classified as: {category} ({confidence*100}% confidence)")
            ],
        }


class UrgentPathNode(BaseNode):
    """Handles urgent queries."""

    def execute(self, state) -> dict:
        """Process urgent query.

        Args:
            state: Current state

        Returns:
            dict: State updates
        """
        self.log("Processing urgent query")

        return {
            "messages": [
                AIMessage(content=f"[URGENT] Processing immediately: {state.query}")
            ]
        }


class SupportPathNode(BaseNode):
    """Handles support queries."""

    def execute(self, state) -> dict:
        """Process support query.

        Args:
            state: Current state

        Returns:
            dict: State updates
        """
        self.log("Processing support query")

        return {
            "messages": [
                AIMessage(content=f"[SUPPORT] Routing to help desk: {state.query}")
            ]
        }


class GeneralPathNode(BaseNode):
    """Handles general queries."""

    def execute(self, state) -> dict:
        """Process general query.

        Args:
            state: Current state

        Returns:
            dict: State updates
        """
        self.log("Processing general query")

        return {
            "messages": [
                AIMessage(content=f"[GENERAL] Standard processing: {state.query}")
            ]
        }


# Define routing function
def route_by_category(
    state: ConditionalState,
) -> Literal["urgent_path", "support_path", "general_path"]:
    """Route to appropriate path based on category.

    Args:
        state: Current state with category

    Returns:
        Name of the next node
    """
    if state.category == "urgent":
        return "urgent_path"
    elif state.category == "support":
        return "support_path"
    else:
        return "general_path"


# Define graph
class ConditionalGraph(BaseGraph):
    """Conditional graph with branching paths."""

    def __init__(self):
        """Initialize the graph."""
        super().__init__()
        self.state = ConditionalState

    def build(self):
        """Build the conditional graph.

        Returns:
            Compiled graph
        """
        builder = StateGraph(self.state)

        # Add nodes
        builder.add_node("classifier", ClassifierNode())
        builder.add_node("urgent_path", UrgentPathNode())
        builder.add_node("support_path", SupportPathNode())
        builder.add_node("general_path", GeneralPathNode())

        # Add edges
        builder.add_edge(START, "classifier")

        # Add conditional edges based on category
        builder.add_conditional_edges(
            "classifier",
            route_by_category,
            {
                "urgent_path": "urgent_path",
                "support_path": "support_path",
                "general_path": "general_path",
            },
        )

        # All paths lead to END
        builder.add_edge("urgent_path", END)
        builder.add_edge("support_path", END)
        builder.add_edge("general_path", END)

        graph = builder.compile()
        graph.name = self.name
        return graph


# Usage example
if __name__ == "__main__":
    print("=== Conditional Graph Example ===\n")

    # Create graph
    graph = ConditionalGraph().build()

    # Test different categories
    test_queries = [
        "This is an urgent emergency!",
        "I need help with my account",
        "What's the weather today?",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        initial_state = {"query": query, "messages": []}
        result = graph.invoke(initial_state)

        print(f"\nCategory: {result['category']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print("\nMessages:")
        for msg in result["messages"]:
            print(f"  - {msg.content}")

    print("\n" + "=" * 60)
    print("Conditional graph pattern is ideal for:")
    print("  - Request routing based on classification")
    print("  - A/B testing different processing paths")
    print("  - Priority-based workflows")
    print("  - Content moderation pipelines")
    print("=" * 60)
