# Workflow Pattern Decision Framework

A decision framework for selecting the right LangGraph workflow pattern based on requirements.

## Pattern Selection Decision Tree

```
START: What type of task are you building?

├─ Simple sequential task with tool calls?
│  └─→ **ReAct Pattern**
│
├─ Complex multi-step task requiring upfront planning?
│  └─→ **Plan-Execute Pattern**
│
├─ Task requiring quality validation and iteration?
│  └─→ **Reflection Pattern**
│
├─ Processing multiple items independently?
│  └─→ **Map-Reduce Pattern**
│
├─ Multiple specialized agents collaborating?
│  └─→ **Multi-Agent Pattern**
│
└─ Custom complex workflow?
   └─→ **Custom Graph Pattern**
```

## Pattern Catalog

### 1. ReAct Pattern (Reasoning + Acting)

**What it is:**
Iterative cycle where agent reasons about what to do, takes action, observes results, and repeats until task complete.

**Decision Criteria - Use when:**
- Task requires tool usage but sequence isn't predetermined
- Agent needs to adapt based on tool results
- Task is exploratory or question-answering
- Latency requirements are low to medium (< 60 sec)
- User wants simple, proven pattern

**Decision Criteria - DON'T use when:**
- You know exact sequence of steps upfront
- Task requires complex upfront planning
- Need to minimize LLM calls for cost
- Multiple independent subtasks exist

**Characteristics:**
- **Flow:** Reason → Act → Observe → Repeat
- **State:** Messages, tool outputs, scratchpad
- **Nodes:** Agent node (LLM), Tool nodes, Router
- **Edges:** Conditional routing based on agent decision

**When to enhance:**
- Add Reflection if quality is critical
- Add Plan-Execute wrapper for complex goals
- Use Multi-Agent if specialized expertise needed

---

### 2. Plan-Execute Pattern

**What it is:**
Separate planning phase from execution. Agent creates multi-step plan, then executes each step, optionally replanning.

**Decision Criteria - Use when:**
- Task is complex with multiple clear steps
- Upfront planning improves success rate
- Want to minimize LLM calls (smaller model for execution)
- Task has sub-goals that can be enumerated
- Latency tolerance is medium to high (> 30 sec)

**Decision Criteria - DON'T use when:**
- Task is highly dynamic/unpredictable
- Planning overhead outweighs benefits
- Single-step task with tools
- Real-time interaction required

**Characteristics:**
- **Flow:** Plan → Execute Step 1 → ... → Execute Step N → Complete
- **State:** Plan (list of steps), current step, results per step
- **Nodes:** Planner node, Executor node(s), Replanner (optional)
- **Edges:** Sequential through steps, conditional replan

**Variations:**
- **Strict Plan-Execute:** Follow plan exactly
- **Adaptive Plan-Execute:** Replan after each step
- **Hierarchical Plan-Execute:** Nested plans for complex steps

**When to enhance:**
- Add Reflection after each step for quality
- Use Map-Reduce for parallel step execution
- Combine with Multi-Agent for specialized executors

---

### 3. Reflection Pattern

**What it is:**
Agent generates output, reflects/critiques it, then improves based on reflection. Iterates until quality threshold met.

**Decision Criteria - Use when:**
- Output quality is critical
- Initial attempts often need refinement
- External validation criteria exist
- Latency tolerance is high (> 60 sec)
- Cost of mistakes is high

**Decision Criteria - DON'T use when:**
- First attempt is usually good enough
- No clear quality criteria
- Latency must be minimal
- Reflection won't add value

**Characteristics:**
- **Flow:** Generate → Reflect → Improve → Repeat (until satisfied)
- **State:** Current output, reflection notes, iteration count
- **Nodes:** Generator node, Reflector node, Improvement node
- **Edges:** Loop until quality threshold or max iterations

