# Edge Types in LangGraph

Comprehensive guide to edge types and patterns in LangGraph.

## Table of Contents

1. [Introduction](#introduction)
2. [Simple Edges](#simple-edges)
   - [Basic Usage](#basic-usage)
   - [Entry and Exit Edges](#entry-and-exit-edges)
   - [Sequential Chains](#sequential-chains)
3. [Conditional Edges](#conditional-edges)
   - [Basic Conditional Routing](#basic-conditional-routing)
   - [Routing Functions](#routing-functions)
   - [Path Mapping](#path-mapping)
   - [Multiple Conditions](#multiple-conditions)
4. [Dynamic Routing](#dynamic-routing)
   - [State-Based Routing](#state-based-routing)
   - [Runtime Decisions](#runtime-decisions)
   - [Complex Routing Logic](#complex-routing-logic)
5. [Special Edge Cases](#special-edge-cases)
   - [START Node](#start-node)
   - [END Node](#end-node)
   - [Self-Loops](#self-loops)
   - [Multiple Edges from Node](#multiple-edges-from-node)
6. [Edge Patterns](#edge-patterns)
   - [Fan-Out Pattern](#fan-out-pattern)
   - [Fan-In Pattern](#fan-in-pattern)
   - [Loop Pattern](#loop-pattern)
   - [Branch-Merge Pattern](#branch-merge-pattern)
7. [Advanced Routing](#advanced-routing)
   - [Multi-Level Routing](#multi-level-routing)
   - [Priority-Based Routing](#priority-based-routing)
   - [Fallback Routing](#fallback-routing)
   - [Parallel Conditional Routing](#parallel-conditional-routing)
8. [Edge Configuration](#edge-configuration)
   - [Edge Metadata](#edge-metadata)
   - [Edge Conditions](#edge-conditions)
   - [Edge Priorities](#edge-priorities)
9. [Best Practices](#best-practices)
10. [Common Patterns](#common-patterns)
11. [Troubleshooting](#troubleshooting)
12. [Examples](#examples)

---

## Introduction

Edges define the flow of execution in LangGraph. They connect nodes and determine how state flows through your graph.

**Edge types:**
- **Simple edges**: Direct node-to-node connections
- **Conditional edges**: Branch based on state conditions
- **Dynamic routing**: Programmatic path selection

**Key concepts:**
- Edges are directional (from source to target)
- Multiple edges can originate from one node
- Conditional edges use routing functions
- START and END are special nodes

---

## Simple Edges

### Basic Usage

Direct connection between two nodes:

```python
from langgraph.graph import StateGraph, START, END
from dataclasses import dataclass

@dataclass(kw_only=True)
class State:
    input: str
    output: str = None

def build_graph():
    builder = StateGraph(State)

    # Add nodes
    builder.add_node("process", ProcessNode())
    builder.add_node("finalize", FinalizeNode())

    # Add simple edges
    builder.add_edge(START, "process")
    builder.add_edge("process", "finalize")
    builder.add_edge("finalize", END)

    return builder.compile()
```

**Characteristics:**
- Always follows the same path
- No conditional logic
- Deterministic flow
- Predictable execution

### Entry and Exit Edges

Connect to START and END:

```python
def build_graph():
    builder = StateGraph(State)

    builder.add_node("entry", EntryNode())
    builder.add_node("process", ProcessNode())
    builder.add_node("exit", ExitNode())

    # Entry edge - from START
    builder.add_edge(START, "entry")

    # Internal edges
    builder.add_edge("entry", "process")
    builder.add_edge("process", "exit")

    # Exit edge - to END
    builder.add_edge("exit", END)

    return builder.compile()
```

**Rules:**
- Every graph needs at least one edge from START
- Every path must eventually reach END
- START has no incoming edges
- END has no outgoing edges

### Sequential Chains

Linear sequence of nodes:

```python
def build_pipeline():
    """Linear data pipeline."""
    builder = StateGraph(State)

    # Pipeline steps
    builder.add_node("fetch", FetchNode())
    builder.add_node("parse", ParseNode())
    builder.add_node("clean", CleanNode())
    builder.add_node("transform", TransformNode())
    builder.add_node("save", SaveNode())

    # Sequential edges
    builder.add_edge(START, "fetch")
    builder.add_edge("fetch", "parse")
    builder.add_edge("parse", "clean")
    builder.add_edge("clean", "transform")
    builder.add_edge("transform", "save")
    builder.add_edge("save", END)

    return builder.compile()
```

**Use cases:**
- ETL pipelines
- Data processing workflows
- Step-by-step procedures
- Linear transformations

---

## Conditional Edges

### Basic Conditional Routing

Branch based on state:

```python
def route_by_status(state):
    """Route based on status field."""
    if state.status == "success":
        return "success"
    else:
        return "error"

def build_graph():
    builder = StateGraph(State)

    builder.add_node("process", ProcessNode())
    builder.add_node("success", SuccessNode())
    builder.add_node("error", ErrorNode())

    builder.add_edge(START, "process")

    # Conditional edge
    builder.add_conditional_edges(
        "process",           # Source node
        route_by_status,     # Routing function
        {
            "success": "success",  # Path mapping
            "error": "error"
        }
    )

    builder.add_edge("success", END)
    builder.add_edge("error", END)

    return builder.compile()
```

**Components:**
1. **Source node**: Where to route from
2. **Routing function**: Returns route key
3. **Path mapping**: Maps keys to target nodes

### Routing Functions

Functions that determine paths:

```python
def simple_route(state):
    """Simple boolean routing."""
    return "yes" if state.condition else "no"

def multi_route(state):
    """Multiple path routing."""
    score = state.score

    if score > 90:
        return "excellent"
    elif score > 70:
        return "good"
    elif score > 50:
        return "fair"
    else:
        return "poor"

def complex_route(state):
    """Complex routing logic."""
    # Check multiple conditions
    if state.error:
        return "error"

    if state.retry_count > 3:
        return "max_retries"

    if not state.validated:
        return "validate"

    return "continue"

# With state inspection
def inspect_route(state):
    """Route based on multiple state fields."""
    if hasattr(state, "messages"):
        last_message = state.messages[-1]
        if hasattr(last_message, "tool_calls"):
            if last_message.tool_calls:
                return "tools"

    return "end"
```

**Rules:**
- Must return string (route key)
- Must be deterministic
- Should be pure function (no side effects)
- Receives full state object

### Path Mapping

Map route keys to nodes:

```python
def build_graph():
    builder = StateGraph(State)

    builder.add_node("check", CheckNode())
    builder.add_node("path_a", PathANode())
    builder.add_node("path_b", PathBNode())
    builder.add_node("path_c", PathCNode())

    builder.add_edge(START, "check")

    # Path mapping
    builder.add_conditional_edges(
        "check",
        route_function,
        {
            "a": "path_a",       # Route key -> node name
            "b": "path_b",
            "c": "path_c",
            "end": END           # Can route directly to END
        }
    )

    builder.add_edge("path_a", END)
    builder.add_edge("path_b", END)
    builder.add_edge("path_c", END)

    return builder.compile()
```

**Notes:**
- Keys must match routing function returns
- Can map to END directly
- All possible return values should be mapped
- Missing mappings cause runtime errors

### Multiple Conditions

Multiple conditional edges from same node:

```python
def primary_route(state):
    """Primary routing logic."""
    if state.type == "query":
        return "search"
    return "process"

def secondary_route(state):
    """Secondary routing (after processing)."""
    if state.needs_review:
        return "review"
    return "finalize"

def build_graph():
    builder = StateGraph(State)

    builder.add_node("classify", ClassifyNode())
    builder.add_node("search", SearchNode())
    builder.add_node("process", ProcessNode())
    builder.add_node("review", ReviewNode())
    builder.add_node("finalize", FinalizeNode())

    builder.add_edge(START, "classify")

    # First conditional edge
    builder.add_conditional_edges(
        "classify",
        primary_route,
        {
            "search": "search",
            "process": "process"
        }
    )

    # Converge at process
    builder.add_edge("search", "process")

    # Second conditional edge
    builder.add_conditional_edges(
        "process",
        secondary_route,
        {
            "review": "review",
            "finalize": "finalize"
        }
    )

    builder.add_edge("review", "finalize")
    builder.add_edge("finalize", END)

    return builder.compile()
```

---

## Dynamic Routing

### State-Based Routing

Route based on state fields:

```python
@dataclass(kw_only=True)
class State:
    query: str
    query_type: str = None
    complexity: str = None
    result: str = None

def route_by_query_type(state):
    """Route based on classified query type."""
    query_type = state.query_type

    if query_type == "factual":
        return "knowledge_base"
    elif query_type == "analytical":
        return "analysis"
    elif query_type == "creative":
        return "generation"
    else:
        return "default"

def route_by_complexity(state):
    """Route based on complexity assessment."""
    complexity = state.complexity

    if complexity == "simple":
        return "quick_answer"
    elif complexity == "moderate":
        return "standard_process"
    else:
        return "deep_analysis"

def build_graph():
    builder = StateGraph(State)

    # Classification node sets query_type
    builder.add_node("classify", ClassifyNode())

    # Handler nodes
    builder.add_node("knowledge_base", KnowledgeNode())
    builder.add_node("analysis", AnalysisNode())
    builder.add_node("generation", GenerationNode())
    builder.add_node("default", DefaultNode())

    builder.add_edge(START, "classify")

    # Route based on classification
    builder.add_conditional_edges(
        "classify",
        route_by_query_type,
        {
            "knowledge_base": "knowledge_base",
            "analysis": "analysis",
            "generation": "generation",
            "default": "default"
        }
    )

    # All paths converge
    builder.add_edge("knowledge_base", END)
    builder.add_edge("analysis", END)
    builder.add_edge("generation", END)
    builder.add_edge("default", END)

    return builder.compile()
```

### Runtime Decisions

Route based on runtime conditions:

```python
def route_by_runtime(state):
    """Route based on runtime conditions."""
    import datetime

    # Time-based routing
    hour = datetime.datetime.now().hour
    if 0 <= hour < 6:
        return "off_hours"

    # Load-based routing
    if state.get("high_load"):
        return "queued"

    # Feature flag routing
    if state.get("beta_enabled"):
        return "beta_handler"

    return "standard"

def build_graph():
    builder = StateGraph(State)

    builder.add_node("check", CheckNode())
    builder.add_node("off_hours", OffHoursNode())
    builder.add_node("queued", QueuedNode())
    builder.add_node("beta_handler", BetaNode())
    builder.add_node("standard", StandardNode())

    builder.add_edge(START, "check")

    builder.add_conditional_edges(
        "check",
        route_by_runtime,
        {
            "off_hours": "off_hours",
            "queued": "queued",
            "beta_handler": "beta_handler",
            "standard": "standard"
        }
    )

    # All converge to END
    for node in ["off_hours", "queued", "beta_handler", "standard"]:
        builder.add_edge(node, END)

    return builder.compile()
```

### Complex Routing Logic

Multi-criteria routing:

```python
def complex_route(state):
    """Route based on multiple criteria."""
    # Priority 1: Error handling
    if state.error:
        if state.retry_count < 3:
            return "retry"
        else:
            return "error_handler"

    # Priority 2: Validation
    if not state.validated:
        return "validate"

    # Priority 3: Processing type
    if state.process_type == "batch":
        if state.batch_size > 1000:
            return "large_batch"
        else:
            return "small_batch"

    # Priority 4: User tier
    if state.user_tier == "premium":
        return "premium_handler"

    # Default
    return "standard"

def build_graph():
    builder = StateGraph(State)

    builder.add_node("process", ProcessNode())
    builder.add_node("retry", RetryNode())
    builder.add_node("error_handler", ErrorNode())
    builder.add_node("validate", ValidateNode())
    builder.add_node("large_batch", LargeBatchNode())
    builder.add_node("small_batch", SmallBatchNode())
    builder.add_node("premium_handler", PremiumNode())
    builder.add_node("standard", StandardNode())

    builder.add_edge(START, "process")

    builder.add_conditional_edges(
        "process",
        complex_route,
        {
            "retry": "retry",
            "error_handler": "error_handler",
            "validate": "validate",
            "large_batch": "large_batch",
            "small_batch": "small_batch",
            "premium_handler": "premium_handler",
            "standard": "standard"
        }
    )

    # Retry loops back
    builder.add_edge("retry", "process")

    # Others go to END
    for node in ["error_handler", "validate", "large_batch",
                  "small_batch", "premium_handler", "standard"]:
        builder.add_edge(node, END)

    return builder.compile()
```

---

## Special Edge Cases

### START Node

Entry point of graph:

```python
def build_graph():
    builder = StateGraph(State)

    builder.add_node("init", InitNode())

    # Simple entry
    builder.add_edge(START, "init")

    # Cannot have edges TO START
    # builder.add_edge("init", START)  # ❌ ERROR

    # Can have conditional entry
    builder.add_conditional_edges(
        START,
        lambda state: "init" if state.ready else "wait",
        {
            "init": "init",
            "wait": "wait"
        }
    )

    return builder.compile()
```

### END Node

Exit point of graph:

```python
def build_graph():
    builder = StateGraph(State)

    builder.add_node("process", ProcessNode())
    builder.add_node("finalize", FinalizeNode())

    builder.add_edge(START, "process")
    builder.add_edge("process", "finalize")

    # Simple exit
    builder.add_edge("finalize", END)

    # Conditional exit
    builder.add_conditional_edges(
        "process",
        lambda state: END if state.done else "process",
        {
            END: END,
            "process": "process"
        }
    )

    # Cannot have edges FROM END
    # builder.add_edge(END, "process")  # ❌ ERROR

    return builder.compile()
```

### Self-Loops

Node that routes back to itself:

```python
def should_continue(state):
    """Check if should continue looping."""
    if state.iteration >= state.max_iterations:
        return "done"

    if state.converged:
        return "done"

    return "continue"

def build_graph():
    builder = StateGraph(State)

    builder.add_node("iterate", IterateNode())
    builder.add_node("finalize", FinalizeNode())

    builder.add_edge(START, "iterate")

    # Self-loop
    builder.add_conditional_edges(
        "iterate",
        should_continue,
        {
            "continue": "iterate",  # Loop back to self
            "done": "finalize"
        }
    )

    builder.add_edge("finalize", END)

    return builder.compile()
```

**Use cases:**
- Iterative refinement
- Retry logic
- Polling operations
- Convergence loops

**Caution:**
- Ensure termination condition
- Prevent infinite loops
- Consider max iteration limits

### Multiple Edges from Node

Fan-out pattern:

```python
def build_graph():
    builder = StateGraph(State)

    builder.add_node("split", SplitNode())
    builder.add_node("process_a", ProcessANode())
    builder.add_node("process_b", ProcessBNode())
    builder.add_node("process_c", ProcessCNode())
    builder.add_node("merge", MergeNode())

    builder.add_edge(START, "split")

    # Multiple edges from split (parallel execution)
    builder.add_edge("split", "process_a")
    builder.add_edge("split", "process_b")
    builder.add_edge("split", "process_c")

    # All converge to merge
    builder.add_edge("process_a", "merge")
    builder.add_edge("process_b", "merge")
    builder.add_edge("process_c", "merge")

    builder.add_edge("merge", END)

    return builder.compile()
```

**Note:** LangGraph executes parallel branches concurrently.

---

## Edge Patterns

### Fan-Out Pattern

One node branches to multiple:

```python
def build_fanout():
    """Fan-out pattern for parallel processing."""
    builder = StateGraph(State)

    builder.add_node("prepare", PrepareNode())
    builder.add_node("worker_1", Worker1Node())
    builder.add_node("worker_2", Worker2Node())
    builder.add_node("worker_3", Worker3Node())
    builder.add_node("collect", CollectNode())

    builder.add_edge(START, "prepare")

    # Fan-out
    builder.add_edge("prepare", "worker_1")
    builder.add_edge("prepare", "worker_2")
    builder.add_edge("prepare", "worker_3")

    # Collect results
    builder.add_edge("worker_1", "collect")
    builder.add_edge("worker_2", "collect")
    builder.add_edge("worker_3", "collect")

    builder.add_edge("collect", END)

    return builder.compile()
```

**Use cases:**
- Parallel data processing
- Multi-source data collection
- Concurrent API calls
- Independent computations

### Fan-In Pattern

Multiple nodes converge to one:

```python
def build_fanin():
    """Fan-in pattern for aggregation."""
    builder = StateGraph(State)

    builder.add_node("source_1", Source1Node())
    builder.add_node("source_2", Source2Node())
    builder.add_node("source_3", Source3Node())
    builder.add_node("aggregate", AggregateNode())

    # Multiple sources
    builder.add_edge(START, "source_1")
    builder.add_edge(START, "source_2")
    builder.add_edge(START, "source_3")

    # Fan-in to aggregate
    builder.add_edge("source_1", "aggregate")
    builder.add_edge("source_2", "aggregate")
    builder.add_edge("source_3", "aggregate")

    builder.add_edge("aggregate", END)

    return builder.compile()
```

**Use cases:**
- Data aggregation
- Result combination
- Consensus building
- Multi-input processing

### Loop Pattern

Iterative processing with exit condition:

```python
def should_exit_loop(state):
    """Determine if should exit loop."""
    if state.iteration >= 5:
        return "exit"

    if state.quality_score > 0.9:
        return "exit"

    return "loop"

def build_loop():
    """Loop pattern with exit condition."""
    builder = StateGraph(State)

    builder.add_node("init", InitNode())
    builder.add_node("process", ProcessNode())
    builder.add_node("evaluate", EvaluateNode())
    builder.add_node("finalize", FinalizeNode())

    builder.add_edge(START, "init")
    builder.add_edge("init", "process")
    builder.add_edge("process", "evaluate")

    # Loop or exit
    builder.add_conditional_edges(
        "evaluate",
        should_exit_loop,
        {
            "loop": "process",     # Loop back
            "exit": "finalize"     # Exit loop
        }
    )

    builder.add_edge("finalize", END)

    return builder.compile()
```

**Use cases:**
- Iterative refinement
- Retry with backoff
- Progressive enhancement
- Quality improvement loops

### Branch-Merge Pattern

Conditional branches that reconverge:

```python
def route_processing(state):
    """Route to appropriate processor."""
    if state.data_type == "text":
        return "text_processor"
    elif state.data_type == "image":
        return "image_processor"
    else:
        return "default_processor"

def build_branch_merge():
    """Branch-merge pattern."""
    builder = StateGraph(State)

    builder.add_node("classify", ClassifyNode())
    builder.add_node("text_processor", TextProcessorNode())
    builder.add_node("image_processor", ImageProcessorNode())
    builder.add_node("default_processor", DefaultProcessorNode())
    builder.add_node("merge", MergeNode())

    builder.add_edge(START, "classify")

    # Branch
    builder.add_conditional_edges(
        "classify",
        route_processing,
        {
            "text_processor": "text_processor",
            "image_processor": "image_processor",
            "default_processor": "default_processor"
        }
    )

    # Merge
    builder.add_edge("text_processor", "merge")
    builder.add_edge("image_processor", "merge")
    builder.add_edge("default_processor", "merge")

    builder.add_edge("merge", END)

    return builder.compile()
```

**Use cases:**
- Type-specific processing
- Multi-format handling
- Conditional logic with convergence
- Specialized handlers

---

## Advanced Routing

### Multi-Level Routing

Nested routing decisions:

```python
def first_level_route(state):
    """First routing decision."""
    if state.category == "A":
        return "category_a"
    elif state.category == "B":
        return "category_b"
    else:
        return "default"

def second_level_route_a(state):
    """Second level routing for category A."""
    if state.priority == "high":
        return "a_high"
    else:
        return "a_low"

def second_level_route_b(state):
    """Second level routing for category B."""
    if state.complexity == "simple":
        return "b_simple"
    else:
        return "b_complex"

def build_multilevel():
    """Multi-level routing."""
    builder = StateGraph(State)

    # Level 1
    builder.add_node("classify", ClassifyNode())

    # Level 2 - Category A
    builder.add_node("category_a", CategoryANode())
    builder.add_node("a_high", AHighNode())
    builder.add_node("a_low", ALowNode())

    # Level 2 - Category B
    builder.add_node("category_b", CategoryBNode())
    builder.add_node("b_simple", BSimpleNode())
    builder.add_node("b_complex", BComplexNode())

    builder.add_node("default", DefaultNode())

    builder.add_edge(START, "classify")

    # First level routing
    builder.add_conditional_edges(
        "classify",
        first_level_route,
        {
            "category_a": "category_a",
            "category_b": "category_b",
            "default": "default"
        }
    )

    # Second level routing - A
    builder.add_conditional_edges(
        "category_a",
        second_level_route_a,
        {
            "a_high": "a_high",
            "a_low": "a_low"
        }
    )

    # Second level routing - B
    builder.add_conditional_edges(
        "category_b",
        second_level_route_b,
        {
            "b_simple": "b_simple",
            "b_complex": "b_complex"
        }
    )

    # All converge
    for node in ["a_high", "a_low", "b_simple", "b_complex", "default"]:
        builder.add_edge(node, END)

    return builder.compile()
```

### Priority-Based Routing

Route based on priority:

```python
def priority_route(state):
    """Route based on priority levels."""
    priority = state.priority

    # Critical - immediate processing
    if priority == "critical":
        return "critical_handler"

    # High priority - expedited
    if priority == "high":
        return "expedited_handler"

    # Check capacity for normal priority
    if priority == "normal":
        if state.queue_length < 10:
            return "normal_handler"
        else:
            return "queued_handler"

    # Low priority - batch processing
    return "batch_handler"

def build_priority():
    """Priority-based routing."""
    builder = StateGraph(State)

    builder.add_node("assess", AssessNode())
    builder.add_node("critical_handler", CriticalNode())
    builder.add_node("expedited_handler", ExpeditedNode())
    builder.add_node("normal_handler", NormalNode())
    builder.add_node("queued_handler", QueuedNode())
    builder.add_node("batch_handler", BatchNode())

    builder.add_edge(START, "assess")

    builder.add_conditional_edges(
        "assess",
        priority_route,
        {
            "critical_handler": "critical_handler",
            "expedited_handler": "expedited_handler",
            "normal_handler": "normal_handler",
            "queued_handler": "queued_handler",
            "batch_handler": "batch_handler"
        }
    )

    for node in ["critical_handler", "expedited_handler", "normal_handler",
                  "queued_handler", "batch_handler"]:
        builder.add_edge(node, END)

    return builder.compile()
```

### Fallback Routing

Route with fallback options:

```python
def route_with_fallback(state):
    """Route with fallback chain."""
    # Try primary handler
    if state.primary_available:
        return "primary"

    # Try secondary handler
    if state.secondary_available:
        return "secondary"

    # Try tertiary handler
    if state.tertiary_available:
        return "tertiary"

    # Fallback to default
    return "default"

def build_fallback():
    """Fallback routing pattern."""
    builder = StateGraph(State)

    builder.add_node("check_availability", CheckNode())
    builder.add_node("primary", PrimaryNode())
    builder.add_node("secondary", SecondaryNode())
    builder.add_node("tertiary", TertiaryNode())
    builder.add_node("default", DefaultNode())

    builder.add_edge(START, "check_availability")

    builder.add_conditional_edges(
        "check_availability",
        route_with_fallback,
        {
            "primary": "primary",
            "secondary": "secondary",
            "tertiary": "tertiary",
            "default": "default"
        }
    )

    for node in ["primary", "secondary", "tertiary", "default"]:
        builder.add_edge(node, END)

    return builder.compile()
```

### Parallel Conditional Routing

Multiple conditional paths execute in parallel:

```python
def build_parallel_conditional():
    """Parallel conditional routing."""
    builder = StateGraph(State)

    builder.add_node("prepare", PrepareNode())

    # Parallel conditional branches
    builder.add_node("check_a", CheckANode())
    builder.add_node("check_b", CheckBNode())
    builder.add_node("process_a1", ProcessA1Node())
    builder.add_node("process_a2", ProcessA2Node())
    builder.add_node("process_b1", ProcessB1Node())
    builder.add_node("process_b2", ProcessB2Node())

    builder.add_node("merge", MergeNode())

    builder.add_edge(START, "prepare")

    # Parallel branches
    builder.add_edge("prepare", "check_a")
    builder.add_edge("prepare", "check_b")

    # Conditional routing in branch A
    builder.add_conditional_edges(
        "check_a",
        lambda state: "a1" if state.condition_a else "a2",
        {
            "a1": "process_a1",
            "a2": "process_a2"
        }
    )

    # Conditional routing in branch B
    builder.add_conditional_edges(
        "check_b",
        lambda state: "b1" if state.condition_b else "b2",
        {
            "b1": "process_b1",
            "b2": "process_b2"
        }
    )

    # All merge
    for node in ["process_a1", "process_a2", "process_b1", "process_b2"]:
        builder.add_edge(node, "merge")

    builder.add_edge("merge", END)

    return builder.compile()
```

---

## Edge Configuration

### Edge Metadata

Attach metadata to edges (LangGraph Studio):

```python
def build_graph_with_metadata():
    """Graph with edge metadata."""
    builder = StateGraph(State)

    builder.add_node("process", ProcessNode())
    builder.add_node("next", NextNode())

    # Note: Metadata is primarily for visualization
    builder.add_edge(START, "process")
    builder.add_edge("process", "next")
    builder.add_edge("next", END)

    return builder.compile()
```

### Edge Conditions

Complex edge conditions:

```python
def complex_condition(state):
    """Complex multi-criteria condition."""
    # Must satisfy all conditions
    if not state.validated:
        return "invalid"

    if state.score < 0.5:
        return "low_quality"

    if state.cost > state.budget:
        return "over_budget"

    # Check business rules
    if state.user_tier == "free" and state.api_calls > 100:
        return "rate_limited"

    # All conditions met
    return "approved"

def build_complex_conditions():
    """Graph with complex edge conditions."""
    builder = StateGraph(State)

    builder.add_node("evaluate", EvaluateNode())
    builder.add_node("invalid", InvalidNode())
    builder.add_node("low_quality", LowQualityNode())
    builder.add_node("over_budget", OverBudgetNode())
    builder.add_node("rate_limited", RateLimitedNode())
    builder.add_node("approved", ApprovedNode())

    builder.add_edge(START, "evaluate")

    builder.add_conditional_edges(
        "evaluate",
        complex_condition,
        {
            "invalid": "invalid",
            "low_quality": "low_quality",
            "over_budget": "over_budget",
            "rate_limited": "rate_limited",
            "approved": "approved"
        }
    )

    for node in ["invalid", "low_quality", "over_budget",
                  "rate_limited", "approved"]:
        builder.add_edge(node, END)

    return builder.compile()
```

### Edge Priorities

Implement priority through routing order:

```python
def priority_routing(state):
    """Check conditions in priority order."""
    # Priority 1: Critical errors
    if state.critical_error:
        return "critical_error"

    # Priority 2: Validation
    if not state.validated:
        return "validation"

    # Priority 3: Rate limits
    if state.rate_limited:
        return "rate_limit"

    # Priority 4: Normal processing
    if state.ready:
        return "process"

    # Priority 5: Queue
    return "queue"
```

---

## Best Practices

### 1. Use descriptive route keys

```python
# ✅ Good
def route(state):
    return "user_authenticated" if state.user else "guest_mode"

# ❌ Bad
def route(state):
    return "a" if state.user else "b"
```

### 2. Document routing logic

```python
def route_by_priority(state):
    """
    Route based on priority level.

    Returns:
        - "critical": priority == 0 (immediate)
        - "high": priority == 1 (expedited)
        - "normal": priority == 2 (standard)
        - "low": priority >= 3 (batched)
    """
    priority = state.priority
    if priority == 0:
        return "critical"
    elif priority == 1:
        return "high"
    elif priority == 2:
        return "normal"
    else:
        return "low"
```

### 3. Ensure all paths are mapped

```python
def route(state):
    """All possible returns are mapped."""
    return state.status  # Can be: success, error, pending

builder.add_conditional_edges(
    "process",
    route,
    {
        "success": "success_handler",
        "error": "error_handler",
        "pending": "pending_handler"  # Don't forget any!
    }
)
```

### 4. Avoid complex routing functions

```python
# ✅ Good - clear logic
def route(state):
    if state.type == "A":
        return "handler_a"
    if state.type == "B":
        return "handler_b"
    return "default"

# ❌ Bad - too complex
def route(state):
    return ("handler_a" if state.type == "A" else
            "handler_b" if state.type == "B" and state.flag else
            "handler_c" if state.nested.value > 10 else "default")
```

### 5. Test routing functions independently

```python
def test_routing():
    """Test routing function."""
    # Test each path
    assert route(State(status="success")) == "success"
    assert route(State(status="error")) == "error"
    assert route(State(status="pending")) == "pending"
```

### 6. Prevent infinite loops

```python
def safe_loop_route(state):
    """Route with loop protection."""
    # Always have exit condition
    if state.iteration >= MAX_ITERATIONS:
        return "exit"

    if state.is_complete:
        return "exit"

    return "continue"
```

### 7. Use meaningful node names

```python
# ✅ Good
builder.add_edge("validate_input", "process_data")

# ❌ Bad
builder.add_edge("node1", "node2")
```

### 8. Keep routing pure

```python
# ✅ Good - pure function
def route(state):
    return "success" if state.valid else "error"

# ❌ Bad - side effects
def route(state):
    log.info("Routing...")  # Side effect
    state.routed = True  # Mutation
    return "success"
```

---

## Common Patterns

### Pattern: Retry Loop

```python
def retry_route(state):
    if state.error and state.retry_count < 3:
        return "retry"
    if state.error:
        return "failed"
    return "success"

builder.add_conditional_edges(
    "process",
    retry_route,
    {
        "retry": "process",  # Loop
        "failed": "error_handler",
        "success": "next_step"
    }
)
```

### Pattern: Validation Chain

```python
def validation_route(state):
    if not state.schema_valid:
        return "schema_error"
    if not state.business_rules_valid:
        return "rules_error"
    return "valid"

builder.add_conditional_edges(
    "validate",
    validation_route,
    {
        "schema_error": "schema_error_handler",
        "rules_error": "rules_error_handler",
        "valid": "process"
    }
)
```

### Pattern: Agent Tool Loop

```python
def agent_route(state):
    last_message = state.messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"

builder.add_conditional_edges(
    "agent",
    agent_route,
    {
        "tools": "tools",  # Execute tools
        "end": END         # No more tools
    }
)
builder.add_edge("tools", "agent")  # Back to agent
```

---

## Troubleshooting

### Issue: "KeyError: route_key"

**Cause:** Routing function returns unmapped key

**Fix:**
```python
# Ensure all returns are mapped
def route(state):
    return state.type  # Returns "unknown"

builder.add_conditional_edges(
    "node",
    route,
    {
        "type_a": "handler_a",
        "type_b": "handler_b",
        # Add mapping for all possible returns
        "unknown": "default_handler"
    }
)
```

### Issue: Infinite loop

**Cause:** No exit condition in loop

**Fix:**
```python
def route(state):
    # Add iteration limit
    if state.iteration >= 100:
        return "exit"

    if state.done:
        return "exit"

    return "continue"
```

### Issue: Routing function not called

**Cause:** Using simple edge instead of conditional

**Fix:**
```python
# ❌ Wrong
builder.add_edge("node", "next")

# ✅ Correct
builder.add_conditional_edges("node", route_func, {...})
```

### Issue: Graph doesn't reach END

**Cause:** Missing edge to END

**Fix:**
```python
# Ensure all terminal nodes reach END
builder.add_edge("final_node", END)
```

---

## Examples

### Complete Example: Query Router

```python
from langgraph.graph import StateGraph, START, END
from dataclasses import dataclass

@dataclass(kw_only=True)
class State:
    query: str
    query_type: str = None
    result: str = None
    error: str = None

def classify_query(state):
    """Classify query type."""
    query = state.query.lower()

    if "weather" in query:
        return "weather"
    elif "news" in query:
        return "news"
    elif "calculate" in query or any(op in query for op in ["+", "-", "*", "/"]):
        return "calculator"
    else:
        return "general"

def build_query_router():
    """Build query router graph."""
    builder = StateGraph(State)

    # Add nodes
    builder.add_node("classify", ClassifyNode())
    builder.add_node("weather", WeatherNode())
    builder.add_node("news", NewsNode())
    builder.add_node("calculator", CalculatorNode())
    builder.add_node("general", GeneralNode())

    # Entry
    builder.add_edge(START, "classify")

    # Route based on classification
    builder.add_conditional_edges(
        "classify",
        classify_query,
        {
            "weather": "weather",
            "news": "news",
            "calculator": "calculator",
            "general": "general"
        }
    )

    # All paths to END
    for node in ["weather", "news", "calculator", "general"]:
        builder.add_edge(node, END)

    return builder.compile()
```

---

## Summary

**Edge types:**
- **Simple edges**: Direct connections
- **Conditional edges**: Branching based on state
- **Dynamic routing**: Runtime decision-making

**Key concepts:**
- START: Entry point
- END: Exit point
- Routing functions: Return route keys
- Path mappings: Map keys to nodes

**Best practices:**
- Use descriptive route keys
- Document routing logic
- Map all possible returns
- Prevent infinite loops
- Test routing independently
- Keep routing pure

**References:**
- LangGraph Edges: https://langchain-ai.github.io/langgraph/concepts/low_level/#edges
- Conditional Routing: https://langchain-ai.github.io/langgraph/how-tos/branching/
- Graph Patterns: https://langchain-ai.github.io/langgraph/concepts/high_level/
