"""[Required] Node implementations for the New Enw graph.

Guidelines:
    - Derive each node from :class:`BaseNode`.
    - Implement :meth:`execute` to mutate and return the graph state.
"""

from casts.base_node import BaseNode
from casts.base_node import AsyncBaseNode

class SampleNode(BaseNode):
    """Sample node for the New Enw graph."""

    def execute(self, state):
        """Execute the sample node."""
        return {"message": "Welcome to the Act!"}

class AsyncSampleNode(AsyncBaseNode):
    """Async sample node for the New Enw graph."""

    async def execute(self, state):
        """Execute the sample node."""
        return {"message": "Welcome to the Act!"}