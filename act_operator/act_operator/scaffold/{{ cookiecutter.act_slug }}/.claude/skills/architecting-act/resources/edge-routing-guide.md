# Edge and Routing Design Guide

A comprehensive guide for designing edges, conditional routing, and control flow in LangGraph.

## Edge Fundamentals

**Edges define how your graph flows.** They connect nodes and determine execution order.

**Three types of edges:**
1. **Normal Edges:** Fixed node-to-node connections
2. **Conditional Edges:** Dynamic routing based on state
3. **Dynamic Edges (Send API):** Parallel routing to multiple nodes

---

## Normal Edges

### What They Are
Direct connections from one node to another.

**Characteristics:**
- Fixed at design time
- Always follow same path
- Simple and predictable
- No decision logic

### When to Use
- Flow is always the same
- No branching needed
- Sequential processing
- Clear next step

### Design Pattern
```
Node A → Node B → Node C
```

**Example:**
```
validate_input → extract_info → format_output
```

---

## Conditional Edges

### What They Are
Edges that route based on state, enabling branching and loops.

**Characteristics:**
- Routing function evaluates state
- Returns node name (string) or list of node names
- Enables branching logic
- Central to dynamic workflows

### When to Use
- Different paths based on state
- Quality checks (pass/fail)
- Classification routing
- Loop conditions
- Multi-way branching

### Routing Function Signature
```
Function receives: current state
Function returns:
  - String (next node name)
  - List[str] (multiple next nodes in parallel)
  - END (finish execution)
```

---

## Routing Patterns

### Pattern 1: Binary Decision
**Use case:** Pass/fail, valid/invalid, continue/stop

**Logic:**
```
if state.is_valid:
    return "continue_node"
else:
    return "error_handler_node"
```

**Example scenarios:**
- Validation: valid → process, invalid → reject
- Quality check: good → finalize, bad → retry
- Completion: done → END, not_done → continue

---

### Pattern 2: Multi-Way Classification
**Use case:** Route based on category, type, priority

**Logic:**
```
if state.category == "urgent":
    return "high_priority_handler"
elif state.category == "normal":
    return "standard_handler"
else:
    return "low_priority_handler"
```

**Example scenarios:**
- Content routing: technical → expert_A, legal → expert_B, general → expert_C
- Risk level: high → deep_analysis, medium → standard_check, low → auto_approve
- Task type: research → researcher, code → coder, write → writer

---

### Pattern 3: State-Based Loop
**Use case:** Iterate until condition met

**Logic:**
```
if state.iteration_count < state.max_iterations and not state.is_complete:
    return "process_again"
else:
    return "finalize"
```

**Example scenarios:**
- Refinement loop: keep improving until quality threshold or max iterations
- Search loop: keep searching until answer found or attempts exhausted
- Validation loop: retry until valid or give up

---

### Pattern 4: Agent Selection
**Use case:** Multi-agent systems, select next agent

**Logic:**
```
# Based on last message or state analysis
if "needs research" in state.last_message:
    return "researcher_agent"
elif "needs code" in state.last_message:
    return "coder_agent"
else:
    return "supervisor_agent"
```

**Example scenarios:**
- Capability-based: route to agent with right tools
- Round-robin: cycle through agents
- Supervisor decides: LLM chooses next agent

---

### Pattern 5: Parallel Fan-Out
**Use case:** Send to multiple nodes simultaneously

**Logic:**
```
# Return list of node names for parallel execution
return ["node_A", "node_B", "node_C"]
```

**Example scenarios:**
- Independent tasks: research multiple topics in parallel
- Redundancy: try multiple approaches simultaneously
- Distributed work: split work across nodes

---

### Pattern 6: Completion Check
**Use case:** Determine if workflow should end

**Logic:**
```
if state.final_answer is not None:
    return END
else:
    return "continue_processing"
```

