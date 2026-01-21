# Mode 2: Add New Cast Questions

Use when CLAUDE.md files exist (distributed structure) and adding a new cast to the Act.

---

## 🎮 Interactive Conversation Protocol

**CRITICAL: Follow these rules for every question:**

1. **One Question at a Time** - Never ask multiple questions in a single message
2. **Wait for Response** - Always pause after asking, do not proceed until user responds
3. **Show Progress** - Display the progress indicator before each question
4. **Use Formatted Templates** - Follow the exact question format below

---

## Step 1: Read Existing Context

**First, read CLAUDE.md files** to understand:
- **Root `/CLAUDE.md`**: Act Overview, purpose, and Casts table
- **Existing cast CLAUDE.md files** (`/casts/{cast_snake_name}/CLAUDE.md`): Each cast's architecture and responsibilities

**Show context analysis:**

```
╭─────────────────────────────────────────────╮
│  🔍 Analyzing Existing Context              │
╰─────────────────────────────────────────────╯

Reading /CLAUDE.md...
   ✓ Act: [Act Name]
   ✓ Purpose: [Purpose]
   ✓ Existing Casts: [N] found

Existing casts:
┌──────────────────┬────────────────────────────┐
│ Cast Name        │ Purpose                    │
├──────────────────┼────────────────────────────┤
│ [cast_1]         │ [brief purpose]            │
│ [cast_2]         │ [brief purpose]            │
└──────────────────┴────────────────────────────┘

Context loaded. Starting questions...
```

---

## Progress Indicator

Display at the start of each question:

```
╭─────────────────────────────────────────────╮
│  🏗️ Act Architect - Mode 2: Add Cast        │
├─────────────────────────────────────────────┤
│  Phase: [1/5] New Cast Purpose              │
│  Progress: ████░░░░░░░░░░░░░░░░ 20%         │
╰─────────────────────────────────────────────╯
```

Update the phase number and progress bar as you proceed.

---

## Questions

**Ask sequentially - wait for response after each question.**

### Q1: New Cast Purpose

**Display:**

```
╭─────────────────────────────────────────────╮
│  🏗️ Act Architect - Mode 2: Add Cast        │
├─────────────────────────────────────────────┤
│  Phase: [1/5] New Cast Purpose              │
│  Progress: ████░░░░░░░░░░░░░░░░ 20%         │
╰─────────────────────────────────────────────╯

📋 **Question 1 of 5: New Cast Purpose**

I see your Act already has these casts:
• [cast_1]: [brief purpose]
• [cast_2]: [brief purpose]

What should the **new cast** accomplish?

💡 **Examples:**
- "We need a separate cast to handle data ingestion"
- "Add a cast for batch processing user requests"
- "Create a validation cast used by other casts"

Your answer: _
```

**Purpose:** Understand the new cast's role and why it's needed.

**🛑 STOP and wait for user response before proceeding.**

---

### Q2: Cast Goal

**Display:**

```
╭─────────────────────────────────────────────╮
│  🏗️ Act Architect - Mode 2: Add Cast        │
├─────────────────────────────────────────────┤
│  Phase: [2/5] Cast Goal                     │
│  Progress: ████████░░░░░░░░░░░░ 40%         │
╰─────────────────────────────────────────────╯

📋 **Question 2 of 5: Cast Goal**

What should this new cast do? (one sentence)

💡 **Examples:**
- "Ingest documents from external sources and queue for processing"
- "Process batches of user requests in parallel"
- "Validate and sanitize input data before processing"

Your answer: _
```

**Purpose:** Establish clear, focused objective.

**🛑 STOP and wait for user response before proceeding.**

---

### Q3: Relationship to Existing Casts

**Display:**

```
╭─────────────────────────────────────────────╮
│  🏗️ Act Architect - Mode 2: Add Cast        │
├─────────────────────────────────────────────┤
│  Phase: [3/5] Relationship                  │
│  Progress: ████████████░░░░░░░░ 60%         │
╰─────────────────────────────────────────────╯

📋 **Question 3 of 5: Relationship to Existing Casts**

How does this new cast relate to existing ones?

   A) 🔗 Independent (runs separately, no direct connection)
   B) ➡️ Sequential (runs after another cast)
   C) 🔄 Provides shared logic (sub-cast used by multiple casts)
   D) 📝 Other (please describe)

Select [A/B/C/D]: _
```

