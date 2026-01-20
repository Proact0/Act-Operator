#!/usr/bin/env python3
"""Tests for validate_architecture.py script.

Usage:
    python tests/test_validate_architecture.py

Tests the architecture validation functions.
"""

import sys
import tempfile
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from validate_architecture import (
    ValidationReport,
    ValidationResult,
    parse_act_claude_md,
    parse_cast_claude_md,
)


def test_validation_result():
    """Test ValidationResult dataclass."""
    print("\n[*] Testing ValidationResult...")

    try:
        result = ValidationResult(passed=True, message="Test passed", severity="info")

        assert result.passed is True
        assert result.message == "Test passed"
        assert result.severity == "info"

        print(f"  [OK] ValidationResult works correctly")
        return True

    except Exception as e:
        print(f"  [X] FAILED: {e}")
        return False


def test_validation_report():
    """Test ValidationReport class."""
    print("\n[*] Testing ValidationReport...")

    try:
        report = ValidationReport()

        # Add some results
        report.add(True, "Check 1 passed")
        report.add(False, "Check 2 failed", "error")
        report.add(False, "Check 3 warning", "warning")

        assert len(report.results) == 3
        assert len(report.errors) == 1
        assert len(report.warnings) == 1
        assert report.passed is False  # Has errors

        print(f"  [OK] ValidationReport tracks results correctly")
        print(f"  [OK] Errors: {len(report.errors)}, Warnings: {len(report.warnings)}")
        return True

    except Exception as e:
        print(f"  [X] FAILED: {e}")
        return False


def test_parse_act_claude_md():
    """Test parsing of root CLAUDE.md."""
    print("\n[*] Testing parse_act_claude_md...")

    sample_content = """# Test Act

## Act Overview
**Purpose:** Test purpose
**Domain:** Testing

## Casts
| Cast Name | Purpose | Location |
|-----------|---------|----------|
| TestCast | Test cast | [casts/test_cast/CLAUDE.md](casts/test_cast/CLAUDE.md) |
| AnotherCast | Another | [casts/another_cast/CLAUDE.md](casts/another_cast/CLAUDE.md) |
"""

    try:
        data = parse_act_claude_md(sample_content)

        assert data["has_act_overview"] is True, "Should detect Act Overview"
        assert data["has_casts_table"] is True, "Should detect Casts table"
        assert len(data["casts_in_table"]) == 2, f"Should find 2 casts, found {len(data['casts_in_table'])}"

        print(f"  [OK] Detected Act Overview: {data['has_act_overview']}")
        print(f"  [OK] Detected Casts table: {data['has_casts_table']}")
        print(f"  [OK] Found {len(data['casts_in_table'])} casts in table")
        return True

    except Exception as e:
        print(f"  [X] FAILED: {e}")
        return False


def test_parse_cast_claude_md():
    """Test parsing of cast CLAUDE.md."""
    print("\n[*] Testing parse_cast_claude_md...")

    sample_content = """# Cast: TestCast

**Parent Act:** [../CLAUDE.md](../CLAUDE.md)

## Overview
**Purpose:** Test cast purpose
**Pattern:** Sequential
**Latency:** Low

## Architecture Diagram

```mermaid
graph TD
    START((START)) --> Process[ProcessNode]
    Process --> END((END))
```

## State Schema

### InputState
| Field | Type | Description |
|-------|------|-------------|
| input | str | Input data |

### OutputState
| Field | Type | Description |
|-------|------|-------------|
| output | str | Output data |

### OverallState
| Field | Type | Category | Description |
|-------|------|----------|-------------|
| input | str | Input | Input data |
| output | str | Output | Output data |
| internal | str | Internal | Internal data |

## Node Specifications

### ProcessNode
| Attribute | Value |
|-----------|-------|
| Responsibility | Process the input |
| Reads | input |
| Writes | output |

## Technology Stack

### Additional Dependencies
| Package | Purpose |
|---------|---------|
| none | No additional deps |
"""

    try:
        data = parse_cast_claude_md(sample_content, "TestCast")

        assert data["name"] == "TestCast"
        assert data["has_overview"] is True
        assert data["has_diagram"] is True
        assert data["has_input_state"] is True
        assert data["has_output_state"] is True
        assert data["has_overall_state"] is True
        assert data["has_nodes"] is True
        assert data["has_tech_stack"] is True
        assert data["has_parent_link"] is True

        print(f"  [OK] Cast name: {data['name']}")
        print(f"  [OK] Has overview: {data['has_overview']}")
        print(f"  [OK] Has diagram: {data['has_diagram']}")
        print(f"  [OK] Has all state schemas: Input={data['has_input_state']}, Output={data['has_output_state']}, Overall={data['has_overall_state']}")
        print(f"  [OK] Has nodes: {data['has_nodes']}")
        print(f"  [OK] Has parent link: {data['has_parent_link']}")
        return True

    except Exception as e:
        print(f"  [X] FAILED: {e}")
        return False


def test_mermaid_detection():
    """Test mermaid diagram detection in cast parsing."""
    print("\n[*] Testing mermaid diagram detection...")

    sample_content = """# Cast: TestCast

## Architecture Diagram

```mermaid
graph TD
    START((START)) --> Node1[First]
    Node1 --> Node2[Second]
    Node2 --> Node3[Third]
    Node3 --> END((END))
```
"""

    try:
        data = parse_cast_claude_md(sample_content, "TestCast")

        assert data.get("mermaid_has_start") is True, "Should detect START node"
        assert data.get("mermaid_has_end") is True, "Should detect END node"
        assert data.get("mermaid_node_count", 0) >= 3, "Should find at least 3 nodes"

        print(f"  [OK] Has START: {data.get('mermaid_has_start')}")
        print(f"  [OK] Has END: {data.get('mermaid_has_end')}")
        print(f"  [OK] Node count: {data.get('mermaid_node_count')}")
        return True

    except Exception as e:
        print(f"  [X] FAILED: {e}")
        return False


def test_report_passed_status():
    """Test ValidationReport.passed property."""
    print("\n[*] Testing report passed status...")

    try:
        # Report with no errors should pass
        report1 = ValidationReport()
        report1.add(True, "Check 1")
        report1.add(True, "Check 2")
        report1.add(False, "Warning", "warning")  # Warnings don't fail

        assert report1.passed is True, "Report with only warnings should pass"

        # Report with errors should fail
        report2 = ValidationReport()
        report2.add(True, "Check 1")
        report2.add(False, "Error", "error")

        assert report2.passed is False, "Report with errors should fail"

        print(f"  [OK] Report without errors: passed={report1.passed}")
        print(f"  [OK] Report with errors: passed={report2.passed}")
        return True

    except Exception as e:
        print(f"  [X] FAILED: {e}")
        return False


def main():
    """Run all validation script tests."""
    print("=" * 70)
    print("VALIDATION SCRIPT TESTS - act-architect")
    print("=" * 70)

    tests = [
        ("ValidationResult", test_validation_result),
        ("ValidationReport", test_validation_report),
        ("Parse Act CLAUDE.md", test_parse_act_claude_md),
        ("Parse Cast CLAUDE.md", test_parse_cast_claude_md),
        ("Mermaid detection", test_mermaid_detection),
        ("Report passed status", test_report_passed_status),
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
