# Act Operator Skills - Comprehensive Feedback Report

**Date:** 2025-01-19
**Analyzer:** Claude Sonnet 4.5
**Purpose:** Detailed analysis and improvement recommendations for all Claude skills in Act Operator

---

## Executive Summary

This report provides a comprehensive analysis of all skills in `act_operator/scaffold/{{ cookiecutter.act_slug }}/.claude/skills`. **Critical structural inconsistencies** were found across multiple skills, particularly regarding the Act project directory structure. Many resources contain incorrect file paths, unnecessary content, duplicate information, and unclear instructions that will cause Claude to implement code incorrectly.

### Skills Analyzed
1. **architecting-act** - 6 resource files + SKILL.md
2. **developing-cast** - 17+ resource files + SKILL.md
3. **engineering-act** - 3 resource files + SKILL.md
4. **testing-cast** - 9+ resource files + SKILL.md

---

## CRITICAL ISSUE #1: Project Structure Inconsistency

### The Problem
**Multiple skills teach INCORRECT project structure.** This is the most serious issue affecting:
- `developing-cast/resources/project/act-conventions.md`
- `developing-cast/resources/quick-reference.md`
- `developing-cast/resources/project/from-architecture-to-code.md`
- Multiple other developing-cast resources

### Incorrect Structure (Currently in Skills)
```
casts/my_cast/
├── graph.py
├── state.py          # ❌ WRONG LOCATION
├── nodes.py          # ❌ WRONG LOCATION
├── conditions.py     # ❌ WRONG LOCATION
└── tools.py          # ❌ WRONG LOCATION
```

### Correct Structure (Actual Project)
```
{{ cookiecutter.act_slug }}/
├── casts/
│   ├── base_node.py
│   ├── base_graph.py
│   └── {{ cookiecutter.cast_snake }}/
│       ├── __init__.py
│       ├── graph.py              # ✅ CORRECT
│       ├── pyproject.toml
│       ├── README.md
│       └── modules/              # ✅ ALL modules go here
│           ├── __init__.py
│           ├── state.py          # ✅ CORRECT LOCATION
│           ├── nodes.py          # ✅ CORRECT LOCATION
│           ├── conditions.py     # ✅ CORRECT LOCATION (optional)
│           ├── agents.py         # ✅ CORRECT LOCATION (optional)
│           ├── middlewares.py    # ✅ CORRECT LOCATION (optional)
│           ├── models.py         # ✅ CORRECT LOCATION (optional)
│           ├── prompts.py        # ✅ CORRECT LOCATION (optional)
│           ├── tools.py          # ✅ CORRECT LOCATION (optional)
│           └── utils.py          # ✅ CORRECT LOCATION (optional)
├── modules/
│   └── tools/                    # ⚠️ GLOBAL tools (reusable across casts)
├── langgraph.json
├── pyproject.toml
└── README.md
```

### Evidence
- Verified in: `act_operator/scaffold/{{ cookiecutter.act_slug }}/casts/{{ cookiecutter.cast_snake }}/modules/`
- Confirmed by: `engineering-act/resources/cast-structure.md` (which has it CORRECT)
- Contradicted by: Most `developing-cast` resources

### Required Changes
**ALL developing-cast resources must be updated to use:**
- `modules/state.py` instead of `state.py`
- `modules/nodes.py` instead of `nodes.py`
- `modules/conditions.py` instead of `conditions.py`
- Import paths must change: `from .modules.state import MyCastState`

---

## CRITICAL ISSUE #2: Tools Location Confusion

### The Problem
Skills are inconsistent about where tools should be located.

### Two Distinct Locations
1. **Cast-specific tools**: `casts/[cast]/modules/tools.py` (NEW, correct per cast-structure.md)
2. **Global reusable tools**: `modules/tools/` (for tools shared across multiple casts)

### Current Skill Guidance is Inconsistent
- `developing-cast/resources/project/act-conventions.md` says: **"ALL tools MUST live in: `modules/tools/`"** (global only)
- `engineering-act/resources/cast-structure.md` says: tools can be in **`modules/tools.py`** (cast-specific)

### Required Clarification
Skills must clearly distinguish:
- **Cast-specific tools** → `casts/[cast]/modules/tools.py`
- **Shared/reusable tools** → `modules/tools/[category]_tools.py`

---

