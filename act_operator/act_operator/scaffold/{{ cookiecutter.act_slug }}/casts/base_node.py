import inspect
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime

LOGGER = logging.getLogger(__name__)


class BaseNode(ABC):
    """Base class for nodes used within LangGraph graphs.

    This class provides a flexible foundation for creating nodes that work
    seamlessly with LangGraph's runtime features.

    Attributes:
        name: Canonical name of the node (class name by default).
        verbose: Flag indicating whether detailed logging is enabled.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Initializes a node instance.

        Args:
            **kwargs: Keyword arguments supporting subclass-specific options.
                verbose (bool): Enable detailed logging. Defaults to False.
        """
        self.name = self.__class__.__name__
        self.verbose = kwargs.get("verbose", False)

    @abstractmethod
    def execute(self, state: Any, **kwargs) -> dict:
        """Processes the incoming state and returns updates.

        This is the main method that subclasses must implement.
        For simple nodes, you only need to work with state.
        For advanced use cases, access config and runtime via kwargs.

        Args:
            state: Mutable graph state passed between nodes.
            **kwargs: Optional keyword arguments that may include:
                - config (RunnableConfig): Configuration with thread_id, tags, etc.
                - runtime (Runtime): Runtime context with store, stream_writer, etc.

        Returns:
            dict: Key/value pairs containing state updates.

        Example:
            Simple node (most common):
            ```python
            def execute(self, state):
                return {"result": state["input"] + " processed"}
            ```

            Advanced node with config:
            ```python
            def execute(self, state, config=None, **kwargs):
                thread_id = self.get_thread_id(config)
                return {"thread_id": thread_id}
            ```

            Advanced node with runtime:
            ```python
            def execute(self, state, runtime=None, **kwargs):
                if runtime and runtime.store:
                    data = runtime.store.get("key")
                return {"data": data}
            ```
        """
        raise NotImplementedError("Must be implemented in a subclass")

    def log(self, message: str, **context) -> None:
        """Logs a message when verbose mode is enabled.

        Args:
            message: The message to log.
            **context: Additional context to include in the log.
        """
        if not self.verbose:
            return

        LOGGER.debug("[%s] %s", self.name, message)
        for key, value in context.items():
            LOGGER.debug("  %s: %r", key, value)

    def get_thread_id(self, config: Optional[RunnableConfig] = None) -> Optional[str]:
        """Extracts thread_id from config if available.

        Args:
            config: Optional RunnableConfig object.

        Returns:
            Thread ID string or None if not available.
        """
        if not config:
            return None
        return config.get("configurable", {}).get("thread_id")

    def get_tags(self, config: Optional[RunnableConfig] = None) -> list[str]:
        """Extracts tags from config if available.

        Args:
            config: Optional RunnableConfig object.

        Returns:
            List of tag strings, empty list if not available.
        """
        if not config:
            return []
        return config.get("tags", [])

    def __call__(
        self,
        state: Any,
        config: Optional[RunnableConfig] = None,
        runtime: Optional[Runtime] = None,
        **kwargs,
    ) -> dict:
        """Allows instances to be invoked like callables.

        This method inspects the execute() signature and only passes
        the parameters it accepts.

        Args:
            state: Current graph state.
            config: Optional RunnableConfig object.
            runtime: Optional Runtime object.
            **kwargs: Extra keyword args forwarded to execute().

        Returns:
            dict: Result from execute().
        """
        # Log entry if verbose
        if self.verbose:
            thread_id = self.get_thread_id(config)
            self.log("Executing", state_keys=list(state.keys()) if hasattr(state, 'keys') else None, thread_id=thread_id)

        # Inspect execute signature to see what parameters it accepts
        sig = inspect.signature(self.execute)
        params = sig.parameters

        # Build kwargs with only the parameters execute accepts
        execute_kwargs = {}
        if "config" in params:
            execute_kwargs["config"] = config
        if "runtime" in params:
            execute_kwargs["runtime"] = runtime

        # Add any additional kwargs if execute has **kwargs
        has_var_keyword = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())
        if has_var_keyword:
            execute_kwargs.update(kwargs)

        # Execute the node
        result = self.execute(state, **execute_kwargs)

        # Log exit if verbose
        if self.verbose:
            self.log("Completed", result_keys=list(result.keys()) if result else None)

        return result


