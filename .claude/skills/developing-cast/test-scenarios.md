# Pressure Test Scenarios for developing-cast Skill

## Purpose
Test whether the developing-cast skill enables agents to:
1. Find the right implementation pattern quickly
2. Apply patterns correctly with OOP and Act conventions
3. Make correct decisions when multiple options exist

## Scenario 1: State Schema with Reducers

**Context:** Building a conversation cast that tracks message history with append-only semantics.

**Prompt to agent:**
"I need to implement state for a conversation cast. The state should track messages that can only be appended, never modified. I also need to track current_user which can be updated. How should I structure my state.py?"

**What we're testing:**
- Can agent find reducer pattern guidance?
- Do they understand when to use Annotated[list, operator.add] vs plain list?
- Do they see examples showing both reducer and non-reducer fields?

**Success criteria:**
- Agent recommends reducers for messages
- Agent shows correct Annotated syntax
- Agent demonstrates TypedDict pattern
- Agent shows imports from typing_extensions and operator

---

## Scenario 2: Tool Creation with Act Conventions

**Context:** Need to create a web search tool that uses ToolRuntime for context access.

**Prompt to agent:**
"I need to create a web search tool for my cast. The tool needs access to the user's API key from runtime context. Where should I put this tool and how do I implement it?"

**What we're testing:**
- Can agent find the "tools ONLY in modules/tools" rule?
- Do they show ToolRuntime access pattern?
- Do they demonstrate @tool decorator usage?
- Do they show proper error handling?

**Success criteria:**
- Agent specifies modules/tools/ location explicitly
- Agent shows ToolRuntime parameter usage
- Agent demonstrates @tool decorator
- Agent includes error handling pattern

---

## Scenario 3: Node Implementation with BaseNode

**Context:** Implementing a processing node that needs setup/teardown logic.

**Prompt to agent:**
"I need to create a node that processes documents. The node needs to initialize a heavy resource on startup and clean it up properly. How should I structure this node?"

**What we're testing:**
- Can agent find BaseNode inheritance pattern?
- Do they show __init__ and execute methods?
- Do they demonstrate proper OOP structure?
- Do they show resource management patterns?

**Success criteria:**
- Agent shows inheritance from casts.base_node.BaseNode
- Agent demonstrates __init__ for setup
- Agent shows execute(self, state) signature
- Agent includes cleanup/resource management

---

## Scenario 4: Memory Placement Decision

**Context:** Cast needs to remember user preferences across sessions.

**Prompt to agent:**
"My cast needs to remember user preferences like theme, language, and notification settings across sessions. Users should be able to update these at any time. How should I implement this memory?"

**What we're testing:**
- Can agent find memory decision framework?
- Do they understand short-term vs long-term distinction?
- Do they recommend correct approach (Store for cross-session)?
- Do they show implementation pattern?

**Success criteria:**
- Agent identifies this as long-term memory use case
- Agent recommends Store (not in-state)
- Agent shows Store implementation pattern
- Agent explains why not other options

---

## Scenario 5: Conditional Routing

**Context:** Cast needs different execution paths based on user intent.

**Prompt to agent:**
"My cast analyzes user input and should route to different nodes: 'search' for search queries, 'chat' for conversations, 'help' for help requests. How do I implement this routing logic?"

**What we're testing:**
- Can agent find conditional edge patterns?
- Do they show conditions.py usage?
- Do they demonstrate routing function signature?
- Do they show StateGraph integration?

**Success criteria:**
- Agent shows conditions.py for routing logic
- Agent demonstrates routing function: (state) -> str
- Agent shows add_conditional_edges usage
- Agent shows proper type annotations

---

## Scenario 6: Multiple Pressures Combined

**Context:** Complex cast with state, tools, memory, and routing - time pressure.

**Prompt to agent:**
"I need to build a research assistant cast ASAP. It should:
- Track conversation history (append-only)
- Use web search and document retrieval tools
- Remember user research topics across sessions
- Route between search, synthesis, and chat modes

Give me the implementation structure following Act conventions."

**What we're testing:**
- Can agent navigate multiple resource areas quickly?
- Do they apply all conventions correctly under pressure?
- Do they use SKILL.md index to find right resources?
- Do they combine patterns correctly?

**Success criteria:**
- Agent finds state, tools, memory, and routing patterns
- Agent follows all Act conventions (tools in modules/tools, BaseNode, etc.)
- Agent provides coherent integrated structure
- Agent uses correct LangGraph 1.0 APIs throughout

---

## Gap Testing Scenarios

### Gap Test 1: Async Patterns
"My node needs to make async API calls. How do I handle this in LangGraph?"

**Tests:** Coverage of async node implementation

### Gap Test 2: Error Handling
"What's the best way to handle errors in nodes and tools?"

**Tests:** Coverage of error handling patterns

### Gap Test 3: Subgraphs
"I want to compose multiple casts together. How do I use subgraphs?"

**Tests:** Coverage of subgraph patterns

### Gap Test 4: Interrupts
"I need human approval before executing certain actions. How do I implement this?"

**Tests:** Coverage of interrupt/human-in-the-loop patterns

### Gap Test 5: MCP Adapter
"How do I integrate MCP tools into my cast?"

**Tests:** Coverage of MCP Adapter (NOT Server) usage

---

## Running Tests

### Baseline (RED Phase)
1. Run each scenario with NEW subagent WITHOUT developing-cast skill
2. Document exact behavior:
   - What did they search for?
   - Did they find the right pattern?
   - Were there errors or confusions?
   - What was missing?
3. Record verbatim any incorrect recommendations
4. Note time taken to find information

### With Skill (GREEN Phase)
1. Run same scenarios WITH developing-cast skill loaded
2. Document behavior:
   - Did they use SKILL.md index correctly?
   - Did they navigate to right resources?
   - Were patterns applied correctly?
   - Were Act conventions followed?
3. Note improvements and remaining issues

### Refactor Testing
1. Identify gaps from GREEN phase
2. Update resources to close gaps
3. Re-test affected scenarios
4. Verify no regressions in other scenarios

---

## Success Metrics

**Quantitative:**
- Time to find correct pattern: < 30 seconds
- Correct pattern application rate: > 90%
- Act convention compliance: 100%
- LangGraph 1.0 API accuracy: 100%

**Qualitative:**
- Agent navigates skill structure intuitively
- Agent applies patterns without confusion
- Agent makes correct decisions when multiple options exist
- Agent follows Act conventions without reminders
