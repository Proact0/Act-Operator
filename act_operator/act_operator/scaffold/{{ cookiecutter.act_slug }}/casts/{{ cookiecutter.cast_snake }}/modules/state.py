"""[Required] State definition shared across Test graphs.

Guidelines:
    - Create dataclass classes for input, output, and overall state.
    - Use `kw_only=True` to make the classes immutable.
    - Use `Annotated` to add metadata to the classes.

Official document URL: 
    - State: https://docs.langchain.com/oss/python/langgraph/graph-api#state
    - Messages: https://docs.langchain.com/oss/python/langchain/messages
"""

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
