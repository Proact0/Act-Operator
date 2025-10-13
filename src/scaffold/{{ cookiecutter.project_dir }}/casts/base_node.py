from abc import ABC, abstractmethod


class BaseNode(ABC):
    """Base class for nodes used within LangGraph workflows.

    Attributes:
        name: Canonical name of the node (class name by default).
        verbose: Flag indicating whether detailed logging is enabled.
    """

    def __init__(self, **kwargs) -> None:
        """Initializes a node instance.

        Args:
            **kwargs: Keyword arguments supporting subclass-specific options.
        """
        self.name = self.__class__.__name__
        self.verbose = kwargs.get("verbose", False)

    @abstractmethod
    def execute(self, state) -> dict:
        """Processes the incoming state and returns updates.

        Args:
            state: Mutable graph state passed between nodes.

        Returns:
            dict: Key/value pairs containing state updates.
        """
        raise NotImplementedError

    def logging(self, method_name: str, **kwargs) -> None:
        """Emits diagnostic messages when verbose mode is enabled.

        Args:
            method_name: Name of the method being logged.
            **kwargs: Additional context to include in the log output.
        """
        if self.verbose:
            print(f"[{self.name}] {method_name}")
            for key, value in kwargs.items():
                print(f"{key}: {value}")

    def __call__(self, state):
        """Allows instances to be invoked like callables.

        Args:
            state: Current workflow state.

        Returns:
            dict: Result from :meth:`execute`.
        """
        return self.execute(state)
