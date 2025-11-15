#!/usr/bin/env python3
"""
Batch add or remove multiple dependencies at once.

Saves typing multiple `uv add` or `uv remove` commands.

Usage:
    uv run python .claude/skills/engineering-act/scripts/batch_dependencies.py add langchain-openai langchain-anthropic
    uv run python .claude/skills/engineering-act/scripts/batch_dependencies.py add --dev pytest-asyncio pytest-mock
    uv run python .claude/skills/engineering-act/scripts/batch_dependencies.py remove langchain-openai
"""

import argparse
import subprocess
import sys


def run_uv_command(action: str, packages: list[str], dev: bool = False):
    """Run uv add or remove command."""

    if action == "add":
        cmd = ["uv", "add"]
        if dev:
            cmd.append("--dev")
        cmd.extend(packages)
        verb = "Adding"
    elif action == "remove":
        cmd = ["uv", "remove"]
        cmd.extend(packages)
        verb = "Removing"
    else:
        print(f"❌ Unknown action: {action}", file=sys.stderr)
        sys.exit(1)

    print(f"\n{verb} {len(packages)} package(s)...")
    print(f"Command: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✅ Successfully {action}ed {len(packages)} package(s)")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error {action}ing packages", file=sys.stderr)
        return e.returncode


def main():
    parser = argparse.ArgumentParser(
        description="Batch add or remove multiple dependencies",
        epilog="Examples:\n"
               "  uv run python .claude/skills/engineering-act/scripts/batch_dependencies.py add langchain-openai langchain-anthropic\n"
               "  uv run python .claude/skills/engineering-act/scripts/batch_dependencies.py add --dev pytest-asyncio pytest-mock\n"
               "  uv run python .claude/skills/engineering-act/scripts/batch_dependencies.py remove langchain-openai",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "action",
        choices=["add", "remove"],
        help="Action to perform (add or remove)"
    )

    parser.add_argument(
        "packages",
        nargs="+",
        help="Package names to add or remove"
    )

    parser.add_argument(
        "--dev",
        action="store_true",
        help="Add to dev dependencies (only for 'add' action)"
    )

    args = parser.parse_args()

    if args.dev and args.action != "add":
        print("⚠️  --dev flag only applies to 'add' action", file=sys.stderr)

    exit_code = run_uv_command(args.action, args.packages, args.dev)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
