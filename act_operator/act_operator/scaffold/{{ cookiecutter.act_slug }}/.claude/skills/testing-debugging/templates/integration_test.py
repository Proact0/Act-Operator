"""Integration test template for testing complete graphs.

This template demonstrates how to test a complete graph end-to-end.
Copy and modify this template for testing your graph.

Usage:
    1. Copy this file to tests/integration_tests/test_your_graph.py
    2. Replace your_cast with your actual cast name
    3. Update test inputs and assertions
    4. Run: pytest tests/integration_tests/test_your_graph.py
"""

from dataclasses import dataclass
from typing import Annotated, List

import pytest
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

# Import your graph
# from casts.your_cast.graph import your_cast_graph


# Define test state (should match your graph state)
@dataclass(kw_only=True)
class TestState:
    """Test state matching your graph state."""

    query: str
    messages: Annotated[list[AnyMessage], add_messages]


# Mock graph for template demonstration
class MockGraph:
    """Replace with actual graph import."""

    def invoke(self, state):
        return {"query": state["query"], "messages": []}

    def stream(self, state):
        yield state


# Replace with: your_cast_graph = MockGraph()
your_cast_graph = MockGraph()


class TestGraphIntegration:
    """Integration tests for the complete graph.

    These tests verify end-to-end behavior of the graph.
    """

    @pytest.fixture
    def graph(self):
        """Fixture that provides the graph.

        Returns:
            Compiled graph instance
        """
        # Use the actual graph
        return your_cast_graph.build() if hasattr(your_cast_graph, "build") else your_cast_graph

    def test_graph_basic_execution(self, graph):
        """Test basic graph execution.

        Args:
            graph: Graph fixture
        """
        # Prepare input
        initial_state = {"query": "test query", "messages": []}

        # Execute graph
        result = graph.invoke(initial_state)

        # Assert basic structure
        assert isinstance(result, dict), "Graph should return dict"
        assert "query" in result, "Result should contain query"
        assert "messages" in result, "Result should contain messages"

        # Assert graph completed successfully
        assert len(result.get("messages", [])) > 0, "Graph should produce messages"

    def test_graph_with_various_inputs(self, graph):
        """Test graph with different input patterns.

        Args:
            graph: Graph fixture
        """
        test_cases = [
            {"query": "simple query", "expected": True},
            {"query": "complex query with many words", "expected": True},
            {"query": "", "expected": False},  # Should handle gracefully
        ]

        for case in test_cases:
            initial_state = {"query": case["query"], "messages": []}
            result = graph.invoke(initial_state)

            if case["expected"]:
                assert "messages" in result
                assert len(result["messages"]) > 0
            else:
                # Verify error handling
                assert "messages" in result or "error" in result

    def test_graph_state_persistence(self, graph):
        """Test that graph maintains state correctly.

        Args:
            graph: Graph fixture
        """
        initial_state = {"query": "test", "messages": []}

        result = graph.invoke(initial_state)

        # Verify input is preserved
        assert result["query"] == initial_state["query"]

        # Verify state was updated
        assert "messages" in result

    def test_graph_idempotency(self, graph):
        """Test that running graph multiple times with same input produces consistent results.

        Args:
            graph: Graph fixture
        """
        initial_state = {"query": "idempotency test", "messages": []}

        # Run twice
        result1 = graph.invoke(initial_state)
        result2 = graph.invoke(initial_state)

        # Compare results
        # Note: Exact comparison depends on whether your graph is deterministic
        assert result1.keys() == result2.keys()
        assert result1["query"] == result2["query"]

    @pytest.mark.slow
    def test_graph_performance(self, graph, benchmark):
        """Test graph performance.

        Args:
            graph: Graph fixture
            benchmark: pytest-benchmark fixture
        """
        initial_state = {"query": "performance test", "messages": []}

        # Benchmark graph execution
        result = benchmark(graph.invoke, initial_state)

        assert isinstance(result, dict)
        assert "messages" in result


class TestGraphStreaming:
    """Tests for graph streaming behavior.

    These tests verify that streaming works correctly.
    """

    @pytest.fixture
    def graph(self):
        """Fixture that provides the graph."""
        return your_cast_graph.build() if hasattr(your_cast_graph, "build") else your_cast_graph

    def test_graph_streaming_basic(self, graph):
        """Test basic streaming functionality.

        Args:
            graph: Graph fixture
        """
        initial_state = {"query": "streaming test", "messages": []}

        # Collect stream chunks
        chunks = []
        for chunk in graph.stream(initial_state):
            chunks.append(chunk)

        # Verify we got chunks
        assert len(chunks) > 0, "Should produce at least one chunk"

        # Verify chunks are dicts
        for chunk in chunks:
            assert isinstance(chunk, dict), "Each chunk should be a dict"

    def test_graph_streaming_completeness(self, graph):
        """Test that streaming produces complete result.

        Args:
            graph: Graph fixture
        """
        initial_state = {"query": "completeness test", "messages": []}

        # Get streaming result
        final_chunk = None
        for chunk in graph.stream(initial_state):
            final_chunk = chunk

        # Get non-streaming result
        invoke_result = graph.invoke(initial_state)

        # Compare final chunk with invoke result
        # Note: Exact comparison depends on your graph's streaming behavior
        assert final_chunk is not None
        assert final_chunk.keys() == invoke_result.keys()