class AsyncBaseNode(ABC):
    """Base class for async nodes used within LangGraph graphs.

    This class provides a flexible foundation for creating async nodes that work
    seamlessly with LangGraph's runtime features.

    Attributes:
        name: Canonical name of the node (class name by default).
        verbose: Flag indicating whether detailed logging is enabled.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Initializes an async node instance.

        Args:
            **kwargs: Keyword arguments supporting subclass-specific options.
                verbose (bool): Enable detailed logging. Defaults to False.
        """
        self.name = self.__class__.__name__
        self.verbose = kwargs.get("verbose", False)

    @abstractmethod
    async def execute(self, state: Any, **kwargs) -> dict:
        """Processes the incoming state asynchronously and returns updates.

        This is the main method that subclasses must implement.
        For simple nodes, you only need to work with state.
        For advanced use cases, access config and runtime via kwargs.

        Args:
            state: Mutable graph state passed between nodes.
            **kwargs: Optional keyword arguments that may include:
                - config (RunnableConfig): Configuration with thread_id, tags, etc.
                - runtime (Runtime): Runtime context with store, stream_writer, etc.

        Returns:
            dict: Key/value pairs containing state updates.

        Example:
            Simple async node (most common):
            ```python
            async def execute(self, state):
                result = await some_async_operation(state["input"])
                return {"result": result}
            ```

            Advanced async node with config:
            ```python
            async def execute(self, state, config=None, **kwargs):
                thread_id = self.get_thread_id(config)
                result = await fetch_data(thread_id)
                return {"result": result}
            ```
        """
        raise NotImplementedError("Must be implemented in a subclass")

    def log(self, message: str, **context) -> None:
        """Logs a message when verbose mode is enabled.

        Args:
            message: The message to log.
            **context: Additional context to include in the log.
        """
        if not self.verbose:
            return

        LOGGER.debug("[%s] %s", self.name, message)
        for key, value in context.items():
            LOGGER.debug("  %s: %r", key, value)

    def get_thread_id(self, config: Optional[RunnableConfig] = None) -> Optional[str]:
        """Extracts thread_id from config if available.

        Args:
            config: Optional RunnableConfig object.

        Returns:
            Thread ID string or None if not available.
        """
        if not config:
            return None
        return config.get("configurable", {}).get("thread_id")

    def get_tags(self, config: Optional[RunnableConfig] = None) -> list[str]:
        """Extracts tags from config if available.

        Args:
            config: Optional RunnableConfig object.

        Returns:
            List of tag strings, empty list if not available.
        """
        if not config:
            return []
        return config.get("tags", [])

    async def __call__(
        self,
        state: Any,
        config: Optional[RunnableConfig] = None,
        runtime: Optional[Runtime] = None,
        **kwargs,
    ) -> dict:
        """Allows instances to be invoked like callables.

        This method inspects the execute() signature and only passes
        the parameters it accepts.

        Args:
            state: Current graph state.
            config: Optional RunnableConfig object.
            runtime: Optional Runtime object.
            **kwargs: Extra keyword args forwarded to execute().

        Returns:
            dict: Result from execute().
        """
        # Log entry if verbose
        if self.verbose:
            thread_id = self.get_thread_id(config)
            self.log("Executing", state_keys=list(state.keys()) if hasattr(state, 'keys') else None, thread_id=thread_id)

        # Inspect execute signature to see what parameters it accepts
        sig = inspect.signature(self.execute)
        params = sig.parameters

        # Build kwargs with only the parameters execute accepts
        execute_kwargs = {}
        if "config" in params:
            execute_kwargs["config"] = config
        if "runtime" in params:
            execute_kwargs["runtime"] = runtime

        # Add any additional kwargs if execute has **kwargs
        has_var_keyword = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())
        if has_var_keyword:
            execute_kwargs.update(kwargs)

        # Execute the node
        result = await self.execute(state, **execute_kwargs)

        # Log exit if verbose
        if self.verbose:
            self.log("Completed", result_keys=list(result.keys()) if result else None)

        return result