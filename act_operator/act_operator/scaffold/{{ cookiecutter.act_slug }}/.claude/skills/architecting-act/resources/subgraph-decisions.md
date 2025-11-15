# Subgraph Decision Framework

A comprehensive guide for deciding when and how to use subgraphs in LangGraph architectures.

## What Are Subgraphs?

**Subgraphs** (sub-casts in Act terminology) are complete graphs embedded as nodes within a parent graph.

**Key Characteristics:**
- Full graph with own nodes, edges, state
- Appears as single node to parent graph
- Can be reused across multiple parent graphs
- Encapsulates complexity
- Enables modularity

**Mental Model:**
```
Parent Graph sees:
  Node A → Subgraph → Node B

Subgraph internally:
  Entry → Internal Node 1 → Internal Node 2 → Exit
```

---

## When to Use Subgraphs

### Decision Tree

```
Do you need subgraphs?

├─ Is there a self-contained workflow within the larger workflow?
│  └─→ YES: Consider subgraph
│
├─ Will this component be reused in multiple graphs?
│  └─→ YES: Strongly consider subgraph
│
├─ Does a portion of the graph have > 5-7 nodes?
│  └─→ YES: Consider extracting to subgraph
│
├─ Is there a clear boundary with specific input/output?
│  └─→ YES: Good subgraph candidate
│
└─ Does the graph have distinct logical phases?
   └─→ YES: Each phase might be a subgraph
```

---

## Criteria for Subgraph Extraction

### ✅ Use Subgraphs When:

**1. Reusability**
- Same workflow needed in multiple places
- Component useful across different graphs
- Common pattern that could be a module

**Example:** Document processing subgraph used in:
- RAG system
- Document summarization
- Content extraction

---

**2. Encapsulation**
- Complex internal logic that parent doesn't need to know
- Clear input/output contract
- Self-contained responsibility

