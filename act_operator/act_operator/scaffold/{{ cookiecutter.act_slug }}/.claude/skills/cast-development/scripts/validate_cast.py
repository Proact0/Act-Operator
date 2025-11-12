#!/usr/bin/env python3
"""Validate Cast structure and implementation.

This script validates that a Cast is properly structured and can be built successfully.
It checks for required files, validates state schemas, and tests graph compilation.

Usage:
    python validate_cast.py <cast_name>
    python validate_cast.py my_cast --verbose
"""

import argparse
import importlib.util
import sys
from pathlib import Path
from typing import Any, Optional


class Colors:
    """ANSI color codes for terminal output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


class CastValidator:
    """Validates Cast structure and implementation."""

    def __init__(self, cast_name: str, verbose: bool = False):
        """Initialize the validator.

        Args:
            cast_name: Name of the cast to validate (e.g., 'my_cast')
            verbose: Enable verbose output
        """
        self.cast_name = cast_name
        self.verbose = verbose
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.base_path = Path("casts") / cast_name

    def log(self, message: str, level: str = "info") -> None:
        """Log a message based on verbosity settings.

        Args:
            message: Message to log
            level: Log level (info, success, warning, error)
        """
        if level == "error":
            print(f"{Colors.RED}✗{Colors.END} {message}")
        elif level == "warning":
            print(f"{Colors.YELLOW}⚠{Colors.END} {message}")
        elif level == "success":
            print(f"{Colors.GREEN}✓{Colors.END} {message}")
        elif level == "info" and self.verbose:
            print(f"{Colors.BLUE}ℹ{Colors.END} {message}")

    def validate_file_exists(self, file_path: Path, description: str) -> bool:
        """Validate that a required file exists.

        Args:
            file_path: Path to the file
            description: Description of the file for error messages

        Returns:
            True if file exists, False otherwise
        """
        if file_path.exists():
            self.log(f"Found {description}: {file_path}", "success")
            return True
        else:
            self.errors.append(f"Missing {description}: {file_path}")
            self.log(f"Missing {description}: {file_path}", "error")
            return False

    def validate_structure(self) -> bool:
        """Validate Cast directory structure.

        Returns:
            True if structure is valid, False otherwise
        """
        self.log("\n=== Validating Cast Structure ===", "info")

        # Check base directory
        if not self.base_path.exists():
            self.errors.append(f"Cast directory not found: {self.base_path}")
            self.log(f"Cast directory not found: {self.base_path}", "error")
            return False

        self.log(f"Found cast directory: {self.base_path}", "success")

        # Check required files
        required_files = {
            self.base_path / "graph.py": "Graph definition",
            self.base_path / "modules" / "nodes.py": "Node implementations",
            self.base_path / "modules" / "state.py": "State definition",
            self.base_path / "__init__.py": "Cast __init__.py",
            self.base_path / "modules" / "__init__.py": "Modules __init__.py",
        }

        all_exist = True
        for file_path, description in required_files.items():
            if not self.validate_file_exists(file_path, description):
                all_exist = False

        return all_exist

    def load_module(self, module_path: str) -> Optional[Any]:
        """Dynamically load a Python module.

        Args:
            module_path: Python module path (e.g., 'casts.my_cast.graph')

        Returns:
            Loaded module or None if loading fails
        """
        try:
            module = importlib.import_module(module_path)
            self.log(f"Successfully loaded module: {module_path}", "success")
            return module
        except Exception as e:
            self.errors.append(f"Failed to load module {module_path}: {str(e)}")
            self.log(f"Failed to load module {module_path}: {str(e)}", "error")
            return None

    def validate_state(self) -> bool:
        """Validate state definition.

        Returns:
            True if state is valid, False otherwise
        """
        self.log("\n=== Validating State Definition ===", "info")

        state_module = self.load_module(f"casts.{self.cast_name}.modules.state")
        if not state_module:
            return False

        # Check for required state classes
        required_classes = ["State", "InputState", "OutputState"]
        all_found = True

        for class_name in required_classes:
            if hasattr(state_module, class_name):
                state_class = getattr(state_module, class_name)
                self.log(f"Found {class_name} class", "success")

                # Validate it's a dataclass
                if not hasattr(state_class, "__dataclass_fields__"):
                    self.warnings.append(
                        f"{class_name} is not a dataclass - consider using @dataclass decorator"
                    )
                    self.log(
                        f"{class_name} is not a dataclass - consider using @dataclass decorator",
                        "warning",
                    )
                else:
                    self.log(f"{class_name} is properly defined as a dataclass", "info")
            else:
                self.errors.append(f"Missing required class: {class_name}")
                self.log(f"Missing required class: {class_name}", "error")
                all_found = False

        return all_found

    def validate_nodes(self) -> bool:
        """Validate node implementations.

        Returns:
            True if nodes are valid, False otherwise
        """
        self.log("\n=== Validating Node Implementations ===", "info")

        nodes_module = self.load_module(f"casts.{self.cast_name}.modules.nodes")
        if not nodes_module:
            return False

        # Find all node classes (look for classes with 'execute' method)
        node_classes = []
        for name in dir(nodes_module):
            obj = getattr(nodes_module, name)
            if (
                isinstance(obj, type)
                and hasattr(obj, "execute")
                and name not in ["BaseNode", "AsyncBaseNode"]
            ):
                node_classes.append((name, obj))

        if not node_classes:
            self.warnings.append("No node classes found - did you implement any nodes?")
            self.log("No node classes found - did you implement any nodes?", "warning")
            return True

        self.log(f"Found {len(node_classes)} node class(es)", "success")

        # Validate each node
        for node_name, node_class in node_classes:
            self.log(f"Validating node: {node_name}", "info")

            # Check for execute method
            if not hasattr(node_class, "execute"):
                self.errors.append(f"Node {node_name} missing execute() method")
                self.log(f"Node {node_name} missing execute() method", "error")
                continue

            # Check if it's async or sync
            import inspect

            if inspect.iscoroutinefunction(node_class.execute):
                self.log(f"{node_name} is an async node", "info")
            else:
                self.log(f"{node_name} is a sync node", "info")

        return len(self.errors) == 0

    def validate_graph(self) -> bool:
        """Validate graph definition and compilation.

        Returns:
            True if graph is valid, False otherwise
        """
        self.log("\n=== Validating Graph Definition ===", "info")

        graph_module = self.load_module(f"casts.{self.cast_name}.graph")
        if not graph_module:
            return False

        # Find graph instance (look for objects with 'build' method)
        graph_instance = None
        for name in dir(graph_module):
            obj = getattr(graph_module, name)
            if hasattr(obj, "build") and not isinstance(obj, type):
                graph_instance = obj
                self.log(f"Found graph instance: {name}", "success")
                break

        if not graph_instance:
            self.errors.append("No graph instance found with build() method")
            self.log("No graph instance found with build() method", "error")
            return False

        # Try to build the graph
        try:
            compiled_graph = graph_instance.build()
            self.log("Graph compiled successfully", "success")

            # Validate graph has nodes
            if hasattr(compiled_graph, "nodes"):
                node_count = len(compiled_graph.nodes)
                self.log(f"Graph has {node_count} node(s)", "info")
                if node_count == 0:
                    self.warnings.append("Graph has no nodes - did you add any?")
                    self.log("Graph has no nodes - did you add any?", "warning")

            return True

        except Exception as e:
            self.errors.append(f"Failed to build graph: {str(e)}")
            self.log(f"Failed to build graph: {str(e)}", "error")
            return False

    def validate(self) -> bool:
        """Run all validations.

        Returns:
            True if all validations pass, False otherwise
        """
        print(f"\n{Colors.BOLD}Validating Cast: {self.cast_name}{Colors.END}\n")

        # Run validations
        structure_valid = self.validate_structure()
        if not structure_valid:
            self.log("\nStructure validation failed - cannot proceed", "error")
            return False

        state_valid = self.validate_state()
        nodes_valid = self.validate_nodes()
        graph_valid = self.validate_graph()

        # Print summary
        print(f"\n{Colors.BOLD}=== Validation Summary ==={Colors.END}")

        if self.errors:
            print(f"\n{Colors.RED}{Colors.BOLD}Errors:{Colors.END}")
            for error in self.errors:
                print(f"  {Colors.RED}✗{Colors.END} {error}")

        if self.warnings:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}Warnings:{Colors.END}")
            for warning in self.warnings:
                print(f"  {Colors.YELLOW}⚠{Colors.END} {warning}")

        # Overall result
        all_valid = structure_valid and state_valid and nodes_valid and graph_valid

        if all_valid and not self.errors:
            print(
                f"\n{Colors.GREEN}{Colors.BOLD}✓ Cast validation passed!{Colors.END}\n"
            )
            return True
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}✗ Cast validation failed{Colors.END}\n")
            return False


def main():
    """Main entry point for the validation script."""
    parser = argparse.ArgumentParser(
        description="Validate Cast structure and implementation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_cast.py my_cast
  python validate_cast.py my_cast --verbose
        """,
    )
    parser.add_argument("cast_name", help="Name of the cast to validate")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    validator = CastValidator(args.cast_name, verbose=args.verbose)
    success = validator.validate()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