**Example scenarios:**
- Answer found: END
- Max iterations reached: END
- Error occurred: END
- Still processing: continue

---

## Dynamic Routing with Send API

### What It Is
LangGraph 1.0 Send API enables dynamic, data-driven parallelization.

**Characteristics:**
- Number of parallel branches unknown at design time
- Each branch gets different state subset
- Enables map-reduce pattern
- Powerful for batch processing

### When to Use
- Process list of items in parallel
- Number of items unknown at design time
- Each item needs independent processing
- Results aggregated after parallel work

### Send API Pattern
```
Routing function:
- Receives state with list of items
- Returns list of Send objects
- Each Send specifies: (node_name, state_subset)

Example:
return [
    Send("process_item", {"item": item1}),
    Send("process_item", {"item": item2}),
    Send("process_item", {"item": item3}),
]
```

### Map-Reduce Flow
```
          ┌─→ Send(process, item1) ─┐
Mapper ───┼─→ Send(process, item2) ─┼──→ Reducer
          └─→ Send(process, item3) ─┘
```

**Key Points:**
- Mapper node uses conditional edge with Send returns
- Process node receives individual item state
- Reducer receives results (via state reducer)
- Process node can have different state schema

---

## Loop Design

### Implementing Loops

**Loop Structure:**
```
Node A → Router → [continue: Node A | done: END]
            ↑           │
            └───────────┘
```

**Essential Components:**
1. **Loop body node:** Does the work
2. **Router:** Decides continue or exit
3. **Iteration tracker:** Count in state
4. **Exit conditions:** Max iterations, success, error

### Loop Anti-Patterns

❌ **Infinite Loop:**
**Problem:** No guaranteed exit condition
**Solution:** Always have max iteration limit

❌ **No Progress Tracking:**
**Problem:** Can't tell if making progress
**Solution:** Track iteration count, changes per iteration

❌ **No Early Exit:**
**Problem:** Keeps iterating even after success
**Solution:** Check completion condition first

### Loop Best Practices

✅ **Multiple Exit Conditions:**
- Success condition (goal achieved)
- Max iterations (prevent infinite loop)
- Error condition (unrecoverable failure)
- Timeout (if time-bound)

✅ **Progress Indicators:**
- Iteration counter in state
- Quality score per iteration
- Convergence metrics

✅ **State Accumulation:**
- Keep iteration history (for debugging)
- Track best result so far
- Log why each iteration happened

---

## Error Handling in Routing

### Error Routing Strategies

**Strategy 1: Error State Field**
```
Router checks state.error field:
if state.error:
    return "error_handler"
else:
    return "normal_path"
```

**Strategy 2: Try-Catch in Router**
```
Router evaluates complex condition:
try:
    # Routing logic
    return decide_next(state)
except Exception:
    return "error_handler"
```

**Strategy 3: Validation Node → Router**
```
Validation node sets state.is_valid
Router:
if state.is_valid:
    return "continue"
else:
    return "handle_invalid"
```

### Error Recovery Patterns

**Pattern 1: Retry with Limit**
```
if state.error and state.retry_count < MAX_RETRIES:
    return "retry_node"
else:
    return "give_up_node"
```

**Pattern 2: Fallback Chain**
```
if state.primary_failed and not state.fallback_tried:
    return "fallback_approach"
elif state.fallback_failed:
    return "ultimate_fallback"
else:
    return "continue"
```

**Pattern 3: Escalation**
```
if state.error_severity == "low":
    return "auto_recover"
elif state.error_severity == "medium":
    return "supervisor_review"
else:
    return "human_intervention"
```

---

## Routing Decision Complexity

### Simple Routing
**Characteristics:**
- One or two conditions
- Clear binary/ternary choice
- Fast evaluation

**Example:**
```
return "next_node" if state.is_ready else "wait_node"
```

---

### Moderate Routing
**Characteristics:**
- 3-5 conditions
- Classification logic
- May use helper functions

