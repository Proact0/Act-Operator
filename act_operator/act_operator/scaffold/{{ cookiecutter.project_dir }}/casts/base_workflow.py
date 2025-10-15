from abc import ABC, abstractmethod

from langgraph.graph.state import CompiledStateGraph


class BaseWorkflow(ABC):
    """Base class for LangGraph workflows.

    Attributes:
        name: Canonical name of the workflow (class name by default).
    """

    def __init__(self) -> None:
        """Initializes the workflow and assigns its canonical name."""
        self.name = self.__class__.__name__

    @abstractmethod
    def build(self) -> CompiledStateGraph:
        """Constructs the workflow graph.

        Returns:
            CompiledStateGraph: Compiled state graph ready for execution.
        """
        raise NotImplementedError

    def __call__(self) -> CompiledStateGraph:
        """Compiles the workflow when invoked like a function.

        Returns:
            CompiledStateGraph: Result returned by :meth:`build`.
        """
        return self.build()
