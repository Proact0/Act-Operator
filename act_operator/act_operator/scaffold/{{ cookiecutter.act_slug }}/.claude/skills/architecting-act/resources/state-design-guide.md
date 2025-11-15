# State Schema Design Guide

A comprehensive guide for designing LangGraph state schemas with proper structure, reducers, and channels.

## State Design Philosophy

**State is the memory of your graph.** It flows through nodes, gets updated, and determines routing decisions. Good state design enables:
- Clear data flow
- Type safety
- Efficient updates
- Easy debugging
- Maintainable code

**Key Principle:** Design state to represent "what your graph knows" at any point in execution, not "how it computes."

---

## State Structure Overview

A LangGraph StateGraph uses a typed state schema (TypedDict or Pydantic model) defining:
- **Fields:** The data attributes
- **Types:** What kind of data each field holds
- **Reducers:** How field updates are merged
- **Annotations:** Metadata for advanced features

### Basic State Structure

```
State Schema
├─ Input Fields (what comes in)
├─ Working Fields (intermediate data)
├─ Output Fields (what goes out)
└─ Metadata Fields (tracking, debugging)
```

---

## State Field Categories

### 1. Input Fields
**Purpose:** Data provided at graph invocation
**Characteristics:**
- Set once at start
- Read-only during execution (usually)
- Defines what user/system provides

**Examples:**
- User message/query
- Input files/documents
- Configuration parameters
- Session context

**Design Tips:**
- Make required inputs explicit
- Provide sensible defaults where possible
- Validate at graph entry point

---

### 2. Working Fields
**Purpose:** Intermediate data created and updated during execution
**Characteristics:**
- Modified by nodes
- May use reducers for accumulation
- Represents computational progress

**Examples:**
- Messages list (conversation history)
- Tool outputs
- Intermediate results
- Iteration counters

**Design Tips:**
- Use reducers for accumulating data (lists, dicts)
- Include iteration/step tracking
- Consider partial results for debugging

---

### 3. Output Fields
**Purpose:** Final results returned to caller
**Characteristics:**
- Set by final nodes
- Represents graph completion
- May overlap with working fields

**Examples:**
- Final response/answer
- Generated artifacts
- Success/failure status
- Confidence scores

**Design Tips:**
- Clearly indicate completion status
- Include metadata (tokens, latency, etc.)
- Make output self-contained

---

### 4. Metadata Fields
**Purpose:** Tracking, debugging, and operational info
**Characteristics:**
- Non-functional but valuable
- Helps with observability
- Aids debugging and optimization

**Examples:**
- Execution timestamps
- Node execution counts
- Cost tracking
- Error messages/warnings

**Design Tips:**
- Don't skip these - very valuable
- Include enough for debugging
- Consider logging/monitoring needs

---

## Reducers: Managing State Updates

Reducers control **how state field updates are merged** when multiple updates occur.

### When Reducers Matter

**Scenario 1: Nodes run in parallel**
- Multiple nodes update same field simultaneously
- Reducer merges their updates

**Scenario 2: Nodes update accumulating data**
- Node adds message to messages list
- Reducer appends instead of replacing

**Scenario 3: Conditional updates**
- Different paths update same field
- Reducer ensures consistent merge

### Common Reducer Patterns

#### 1. Override Reducer (Default)
**Behavior:** New value replaces old value
**Use for:** Single-value fields updated once
**Example fields:** current_step, final_answer, status

```
No explicit reducer needed - this is default behavior
```

#### 2. List Append Reducer
**Behavior:** New items added to list
**Use for:** Accumulating messages, results, tool outputs
**Example fields:** messages, intermediate_results, tool_calls

```
Annotation: Annotated[list[X], operator.add]
```

#### 3. Dict Merge Reducer
**Behavior:** New dict merged into existing dict
**Use for:** Accumulated key-value data
**Example fields:** tool_outputs, metadata, scores

```
Annotation: Annotated[dict, merge_dicts]  # Custom merge function
```

#### 4. Counter Reducer
**Behavior:** Numeric values summed
**Use for:** Counts, costs, tokens
**Example fields:** total_tokens, step_count, total_cost

```
Annotation: Annotated[int, operator.add]
```

