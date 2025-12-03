# Question Templates

Interactive questioning workflow for Step 1 (Requirements Gathering).

## Step 1 Questions

**Ask sequentially - wait for response after each question.**

### Q1: Goal
"What should this graph accomplish? (one sentence)"

**Purpose:** Establish core objective clearly.

**Examples:**
- "Summarize long documents into key points"
- "Route customer queries to appropriate handlers"
- "Generate and refine blog posts until quality threshold met"

---

### Q2: Input/Output
"What goes in and what comes out?
- **Input:** (e.g., user query, document)
- **Output:** (e.g., generated text, classification)"

**Purpose:** Define data boundaries.

**Examples:**
- Input: Raw text document | Output: 200-word summary
- Input: User message | Output: Response + conversation history
- Input: Code snippet | Output: Test cases + coverage report

---

### Q3: Constraints
"Any constraints?
- A) Low latency (<10s)
- B) Normal (<60s)
- C) Long-running (>60s)
- D) Other?"

**Purpose:** Identify performance/scalability requirements.

**Follow-up if D:**
- "What specific constraints?" (e.g., token limits, cost, accuracy)

---

## After Q3: Summarize

**Template:**
"Got it. Here's what I understand:
- **Goal:** [summary]
- **Input:** [input]
- **Output:** [output]
- **Constraints:** [constraints]

Is this correct?"

**Wait for confirmation before proceeding to Step 2.**
