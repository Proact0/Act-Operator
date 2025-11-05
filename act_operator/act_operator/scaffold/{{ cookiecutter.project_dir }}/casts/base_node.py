import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime

LOGGER = logging.getLogger(__name__)


class BaseNode(ABC):
    """Base class for nodes used within LangGraph graphs.

    Attributes:
        name: Canonical name of the node (class name by default).
        verbose: Flag indicating whether detailed logging is enabled.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Initializes a node instance.

        Args:
            **kwargs: Keyword arguments supporting subclass-specific options.
        """
        self.name = self.__class__.__name__
        self.verbose = kwargs.get("verbose", False)

    @abstractmethod
    def execute(
        self,
        state: Any,
        config: Optional[RunnableConfig] = None,
        runtime: Optional[Runtime] = None,
    ) -> dict:
        """Processes the incoming state and returns updates.

        Args:
            state: Mutable graph state passed between nodes.
            config: Optional RunnableConfig object containing configuration info
                like thread_id and tracing information like tags.
            runtime: Optional Runtime object containing runtime context like
                store and stream_writer.

        Returns:
            dict: Key/value pairs containing state updates.
        """
        raise NotImplementedError("Must be implemented in a subclass")

    def logging(self, method_name: str, **kwargs) -> None:
        """Emits diagnostic messages when verbose mode is enabled.

        Args:
            method_name: Name of the method being logged.
            **kwargs: Additional context to include in the log output.
        """
        if not self.verbose:
            return

        LOGGER.debug("[%s] %s", self.name, method_name)
        for key, value in kwargs.items():
            LOGGER.debug("%s: %r", key, value)

    def __call__(
        self,
        state: Any,
        config: Optional[RunnableConfig] = None,
        runtime: Optional[Runtime] = None,
        **kwargs,
    ) -> dict:
        """Allows instances to be invoked like callables.

        Args:
            state: Current graph state.
            config: Optional RunnableConfig object.
            runtime: Optional Runtime object.
            **kwargs: Extra keyword args forwarded to :meth:`execute` for flexibility.

        Returns:
            dict: Result from :meth:`execute`.
        """
        return self.execute(state, config=config, runtime=runtime, **kwargs)


class AsyncBaseNode(ABC):
    """Base class for async nodes used within LangGraph graphs.

    Attributes:
        name: Canonical name of the node (class name by default).
        verbose: Flag indicating whether detailed logging is enabled.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Initializes an async node instance.

        Args:
            **kwargs: Keyword arguments supporting subclass-specific options.
        """
        self.name = self.__class__.__name__
        self.verbose = kwargs.get("verbose", False)

    @abstractmethod
    async def execute(
        self,
        state: Any,
        config: Optional[RunnableConfig] = None,
        runtime: Optional[Runtime] = None,
    ) -> dict:
        """Processes the incoming state asynchronously and returns updates.

        Args:
            state: Mutable graph state passed between nodes.
            config: Optional RunnableConfig object containing configuration info
                like thread_id and tracing information like tags.
            runtime: Optional Runtime object containing runtime context like
                store and stream_writer.

        Returns:
            dict: Key/value pairs containing state updates.
        """
        raise NotImplementedError("Must be implemented in a subclass")

    def logging(self, method_name: str, **kwargs) -> None:
        """Emits diagnostic messages when verbose mode is enabled.

        Args:
            method_name: Name of the method being logged.
            **kwargs: Additional context to include in the log output.
        """
        if not self.verbose:
            return

        LOGGER.debug("[%s] %s", self.name, method_name)
        for key, value in kwargs.items():
            LOGGER.debug("%s: %r", key, value)

    async def __call__(
        self,
        state: Any,
        config: Optional[RunnableConfig] = None,
        runtime: Optional[Runtime] = None,
        **kwargs,
    ) -> dict:
        """Allows instances to be invoked like callables.

        Args:
            state: Current graph state.
            config: Optional RunnableConfig object.
            runtime: Optional Runtime object.
            **kwargs: Extra keyword args forwarded to :meth:`execute` for flexibility.

        Returns:
            dict: Result from :meth:`execute`.
        """
        return await self.execute(state, config=config, runtime=runtime, **kwargs)