#### 5. Custom Reducer
**Behavior:** User-defined merge logic
**Use for:** Complex domain-specific merging
**Example:** Combining scores, resolving conflicts

```
def custom_reducer(existing, new):
    # Your merge logic
    return merged

Annotation: Annotated[YourType, custom_reducer]
```

### Reducer Selection Guide

| Field Type | Default Update | Recommended Reducer |
|------------|----------------|---------------------|
| Single value (set once) | Override | None (default) |
| Conversation messages | Accumulate | List append |
| Tool outputs collection | Accumulate | List append or Dict merge |
| Status/flags | Override | None (default) |
| Counts/metrics | Increment | Counter (add) |
| Complex objects | Custom | Custom function |

---

## Input/Output Schema Separation

**Concept:** Define separate schemas for what goes IN vs what comes OUT.

### Why Separate?

**Benefits:**
- Clear API contract
- Type safety at boundaries
- Easier validation
- Better documentation

**Implementation:**
- Use Input/Output annotations
- Validate at graph entry/exit
- Transform between schemas if needed

### Design Pattern

```
Input Schema:
- user_query: str
- context_docs: list[str]
- max_iterations: int = 5

Working Schema (extends Input):
- messages: list[Message]  (reducer: append)
- current_iteration: int
- tool_outputs: dict  (reducer: merge)

Output Schema:
- final_answer: str
- sources_used: list[str]
- confidence: float
- metadata: dict
```

**Key Idea:** Input → Working (accumulates) → Output (extracted)

---

## State Type Best Practices

### Primitive Types
**Use for:** Simple values
**Examples:** str, int, float, bool
**Pros:** Simple, type-safe
**Cons:** Limited structure

### Lists
**Use for:** Ordered collections, accumulation
**Examples:** messages, results, tool_calls
**Pros:** Easy to append, iterate
**Cons:** Can grow large, no key access
**Reducer:** Typically append (operator.add)

### Dicts
**Use for:** Key-value data, flexible structure
**Examples:** tool_outputs, metadata, config
**Pros:** Flexible, key access
**Cons:** Less type-safe without TypedDict
**Reducer:** Typically merge

### Custom Objects (Pydantic)
**Use for:** Complex structured data
**Examples:** Document, SearchResult, Analysis
**Pros:** Validation, methods, composition
**Cons:** More complex
**Reducer:** Custom based on logic

### Optional Fields
**Use for:** Fields not always present
**Annotation:** Optional[T] or T | None
**Examples:** error_message, final_result (before completion)
**Default:** None

---

## State Design Patterns

### Pattern 1: Message-Based State
**Best for:** Conversational agents, ReAct pattern
**Characteristics:**
- Central messages list (with append reducer)
- Minimal additional state
- Simple and standard

**Example Structure:**
```
State:
- messages: list[Message]  (append reducer)
- current_tool: Optional[str]
- iteration_count: int
```

---

### Pattern 2: Structured Task State
**Best for:** Plan-Execute, complex workflows
**Characteristics:**
- Explicit task/plan tracking
- Status fields for each step
- Rich metadata

**Example Structure:**
```
State:
- plan: list[Step]
- current_step_idx: int
- step_results: dict[int, Result]  (merge reducer)
- overall_status: str
```

---

### Pattern 3: Multi-Agent Shared State
**Best for:** Multi-agent collaboration
**Characteristics:**
- Shared scratchpad (messages)
- Per-agent context
- Supervisor metadata

**Example Structure:**
```
State:
- messages: list[Message]  (append reducer)
- agent_outputs: dict[str, Output]  (merge reducer)
- next_agent: str
- consensus: Optional[str]
```

---

### Pattern 4: Map-Reduce State
**Best for:** Parallel processing
**Characteristics:**
- Items to process
- Per-item results
- Aggregated output

**Example Structure:**
```
State (Parent):
- items: list[Item]
- results: list[Result]  (append reducer)
- aggregated: Optional[Final]

State (Worker - different schema):
- item: Item
- result: Result
```

**Note:** Worker nodes may have different state schema using Send API.

---

## Advanced State Features

### Channels (LangGraph 1.0)
**What:** Named state fields with specific behaviors
**Use for:** Advanced state management, custom persistence
**Example:** LastValue channel, Topic channel, BinaryOperator channel

