# From Architecture to Code

## Table of Contents

- [When to Use This Resource](#when-to-use-this-resource)
- [The Translation Process](#the-translation-process)
- [CLAUDE.md Structure](#claudemd-structure)
- [Step-by-Step Translation](#step-by-step-translation)
  - [Step 1: Create State Schema](#step-1-create-state-schema)
  - [Step 2: Create Node Classes](#step-2-create-node-classes)
  - [Step 3: Create Routing Functions](#step-3-create-routing-functions)
  - [Step 4: Build Graph](#step-4-build-graph)
  - [Step 5: Implement Tools (if specified)](#step-5-implement-tools-if-specified)
- [Decision Points During Translation](#decision-points-during-translation)
  - [When CLAUDE.md says "ReAct Pattern"](#when-claudemd-says-react-pattern)
  - [When CLAUDE.md says "Plan-Execute"](#when-claudemd-says-plan-execute)
  - [When CLAUDE.md says "Map-Reduce"](#when-claudemd-says-map-reduce)
  - [When CLAUDE.md mentions "Human Approval"](#when-claudemd-mentions-human-approval)
  - [When CLAUDE.md specifies "Persistent Memory"](#when-claudemd-specifies-persistent-memory)
- [Validation Checklist](#validation-checklist)
- [Example: Complete Translation](#example-complete-translation)
- [When Architecture Changes](#when-architecture-changes)
- [References](#references)

## When to Use This Resource
Read this when translating CLAUDE.md (from architecting-act) into actual implementation code.

## The Translation Process

**architecting-act** produces → **CLAUDE.md** (architecture spec)
**developing-cast** (this skill) translates → **Actual code**

## CLAUDE.md Structure

CLAUDE.md contains:
1. **Architecture Overview** - High-level pattern and purpose
2. **State Schema** - Fields, types, reducers
3. **Node Specifications** - What each node does
4. **Edge Routing** - Flow between nodes
5. **Subgraphs** (if applicable)
6. **Implementation Guidance**

## Step-by-Step Translation

### Step 1: Create State Schema

**From CLAUDE.md:**
```
State Schema:
- input: str - User's input query
- messages: list[dict] with add reducer - Conversation messages
- research_results: list[dict] with add reducer - Accumulated research
- final_report: str | None - Generated report
```

**To state.py:**
```python
# casts/research_cast/state.py
from typing import TypedDict, Annotated
from langgraph.graph import add

class ResearchCastState(TypedDict):
    """State for ResearchCast graph."""
    input: str
    messages: Annotated[list[dict], add]
    research_results: Annotated[list[dict], add]
    final_report: str | None
```

**See:** `../core/state-management.md`

### Step 2: Create Node Classes

**From CLAUDE.md:**
```
Nodes:
1. InputProcessor
   - Input: input
   - Output: processed_query, search_terms
   - Responsibility: Extract search terms from input

2. Researcher (async)
   - Input: search_terms
   - Output: research_results (appends)
   - Responsibility: Search web for each term

3. ReportGenerator
   - Input: research_results
   - Output: final_report
   - Responsibility: Generate final report from research
```

**To nodes.py:**
```python
# casts/research_cast/nodes.py
from casts.base_node import BaseNode, AsyncBaseNode

class InputProcessorNode(BaseNode):
    """Extracts search terms from user input."""

    def execute(self, state: dict) -> dict:
        input_text = state["input"]
        search_terms = extract_search_terms(input_text)

        return {
            "processed_query": input_text,
            "search_terms": search_terms
        }

class ResearcherNode(AsyncBaseNode):
    """Searches web for each search term."""

    async def execute(self, state: dict) -> dict:
        search_terms = state.get("search_terms", [])

        results = []
        for term in search_terms:
            data = await async_web_search(term)
            results.append({"term": term, "data": data})

        return {"research_results": results}

class ReportGeneratorNode(BaseNode):
    """Generates final report from research."""

    def execute(self, state: dict) -> dict:
        research = state.get("research_results", [])
        report = generate_report(research)

        return {"final_report": report}
```

**See:** `../core/implementing-nodes.md`

### Step 3: Create Routing Functions

**From CLAUDE.md:**
```
Edge Routing:
- START → input_processor
- input_processor → researcher
- researcher → check_quality
  - If quality_score > 0.8 → report_generator
  - If quality_score <= 0.8 and attempts < 3 → researcher (retry)
  - Otherwise → error_handler
```

**To conditions.py:**
```python
# casts/research_cast/conditions.py
from langgraph.graph import END

def check_quality(state: dict) -> str:
    """Determines if research quality is sufficient."""
    quality_score = state.get("quality_score", 0)
    attempts = state.get("research_attempts", 0)

    if quality_score > 0.8:
        return "report_generator"
    elif attempts < 3:
        return "researcher"  # Retry
    else:
        return "error_handler"
```

**See:** `../core/edge-patterns.md`

### Step 4: Build Graph

**From CLAUDE.md (synthesizing all parts):**

**To graph.py:**
```python
# casts/research_cast/graph.py
from langgraph.graph import StateGraph, START, END
from casts.base_graph import BaseGraph

from .state import ResearchCastState
from .nodes import InputProcessorNode, ResearcherNode, ReportGeneratorNode
from .conditions import check_quality

class ResearchCastGraph(BaseGraph):
    """Research agent graph."""

    def build(self):
        builder = StateGraph(ResearchCastState)

        # Instantiate nodes
        input_processor = InputProcessorNode()
        researcher = ResearcherNode()
        report_generator = ReportGeneratorNode()

        # Add nodes
        builder.add_node("input_processor", input_processor)
        builder.add_node("researcher", researcher)
        builder.add_node("report_generator", report_generator)

        # Add edges (from CLAUDE.md routing spec)
        builder.add_edge(START, "input_processor")
        builder.add_edge("input_processor", "researcher")

        builder.add_conditional_edges(
            "researcher",
            check_quality,
            {
                "report_generator": "report_generator",
                "researcher": "researcher",
                "error_handler": "error_handler"
            }
        )

        builder.add_edge("report_generator", END)

        return builder.compile()
```

**See:** `../core/graph-compilation.md`

### Step 5: Implement Tools (if specified)

**From CLAUDE.md:**
```
Tools Required:
- web_search: Search the web for information
- extract_entities: Extract named entities from text
```

**To modules/tools/:**
```python
# modules/tools/research_tools.py
from langchain_core.tools import tool

@tool
def web_search(query: str) -> list[dict]:
    """Search the web for information.

    Args:
        query: Search query string

    Returns:
        List of search results
    """
    # Implementation
    ...

@tool
def extract_entities(text: str) -> list[str]:
    """Extract named entities from text.

    Args:
        text: Input text

    Returns:
        List of entity names
    """
    # Implementation
    ...
```

**See:** `../core/tools-integration.md`

## Decision Points During Translation

### When CLAUDE.md says "ReAct Pattern"
→ **Implement:** Agent node with tools + conditional routing

**See:** `../core/tools-integration.md` for agent+tools pattern

### When CLAUDE.md says "Plan-Execute"
→ **Implement:** Planning node → Execution nodes → Review node

### When CLAUDE.md says "Map-Reduce"
→ **Implement:** Parallel nodes + aggregation node

**See:** `../advanced/subgraphs.md` if pattern suggests modularity

### When CLAUDE.md mentions "Human Approval"
→ **Implement:** Interrupts with checkpointer

**See:** `../advanced/interrupts-hitl.md`

### When CLAUDE.md specifies "Persistent Memory"
→ **Implement:** Checkpointer + Store

**See:** `../memory/checkpoints-persistence.md`, `../memory/cross-thread-memory.md`

## Validation Checklist

After translating CLAUDE.md to code:

✓ **State schema** matches CLAUDE.md specification
✓ **All nodes** from architecture are implemented
✓ **Node responsibilities** match CLAUDE.md descriptions
✓ **Edge routing** follows CLAUDE.md flow diagram
✓ **Tools** (if any) are in `modules/tools/`
✓ **Conditional logic** implements decision points
✓ **Error handling** covers failure scenarios
✓ **Memory/persistence** configured as specified

## Example: Complete Translation

**CLAUDE.md snippet:**
```
Architecture: Simple sequential pipeline

State:
- input: str
- processed: bool
- result: str

Nodes:
1. ValidateInput: Check input validity
2. ProcessData: Transform input
3. FormatOutput: Format result

Flow:
START → ValidateInput → ProcessData → FormatOutput → END
```

**Complete implementation:**

```python
# state.py
from typing import TypedDict

class PipelineState(TypedDict):
    input: str
    processed: bool
    result: str

# nodes.py
from casts.base_node import BaseNode

class ValidateInputNode(BaseNode):
    def execute(self, state: dict) -> dict:
        if not state.get("input"):
            return {"error": "No input"}
        return {"processed": False}

class ProcessDataNode(BaseNode):
    def execute(self, state: dict) -> dict:
        transformed = transform(state["input"])
        return {"processed": True, "result": transformed}

class FormatOutputNode(BaseNode):
    def execute(self, state: dict) -> dict:
        formatted = format_result(state["result"])
        return {"result": formatted}

# graph.py
from langgraph.graph import StateGraph, START, END
from casts.base_graph import BaseGraph

from .state import PipelineState
from .nodes import ValidateInputNode, ProcessDataNode, FormatOutputNode

class PipelineGraph(BaseGraph):
    def build(self):
        builder = StateGraph(PipelineState)

        builder.add_node("validate", ValidateInputNode())
        builder.add_node("process", ProcessDataNode())
        builder.add_node("format", FormatOutputNode())

        builder.add_edge(START, "validate")
        builder.add_edge("validate", "process")
        builder.add_edge("process", "format")
        builder.add_edge("format", END)

        return builder.compile()
```

## When Architecture Changes

If CLAUDE.md is updated:
1. Review changed sections
2. Update corresponding code files
3. Test changes
4. Ensure edge routing still makes sense

## References
- All core resources for implementation details
- Related: architecting-act skill (creates CLAUDE.md)
- Related: testing-cast skill (tests the implementation)
