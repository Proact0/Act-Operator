"""Examples of nodes using the runtime parameter.

The runtime parameter provides access to:
- store: Persistent key-value store for state across invocations
- stream_writer: For streaming intermediate results
- background_tasks: For managing async background operations

These are useful for persistence, streaming, and complex async patterns.
"""

from langchain_core.messages import AIMessage
from langgraph.runtime import Runtime

from casts.base_node import BaseNode


class PersistentCounterNode(BaseNode):
    """Node that maintains a counter using the store.

    Use this pattern when you need to:
    - Track metrics across invocations
    - Maintain counters or accumulators
    - Store simple state persistently
    """

    def execute(self, state, runtime: Runtime = None) -> dict:
        """Execute with persistent counter.

        Args:
            state: Current graph state
            runtime: Runtime with store access

        Returns:
            dict: State update with counter value
        """
        if not runtime or not runtime.store:
            self.log("No store available, skipping counter", level="warning")
            return {"messages": [AIMessage(content="Counter not available")]}

        # Get current count
        count = runtime.store.get("query_count", 0)
        count += 1

        # Update store
        runtime.store.put("query_count", count)

        self.log(f"Query count: {count}")

        message = f"Query #{count}: {state.query}"
        return {"messages": [AIMessage(content=message)]}


class CachedDataNode(BaseNode):
    """Node that caches data using the store.

    Use this pattern when you need to:
    - Cache expensive computations
    - Avoid redundant processing
    - Store temporary results
    """

    def execute(self, state, runtime: Runtime = None) -> dict:
        """Execute with data caching.

        Args:
            state: Current graph state
            runtime: Runtime with store access

        Returns:
            dict: State update with cached or computed result
        """
        if not runtime or not runtime.store:
            # No cache available, compute fresh
            result = self._compute(state.query)
            return {"messages": [AIMessage(content=f"Fresh: {result}")]}

        # Try to get from cache
        cache_key = f"cache_{state.query}"
        cached = runtime.store.get(cache_key)

        if cached:
            self.log(f"Cache hit for: {state.query}")
            return {"messages": [AIMessage(content=f"Cached: {cached}")]}

        # Cache miss, compute and store
        self.log(f"Cache miss for: {state.query}")
        result = self._compute(state.query)
        runtime.store.put(cache_key, result)

        return {"messages": [AIMessage(content=f"Computed: {result}")]}

    def _compute(self, query: str) -> str:
        """Simulate expensive computation.

        Args:
            query: Input query

        Returns:
            Computed result
        """
        return f"Processed: {query.upper()}"


class SessionStateNode(BaseNode):
    """Node that maintains session state using the store.

    Use this pattern when you need to:
    - Track user sessions
    - Maintain conversation context
    - Store user preferences
    """

    def execute(self, state, runtime: Runtime = None) -> dict:
        """Execute with session state.

        Args:
            state: Current graph state
            runtime: Runtime with store access

        Returns:
            dict: State update with session info
        """
        if not runtime or not runtime.store:
            return {"messages": [AIMessage(content="Session not available")]}

        # Get or initialize session
        session = runtime.store.get("session", {})
        
        # Update session
        if "queries" not in session:
            session["queries"] = []
        session["queries"].append(state.query)
        session["last_query"] = state.query
        session["query_count"] = len(session["queries"])

        # Save session
        runtime.store.put("session", session)

        self.log(
            "Session updated",
            query_count=session["query_count"],
            last_query=session["last_query"],
        )

        message = f"Session query {session['query_count']}: {state.query}\n"
        message += f"History: {session['queries']}"

        return {"messages": [AIMessage(content=message)]}


class StreamingNode(BaseNode):
    """Node that streams intermediate results.

    Use this pattern when you need to:
    - Stream partial results to users
    - Provide real-time feedback
    - Handle long-running operations
    """

    def execute(self, state, runtime: Runtime = None) -> dict:
        """Execute with streaming output.

        Args:
            state: Current graph state
            runtime: Runtime with stream_writer access

        Returns:
            dict: State update
        """
        if runtime and runtime.stream_writer:
            # Stream progress updates
            words = state.query.split()
            for i, word in enumerate(words, 1):
                chunk = {"progress": f"Processing word {i}/{len(words)}: {word}"}
                runtime.stream_writer(chunk)
                self.log(f"Streamed: {chunk}")

        # Return final result
        result = f"Processed all {len(state.query.split())} words"
        return {"messages": [AIMessage(content=result)]}


class FullRuntimeNode(BaseNode):
    """Node that demonstrates full runtime usage.

    Use this pattern when you need to:
    - Use multiple runtime features
    - Implement complex patterns
    - Build production-ready nodes
    """

    def execute(self, state, runtime: Runtime = None, **kwargs) -> dict:
        """Execute with full runtime access.

        Args:
            state: Current graph state
            runtime: Full runtime object
            **kwargs: Additional arguments

        Returns:
            dict: State update
        """
        self.log("Processing with full runtime")

        result_parts = [f"Query: {state.query}"]

        if runtime:
            # Use store
            if runtime.store:
                count = runtime.store.get("total_count", 0) + 1
                runtime.store.put("total_count", count)
                result_parts.append(f"Total queries: {count}")
                self.log(f"Stored count: {count}")

            # Use stream_writer
            if runtime.stream_writer:
                runtime.stream_writer({"status": "processing"})
                self.log("Streamed status update")

        message = "\n".join(result_parts)
        return {"messages": [AIMessage(content=message)]}


# Usage example
if __name__ == "__main__":
    from dataclasses import dataclass
    from typing import List

    @dataclass(kw_only=True)
    class State:
        query: str
        messages: List = None

        def __post_init__(self):
            if self.messages is None:
                self.messages = []

    # Simple in-memory store for testing
    class SimpleStore:
        def __init__(self):
            self.data = {}

        def get(self, key, default=None):
            return self.data.get(key, default)

        def put(self, key, value):
            self.data[key] = value

    # Create runtime with store
    runtime = Runtime(store=SimpleStore())

    # Test PersistentCounterNode
    print("=== PersistentCounterNode ===")
    node = PersistentCounterNode()
    for i in range(3):
        state = State(query=f"Query {i+1}")
        result = node(state, runtime=runtime)
        print(f"Result {i+1}: {result}")
    print()

    # Test CachedDataNode
    print("=== CachedDataNode ===")
    node = CachedDataNode()
    state = State(query="hello")
    result1 = node(state, runtime=runtime)
    print(f"First call: {result1}")
    result2 = node(state, runtime=runtime)
    print(f"Second call: {result2}")
    print()

    # Test SessionStateNode
    print("=== SessionStateNode ===")
    node = SessionStateNode()
    for query in ["How are you?", "What's the weather?", "Tell me a joke"]:
        state = State(query=query)
        result = node(state, runtime=runtime)
        print(f"Result: {result}")
    print()

    # Test FullRuntimeNode
    print("=== FullRuntimeNode ===")
    node = FullRuntimeNode(verbose=True)
    state = State(query="Full runtime test")
    result = node(state, runtime=runtime)
    print(f"Result: {result}")