**Purpose:** Understand cast relationships and data flow.

**Follow-up based on answer:**

**If B (Sequential):**

```
📋 **Follow-up: Sequential Relationship**

Which cast runs before this one? And what data is passed?

   Runs after: _
   Data passed: _
```

**If C (Shared logic):**

```
📋 **Follow-up: Shared Logic**

Which casts will use this sub-cast?

Your answer (comma-separated): _
```

**If D (Other):**

```
📋 **Follow-up: Custom Relationship**

Please describe how this cast relates to the existing ones:

Your answer: _
```

**🛑 STOP and wait for user response before proceeding.**

---

### Q4: Input/Output

**Display:**

```
╭─────────────────────────────────────────────╮
│  🏗️ Act Architect - Mode 2: Add Cast        │
├─────────────────────────────────────────────┤
│  Phase: [4/5] Input/Output                  │
│  Progress: ████████████████░░░░ 80%         │
╰─────────────────────────────────────────────╯

📋 **Question 4 of 5: Input/Output**

What goes in and what comes out of this cast?

**Input:** (e.g., file path, request batch)
**Output:** (e.g., processed data, validation result)

💡 **Examples:**
- Input: File path (str) → Output: Parsed data (dict)
- Input: Request batch (list) → Output: Processed results (list)
- Input: Raw input (any) → Output: Validated input (any) or error

Your answer (format: Input: ... → Output: ...): _
```

**Purpose:** Define data boundaries.

**🛑 STOP and wait for user response before proceeding.**

---

### Q5: Constraints

**Display:**

```
╭─────────────────────────────────────────────╮
│  🏗️ Act Architect - Mode 2: Add Cast        │
├─────────────────────────────────────────────┤
│  Phase: [5/5] Constraints                   │
│  Progress: ████████████████████ 100%        │
╰─────────────────────────────────────────────╯

📋 **Question 5 of 5: Constraints**

Any performance constraints for this cast?

   A) ⚡ Low latency (<10s)
   B) 🕐 Normal (<60s)
   C) 🐢 Long-running (>60s)
   D) 📝 Other (please specify)

Select [A/B/C/D]: _
```

**Purpose:** Identify performance requirements.

**Follow-up if D:**

```
📋 **Follow-up: Specific Constraints**

What specific constraints? (e.g., token limits, cost, accuracy requirements)

Your answer: _
```

**🛑 STOP and wait for user response before proceeding.**

---

## After Q5: Summarize and Confirm

**CRITICAL: Always confirm understanding before proceeding to pattern selection.**

**Display:**

```
╭─────────────────────────────────────────────╮
│  ✅ Phase Complete - Please Confirm         │
╰─────────────────────────────────────────────╯

Here's what I understand:

┌─────────────────────────────────────────────┐
│  **New Cast: {cast_name}**                  │
│  Goal: [cast goal]                          │
│  Relationship: [how it relates]             │
│  Input: [input]                             │
│  Output: [output]                           │
│  Constraints: [constraints]                 │
├─────────────────────────────────────────────┤
│  **Integration with existing casts:**       │
│  [list existing casts and relationship]     │
└─────────────────────────────────────────────┘

Is this correct?

   A) ✅ Yes, proceed to design
   B) 🔄 No, I'd like to change something

Select [A/B]: _
```

**If user selects B:**

```
📋 **What would you like to change?**

   A) Cast Purpose
   B) Cast Goal
   C) Relationship to Existing Casts
   D) Input/Output
   E) Constraints

Select [A/B/C/D/E]: _
```

Then re-ask that specific question.

**🛑 Wait for confirmation before proceeding to Cast Design Workflow.**

---

## Transition to Cast Design

**After confirmation, show transition:**

```
╭─────────────────────────────────────────────╮
│  🎨 Transitioning to Cast Design Workflow   │
├─────────────────────────────────────────────┤
│  Next: Pattern Selection                    │
│  Estimated steps: 6                         │
│                                             │
│  After design, will:                        │
│  1. Create cast package (if needed)         │
│  2. Generate /casts/{new_cast}/CLAUDE.md    │
│  3. Update /CLAUDE.md Casts table           │
│  4. Validate architecture                   │
╰─────────────────────────────────────────────╯

Starting pattern selection...
```

**Then proceed to "Cast Design Workflow" in SKILL.md.**
