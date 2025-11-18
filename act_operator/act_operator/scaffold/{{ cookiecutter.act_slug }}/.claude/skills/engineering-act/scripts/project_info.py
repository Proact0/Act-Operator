#!/usr/bin/env python3
"""
Display comprehensive Act project information.

Shows Python version, installed packages, casts, and project status.

Usage:
    uv run python .claude/skills/engineering-act/scripts/project_info.py
    uv run python .claude/skills/engineering-act/scripts/project_info.py --packages
"""

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path


def run_command(cmd: list[str], capture=True) -> tuple[str, int]:
    """Run command and return output."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
            check=False
        )
        return result.stdout.strip() if capture else "", result.returncode
    except Exception as e:
        return f"Error: {e}", 1


def get_python_version() -> str:
    """Get Python version."""
    output, _ = run_command(["uv", "run", "python", "--version"])
    return output.replace("Python ", "")


def get_project_name() -> str:
    """Get project name from pyproject.toml."""
    pyproject = Path("pyproject.toml")
    if not pyproject.exists():
        return "Unknown"

    try:
        with open(pyproject, "rb") as f:
            data = tomllib.load(f)
            return data.get("project", {}).get("name", "Unknown")
    except Exception:
        return "Unknown"


def get_casts() -> list[str]:
    """Get list of casts."""
    casts_dir = Path("casts")
    if not casts_dir.exists():
        return []

    casts = []
    for item in casts_dir.iterdir():
        if item.is_dir() and not item.name.startswith("_") and item.name != "__pycache__":
            # Check if has graph.py or pyproject.toml
            if (item / "graph.py").exists() or (item / "pyproject.toml").exists():
                casts.append(item.name)

    return sorted(casts)


def get_dependencies() -> dict[str, list[str]]:
    """Get dependencies from pyproject.toml."""
    pyproject = Path("pyproject.toml")
    if not pyproject.exists():
        return {}

    try:
        with open(pyproject, "rb") as f:
            data = tomllib.load(f)

            deps = {
                "production": data.get("project", {}).get("dependencies", []),
            }

            # Get dependency groups
            dep_groups = data.get("dependency-groups", {})
            for group_name, group_deps in dep_groups.items():
                # Filter out include-group entries
                actual_deps = [
                    d for d in group_deps
                    if not isinstance(d, dict) or "include-group" not in d
                ]
                deps[group_name] = actual_deps

            return deps
    except Exception:
        return {}


def count_installed_packages() -> int:
    """Count installed packages."""
    output, code = run_command(["uv", "pip", "list"])
    if code != 0:
        return 0
    # Subtract 2 for header lines
    return max(0, len(output.strip().split("\n")) - 2)


def display_info(show_packages: bool = False):
    """Display project information."""

    print("\n╔═══════════════════════════════════════╗")
    print("║     ACT PROJECT INFORMATION          ║")
    print("╚═══════════════════════════════════════╝\n")

    # Project basics
    print(f"📦 Project: {get_project_name()}")
    print(f"🐍 Python: {get_python_version()}")
    print(f"📚 Installed packages: {count_installed_packages()}")

    # Casts
    casts = get_casts()
    print(f"\n🎬 Casts ({len(casts)}):")
    if casts:
        for cast in casts:
            print(f"   • {cast}")
    else:
        print("   (no casts found)")

    # Dependencies
    deps = get_dependencies()
    print(f"\n📋 Dependencies:")

    for group, packages in deps.items():
        if packages:
            print(f"   {group}: {len(packages)} package(s)")
            if show_packages:
                for pkg in packages:
                    print(f"      • {pkg}")

    # Environment status
    print(f"\n🔧 Environment:")
    env_path = Path(".venv")
    if env_path.exists():
        print(f"   ✓ Virtual environment: .venv/")
    else:
        print(f"   ✗ No virtual environment found")

    lock_file = Path("uv.lock")
    if lock_file.exists():
        print(f"   ✓ Lockfile: uv.lock")
    else:
        print(f"   ✗ No lockfile found (managed by CI/CD)")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Display Act project information"
    )
    parser.add_argument(
        "--packages", "-p",
        action="store_true",
        help="Show individual packages in each dependency group"
    )

    args = parser.parse_args()

    # Check if in Act project
    if not Path("pyproject.toml").exists():
        print("❌ Not in an Act project directory", file=sys.stderr)
        print("   (no pyproject.toml found)", file=sys.stderr)
        sys.exit(1)

    display_info(show_packages=args.packages)


if __name__ == "__main__":
    main()
