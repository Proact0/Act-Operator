# Mode 2: Add New Cast Questions

Use when CLAUDE.md files exist (distributed structure) and adding a new cast to the Act.

---

## Step 1: Read Existing Context

**First, read CLAUDE.md files** to understand:
- **Root `/CLAUDE.md`**: Act Overview, purpose, and Casts table
- **Existing cast CLAUDE.md files** (`/casts/{cast_snake_name}/CLAUDE.md`): Each cast's architecture and responsibilities

---

## Questions

**Ask sequentially - wait for response after each question.**

### Q1: New Cast Purpose
"I see your Act already has these casts: [list existing casts]. What should the new cast accomplish?"

**Purpose:** Understand the new cast's role and why it's needed.

**Examples:**
- "We need a separate cast to handle data ingestion"
- "Add a cast for batch processing user requests"
- "Create a validation cast used by other casts"

---

### Q2: Cast Goal
"What should this new cast do? (one sentence)"

**Purpose:** Establish clear, focused objective.

**Examples:**
- "Ingest documents from external sources and queue for processing"
- "Process batches of user requests in parallel"
- "Validate and sanitize input data before processing"

---

### Q3: Relationship to Existing Casts
"How does this cast relate to existing ones?
- A) Independent (runs separately, no direct connection)
- B) Sequential (runs after another cast)
- C) Provides shared logic (sub-cast used by multiple casts)
- D) Other?"

**Purpose:** Understand cast relationships and data flow.

**Follow-up based on answer:**
- If B: "Which cast runs before it? What data is passed?"
- If C: "Which casts will use this sub-cast?"
- If D: "How does it relate?"

---

### Q4: Input/Output
"What goes in and what comes out?
- **Input:** (e.g., file path, request batch)
- **Output:** (e.g., processed data, validation result)"

**Purpose:** Define data boundaries.

---

### Q5: Constraints
"Any constraints?
- A) Low latency (<10s)
- B) Normal (<60s)
- C) Long-running (>60s)
- D) Other?"

**Purpose:** Identify performance requirements.

---

## After Q5: Summarize

**Template:**
```
"Got it. Here's what I understand:

**New Cast: {cast_name}**
- **Goal:** [cast goal]
- **Relationship:** [how it relates to existing casts]
- **Input:** [input]
- **Output:** [output]
- **Constraints:** [constraints]

This will be added to your Act alongside: [existing casts].

Is this correct?"
```

**Wait for confirmation before proceeding to pattern selection.**
