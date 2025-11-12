#!/usr/bin/env python3
"""
Cast Structure Validator

Validates that a Cast has the correct structure and required files.

Usage:
    python scripts/validate_cast.py casts/my_cast
    python scripts/validate_cast.py casts/my_cast --verbose

Checks:
- Required files exist (graph.py, modules/state.py, modules/nodes.py)
- Optional files are properly structured
- Python syntax is valid
- BaseGraph and BaseNode are used correctly
"""

import argparse
import ast
import sys
from pathlib import Path


class CastValidator:
    """Validates Cast structure and content."""

    def __init__(self, cast_path: Path, verbose: bool = False):
        self.cast_path = cast_path
        self.verbose = verbose
        self.errors = []
        self.warnings = []

    def log(self, message: str):
        """Log message if verbose."""
        if self.verbose:
            print(f"  {message}")

    def error(self, message: str):
        """Add error message."""
        self.errors.append(message)
        print(f"  ❌ {message}")

    def warning(self, message: str):
        """Add warning message."""
        self.warnings.append(message)
        print(f"  ⚠️  {message}")

    def success(self, message: str):
        """Print success message."""
        print(f"  ✅ {message}")

    def validate(self) -> bool:
        """Run all validations."""
        print(f"\n🔍 Validating Cast: {self.cast_path.name}")
        print("=" * 60)

        # Check directory exists
        if not self.cast_path.exists():
            self.error(f"Cast directory not found: {self.cast_path}")
            return False

        if not self.cast_path.is_dir():
            self.error(f"Not a directory: {self.cast_path}")
            return False

        # Run checks
        self.check_required_files()
        self.check_graph_py()
        self.check_modules_dir()
        self.check_state_py()
        self.check_nodes_py()
        self.check_optional_files()
        self.check_pyproject_toml()

        # Summary
        print("\n" + "=" * 60)
        print("📊 Validation Summary")
        print("=" * 60)

        if self.errors:
            print(f"❌ Errors: {len(self.errors)}")
            for err in self.errors:
                print(f"   - {err}")

        if self.warnings:
            print(f"⚠️  Warnings: {len(self.warnings)}")
            for warn in self.warnings:
                print(f"   - {warn}")

        if not self.errors and not self.warnings:
            print("✅ All checks passed! Cast structure is valid.")
            return True
        elif not self.errors:
            print("✅ No errors found. Warnings are informational.")
            return True
        else:
            print(f"\n❌ Validation failed with {len(self.errors)} error(s).")
            return False

    def check_required_files(self):
        """Check required files exist."""
        print("\n📁 Checking required files...")

        required = [
            ("graph.py", "Graph definition file"),
            ("modules/", "Modules directory"),
            ("modules/state.py", "State schema file"),
            ("modules/nodes.py", "Node implementations file"),
        ]

        for file_path, description in required:
            full_path = self.cast_path / file_path
            if full_path.exists():
                self.success(f"{description}: {file_path}")
            else:
                self.error(f"Missing {description}: {file_path}")

    def check_graph_py(self):
        """Check graph.py structure."""
        print("\n📄 Checking graph.py...")

        graph_file = self.cast_path / "graph.py"
        if not graph_file.exists():
            return

        try:
            with open(graph_file) as f:
                content = f.read()
                tree = ast.parse(content)

            # Check for BaseGraph import
            has_base_graph_import = any(
                isinstance(node, ast.ImportFrom) and
                node.module == "casts.base_graph" and
                any(alias.name == "BaseGraph" for alias in node.names)
                for node in ast.walk(tree)
            )

            if has_base_graph_import:
                self.success("Imports BaseGraph")
            else:
                self.warning("BaseGraph not imported from casts.base_graph")

            # Check for class extending BaseGraph
            has_graph_class = any(
                isinstance(node, ast.ClassDef) and
                any(
                    isinstance(base, ast.Name) and base.id == "BaseGraph" or
                    isinstance(base, ast.Attribute) and base.attr == "BaseGraph"
                    for base in node.bases
                )
                for node in ast.walk(tree)
            )

            if has_graph_class:
                self.success("Defines class extending BaseGraph")
            else:
                self.error("No class found extending BaseGraph")

            # Check for build method
            has_build_method = any(
                isinstance(node, ast.FunctionDef) and node.name == "build"
                for node in ast.walk(tree)
            )

            if has_build_method:
                self.success("Implements build() method")
            else:
                self.error("Missing build() method in graph class")

        except SyntaxError as e:
            self.error(f"Syntax error in graph.py: {e}")

    def check_modules_dir(self):
        """Check modules directory."""
        print("\n📁 Checking modules/...")

        modules_dir = self.cast_path / "modules"
        if not modules_dir.exists():
            return

        # Check for __init__.py
        init_file = modules_dir / "__init__.py"
        if init_file.exists():
            self.success("__init__.py exists")
        else:
            self.warning("Missing __init__.py in modules/")

    def check_state_py(self):
        """Check state.py structure."""
        print("\n📄 Checking modules/state.py...")

        state_file = self.cast_path / "modules" / "state.py"
        if not state_file.exists():
            return

        try:
            with open(state_file) as f:
                content = f.read()
                tree = ast.parse(content)

            # Check for dataclass usage
            has_dataclass = any(
                isinstance(node, ast.ClassDef) and
                any(
                    isinstance(decorator, ast.Name) and decorator.id == "dataclass" or
                    isinstance(decorator, ast.Call) and
                    isinstance(decorator.func, ast.Name) and
                    decorator.func.id == "dataclass"
                    for decorator in node.decorator_list
                )
                for node in ast.walk(tree)
            )

            if has_dataclass:
                self.success("Uses @dataclass decorator")
            else:
                self.warning("State classes should use @dataclass")

            # Check for State classes
            class_names = [
                node.name for node in ast.walk(tree)
                if isinstance(node, ast.ClassDef)
            ]

            expected_classes = ["InputState", "OutputState", "State"]
            for cls in expected_classes:
                if cls in class_names:
                    self.success(f"Defines {cls}")
                else:
                    self.warning(f"Missing {cls} class (recommended)")

        except SyntaxError as e:
            self.error(f"Syntax error in state.py: {e}")

    def check_nodes_py(self):
        """Check nodes.py structure."""
        print("\n📄 Checking modules/nodes.py...")

        nodes_file = self.cast_path / "modules" / "nodes.py"
        if not nodes_file.exists():
            return

        try:
            with open(nodes_file) as f:
                content = f.read()
                tree = ast.parse(content)

            # Check for BaseNode import
            has_base_node_import = any(
                isinstance(node, ast.ImportFrom) and
                node.module == "casts.base_node" and
                any(alias.name in ["BaseNode", "AsyncBaseNode"] for alias in node.names)
                for node in ast.walk(tree)
            )

            if has_base_node_import:
                self.success("Imports BaseNode or AsyncBaseNode")
            else:
                self.warning("BaseNode not imported from casts.base_node")

            # Check for node classes
            node_classes = [
                node.name for node in ast.walk(tree)
                if isinstance(node, ast.ClassDef) and
                any(
                    isinstance(base, ast.Name) and base.id in ["BaseNode", "AsyncBaseNode"]
                    for base in node.bases
                )
            ]

            if node_classes:
                self.success(f"Defines {len(node_classes)} node class(es)")
                for cls in node_classes:
                    self.log(f"Found node: {cls}")
            else:
                self.error("No node classes found extending BaseNode")

            # Check for execute methods
            has_execute = any(
                isinstance(node, ast.FunctionDef) and node.name == "execute"
                for node in ast.walk(tree)
            )

            if has_execute:
                self.success("Implements execute() method")
            else:
                self.error("No execute() method found in nodes")

        except SyntaxError as e:
            self.error(f"Syntax error in nodes.py: {e}")

    def check_optional_files(self):
        """Check optional module files."""
        print("\n📄 Checking optional files...")

        optional_files = [
            "modules/agents.py",
            "modules/tools.py",
            "modules/prompts.py",
            "modules/models.py",
            "modules/conditions.py",
            "modules/utils.py",
        ]

        found_optional = []
        for file_path in optional_files:
            full_path = self.cast_path / file_path
            if full_path.exists():
                found_optional.append(file_path)

        if found_optional:
            self.success(f"Found {len(found_optional)} optional module(s)")
            for file_path in found_optional:
                self.log(f"Optional: {file_path}")
        else:
            self.log("No optional modules (this is fine)")

    def check_pyproject_toml(self):
        """Check pyproject.toml if it exists."""
        print("\n📄 Checking pyproject.toml...")

        pyproject_file = self.cast_path / "pyproject.toml"
        if pyproject_file.exists():
            self.success("pyproject.toml exists")

            # Check content
            with open(pyproject_file) as f:
                content = f.read()

            if "[project]" in content:
                self.success("Has [project] section")
            else:
                self.warning("Missing [project] section in pyproject.toml")

            if f'name = "{self.cast_path.name}"' in content:
                self.success(f"Package name matches directory: {self.cast_path.name}")
            else:
                self.warning(f"Package name should match directory: {self.cast_path.name}")
        else:
            self.warning("No pyproject.toml (needed for workspace)")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate Cast structure and files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/validate_cast.py casts/my_cast
  python scripts/validate_cast.py casts/my_cast --verbose
        """
    )

    parser.add_argument(
        "cast_path",
        type=Path,
        help="Path to Cast directory (e.g., casts/my_cast)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed validation steps"
    )

    args = parser.parse_args()

    # Validate
    validator = CastValidator(args.cast_path, verbose=args.verbose)
    success = validator.validate()

    # Exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
