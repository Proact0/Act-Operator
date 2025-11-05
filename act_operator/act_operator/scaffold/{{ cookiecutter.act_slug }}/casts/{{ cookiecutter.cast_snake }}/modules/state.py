"""[Required] State definition shared across Test graphs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from langchain.messages import AnyMessage
from langgraph.graph.message import add_messages


@dataclass(kw_only=True)
class InputState:
    """Input state container.

    Attributes:
        query: User query
    """

    query: str


@dataclass(kw_only=True)
class OutputState:
    """Output state container.

    Attributes:
        messages: Additional messages
    """

    messages: Annotated[list[AnyMessage], add_messages]


@dataclass(kw_only=True)
class State:
    """Graph state container.

    Attributes:
        query: User query
        messages: Additional messages
    """

    query: str
    messages: Annotated[list[AnyMessage], add_messages]
