#!/usr/bin/env python3
"""Generate test file for graph.py."""

import sys
from pathlib import Path


def generate_graph_tests(cast_name: str, output_file: Path):
    """Generate graph test template."""
    content = f'''"""Tests for {cast_name} graph."""

import pytest
from langgraph.checkpoint.memory import MemorySaver
from casts.{cast_name}.graph import {cast_name.title().replace("_", "")}Graph


class Test{cast_name.title().replace("_", "")}Graph:
    """Test suite for {cast_name} graph."""

    @pytest.fixture
    def graph(self):
        """Provides compiled graph."""
        graph_builder = {cast_name.title().replace("_", "")}Graph()
        return graph_builder.build()

    @pytest.fixture
    def graph_with_memory(self):
        """Provides graph with checkpointer."""
        graph_builder = {cast_name.title().replace("_", "")}Graph()
        checkpointer = MemorySaver()
        # Adjust based on your graph's build() signature
        return graph_builder.build(checkpointer=checkpointer)

    def test_graph_compiles(self, graph):
        """Graph should compile without errors."""
        assert graph is not None
        assert hasattr(graph, "invoke")
        assert hasattr(graph, "stream")

    def test_graph_invoke_basic(self, graph):
        """Test basic graph invocation."""
        initial_state = {{"input": "test"}}

        result = graph.invoke(initial_state)

        assert result is not None
        assert isinstance(result, dict)
        # TODO: Add assertions for expected output fields

    def test_graph_with_config(self, graph_with_memory):
        """Test graph with thread configuration."""
        config = {{"configurable": {{"thread_id": "test-123"}}}}
        initial_state = {{"input": "test"}}

        result = graph_with_memory.invoke(initial_state, config=config)

        assert result is not None

    def test_graph_streaming(self, graph):
        """Test graph streaming."""
        initial_state = {{"input": "test"}}

        chunks = list(graph.stream(initial_state, stream_mode="updates"))

        assert len(chunks) > 0
        # Each chunk should be a dict
        for chunk in chunks:
            assert isinstance(chunk, dict)

    def test_graph_state_updates(self, graph):
        """Test state updates through graph."""
        initial_state = {{"input": "test", "step": 0}}

        final_state = graph.invoke(initial_state)

        # TODO: Verify expected state transformations
        assert "step" in final_state or "result" in final_state

    # TODO: Add tests for specific routing conditions
    # TODO: Add tests for error handling
    # TODO: Add tests for edge cases


class TestGraphNodes:
    """Test individual nodes in the graph."""

    @pytest.fixture
    def graph(self):
        graph_builder = {cast_name.title().replace("_", "")}Graph()
        return graph_builder.build()

    # TODO: Add tests for individual nodes accessed via graph.nodes["node_name"]


class TestGraphIntegration:
    """Integration tests for complete workflows."""

    @pytest.fixture
    def graph_with_memory(self):
        graph_builder = {cast_name.title().replace("_", "")}Graph()
        checkpointer = MemorySaver()
        return graph_builder.build(checkpointer=checkpointer)

    def test_complete_workflow(self, graph_with_memory):
        """Test end-to-end workflow."""
        config = {{"configurable": {{"thread_id": "integration-test"}}}}

        # TODO: Implement complete workflow test
        result = graph_with_memory.invoke({{"input": "start"}}, config=config)

        assert result is not None
'''

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(content)


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_graph_tests.py <cast_name> [output_file]")
        print("\nExample:")
        print("  python generate_graph_tests.py my_cast")
        print("  python generate_graph_tests.py my_cast casts/my_cast/tests/test_graph.py")
        sys.exit(1)

    cast_name = sys.argv[1]

    if len(sys.argv) >= 3:
        output_file = Path(sys.argv[2])
    else:
        output_file = Path(f"casts/{cast_name}/tests/test_graph.py")

    generate_graph_tests(cast_name, output_file)

    print(f"Generated graph tests for {cast_name}")
    print(f"Test file: {output_file}")


if __name__ == "__main__":
    main()
