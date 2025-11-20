# Act Operator Skills - Comprehensive Analysis and Restructuring

Analyze and restructure all Claude skills in: `act_operator/act_operator/scaffold/{{ cookiecutter.act_slug }}/.claude/skills/`

---

## Act Project Structure

This is the complete and accurate project structure:

```
{{ cookiecutter.act_slug }}/
├── .claude/
│   └── skills/
│       ├── architecting-act/
│       ├── developing-cast/
│       ├── engineering-act/
│       └── testing-cast/
├── casts/
│   ├── __init__.py
│   ├── base_node.py
│   ├── base_graph.py
│   └── {{ cookiecutter.cast_snake }}/
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

### In modules/tools.py

```python
# casts/my_cast/modules/tools.py
from langchain_core.tools import tool
from .utils import helper_function  # Relative
```

---

## Test Structure

### Graph Tests

**Location:** `tests/cast_tests/{{ cookiecutter.cast_snake }}_test.py`

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

**Location:** `tests/node_tests/test_node.py`

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

## Analysis Methodology

### Phase 1: Discovery

Read all resources in each skill:
- Every `.md` file in `resources/`
- All scripts in `scripts/`
- All templates in `templates/`
- Note all file paths, import patterns, and structural examples

### Phase 2: Verification

For each code example:
- Verify file paths match scaffold structure
- Verify imports match correct patterns
- Check references to project structure
- Confirm test organization alignment

### Phase 3: Pattern Analysis

Within each skill:
- Identify duplicate content
- Identify contradictions
- Identify inefficiencies
- Identify gaps

Across skills:
- Check terminology consistency
- Check for overlaps
- Verify integration points

### Phase 4: Evaluation

For each resource:
- Accuracy against scaffold
- Completeness of coverage
- Organization efficiency
- Clarity of instructions

For each skill:
- Resource organization effectiveness
- Scope appropriateness
- Integration with other skills

### Phase 5: Recommendation

Document findings:
- Specific issues with locations
- Severity assessment
- Proposed solutions
- Restructuring proposals when needed

---

## Issue Categories to Investigate

### Structure References

Verify all file path examples:
- `casts/[cast]/modules/state.py` ✓
- `casts/[cast]/modules/nodes.py` ✓
- `casts/[cast]/modules/conditions.py` ✓

### Import Patterns

Check all import examples:
- graph.py uses absolute imports
- modules/*.py uses absolute for base classes
- modules/*.py uses relative for sibling modules

### Node Naming

Verify node examples:
- PascalCase class names
- Noun-based (what it IS)

### Test Organization

Check test references:
- `tests/cast_tests/` for graph tests
- `tests/node_tests/` for node tests
- Correct template file names

### Scope Alignment

Verify content is within Act Project scope:
- Building graphs ✓
- Testing graphs ✓
- Deploying graphs ✗ (out of scope)
- Using graphs ✗ (out of scope)

### Content Efficiency

Look for:
- Redundant explanations
- Duplicate examples
- Unnecessary verbosity
- Cross-references between resources

### Terminology Consistency

Check for consistent use of:
- nodes.py vs agents.py
- conditions.py vs routing functions
- Standard naming patterns

---

## Output Format

### Part 1: Issue Inventory

For each skill, document issues in this format:

```markdown
## [Skill Name]

### Issue: [Title]
**Files:** [Specific paths and lines]
**Severity:** CRITICAL | HIGH | MEDIUM | LOW
**Description:** [What's wrong]
**Correction:** [What it should be]
**Action:** [Specific fix needed]
```

### Part 2: Restructuring Proposals

When resource organization needs improvement:

```markdown
## [Skill Name] Restructuring

### Current Structure
[Current organization]

### Proposed Structure
[Improved organization]

### Rationale
[Why this improves effectiveness]

### Implementation
[How to migrate]
```

### Part 3: Priority Action Plan

```markdown
## Action Plan

### Phase 1: Critical Fixes
[CRITICAL severity issues - must fix first]

### Phase 2: High Priority
[HIGH severity issues - fix soon]

### Phase 3: Improvements
[MEDIUM/LOW severity - optimize]

### Phase 4: Restructuring
[Organizational improvements]
```

---

## Analysis Scope

Analyze these aspects comprehensively:

### Accuracy
- File paths match scaffold
- Import patterns match templates
- Structure examples are correct
- Code examples will run

### Completeness
- All necessary topics covered
- No critical gaps
- Appropriate depth

### Efficiency
- No unnecessary content
- Clear, concise instructions
- Minimal redundancy
- Self-contained resources

### Organization
- Logical resource grouping
- Appropriate depth (one level from SKILL.md)
- Easy navigation
- Clear scope

### Integration
- Consistent with other skills
- No contradictions
- Smooth handoffs between skills

---

## Quality Standards

### Precision
Every file path, import pattern, and code example must be verifiable against the scaffold.

### Completeness
Cover all resources thoroughly. Don't skip files or sections.

### Clarity
Issues must be specific with exact file locations and line numbers.

### Practicality
Recommendations must be implementable with clear action steps.

---

## Deliverables

1. **Complete Issue Inventory** - All issues found across all skills
2. **Restructuring Proposals** - Organizational improvements needed
3. **Priority Action Plan** - Phased implementation roadmap
4. **Verification Checklist** - How to confirm fixes are correct

---

Begin systematic analysis following the five phases. Focus on accuracy, completeness, and practical improvements.
