# Act Template Skills - Comprehensive Analysis, Restructuring, and Implementation

Analyze, restructure, and update all Claude skills for the Act Template.

**Context:** Act Operator is a cookiecutter-based CLI tool that generates Act Template projects. The skills you are analyzing guide users working within generated Act Template projects.

**Skills Location:** `act_operator/act_operator/scaffold/{{ cookiecutter.act_slug }}/.claude/skills/`

**Note:** `{{ cookiecutter.* }}` are Jinja2 template variables replaced by cookiecutter during project setup.

---

## Your Mission

This is a comprehensive improvement process:

1. **Analyze** all skills thoroughly
2. **Document** all issues found
3. **Restructure** resources for optimal organization
4. **Implement** all fixes and improvements
5. **Verify** changes are correct

You will be making actual file changes to improve the skills.

---

## Act Template Structure

When Act Operator generates a project, it creates this structure:

```
{{ cookiecutter.act_slug }}/                    # Project name (e.g., "my-project")
├── .claude/
│   └── skills/                                 # Skills for Claude to help users
│       ├── architecting-act/
│       ├── developing-cast/
│       ├── engineering-act/
│       └── testing-cast/
├── casts/
│   ├── __init__.py
│   ├── base_node.py
│   ├── base_graph.py
│   └── {{ cookiecutter.cast_snake }}/          # Initial cast (e.g., "hello_world")
│       ├── __init__.py
│       ├── graph.py
│       ├── pyproject.toml
│       ├── README.md
│       └── modules/
│           ├── __init__.py
│           ├── state.py          (required)
│           ├── nodes.py          (required)
│           ├── agents.py         (optional)
│           ├── conditions.py     (optional)
│           ├── middlewares.py    (optional)
│           ├── models.py         (optional)
│           ├── prompts.py        (optional)
│           ├── tools.py          (optional)
│           └── utils.py          (optional)
├── tests/
│   ├── cast_tests/
│   │   ├── __init__.py
│   │   └── {{ cookiecutter.cast_snake }}_test.py
│   └── node_tests/
│       ├── __init.py
│       └── test_node.py
├── .github/
├── media/
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── langgraph.json
├── pyproject.toml
├── README.md
└── TEMPLATE_README.md
```

**Dynamic Structure:**
- Users can add multiple casts to `casts/` directory
- Each cast gets its own test file in `tests/cast_tests/{cast_name}_test.py`
- Node tests for all casts go in `tests/node_tests/`

---

## Import Patterns

### In graph.py

Use absolute imports:

```python
# casts/my_cast/graph.py
from langgraph.graph import END, START, StateGraph
from casts.base_graph import BaseGraph
from casts.my_cast.modules.nodes import SampleNode
from casts.my_cast.modules.state import InputState, OutputState, State
```

### In modules/*.py

Base classes use absolute imports. Sibling modules use relative imports:

```python
# casts/my_cast/modules/nodes.py
from casts.base_node import AsyncBaseNode, BaseNode  # Absolute

from .tools import my_tool          # Relative
from .models import get_llm         # Relative
from .prompts import SYSTEM_PROMPT  # Relative
```

---

## Test Structure

### Graph Tests

**Location:** `tests/cast_tests/{cast_name}_test.py` (one per cast)

Template file for automated graph testing:

```python
from casts.my_cast.graph import my_cast_graph

def test_graph_produces_message() -> None:
    graph = my_cast_graph()
    result = graph.invoke({"query": "test"})
    assert "messages" in result
```

Run with: `uv run pytest tests/cast_tests/`

### Node Tests

**Location:** `tests/node_tests/test_node.py` (shared by all casts)

Area for writing node unit tests:

```python
from casts.my_cast.modules.nodes import SampleNode

def test_node_execute() -> None:
    node = SampleNode()
    result = node({"input": "test"})
    assert "output" in result
```

Run with: `uv run pytest tests/node_tests/`

---

## Workflow

### Phase 1: Analysis

Read and analyze all resources:

**For each skill:**
1. Read SKILL.md
2. Read all files in `resources/`
3. Read all files in `scripts/`
4. Read all files in `templates/`
5. Note issues, patterns, inefficiencies

**Compare against:**
- Template structure (scaffold files)
- Import patterns (actual template code)
- Test structure
- Python conventions
- LangGraph best practices

### Phase 2: Documentation

Create issue inventory:

**For each issue found:**
- Specific file and line location
- Severity (CRITICAL/HIGH/MEDIUM/LOW)
- Clear description
- Correct pattern
- Fix action needed

**Organize by:**
- Skill (architecting-act, developing-cast, etc.)
- Category (structure, imports, tests, scope, efficiency, etc.)
- Severity

### Phase 3: Planning

Develop implementation plan:

**Prioritize:**
1. CRITICAL issues (breaks functionality)
2. HIGH issues (incorrect information)
3. MEDIUM issues (inefficiency, inconsistency)
4. LOW issues (optimization)

**Consider:**
- File reorganization needs
- Resource merging/splitting
- New resources needed
- Deprecated resources

### Phase 4: Implementation

Execute fixes systematically:

