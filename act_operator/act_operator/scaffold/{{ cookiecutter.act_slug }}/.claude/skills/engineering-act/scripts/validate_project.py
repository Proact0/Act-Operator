#!/usr/bin/env python3
"""
Validate Act project structure and configuration.

Checks for required files, proper configuration, and common issues.

Usage:
    uv run python .claude/skills/engineering-act/scripts/validate_project.py
    uv run python .claude/skills/engineering-act/scripts/validate_project.py --fix
"""

import argparse
import sys
import tomllib
from pathlib import Path


class Validator:
    """Project structure validator."""

    def __init__(self, fix: bool = False):
        self.fix = fix
        self.errors = []
        self.warnings = []
        self.fixes_applied = []

    def error(self, message: str):
        """Add error message."""
        self.errors.append(message)

    def warning(self, message: str):
        """Add warning message."""
        self.warnings.append(message)

    def fixed(self, message: str):
        """Add fix message."""
        self.fixes_applied.append(message)

    def check_file_exists(self, path: Path, required: bool = True) -> bool:
        """Check if file exists."""
        if not path.exists():
            if required:
                self.error(f"Missing required file: {path}")
            else:
                self.warning(f"Missing optional file: {path}")
            return False
        return True

    def validate_pyproject_toml(self):
        """Validate pyproject.toml."""
        print("📋 Checking pyproject.toml...")

        pyproject = Path("pyproject.toml")
        if not self.check_file_exists(pyproject):
            return

        try:
            with open(pyproject, "rb") as f:
                data = tomllib.load(f)

            # Check project section
            if "project" not in data:
                self.error("pyproject.toml missing [project] section")
                return

            project = data["project"]

            # Check required fields
            required_fields = ["name", "version", "requires-python", "dependencies"]
            for field in required_fields:
                if field not in project:
                    self.error(f"pyproject.toml missing project.{field}")

            # Check workspace configuration
            if "tool" in data and "uv" in data["tool"]:
                uv_config = data["tool"]["uv"]
                if "workspace" in uv_config:
                    workspace = uv_config["workspace"]
                    if "members" in workspace:
                        if "casts/*" not in workspace["members"]:
                            self.warning("workspace.members should include 'casts/*'")
                    else:
                        self.warning("workspace missing 'members' field")
                else:
                    self.warning("Missing [tool.uv.workspace] section")

            print("  ✓ pyproject.toml valid")

        except tomllib.TOMLDecodeError as e:
            self.error(f"Invalid TOML in pyproject.toml: {e}")
        except Exception as e:
            self.error(f"Error reading pyproject.toml: {e}")

    def validate_structure(self):
        """Validate project directory structure."""
        print("\n📁 Checking project structure...")

        # Required directories
        required_dirs = [
            ("casts", True),
            ("tests", False),
            (".venv", False),
        ]

        for dir_name, required in required_dirs:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                if required:
                    self.error(f"Missing required directory: {dir_name}/")
                else:
                    self.warning(f"Missing directory: {dir_name}/")
            else:
                print(f"  ✓ {dir_name}/ exists")

        # Required files
        required_files = [
            ("pyproject.toml", True),
            ("README.md", False),
            (".gitignore", False),
            ("uv.lock", False),
        ]

        for file_name, required in required_files:
            self.check_file_exists(Path(file_name), required)

    def validate_casts(self):
        """Validate cast structures."""
        print("\n🎬 Checking casts...")

        casts_dir = Path("casts")
        if not casts_dir.exists():
            return

        # Check base files
        base_files = ["base_node.py", "base_graph.py", "__init__.py"]
        for base_file in base_files:
            path = casts_dir / base_file
            if not path.exists():
                self.error(f"Missing base file: casts/{base_file}")

        # Check individual casts
        casts = [
            d for d in casts_dir.iterdir()
            if d.is_dir() and not d.name.startswith("_") and d.name != "__pycache__"
        ]

        if not casts:
            self.warning("No casts found in casts/ directory")
            return

        for cast_dir in casts:
            print(f"\n  Checking cast: {cast_dir.name}")

            # Required files
            required = ["graph.py", "__init__.py"]
            for file_name in required:
                if not (cast_dir / file_name).exists():
                    self.error(f"  Missing {cast_dir.name}/{file_name}")

            # Optional modules directory
            modules_dir = cast_dir / "modules"
            if modules_dir.exists():
                print(f"    ✓ modules/ directory exists")
            else:
                self.warning(f"  {cast_dir.name}/ missing modules/ directory")

    def validate_environment(self):
        """Validate environment setup."""
        print("\n🔧 Checking environment...")

        venv = Path(".venv")
        if venv.exists():
            print("  ✓ Virtual environment exists")
        else:
            self.warning("No virtual environment (.venv/) found")
            if self.fix:
                print("    Run: uv sync")

        lock_file = Path("uv.lock")
        if lock_file.exists():
            print("  ✓ Lockfile exists")
        else:
            self.warning("No lockfile (uv.lock) found")
            if self.fix:
                print("    Run: uv lock")

    def run_validation(self):
        """Run all validations."""
        print("\n" + "="*50)
        print("  ACT PROJECT VALIDATION")
        print("="*50 + "\n")

        self.validate_structure()
        self.validate_pyproject_toml()
        self.validate_casts()
        self.validate_environment()

        # Print summary
        print("\n" + "="*50)
        print("  VALIDATION SUMMARY")
        print("="*50 + "\n")

        if self.errors:
            print(f"❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
            print()

        if self.warnings:
            print(f"⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
            print()

        if self.fixes_applied:
            print(f"🔧 Fixes Applied ({len(self.fixes_applied)}):")
            for fix in self.fixes_applied:
                print(f"   • {fix}")
            print()

        if not self.errors and not self.warnings:
            print("✅ Project structure is valid!\n")
            return 0
        elif self.errors:
            print("❌ Validation failed with errors\n")
            return 1
        else:
            print("⚠️  Validation passed with warnings\n")
            return 0


def main():
    parser = argparse.ArgumentParser(
        description="Validate Act project structure and configuration"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to fix common issues automatically"
    )

    args = parser.parse_args()

    # Check if in project directory
    if not Path("pyproject.toml").exists():
        print("❌ Not in an Act project directory", file=sys.stderr)
        print("   (no pyproject.toml found)", file=sys.stderr)
        sys.exit(1)

    validator = Validator(fix=args.fix)
    exit_code = validator.run_validation()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
