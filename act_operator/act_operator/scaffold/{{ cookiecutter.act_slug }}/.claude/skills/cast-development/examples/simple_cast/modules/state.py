"""Simple Cast State - Basic state structure."""

from dataclasses import dataclass
from typing import Annotated

from langchain.messages import AnyMessage
from langgraph.graph.message import add_messages


@dataclass(kw_only=True)
class InputState:
    """Input state for the graph.

    Attributes:
        name: User's name for greeting
    """
    name: str


@dataclass(kw_only=True)
class OutputState:
    """Output state for the graph.

    Attributes:
        messages: List of messages (accumulated)
    """
    messages: Annotated[list[AnyMessage], add_messages]


@dataclass(kw_only=True)
class State:
    """Internal graph state.

    Combines input and output fields for processing.

    Attributes:
        name: User's name
        messages: Message history
    """
    name: str
    messages: Annotated[list[AnyMessage], add_messages]
