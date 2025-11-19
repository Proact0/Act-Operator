# Claude Prompt: Fix Act Operator Skills

You are tasked with fixing all Claude skills in the Act Operator project located at:
`act_operator/act_operator/scaffold/{{ cookiecutter.act_slug }}/.claude/skills/`

## Context

The skills contain critical structural errors that teach incorrect Act project architecture. You must systematically fix all resources to match the actual project structure.

## Actual Project Structure (CORRECT)

```
{{ cookiecutter.act_slug }}/                    # Root directory
├── casts/
│   ├── __init__.py
│   ├── base_node.py                             # Base classes (DO NOT MODIFY)
│   ├── base_graph.py                            # Base classes (DO NOT MODIFY)
│   └── {{ cookiecutter.cast_snake }}/           # Individual cast
│       ├── __init__.py
│       ├── graph.py                              # Graph definition
│       ├── pyproject.toml                        # Cast dependencies
│       ├── README.md
│       └── modules/                              # ⚠️ ALL implementation files go here
│           ├── __init__.py
│           ├── state.py                          # State schema (REQUIRED)
│           ├── nodes.py                          # Node implementations (REQUIRED)
│           ├── conditions.py                     # Routing functions (optional)
│           ├── agents.py                         # Alternative org pattern (optional)
│           ├── middlewares.py                    # Middleware functions (optional)
│           ├── models.py                         # LLM configs (optional)
│           ├── prompts.py                        # Prompt templates (optional)
│           ├── tools.py                          # Cast-specific tools (optional)
│           └── utils.py                          # Utility functions (optional)
├── modules/
│   ├── tools/                                    # Global/shared tools only
│   │   ├── search_tools.py
│   │   └── data_tools.py
│   ├── clients/                                  # API clients
│   └── utils/                                    # Global utilities
├── langgraph.json
├── pyproject.toml
└── README.md
```

## Critical Rules

### Rule 1: File Locations
**ALWAYS** use these paths:
- State: `casts/[cast]/modules/state.py` ✅
- Nodes: `casts/[cast]/modules/nodes.py` ✅
- Graph: `casts/[cast]/graph.py` ✅
- Conditions: `casts/[cast]/modules/conditions.py` ✅
- Cast-specific tools: `casts/[cast]/modules/tools.py` ✅
- Global tools: `modules/tools/[category]_tools.py` ✅

**NEVER** use:
- `casts/[cast]/state.py` ❌
- `casts/[cast]/nodes.py` ❌
- `casts/[cast]/conditions.py` ❌
- `casts/[cast]/tools.py` ❌

### Rule 2: Import Patterns
**ALWAYS** use:
```python
# In casts/my_cast/graph.py
from .modules.state import MyCastState
from .modules.nodes import Node1, Node2
from .modules.conditions import should_continue
```

**NEVER** use:
```python
# ❌ WRONG - missing modules/
from .state import MyCastState
from .nodes import Node1, Node2
```

### Rule 3: Node Naming
Nodes are Python classes, therefore:
- **ALWAYS** use PascalCase: `KeyExtractorNode`, `ResponseValidatorNode`
- **ALWAYS** use noun-based names (what it IS, not what it DOES)
- **NEVER** use snake_case: `extract_key`, `validate_response`
- **NEVER** use verb-based class names

### Rule 4: Tools Location Clarity
**Cast-specific tools** (used by one cast only):
```python
# casts/my_cast/modules/tools.py
from langchain_core.tools import tool

@tool
def my_specific_tool(query: str) -> str:
    """Tool used only by this cast."""
    return process(query)
```

**Global/shared tools** (used by multiple casts):
```python
# modules/tools/search_tools.py
from langchain_core.tools import tool

@tool
def web_search(query: str) -> str:
    """Shared web search tool."""
    return search_web(query)
```

## Tasks

### Task 1: Fix `architecting-act` Skill

**File:** `architecting-act/resources/anti-patterns.md`

**Change Required:**

Replace:
```markdown
### ❌ Generic Names
**Problem:** Nodes named `process`, `handle`, `manage`
**Solution:** Use specific verb-based names: `extract_key_info`, `validate_response`
```

