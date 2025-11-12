"""Complex state example with multi-layer structure and tracking.

This example demonstrates a comprehensive state schema with:
- Three-layer architecture (Input/Output/State)
- Message handling
- Iteration tracking
- Error accumulation
"""

from dataclasses import dataclass
from typing import Annotated

from langchain_core.messages import AnyMessage, AIMessage
from langgraph.graph.message import add_messages


@dataclass(kw_only=True)
class InputState:
    """External API input.

    Attributes:
        query: User's query
    """

    query: str


@dataclass(kw_only=True)
class OutputState:
    """External API output.

    Attributes:
        messages: Response messages
        answer: Final answer (if complete)
    """

    messages: Annotated[list[AnyMessage], add_messages]
    answer: str | None = None


@dataclass(kw_only=True)
class State:
    """Complete internal state.

    Use for: Complex workflows, multi-step processes, retry logic

    Attributes:
        query: User's query
        messages: Conversation history (accumulated)
        answer: Final answer
        iterations: Number of processing iterations
        errors: Accumulated error messages
        intermediate_results: Internal processing results (not exposed to API)
    """

    # Public fields (in Input/Output)
    query: str
    messages: Annotated[list[AnyMessage], add_messages]
    answer: str | None = None

    # Internal tracking (not in Input/Output)
    iterations: int = 0
    errors: Annotated[list[str], lambda old, new: (old or []) + new] = None
    intermediate_results: list[str] = None


# Example usage in nodes
def process_node(state: State) -> dict:
    """Process query with error tracking."""
    try:
        # Simulate processing
        result = f"Processed: {state.query}"

        return {
            "intermediate_results": [result],
            "iterations": state.iterations + 1
        }

    except Exception as e:
        return {
            "errors": [str(e)],
            "iterations": state.iterations + 1
        }


def finalize_node(state: State) -> dict:
    """Generate final answer."""
    if state.intermediate_results:
        answer = state.intermediate_results[-1]
    else:
        answer = "Error: No results"

    return {
        "answer": answer,
        "messages": [AIMessage(content=answer)]
    }


# Example graph invocation
if __name__ == "__main__":
    # Initial state
    initial = State(query="What is 2+2?")

    # Simulate node execution
    step1 = process_node(initial)
    print(f"After processing: iterations={step1['iterations']}")

    # Merge state
    updated_state = State(
        query=initial.query,
        iterations=step1["iterations"],
        intermediate_results=step1.get("intermediate_results")
    )

    step2 = finalize_node(updated_state)
    print(f"Final answer: {step2['answer']}")
