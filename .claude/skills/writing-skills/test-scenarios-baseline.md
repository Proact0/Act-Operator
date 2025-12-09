# Baseline Test Scenarios for Skills Description Migration

## Test Purpose
Verify that current descriptions effectively trigger skill discovery for appropriate scenarios.

## Test Scenarios

### Scenario 1: architecting-act - Initial Project Setup

**User Query:**
"I just ran `act new my-project` and now I need to design the architecture. I don't have any CLAUDE.md file yet. How should I start?"

**Expected Skill Selection:** architecting-act

**Current Description Test:**
```yaml
description: Use when planning {{ cookiecutter.act_name }} Act project architecture, designing new casts(graphs), adding casts to existing Act, analyzing cast complexity for sub-cast extraction, or managing Act/Cast blueprints - guides from requirements to architecture
```

**Success Criteria:**
- Agent recognizes "no CLAUDE.md" as trigger for Initial Design mode
- Agent understands this is architecture planning (not implementation)
- Agent knows to use interactive questioning approach

---

### Scenario 2: architecting-act - Complex Cast Extraction

**User Query:**
"My cast has 12 nodes and it's getting hard to manage. Should I split it into smaller casts?"

**Expected Skill Selection:** architecting-act

**Current Description Test:**
- Does "12 nodes" trigger the skill? (>7 nodes complexity threshold)
- Does agent recognize this as sub-cast extraction scenario?

**Success Criteria:**
- Agent recognizes complexity threshold (>7 nodes)
- Agent identifies this as Mode 3: Extract Sub-Cast scenario
- Agent knows to analyze complexity first

---

### Scenario 3: developing-cast - Implementation Workflow

**User Query:**
"I have the architecture in CLAUDE.md. Now I need to implement the state, nodes, and graph. What order should I do this in?"

**Expected Skill Selection:** developing-cast

**Current Description Test:**
```yaml
description: Use when implementing LangGraph nodes/edges/state from CLAUDE.md, stuck on specific patterns (conditional routing, parallel execution, state updates), or need code examples for 50+ situations - provides systematic reference from architecture to working implementation
```

**Success Criteria:**
- Agent recognizes implementation task (not design)
- Agent knows there's a specific workflow: state → deps → nodes → conditions → graph
- Agent understands CLAUDE.md is the input

---

### Scenario 4: developing-cast - Advanced Features

**User Query:**
"I need to add conversation memory to my agent and also implement retry logic for failed LLM calls. Where do I start?"

**Expected Skill Selection:** developing-cast

**Current Description Test:**
- Does "conversation memory" trigger the skill?
- Does "retry logic" trigger the skill?
- Are these recognized as middleware/memory features?

**Success Criteria:**
- Agent recognizes memory and middleware as developing-cast topics
- Agent knows to reference Component Reference tables
- Agent finds short-term memory and model-retry middleware resources

---

### Scenario 5: engineering-act - Dependency Management

**User Query:**
"I need to add langchain-openai to my project. Also, the dependencies seem out of sync after I pulled from git."

**Expected Skill Selection:** engineering-act

**Current Description Test:**
```yaml
description: Use when creating new cast package in {{ cookiecutter.act_name }} Act monorepo, adding dependencies to workspace or specific cast, facing uv sync issues, or launching langgraph dev server - handles all project setup and package management infrastructure
```

**Success Criteria:**
- Agent recognizes "add dependency" task
- Agent recognizes "out of sync" as sync issue
- Agent knows to check CLAUDE.md first
- Agent knows this is uv-based project

---

### Scenario 6: engineering-act - New Cast Creation

**User Query:**
"I want to create a new cast called 'data-processor' in my Act project. What's the command?"

**Expected Skill Selection:** engineering-act

**Current Description Test:**
- Does "create new cast" trigger the skill?
- Does agent know this is package scaffolding task?

**Success Criteria:**
- Agent identifies this as engineering-act (not architecting-act)
- Agent knows to check CLAUDE.md first if it exists
- Agent knows the command: `uv run act cast -c "Data Processor"`

---

## Pressure Scenarios (Combined)

### Pressure 1: Time + Authority + Ambiguity

**User Query:**
"Quick! My manager wants to see the architecture diagram in 10 minutes. I have a vague idea of what the system should do but CLAUDE.md doesn't exist yet. Should I just start coding the nodes?"

**Expected Behaviors:**
1. **architecting-act** should be triggered (no CLAUDE.md = Initial Design)
2. Agent should NOT skip architecture and jump to coding
3. Agent should recognize Interactive questioning is needed
4. Agent should know architecture comes before implementation

**Failure Modes to Document:**
- Agent selects developing-cast instead (starts coding)
- Agent skips interactive questioning (writes architecture without asking)
- Agent doesn't recognize "no CLAUDE.md" as trigger

---

### Pressure 2: Sunk Cost + Exhaustion

**User Query:**
"I've been implementing nodes for 3 hours but I keep getting stuck on the state schema. I looked at CLAUDE.md but I'm not sure how to translate the State Schema table into TypedDict. Maybe I should just guess and fix it later?"

**Expected Behaviors:**
1. **developing-cast** should be triggered (implementation task)
2. Agent should reference core/state.md resource
3. Agent should know state.py comes FIRST in workflow
4. Agent should NOT encourage "guess and fix later"

**Failure Modes to Document:**
- Agent doesn't reference Component Reference table
- Agent doesn't emphasize workflow order (state first)
- Agent encourages skipping proper implementation

---

## Test Execution Plan

1. **Create minimal test environment** with skill files
2. **Spawn subagent** with ONLY base knowledge (no skills loaded)
3. **Present scenario** and observe skill selection + behavior
4. **Document verbatim** any rationalizations or failures
5. **Repeat** with skills loaded and compare behavior

## What to Capture

For each scenario, document:
- ✅/❌ Did agent select correct skill?
- ✅/❌ Did agent recognize mode/context correctly?
- ✅/❌ Did agent know which resources to use?
- 📝 Verbatim rationalizations if agent went wrong
- 📝 What triggers were missed?
- 📝 What additional symptoms should be added to description?