## ISSUE #3: Incorrect File Path References

### developing-cast/resources/quick-reference.md

**Lines 246-257** - File Locations Cheatsheet is INCORRECT:

```markdown
| What | Where |
|------|-------|
| State schema | `casts/[cast]/state.py` |          # ❌ Should be modules/state.py
| Nodes | `casts/[cast]/nodes.py` |                # ❌ Should be modules/nodes.py
| Graph | `casts/[cast]/graph.py` |                # ✅ Correct
| Routing functions | `casts/[cast]/conditions.py` |  # ❌ Should be modules/conditions.py
| **Tools** | **`modules/tools/`** ⚠️ |             # ⚠️ Ambiguous (global vs cast)
| API clients | `modules/clients/` |                 # ✅ Correct
```

**Required Fix:**
```markdown
| What | Where |
|------|-------|
| State schema | `casts/[cast]/modules/state.py` |
| Nodes | `casts/[cast]/modules/nodes.py` |
| Graph | `casts/[cast]/graph.py` |
| Routing functions | `casts/[cast]/modules/conditions.py` (optional) |
| Cast-specific tools | `casts/[cast]/modules/tools.py` (optional) |
| Shared tools | `modules/tools/[category]_tools.py` |
| API clients | `modules/clients/` |
| Base classes | `casts/base_node.py`, `casts/base_graph.py` |
```

### developing-cast/resources/project/from-architecture-to-code.md

All file path examples are incorrect (using old structure without `modules/`).

**Example - Lines 56-68:**
```python
# casts/research_cast/state.py  # ❌ WRONG PATH
```

**Should be:**
```python
# casts/research_cast/modules/state.py  # ✅ CORRECT PATH
```

### Multiple Other Files
The same incorrect paths appear in:
- `developing-cast/resources/core/state-management.md` (line 108)
- `developing-cast/resources/core/implementing-nodes.md` (line 172)
- `developing-cast/resources/core/edge-patterns.md` (line 139)
- `developing-cast/resources/core/tools-integration.md` (lines 173, 193)
- `developing-cast/resources/project/act-conventions.md` (entire file structure)

---

## ISSUE #4: Incorrect Import Patterns

### Problem
Import examples don't reflect the `modules/` structure.

### Current (INCORRECT):
```python
# In casts/my_cast/graph.py
from .state import MyCastState      # ❌ WRONG
from .nodes import Node1, Node2     # ❌ WRONG
from .conditions import should_continue  # ❌ WRONG
```

### Correct:
```python
# In casts/my_cast/graph.py
from .modules.state import MyCastState         # ✅ CORRECT
from .modules.nodes import Node1, Node2        # ✅ CORRECT
from .modules.conditions import should_continue  # ✅ CORRECT
```

### Files Affected:
- All code examples in `developing-cast/resources/`
- Templates in `developing-cast/resources/project/act-conventions.md`

---

## ISSUE #5: Node Naming Convention Error

### architecting-act/resources/anti-patterns.md

**Lines 35-37:**
```markdown
### ❌ Generic Names
**Problem:** Nodes named `process`, `handle`, `manage`
**Solution:** Use specific verb-based names: `extract_key_info`, `validate_response`
```

### The Problem
**This is INCORRECT** for Act projects. Nodes are classes in Python (extending BaseNode), therefore they MUST follow:
- **PascalCase naming** (class convention)
- **Noun-based names** (class convention)

### Correct Guidance:
```markdown
### ❌ Generic Names
**Problem:** Node classes named `ProcessNode`, `HandleNode`, `ManageNode`
**Solution:** Use specific descriptive names: `KeyInfoExtractorNode`, `ResponseValidatorNode`

### ❌ Wrong Case
**Problem:** Node classes using snake_case: `extract_key_info`, `validate_response`
**Solution:** Use PascalCase for class names: `KeyInfoExtractorNode`, `ResponseValidatorNode`
```

**Note:** The class name should describe **what the node is** (noun), not **what it does** (verb).

---

## ISSUE #6: Unnecessary/Irrelevant Content

### developing-cast/resources/advanced/streaming.md

**Purpose of this file:** Show how to IMPLEMENT streaming in graphs you're BUILDING

**Problem:** Large sections show how to USE/CONSUME a graph's stream (lines 181-240):
- WebSocket patterns (lines 182-193)
- Server-Sent Events patterns (lines 195-206)
- Progress bar usage (lines 208-220)
- Token display (lines 222-240)

