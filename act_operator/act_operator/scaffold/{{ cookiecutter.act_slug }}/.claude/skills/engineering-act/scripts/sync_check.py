#!/usr/bin/env python3
"""
Sync environment and show what changed.

Runs `uv sync` and displays added/removed packages.

Usage:
    uv run python .claude/skills/engineering-act/scripts/sync_check.py
    uv run python .claude/skills/engineering-act/scripts/sync_check.py --all-extras
"""

import argparse
import subprocess
import sys


def get_installed_packages() -> set[str]:
    """Get set of currently installed packages."""
    try:
        result = subprocess.run(
            ["uv", "pip", "list"],
            capture_output=True,
            text=True,
            check=True
        )

        packages = set()
        # Skip header lines
        lines = result.stdout.strip().split("\n")[2:]
        for line in lines:
            if line.strip():
                # Format: "package-name version"
                parts = line.split()
                if parts:
                    packages.add(parts[0])

        return packages
    except Exception as e:
        print(f"⚠️  Could not get package list: {e}", file=sys.stderr)
        return set()


def sync_environment(all_extras: bool = False):
    """Sync environment and report changes."""

    print("\n📦 Syncing environment...\n")

    # Get packages before sync
    before = get_installed_packages()
    print(f"Packages before sync: {len(before)}")

    # Run uv sync
    cmd = ["uv", "sync"]
    if all_extras:
        cmd.append("--all-extras")

    print(f"Command: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, check=True)
        print()
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Sync failed with exit code {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)

    # Get packages after sync
    after = get_installed_packages()
    print(f"Packages after sync: {len(after)}")

    # Calculate changes
    added = after - before
    removed = before - after

    # Report changes
    print("\n" + "="*50)
    print("  SYNC SUMMARY")
    print("="*50 + "\n")

    if added:
        print(f"✅ Added ({len(added)}):")
        for pkg in sorted(added):
            print(f"   + {pkg}")
        print()

    if removed:
        print(f"❌ Removed ({len(removed)}):")
        for pkg in sorted(removed):
            print(f"   - {pkg}")
        print()

    if not added and not removed:
        print("✓ No changes - environment already up to date\n")


def main():
    parser = argparse.ArgumentParser(
        description="Sync environment and show what changed"
    )

    parser.add_argument(
        "--all-extras",
        action="store_true",
        help="Install all dependency groups (dev, test, lint)"
    )

    args = parser.parse_args()

    sync_environment(all_extras=args.all_extras)


if __name__ == "__main__":
    main()
