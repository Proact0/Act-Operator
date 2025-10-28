from abc import ABC, abstractmethod

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
    def build(self) -> CompiledStateGraph:
        """Constructs the graph graph.

        Returns:
            CompiledStateGraph: Compiled state graph ready for execution.
        """
        raise NotImplementedError

    def __call__(self) -> CompiledStateGraph:
        """Compiles the graph when invoked like a function.

        Returns:
            CompiledStateGraph: Result returned by :meth:`build`.
        """
        return self.build()