**Example:**
```
category = classify_request(state.request)
return CATEGORY_TO_NODE[category]
```

---

### Complex Routing
**Characteristics:**
- > 5 conditions
- May call LLM for decision
- Sophisticated logic

**Example:**
```
# LLM decides next agent
decision = llm.invoke(f"Who should handle: {state.task}")
return parse_agent_name(decision)
```

**Warning:** Complex routing may indicate need to split into:
1. Decision node (makes choice, updates state)
2. Simple router (reads state.next_node)

---

## Entry and Exit Points

### Entry Point (START)
**What:** Where execution begins
**Design:**
- START → first_node
- First node typically validation or initialization

**Example:**
```
START → validate_input → [valid: process | invalid: END]
```

---

### Exit Points (END)
**What:** Where execution terminates
**Design:**
- Multiple paths can lead to END
- Conditional routing often has END option
- Completion routers return END

**Example:**
```
completion_router:
  if state.final_answer:
      return END
  elif state.iteration_count >= MAX:
      return END
  else:
      return "continue"
```

**Best Practice:** Document all END paths and their meaning:
- Success END: task completed
- Failure END: error or timeout
- Early EXIT END: user cancelled or invalid input

---

## Subgraph Routing

### Routing to Subgraphs
**What:** Edge from parent graph node to subgraph

**Characteristics:**
- Subgraph runs as single unit
- Returns to parent when complete
- State flows in and out

**Pattern:**
```
Parent Node → Subgraph (runs internally) → Parent Node
```

### Routing within Subgraphs
**What:** Edges inside subgraph are independent

**Characteristics:**
- Subgraph has own internal routing
- Parent graph sees subgraph as single node
- Subgraph can have loops, conditions, etc.

---

## Routing Documentation

### Document Each Router
**Template:**
```
Router: <name>
Purpose: <what decision it makes>
Inputs (state fields read): <fields>
Outputs (possible next nodes): <node names>
Logic: <brief description>
Special cases: <edge cases, errors>
```

**Example:**
```
Router: route_by_quality
Purpose: Decide if output meets quality threshold
Inputs: quality_score, iteration_count
Outputs:
  - "finalize" (score >= 0.8)
  - "improve" (score < 0.8 and iteration_count < 5)
  - "give_up" (iteration_count >= 5)
Logic: Check quality score and iteration limit
Special cases: If quality_score is None, route to "error"
```

---

## Routing Anti-Patterns

### ❌ God Router
**Problem:** One router making too many different decisions
**Solution:** Split into multiple focused routers

### ❌ Implicit Routing Logic
**Problem:** Routing decisions not documented or clear
**Solution:** Document all routing logic and conditions

### ❌ Duplicate Routing Logic
**Problem:** Same decision logic in multiple routers
**Solution:** Extract to helper function or dedicated node

### ❌ Stateful Router
**Problem:** Router modifies state (should only read)
**Solution:** Move state updates to nodes, routers only read

### ❌ Non-Deterministic Router Without Reason
**Problem:** Router gives different results for same state randomly
**Solution:** Make randomness explicit with seed in state

---

## Advanced Routing Patterns

### Pattern: Human-in-the-Loop
**Use case:** Route to human approval when needed

**Logic:**
```
if state.needs_human_approval:
    return "await_human_input"
else:
    return "continue_automated"
```

**State requirements:**
- `needs_human_approval` flag
- `human_response` field (set by external system)
- Timeout mechanism

---

### Pattern: Confidence-Based Routing
**Use case:** Route based on confidence scores

**Logic:**
```
if state.confidence > 0.9:
    return "high_confidence_path"
elif state.confidence > 0.6:
    return "medium_confidence_path"
else:
    return "low_confidence_path"
```

**Example scenarios:**
- High confidence: auto-approve
- Medium: additional validation
- Low: human review

---

### Pattern: Resource-Based Routing
**Use case:** Route based on available resources