**For content fixes:**
1. Update file paths
2. Correct import patterns
3. Fix code examples
4. Remove out-of-scope content
5. Improve clarity and efficiency

**For restructuring:**
1. Create new organization
2. Move/merge resources
3. Update cross-references in SKILL.md
4. Remove deprecated resources

**Use tools:**
- Read: Verify current content
- Edit: Make targeted changes
- Write: Create new resources
- Bash: Rename/move files if needed

### Phase 5: Verification

Confirm changes are correct:

**Check:**
- All file paths match template
- All imports are correct
- All code examples work
- No broken references
- Consistent terminology
- Clear, efficient content

---

## Issue Categories

### Structure References

Verify:
- `casts/{cast}/modules/state.py` ✓
- `casts/{cast}/modules/nodes.py` ✓
- No references to non-existent root `modules/`

### Import Patterns

Check:
- graph.py uses absolute imports
- modules/*.py uses absolute for base classes
- modules/*.py uses relative for siblings

### Template Variables

Verify:
- `{{ cookiecutter.act_slug }}` used appropriately
- `{{ cookiecutter.cast_snake }}` used appropriately
- Explained when needed, not overused

### Node Naming

Ensure:
- PascalCase class names
- Noun-based (what it IS)

### Test Organization

Verify:
- `tests/cast_tests/{cast_name}_test.py`
- `tests/node_tests/test_node.py`
- Dynamic per-cast test files

### Scope Alignment

Remove:
- Deployment content (out of scope)
- Usage/consumption patterns (out of scope)

Keep:
- Building casts
- Testing casts

### Content Efficiency

Eliminate:
- Redundant explanations
- Duplicate examples
- Excessive verbosity
- Unnecessary cross-references

### Terminology

Standardize:
- "cast" as primary term
- Consistent file naming
- Consistent concepts

---

## Implementation Guidelines

### Making Changes

**File modifications:**
```bash
# Read before editing
Read file_path

# Make precise edits
Edit file_path old_string new_string

# Or write new content
Write file_path content
```

**File organization:**
```bash
# Rename/move if needed
mv old_path new_path

# Remove deprecated
rm deprecated_file
```

### Change Standards

**Every change must:**
- Fix a documented issue
- Be verifiable against template
- Maintain or improve clarity
- Not introduce new issues

**Avoid:**
- Changing correct content
- Breaking working examples
- Introducing inconsistencies
- Over-engineering

### Batch Changes

**For systematic issues:**
1. Document the pattern
2. Find all instances
3. Fix consistently
4. Verify all fixes

**Example:**
```markdown
Pattern: `casts/{cast}/state.py` → `casts/{cast}/modules/state.py`
Files affected: 15 resources in developing-cast
Fix approach: Search and replace with verification
```

---

## Deliverables

### 1. Analysis Report

```markdown
# Skills Analysis Report

## Summary
- Files analyzed: [count]
- Issues found: [count by severity]
- Resources restructured: [count]

## Issues by Skill

### architecting-act
[List of issues with severity]

### developing-cast
[List of issues with severity]

### engineering-act
[List of issues with severity]

### testing-cast
[List of issues with severity]

## Restructuring Performed
[List of reorganizations]
```

### 2. Implementation Log

```markdown
# Implementation Log

## Files Modified
1. [file_path] - [what was changed]
2. [file_path] - [what was changed]
...

## Files Created
1. [file_path] - [purpose]
...

## Files Removed
1. [file_path] - [reason]
...

## Verification Results
[Confirmation all changes are correct]
```

### 3. Updated Skills

All skill files corrected and improved, ready for use.

---

## Quality Standards

### Accuracy
Every file path, import, and example must match the template.

### Completeness
All issues must be addressed, no gaps.

### Consistency
Same patterns applied uniformly across all skills.

### Efficiency
Concise, clear, actionable content.

### Verifiability
All changes can be confirmed against template structure.

---

## Example Workflow

### Issue Found
```markdown
Issue: Incorrect file paths in developing-cast/resources/quick-reference.md
Location: Lines 246-257
Pattern: Missing `modules/` in all paths
Severity: CRITICAL
```

### Implementation
```python
# Read current content
Read "act_operator/.../quick-reference.md"

# Fix paths
Edit "act_operator/.../quick-reference.md"
  old: "| State schema | `casts/[cast]/state.py` |"
  new: "| State schema | `casts/[cast]/modules/state.py` |"

Edit "act_operator/.../quick-reference.md"
  old: "| Nodes | `casts/[cast]/nodes.py` |"
  new: "| Nodes | `casts/[cast]/modules/nodes.py` |"

# Verify
Read "act_operator/.../quick-reference.md"  # Check changes
```

### Verification
```markdown
✓ All paths now include modules/
✓ Matches template structure
✓ No broken references
✓ Consistent with other resources
```

---

Begin the comprehensive improvement process. Work through all five phases systematically, making actual improvements to the skills documentation.

Focus on:
1. **Accuracy** - Fix all incorrect information
2. **Efficiency** - Remove redundancy and verbosity
3. **Organization** - Restructure for optimal usability
4. **Completeness** - Address all issues found
5. **Quality** - Ensure every change improves the skills
