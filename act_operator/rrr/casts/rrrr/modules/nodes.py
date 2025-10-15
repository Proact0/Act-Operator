"""[Required] Node implementations for the Rrrr workflow.

Guidelines:
    - Derive each node from :class:`BaseNode`.
    - Implement :meth:`execute` to mutate and return the workflow state.
"""

from casts.base_node import BaseNode


class SampleNode(BaseNode):
    """Sample node for the Rrrr workflow."""

    def execute(self, state):
        """Execute the sample node."""
        return {"message": "Welcome to the Act!"}
