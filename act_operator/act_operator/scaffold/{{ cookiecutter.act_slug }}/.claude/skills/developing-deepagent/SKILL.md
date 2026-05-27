---
name: developing-deepagent
description: Implements DeepAgent components using LangChain's deepagents SDK. Use when building deep agents with create_deep_agent, configuring backends/subagents/skills/memory/interpreter, need DeepAgent patterns (sandbox, HITL interrupts, long-term memory, subagent spawning, subagent structured output, QuickJS code interpreter with programmatic tool calling), or ask "implement deep agent", "add subagent", "configure backend", "add interpreter".
version: "2026.05.26"
author: Proact0
allowed-tools:
  - Bash(uv sync *)
  - Bash(uv add --dev *)
  - Bash(uv add --group *)
  - Bash(uv add --package *)
  - Bash(uv remove --package *)
  - Read
  - Write
  - Edit
  - AskUserQuestion
---
# Developing {{ cookiecutter.act_name }}'s DeepAgent

Implement DeepAgent components using the `deepagents` SDK within {{ cookiecutter.act_name }} Act patterns.

## When to Use

- Building deep agents with `create_deep_agent`
- Configuring backends, subagents, skills, or long-term memory
- Need DeepAgent harness patterns (sandbox, HITL, memory)
- Integrating subagent delegation into existing casts

## When NOT to Use

- LangGraph graph building (state/node/edge) → `developing-cast`
- Architecture design → `architecting-act`
- Project / cast scaffolding → run `uv run act new` (project) or `uv run act cast` (new cast) directly
- Testing → `testing-cast`

---

## DeepAgent vs Cast

> **Cast** = LangGraph StateGraph (low-level nodes, edges, state)
> **DeepAgent** = Agent harness built on LangChain + LangGraph (high-level: planning, filesystem, subagents, memory)

Use `developing-cast` when you need custom graph topology. Use `developing-deepagent` when you need an agent harness with built-in capabilities.

---

## Implementation Workflow

### Step 1: Understand Requirements

**If CLAUDE.md exists:**
1. Read `/CLAUDE.md` → Act overview, find target agent spec
2. Identify: model, tools, subagents, backend type, memory needs
3. Proceed to Step 2

**If CLAUDE.md not found:**
AskUserQuestion Format:
```json
{
  "question": "CLAUDE.md not found. Create architecture first?",
  "header": "Architecture",
  "multiSelect": false,
  "options": [
    {"label": "Yes", "description": "Switch to architecting-act skill"},
    {"label": "No", "description": "Proceed without architecture specs"}
  ]
}
```

### Step 2: Install deepagents

```bash
uv add --package {{ cookiecutter.act_slug }} deepagents
```

### Step 3: Implementation

**Implement in this order — each layer depends on the previous one:**

```
Step  Module File              Component
────  ───────────────────────  ──────────────────────────────────────
1.    modules/utils.py         Backend instances (StateBackend(), ...)
2.    modules/tools.py         Custom tools (@tool / MCP)
3.    modules/agents.py        Subagent definitions
4.    modules/middlewares.py   Middleware configuration
5.    modules/models.py        Model configuration
6.    modules/prompts.py       System prompt content
7.    modules/agents.py        create_deep_agent assembly
```

### Optional Step 4: Environment Variables

Update `.env.example` (project root):

```bash
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
```

---

## Component Reference

### Core

| Use when | Resource |
|----------|----------|
| creating a deep agent with `create_deep_agent` | [core/create-deep-agent.md](./resources/core/create-deep-agent.md) |
| understanding the harness (filesystem, planning, context) | [core/harness.md](./resources/core/harness.md) |

### Backends (Virtual Filesystem)

| Use when | Resource |
|----------|----------|
| using ephemeral in-state storage (default) | [backend/state-backend.md](./resources/backend/state-backend.md) |
| granting agent local filesystem access | [backend/filesystem-backend.md](./resources/backend/filesystem-backend.md) |
| persisting files across threads (Store) | [backend/store-backend.md](./resources/backend/store-backend.md) |
| mixing ephemeral + persistent paths | [backend/composite-backend.md](./resources/backend/composite-backend.md) |
| implementing custom storage (S3, DB) | [backend/custom-backend.md](./resources/backend/custom-backend.md) |

### Subagents

| Use when | Resource |
|----------|----------|
| understanding subagent architecture and delegation | [subagents/overview.md](./resources/subagents/overview.md) |
| using the built-in general-purpose subagent | [subagents/general-purpose.md](./resources/subagents/general-purpose.md) |
| defining custom specialized subagents | [subagents/custom-subagent.md](./resources/subagents/custom-subagent.md) |
| wrapping a LangGraph graph as subagent | [subagents/compiled-subagent.md](./resources/subagents/compiled-subagent.md) |
| launching non-blocking background subagents (v0.5+) | [subagents/async-subagent.md](./resources/subagents/async-subagent.md) |