With:
```markdown
### ❌ Generic Names
**Problem:** Node classes with vague names: `ProcessorNode`, `HandlerNode`, `ManagerNode`
**Solution:** Use descriptive noun-based names: `KeyInfoExtractorNode`, `ResponseValidatorNode`

**Remember:** Nodes are classes (PascalCase, noun-based), not functions.
```

---

### Task 2: Fix `developing-cast` Skill

This is the most extensive task. You must update ALL resources in `developing-cast/`.

#### Task 2.1: Fix `developing-cast/resources/quick-reference.md`

**Lines ~246-257** - Update File Locations Cheatsheet:

Replace entire table with:
```markdown
## File Locations Cheatsheet

| What | Where |
|------|-------|
| State schema | `casts/[cast]/modules/state.py` |
| Nodes | `casts/[cast]/modules/nodes.py` |
| Graph | `casts/[cast]/graph.py` |
| Routing functions | `casts/[cast]/modules/conditions.py` (optional) |
| Cast-specific tools | `casts/[cast]/modules/tools.py` (optional) |
| Global/shared tools | `modules/tools/[category]_tools.py` |
| API clients | `modules/clients/` |
| Base classes | `casts/base_node.py`, `casts/base_graph.py` |
```

#### Task 2.2: Fix `developing-cast/resources/project/act-conventions.md`

**Entire file structure section** - Update to show `modules/` subdirectory:

Replace the directory structure (lines ~27-67) with:
```markdown
## Directory Structure

```
act_project/
├── casts/
│   ├── base_node.py              # BaseNode and AsyncBaseNode (DO NOT MODIFY)
│   ├── base_graph.py             # BaseGraph (DO NOT MODIFY)
│   │
│   └── my_cast/                  # Your cast implementation
│       ├── __init__.py
│       ├── graph.py              # REQUIRED: Graph class inheriting BaseGraph
│       ├── pyproject.toml
│       ├── README.md
│       └── modules/              # ⚠️ ALL implementation files go here
│           ├── __init__.py
│           ├── state.py          # REQUIRED: State schema (TypedDict/Pydantic)
│           ├── nodes.py          # REQUIRED: Node classes
│           ├── conditions.py     # Routing functions for conditional edges (optional)
│           ├── agents.py         # Alternative node organization (optional)
│           ├── tools.py          # Cast-specific tools (optional)
│           ├── prompts.py        # Prompt templates (optional)
│           ├── middlewares.py    # Custom middleware (optional)
│           └── utils.py          # Utilities (optional)
│
├── modules/
│   ├── tools/                    # ⚠️ GLOBAL tools (shared across casts)
│   │   ├── search_tools.py
│   │   ├── data_tools.py
│   │   └── memory_tools.py
│   │
│   ├── clients/                  # Optional: API clients
│   │   └── example_api.py
│   │
│   └── utils/                    # Optional: Global utilities
│       └── helpers.py
│
└── config/                       # Optional: Configuration
    ├── mcp_config.yaml
    └── settings.py
```
```

Update all code examples to use `modules/`:
- Change `from .state import` → `from .modules.state import`
- Change `casts/my_cast/nodes.py` → `casts/my_cast/modules/nodes.py`
- Update all file path comments in code examples

#### Task 2.3: Fix `developing-cast/resources/project/from-architecture-to-code.md`

Update ALL file path comments in code examples:

**Example 1 - Lines ~56-68:**
Replace:
```python
# casts/research_cast/state.py
```

With:
```python
# casts/research_cast/modules/state.py
```

**Example 2 - Lines ~94-131:**
Replace:
```python
# casts/research_cast/nodes.py
```

With:
```python
# casts/research_cast/modules/nodes.py
```

**Example 3 - Lines ~149-164:**
Replace:
```python
# casts/research_cast/conditions.py
```

With:
```python
# casts/research_cast/modules/conditions.py
```

Apply this pattern to **ALL** code examples in the file.

#### Task 2.4: Fix `developing-cast/resources/core/state-management.md`

**Line ~108:**
Replace:
```python
# casts/my_cast/state.py
```

With:
```python
# casts/my_cast/modules/state.py
```

#### Task 2.5: Fix `developing-cast/resources/core/implementing-nodes.md`

**Line ~172:**
Replace:
```python
# casts/my_cast/nodes.py
```

With:
```python
# casts/my_cast/modules/nodes.py
```

