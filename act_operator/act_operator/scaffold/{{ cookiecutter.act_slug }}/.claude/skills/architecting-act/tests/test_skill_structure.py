#!/usr/bin/env python3
"""Tests for architecting-act skill structure and completeness.

Usage:
    python tests/test_skill_structure.py

Validates that the skill has all required files and proper structure.
"""

import json
import sys
from pathlib import Path


def get_skill_root() -> Path:
    """Get skill root directory."""
    return Path(__file__).parent.parent


def test_marketplace_json_exists():
    """Test marketplace.json exists and is valid."""
    print("\n[*] Testing marketplace.json exists...")

    skill_root = get_skill_root()
    marketplace_path = skill_root / ".claude-plugin" / "marketplace.json"

    try:
        assert marketplace_path.exists(), f"marketplace.json not found at {marketplace_path}"
        print(f"  [OK] File exists: {marketplace_path}")

        with open(marketplace_path) as f:
            data = json.load(f)

        assert "name" in data, "Missing 'name' field"
        assert "plugins" in data, "Missing 'plugins' field"
        assert len(data["plugins"]) > 0, "No plugins defined"
        assert "skills" in data["plugins"][0], "Missing 'skills' in plugin"

        print(f"  [OK] Valid JSON structure")
        print(f"  [OK] Plugin name: {data['name']}")
        return True

    except Exception as e:
        print(f"  [X] FAILED: {e}")
        return False


def test_skill_md_exists():
    """Test SKILL.md exists with proper frontmatter."""
    print("\n[*] Testing SKILL.md exists and has frontmatter...")

    skill_root = get_skill_root()
    skill_md_path = skill_root / "SKILL.md"

    try:
        assert skill_md_path.exists(), f"SKILL.md not found at {skill_md_path}"
        print(f"  [OK] File exists: {skill_md_path}")

        content = skill_md_path.read_text(encoding="utf-8")

        # Check frontmatter markers
        assert content.startswith("---"), "Missing frontmatter start marker"
        assert content.count("---") >= 2, "Missing frontmatter end marker"

        # Extract frontmatter
        parts = content.split("---", 2)
        frontmatter = parts[1].strip()

        assert "name:" in frontmatter, "Missing 'name' in frontmatter"
        assert "description:" in frontmatter, "Missing 'description' in frontmatter"

        print(f"  [OK] Valid frontmatter structure")
        return True

    except Exception as e:
        print(f"  [X] FAILED: {e}")
        return False


def test_version_file_exists():
    """Test VERSION file exists."""
    print("\n[*] Testing VERSION file exists...")

    skill_root = get_skill_root()
    version_path = skill_root / "VERSION"

    try:
        assert version_path.exists(), f"VERSION not found at {version_path}"

        version = version_path.read_text(encoding="utf-8").strip()
        assert version, "VERSION file is empty"

        # Basic semver format check
        parts = version.split(".")
        assert len(parts) == 3, f"Invalid version format: {version}"

        print(f"  [OK] Version: {version}")
        return True

    except Exception as e:
        print(f"  [X] FAILED: {e}")
        return False


def test_changelog_exists():
    """Test CHANGELOG.md exists."""
    print("\n[*] Testing CHANGELOG.md exists...")

    skill_root = get_skill_root()
    changelog_path = skill_root / "CHANGELOG.md"

    try:
        assert changelog_path.exists(), f"CHANGELOG.md not found at {changelog_path}"

        content = changelog_path.read_text(encoding="utf-8")
        assert "## [1.0.0]" in content, "Missing v1.0.0 entry"

        print(f"  [OK] CHANGELOG.md has version entry")
        return True

    except Exception as e:
        print(f"  [X] FAILED: {e}")
        return False


def test_resources_exist():
    """Test required resource files exist."""
    print("\n[*] Testing resource files exist...")

    skill_root = get_skill_root()
    resources_dir = skill_root / "resources"

    # Note: act-template.md, cast-template.md, validation-checklist.md
    # have been migrated to templates/ directory
    required_files = [
        "agentic-design-patterns.md",
        "pattern-decision-matrix.md",
        "cast-analysis-guide.md",
        "modes/initial-design-questions.md",
        "modes/add-cast-questions.md",
        "modes/extract-subcast-questions.md",
        "design/state-schema.md",
        "design/node-specification.md",
        "design/edge-routing.md",
    ]

    try:
        missing = []
        for file in required_files:
            file_path = resources_dir / file
            if not file_path.exists():
                missing.append(file)
            else:
                print(f"  [OK] Found: {file}")

        assert len(missing) == 0, f"Missing resource files: {missing}"
        return True

    except Exception as e:
        print(f"  [X] FAILED: {e}")
        return False


