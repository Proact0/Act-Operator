from abc import ABC, abstractmethod

from langgraph.graph.state import CompiledStateGraph


class BaseGraph(ABC):
    """Base class for LangGraph graphs.

    This class provides a base implementation for LangGraph graphs.
    Subclasses must implement the `build` method to define the graph structure.

    Attributes:
        name: Canonical name of the graph (class name by default).
    """

    def __init__(self) -> None:
        """Initializes the graph and assigns its canonical name."""
        self.name = self.__class__.__name__

    @abstractmethod
    def build(self) -> CompiledStateGraph:
        """Constructs the graph structure (nodes and edges only).

        This method should:
        1. Create a StateGraph instance with appropriate state schema
        2. Add nodes using builder.add_node()
        3. Add edges using builder.add_edge() or builder.add_conditional_edges()
        4. Return the COMPILED StateGraph

        Returns:
            CompiledStateGraph: Compiled state graph.
        """
        raise NotImplementedError

    def __call__(self) -> CompiledStateGraph:
        """Compiles the graph when invoked like a function.

        Returns:
            CompiledStateGraph: Result returned by :meth:`build`.
        """
        return self.build()
