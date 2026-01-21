# Mode 1: Initial Act & Cast Design Questions

Use when CLAUDE.md doesn't exist (initial project setup after `act new`).

---

## 🎮 Interactive Conversation Protocol

**CRITICAL: Follow these rules for every question:**

1. **One Question at a Time** - Never ask multiple questions in a single message
2. **Wait for Response** - Always pause after asking, do not proceed until user responds
3. **Show Progress** - Display the progress indicator before each question
4. **Use Formatted Templates** - Follow the exact question format below

---

## Progress Indicator

Display at the start of each question:

```
╭─────────────────────────────────────────────╮
│  🏗️ Act Architect - Mode 1: Initial Design  │
├─────────────────────────────────────────────┤
│  Phase: [1/5] Act Overview                  │
│  Progress: ████░░░░░░░░░░░░░░░░ 20%         │
╰─────────────────────────────────────────────╯
```

Update the phase number and progress bar as you proceed.

---

## Act-Level Questions

**Ask sequentially - wait for response after each question.**

### Q1: Act Purpose

**Display:**

```
╭─────────────────────────────────────────────╮
│  🏗️ Act Architect - Mode 1: Initial Design  │
├─────────────────────────────────────────────┤
│  Phase: [1/5] Act Purpose                   │
│  Progress: ████░░░░░░░░░░░░░░░░ 20%         │
╰─────────────────────────────────────────────╯

📋 **Question 1 of 5: Act Purpose**

What does this project do? (one sentence describing the overall goal)

💡 **Examples:**
- "Customer support automation system"
- "Document processing pipeline"
- "Multi-agent research assistant"

Your answer: _
```

**Purpose:** Establish project-level context for CLAUDE.md.

**🛑 STOP and wait for user response before proceeding.**

---

### Q2: Initial Cast Identification

**Display:**

```
╭─────────────────────────────────────────────╮
│  🏗️ Act Architect - Mode 1: Initial Design  │
├─────────────────────────────────────────────┤
│  Phase: [2/5] Cast Identification           │
│  Progress: ████████░░░░░░░░░░░░ 40%         │
╰─────────────────────────────────────────────╯

📋 **Question 2 of 5: Initial Cast**

I see you created a cast called '{{ cookiecutter.cast_snake }}'.

What should this cast accomplish within your Act?

💡 **Examples:**
- "Handle customer inquiries with RAG"
- "Process and index documents"
- "Coordinate research agents"

Your answer: _
```

**Purpose:** Understand the first cast's role within the Act.

**🛑 STOP and wait for user response before proceeding.**

---

## Cast-Level Questions

**Now design the identified cast:**

### Q3: Cast Goal

**Display:**

```
╭─────────────────────────────────────────────╮
│  🏗️ Act Architect - Mode 1: Initial Design  │
├─────────────────────────────────────────────┤
│  Phase: [3/5] Cast Goal                     │
│  Progress: ████████████░░░░░░░░ 60%         │
╰─────────────────────────────────────────────╯

📋 **Question 3 of 5: Cast Goal**

What should this cast accomplish? (one sentence)

💡 **Examples:**
- "Retrieve context and generate responses to user questions"
- "Parse documents and create embeddings for vector storage"
- "Route queries to specialized agents based on intent"

Your answer: _
```

**Purpose:** Establish cast-level objective clearly.

**🛑 STOP and wait for user response before proceeding.**

---

### Q4: Input/Output

**Display:**

```
╭─────────────────────────────────────────────╮
│  🏗️ Act Architect - Mode 1: Initial Design  │
├─────────────────────────────────────────────┤
│  Phase: [4/5] Input/Output                  │
│  Progress: ████████████████░░░░ 80%         │
╰─────────────────────────────────────────────╯

📋 **Question 4 of 5: Input/Output**

What goes in and what comes out?

**Input:** (e.g., user query, document)
**Output:** (e.g., generated text, classification)

💡 **Examples:**
- Input: User question (str) → Output: Contextual response (str)
- Input: Raw document (str) → Output: Vector embeddings (list)
- Input: User query (str) → Output: Agent routing decision (str)

Your answer (format: Input: ... → Output: ...): _
```

**Purpose:** Define data boundaries.

**🛑 STOP and wait for user response before proceeding.**

---

### Q5: Constraints

**Display:**

```
╭─────────────────────────────────────────────╮
│  🏗️ Act Architect - Mode 1: Initial Design  │
├─────────────────────────────────────────────┤
│  Phase: [5/5] Constraints                   │
│  Progress: ████████████████████ 100%        │
╰─────────────────────────────────────────────╯

📋 **Question 5 of 5: Constraints**

Any performance constraints?

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
│  **Act: {{ cookiecutter.act_name }}**       │
│  Purpose: [captured purpose]                │
├─────────────────────────────────────────────┤
│  **Cast: {{ cookiecutter.cast_snake }}**    │
│  Goal: [cast goal]                          │
│  Input: [input]                             │
│  Output: [output]                           │
│  Constraints: [constraints]                 │
└─────────────────────────────────────────────┘

Is this correct?

   A) ✅ Yes, proceed to design
   B) 🔄 No, I'd like to change something

Select [A/B]: _
```

**If user selects B:**

```
📋 **What would you like to change?**

   A) Act Purpose
   B) Cast Identification
   C) Cast Goal
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
╰─────────────────────────────────────────────╯

Starting pattern selection...
```

**Then proceed to "Cast Design Workflow" in SKILL.md.**