**Example:** "Research Topic" subgraph that:
- Takes: topic (string)
- Returns: research findings (structured)
- Internally: searches, validates, synthesizes (parent doesn't care how)

---

**3. Organizational Clarity**
- Large graph becoming hard to understand
- Natural logical boundaries exist
- Team structure (different teams own different subgraphs)

**Example:** Customer service system:
- Intent classification subgraph
- Query handling subgraph
- Response generation subgraph

---

**4. Parallel Execution (Map-Reduce)**
- Process multiple items with same workflow
- Each item runs through identical subgraph
- Results aggregated after

**Example:** Batch document analysis:
- Parent sends each document to analysis subgraph (via Send API)
- Each runs independently
- Parent aggregates results

---

**5. Versioning/Testing**
- Need different versions of same component
- A/B testing different approaches
- Gradual rollout of changes

**Example:**
- Parent routes to subgraph_v1 or subgraph_v2 based on config
- Test new approach without changing parent logic

---

### ❌ DON'T Use Subgraphs When:

**1. Over-Modularization**
- Only 2-3 simple nodes
- No reuse potential
- Adds complexity without benefit

**Anti-pattern:** Creating subgraph for every 2-node sequence

---

**2. Tight Coupling**
- Subgraph needs constant access to parent state
- Many state fields flow back and forth
- Boundary is artificial

**Anti-pattern:** Subgraph that needs 80% of parent state fields

---

**3. One-Time Use**
- Workflow only used once
- No encapsulation benefit
- No organizational benefit

**Exception:** If it significantly improves readability of complex graph

---

**4. Premature Abstraction**
- Requirements unclear
- Workflow still evolving rapidly
- Flexibility more important than structure

**Better:** Start flat, extract subgraphs when patterns emerge

---

## Subgraph Design Patterns

### Pattern 1: Reusable Component

**Structure:**
```
Parent A → Reusable Subgraph → Continue A
Parent B → Reusable Subgraph → Continue B
```

**Characteristics:**
- Single subgraph, multiple parents
- Generic interface (input/output)
- Well-defined contract

**Example:** Email validation subgraph used by:
- User registration flow
- Contact form flow
- Profile update flow

---

### Pattern 2: Complexity Encapsulation

**Structure:**
```
Parent: Node A → [Complex Subgraph] → Node B

Subgraph internally:
  Entry → 10+ nodes with complex routing → Exit
```

**Characteristics:**
- Hides complexity from parent
- Clear responsibility boundary
- Simplifies parent graph readability

**Example:** "Process Payment" subgraph hiding:
- Validation
- Fraud check
- Gateway selection
- Retry logic
- Receipt generation

---

### Pattern 3: Map-Reduce with Subgraph

**Structure:**
```
Parent:
  Mapper → [Send(Subgraph, item1) | Send(Subgraph, item2) | ...] → Reducer

Subgraph:
  Process single item → Return result
```

**Characteristics:**
- Subgraph is the "worker"
- Parent orchestrates parallelism
- Each invocation independent

**Example:** Batch sentiment analysis:
- Parent sends each review to sentiment subgraph
- Subgraph analyzes one review
- Parent aggregates sentiment scores

---

### Pattern 4: Hierarchical Delegation

**Structure:**
```
Parent (Supervisor):
  Decide task → Route to specialist subgraph → Review result

Subgraphs:
  - Research Specialist
  - Coding Specialist
  - Writing Specialist
```

**Characteristics:**
- Parent is high-level orchestrator
- Each subgraph is domain expert
- Clear role separation

**Example:** Multi-domain assistant:
- Parent identifies: code question vs research question
- Routes to appropriate specialist subgraph
- Specialist handles complexity

---

### Pattern 5: Sequential Phases

**Structure:**
```
Parent:
  Phase 1 Subgraph → Phase 2 Subgraph → Phase 3 Subgraph

Each subgraph:
  Internal workflow for that phase
```

**Characteristics:**
- Workflow naturally divided into phases
- Each phase complex enough for subgraph
- Clear phase transitions

**Example:** Content creation pipeline:
- Research phase subgraph
- Drafting phase subgraph
- Editing phase subgraph

---

## Parent-Subgraph Communication

### State Flow: Parent → Subgraph

**Pattern 1: Full State**
- Pass entire parent state to subgraph
- Subgraph can access everything
- **Use when:** Subgraph needs most of parent state

**Pattern 2: Subset State**
- Pass only required fields
- Cleaner interface
- **Use when:** Subgraph has focused responsibility

**Pattern 3: Transformed State**
- Parent node prepares specific subgraph input
- Subgraph has specialized state schema
- **Use when:** Subgraph is generic component

**Recommended:** Pattern 2 or 3 for better encapsulation

---

### State Flow: Subgraph → Parent

**Pattern 1: Merge into Parent State**
- Subgraph updates parent state fields directly
- **Use when:** Subgraph and parent share state schema

**Pattern 2: Output Field**
- Subgraph writes to specific output field
- Parent reads that field
- **Use when:** Clear output contract

**Pattern 3: Transformed Result**
- Parent node processes subgraph output
- **Use when:** Subgraph output needs adaptation

**Recommended:** Pattern 2 for clear contracts

---

## Subgraph State Schema Design

### Option 1: Shared Schema
**What:** Subgraph uses same state schema as parent

**Pros:**
- Simple
- Easy state flow
- No transformation needed

**Cons:**
- Tight coupling
- Subgraph less reusable
- Unclear dependencies

**Use when:** Subgraph is specific to one parent

---

### Option 2: Independent Schema
**What:** Subgraph has its own state schema

**Pros:**
- Clear interface
- Highly reusable
- Explicit contract
- Better testability

**Cons:**
- Need state transformation at boundary
- More setup

**Use when:** Subgraph is reusable component

**Pattern:**
```
Parent state:
  - user_query: str
  - documents: list[Doc]

Subgraph state (independent):
  - input_text: str
  - output_summary: str

Parent node before subgraph:
  - Transform parent state to subgraph input

Parent node after subgraph:
  - Extract subgraph output, update parent state
```

---

### Option 3: Extended Schema
**What:** Subgraph schema extends parent schema with additional fields

**Pros:**
- Can access parent state
- Can add internal working fields
- Flexible

**Cons:**
- Still coupled to parent schema
- Less reusable

**Use when:** Subgraph needs parent context plus own working state

---

## Nested Subgraphs

### What Are Nested Subgraphs?
Subgraphs that contain other subgraphs.

**Structure:**
```
Parent Graph
  └─ Subgraph A
       └─ Subgraph B
            └─ Subgraph C (potentially)
```

### When to Use Nested Subgraphs

**✅ Use when:**
- Natural hierarchical decomposition
- Each level has clear abstraction
- Organizational structure matches (teams, domains)

**Example:** E-commerce order processing:
- Parent: Order fulfillment
  - Subgraph: Payment processing
    - Nested subgraph: Fraud detection

---

### When NOT to Use Nested Subgraphs

**❌ Avoid when:**
- > 2-3 levels of nesting (gets confusing)
- No clear abstraction benefit
- Makes debugging difficult

**Warning:** Nested subgraphs increase complexity. Use judiciously.

---

## Subgraph Testing Strategy

### Unit Testing
**What:** Test subgraph in isolation
**How:** Provide mock input state, assert output state
**Benefit:** Fast, focused, independent

---

### Integration Testing
**What:** Test subgraph within parent graph
**How:** Run parent graph, verify subgraph behavior in context
**Benefit:** Catches interface issues

---

### Reusability Testing
**What:** Test subgraph with different parent graphs
**How:** Use subgraph in multiple parent graphs
**Benefit:** Validates reusability claim

---

## Subgraph Anti-Patterns

### ❌ Subgraph Hell
**Problem:** Too many tiny subgraphs
**Symptom:** More time navigating subgraphs than understanding logic
**Solution:** Merge related small subgraphs

---

### ❌ God Subgraph
**Problem:** One massive subgraph doing too much
**Symptom:** Subgraph has > 20 nodes, multiple responsibilities
**Solution:** Break into multiple focused subgraphs

---

### ❌ Circular Subgraph Dependencies
**Problem:** Subgraph A depends on B, B depends on A
**Symptom:** Can't test or use independently
**Solution:** Refactor to remove circular dependency

---

### ❌ Leaky Abstraction
**Problem:** Parent needs to know subgraph internals
**Symptom:** Parent routing depends on subgraph internal state
**Solution:** Improve subgraph interface, return clear status

---

### ❌ Premature Extraction
**Problem:** Creating subgraph before workflow is stable
**Symptom:** Constant subgraph interface changes
**Solution:** Wait until workflow stabilizes

---

## Subgraph Decision Checklist

Before creating a subgraph, verify:

- [ ] Clear, single responsibility
- [ ] Well-defined input/output contract
- [ ] Reusable OR significantly improves organization
- [ ] > 3-4 nodes (if smaller, probably not worth it)
- [ ] Can be tested independently
- [ ] Doesn't create tight coupling
- [ ] Parent graph is simpler with it than without
- [ ] Team agrees boundary makes sense
- [ ] Documentation exists for subgraph interface

---

## Subgraph Naming Conventions

**Good subgraph names:**
- Describe the workflow/capability
- Are specific, not generic
- Indicate level of abstraction

**Examples:**

| Purpose | ❌ Bad Name | ✅ Good Name |
|---------|------------|-------------|
| Document processing | `process_subgraph` | `document_extraction_pipeline` |
| Research task | `research` | `multi_source_research_synthesizer` |
| Validation | `check` | `content_quality_validator` |
| Payment flow | `payment` | `secure_payment_processor` |

---

## Example Subgraph Architectures

### Example 1: Reusable RAG Subgraph

**Parent graphs using it:**
- Customer support bot
- Document Q&A system
- Code assistant

**Subgraph (RAG):**
```
Input State:
  - query: str
  - context_docs: list[str]

Internal:
  - retrieve_relevant
  - rerank_by_relevance
  - generate_answer
  - validate_answer

Output State:
  - answer: str
  - sources: list[str]
```

---

### Example 2: Map-Reduce Analysis

**Parent:**
```
Input: list of articles

Mapper → [Send(analysis_subgraph, article1) | ...]→ Reducer
```

**Analysis Subgraph:**
```
Input State:
  - article_text: str

Internal:
  - extract_entities
  - extract_topics
  - score_sentiment

Output State:
  - entities: list[str]
  - topics: list[str]
  - sentiment: float
```

---

### Example 3: Hierarchical Multi-Agent

**Parent (Supervisor):**
```
plan → route_to_specialist → review → [done: END | continue: route]
```

**Specialist Subgraphs:**
- **Researcher:** Search → Validate → Synthesize
- **Coder:** Plan code → Write → Test → Debug
- **Writer:** Outline → Draft → Edit

Each specialist is complex enough to warrant subgraph.

---

## Migration Strategy: Flat to Subgraphs

### Step 1: Identify Candidates
- Look for clusters of related nodes
- Find repeated patterns
- Identify clear boundaries

### Step 2: Extract One at a Time
- Start with most obvious candidate
- Don't extract everything at once
- Validate benefits before continuing

### Step 3: Define Interface
- Determine input state
- Determine output state
- Document contract

### Step 4: Implement Subgraph
- Move nodes to subgraph
- Adapt state flow
- Test independently

### Step 5: Integrate and Test
- Replace original nodes with subgraph node
- Test parent graph
- Verify no regression

### Step 6: Iterate
- Extract next candidate if beneficial
- Stop when diminishing returns

---

## Best Practices Summary

1. **Clear Boundaries:** Subgraphs should have well-defined responsibilities
2. **Explicit Contracts:** Document input/output state clearly
3. **Favor Reusability:** If used > once, strong subgraph candidate
4. **Limit Nesting:** Avoid > 2-3 levels
5. **Independent Testing:** Subgraphs should be testable in isolation
6. **Don't Over-Extract:** Not every 3 nodes needs a subgraph
7. **Evolve Gradually:** Start flat, extract as patterns emerge
8. **Name Descriptively:** Make purpose obvious
9. **Document Interface:** Help future users (including yourself)
10. **Consider Team Structure:** Subgraphs can align with team ownership

---

**Remember:** Subgraphs are powerful for modularity and reusability, but add complexity. Use them when benefits clearly outweigh costs. Start simple, extract when clear value exists.