class TestGraphEdgeCases:
    """Tests for edge cases and error scenarios.

    These tests verify the graph handles unusual inputs correctly.
    """

    @pytest.fixture
    def graph(self):
        """Fixture that provides the graph."""
        return your_cast_graph.build() if hasattr(your_cast_graph, "build") else your_cast_graph

    def test_graph_with_empty_state(self, graph):
        """Test graph with minimal/empty state.

        Args:
            graph: Graph fixture
        """
        # Test with only required fields
        initial_state = {"query": "", "messages": []}

        # Should handle gracefully or raise clear error
        try:
            result = graph.invoke(initial_state)
            assert isinstance(result, dict)
        except Exception as e:
            # If it raises, error should be clear
            assert str(e), "Error should have message"

    def test_graph_with_large_input(self, graph):
        """Test graph with large input.

        Args:
            graph: Graph fixture
        """
        # Create large query
        large_query = "word " * 1000  # 1000 words

        initial_state = {"query": large_query, "messages": []}

        # Should handle large input
        result = graph.invoke(initial_state)
        assert isinstance(result, dict)

    def test_graph_with_special_characters(self, graph):
        """Test graph with special characters in input.

        Args:
            graph: Graph fixture
        """
        special_queries = [
            "query with émojis 🎉",
            "query with\nnewlines",
            "query with\ttabs",
            "query with 'quotes'",
            "query with \"double quotes\"",
        ]

        for query in special_queries:
            initial_state = {"query": query, "messages": []}
            result = graph.invoke(initial_state)
            assert isinstance(result, dict)
            assert "messages" in result


class TestGraphConfiguration:
    """Tests for graph configuration options.

    These tests verify that configuration parameters work correctly.
    """

    @pytest.fixture
    def graph(self):
        """Fixture that provides the graph."""
        return your_cast_graph.build() if hasattr(your_cast_graph, "build") else your_cast_graph

    def test_graph_with_config(self, graph):
        """Test graph execution with configuration.

        Args:
            graph: Graph fixture
        """
        initial_state = {"query": "config test", "messages": []}

        config = {"configurable": {"thread_id": "test-thread-123"}}

        # Execute with config
        result = graph.invoke(initial_state, config=config)

        assert isinstance(result, dict)
        assert "messages" in result

    def test_graph_with_tags(self, graph):
        """Test graph execution with tags.

        Args:
            graph: Graph fixture
        """
        initial_state = {"query": "tags test", "messages": []}

        config = {"tags": ["test", "integration"]}

        # Execute with tags
        result = graph.invoke(initial_state, config=config)

        assert isinstance(result, dict)


class TestGraphRealWorld:
    """Real-world scenario tests.

    These tests simulate actual usage patterns.
    """

    @pytest.fixture
    def graph(self):
        """Fixture that provides the graph."""
        return your_cast_graph.build() if hasattr(your_cast_graph, "build") else your_cast_graph

    def test_typical_user_query(self, graph):
        """Test with typical user query.

        Args:
            graph: Graph fixture
        """
        initial_state = {
            "query": "What is the weather like today?",
            "messages": [],
        }

        result = graph.invoke(initial_state)

        # Verify reasonable response
        assert "messages" in result
        assert len(result["messages"]) > 0

    def test_multi_turn_conversation(self, graph):
        """Test multi-turn conversation flow.

        Args:
            graph: Graph fixture
        """
        # First turn
        state1 = {"query": "Hello, I need help", "messages": []}
        result1 = graph.invoke(state1)

        # Second turn (with context from first)
        state2 = {
            "query": "Can you elaborate?",
            "messages": result1.get("messages", []),
        }
        result2 = graph.invoke(state2)

        # Verify conversation continuity
        assert len(result2["messages"]) >= len(result1["messages"])

    @pytest.mark.parametrize(
        "scenario",
        [
            "simple_query",
            "complex_analysis",
            "error_recovery",
        ],
    )
    def test_common_scenarios(self, graph, scenario):
        """Test common usage scenarios.

        Args:
            graph: Graph fixture
            scenario: Scenario name
        """
        scenarios = {
            "simple_query": {"query": "Simple question", "messages": []},
            "complex_analysis": {
                "query": "Analyze this complex situation with multiple factors",
                "messages": [],
            },
            "error_recovery": {"query": "", "messages": []},  # Empty query
        }

        initial_state = scenarios[scenario]
        result = graph.invoke(initial_state)

        # All scenarios should return valid dict
        assert isinstance(result, dict)


if __name__ == "__main__":
    # Run tests with: python -m pytest tests/integration_tests/test_your_graph.py
    pytest.main([__file__, "-v", "-s"])