#### Task 2.6: Fix `developing-cast/resources/core/edge-patterns.md`

**Line ~139 and ~165:**
Replace:
```python
# casts/my_cast/conditions.py
```

With:
```python
# casts/my_cast/modules/conditions.py
```

Update import examples to:
```python
from .modules.conditions import route_by_intent, should_continue_research
```

#### Task 2.7: Fix `developing-cast/resources/core/tools-integration.md`

**Line ~173:**
Update:
```markdown
## Act Project Convention

⚠️ **Two tool locations depending on scope:**

**Cast-specific tools (used only by this cast):**
```python
# casts/my_cast/modules/tools.py
from langchain_core.tools import tool

@tool
def my_cast_specific_tool(query: str) -> str:
    """Tool specific to this cast."""
    return process_cast_specific(query)
```

**Global/shared tools (used across multiple casts):**
```python
# modules/tools/search_tools.py
from langchain_core.tools import tool

@tool
def web_search(query: str) -> str:
    """Shared web search tool."""
    return search_web(query)
```

**Importing tools:**
```python
# In casts/my_cast/modules/nodes.py

# Import cast-specific tools
from .tools import my_cast_specific_tool

# Import global tools
from modules.tools.search_tools import web_search

# Use in node
tools = [my_cast_specific_tool, web_search]
```

#### Task 2.8: Fix `developing-cast/resources/core/graph-compilation.md`

**Line ~169:**
Replace:
```python
# casts/my_cast/graph.py
```

Add import examples showing modules:
```python
from .modules.state import MyCastState
from .modules.nodes import (
    InputNode,
    ProcessNode,
    OutputNode,
)
from .modules.conditions import should_continue, route_by_intent
```

#### Task 2.9: Remove Irrelevant Content from `developing-cast/resources/advanced/streaming.md`

**Delete lines ~181-280** (all production deployment patterns):
- WebSocket patterns
- Server-Sent Events
- Progress bars for end users
- Token-by-token display for UIs

**Keep only:**
- Stream modes overview (understanding for development)
- Custom event emission from nodes (for debugging)
- Streaming with interrupts

**Add note at top:**
```markdown
## Scope Note

This resource covers streaming **during graph development** (debugging, testing).

Production deployment patterns (WebSocket, SSE, UI integration) are **out of scope** for Act Project.
These are handled by your deployment platform (LangGraph Cloud, custom server, etc.).
```

#### Task 2.10: Fix `developing-cast/resources/advanced/subgraphs.md`

**Lines ~55-91** - Add explicit file separation:

Replace the unified example with:
```python
# File: casts/parent_cast/modules/state.py
from typing import TypedDict

class ParentState(TypedDict):
    input: str
    result: dict

# File: casts/subgraph_cast/modules/state.py
from typing import TypedDict

class SubgraphState(TypedDict):
    query: str
    data: list[dict]

# File: casts/subgraph_cast/modules/nodes.py
from casts.base_node import BaseNode

class SubgraphProcessorNode(BaseNode):
    def execute(self, state: dict) -> dict:
        # Process subgraph logic
        return {"data": processed_data}

# File: casts/subgraph_cast/graph.py
from langgraph.graph import StateGraph, START, END
from casts.base_graph import BaseGraph
from .modules.state import SubgraphState
from .modules.nodes import SubgraphProcessorNode

class SubgraphCastGraph(BaseGraph):
    def build(self):
        builder = StateGraph(SubgraphState)
        builder.add_node("processor", SubgraphProcessorNode())
        builder.add_edge(START, "processor")
        builder.add_edge("processor", END)
        return builder.compile()

# File: casts/parent_cast/modules/nodes.py
from casts.base_node import BaseNode

class SubgraphWrapperNode(BaseNode):
    def __init__(self, subgraph, **kwargs):
        super().__init__(**kwargs)
        self.subgraph = subgraph

    def execute(self, state: dict) -> dict:
        # Transform parent state to subgraph input
        sub_input = {"query": state["input"], "data": []}

        # Invoke subgraph
        sub_result = self.subgraph.invoke(sub_input)

        # Transform result back
        return {"result": sub_result}

