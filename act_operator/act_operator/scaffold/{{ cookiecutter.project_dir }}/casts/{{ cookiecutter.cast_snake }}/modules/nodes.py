"""[Required] Node implementations for the {{ cookiecutter.cast_name }} graph.

Guidelines:
    - Derive each node from :class:`BaseNode`.
    - Implement :meth:`execute` to mutate and return the graph state.
"""

from casts.base_node import BaseNode
from casts.base_node import AsyncBaseNode

class SampleNode(BaseNode):
    """Sample node for the {{ cookiecutter.cast_name }} graph.
    
    Attributes:
        name: Canonical name of the node (class name by default).
        verbose: Flag indicating whether detailed logging is enabled.
    """

    def execute(self, state):
        """Execute the sample node.
        
        Args:
            state: Current graph state.
            
        Returns:
            dict: Result from :meth:`execute`.
        """
        return {"message": "Welcome to the Act! by Sync Node"}

class AsyncSampleNode(AsyncBaseNode):
    """Async sample node for the {{ cookiecutter.cast_name }} graph.
    
    Attributes:
        name: Canonical name of the node (class name by default).
        verbose: Flag indicating whether detailed logging is enabled.
    """

    async def execute(self, state):
        """Execute the sample node.
        
        Args:
            state: Current graph state.
            
        Returns:
            dict: Result from :meth:`execute`.
        """
        return {"message": "Welcome to the Act! by Async Node"}