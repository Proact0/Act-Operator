"""Simple state example for data processing workflows.

This example demonstrates a basic state schema for data processing
without messages or complex tracking.
"""

from dataclasses import dataclass


@dataclass(kw_only=True)
class State:
    """Simple processing state.

    Use for: ETL, data pipelines, simple transformations

    Attributes:
        input_data: Raw input data
        processed_data: Processed result
        status: Processing status
    """

    # Required input
    input_data: str

    # Processing results
    processed_data: str | None = None
    status: str = "pending"


# Example usage in nodes
def process_node(state: State) -> dict:
    """Process the input data."""
    processed = state.input_data.upper()

    return {
        "processed_data": processed,
        "status": "complete"
    }


# Example graph invocation
if __name__ == "__main__":
    # Initial state
    initial = State(input_data="hello world")

    # Simulate node execution
    result = process_node(initial)

    print(f"Status: {result['status']}")
    print(f"Result: {result['processed_data']}")
