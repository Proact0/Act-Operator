"""Advanced Cast State - Message-based state."""

from dataclasses import dataclass
from typing import Annotated

from langchain.messages import AnyMessage
from langgraph.graph.message import add_messages


@dataclass(kw_only=True)
class InputState:
    """Input state for the graph.

    Attributes:
        query: User's query to the agent
    """
    query: str


@dataclass(kw_only=True)
class OutputState:
    """Output state for the graph.

    Attributes:
        messages: Conversation history with tool results
    """
    messages: Annotated[list[AnyMessage], add_messages]


@dataclass(kw_only=True)
class State:
    """Internal graph state.

    Attributes:
        query: User's query
        messages: Full message history (user, agent, tool messages)
    """
    query: str
    messages: Annotated[list[AnyMessage], add_messages]