# File: casts/parent_cast/graph.py
from langgraph.graph import StateGraph, START, END
from casts.base_graph import BaseGraph
from .modules.state import ParentState
from .modules.nodes import SubgraphWrapperNode
from casts.subgraph_cast.graph import SubgraphCastGraph

class ParentCastGraph(BaseGraph):
    def build(self):
        builder = StateGraph(ParentState)

        # Build and wrap subgraph
        subgraph = SubgraphCastGraph().build()
        wrapper = SubgraphWrapperNode(subgraph)

        builder.add_node("process_subgraph", wrapper)
        builder.add_edge(START, "process_subgraph")
        builder.add_edge("process_subgraph", END)

        return builder.compile()
```

**Lines ~179-194** - Update structure example:
Replace:
```markdown
## Act Project Structure

```
casts/
├── main_cast/
│   ├── graph.py          # Main orchestrator
│   ├── state.py
│   └── nodes.py
```

With:
```markdown
## Act Project Structure

```
casts/
├── main_cast/
│   ├── graph.py          # Main orchestrator
│   └── modules/
│       ├── state.py
│       ├── nodes.py
│       └── conditions.py
├── research_agent/       # Subgraph 1
│   ├── graph.py
│   └── modules/
│       ├── state.py
│       └── nodes.py
└── writing_agent/        # Subgraph 2
    ├── graph.py
    └── modules/
        ├── state.py
        └── nodes.py
```

#### Task 2.11: Remove Resource-to-Resource References

Search ALL developing-cast resources for:
- "See also:"
- "Related:"
- "References:"

**Remove or replace** these sections. Resources should be self-contained.

**Example:**
Replace:
```markdown
## References
- Related: `state-management.md`
- Related: `implementing-nodes.md`
```

With:
```markdown
<!-- No cross-references - all resources linked from SKILL.md -->
```

---

### Task 3: Fix `engineering-act` Skill

#### Task 3.1: Fix `engineering-act/resources/uv-commands.md`

**Lines 72-81** - Consolidate duplicate sections:

Replace:
```bash
### Fresh Environment Setup
```bash
uv sync --all-packages
```

### After Editing pyproject.toml
```bash
uv sync --all-packages
```
```

With:
```bash
### Environment Synchronization

Use when:
- Fresh environment setup
- After editing pyproject.toml
- After git pull with dependency changes

```bash
uv sync --all-packages
```
```

**Lines 94-100** - Remove irrelevant tips:

Delete:
```markdown
✓ Use `uvx` for one-off tool execution
❌ Don't use `pip` directly in uv projects (use `uv run` if needed)
```

These are generic uv features not relevant to Act workflows.

#### Task 3.2: Verify `engineering-act/resources/cast-structure.md`

This file has the CORRECT structure. Verify it matches the scaffold template structure exactly.

Confirm:
- Uses `modules/` subdirectory ✅
- Uses `modules/state.py` ✅
- Uses `modules/nodes.py` (or `agents.py` as alternative) ✅

**One terminology fix:**
Change primary reference from `agents.py` to `nodes.py` for consistency:

Replace:
```markdown
**`modules/agents.py`**
- Node implementations extending BaseNode
```

With:
```markdown
**`modules/nodes.py`**
- Node implementations extending BaseNode
- (Alternative: `modules/agents.py` for different organization)
```

---

### Task 4: Fix `testing-cast` Skill

#### Task 4.1: Fix `testing-cast/SKILL.md`

**Lines ~191-205** - Update test organization structure:

Replace:
```markdown
```
casts/my_cast/
├── nodes.py
├── graph.py
├── state.py
└── tests/
    ├── conftest.py
    ├── test_nodes.py
    ├── test_graph.py
    └── test_state.py
```
```

With:
```markdown
```
casts/my_cast/
├── graph.py
├── modules/
│   ├── nodes.py
│   ├── state.py
│   └── conditions.py
└── tests/
    ├── conftest.py
    ├── test_nodes.py
    ├── test_graph.py
    └── test_state.py
```
```

#### Task 4.2: Update all testing resource examples

Apply the same structure fix to ALL test examples in:
- `testing-cast/resources/core/testing-nodes.md`
- `testing-cast/resources/core/testing-graphs.md`
- `testing-cast/resources/core/testing-state.md`
- All other testing resources

---

## Execution Guidelines

### Approach
1. **Work systematically** through each task in order
2. **Verify each change** before moving to next
3. **Search thoroughly** for all instances of incorrect patterns
4. **Test critical examples** by checking they match the scaffold template

### Verification After Each File
Before marking a file as complete, verify:
- [ ] All file paths use `modules/` subdirectory
- [ ] All imports use `from .modules.[module] import ...`
- [ ] No `casts/[cast]/state.py` references
- [ ] No `casts/[cast]/nodes.py` references
- [ ] Tools location is clear (cast vs global)
- [ ] Code examples show file separation when needed
- [ ] No resource-to-resource cross-references

### Search Patterns to Find Issues
Use these patterns to find remaining issues:

```bash
# Find incorrect file paths
grep -r "casts/.*cast.*/state.py" .claude/skills/
grep -r "casts/.*cast.*/nodes.py" .claude/skills/
grep -r "casts/.*cast.*/conditions.py" .claude/skills/

