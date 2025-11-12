"""Unit test template for testing individual nodes.

This template demonstrates how to test a single node in isolation.
Copy and modify this template for each node you implement.

Usage:
    1. Copy this file to tests/unit_tests/test_your_node.py
    2. Replace YourNode with your actual node class name
    3. Update the test state and assertions
    4. Run: pytest tests/unit_tests/test_your_node.py
"""

from dataclasses import dataclass
from typing import Annotated, List

import pytest
from langchain_core.messages import AIMessage, AnyMessage
from langgraph.graph.message import add_messages

# Import your node class
# from casts.your_cast.modules.nodes import YourNode


# Define test state (should match your actual state)
@dataclass(kw_only=True)
class TestState:
    """Test state matching your graph state."""

    query: str
    messages: Annotated[list[AnyMessage], add_messages]
    # Add other fields as needed


# Mock node for template demonstration
class YourNode:
    """Replace this with your actual node import."""

    def __call__(self, state):
        return {"messages": [AIMessage(content=f"Processed: {state.query}")]}


class TestYourNode:
    """Test suite for YourNode.

    This class contains all tests for a single node.
    Group related tests together using methods.
    """

    @pytest.fixture
    def node(self):
        """Fixture that provides a node instance.

        Returns:
            Configured node instance
        """
        return YourNode()

    @pytest.fixture
    def sample_state(self):
        """Fixture that provides sample state.

        Returns:
            Sample state for testing
        """
        return TestState(query="test query", messages=[])

    def test_node_basic_execution(self, node, sample_state):
        """Test basic node execution.

        Args:
            node: Node fixture
            sample_state: State fixture
        """
        # Execute node
        result = node(sample_state)

        # Assert result structure
        assert isinstance(result, dict), "Node should return a dict"
        assert "messages" in result, "Result should contain 'messages' key"

        # Assert result content
        messages = result["messages"]
        assert len(messages) > 0, "Should return at least one message"
        assert isinstance(messages[0], AIMessage), "Should return AIMessage"

    def test_node_with_empty_query(self, node):
        """Test node behavior with empty query.

        Args:
            node: Node fixture
        """
        state = TestState(query="", messages=[])
        result = node(state)

        # Verify node handles empty input gracefully
        assert "messages" in result
        # Add specific assertions for your node's behavior

    def test_node_with_long_query(self, node):
        """Test node behavior with long query.

        Args:
            node: Node fixture
        """
        long_query = "word " * 100  # 100 words
        state = TestState(query=long_query, messages=[])
        result = node(state)

        # Verify node handles long input
        assert "messages" in result
        # Add specific assertions

    def test_node_preserves_existing_messages(self, node):
        """Test that node preserves existing messages in state.

        Args:
            node: Node fixture
        """
        existing_message = AIMessage(content="Existing message")
        state = TestState(query="new query", messages=[existing_message])

        result = node(state)

        # Verify messages are added, not replaced
        assert "messages" in result
        # Note: Actual behavior depends on your reducer

    def test_node_return_type(self, node, sample_state):
        """Test that node returns correct type.

        Args:
            node: Node fixture
            sample_state: State fixture
        """
        result = node(sample_state)

        # Verify return type
        assert isinstance(result, dict), "Must return dict"

        # Verify all keys are state fields
        # (This helps catch typos in state updates)
        valid_keys = {"query", "messages"}  # Update with your state fields
        for key in result.keys():
            assert key in valid_keys, f"Unknown state key: {key}"

    def test_node_idempotency(self, node, sample_state):
        """Test that running node multiple times is safe.

        Args:
            node: Node fixture
            sample_state: State fixture
        """
        # Run node twice
        result1 = node(sample_state)
        result2 = node(sample_state)

        # Verify consistent behavior
        # (Adjust based on whether your node should be idempotent)
        assert result1.keys() == result2.keys()

    @pytest.mark.parametrize(
        "query,expected_content",
        [
            ("hello", "hello"),
            ("HELLO", "HELLO"),
            ("123", "123"),
        ],
    )
    def test_node_with_various_inputs(self, node, query, expected_content):
        """Test node with various input patterns.

        Args:
            node: Node fixture
            query: Input query
            expected_content: Expected content in response
        """
        state = TestState(query=query, messages=[])
        result = node(state)

        # Verify expected content appears in result
        messages = result.get("messages", [])
        assert len(messages) > 0
        # Add specific assertions based on your node's behavior


# Async node testing example
class TestYourAsyncNode:
    """Test suite for async nodes.

    Use this pattern for testing AsyncBaseNode implementations.
    """

    @pytest.fixture
    def async_node(self):
        """Fixture that provides an async node instance.

        Returns:
            Configured async node instance
        """
        # from casts.your_cast.modules.nodes import YourAsyncNode
        # return YourAsyncNode()
        pass

    @pytest.mark.asyncio
    async def test_async_node_execution(self, async_node, sample_state):
        """Test async node execution.

        Args:
            async_node: Async node fixture
            sample_state: State fixture
        """
        # Execute async node
        # result = await async_node(sample_state)

        # Assert result
        # assert isinstance(result, dict)
        # assert "messages" in result
        pass


# Error handling tests
class TestYourNodeErrorHandling:
    """Test error handling in YourNode.

    These tests verify the node handles errors gracefully.
    """

    @pytest.fixture
    def node(self):
        """Fixture that provides a node instance."""
        return YourNode()

    def test_node_with_invalid_state(self, node):
        """Test node behavior with invalid state.

        Args:
            node: Node fixture
        """
        # Test with missing required fields
        # This should either raise a clear error or handle gracefully
        with pytest.raises(Exception):
            # Invalid state - missing required fields
            node(None)

    def test_node_with_malformed_input(self, node):
        """Test node with malformed input.

        Args:
            node: Node fixture
        """
        # Test how node handles unexpected input types
        state = TestState(query=None, messages=[])  # None instead of string

        # Depending on your implementation, this might:
        # 1. Raise an exception (use pytest.raises)
        # 2. Return an error message
        # 3. Handle gracefully with default behavior

        # Example: expecting graceful handling
        result = node(state)
        assert isinstance(result, dict)


# Performance tests (optional)
class TestYourNodePerformance:
    """Performance tests for YourNode.

    These tests verify the node performs adequately.
    """

    @pytest.fixture
    def node(self):
        """Fixture that provides a node instance."""
        return YourNode()

    @pytest.mark.slow  # Mark as slow test
    def test_node_performance(self, node, benchmark):
        """Test node performance with benchmark.

        Args:
            node: Node fixture
            benchmark: pytest-benchmark fixture
        """
        state = TestState(query="performance test", messages=[])

        # Benchmark the node execution
        result = benchmark(node, state)

        assert isinstance(result, dict)

    def test_node_memory_usage(self, node):
        """Test that node doesn't leak memory.

        Args:
            node: Node fixture
        """
        # Run node many times and verify memory doesn't grow unbounded
        for _ in range(100):
            state = TestState(query="memory test", messages=[])
            result = node(state)
            assert isinstance(result, dict)


if __name__ == "__main__":
    # Run tests with: python -m pytest tests/unit_tests/test_your_node.py
    pytest.main([__file__, "-v"])
