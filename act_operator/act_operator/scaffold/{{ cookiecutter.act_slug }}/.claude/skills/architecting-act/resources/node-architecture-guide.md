# Node Architecture Guide

A comprehensive guide for designing LangGraph nodes following SOLID principles and best practices.

## Node Design Philosophy

**Nodes are the building blocks of your graph.** Each node is a function that:
- Receives current state
- Performs a single, well-defined responsibility
- Returns updated state

**Key Principle:** Design nodes as minimum functional units with single responsibilities (SOLID).

---

## SOLID Principles for Nodes

### S - Single Responsibility Principle
**Definition:** Each node should do ONE thing well.

**Why it matters:**
- Easier to test
- Easier to debug
- Reusable across graphs
- Clear naming

**Examples:**
- ✅ `extract_key_info` - ONE job: extract information
- ✅ `validate_response` - ONE job: validate
- ❌ `process_and_validate_and_format` - THREE jobs (split into 3 nodes)

**How to apply:**
- If node name has "and", consider splitting
- If node has multiple unrelated conditionals, split
- If node is > 50 lines, likely doing too much

---

### O - Open/Closed Principle
**Definition:** Nodes should be extensible without modification.

**Why it matters:**
- Add new behaviors without changing existing nodes
- Safer evolution
- Backward compatibility

**How to apply:**
- Use configuration from state, not hardcoded logic
- Design nodes to accept parameters via state
- Use routing edges to add new paths, not modify node logic

**Example:**
- ✅ Node reads `model_name` from state, works with any model
- ❌ Node hardcodes specific model, needs modification for new models

---

### L - Liskov Substitution Principle
**Definition:** Node variations should be interchangeable.

**Why it matters:**
- Swap implementations easily
- A/B testing different approaches
- Environment-specific variations

**How to apply:**
- Keep node interfaces consistent (input/output state fields)
- Multiple implementations of same node type
- Use configuration to select implementation

**Example:**
- `search_web` and `search_database` both receive `query`, return `results`
- Graph can use either based on configuration

---

### I - Interface Segregation Principle
**Definition:** Nodes should only depend on state fields they need.