def test_templates_exist():
    """Test required template files exist with AUTO-MANAGED markers."""
    print("\n[*] Testing template files exist...")

    skill_root = get_skill_root()
    templates_dir = skill_root / "templates"

    required_templates = [
        "CLAUDE.act.md.template",
        "CLAUDE.cast.md.template",
    ]

    try:
        for template in required_templates:
            template_path = templates_dir / template
            assert template_path.exists(), f"Missing template: {template}"
            print(f"  [OK] Found: {template}")

            # Verify AUTO-MANAGED markers
            content = template_path.read_text(encoding="utf-8")
            assert "<!-- AUTO-MANAGED:" in content, f"Missing AUTO-MANAGED marker in {template}"
            assert "<!-- END AUTO-MANAGED -->" in content, f"Missing END AUTO-MANAGED marker in {template}"
            assert "<!-- MANUAL -->" in content, f"Missing MANUAL section in {template}"
            print(f"  [OK] {template} has proper markers")

        return True

    except Exception as e:
        print(f"  [X] FAILED: {e}")
        return False


def test_scripts_exist():
    """Test required script files exist."""
    print("\n[*] Testing script files exist...")

    skill_root = get_skill_root()
    scripts_dir = skill_root / "scripts"

    required_files = [
        "validate_architecture.py",
    ]

    try:
        for file in required_files:
            file_path = scripts_dir / file
            assert file_path.exists(), f"Missing script: {file}"
            print(f"  [OK] Found: {file}")

        return True

    except Exception as e:
        print(f"  [X] FAILED: {e}")
        return False


def test_activation_keywords():
    """Test activation keywords are defined."""
    print("\n[*] Testing activation keywords...")

    skill_root = get_skill_root()
    marketplace_path = skill_root / ".claude-plugin" / "marketplace.json"

    try:
        with open(marketplace_path) as f:
            data = json.load(f)

        activation = data.get("activation", {})
        keywords = activation.get("keywords", [])
        patterns = activation.get("patterns", [])

        assert len(keywords) >= 10, f"Need at least 10 keywords, found {len(keywords)}"
        assert len(patterns) >= 5, f"Need at least 5 patterns, found {len(patterns)}"

        print(f"  [OK] Keywords: {len(keywords)}")
        print(f"  [OK] Patterns: {len(patterns)}")
        return True

    except Exception as e:
        print(f"  [X] FAILED: {e}")
        return False


def test_description_sync():
    """Test marketplace.json description matches SKILL.md."""
    print("\n[*] Testing description synchronization...")

    skill_root = get_skill_root()
    marketplace_path = skill_root / ".claude-plugin" / "marketplace.json"
    skill_md_path = skill_root / "SKILL.md"

    try:
        # Get marketplace description
        with open(marketplace_path) as f:
            marketplace_data = json.load(f)

        marketplace_desc = marketplace_data["plugins"][0]["description"]

        # Get SKILL.md description
        content = skill_md_path.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        frontmatter = parts[1]

        # Extract description from frontmatter
        for line in frontmatter.split("\n"):
            if line.startswith("description:"):
                skill_desc = line.replace("description:", "").strip()
                break

        assert marketplace_desc == skill_desc, (
            f"Description mismatch!\n"
            f"marketplace.json: {marketplace_desc[:50]}...\n"
            f"SKILL.md: {skill_desc[:50]}..."
        )

        print(f"  [OK] Descriptions are synchronized")
        return True

    except Exception as e:
        print(f"  [X] FAILED: {e}")
        return False


def main():
    """Run all skill structure tests."""
    print("=" * 70)
    print("SKILL STRUCTURE TESTS - architecting-act")
    print("=" * 70)

    tests = [
        ("Marketplace.json exists", test_marketplace_json_exists),
        ("SKILL.md exists", test_skill_md_exists),
        ("VERSION file", test_version_file_exists),
        ("CHANGELOG.md", test_changelog_exists),
        ("Resource files", test_resources_exist),
        ("Template files", test_templates_exist),
        ("Script files", test_scripts_exist),
        ("Activation keywords", test_activation_keywords),
        ("Description sync", test_description_sync),
    ]

    results = []
    for test_name, test_func in tests:
        passed = test_func()
        results.append((test_name, passed))

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{'[OK]' if passed else '[X]'} {test_name}")

    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)

    print(f"\nResults: {passed_count}/{total_count} passed")

    return passed_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