**Logic:**
```
if state.budget_remaining > EXPENSIVE_THRESHOLD:
    return "premium_model_node"
else:
    return "budget_model_node"
```

**Example scenarios:**
- GPU available: use local model
- API credits available: use cloud model
- Time remaining: fast vs thorough approach

---

### Pattern: Adaptive Routing
**Use case:** Route based on historical performance

**Logic:**
```
if state.approach_A_success_rate > state.approach_B_success_rate:
    return "approach_A"
else:
    return "approach_B"
```

**State requirements:**
- Performance metrics
- Historical data
- Success rate tracking

---

## Routing Testing Considerations

### Test Each Routing Path
**For each router:**
- Test all possible return values
- Test edge cases (None values, empty lists, etc.)
- Test boundary conditions (thresholds)
- Test error conditions

**Example test cases for quality router:**
- score = 0.9 → "finalize"
- score = 0.5, iteration = 2 → "improve"
- score = 0.5, iteration = 5 → "give_up"
- score = None → "error"

---

## Routing Performance Considerations

### Fast Routing
**Characteristics:**
- Simple conditionals
- No LLM calls
- No expensive computations
- < 10ms typical

**Use for:**
- High-frequency decisions
- Real-time systems
- Simple classification

---

### Slow Routing
**Characteristics:**
- LLM-based decisions
- Complex computations
- May involve external calls
- > 100ms typical

**Use for:**
- Complex decisions requiring reasoning
- When accuracy > speed
- Infrequent routing

**Optimization:** Consider moving LLM decision to node, router reads node's decision from state

---

## Routing Checklist

Before finalizing edge/routing design:

- [ ] All nodes have outgoing edges (or return END)
- [ ] All routers documented (inputs, outputs, logic)
- [ ] Loop exit conditions defined (success, max iterations, error)
- [ ] Error routing paths defined
- [ ] No infinite loops possible
- [ ] Parallel opportunities using Send API identified
- [ ] Entry point (START) clearly defined
- [ ] Exit points (END) clearly documented
- [ ] Complex routers justified (or split into node + simple router)
- [ ] All routing paths tested conceptually

---

## Example Routing Architectures

### Example 1: Simple Linear with Validation
```
START → validate → [valid: process → END | invalid: END]
```

---

### Example 2: ReAct Loop
```
START → agent → route_action
                 ├─ tool_call → tool → agent (loop)
                 └─ final_answer → END
```

---

### Example 3: Multi-Agent with Supervisor
```
START → supervisor_plan → route_agent
                           ├─ researcher → supervisor_review
                           ├─ coder → supervisor_review
                           └─ writer → supervisor_review
supervisor_review → [done: END | continue: route_agent]
```

---

### Example 4: Map-Reduce with Send
```
START → mapper → [Send(process, item1) | Send(process, item2) | ...] → reducer → END
```

---

### Example 5: Plan-Execute with Reflection
```
START → plan → execute_step → reflect → route_quality
                                         ├─ good: next_step
                                         └─ bad: replan → execute_step
next_step → [more: execute_step | done: END]
```

---

## Best Practices Summary

1. **Document All Routers:** Make routing logic explicit
2. **Prevent Infinite Loops:** Always have exit conditions
3. **Test All Paths:** Ensure every route is reachable and correct
4. **Keep Routers Simple:** Complex logic → node, simple routing → router
5. **Use Send for Dynamic Parallelism:** When fan-out is data-driven
6. **Plan Error Routes:** Every node should have error path
7. **Track Iterations:** Always count loops
8. **Clear Entry/Exit:** Document START and all ENDs
9. **Avoid God Routers:** Split complex routing
10. **Consider Performance:** LLM routing is slow, use when justified

---

**Remember:** Edges and routing define the intelligence of your graph's control flow. Well-designed routing makes workflows adaptive, robust, and maintainable.
