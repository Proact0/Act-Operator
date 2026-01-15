"""Pytest configuration for architecting-act skill tests."""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))


@pytest.fixture
def skill_root():
    """Get skill root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def sample_act_claude_md():
    """Sample Act-level CLAUDE.md content."""
    return """# Test Act

## Act Overview
**Purpose:** Test purpose
**Domain:** Testing

## Casts
| Cast Name | Purpose | Location |
|-----------|---------|----------|
| TestCast | Test cast | [casts/test_cast/CLAUDE.md](casts/test_cast/CLAUDE.md) |
"""


@pytest.fixture
def sample_cast_claude_md():
    """Sample Cast-level CLAUDE.md content."""
    return """# Cast: TestCast

**Parent Act:** [../CLAUDE.md](../CLAUDE.md)

## Overview
**Purpose:** Test purpose
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

## Node Specifications

### ProcessNode
| Attribute | Value |
|-----------|-------|
| Responsibility | Process input |
| Reads | input |
| Writes | output |

## Technology Stack

### Additional Dependencies
| Package | Purpose |
|---------|---------|
| none | No additional deps |
"""
