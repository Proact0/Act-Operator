# Architectural Anti-Patterns

Common mistakes in LangGraph architecture design and how to avoid them.

## State Anti-Patterns

### ❌ Kitchen Sink State
**Problem:** State has too many fields (20+)
**Solution:** Keep only essential fields, group related data, separate input/working/output clearly

### ❌ Missing Reducers
**Problem:** Accumulating fields (lists/dicts) without reducers
**Solution:** Add `Annotated[list[T], operator.add]` for lists, merge functions for dicts

### ❌ No Metadata
**Problem:** No iteration counters, timestamps, or error tracking
**Solution:** Include `iteration: int`, `errors: list[str]`, `total_tokens: int`

---

## Node Anti-Patterns

### ❌ God Node
**Problem:** One node doing too much (>100 lines, multiple responsibilities)
**Solution:** Decompose into focused nodes with single responsibility each

### ❌ Chatty Nodes
**Problem:** Too many tiny nodes (>20 nodes total) just passing data
**Solution:** Merge related trivial nodes, aim for 5-15 meaningful nodes

### ❌ Hidden Dependencies
**Problem:** Node depends on undocumented state fields
**Solution:** Document all reads/writes, validate required fields at entry

### ❌ Generic Names
**Problem:** Nodes named `process`, `handle`, `manage`
**Solution:** Use specific verb-based names: `extract_key_info`, `validate_response`

---

## Routing Anti-Patterns

### ❌ Infinite Loop
**Problem:** Loop without max iteration limit
**Solution:** Always include max iteration check and success condition
```
if state.success or state.iteration >= MAX:
    return END
```

### ❌ God Router
**Problem:** One router with >10 branches for unrelated decisions
**Solution:** Split into focused routers, one per decision type

### ❌ No Error Routing
**Problem:** Only happy path, no error handling
**Solution:** Add error paths: `[success: next | error: error_handler]`

### ❌ Stateful Router
**Problem:** Router modifies state instead of just reading
**Solution:** Routers read only, nodes update state

---

## Pattern Selection Anti-Patterns

### ❌ Over-Engineering
**Problem:** Multi-agent or Reflection for simple tasks
**Solution:** Start with ReAct, add complexity only when needed

### ❌ Under-Engineering
**Problem:** ReAct for complex multi-step planning tasks
**Solution:** Use Plan-Execute when upfront planning helps

### ❌ Pattern/Latency Mismatch
**Problem:** Reflection or Multi-Agent with low latency (<10s) requirements
**Solution:** Complex patterns increase latency; match pattern to requirements

---

## Subgraph Anti-Patterns

### ❌ Subgraph Hell
**Problem:** Too many tiny subgraphs (<3 nodes each)
**Solution:** Only extract subgraphs with >3-4 nodes and clear benefit

### ❌ God Subgraph
**Problem:** One massive subgraph (>20 nodes)
**Solution:** Break into focused subgraphs, 5-10 nodes each

### ❌ Premature Extraction
**Problem:** Creating subgraphs before workflow is stable
**Solution:** Wait until pattern emerges, start flat and refactor later

### ❌ Tight Coupling
**Problem:** Subgraph needs 80% of parent state
**Solution:** Define focused interface, pass only required fields

---

## Process Anti-Patterns

### ❌ Skipping Architecture
**Problem:** Jumping straight to implementation
**Solution:** Always create CLAUDE.md, think through state/nodes/edges first

### ❌ Analysis Paralysis
**Problem:** Weeks on architecture, no code
**Solution:** Set time limit, start with MVP design, iterate

### ❌ No Validation
**Problem:** Architecture not validated before implementation
**Solution:** Run `validate_architecture.py`, check anti-patterns

### ❌ Ignoring Latency
**Problem:** Designing without considering latency requirements
**Solution:** Ask about latency early (Stage 2), choose pattern accordingly

### ❌ Assuming Intent
**Problem:** Designing without clarifying questions
**Solution:** Ask strategic questions (Stage 1), confirm understanding

---

## Red Flags Checklist

**State Design:**
- [ ] >15 state fields (Kitchen Sink?)
- [ ] Lists/dicts without reducers (Missing Reducers?)
- [ ] No metadata fields (No Metadata?)

**Node Design:**
- [ ] Node >100 lines (God Node?)
- [ ] >20 nodes total (Chatty Nodes?)
- [ ] Undocumented dependencies (Hidden Dependencies?)

**Routing:**
- [ ] Loop without max iterations (Infinite Loop?)
- [ ] Router >10 branches (God Router?)
- [ ] No error paths (No Error Routing?)

**Pattern:**
- [ ] Multi-agent for simple task (Over-Engineering?)
- [ ] ReAct for complex planning (Under-Engineering?)
- [ ] Wrong pattern for latency (Mismatch?)

**Subgraphs:**
- [ ] Subgraphs <3 nodes (Hell?)
- [ ] Subgraph >20 nodes (God Subgraph?)
- [ ] Unstable interface (Premature?)

**Process:**
- [ ] No CLAUDE.md (Skipping?)
- [ ] Week+ on architecture (Paralysis?)
- [ ] Latency not discussed (Ignoring?)

---

## Quick Fixes

**If you detect these anti-patterns:**

1. **Identify**: Use validation script, checklist above
2. **Prioritize**: High-impact issues first
3. **Refactor**: One change at a time
4. **Validate**: Re-run validation after each fix

**Prevention:**
- Review checklist during Stage 3 (Design)
- Run validation before Stage 4 (Finalization)
- Apply SOLID principles throughout
- Document rationale for decisions

---

## Best Practices (Anti-Anti-Patterns)

### ✅ State
- Minimal focused fields (<15)
- Appropriate reducers for lists/dicts
- Metadata included (iteration, errors, costs)

### ✅ Nodes
- Single responsibility (20-50 lines)
- Clear documented dependencies
- Specific descriptive names

### ✅ Routing
- Multiple exit conditions (success, max iterations, error)
- Error paths for all nodes
- Simple focused routers

### ✅ Patterns
- Match pattern to task complexity
- Consider latency requirements
- Start simple, justify complexity

### ✅ Subgraphs
- Clear boundaries (>3 nodes, <20 nodes)
- Well-defined interface
- Independently testable

### ✅ Process
- Create CLAUDE.md always
- Ask strategic questions
- Validate before implementing
- Document rationale

---

**Remember:** Anti-patterns are learning opportunities. Recognize them early through the validation checklist, refactor thoughtfully, and apply best practices consistently.