**Reflection Approaches:**
- **Self-Reflection:** Same LLM critiques own work
- **External Reflection:** Tool/validator provides feedback
- **Peer Reflection:** Different agent critiques
- **Multi-Aspect Reflection:** Multiple reflection dimensions

**When to enhance:**
- Combine with Plan-Execute (reflect on plan quality)
- Use with ReAct (reflect on tool usage)
- Add Human-in-Loop for critical validations

---

### 4. Map-Reduce Pattern

**What it is:**
Split work into independent subtasks (Map), process in parallel, aggregate results (Reduce).

**Decision Criteria - Use when:**
- Multiple independent items to process
- Each item processing doesn't depend on others
- Parallelization improves performance
- Items share same processing logic
- Number of items unknown at design time

**Decision Criteria - DON'NOT use when:**
- Items must be processed sequentially
- Processing depends on previous results
- Single item to process
- Coordination overhead > parallelization benefit

**Characteristics:**
- **Flow:** Split → Process_1 | Process_2 | ... | Process_N → Aggregate
- **State:** Items list, individual results, aggregated result
- **Nodes:** Mapper (uses Send API), Worker nodes (parallel), Reducer
- **Edges:** Dynamic parallel edges via Send, convergence to reducer

**Implementation Notes:**
- Use LangGraph Send API for dynamic parallel edges
- Each worker gets different state subset
- Reducer receives all worker outputs
- Consider defer pattern for synchronization

**When to enhance:**
- Add Reflection to worker nodes for quality
- Use Hierarchical Map-Reduce for nested parallelism (carefully!)
- Combine with Plan-Execute for complex aggregation

---

### 5. Multi-Agent Pattern

**What it is:**
Multiple specialized agents collaborate, each with own expertise, tools, and prompts.

**Decision Criteria - Use when:**
- Task requires distinct expertise areas
- Different tools/permissions per role
- Collaboration improves output quality
- Task naturally decomposes by role/specialty
- Want modularity and reusability

**Decision Criteria - DON'T use when:**
- Single agent can handle everything
- No clear role boundaries
- Coordination overhead too high
- Simple task doesn't warrant complexity

**Characteristics:**
- **Flow:** Varies (sequential, parallel, hierarchical, network)
- **State:** Shared scratchpad (messages) or isolated states
- **Nodes:** One node per agent + supervisor/router
- **Edges:** Determines collaboration pattern

**Collaboration Patterns:**
- **Sequential:** Agent A → Agent B → Agent C
- **Parallel:** All agents work simultaneously, aggregate
- **Hierarchical:** Supervisor delegates to workers
- **Network:** Agents message each other dynamically

**When to enhance:**
- Add Reflection for agent output quality
- Use Map-Reduce for parallel agent work
- Implement Human-in-Loop for oversight

---

### 6. Custom Graph Pattern

**What it is:**
Fully custom graph designed for specific complex requirements not fitting standard patterns.

**Decision Criteria - Use when:**
- Standard patterns don't fit requirements
- Unique control flow needed
- Combining multiple patterns
- Specific business logic requires custom design

**Decision Criteria - DON'T use when:**
- Standard pattern would work (prefer simplicity)
- Team unfamiliar with graph design
- Maintenance burden too high

**Design Approach:**
1. Identify all required states
2. Map out nodes (single responsibilities)
3. Define edges and routing logic
4. Consider error handling flows
5. Document rationale extensively

---

## Pattern Combinations

Patterns can be combined for sophisticated workflows:

### Plan-Execute + Reflection
- Planner creates plan
- Executor runs each step
- Reflector validates step output
- Replanner adjusts if needed
**Use for:** Complex tasks requiring quality assurance

### ReAct + Multi-Agent
- Multiple ReAct agents with different tools
- Router selects agent based on task
**Use for:** Complex tool-using tasks with specialization

### Map-Reduce + Reflection
- Process items in parallel (Map)
- Each worker reflects on its output
- Reduce aggregates validated results
**Use for:** Batch processing with quality requirements

