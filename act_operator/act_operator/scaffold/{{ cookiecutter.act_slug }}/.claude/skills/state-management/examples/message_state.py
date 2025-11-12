"""Message-based state example for chat/agent applications.

This example demonstrates state schema for chat applications
using LangChain messages and the add_messages reducer.
"""

from dataclasses import dataclass
from typing import Annotated

from langchain_core.messages import AnyMessage, AIMessage, HumanMessage
from langgraph.graph.message import add_messages


@dataclass(kw_only=True)
class InputState:
    """API input schema.

    Attributes:
        messages: User messages
    """

    messages: Annotated[list[AnyMessage], add_messages]


@dataclass(kw_only=True)
class OutputState:
    """API output schema.

    Attributes:
        messages: All messages including responses
    """

    messages: Annotated[list[AnyMessage], add_messages]


@dataclass(kw_only=True)
class State:
    """Complete chat state.

    Use for: Chat applications, agents, conversational AI

    Attributes:
        messages: Full conversation history (accumulated)
    """

    messages: Annotated[list[AnyMessage], add_messages]


# Example usage in nodes
def chat_node(state: State) -> dict:
    """Generate AI response."""
    last_message = state.messages[-1]

    # Simulate LLM response
    response = AIMessage(content=f"Echo: {last_message.content}")

    # Return only NEW message (add_messages handles accumulation)
    return {"messages": [response]}


# Example graph invocation
if __name__ == "__main__":
    # Initial state
    initial = State(messages=[HumanMessage(content="Hello!")])

    # Simulate node execution
    result = chat_node(initial)

    print("Messages:")
    for msg in initial.messages + result["messages"]:
        print(f"  {msg.__class__.__name__}: {msg.content}")
