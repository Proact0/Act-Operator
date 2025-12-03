"""Base node classes for LangGraph graphs.

This module provides foundational classes for building LangGraph nodes with
flexible execute signatures.

Classes:
    - ``BaseNode``: Sync node base class
    - ``AsyncBaseNode``: Async node base class
"""

from __future__ import annotations

import inspect
import logging
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Mapping, Optional

if TYPE_CHECKING:
    from langchain_core.runnables import RunnableConfig
    from langgraph.runtime import Runtime

__all__ = ["BaseNode", "AsyncBaseNode"]

LOGGER = logging.getLogger(__name__)

# Allowed optional parameters for execute()
_ALLOWED_PARAMS = frozenset({"config", "runtime"})


def _validate_execute(cls: type, *, expect_async: bool) -> None:
    """Validate that a class defines a proper execute implementation."""
    try:
        execute_attr = inspect.getattr_static(cls, "execute")
    except AttributeError as e:
        raise TypeError(f"{cls.__name__} must implement an execute() method.") from e

    if isinstance(execute_attr, (staticmethod, classmethod)):
        raise TypeError(f"{cls.__name__}.execute() must be an instance method.")

    is_async = inspect.iscoroutinefunction(execute_attr)
    if expect_async and not is_async:
        raise TypeError(f"{cls.__name__}.execute() must be defined with 'async def'.")
    if not expect_async and is_async:
        raise TypeError(f"{cls.__name__}.execute() must not be asynchronous.")

    # Validate signature
    sig = inspect.signature(execute_attr)
    params = list(sig.parameters.values())

    # Remove 'self'
    if not params or params[0].name != "self":
        raise TypeError(f"{cls.__name__}.execute() must define 'self' first.")
    params = params[1:]

    # Check 'state' parameter
    if not params or params[0].name != "state":
        raise TypeError(
            f"{cls.__name__}.execute() must declare 'state' as first argument."
        )

    # Check optional parameters
    for param in params[1:]:
        if param.name not in _ALLOWED_PARAMS:
            raise TypeError(
                f"{cls.__name__}.execute() only supports optional args: "
                f"{', '.join(sorted(_ALLOWED_PARAMS))}. Got '{param.name}'."
            )


def _build_kwargs(
    execute_fn: Callable[..., Any],
    config: Any,
    runtime: Any,
) -> dict[str, Any]:
    """Build kwargs dict for execute() based on its signature."""
    params = inspect.signature(execute_fn).parameters
    kwargs: dict[str, Any] = {}

    if "config" in params:
        kwargs["config"] = config
    if "runtime" in params:
        kwargs["runtime"] = runtime

    return kwargs


class BaseNode:
    """Base class for synchronous nodes in LangGraph graphs.

    Subclasses must implement ``execute`` with ``state`` as the first argument,
    and may optionally accept ``config`` and/or ``runtime``.

    Supported execute signatures::

        def execute(self, state): ...
        def execute(self, state, config): ...
        def execute(self, state, runtime): ...
        def execute(self, state, config, runtime): ...

    Attributes:
        name: Canonical name of the node (class name by default).
        verbose: Flag indicating whether detailed logging is enabled.

    Example:
        >>> class MyNode(BaseNode):
        ...     def execute(self, state):
        ...         return {"processed": state["input"].upper()}
    """

    execute: Callable[..., dict]

    def __init__(self, **kwargs: Any) -> None:
        self.name = self.__class__.__name__
        self.verbose = kwargs.get("verbose", False)

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if cls is BaseNode or inspect.isabstract(cls):
            return
        _validate_execute(cls, expect_async=False)

    def __call__(
        self,
        state: Any,
        config: Optional[RunnableConfig] = None,
        runtime: Optional[Runtime] = None,
    ) -> dict:
        """Invoke the node as a callable."""
        if self.verbose:
            LOGGER.debug("[%s] Executing", self.name)

        kwargs = _build_kwargs(self.execute, config, runtime)
        result = self.execute(state, **kwargs)

        if not isinstance(result, dict):
            raise TypeError(
                f"{self.name}.execute() must return a dict, got {type(result).__name__}."
            )

        if self.verbose:
            LOGGER.debug("[%s] Completed", self.name)

        return result

    def log(self, message: str, **context: Any) -> None:
        """Log a debug message when verbose mode is enabled."""
        if not self.verbose:
            return
        LOGGER.debug("[%s] %s", self.name, message)
        for key, value in context.items():
            LOGGER.debug("  %s: %r", key, value)

    def get_thread_id(
        self, config: Optional[Mapping[str, Any]] = None
    ) -> Optional[str]:
        """Extract thread_id from config if available."""
        if not config:
            return None
        configurable = config.get("configurable")
        return configurable.get("thread_id") if configurable else None

    def get_tags(self, config: Optional[Mapping[str, Any]] = None) -> list[str]:
        """Extract tags from config if available."""
        if not config:
            return []
        return config.get("tags", [])


class AsyncBaseNode:
    """Base class for asynchronous nodes in LangGraph graphs.

    Async subclasses must implement ``async def execute`` following the same
    signature rules as ``BaseNode``.

    Supported execute signatures::

        async def execute(self, state): ...
        async def execute(self, state, config): ...
        async def execute(self, state, runtime): ...
        async def execute(self, state, config, runtime): ...

    Attributes:
        name: Canonical name of the node (class name by default).
        verbose: Flag indicating whether detailed logging is enabled.

    Example:
        >>> class MyAsyncNode(AsyncBaseNode):
        ...     async def execute(self, state):
        ...         result = await fetch_data(state["url"])
        ...         return {"data": result}
    """

    execute: Callable[..., Awaitable[dict]]

    def __init__(self, **kwargs: Any) -> None:
        self.name = self.__class__.__name__
        self.verbose = kwargs.get("verbose", False)

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if cls is AsyncBaseNode or inspect.isabstract(cls):
            return
        _validate_execute(cls, expect_async=True)

    async def __call__(
        self,
        state: Any,
        config: Optional[RunnableConfig] = None,
        runtime: Optional[Runtime] = None,
    ) -> dict:
        """Invoke the async node as a callable."""
        if self.verbose:
            LOGGER.debug("[%s] Executing", self.name)

        kwargs = _build_kwargs(self.execute, config, runtime)
        result = await self.execute(state, **kwargs)

        if not isinstance(result, dict):
            raise TypeError(
                f"{self.name}.execute() must return a dict, got {type(result).__name__}."
            )

        if self.verbose:
            LOGGER.debug("[%s] Completed", self.name)

        return result

    def log(self, message: str, **context: Any) -> None:
        """Log a debug message when verbose mode is enabled."""
        if not self.verbose:
            return
        LOGGER.debug("[%s] %s", self.name, message)
        for key, value in context.items():
            LOGGER.debug("  %s: %r", key, value)

    def get_thread_id(
        self, config: Optional[Mapping[str, Any]] = None
    ) -> Optional[str]:
        """Extract thread_id from config if available."""
        if not config:
            return None
        configurable = config.get("configurable")
        return configurable.get("thread_id") if configurable else None

    def get_tags(self, config: Optional[Mapping[str, Any]] = None) -> list[str]:
        """Extract tags from config if available."""
        if not config:
            return []
        return config.get("tags", [])