### Hierarchical Multi-Agent
- Supervisor plans and delegates
- Worker agents execute with ReAct/Plan-Execute
- Supervisor aggregates and decides next steps
**Use for:** Complex multi-role workflows

---

## Selection Decision Matrix

| Requirement | ReAct | Plan-Execute | Reflection | Map-Reduce | Multi-Agent |
|-------------|-------|--------------|------------|------------|-------------|
| Simple task | ✓✓✓ | ✗ | ✗ | ✗ | ✗ |
| Complex planning | ✗ | ✓✓✓ | ✓ | ✗ | ✓ |
| Quality critical | ✓ | ✓ | ✓✓✓ | ✓ | ✓✓ |
| Parallel work | ✗ | ✗ | ✗ | ✓✓✓ | ✓✓ |
| Tool usage | ✓✓✓ | ✓✓ | ✓ | ✓ | ✓✓✓ |
| Specialization | ✗ | ✗ | ✗ | ✗ | ✓✓✓ |
| Low latency | ✓✓✓ | ✗ | ✗ | ✓✓ | ✗ |
| Cost efficiency | ✓✓ | ✓✓✓ | ✗ | ✓ | ✓ |

**Legend:** ✓✓✓ Excellent | ✓✓ Good | ✓ Adequate | ✗ Poor fit

---

## Latency Considerations

### Low Latency (< 10 sec)
- **Recommended:** ReAct (simple), Custom sequential
- **Avoid:** Reflection, Plan-Execute, Multi-Agent
- **Tips:** Minimize LLM calls, use streaming, small models

### Medium Latency (10-60 sec)
- **Recommended:** ReAct, Plan-Execute, Map-Reduce
- **Possible:** Multi-Agent (2-3 agents), light Reflection
- **Tips:** Parallelize where possible, batch operations

### High Latency (> 60 sec)
- **Recommended:** All patterns viable
- **Best fit:** Plan-Execute, Reflection, Multi-Agent, Combinations
- **Tips:** Focus on quality and correctness over speed

---

## Anti-Patterns in Pattern Selection

### ❌ Over-Engineering
**Problem:** Using complex pattern (Multi-Agent, Reflection) for simple task
**Solution:** Start with simplest pattern (ReAct), add complexity only if needed

### ❌ Wrong Pattern for Problem
**Problem:** Using ReAct when clear steps exist (should be Plan-Execute)
**Solution:** Match pattern characteristics to task requirements

### ❌ Pattern Mixing Without Rationale
**Problem:** Combining patterns randomly hoping for better results
**Solution:** Combine patterns intentionally to solve specific limitations

### ❌ Ignoring Latency Constraints
**Problem:** Using Reflection pattern when user needs instant response
**Solution:** Check latency requirements before pattern selection

---

## Pattern Selection Process

**Step 1: Understand Requirements**
- What is the task?
- What are the inputs/outputs?
- What are latency requirements?
- What quality standards exist?

**Step 2: Check Decision Tree**
- Follow decision tree to initial recommendation
- Consider alternatives from matrix

**Step 3: Validate Choice**
- Does pattern match latency needs?
- Does pattern handle task complexity?
- Is pattern appropriate for team skill level?

**Step 4: Consider Enhancements**
- Would pattern combination add value?
- Is complexity justified?

**Step 5: Document Rationale**
- Why this pattern?
- What alternatives considered?
- What trade-offs accepted?

---

## References & Further Reading

- **LangGraph 1.0 Patterns:** Official docs at langchain-ai.github.io/langgraph
- **ReAct Paper:** "ReAct: Synergizing Reasoning and Acting in Language Models"
- **Reflection Techniques:** Reflexion, LATS implementations
- **Plan-and-Solve:** "Plan-and-Solve Prompting" paper
- **Multi-Agent Systems:** LangGraph multi-agent tutorials

---

**Remember:** The best pattern is the simplest one that meets requirements. Start simple, iterate based on real needs.