**Why this is wrong:**
- Act Project is for **building** LangGraph casts (graphs), not for **using/deploying** them
- Users will deploy graphs to LangGraph Cloud or other platforms
- The deployment/usage layer is outside the scope of Act Project
- These patterns are for **application developers consuming graphs**, not **graph developers building graphs**

**What should remain:**
- How to emit custom events from nodes (for debugging/observability)
- Stream modes overview (understanding what downstream users will receive)
- Streaming with interrupts (relevant for graph development)

**What should be removed:**
- All production deployment patterns (WebSocket, SSE, etc.)
- UI integration examples
- Consumer-side streaming code

### Justification
```markdown
Act Project Purpose:
├─ Build graphs (StateGraph, nodes, edges) → IN SCOPE
├─ Test graphs → IN SCOPE
├─ Debug graphs → IN SCOPE
└─ Deploy/use graphs → OUT OF SCOPE (handled by LangGraph Cloud or custom deployments)
```

---

## ISSUE #7: Duplicate and Redundant Content

### engineering-act/resources/uv-commands.md

**Lines 72-81:**
```bash
### Fresh Environment Setup
```bash
uv sync --all-packages      # Sync all groups
```

### After Editing pyproject.toml
```bash
# Sync environment (lockfile updated automatically by GitHub Actions)
uv sync --all-packages
```
```

**Problem:** Same command (`uv sync --all-packages`) shown twice with no meaningful difference.

**Solution:** Consolidate:
```bash
### Environment Synchronization

Use this command when:
- Setting up a fresh development environment
- After editing pyproject.toml
- After git pull with dependency changes

```bash
uv sync --all-packages  # Installs all casts + dev dependencies
```
```

### engineering-act/resources/uv-commands.md

**Lines 94-100:**
```markdown
✓ `uv.lock` managed by GitHub Actions (commit changes from CI)
✓ Use `uvx` for one-off tool execution

❌ Don't manually edit `uv.lock` (use uv commands)
❌ Don't use `pip` directly in uv projects (use `uv run` if needed)
```