### Interrupt (Human-in-the-Loop)

| Use when | Resource |
|----------|----------|
| requiring human approval for tool calls | [interrupt/human-in-the-loop.md](./resources/interrupt/human-in-the-loop.md) |
| resuming execution after interrupt (approve/edit/reject) | [interrupt/resume.md](./resources/interrupt/resume.md) |

### Memory

| Use when | Resource |
|----------|----------|
| persisting data across threads with CompositeBackend | [memory/long-term-memory.md](./resources/memory/long-term-memory.md) |
| sharing state between agent and subagents | [memory/cross-thread-persistence.md](./resources/memory/cross-thread-persistence.md) |

### Skills

| Use when | Resource |
|----------|----------|
| adding skill directories to deep agent | [skills/usage.md](./resources/skills/usage.md) |
| configuring skills for subagents | [skills/subagent-skills.md](./resources/skills/subagent-skills.md) |

### Sandbox (Code Execution — OS-level)

| Use when | Resource |
|----------|----------|
| understanding sandbox architecture | [sandbox/overview.md](./resources/sandbox/overview.md) |
| running code in isolated environment (Modal/Daytona/Runloop) | [sandbox/providers.md](./resources/sandbox/providers.md) |
| using local shell for dev/testing | [sandbox/local-shell.md](./resources/sandbox/local-shell.md) |

### Interpreter (Code Execution — QuickJS, in-agent)

| Use when | Resource |
|----------|----------|
| composing tools/orchestrating subagents from code (CodeInterpreterMiddleware) | [interpreter/code-interpreter.md](./resources/interpreter/code-interpreter.md) |

### Middleware

| Use when | Resource |
|----------|----------|
| LLM calls fail intermittently | [middlewares/provider-agnostic/model-retry.md](./resources/middlewares/provider-agnostic/model-retry.md) |
| tool execution fails intermittently | [middlewares/provider-agnostic/tool-retry.md](./resources/middlewares/provider-agnostic/tool-retry.md) |
| need backup model when primary fails | [middlewares/provider-agnostic/model-fallback.md](./resources/middlewares/provider-agnostic/model-fallback.md) |
| validating/blocking inappropriate content | [middlewares/provider-agnostic/guardrails.md](./resources/middlewares/provider-agnostic/guardrails.md) |
| preventing infinite LLM call loops | [middlewares/provider-agnostic/model-call-limit.md](./resources/middlewares/provider-agnostic/model-call-limit.md) |
| limiting tool calls to control costs | [middlewares/provider-agnostic/tool-call-limit.md](./resources/middlewares/provider-agnostic/tool-call-limit.md) |
| requiring human approval at checkpoints | [middlewares/provider-agnostic/human-in-the-loop.md](./resources/middlewares/provider-agnostic/human-in-the-loop.md) |
| dynamically selecting relevant tools | [middlewares/provider-agnostic/llm-tool-selector.md](./resources/middlewares/provider-agnostic/llm-tool-selector.md) |
| emulating tools with LLM for testing | [middlewares/provider-agnostic/llm-tool-emulator.md](./resources/middlewares/provider-agnostic/llm-tool-emulator.md) |
| agent needs persistent shell session | [middlewares/provider-agnostic/shell-tool.md](./resources/middlewares/provider-agnostic/shell-tool.md) |
| agent needs to search files (glob/grep) | [middlewares/provider-agnostic/file-search.md](./resources/middlewares/provider-agnostic/file-search.md) |
| modifying/removing messages at runtime | [middlewares/provider-agnostic/context-editing.md](./resources/middlewares/provider-agnostic/context-editing.md) |
| auto-summarizing near token limits | [middlewares/provider-agnostic/summarization.md](./resources/middlewares/provider-agnostic/summarization.md) |
| using OpenAI Responses API or moderation | [middlewares/provider-specific/openai.md](./resources/middlewares/provider-specific/openai.md) |
| using Claude caching/bash/text-editor | [middlewares/provider-specific/anthropic.md](./resources/middlewares/provider-specific/anthropic.md) |
| building custom before/after/wrap hooks | [middlewares/custom.md](./resources/middlewares/custom.md) |

---

## Verification

- [ ] CLAUDE.md checked (root + agent spec if exists, skipped if not)
- [ ] `deepagents` package installed (`deepagents[quickjs]` if using interpreter)
- [ ] Implementation order: backend → tools → subagents → middleware → agent
- [ ] Backend type matches requirements (State/Filesystem/Store/Composite)
- [ ] Backends instantiated directly (`StateBackend()`, `StoreBackend()`) — no factory closures (v0.5+)
- [ ] HITL configured for sensitive tools (if needed)
- [ ] Subagent `response_format` set when parent needs structured output (v0.5.3+)
- [ ] Interpreter PTC allowlist scoped only to required tools (if using `CodeInterpreterMiddleware`)
- [ ] Agent compiles and invokes successfully
