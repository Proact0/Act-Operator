from abc import ABC, abstractmethod
from typing import Any, Optional

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph


class BaseGraph(ABC):
    """Base class for LangGraph graphs.

    Attributes:
        name: Canonical name of the graph (class name by default).
    """

    def __init__(self) -> None:
        """Initializes the graph and assigns its canonical name."""
        self.name = self.__class__.__name__

    @abstractmethod
    def build(
        self,
        checkpointer: Optional[BaseCheckpointSaver] = None,
        interrupt_before: Optional[list[str]] = None,
        interrupt_after: Optional[list[str]] = None,
        debug: bool = False,
    ) -> CompiledStateGraph:
        """Constructs and compiles the graph with optional runtime configuration.

        Args:
            checkpointer: Optional checkpointer for persistence and state management.
            interrupt_before: List of node names to interrupt before execution.
            interrupt_after: List of node names to interrupt after execution.
            debug: Enable debug mode for detailed execution tracing.

        Returns:
            CompiledStateGraph: Compiled state graph ready for execution.
        """
        raise NotImplementedError

    def __call__(
        self,
        checkpointer: Optional[BaseCheckpointSaver] = None,
        interrupt_before: Optional[list[str]] = None,
        interrupt_after: Optional[list[str]] = None,
        debug: bool = False,
    ) -> CompiledStateGraph:
        """Compiles the graph when invoked like a function.

        Args:
            checkpointer: Optional checkpointer for persistence and state management.
            interrupt_before: List of node names to interrupt before execution.
            interrupt_after: List of node names to interrupt after execution.
            debug: Enable debug mode for detailed execution tracing.

        Returns:
            CompiledStateGraph: Result returned by :meth:`build`.
        """
        return self.build(
            checkpointer=checkpointer,
            interrupt_before=interrupt_before,
            interrupt_after=interrupt_after,
            debug=debug,
        )
