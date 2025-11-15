#!/usr/bin/env python3
"""Generate test boilerplate for LangGraph casts.

Usage:
    python generate_tests.py --node ProcessNode --cast my_agent
    python generate_tests.py --graph MyAgentGraph --cast my_agent
    python generate_tests.py --all --cast my_agent
"""

import argparse
import os
from pathlib import Path


NODE_TEST_TEMPLATE = '''"""Tests for {node_name}."""

import pytest
from casts.{cast_name}.nodes import {node_name}
from casts.{cast_name}.state import {state_class}


class Test{node_name}:
    """Tests for {node_name}."""

    @pytest.fixture
    def node(self, mock_llm):
        """Provide {node_name} instance."""
        # TODO: Add dependencies as needed
        return {node_name}()

    @pytest.fixture
    def sample_state(self):
        """Provide sample state for testing."""
        return {{
            "messages": [],
            "task": "test task",
            # TODO: Add other required state fields
        }}

    def test_execute_basic(self, node, sample_state):
        """Test basic execution."""
        result = node.execute(sample_state)

        assert isinstance(result, dict)
        # TODO: Add specific assertions

    def test_execute_with_valid_input(self, node, sample_state):
        """Test execution with valid input."""
        # TODO: Implement test
        pass

    def test_execute_handles_errors(self, node):
        """Test error handling."""
        invalid_state = {{}}  # Invalid state

        result = node.execute(invalid_state)

        # TODO: Add error assertions

    @pytest.mark.parametrize("input_data,expected", [
        # TODO: Add test cases
        ("test1", "expected1"),
        ("test2", "expected2"),
    ])
    def test_execute_parametrized(self, node, sample_state, input_data, expected):
        """Test with multiple inputs."""
        sample_state["data"] = input_data
        result = node.execute(sample_state)
        # TODO: Add assertions
'''


GRAPH_TEST_TEMPLATE = '''"""Tests for {graph_name}."""

import pytest
from langgraph.checkpoint.memory import MemorySaver
from casts.{cast_name}.graph import {graph_name}
from casts.{cast_name}.state import {state_class}


class Test{graph_name}:
    """Integration tests for {graph_name}."""

    @pytest.fixture
    def graph(self, mock_llm):
        """Provide test graph."""
        # TODO: Pass required dependencies
        return {graph_name}(
            checkpointer=MemorySaver()
        ).build()

    @pytest.fixture
    def test_config(self):
        """Provide test config with thread_id."""
        return {{"configurable": {{"thread_id": "test-123"}}}}

    def test_graph_execution_basic(self, graph):
        """Test basic graph execution."""
        result = graph.invoke({{
            "messages": [],
            "task": "test task"
        }})

        assert result is not None
        # TODO: Add specific assertions

    def test_graph_with_config(self, graph, test_config):
        """Test graph execution with config."""
        result = graph.invoke(
            {{"messages": [], "task": "test"}},
            test_config
        )

        assert result is not None
        # TODO: Verify state persistence

    def test_graph_routing(self, graph):
        """Test conditional edge routing."""
        # Test different routing paths
        # TODO: Implement routing tests
        pass

    def test_graph_state_flow(self, graph, test_config):
        """Test state flow through graph."""
        # First invocation
        result1 = graph.invoke(
            {{"messages": [], "count": 1}},
            test_config
        )

        # Second invocation - test accumulation
        result2 = graph.invoke(
            {{"count": 1}},
            test_config
        )

        # TODO: Add assertions for state accumulation

    @pytest.mark.slow
    def test_graph_complete_workflow(self, graph):
        """Test complete multi-step workflow."""
        result = graph.invoke({{
            "messages": [],
            "task": "complex task"
        }})

        # TODO: Verify workflow completion
        assert result["status"] == "completed"
'''


CONFTEST_TEMPLATE = '''"""Test fixtures for {cast_name}."""

import pytest
from langchain_core.messages import AIMessage


class MockLLM:
    """Mock LLM for testing."""

    def invoke(self, messages):
        """Return mock AI response."""
        return AIMessage(content="Mock response")

    def bind_tools(self, tools):
        """Mock tool binding."""
        return self


@pytest.fixture
def mock_llm():
    """Provide mock LLM."""
    return MockLLM()


@pytest.fixture
def test_config():
    """Provide test config with thread_id."""
    return {{"configurable": {{"thread_id": "test-123"}}}}


# TODO: Add cast-specific fixtures here
'''


def generate_node_test(node_name: str, cast_name: str, output_dir: Path):
    """Generate node test file."""
    # Infer state class name from cast name
    state_class = f"{cast_name.title().replace('_', '')}State"

    content = NODE_TEST_TEMPLATE.format(
        node_name=node_name,
        cast_name=cast_name,
        state_class=state_class
    )

    test_file = output_dir / f"test_{node_name.lower()}.py"

    if test_file.exists():
        print(f"⚠️  {test_file} already exists. Skipping.")
        return

    test_file.write_text(content)
    print(f"✓ Generated {test_file}")


def generate_graph_test(graph_name: str, cast_name: str, output_dir: Path):
    """Generate graph test file."""
    state_class = f"{cast_name.title().replace('_', '')}State"

    content = GRAPH_TEST_TEMPLATE.format(
        graph_name=graph_name,
        cast_name=cast_name,
        state_class=state_class
    )

    test_file = output_dir / "test_graph.py"

    if test_file.exists():
        print(f"⚠️  {test_file} already exists. Skipping.")
        return

    test_file.write_text(content)
    print(f"✓ Generated {test_file}")


def generate_conftest(cast_name: str, output_dir: Path):
    """Generate conftest.py file."""
    content = CONFTEST_TEMPLATE.format(cast_name=cast_name)

    conftest_file = output_dir / "conftest.py"

    if conftest_file.exists():
        print(f"⚠️  {conftest_file} already exists. Skipping.")
        return

    conftest_file.write_text(content)
    print(f"✓ Generated {conftest_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate test boilerplate for LangGraph casts"
    )
    parser.add_argument(
        "--node",
        help="Node class name to generate tests for"
    )
    parser.add_argument(
        "--graph",
        help="Graph class name to generate tests for"
    )
    parser.add_argument(
        "--cast",
        required=True,
        help="Cast name (e.g., my_agent)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate all test files (conftest, test_nodes, test_graph)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory (default: casts/{cast}/tests)"
    )

    args = parser.parse_args()

    # Determine output directory
    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = Path(f"casts/{args.cast}/tests")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create __init__.py
    (output_dir / "__init__.py").touch()

    if args.all:
        # Generate all test files
        generate_conftest(args.cast, output_dir)
        generate_node_test("ProcessNode", args.cast, output_dir)
        generate_graph_test(f"{args.cast.title().replace('_', '')}Graph", args.cast, output_dir)
        print(f"\n✓ Generated complete test suite in {output_dir}")
    else:
        # Generate specific files
        if args.node:
            generate_node_test(args.node, args.cast, output_dir)

        if args.graph:
            generate_graph_test(args.graph, args.cast, output_dir)

        if not args.node and not args.graph:
            # Just generate conftest
            generate_conftest(args.cast, output_dir)


if __name__ == "__main__":
    main()
