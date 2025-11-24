import inspect
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime

LOGGER = logging.getLogger(__name__)


def _validate_signature(node_name: str, sig: inspect.Signature) -> None:
    """Ensures execute(state, [config], [runtime]) signature only."""
    params = list(sig.parameters.values())
    if not params:
        raise TypeError(f"{node_name}.execute() must accept a 'state' argument.")

    state_param = params[0]
    if state_param.name != "state":
        raise TypeError(f"{node_name}.execute() must declare 'state' first.")
    if state_param.kind not in (
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
    ):
        raise TypeError(
            f"{node_name}.execute() must allow passing 'state' as a positional argument."
        )

    allowed = {"config", "runtime"}
    for param in params[1:]:
        if param.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            raise TypeError(f"{node_name}.execute() cannot use *args or **kwargs.")
        if param.name not in allowed:
            raise TypeError(
                f"{node_name}.execute() only supports optional args: {', '.join(sorted(allowed))}."
            )
        if param.kind == inspect.Parameter.POSITIONAL_ONLY:
            raise TypeError(
                f"{node_name}.execute() parameter '{param.name}' cannot be positional-only."
            )


def _build_execute_kwargs(
    *,
    node_name: str,
    sig: inspect.Signature,
    config: Optional[RunnableConfig],
    runtime: Optional[Runtime],
) -> dict[str, Any]:
    """Returns kwargs for execute based on provided config/runtime."""
    execute_kwargs: dict[str, Any] = {}
    expects_config = "config" in sig.parameters
    expects_runtime = "runtime" in sig.parameters

    if expects_config:
        config_param = sig.parameters["config"]
        if config is None and config_param.default is inspect._empty:
            raise TypeError(f"{node_name}.execute() requires 'config' but none was provided.")
        execute_kwargs["config"] = config

    if expects_runtime:
        runtime_param = sig.parameters["runtime"]
        if runtime is None and runtime_param.default is inspect._empty:
            raise TypeError(
                f"{node_name}.execute() requires 'runtime' but none was provided."
            )
        execute_kwargs["runtime"] = runtime

    return execute_kwargs


class BaseNode(ABC):
    """Base class for nodes used within LangGraph graphs.

    This class provides a flexible foundation for creating nodes that work
    seamlessly with LangGraph's runtime features.

    Attributes:
        name: Canonical name of the node (class name by default).
        verbose: Flag indicating whether detailed logging is enabled.
    """

    def __init__(self, **kwargs) -> None:
        """Initializes a node instance.

        Args:
            **kwargs: Keyword arguments supporting subclass-specific options.
                verbose (bool): Enable detailed logging. Defaults to False.
        """
        self.name = self.__class__.__name__
        self.verbose = kwargs.get("verbose", False)

    @abstractmethod
    def execute(
        self,
        state,
        config: Optional[RunnableConfig] = None,
        runtime: Optional[Runtime] = None,
    ) -> dict:
        """Processes the incoming state and returns updates.

        This is the main method that subclasses must implement.
        For simple nodes, you only need to work with state.
        For advanced use cases, access config and runtime via kwargs.

        Args:
            state: Mutable graph state passed between nodes.
            config: Optional RunnableConfig containing thread/call metadata.
            runtime: Optional Runtime providing store, stream writer, etc.

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
            def execute(self, state, config=None):
                thread_id = self.get_thread_id(config)
                return {"thread_id": thread_id}
            ```

            Advanced node with runtime:
            ```python
            def execute(self, state, runtime=None):
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
        state,
        config: Optional[RunnableConfig] = None,
        runtime: Optional[Runtime] = None,
    ) -> dict:
        """Allows instances to be invoked like callables.

        This method inspects the execute() signature and only passes
        the parameters it accepts.

        Args:
            state: Current graph state.
            config: Optional RunnableConfig object.
            runtime: Optional Runtime object.

        Returns:
            dict: Result from execute().
        """
        # Log entry if verbose
        if self.verbose:
            thread_id = self.get_thread_id(config)
            self.log(
                "Executing",
                state_keys=list(state.keys()) if hasattr(state, "keys") else None,
                thread_id=thread_id,
            )

        # Inspect execute signature to see what parameters it accepts
        sig = inspect.signature(self.execute)
        _validate_signature(self.name, sig)
        execute_kwargs = _build_execute_kwargs(
            node_name=self.name,
            sig=sig,
            config=config,
            runtime=runtime,
        )

        # Execute the node
        result = self.execute(state, **execute_kwargs)
        if not isinstance(result, dict):
            raise TypeError(f"{self.name}.execute() must return a dict, got {type(result)}.")

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

    def __init__(self, **kwargs) -> None:
        """Initializes an async node instance.

        Args:
            **kwargs: Keyword arguments supporting subclass-specific options.
                verbose (bool): Enable detailed logging. Defaults to False.
        """
        self.name = self.__class__.__name__
        self.verbose = kwargs.get("verbose", False)

    @abstractmethod
    async def execute(
        self,
        state,
        config: Optional[RunnableConfig] = None,
        runtime: Optional[Runtime] = None,
    ) -> dict:
        """Processes the incoming state asynchronously and returns updates.

        This is the main method that subclasses must implement.
        For simple nodes, you only need to work with state.
        For advanced use cases, access config and runtime via kwargs.

        Args:
            state: Mutable graph state passed between nodes.
            config: Optional RunnableConfig containing thread/call metadata.
            runtime: Optional Runtime providing store, stream writer, etc.

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
            async def execute(self, state, config=None):
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
        state,
        config: Optional[RunnableConfig] = None,
        runtime: Optional[Runtime] = None,
    ) -> dict:
        """Allows instances to be invoked like callables.

        This method inspects the execute() signature and only passes
        the parameters it accepts.

        Args:
            state: Current graph state.
            config: Optional RunnableConfig object.
            runtime: Optional Runtime object.

        Returns:
            dict: Result from execute().
        """
        # Log entry if verbose
        if self.verbose:
            thread_id = self.get_thread_id(config)
            self.log(
                "Executing",
                state_keys=list(state.keys()) if hasattr(state, "keys") else None,
                thread_id=thread_id,
            )

        # Inspect execute signature to see what parameters it accepts
        sig = inspect.signature(self.execute)
        _validate_signature(self.name, sig)
        execute_kwargs = _build_execute_kwargs(
            node_name=self.name,
            sig=sig,
            config=config,
            runtime=runtime,
        )

        # Execute the node
        result = await self.execute(state, **execute_kwargs)
        if not isinstance(result, dict):
            raise TypeError(f"{self.name}.execute() must return a dict, got {type(result)}.")

        # Log exit if verbose
        if self.verbose:
            self.log("Completed", result_keys=list(result.keys()) if result else None)

        return result