**Why it matters:**
- Clear dependencies
- Easier testing (mock only what's needed)
- Reduced coupling

**How to apply:**
- Document which state fields each node reads/writes
- Don't pass entire state if only subset needed
- Consider focused state schemas for subgraphs

**Example:**
- `summarize_text` only needs `text` field, not entire conversation history
- Make dependencies explicit in node documentation

---

### D - Dependency Inversion Principle
**Definition:** Nodes should depend on abstractions, not concrete implementations.

**Why it matters:**
- Testable (inject mocks)
- Flexible (swap implementations)
- Environment-agnostic

**How to apply:**
- Inject LLM, tools, clients via state or config
- Don't hardcode external service URLs/keys
- Use factory functions to create configured nodes

**Example:**
- ✅ Node receives `llm` from state/config
- ❌ Node creates OpenAI client with hardcoded key

---

## Node Decomposition Strategies

### Strategy 1: By Computation Stage
Break workflow into distinct computational phases.

**Example: Document Processing**
```
Input → Extract Text → Chunk Text → Embed Chunks → Store Embeddings → Output
```

**When to use:**
- Clear sequential stages
- Each stage transforms data
- Stages reusable independently

---

### Strategy 2: By Responsibility Domain
Group by what the node is responsible for.

**Example: Research Agent**
```
Plan Research → Search Sources → Extract Info → Validate Facts → Synthesize Report
```

**When to use:**
- Different expertise/tools per domain
- Each domain has distinct logic
- Natural separation of concerns

---

### Strategy 3: By Decision Point
Create nodes around decision-making moments.

**Example: Content Moderation**
```
Check Content → Route by Risk → [High: Deep Analysis | Low: Auto-Approve | Medium: Human Review]
```

**When to use:**
- Multiple execution paths
- Conditional logic is complex
- Decisions need separate reasoning

---

### Strategy 4: By Actor/Agent
One node per agent/actor in multi-agent systems.

**Example: Collaborative Writing**
```
Writer Agent → Editor Agent → Fact Checker Agent → Final Reviewer
```

**When to use:**
- Multi-agent collaboration
- Different prompts/tools per agent
- Clear role boundaries

---

## Node Granularity

### Too Coarse (Anti-pattern)
**Problem:** Monolithic nodes doing too much
**Signs:**
- Node > 100 lines
- Multiple unrelated responsibilities
- Hard to test
- Difficult to reuse

**Solution:** Decompose using strategies above

---

### Too Fine (Anti-pattern)
**Problem:** Excessive node splitting
**Signs:**
- Nodes just pass data through
- No meaningful computation
- Over-complicated graph
- Hard to understand flow

**Solution:** Merge trivial nodes with neighbors

---

### Just Right
**Characteristics:**
- 20-50 lines per node (typical)
- Single clear responsibility
- Testable in isolation
- Reusable
- Descriptive name explains purpose

---

## Node Dependency Management

### Identifying Dependencies

**Data Dependencies:**
- Which state fields does this node READ?
- Which state fields does this node WRITE?
- Are there optional dependencies?

**External Dependencies:**
- LLM/model calls
- Tool/API calls
- Database access
- File system access

**Control Dependencies:**
- Must run after node X?
- Can run in parallel with node Y?
- Conditional on state value?

### Documenting Dependencies

**Node Documentation Template:**
```
Node: <name>
Purpose: <one-line description>
Reads: <state fields>
Writes: <state fields>
External: <APIs, tools, LLMs used>
Dependencies: <must run after which nodes>
Parallel: <can run with which nodes>
```

---

## Parallel vs Sequential Execution

### Identifying Parallel Opportunities

**Nodes can run in parallel when:**
- No data dependencies between them
- Both only read (don't write same fields)
- Order doesn't matter
- Independent computations

**Example:**
```
After "Plan" node, these can run in parallel:
- Research topic A
- Research topic B
- Research topic C
```

### Identifying Sequential Requirements

**Nodes must run sequentially when:**
- One depends on other's output
- Both write to same field (without appropriate reducer)
- Order matters for correctness
- Side effects must be ordered

**Example:**
```
Must run in sequence:
1. Generate draft
2. Critique draft (depends on draft existing)
3. Revise draft (depends on critique)
```

### Design Pattern: Parallel-Merge

```
                  ┌─→ Task A ─┐
Input → Split ────┼─→ Task B ─┼──→ Merge → Output
                  └─→ Task C ─┘
```

**When to use:**
- Independent subtasks
- Results need aggregation
- Latency critical (parallelization helps)

**State Requirements:**
- Appropriate reducers on merge fields
- Synchronization mechanism (defer pattern if needed)

---

## Node Types Catalog

### 1. Input Validation Node
**Purpose:** Validate and sanitize inputs
**Characteristics:**
- First node after START
- Checks input validity
- May transform input format
- Sets error state if invalid

**Example responsibilities:**
- Validate user query not empty
- Check file formats
- Sanitize inputs

---

### 2. Agent/LLM Node
**Purpose:** Call LLM for reasoning, generation, decision
**Characteristics:**
- Contains prompt template
- Calls LLM with state context
- Parses LLM response
- Updates state with result

**Example responsibilities:**
- Generate response
- Make routing decision
- Extract information
- Classify input

---

### 3. Tool Node
**Purpose:** Execute external tool/API call
**Characteristics:**
- Wraps tool invocation
- Handles errors
- Formats tool output
- Updates state with results

**Example responsibilities:**
- Search web
- Query database
- Call API
- Process file

---

### 4. Routing/Decision Node
**Purpose:** Determine next node(s) based on state
**Characteristics:**
- Evaluates conditions
- Returns routing decision (string or list)
- No state updates (usually)
- Pure decision logic

**Example responsibilities:**
- Route by category
- Decide if done or continue
- Select agent for task
- Branch based on state

---

### 5. Aggregation/Reduce Node
**Purpose:** Combine results from parallel executions
**Characteristics:**
- Receives multiple inputs (via reducer)
- Synthesizes/summarizes
- Produces combined output

**Example responsibilities:**
- Summarize parallel research results
- Combine scores
- Merge documents

---

### 6. Validation/Reflection Node
**Purpose:** Check quality, validate correctness
**Characteristics:**
- Evaluates output against criteria
- May use LLM for judgment
- Sets quality flags
- Triggers retry if needed

**Example responsibilities:**
- Check response quality
- Validate facts
- Score confidence
- Detect hallucinations

---

### 7. Transformation Node
**Purpose:** Convert data format or structure
**Characteristics:**
- Pure transformation logic
- No LLM calls (usually)
- Deterministic
- Format conversion

**Example responsibilities:**
- Format output
- Convert types
- Restructure data
- Apply templates

---

### 8. State Management Node
**Purpose:** Update state metadata, counters
**Characteristics:**
- Updates tracking fields
- Increments counters
- Sets flags
- Minimal computation

**Example responsibilities:**
- Increment iteration count
- Set completion flag
- Update timestamp
- Track costs

---

## Node Design Patterns

### Pattern 1: Try-Validate-Retry
```
Generate → Validate → [Valid: Continue | Invalid: Regenerate]
                           ↑                      │
                           └──────────────────────┘
```

**Use for:** Quality-critical outputs
**Nodes:**
- Generator node
- Validator node
- Router (continue or retry)

---

### Pattern 2: Agent-Tool-Agent
```
Agent Decides → Execute Tool → Agent Processes Result
```

**Use for:** ReAct pattern
**Nodes:**
- Agent node (decision)
- Tool execution node(s)
- Agent node (observation)

---

### Pattern 3: Hierarchical Delegation
```
Supervisor Plans → [Worker 1 | Worker 2 | Worker 3] → Supervisor Aggregates
```

**Use for:** Multi-agent with supervisor
**Nodes:**
- Supervisor planner
- Worker nodes (parallel or sequential)
- Supervisor aggregator

---

### Pattern 4: Sequential Refinement
```
Draft → Critique → Revise → Critique → Revise → Finalize
```

**Use for:** Iterative improvement
**Nodes:**
- Generator
- Critic
- Reviser
- Finalizer

---

## Node Communication Patterns

### Pattern 1: Direct State Update
**How:** Node updates state field, next node reads it
**Best for:** Simple sequential flow
**Example:** Node A writes `draft`, Node B reads `draft`

---

### Pattern 2: Message Passing
**How:** Nodes append to messages list (with reducer)
**Best for:** Conversational, multi-agent
**Example:** Agents add messages, all agents read full history

---

### Pattern 3: Result Accumulation
**How:** Nodes write to list/dict with merge reducer
**Best for:** Parallel execution, map-reduce
**Example:** Workers add results to `results` list

---

### Pattern 4: Flag Signaling
**How:** Node sets boolean flag, routing checks it
**Best for:** Conditional flow control
**Example:** Validator sets `is_valid`, router checks flag

---

## Node Testing Considerations

### Design for Testability

**Characteristics of testable nodes:**
- Pure functions (same input → same output) when possible
- Clear input/output contracts (state fields)
- Minimal external dependencies (injected)
- Isolated responsibilities

**Testing approach:**
```
1. Create mock state with required input fields
2. Call node function
3. Assert output state fields match expected
4. Verify external calls (if any) with mocks
```

---

## Node Error Handling

### Error Handling Strategies

**Strategy 1: Error State Field**
- Node catches errors
- Sets `error` field in state
- Returns updated state
- Routing checks error field

**Strategy 2: Retry Logic**
- Node attempts operation
- On failure, increments retry counter
- Routes back to self if retries remain
- Routes to error handler if exhausted

**Strategy 3: Graceful Degradation**
- Node attempts primary approach
- On failure, tries fallback
- Sets flag indicating fallback used
- Continues execution

**Strategy 4: Error Router**
- Node raises exception
- Error router catches it
- Routes to error handling node
- Error handler updates state, recovers

---

## Anti-Patterns in Node Design

### ❌ God Node
**Problem:** One node doing everything
**Solution:** Decompose by responsibility

### ❌ Chatty Nodes
**Problem:** Many tiny nodes with excessive state passing
**Solution:** Merge related trivial nodes

### ❌ Hidden Dependencies
**Problem:** Node depends on undocumented state fields
**Solution:** Document all dependencies explicitly

### ❌ Side Effects
**Problem:** Node modifies external state without state tracking
**Solution:** Make all effects visible in state

### ❌ Hardcoded Config
**Problem:** Node has hardcoded values that should be configurable
**Solution:** Read configuration from state

### ❌ Non-Deterministic Without Reason
**Problem:** Node behaves differently on same input without clear reason
**Solution:** Make randomness explicit (seed in state)

---

## Node Design Checklist

Before finalizing node architecture:

- [ ] Each node has single, clear responsibility
- [ ] Node names clearly describe purpose
- [ ] Dependencies documented (reads/writes state fields)
- [ ] Parallel opportunities identified
- [ ] Sequential constraints respected
- [ ] Error handling strategy defined
- [ ] External dependencies injectable/testable
- [ ] No god nodes (< 100 lines each)
- [ ] No excessive chatty nodes (merged where appropriate)
- [ ] Routing decisions have dedicated router nodes
- [ ] Validation/quality checks have dedicated nodes
- [ ] Node count is reasonable (not too many, not too few)

---

## Node Naming Conventions

**Good names are:**
- Verb-based (describes action)
- Specific (not generic)
- Clear intent
- Consistent style

**Examples:**

| Purpose | ❌ Bad Name | ✅ Good Name |
|---------|------------|-------------|
| Extract info | `process` | `extract_key_info` |
| Call LLM | `llm_node` | `generate_response` |
| Validate | `check` | `validate_output_quality` |
| Route | `router` | `route_by_category` |
| Tool call | `tool` | `search_web` |
| Aggregate | `combine` | `aggregate_research_results` |

---

## Example Node Architectures

### Example 1: Simple RAG System
```
Nodes:
1. validate_query: Check user query is valid
2. retrieve_documents: Search vector store
3. rerank_documents: Rerank by relevance
4. generate_response: LLM with context
5. validate_response: Check quality
6. format_output: Format for user

Flow: 1 → 2 → 3 → 4 → 5 → [valid: 6 | invalid: 4]
```

---

### Example 2: Multi-Agent Research
```
Nodes:
1. plan_research: Supervisor creates plan
2. researcher_agent: Gathers information
3. critic_agent: Critiques findings
4. writer_agent: Drafts report
5. fact_checker_agent: Validates facts
6. supervisor_review: Final review
7. revise_report: Apply feedback
8. finalize: Format final output

Flow: 1 → 2 → 3 → [approved: 4 | revise: 2]
      4 → 5 → [valid: 6 | invalid: 7 → 4]
      6 → [approved: 8 | revise: 7 → 4]
```

---

### Example 3: Plan-Execute with Reflection
```
Nodes:
1. create_plan: Plan steps
2. execute_step: Run current step
3. reflect_on_step: Validate step output
4. advance_step: Move to next step
5. replan: Adjust plan if needed
6. aggregate_results: Combine step outputs
7. generate_final: Create final response

Flow: 1 → 2 → 3 → [good: 4 | bad: 5 → 2]
      4 → [more steps: 2 | done: 6] → 7
```

---

## Best Practices Summary

1. **Single Responsibility:** One node, one job
2. **Clear Dependencies:** Document what each node needs
3. **Appropriate Granularity:** Not too big, not too small (20-50 lines typical)
4. **Parallelize When Possible:** Identify independent nodes
5. **Error Handling:** Plan for failures
6. **Testability:** Design for easy testing
7. **Descriptive Names:** Make purpose obvious
8. **Inject Dependencies:** Don't hardcode
9. **Pure When Possible:** Minimize side effects
10. **Document Well:** Explain purpose and dependencies

---

**Remember:** Well-designed nodes make the graph maintainable, testable, and evolvable. Invest time in thoughtful decomposition - it's the foundation of quality implementation.