**Problem:** `uvx` and `pip` mentions are irrelevant to Act Project workflows:
- `uvx` is for running one-off tools (not part of Act development)
- Users won't use `pip` directly (uv handles everything)
- `uv.lock` is managed by CI (developers don't interact with it)

**These are generic uv tips, not Act-specific guidance.**

**Solution:** Remove or move to a general "UV Background" section with clear disclaimer that these aren't typically needed in Act development.

---

## ISSUE #8: Verbose and Unclear Instructions

### Multiple Files Contain Token-Wasting Explanatory Text

Examples of unnecessary verbosity:

#### act-conventions.md - Lines 68-92
```markdown
### 1. Tools Location

⚠️ **MUST:** All tools in `modules/tools/`
❌ **NEVER:** Tools in `casts/[cast_name]/tools.py`

**Why:** Tools should be reusable across multiple casts.

```python
# ✅ CORRECT
# modules/tools/search_tools.py
from langchain_core.tools import tool

@tool
def web_search(query: str) -> str:
    """Search the web."""
    ...
```

```python
# ❌ WRONG
# casts/my_cast/tools.py
```
```

**Problem:** The "Why:" explanation and empty ❌ example waste tokens without adding value. Claude doesn't need to understand "why", just "what" to do.

**Better (concise):**
```markdown
### 1. Tools Location

Cast-specific tools: `casts/[cast]/modules/tools.py`
Shared tools: `modules/tools/[category]_tools.py`

Example:
```python
# modules/tools/search_tools.py
from langchain_core.tools import tool

@tool
def web_search(query: str) -> str:
    """Search the web."""
    return perform_search(query)
```
```

### Principle for Skills
Skills are **reference documentation for execution**, not **educational tutorials**. Remove:
- Philosophical explanations ("Why this matters:")
- Step-by-step thought processes
- Redundant examples
- Marketing language ("powerful", "robust", "elegant")

Keep:
- Direct instructions
- Code examples
- Decision trees
- Exact paths and patterns

---

## ISSUE #9: Ambiguous Implementation Guidance

### developing-cast/resources/advanced/subgraphs.md

**Lines 55-91 - State transformation example:**

```python
# Parent state
class ParentState(TypedDict):
    input: str
    result: dict

# Subgraph state
class SubgraphState(TypedDict):
    query: str
    data: list[dict]

# Transform function
from casts.base_node import BaseNode

class SubgraphWrapperNode(BaseNode):
    def __init__(self, subgraph, **kwargs):
        super().__init__(**kwargs)
        self.subgraph = subgraph

    def execute(self, state: ParentState) -> dict:
        # Transform parent state to subgraph state
        sub_input = {"query": state["input"], "data": []}

        # Invoke subgraph
        sub_result = self.subgraph.invoke(sub_input)

        # Transform subgraph result back to parent state
        return {"result": sub_result}

# Add to parent graph
wrapper = SubgraphWrapperNode(compiled_subgraph)
parent_builder.add_node("process_subgraph", wrapper)
```

**Problem:** Code shows everything in one place, but Act Project requires:
- State schemas in `modules/state.py`
- Node classes in `modules/nodes.py`
- Graph building in `graph.py`

**Claude might implement all of this in a single file**, violating Act conventions.

**Required Fix:** Explicitly show file separation:
```python
# casts/parent_cast/modules/state.py
class ParentState(TypedDict):
    input: str
    result: dict

# casts/subgraph_cast/modules/state.py
class SubgraphState(TypedDict):
    query: str
    data: list[dict]

# casts/parent_cast/modules/nodes.py
from casts.base_node import BaseNode

class SubgraphWrapperNode(BaseNode):
    def __init__(self, subgraph, **kwargs):
        super().__init__(**kwargs)
        self.subgraph = subgraph

    def execute(self, state: dict) -> dict:
        # Transform and invoke subgraph
        sub_input = {"query": state["input"], "data": []}
        sub_result = self.subgraph.invoke(sub_input)
        return {"result": sub_result}

# casts/parent_cast/graph.py
from .modules.state import ParentState
from .modules.nodes import SubgraphWrapperNode
from casts.subgraph_cast.graph import SubgraphCastGraph

class ParentCastGraph(BaseGraph):
    def build(self):
        builder = StateGraph(ParentState)

        # Compile subgraph
        subgraph = SubgraphCastGraph().build()
        wrapper = SubgraphWrapperNode(subgraph)

        builder.add_node("process_subgraph", wrapper)
        # ... rest of graph
        return builder.compile()
```

**This issue affects:**
- All multi-file code examples in `developing-cast/resources/`
- Examples showing state + nodes + graph together

---

## ISSUE #10: Missing Resource Depth Limit Enforcement

### Current State
Some resources reference other resources, creating multi-level depth:
- `SKILL.md` → `resource1.md` → `resource2.md` → `resource3.md`

### User Requirement (Case 4)
> "모든 리소스는 오로지 **SKILL.md에서 한 단계 깊이의 참조를 유지해야 한다**. 모든 참조 파일은 Claude가 필요할 때 전체 파일을 읽을 수 있도록 SKILL.md에서 직접 링크해야 한다. 리소스에서 다른 리소스를 참조하는 경우는 없어야 한다."

### Problem Files
While most resources follow this correctly, some resources contain cross-references:
- `state-management.md` references `implementing-nodes.md` and `graph-compilation.md`
- `implementing-nodes.md` references `state-management.md` and `tools-integration.md`
- Many "See also" sections create resource-to-resource links

### Required Pattern
**Allowed:**
```markdown
# SKILL.md
- Read: resources/core/state-management.md
- Read: resources/core/implementing-nodes.md
```

**NOT Allowed:**
```markdown
# resources/core/implementing-nodes.md
See also: state-management.md  # ❌ Resource→Resource reference
```

### Solution
1. Remove all "See also:", "Related:", "References:" sections from resources
2. Ensure SKILL.md lists ALL resources clearly
3. Make each resource self-contained for its specific topic

---

## ISSUE #11: Incorrect Examples in Testing Skill

### testing-cast/SKILL.md - Test Organization

**Lines 191-205:**
```markdown
## Test Organization

**Note:** All paths use forward slashes (/) for cross-platform compatibility.

```
casts/my_cast/
├── nodes.py
├── graph.py
├── state.py              # ❌ WRONG LOCATIONS
└── tests/
    ├── conftest.py
    ├── test_nodes.py
    ├── test_graph.py
    └── test_state.py
```
```

**Problem:** Same incorrect structure (missing `modules/`).

**Correct:**
```
casts/my_cast/
├── graph.py
├── modules/
│   ├── nodes.py         # ✅ CORRECT
│   ├── state.py         # ✅ CORRECT
│   └── conditions.py    # ✅ CORRECT
└── tests/
    ├── conftest.py
    ├── test_nodes.py
    ├── test_graph.py
    └── test_state.py
```

---

## ISSUE #12: Inconsistent Terminology

### "nodes.py" vs "agents.py"

**engineering-act/resources/cast-structure.md** calls node file **`agents.py`**:
```python
**`modules/agents.py`**
- Node implementations extending BaseNode
```

**developing-cast** resources call it **`nodes.py`**:
```python
**`modules/nodes.py`**
- Node implementations
```

**Actual template:** Uses **`modules/nodes.py`** (verified in scaffold)

### Required Fix
- Standardize on `modules/nodes.py` everywhere
- Remove references to `agents.py` as the primary node file
- Clarify that `agents.py` is an optional alternative organization pattern

---

## Summary of Required Changes

### architecting-act
1. ✅ Fix node naming convention in `anti-patterns.md` (verb→noun, snake_case→PascalCase)

### developing-cast
1. ❌ **CRITICAL:** Update ALL resources with correct structure (`modules/` subdirectory)
2. ❌ **CRITICAL:** Fix all file path examples to use `modules/state.py`, `modules/nodes.py`, etc.
3. ❌ **CRITICAL:** Update all import examples to use `from .modules.state import ...`
4. ⚠️ Remove production/usage patterns from `streaming.md`
5. ⚠️ Clarify tools location (cast-specific vs global)
6. ⚠️ Fix `subgraphs.md` to show explicit file separation
7. ⚠️ Remove resource-to-resource cross-references
8. ⚠️ Reduce verbosity in examples

### engineering-act
1. ⚠️ Consolidate duplicate commands in `uv-commands.md`
2. ⚠️ Remove irrelevant uv tips
3. ✅ Fix terminology: use `nodes.py` not `agents.py` as primary

### testing-cast
1. ❌ **CRITICAL:** Fix test organization structure to show `modules/`

### All Skills
1. ❌ **CRITICAL:** Ensure consistency with actual project structure
2. ⚠️ Remove unnecessary explanatory text
3. ⚠️ Make all examples concise and actionable
4. ✅ Remove resource-to-resource references

---

## Verification Checklist

Before finalizing fixes, verify:
- [ ] All file paths match: `casts/[cast]/modules/[file].py`
- [ ] All imports use: `from .modules.[module] import ...`
- [ ] No references to `casts/[cast]/state.py` (without `modules/`)
- [ ] No references to `casts/[cast]/nodes.py` (without `modules/`)
- [ ] Tools location is clarified (cast vs global)
- [ ] Node naming follows PascalCase + noun pattern
- [ ] streaming.md focuses on graph development, not deployment
- [ ] No resource-to-resource references
- [ ] All examples show proper file separation
- [ ] Terminology is consistent (`nodes.py` everywhere)

---

## Impact Assessment

### High Impact (Must Fix)
- Project structure inconsistency → **Claude will create files in wrong locations**
- Import path errors → **Code won't run**
- Node naming convention error → **Non-Pythonic code**

### Medium Impact (Should Fix)
- Unnecessary streaming.md content → **Confusion about scope**
- Tools location ambiguity → **Potential misplacement**
- Duplicate content → **Wasted tokens**

### Low Impact (Nice to Fix)
- Verbose explanations → **Token efficiency**
- Resource cross-references → **Navigation efficiency**
- Terminology inconsistency → **Clarity**

---

## Conclusion

The skills contain valuable content but require **structural corrections** to align with the actual Act project architecture. The most critical issue is the widespread use of incorrect file paths and structure throughout the `developing-cast` skill resources. This will cause Claude to implement code in the wrong locations, breaking the entire project structure.

**Priority:** Fix all CRITICAL issues first (structure, paths, imports), then address other improvements.

**Estimated Effort:**
- High impact fixes: ~40-50 files to update
- Medium impact fixes: ~10-15 files
- Low impact improvements: Throughout all skills

**Next Steps:** Use the accompanying Claude prompt to systematically fix all identified issues.
