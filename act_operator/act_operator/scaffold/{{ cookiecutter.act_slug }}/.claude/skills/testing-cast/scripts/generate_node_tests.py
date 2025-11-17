#!/usr/bin/env python3
"""Generate test file for nodes.py based on node classes."""

import ast
import sys
from pathlib import Path
from typing import List


class NodeTestGenerator:
    """Generates pytest tests for node classes."""

    def __init__(self, nodes_file: Path, output_file: Path):
        self.nodes_file = nodes_file
        self.output_file = output_file
        self.node_classes = []

    def parse_nodes(self):
        """Extract node class names from nodes.py."""
        with open(self.nodes_file) as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if inherits from BaseNode or AsyncBaseNode
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id in ("BaseNode", "AsyncBaseNode"):
                        is_async = base.id == "AsyncBaseNode"
                        self.node_classes.append((node.name, is_async))

    def generate_tests(self):
        """Generate test file content."""
        cast_name = self.nodes_file.parent.name

        content = f'''"""Tests for {cast_name} nodes."""

import pytest
from casts.{cast_name}.nodes import (
    {", ".join(cls[0] for cls in self.node_classes)}
)


'''

        for class_name, is_async in self.node_classes:
            content += self.generate_test_class(class_name, is_async)

        return content

    def generate_test_class(self, class_name: str, is_async: bool):
        """Generate test class for a node."""
        decorator = "@pytest.mark.asyncio\n    " if is_async else ""
        async_keyword = "async " if is_async else ""
        await_keyword = "await " if is_async else ""

        return f'''class Test{class_name}:
    """Test suite for {class_name}."""

    {decorator}@pytest.fixture
    {async_keyword}def node(self):
        """Provides {class_name} instance."""
        return {class_name}()

    {decorator}def test_execute_basic(self, node):
        """Test basic execution."""
        state = {{"input": "test"}}

        result = {await_keyword}node.execute(state)

        assert result is not None
        assert isinstance(result, dict)

    {decorator}def test_execute_with_empty_state(self, node):
        """Test execution with empty state."""
        state = {{}}

        result = {await_keyword}node.execute(state)

        # Should handle gracefully
        assert result is not None

    # TODO: Add more specific tests for {class_name}


'''

    def run(self):
        """Execute test generation."""
        self.parse_nodes()

        if not self.node_classes:
            print(f"No node classes found in {self.nodes_file}")
            return False

        content = self.generate_tests()

        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.output_file.write_text(content)

        print(f"Generated tests for {len(self.node_classes)} nodes:")
        for name, is_async in self.node_classes:
            async_label = " (async)" if is_async else ""
            print(f"  - {name}{async_label}")
        print(f"\nTest file: {self.output_file}")

        return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_node_tests.py <path_to_nodes.py> [output_file]")
        print("\nExample:")
        print("  python generate_node_tests.py casts/my_cast/nodes.py")
        print("  python generate_node_tests.py casts/my_cast/nodes.py casts/my_cast/tests/test_nodes.py")
        sys.exit(1)

    nodes_file = Path(sys.argv[1])

    if not nodes_file.exists():
        print(f"Error: {nodes_file} not found")
        sys.exit(1)

    # Default output location
    if len(sys.argv) >= 3:
        output_file = Path(sys.argv[2])
    else:
        cast_dir = nodes_file.parent
        output_file = cast_dir / "tests" / "test_nodes.py"

    generator = NodeTestGenerator(nodes_file, output_file)
    success = generator.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
