#!/usr/bin/env python3
"""Validate node implementation.

This script validates that a node is properly implemented with correct inheritance,
method signatures, and functionality.

Usage:
    python validate_node.py <cast_name> <node_name>
    python validate_node.py my_cast MyNode --verbose
    python validate_node.py my_cast MyNode --test
"""

import argparse
import asyncio
import importlib
import inspect
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


class NodeValidator:
    """Validates node implementation."""

    def __init__(
        self, cast_name: str, node_name: str, verbose: bool = False, test: bool = False
    ):
        """Initialize the validator.

        Args:
            cast_name: Name of the cast containing the node
            node_name: Name of the node class to validate
            verbose: Enable verbose output
            test: Enable test execution
        """
        self.cast_name = cast_name
        self.node_name = node_name
        self.verbose = verbose
        self.test = test
        self.errors: list[str] = []
        self.warnings: list[str] = []

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

    def load_node_class(self) -> Optional[type]:
        """Load the node class from the module.

        Returns:
            Node class or None if loading fails
        """
        try:
            module = importlib.import_module(f"casts.{self.cast_name}.modules.nodes")
            self.log(
                f"Successfully loaded module: casts.{self.cast_name}.modules.nodes",
                "success",
            )

            if not hasattr(module, self.node_name):
                self.errors.append(f"Node class '{self.node_name}' not found in module")
                self.log(f"Node class '{self.node_name}' not found in module", "error")
                return None

            node_class = getattr(module, self.node_name)
            self.log(f"Found node class: {self.node_name}", "success")
            return node_class

        except Exception as e:
            self.errors.append(f"Failed to load node class: {str(e)}")
            self.log(f"Failed to load node class: {str(e)}", "error")
            return None

    def validate_inheritance(self, node_class: type) -> bool:
        """Validate node inherits from BaseNode or AsyncBaseNode.

        Args:
            node_class: Node class to validate

        Returns:
            True if inheritance is valid, False otherwise
        """
        self.log("\n=== Validating Inheritance ===", "info")

        # Get base class names
        base_names = [base.__name__ for base in node_class.__bases__]
        self.log(f"Base classes: {base_names}", "info")

        if "BaseNode" in base_names:
            self.log("Node inherits from BaseNode (sync)", "success")
            return True
        elif "AsyncBaseNode" in base_names:
            self.log("Node inherits from AsyncBaseNode (async)", "success")
            return True
        else:
            self.errors.append(
                f"Node must inherit from BaseNode or AsyncBaseNode, found: {base_names}"
            )
            self.log(
                f"Node must inherit from BaseNode or AsyncBaseNode, found: {base_names}",
                "error",
            )
            return False

    def validate_execute_method(self, node_class: type) -> bool:
        """Validate execute method signature.

        Args:
            node_class: Node class to validate

        Returns:
            True if execute method is valid, False otherwise
        """
        self.log("\n=== Validating execute() Method ===", "info")

        if not hasattr(node_class, "execute"):
            self.errors.append("Node missing execute() method")
            self.log("Node missing execute() method", "error")
            return False

        self.log("Found execute() method", "success")

        # Get method signature
        sig = inspect.signature(node_class.execute)
        params = list(sig.parameters.keys())
        self.log(f"Method signature: {params}", "info")

        # Validate first parameter is 'self'
        if not params or params[0] != "self":
            self.errors.append("execute() must have 'self' as first parameter")
            self.log("execute() must have 'self' as first parameter", "error")
            return False

        # Validate second parameter is 'state'
        if len(params) < 2 or params[1] != "state":
            self.errors.append("execute() must have 'state' as second parameter")
            self.log("execute() must have 'state' as second parameter", "error")
            return False

        self.log("Method signature is valid", "success")

        # Check if method is async
        if inspect.iscoroutinefunction(node_class.execute):
            self.log("Method is async (uses 'async def')", "info")

            # Verify async node inherits from AsyncBaseNode
            base_names = [base.__name__ for base in node_class.__bases__]
            if "AsyncBaseNode" not in base_names:
                self.warnings.append(
                    "Async execute() method should inherit from AsyncBaseNode"
                )
                self.log(
                    "Async execute() method should inherit from AsyncBaseNode",
                    "warning",
                )
        else:
            self.log("Method is sync", "info")

        # Check return type annotation
        if sig.return_annotation != inspect.Signature.empty:
            return_type = sig.return_annotation
            self.log(f"Return type annotation: {return_type}", "info")
            
            # Check if it's dict or dict-like
            if hasattr(return_type, "__name__") and "dict" in return_type.__name__.lower():
                self.log("Return type is dict (correct)", "success")
            else:
                self.warnings.append(
                    f"execute() should return dict, found annotation: {return_type}"
                )
                self.log(
                    f"execute() should return dict, found annotation: {return_type}",
                    "warning",
                )
        else:
            self.warnings.append(
                "execute() missing return type annotation (should be -> dict)"
            )
            self.log(
                "execute() missing return type annotation (should be -> dict)", "warning"
            )

        return True

    def test_node_execution(self, node_class: type) -> bool:
        """Test node execution with dummy state.

        Args:
            node_class: Node class to test

        Returns:
            True if test passes, False otherwise
        """
        if not self.test:
            return True

        self.log("\n=== Testing Node Execution ===", "info")

        try:
            # Create node instance
            node = node_class()
            self.log("Created node instance", "success")

            # Create dummy state
            from dataclasses import dataclass

            @dataclass
            class DummyState:
                query: str = "test"
                messages: list = None

                def __post_init__(self):
                    if self.messages is None:
                        self.messages = []

            state = DummyState()
            self.log("Created dummy state", "info")

            # Execute node
            if inspect.iscoroutinefunction(node_class.execute):
                self.log("Executing async node...", "info")
                result = asyncio.run(node(state))
            else:
                self.log("Executing sync node...", "info")
                result = node(state)

            self.log(f"Execution completed", "success")
            self.log(f"Result: {result}", "info")

            # Validate result is a dict
            if not isinstance(result, dict):
                self.errors.append(
                    f"execute() must return dict, got: {type(result).__name__}"
                )
                self.log(
                    f"execute() must return dict, got: {type(result).__name__}", "error"
                )
                return False

            self.log("Result is a dict (correct)", "success")

            # Check result has content
            if not result:
                self.warnings.append("Result dict is empty")
                self.log("Result dict is empty", "warning")
            else:
                self.log(f"Result keys: {list(result.keys())}", "info")

            return True

        except Exception as e:
            self.errors.append(f"Node execution failed: {str(e)}")
            self.log(f"Node execution failed: {str(e)}", "error")
            return False

    def validate(self) -> bool:
        """Run all validations.

        Returns:
            True if all validations pass, False otherwise
        """
        print(
            f"\n{Colors.BOLD}Validating Node: {self.cast_name}.{self.node_name}{Colors.END}\n"
        )

        # Load node class
        node_class = self.load_node_class()
        if not node_class:
            return False

        # Run validations
        inheritance_valid = self.validate_inheritance(node_class)
        execute_valid = self.validate_execute_method(node_class)
        test_valid = self.test_node_execution(node_class)

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
        all_valid = inheritance_valid and execute_valid and test_valid

        if all_valid and not self.errors:
            print(
                f"\n{Colors.GREEN}{Colors.BOLD}✓ Node validation passed!{Colors.END}\n"
            )
            return True
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}✗ Node validation failed{Colors.END}\n")
            return False


def main():
    """Main entry point for the validation script."""
    parser = argparse.ArgumentParser(
        description="Validate node implementation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_node.py my_cast MyNode
  python validate_node.py my_cast MyNode --verbose
  python validate_node.py my_cast MyNode --test
        """,
    )
    parser.add_argument("cast_name", help="Name of the cast containing the node")
    parser.add_argument("node_name", help="Name of the node class to validate")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "-t", "--test", action="store_true", help="Test node execution with dummy state"
    )

    args = parser.parse_args()

    validator = NodeValidator(
        args.cast_name, args.node_name, verbose=args.verbose, test=args.test
    )
    success = validator.validate()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
