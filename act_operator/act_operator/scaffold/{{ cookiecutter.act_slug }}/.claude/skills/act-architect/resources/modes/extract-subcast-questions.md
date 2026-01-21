# Mode 3: Extract Sub-Cast Questions

Use when analyzing existing cast for complexity and suggesting extraction.

---

## 🎮 Interactive Conversation Protocol

**CRITICAL: Follow these rules for every question:**

1. **One Question at a Time** - Never ask multiple questions in a single message
2. **Wait for Response** - Always pause after asking, do not proceed until user responds
3. **Show Progress** - Display the progress indicator before each question
4. **Present Analysis First** - Show findings before asking for decisions

---

## Step 1: Analyze Current Cast

**Read the cast-specific CLAUDE.md** (`/casts/{cast_snake_name}/CLAUDE.md`) and analyze:
- Count nodes (excluding START/END)
- Identify repeated patterns
- Check for isolated sections
- Look for reusable logic across multiple casts (check root `/CLAUDE.md` Casts table and other cast files)

**Show analysis progress:**

```
╭─────────────────────────────────────────────╮
│  🔍 Analyzing Cast Complexity               │
╰─────────────────────────────────────────────╯

Reading /casts/{cast_name}/CLAUDE.md...
   ✓ Cast: [Cast Name]
   ✓ Pattern: [Pattern Type]
   ✓ Node Count: [X] nodes

Performing complexity analysis...
   ✓ Counting nodes
   ✓ Identifying patterns
   ✓ Checking for isolated sections
   ✓ Looking for reusable logic

Analysis complete.
```

---

## Complexity Indicators

**Extraction may be beneficial if:**
- Node count > 7
- Repeated node sequences found
- Shared logic across multiple casts
- Isolated section with clear input/output

**Extraction NOT recommended if:**
- Cast is simple (≤7 nodes)
- No clear extraction boundary
- Logic is tightly coupled

---

## Progress Indicator

Display at the start of each question:

```
╭─────────────────────────────────────────────╮
│  🏗️ Act Architect - Mode 3: Extract Sub-Cast │
├─────────────────────────────────────────────┤
│  Phase: [1/4] Complexity Check              │
│  Progress: █████░░░░░░░░░░░░░░░ 25%         │
╰─────────────────────────────────────────────╯
```

Update the phase number and progress bar as you proceed.

---

## Questions

### Q1: Complexity Check

**Present analysis first, then ask:**

```
╭─────────────────────────────────────────────╮
│  🏗️ Act Architect - Mode 3: Extract Sub-Cast │
├─────────────────────────────────────────────┤
│  Phase: [1/4] Complexity Check              │
│  Progress: █████░░░░░░░░░░░░░░░ 25%         │
╰─────────────────────────────────────────────╯

📊 **Complexity Analysis: Cast {cast_name}**

┌─────────────────────────────────────────────┐
│  **Current Complexity:**                    │
│                                             │
│  Node count: [X] nodes                      │
│  Threshold:  7 nodes (recommended max)      │
│  Status:     [✅ OK / ⚠️ Complex]           │
├─────────────────────────────────────────────┤
│  **Findings:**                              │
│                                             │
│  [✓/✗] Repeated patterns: [details]         │
│  [✓/✗] Isolated sections: [details]         │
│  [✓/✗] Shared logic potential: [details]    │
└─────────────────────────────────────────────┘

[If complexity indicators found:]
📋 **Question 1 of 4: Proceed with Extraction?**

Based on this analysis, extraction could reduce complexity.

Would you like to consider extracting sections to reduce complexity?

   A) ✅ Yes, show me what you'd suggest extracting
   B) ❌ No, keep the cast as-is
   C) 🤔 Tell me more about the benefits first

Select [A/B/C]: _

[If no complexity indicators:]
✅ **Cast complexity is acceptable.**

Node count is within recommended limits and no clear extraction candidates found.
No action needed.

Would you like to:
   A) 🔍 Review the analysis details anyway
   B) ✅ Continue with current architecture

Select [A/B]: _
```

**🛑 STOP and wait for user response before proceeding.**

**If user selects C (Tell me more):**

```
📋 **Benefits of Extraction:**

┌─────────────────────────────────────────────┐
│  **Why extract sub-casts?**                 │
│                                             │
│  • 🔧 Maintainability: Smaller casts are    │
│       easier to understand and modify       │
│                                             │
│  • 🔄 Reusability: Extracted logic can be   │
│       shared across multiple casts          │
│                                             │
│  • 🧪 Testability: Isolated components are  │
│       easier to test independently          │
│                                             │
│  • 📐 Clarity: Clear separation of concerns │
│       makes architecture more understandable│
└─────────────────────────────────────────────┘

Would you like to proceed with extraction analysis?

   A) ✅ Yes, show me what you'd suggest
   B) ❌ No, keep as-is

Select [A/B]: _
```

**If user selects B at any point, end the workflow:**

```
╭─────────────────────────────────────────────╮
│  ✅ Keeping Current Architecture            │
╰─────────────────────────────────────────────╯

No changes will be made. The cast will remain as-is.

If you change your mind later, you can run this analysis again.
```

---

### Q2: Extraction Proposal

**If user is interested, propose specific extraction:**

