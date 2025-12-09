"""[Required] State definition shared across sam graphs.

Guidelines:
    - Create TypedDict classes for input, output, overall state, and any other state you need.
    - Use `MessagesState` from langgraph.graph or use `Annotated[list[AnyMessage], add_messages]` for messages to enable proper message merging.
    - When inheriting from MessagesState, do not override the messages field.

Official document URL:
    - State: https://docs.langchain.com/oss/python/langgraph/graph-api#state
"""

from langgraph.graph import MessagesState
from typing_extensions import TypedDict


class InputState(TypedDict):
    """Input state container.

    Attributes:
        query: User query
    """

    query: str


class OutputState(TypedDict):
    """Output state container.

    Attributes:
        messages: Additional messages (inherited from MessagesState)
    """

    result: str


class State(MessagesState):
    """Graph state container.

    Attributes:
        query: User query
        messages: Additional messages (inherited from MessagesState)
    """

    # messages field is inherited from MessagesState
    # It is defined as: messages: Annotated[list[AnyMessage], add_messages]
    result: str
    query: str