# Find incorrect imports
grep -r "from .state import" .claude/skills/
grep -r "from .nodes import" .claude/skills/
grep -r "from .conditions import" .claude/skills/

# Find cross-references
grep -r "See also:" .claude/skills/
grep -r "Related:" .claude/skills/
grep -r "References:" .claude/skills/
```

### Final Verification
After completing all tasks, verify the entire skills directory:

1. **Structure test:** Read 5 random developing-cast resources → all should show `modules/`
2. **Import test:** Check all code examples use `from .modules.X import`
3. **Path test:** No mentions of `casts/[cast]/state.py` (without modules/)
4. **Cross-ref test:** No "See also" sections in resources (only in SKILL.md)

---

## Success Criteria

You have successfully completed this task when:

✅ **ALL** file paths in examples use `casts/[cast]/modules/[file].py`
✅ **ALL** import statements use `from .modules.[module] import`
✅ **ALL** node naming examples use PascalCase nouns
✅ **ZERO** references to flat structure (`casts/[cast]/nodes.py` without `modules/`)
✅ Tools location distinction is clear throughout
✅ streaming.md focuses on development, not deployment
✅ No duplicate or redundant command examples
✅ No resource-to-resource cross-references
✅ All multi-file examples show explicit file separation
✅ Terminology is consistent (`nodes.py` as primary, `agents.py` as alternative)

---

## Common Mistakes to Avoid

❌ **Don't** half-update files (e.g., fix some examples but miss others)
❌ **Don't** skip verification after each file
❌ **Don't** assume - always check the actual scaffold template
❌ **Don't** preserve cross-references between resources
❌ **Don't** leave ambiguous tool location guidance

✅ **Do** update ALL instances in each file
✅ **Do** verify against scaffold template structure
✅ **Do** make each resource self-contained
✅ **Do** ensure examples show file separation
✅ **Do** test critical import paths

---

## Questions?

If you encounter ambiguity:
1. **Check the scaffold template:** `act_operator/scaffold/{{ cookiecutter.act_slug }}/casts/{{ cookiecutter.cast_snake }}/`
2. **Refer to:** `engineering-act/resources/cast-structure.md` (this one is CORRECT)
3. **Verify:** Actual file locations in the scaffold match your understanding

---

## Output Format

After completing all tasks, provide:

1. **Summary of changes:** Count of files modified per skill
2. **Verification results:** Results of final verification tests
3. **Remaining issues:** Any patterns you couldn't resolve
4. **Commit message suggestion:** Clear description for git commit

Example output:
```markdown
## Completion Report

### Files Modified
- architecting-act: 1 file
- developing-cast: 25 files
- engineering-act: 2 files
- testing-cast: 3 files

### Verification
✅ All file paths use modules/
✅ All imports corrected
✅ No flat structure references
✅ Tools location clarified
✅ Cross-references removed

### Commit Message
```
fix(skills): correct Act project structure across all skills

- Update all file paths to use modules/ subdirectory
- Fix imports to use from .modules.X pattern
- Clarify cast-specific vs global tools location
- Remove production patterns from streaming.md
- Fix node naming convention in anti-patterns
- Remove resource cross-references
- Add explicit file separation in multi-file examples

Refs: SKILLS_FEEDBACK_REPORT.md
```
```

---

Begin with Task 1 and proceed systematically through all tasks.
