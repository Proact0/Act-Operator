"""Examples of AsyncBaseNode implementations.

AsyncBaseNode is used for nodes that perform async operations:
- API calls
- Database queries
- Concurrent processing
- I/O-bound operations

Use async nodes when you need true asynchronous execution.
"""

import asyncio
from typing import List

from langchain_core.messages import AIMessage

from casts.base_node import AsyncBaseNode


class AsyncAPINode(AsyncBaseNode):
    """Node that makes async API calls.

    Use this pattern when you need to:
    - Call external APIs
    - Perform I/O-bound operations
    - Avoid blocking the event loop
    """

    async def execute(self, state) -> dict:
        """Execute with async API call.

        Args:
            state: Current graph state

        Returns:
            dict: State update with API response
        """
        self.log(f"Making async API call for: {state.query}")

        # Simulate async API call
        response = await self._call_api(state.query)

        return {"messages": [AIMessage(content=f"API Response: {response}")]}

    async def _call_api(self, query: str) -> str:
        """Simulate async API call.

        Args:
            query: Query to send to API

        Returns:
            API response
        """
        # Simulate network delay
        await asyncio.sleep(0.1)
        return f"Processed: {query}"


class ParallelProcessingNode(AsyncBaseNode):
    """Node that processes multiple items concurrently.

    Use this pattern when you need to:
    - Process multiple items in parallel
    - Fan-out operations
    - Maximize throughput
    """

    async def execute(self, state) -> dict:
        """Execute with parallel processing.

        Args:
            state: Current graph state

        Returns:
            dict: State update with all results
        """
        self.log(f"Processing query in parallel: {state.query}")

        # Split query into words and process in parallel
        words = state.query.split()
        tasks = [self._process_word(word) for word in words]
        results = await asyncio.gather(*tasks)

        combined = " | ".join(results)
        return {"messages": [AIMessage(content=f"Parallel results: {combined}")]}

    async def _process_word(self, word: str) -> str:
        """Process a single word asynchronously.

        Args:
            word: Word to process

        Returns:
            Processed word
        """
        await asyncio.sleep(0.05)  # Simulate processing
        return word.upper()


class AsyncDatabaseNode(AsyncBaseNode):
    """Node that performs async database operations.

    Use this pattern when you need to:
    - Query databases asynchronously
    - Perform batch operations
    - Manage database connections efficiently
    """

    def __init__(self, verbose: bool = False):
        """Initialize with mock database.

        Args:
            verbose: Enable verbose logging
        """
        super().__init__(verbose=verbose)
        self.db = {"user1": "Alice", "user2": "Bob", "user3": "Charlie"}

    async def execute(self, state) -> dict:
        """Execute with async database query.

        Args:
            state: Current graph state

        Returns:
            dict: State update with query results
        """
        self.log(f"Querying database for: {state.query}")

        # Simulate async database query
        results = await self._query_db(state.query)

        return {"messages": [AIMessage(content=f"DB Results: {results}")]}

    async def _query_db(self, query: str) -> List[str]:
        """Simulate async database query.

        Args:
            query: Search query

        Returns:
            Query results
        """
        await asyncio.sleep(0.1)  # Simulate query time
        
        # Simple search
        results = [v for k, v in self.db.items() if query.lower() in v.lower()]
        return results if results else ["No results found"]


class AsyncChainNode(AsyncBaseNode):
    """Node that chains multiple async operations.

    Use this pattern when you need to:
    - Chain async operations sequentially
    - Handle complex async workflows
    - Manage dependencies between async calls
    """

    async def execute(self, state) -> dict:
        """Execute with chained async operations.

        Args:
            state: Current graph state

        Returns:
            dict: State update with chained results
        """
        self.log("Starting async operation chain")

        # Step 1: Fetch data
        data = await self._fetch_data(state.query)
        self.log(f"Fetched data: {data}")

        # Step 2: Process data
        processed = await self._process_data(data)
        self.log(f"Processed data: {processed}")

        # Step 3: Store result
        stored = await self._store_result(processed)
        self.log(f"Stored result: {stored}")

        return {"messages": [AIMessage(content=f"Chain complete: {stored}")]}

    async def _fetch_data(self, query: str) -> str:
        """Fetch data asynchronously."""
        await asyncio.sleep(0.05)
        return f"data_{query}"

    async def _process_data(self, data: str) -> str:
        """Process data asynchronously."""
        await asyncio.sleep(0.05)
        return data.upper()

    async def _store_result(self, result: str) -> str:
        """Store result asynchronously."""
        await asyncio.sleep(0.05)
        return f"stored_{result}"


