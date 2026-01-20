# Mode 1: Initial Act & Cast Design Questions

Use when CLAUDE.md doesn't exist (initial project setup after `act new`).

---

## Act-Level Questions

**Ask sequentially - wait for response after each question.**

### Q1: Act Purpose
"What does this project do? (one sentence describing the overall goal)"

**Purpose:** Establish project-level context for CLAUDE.md.

**Examples:**
- "Customer support automation system"
- "Document processing pipeline"
- "Multi-agent research assistant"

---

### Q2: Initial Cast Identification
"I see you created a cast called '{{ cookiecutter.cast_snake }}'. What should this cast accomplish?"

**Purpose:** Understand the first cast's role within the Act.

**Examples:**
- "Handle customer inquiries with RAG"
- "Process and index documents"
- "Coordinate research agents"

---

## Cast-Level Questions

**Now design the identified cast:**

### Q3: Cast Goal
"What should this cast accomplish? (one sentence)"

**Purpose:** Establish cast-level objective clearly.

**Examples:**
- "Retrieve context and generate responses to user questions"
- "Parse documents and create embeddings for vector storage"
- "Route queries to specialized agents based on intent"

---

### Q4: Input/Output
"What goes in and what comes out?
- **Input:** (e.g., user query, document)
- **Output:** (e.g., generated text, classification)"

**Purpose:** Define data boundaries.

**Examples:**
- Input: User question (str) | Output: Contextual response (str)
- Input: Raw document (str) | Output: Vector embeddings (list)
- Input: User query (str) | Output: Agent routing decision (str)

---

### Q5: Constraints
"Any constraints?
- A) Low latency (<10s)
- B) Normal (<60s)
- C) Long-running (>60s)
- D) Other?"

**Purpose:** Identify performance requirements.

**Follow-up if D:**
- "What specific constraints?" (e.g., token limits, cost, accuracy requirements)

---

## After Q5: Summarize

**Template:**
```
"Got it. Here's what I understand:

**Act:**
- **Purpose:** [project goal]

**Cast: {{ cookiecutter.cast_snake }}**
- **Goal:** [cast goal]
- **Input:** [input]
- **Output:** [output]
- **Constraints:** [constraints]

Is this correct?"
```

**Wait for confirmation before proceeding to pattern selection.**
