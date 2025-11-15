# Baseline Test Findings (RED Phase)

## Test Date: 2025-11-15
## Scenario: Complex Multi-Component Cast (Research Assistant)

---

## What Agent Got RIGHT ✓

### 1. State Management Fundamentals
- Correctly used TypedDict for state schema
- Properly applied `Annotated[list, operator.add]` for append-only semantics
- Distinguished between plain fields (overwrite) and reducer fields (append)
- Understood MessagesState inheritance

### 2. Tool Creation Basics
- Used `@tool` decorator correctly
- Placed tools in `modules/tools.py` (correct Act convention!)
- Understood that docstrings become tool descriptions
- Showed parameter typing for tool schema

### 3. Node OOP Pattern
- Correctly inherited from `BaseNode`
- Used `execute(self, state)` signature
- Showed instance creation for add_node
- Demonstrated self.log() for debugging

### 4. Routing Logic
- Created separate conditions.py file
- Router functions with `(state) -> str` signature
- Used add_conditional_edges with mapping
- Understood fallback routing

### 5. Graph Construction
- Correct StateGraph instantiation
- add_node, add_edge, set_entry_point/START pattern
- Compilation with checkpointer
- Input/output schema separation

### 6. Memory Conceptual Understanding
- Distinguished short-term (checkpointer) from long-term (Store)
- Identified MemorySaver vs SqliteSaver
- Understood thread-scoped vs cross-session

---

## UNCERTAINTIES and GAPS ⚠️

### 1. Store API Initialization ⚠️⚠️⚠️
**What was shown:**
```python
if runtime and runtime.store:
    runtime.store.put(namespace, key, value)
```

**Uncertainties:**
- How to initialize Store (InMemoryStore, MongoDBStore)?
- Where to pass Store to graph (in compile? separate config?)?
- Exact Store API methods (put, get, search)?
- Namespace structure and conventions?

**Impact:** HIGH - Cross-session memory won't work without this

---

### 2. Tool Integration Patterns ⚠️⚠️
**What was shown:**
- Direct tool invocation: `web_search.invoke({"query": query})`
- Mentioned ToolRuntime but didn't fully explain
- Mentioned bind_tools and ToolNode but unsure when to use

**Uncertainties:**
- When to use direct invocation vs ToolNode vs bind_tools?
- How does ToolNode work with state?
- What is ToolRuntime and how to access it?
- Exact tool invocation syntax?

**Impact:** MEDIUM - Tools might not integrate correctly

---

### 3. Async Patterns ⚠️
**What was shown:**
- Mentioned AsyncBaseNode
- Noted `ainvoke()` vs `invoke()` distinction
- Recognized async checkpointer issue

**Uncertainties:**
- When exactly to use async vs sync?
- How to implement async nodes?
- What happens if you mix async/sync?
- Performance implications?

**Impact:** MEDIUM - Could cause hangs or performance issues

---

### 4. Runtime Context Access ⚠️
**What was shown:**
```python
def execute(self, state, runtime=None):
```

**Uncertainties:**
- Is it `runtime`, `context`, or `config`?
- What's available in runtime?
- How to access Store, config, etc.?
- Is this Act-specific or LangGraph standard?

**Impact:** HIGH for Act projects - ToolRuntime is critical

---

### 5. Error Handling Patterns ⚠️
**What was missing:**
- No try/except patterns shown
- No retry logic
- No timeout handling
- No error recovery strategies

**Impact:** HIGH - Production code needs this

---

### 6. Streaming Implementation ⚠️
**What was mentioned:**
- astream_events exists
- Mentioned token streaming
- Marked as "implement later"

**Uncertainties:**
- How to actually use astream_events?
- What events to filter for?
- How to stream tokens?
- How to stream state updates?

**Impact:** MEDIUM - Nice to have, not critical

---

### 7. Interrupt/Human-in-the-Loop ⚠️
**What was missing:**
- No mention of interrupt() function
- No approval patterns shown
- Not addressed in implementation

**Impact:** LOW for this scenario, but HIGH for other use cases

---

## POTENTIAL MISTAKES and ANTI-PATTERNS ❌

### 1. File Structure Confusion ❌
**What was shown:**
```
modules/
  ├── state.py
  ├── nodes.py
  ├── tools.py
```

**Act Convention (need to verify):**
```
casts/cast_name/
  ├── state.py      # At cast root, not in modules?
  ├── nodes.py      # At cast root?
  ├── graph.py
  └── modules/
      ├── tools.py  # Tools MUST be here
      └── ...
```

**Impact:** MEDIUM - File organization matters for imports

---

### 2. Tool Invocation Syntax ❌
**What was shown:**
```python
web_search.invoke({"query": query})
```

**Possible Issues:**
- May need `web_search.invoke(query)` (direct arg)
- Or `web_search.invoke(input={"query": query})`
- Depends on tool definition

