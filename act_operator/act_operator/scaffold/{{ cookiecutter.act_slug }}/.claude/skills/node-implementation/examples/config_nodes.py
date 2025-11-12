"""Examples of nodes using the config parameter.

The config parameter provides access to:
- thread_id: Unique identifier for conversation threads
- tags: List of tags for filtering/categorization
- metadata: Additional configuration metadata

These are useful for thread-aware behavior and conditional logic.
"""

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig

from casts.base_node import BaseNode


class ThreadAwareNode(BaseNode):
    """Node that uses thread_id from config.

    Use this pattern when you need to:
    - Track conversation threads
    - Store/retrieve thread-specific data
    - Implement per-thread logic
    """

    def execute(self, state, config: RunnableConfig = None) -> dict:
        """Execute with thread awareness.

        Args:
            state: Current graph state
            config: Configuration with thread_id

        Returns:
            dict: State update with thread info
        """
        thread_id = self.get_thread_id(config)
        self.log(f"Processing in thread: {thread_id}")

        # Use thread_id for thread-specific logic
        if thread_id:
            message = f"Processing query in thread {thread_id}: {state.query}"
        else:
            message = f"Processing query (no thread): {state.query}"

        return {"messages": [AIMessage(content=message)]}


class TagBasedRoutingNode(BaseNode):
    """Node that uses tags from config for conditional logic.

    Use this pattern when you need to:
    - Route based on tags
    - Apply tag-specific processing
    - Filter or categorize requests
    """

    def execute(self, state, config: RunnableConfig = None) -> dict:
        """Execute with tag-based routing.

        Args:
            state: Current graph state
            config: Configuration with tags

        Returns:
            dict: State update with routing decision
        """
        tags = self.get_tags(config)
        self.log(f"Processing with tags: {tags}")

        # Example: Different processing based on tags
        if "priority" in tags:
            processing_level = "high_priority"
            message = f"[PRIORITY] Processing: {state.query}"
        elif "batch" in tags:
            processing_level = "batch"
            message = f"[BATCH] Queued: {state.query}"
        else:
            processing_level = "normal"
            message = f"Processing: {state.query}"

        return {
            "messages": [AIMessage(content=message)],
            "processing_level": processing_level,
        }


class ConfigurableNode(BaseNode):
    """Node that accesses multiple config properties.

    Use this pattern when you need to:
    - Access multiple config properties
    - Implement complex configuration logic
    - Debug configuration issues
    """

    def execute(self, state, config: RunnableConfig = None, **kwargs) -> dict:
        """Execute with full config access.

        Args:
            state: Current graph state
            config: Full configuration object
            **kwargs: Additional arguments

        Returns:
            dict: State update with config info
        """
        if config:
            thread_id = self.get_thread_id(config)
            tags = self.get_tags(config)
            configurable = config.get("configurable", {})
            
            self.log("Configuration details", thread_id=thread_id, tags=tags)

            message = f"Query: {state.query}\n"
            message += f"Thread: {thread_id or 'None'}\n"
            message += f"Tags: {tags or []}\n"
            message += f"Configurable: {list(configurable.keys())}"
        else:
            message = f"Query: {state.query}\nNo config provided"

        return {"messages": [AIMessage(content=message)]}


class VerboseLoggingNode(BaseNode):
    """Node that demonstrates verbose logging with config.

    Use this pattern when you need to:
    - Debug node execution
    - Log configuration state
    - Track execution flow
    """

    def __init__(self, verbose: bool = True):
        """Initialize with verbose logging enabled.

        Args:
            verbose: Enable verbose logging (default: True)
        """
        super().__init__(verbose=verbose)

    def execute(self, state, config: RunnableConfig = None) -> dict:
        """Execute with verbose logging.

        Args:
            state: Current graph state
            config: Configuration object

        Returns:
            dict: State update
        """
        # Log entry
        self.log("Node started", query=state.query)

        # Log config
        if config:
            self.log(
                "Configuration",
                thread_id=self.get_thread_id(config),
                tags=self.get_tags(config),
            )

        # Process
        result = {"messages": [AIMessage(content=f"Processed: {state.query}")]}

        # Log exit
        self.log("Node completed", result_keys=list(result.keys()))

        return result


# Usage example
if __name__ == "__main__":
    from dataclasses import dataclass
    from typing import List

    @dataclass(kw_only=True)
    class State:
        query: str
        messages: List = None
        processing_level: str = "normal"

        def __post_init__(self):
            if self.messages is None:
                self.messages = []

    # Test ThreadAwareNode
    print("=== ThreadAwareNode ===")
    node = ThreadAwareNode()
    state = State(query="Hello")
    config = RunnableConfig(configurable={"thread_id": "thread-123"})
    result = node(state, config=config)
    print(f"Result: {result}\n")

    # Test TagBasedRoutingNode
    print("=== TagBasedRoutingNode ===")
    node = TagBasedRoutingNode()
    state = State(query="Urgent request")
    config = RunnableConfig(tags=["priority", "urgent"])
    result = node(state, config=config)
    print(f"Result: {result}\n")

    # Test ConfigurableNode
    print("=== ConfigurableNode ===")
    node = ConfigurableNode()
    state = State(query="Full config test")
    config = RunnableConfig(
        configurable={"thread_id": "thread-456", "user_id": "user-789"},
        tags=["test", "example"],
    )
    result = node(state, config=config)
    print(f"Result: {result}\n")

    # Test VerboseLoggingNode
    print("=== VerboseLoggingNode ===")
    node = VerboseLoggingNode(verbose=True)
    state = State(query="Verbose test")
    config = RunnableConfig(tags=["debug"])
    result = node(state, config=config)
    print(f"Result: {result}")
