"""[Required] Node implementations for the {{ cookiecutter.cast_name }} graph.

Guidelines:
    - Derive each node from :class:`BaseNode` or :class:`AsyncBaseNode`.
    - Implement :meth:`execute` to process state and return updates.
    - Choose your node signature based on what you need:
      * Simple: `def execute(self, state)` - Only needs state
      * With config: `def execute(self, state, config)` - Needs thread_id, tags
      * With runtime: `def execute(self, state, runtime)` - Needs store, stream
      * Full: `def execute(self, state, config, runtime)` - Needs everything
      * Flexible: `def execute(self, state, **kwargs)` - Access via kwargs.get()
    - Use `self.log()` for debugging when `verbose=True`.
"""

from langchain_core.messages import AIMessage

from casts.base_node import AsyncBaseNode, BaseNode


class SampleNode(BaseNode):
    """Simple sync node - only uses state.

    Attributes:
        name: Canonical name of the node (class name by default).
        verbose: Flag indicating whether detailed logging is enabled.
    """

    def execute(self, state):
        """Execute the sample node.

        Args:
            state: Current graph state.

        Returns:
            dict: State updates (must be a dict)
        """
        return {"messages": [AIMessage(content="Welcome to the Act! by Sync Node")]}


class AsyncSampleNode(AsyncBaseNode):
    """Simple async node - only uses state.

    Attributes:
        name: Canonical name of the node (class name by default).
        verbose: Flag indicating whether detailed logging is enabled.
    """

    async def execute(self, state):
        """Execute the sample node.

        Args:
            state: Current graph state.

        Returns:
            dict: State updates (must be a dict)
        """
        return {"messages": [AIMessage(content="Welcome to the Act! by Async Node")]}