**Impact:** HIGH - Tool calls might fail

---

### 3. Reducer Return Type Mismatch ❌
**What was shown:**
```python
research_topics: Annotated[list[str], operator.add]

# In node:
return {"research_topics": new_topics}  # Must be list!
```

**Possible Issue:**
- If new_topics is not a list, operator.add will fail
- Need to ensure type consistency

**Impact:** HIGH - Runtime errors

---

### 4. Missing BaseGraph Explanation ❌
**What was shown:**
- Inheritance from BaseGraph
- build() method
- But no explanation of BaseGraph API

**Impact:** HIGH for Act projects - BaseGraph is core

---

### 5. State Schema Location ❌
**Uncertainty:**
- Is state.py in modules/ or at cast root?
- Act conventions unclear

**Impact:** MEDIUM - Affects imports

---

### 6. Missing Middleware, Agents ❌
**What wasn't addressed:**
- Middleware patterns (mentioned in Act structure but not used)
- Agent patterns (when to use prebuilt agents?)
- Prompts integration with nodes

**Impact:** LOW for this scenario

---

## KEY INSIGHTS for Skill Design

### 1. Strong Foundation Exists ✓
- Agent understands LangGraph 1.0 basics well
- Knows about modern APIs (interrupt vs NodeInterrupt)
- Conceptual understanding is solid

### 2. Gaps Are in Details ⚠️
- **Store initialization and usage** - CRITICAL gap
- **ToolRuntime patterns** - Act-specific, needs clear explanation
- **File structure** - Act conventions need clarity
- **Error handling** - Missing entirely

### 3. Decision Frameworks Needed ⚠️
- **When to use:** bind_tools vs ToolNode vs direct invocation?
- **When to use:** async vs sync nodes?
- **When to use:** MemorySaver vs SqliteSaver vs Store?
- **Where to put:** state, nodes, tools, conditions?

### 4. Code Examples Must Be Minimal ✓
- Agent created comprehensive examples
- But some were overly verbose
- Skill should show MINIMAL patterns, not full implementations

### 5. Act Conventions Are CRITICAL ⚠️⚠️⚠️
- Tools location is understood
- BaseNode inheritance is understood
- But BaseGraph, ToolRuntime, file structure need reinforcement

---

## Priority Order for Skill Resources

### CRITICAL (Must have, < 2k tokens):
1. **state-management.md** - Reducers, TypedDict, channels
2. **node-patterns.md** - BaseNode, execute signature, OOP
3. **tool-creation.md** - @tool, proper invocation, ToolRuntime
4. **act-conventions.md** - File structure, BaseGraph, where to put what
5. **graph-construction.md** - StateGraph, compilation, execution

### HIGH PRIORITY (< 4k tokens):
6. **long-term-memory.md** - Store initialization and usage (major gap!)
7. **error-handling.md** - Try/except, retries, timeouts (completely missing)
8. **tool-runtime.md** - Act-specific ToolRuntime patterns

### MEDIUM PRIORITY (< 4k tokens):
9. **edge-patterns.md** - Conditional routing, dynamic routing
10. **short-term-memory.md** - Checkpointers, thread-scoped
11. **async-patterns.md** - When to use, how to implement
12. **interrupts.md** - interrupt() function, approval patterns

### LOWER PRIORITY (< 4k tokens):
13. **streaming.md** - astream_events, token streaming
14. **subgraphs.md** - Composition patterns
15. **mcp-integration.md** - MCP Adapter usage

---

## Validation Criteria

After creating skill, retest with same scenario and verify:

### Must Fix:
- [ ] Store initialization and usage is clear
- [ ] ToolRuntime pattern is explained
- [ ] File structure follows Act conventions
- [ ] Error handling patterns included
- [ ] Tool invocation syntax is correct

### Should Improve:
- [ ] Decision frameworks for tool integration
- [ ] Async vs sync guidance clear
- [ ] Memory placement decisions clear

### Nice to Have:
- [ ] Streaming examples
- [ ] Interrupt patterns
- [ ] Subgraph composition

---

## Quotes from Baseline (Verbatim Uncertainties)

> "**Uncertainty:** How to initialize and configure Store (InMemoryStore, MongoDBStore) in the graph"

> "**Uncertainty:** Whether to use `bind_tools()` or `ToolNode` pattern for automatic tool calling"

> "**Uncertainty:** When to use `AsyncBaseNode` vs `BaseNode`"

> "**Uncertainty:** Where and how to initialize the Store"

> "I showed `runtime.store` access but haven't verified the exact initialization pattern"

> "I used `.invoke({"query": query})` but the exact parameter structure depends on how the tool is defined"

These uncertainties are EXACTLY what the skill must address with clear, verified patterns.