```
╭─────────────────────────────────────────────╮
│  🏗️ Act Architect - Mode 3: Extract Sub-Cast │
├─────────────────────────────────────────────┤
│  Phase: [2/4] Extraction Proposal           │
│  Progress: ██████████░░░░░░░░░░ 50%         │
╰─────────────────────────────────────────────╯

📋 **Extraction Proposal**

I've identified the following extraction candidate:

┌─────────────────────────────────────────────┐
│  **Suggested Sub-Cast: {ProposedName}**     │
├─────────────────────────────────────────────┤
│  **Nodes to extract:**                      │
│  • {NodeA}                                  │
│  • {NodeB}                                  │
│  • {NodeC}                                  │
├─────────────────────────────────────────────┤
│  **Impact:**                                │
│  • Main cast: [X] → [Y] nodes              │
│  • New sub-cast: [Z] nodes                  │
│  • Complexity reduction: [X-Y] nodes        │
├─────────────────────────────────────────────┤
│  **Benefits:**                              │
│  • [Benefit 1: e.g., "Reusable validation"] │
│  • [Benefit 2: e.g., "Clearer main flow"]   │
│  • [Benefit 3: e.g., "Easier testing"]      │
└─────────────────────────────────────────────┘

Should we proceed with this extraction?

   A) ✅ Yes, proceed with this proposal
   B) 🔄 Modify the proposal (different nodes)
   C) ❌ Cancel extraction

Select [A/B/C]: _
```

**🛑 STOP and wait for user response before proceeding.**

**If user selects B (Modify):**

```
📋 **Modify Extraction Proposal**

Current proposed nodes for extraction:
• {NodeA}
• {NodeB}
• {NodeC}

What would you like to change?

   A) ➕ Add more nodes to extraction
   B) ➖ Remove nodes from extraction
   C) 🔄 Start with different nodes entirely

Select [A/B/C]: _
```

Then gather specific modifications based on selection.

---

### Q3: Sub-Cast Purpose

**If confirmed, clarify purpose:**

```
╭─────────────────────────────────────────────╮
│  🏗️ Act Architect - Mode 3: Extract Sub-Cast │
├─────────────────────────────────────────────┤
│  Phase: [3/4] Sub-Cast Purpose              │
│  Progress: ███████████████░░░░░ 75%         │
╰─────────────────────────────────────────────╯

📋 **Question 3 of 4: Sub-Cast Purpose**

What is the primary purpose of this sub-cast? (one sentence)

Based on the nodes, I suggest: "[inferred purpose]"

💡 **Examples:**
- "Validate and sanitize user input before processing"
- "Handle document parsing and text extraction"
- "Manage API calls with retry logic and rate limiting"

Your answer (or press Enter to accept suggestion): _
```

**Purpose:** Ensure extracted sub-cast has clear responsibility.

**🛑 STOP and wait for user response before proceeding.**

---

### Q4: Input/Output Verification

**Verify data boundaries:**

```
╭─────────────────────────────────────────────╮
│  🏗️ Act Architect - Mode 3: Extract Sub-Cast │
├─────────────────────────────────────────────┤
│  Phase: [4/4] Input/Output Verification     │
│  Progress: ████████████████████ 100%        │
╰─────────────────────────────────────────────╯

📋 **Question 4 of 4: Verify Input/Output**

Based on the extracted nodes, I've inferred:

┌─────────────────────────────────────────────┐
│  **Sub-Cast: {SubCastName}**                │
├─────────────────────────────────────────────┤
│  Input:  [inferred from first node]         │
│  Output: [inferred from last node]          │
└─────────────────────────────────────────────┘

Is this correct?

   A) ✅ Yes, this is correct
   B) 🔄 No, I need to modify

Select [A/B]: _
```

**If user selects B:**

```
📋 **Modify Input/Output**

Please specify the correct boundaries:

**Input:** _
**Output:** _
```

**🛑 STOP and wait for user response before proceeding.**

---

## After Confirmation: Show Update Plan

**Explain next steps clearly:**

```
╭─────────────────────────────────────────────╮
│  ✅ Extraction Confirmed - Update Plan      │
╰─────────────────────────────────────────────╯

Here's what I'll create:

┌─────────────────────────────────────────────┐
│  **1. New Sub-Cast: {name}**                │
│     • Extract [X] nodes from {parent_cast}  │
│     • Create /casts/{subcast_slug}/         │
│     • Generate CLAUDE.md with spec          │
├─────────────────────────────────────────────┤
│  **2. Update {parent_cast}**                │
│     • Replace extracted nodes with          │
│       sub-cast invocation node              │
│     • Update Mermaid diagram                │
│     • Update node specifications            │
├─────────────────────────────────────────────┤
│  **3. Update Root CLAUDE.md**               │
│     • Add sub-cast to Casts table           │
│     • Update relationships                  │
├─────────────────────────────────────────────┤
│  **Result:**                                │
│     • {parent_cast}: [X] → [Y] nodes       │
│     • {subcast}: [Z] nodes (new)            │
│     • Total complexity: Reduced             │
└─────────────────────────────────────────────┘

Ready to proceed?

   A) ✅ Yes, create the sub-cast
   B) 🔄 I want to change something first
   C) ❌ Cancel, don't make any changes

Select [A/B/C]: _
```

**🛑 Wait for final confirmation before proceeding to sub-cast design.**

---

## Transition to Sub-Cast Design

**After confirmation, show transition:**

```
╭─────────────────────────────────────────────╮
│  🎨 Creating Sub-Cast: {SubCastName}        │
├─────────────────────────────────────────────┤
│  Next: Pattern Selection (for sub-cast)     │
│  Estimated steps: 6                         │
│                                             │
│  After design, will:                        │
│  1. Create sub-cast package                 │
│  2. Generate sub-cast CLAUDE.md             │
│  3. Update parent cast CLAUDE.md            │
│  4. Update root CLAUDE.md                   │
│  5. Validate architecture                   │
╰─────────────────────────────────────────────╯

Starting sub-cast design...
```

**Then proceed to "Cast Design Workflow" in SKILL.md for the sub-cast.**