### Private State
**What:** State not exposed in output
**Use for:** Internal tracking, debugging
**Pattern:** Prefix with underscore (_internal_field)

### State Validation
**What:** Ensuring state integrity
**Use with:** Pydantic models with validators
**Example:** Validate message format, check iteration limits

---

## State Design Decision Framework

### Step 1: Identify Data Flow
**Questions:**
- What data enters the graph?
- What intermediate data is needed?
- What data exits the graph?
- What data accumulates vs gets replaced?

### Step 2: Choose Field Types
**For each data element:**
- Single value or collection?
- Primitive or complex object?
- Required or optional?
- Validated or freeform?

### Step 3: Determine Reducers
**For each field:**
- Can multiple nodes update it?
- Should updates accumulate or override?
- Is there a natural merge logic?

### Step 4: Organize by Category
**Group fields:**
- Input section
- Working section
- Output section
- Metadata section

### Step 5: Validate Design
**Check:**
- All node outputs have a state field
- All routing decisions have necessary state
- No redundant fields
- Clear field responsibilities

---

## Common State Design Mistakes

### ❌ Overly Complex State
**Problem:** Too many fields, unclear responsibilities
**Solution:** Simplify, group related data, use nested objects

### ❌ Missing Reducers
**Problem:** Parallel updates clobber each other
**Solution:** Add appropriate reducers for accumulating fields

### ❌ No Metadata
**Problem:** Can't debug or track execution
**Solution:** Include step counts, timestamps, costs

### ❌ Mixing Concerns
**Problem:** Blending input, working, and output data unclearly
**Solution:** Organize by category, comment sections

### ❌ Mutable Shared Objects
**Problem:** Nodes modifying same object reference causing side effects
**Solution:** Use immutable types or copy before modify

### ❌ No Optional Fields
**Problem:** Fields required even when not yet available
**Solution:** Make pre-completion fields Optional

---

## State Design Checklist

Before finalizing state schema:

- [ ] All input data has a field
- [ ] All node outputs have target fields
- [ ] Accumulating fields have reducers
- [ ] Output fields are identified
- [ ] Metadata fields included (iteration, cost, etc.)
- [ ] Optional fields marked as Optional
- [ ] Field types are specific (not just dict/list)
- [ ] State enables all routing decisions
- [ ] State is documented (comments or docstrings)
- [ ] State is validated (if using Pydantic)

---

## Example State Schemas

### Example 1: Simple ReAct Agent
```
Input:
- user_query: str

Working:
- messages: list[Message]  (append)
- iteration: int

Output:
- final_response: str
- tool_calls_made: int
```

---

### Example 2: Plan-Execute System
```
Input:
- task_description: str
- max_steps: int = 10

Working:
- plan: list[str]
- current_step: int
- step_results: dict[int, str]  (merge)
- need_replan: bool

Output:
- final_result: str
- steps_completed: int
- success: bool
```

---

### Example 3: Multi-Agent Research
```
Input:
- research_question: str
- sources: list[str]

Working:
- messages: list[Message]  (append)
- researcher_findings: Optional[str]
- critic_feedback: Optional[str]
- revision_count: int

Output:
- final_report: str
- sources_used: list[str]
- confidence: float
```

---

### Example 4: Map-Reduce Document Processing

**Parent State:**
```
Input:
- documents: list[Document]

Working:
- processed_count: int
- summaries: list[str]  (append)

Output:
- final_summary: str
- total_docs: int
```

**Worker State (different schema via Send):**
```
- document: Document
- summary: str
```

---

## Best Practices Summary

1. **Start Simple:** Add fields as needed, don't over-design
2. **Be Explicit:** Clear field names and types
3. **Use Reducers:** For any accumulating data
4. **Separate Concerns:** Input, working, output, metadata
5. **Include Metadata:** You'll thank yourself when debugging
6. **Validate Types:** Use Pydantic for complex schemas
7. **Document State:** Comments explaining field purposes
8. **Plan for Evolution:** State may grow, keep it organized

---

**Remember:** State design is the foundation of your graph architecture. Invest time here - it pays dividends throughout development and maintenance.
