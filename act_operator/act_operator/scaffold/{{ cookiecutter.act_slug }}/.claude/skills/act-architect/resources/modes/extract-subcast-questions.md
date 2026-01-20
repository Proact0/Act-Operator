# Extract Sub-Cast Questions

Use when analyzing existing cast for complexity and suggesting extraction.

---

## Step 1: Analyze Current Cast

**Read the cast-specific CLAUDE.md** (`/casts/{cast_snake_name}/CLAUDE.md`) and analyze:
- Count nodes (excluding START/END)
- Identify repeated patterns
- Check for isolated sections
- Look for reusable logic across multiple casts (check root `/CLAUDE.md` Casts table and other cast files)

**Complexity indicators:**
- Node count > 7
- Repeated node sequences
- Shared logic across multiple casts
- Isolated section with clear input/output

---

## When to Suggest Extraction

**Only suggest if:**
- Node count > 7
- Repeated node sequences found
- Shared logic across multiple casts
- Isolated section with clear input/output

**Do NOT suggest if:**
- Cast is simple (≤7 nodes)
- No clear extraction boundary
- Logic is tightly coupled

---

## Questions

### Q1: Complexity Check

**Present analysis first:**
```
"I'm analyzing Cast: {cast_name}.

**Current complexity:**
- Node count: {X} nodes
- [Additional findings: e.g., repeated patterns, isolated sections]

Should we consider extracting any sections to reduce complexity?"
```

**Wait for user interest before proceeding.**

---

### Q2: Extraction Proposal

**If user is interested, propose specific extraction:**
```
"I notice [specific pattern/section]:

**Nodes to extract:**
- {NodeA}
- {NodeB}
- {NodeC}

**Suggested Sub-Cast name:** {ProposedName}

**Benefits:**
- Reduces main cast from {X} to {Y} nodes
- Reusable in [other casts if applicable]
- Clearer separation of concerns

Should we proceed with this extraction?"
```

**Wait for confirmation.**

---

### Q3: Sub-Cast Purpose

**If confirmed, clarify purpose:**
"What is the primary purpose of this sub-cast? (one sentence)"

**Purpose:** Ensure extracted sub-cast has clear responsibility.

---

### Q4: Input/Output Verification

"For the extracted sub-cast:
- **Input:** [inferred from nodes]
- **Output:** [inferred from nodes]

Is this correct?"

**Purpose:** Confirm data boundaries are clear.

---

## After Confirmation: Update Plan

**Explain next steps:**
```
"I'll create:

1. **New Sub-Cast: {name}**
   - Extract {X} nodes from {parent_cast}
   - Add to Casts table in root `/CLAUDE.md`
   - Create `/casts/{subcast_snake_name}/CLAUDE.md` with extracted specification

2. **Update {parent_cast}**
   - Replace extracted nodes with sub-cast invocation node in `/casts/{parent_cast_snake_name}/CLAUDE.md`
   - Update diagram

This will reduce {parent_cast} complexity and make the logic reusable.

Proceed?"
```

**Wait for final confirmation before designing sub-cast.**