class AsyncWithTimeoutNode(AsyncBaseNode):
    """Node that implements timeout for async operations.

    Use this pattern when you need to:
    - Implement operation timeouts
    - Handle slow operations gracefully
    - Provide fallback behavior
    """

    def __init__(self, timeout: float = 1.0, verbose: bool = False):
        """Initialize with timeout.

        Args:
            timeout: Timeout in seconds
            verbose: Enable verbose logging
        """
        super().__init__(verbose=verbose)
        self.timeout = timeout

    async def execute(self, state) -> dict:
        """Execute with timeout.

        Args:
            state: Current graph state

        Returns:
            dict: State update
        """
        self.log(f"Processing with {self.timeout}s timeout")

        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                self._slow_operation(state.query), timeout=self.timeout
            )
            return {"messages": [AIMessage(content=f"Success: {result}")]}

        except asyncio.TimeoutError:
            self.log("Operation timed out", level="warning")
            return {
                "messages": [
                    AIMessage(content=f"Timeout processing: {state.query}")
                ]
            }

    async def _slow_operation(self, query: str) -> str:
        """Simulate slow async operation.

        Args:
            query: Input query

        Returns:
            Operation result
        """
        # This could timeout depending on self.timeout
        await asyncio.sleep(0.5)
        return f"Processed: {query}"


class ConcurrentAPINode(AsyncBaseNode):
    """Node that makes multiple API calls concurrently with error handling.

    Use this pattern when you need to:
    - Call multiple APIs concurrently
    - Handle partial failures gracefully
    - Aggregate results from multiple sources
    """

    async def execute(self, state) -> dict:
        """Execute with concurrent API calls.

        Args:
            state: Current graph state

        Returns:
            dict: State update with aggregated results
        """
        self.log("Making concurrent API calls")

        # Define multiple API calls
        apis = ["api1", "api2", "api3"]
        tasks = [self._call_api(api, state.query) for api in apis]

        # Gather results with error handling
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        successful = []
        failed = []

        for api, result in zip(apis, results):
            if isinstance(result, Exception):
                failed.append(f"{api}: {str(result)}")
                self.log(f"API {api} failed: {result}", level="warning")
            else:
                successful.append(f"{api}: {result}")
                self.log(f"API {api} succeeded: {result}")

        message = "API Results:\n"
        message += "Successful: " + ", ".join(successful) + "\n"
        if failed:
            message += "Failed: " + ", ".join(failed)

        return {"messages": [AIMessage(content=message)]}

    async def _call_api(self, api_name: str, query: str) -> str:
        """Simulate async API call.

        Args:
            api_name: Name of the API
            query: Query parameter

        Returns:
            API response
        """
        await asyncio.sleep(0.1)
        
        # Simulate occasional failures
        if api_name == "api2":
            raise Exception("API temporarily unavailable")
        
        return f"{query}_from_{api_name}"


# Usage example
if __name__ == "__main__":
    from dataclasses import dataclass

    @dataclass(kw_only=True)
    class State:
        query: str
        messages: List = None

        def __post_init__(self):
            if self.messages is None:
                self.messages = []

    async def run_examples():
        """Run all async node examples."""
        
        # Test AsyncAPINode
        print("=== AsyncAPINode ===")
        node = AsyncAPINode()
        state = State(query="test query")
        result = await node(state)
        print(f"Result: {result}\n")

        # Test ParallelProcessingNode
        print("=== ParallelProcessingNode ===")
        node = ParallelProcessingNode(verbose=True)
        state = State(query="hello world from async")
        result = await node(state)
        print(f"Result: {result}\n")

        # Test AsyncDatabaseNode
        print("=== AsyncDatabaseNode ===")
        node = AsyncDatabaseNode(verbose=True)
        state = State(query="Alice")
        result = await node(state)
        print(f"Result: {result}\n")

        # Test AsyncChainNode
        print("=== AsyncChainNode ===")
        node = AsyncChainNode(verbose=True)
        state = State(query="test")
        result = await node(state)
        print(f"Result: {result}\n")

        # Test AsyncWithTimeoutNode
        print("=== AsyncWithTimeoutNode ===")
        node = AsyncWithTimeoutNode(timeout=1.0, verbose=True)
        state = State(query="timeout test")
        result = await node(state)
        print(f"Result: {result}\n")

        # Test ConcurrentAPINode
        print("=== ConcurrentAPINode ===")
        node = ConcurrentAPINode(verbose=True)
        state = State(query="concurrent")
        result = await node(state)
        print(f"Result: {result}\n")

    # Run examples
    asyncio.run(run_examples())
