---
name: developing-cast
description: Implements LangGraph cast components following systematic workflow (state, deps, nodes, conditions, graph). Use when implementing cast, building nodes/agents/tools, need LangGraph patterns (memory, retry, guardrails, vector stores, node timeouts, error handlers, DeltaChannel, graceful shutdown), or ask "implement cast", "build graph", "add node".
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
# Developing Backend's Cast

Implement LangGraph casts following Backend Act patterns.

## When to Use

- Building nodes, agents, tools, or graphs
- Need LangGraph implementation patterns
- Have architecture specs to implement

## When NOT to Use

- Architecture design → `architecting-act`
- DeepAgent harness (create_deep_agent, backends, subagents) → `developing-deepagent`
- Project / cast scaffolding → run `uv run act new` (project) or `uv run act cast` (new cast) directly
- Testing → `testing-cast`

---

## Implementation Workflow

### Step 1: Understand CLAUDE.md

> **Act** = Project, **Cast** = Graph/Workflow in the project

**If CLAUDE.md exists:**
1. Read `/CLAUDE.md` → Act overview, find target cast
2. Read `/casts/{cast_slug}/CLAUDE.md` → Architecture diagram, node specs
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

- Yes → use `architecting-act` skill first
- No → proceed to Step 2

### Step 2: Implementation

**Implement in order:** state → dependency modules → nodes → conditions → graph
  - Use Component Reference tables below for each component type

```
1. State (state.py)           # Foundation
   ↓
2. Dependency modules         # agents, models, tools, prompts, middlewares, utils (if needed)
   ↓
3. Nodes (nodes.py)           # Business logic
   ↓
4. Conditions (conditions.py) # Route Functions (if needed)
   ↓
5. Graph (graph.py)           # Assembly
```

### Optional Step 3: Create required environment variables (if needed)

Update `.env.example` (project root):

```bash
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
```

### Optional Step 4: Install dependency packages (if needed)

```bash
uv add --package {{ cookiecutter.act_slug }} <package-name>
```

---

## Component Reference

### Core Components

| Use when | Resource |
|-------------|----------|
| defining graph state with TypedDict | [core/state.md](./resources/core/state.md) |
| implementing sync/async node classes | [core/node.md](./resources/core/node.md) |
| using prebuilt ToolNode for tool execution | [core/tool-node.md](./resources/core/tool-node.md) |
| setting up edges or conditional routing | [core/edge.md](./resources/core/edge.md) |
| assembling StateGraph and compiling | [core/graph.md](./resources/core/graph.md) |
| reusing graphs as subgraphs | [core/subgraph.md](./resources/core/subgraph.md) |

### Prompts & Messages

| Use when | Resource |
|-------------|----------|
| creating System/Human/AI/Tool messages | [prompts/message-types.md](./resources/prompts/message-types.md) |
| handling image/audio/PDF inputs | [prompts/multimodal.md](./resources/prompts/multimodal.md) |

### Models & Agents

| Use when | Resource |
|-------------|----------|
| choosing between OpenAI/Anthropic/Google | [models/select-chat-models.md](./resources/models/select-chat-models.md) |
| configuring model (temperature, tokens) | [models/standalone-model.md](./resources/models/standalone-model.md) |
| need model to return structured output(Pydantic schema) | [models/structured-output.md](./resources/models/structured-output.md) |
| creating agent with tools | [agents/configuration.md](./resources/agents/configuration.md) |
| need agent to return structured output(Pydantic schema) | [agents/structured-output.md](./resources/agents/structured-output.md) |

### Tools

| Use when | Resource |
|-------------|----------|
| creating simple tool with @tool | [tools/basic-tool.md](./resources/tools/basic-tool.md) |
| tool needs complex Pydantic inputs | [tools/tool-with-complex-inputs.md](./resources/tools/tool-with-complex-inputs.md) |
| tool needs to read/write state or store | [tools/access-context.md](./resources/tools/access-context.md) |

### Memory

| Use when | Resource |
|-------------|----------|
| adding conversation memory to agent | [memory/short-term/add-to-agent.md](./resources/memory/short-term/add-to-agent.md) |
| customizing agent memory storage | [memory/short-term/customize-agent-memory.md](./resources/memory/short-term/customize-agent-memory.md) |
| trimming/deleting/summarizing history | [memory/short-term/manage-conversations.md](./resources/memory/short-term/manage-conversations.md) |
| accessing memory from middleware/tools | [memory/short-term/access-and-modify-memory.md](./resources/memory/short-term/access-and-modify-memory.md) |
| persisting data across sessions (Store) | [memory/long-term/memory-storage.md](./resources/memory/long-term/memory-storage.md) |
| accessing Store from within tools | [memory/long-term/in-tools.md](./resources/memory/long-term/in-tools.md) |

### Middleware - Reliability

| Use when | Resource |
|-------------|----------|
| LLM calls fail intermittently | [middlewares/provider-agnostic/model-retry.md](./resources/middlewares/provider-agnostic/model-retry.md) |
| tool execution fails intermittently | [middlewares/provider-agnostic/tool-retry.md](./resources/middlewares/provider-agnostic/tool-retry.md) |
| need backup model when primary fails | [middlewares/provider-agnostic/model-fallback.md](./resources/middlewares/provider-agnostic/model-fallback.md) |

### Middleware - Safety & Control

| Use when | Resource |
|-------------|----------|
| validating/blocking inappropriate content | [middlewares/provider-agnostic/guardrails.md](./resources/middlewares/provider-agnostic/guardrails.md) |
| preventing infinite LLM call loops | [middlewares/provider-agnostic/model-call-limit.md](./resources/middlewares/provider-agnostic/model-call-limit.md) |
| limiting tool calls to control costs | [middlewares/provider-agnostic/tool-call-limit.md](./resources/middlewares/provider-agnostic/tool-call-limit.md) |
| requiring human approval at checkpoints | [middlewares/provider-agnostic/human-in-the-loop.md](./resources/middlewares/provider-agnostic/human-in-the-loop.md) |

### Middleware - Tool Management

| Use when | Resource |
|-------------|----------|
| dynamically selecting relevant tools | [middlewares/provider-agnostic/llm-tool-selector.md](./resources/middlewares/provider-agnostic/llm-tool-selector.md) |
| emulating tools with LLM for testing | [middlewares/provider-agnostic/llm-tool-emulator.md](./resources/middlewares/provider-agnostic/llm-tool-emulator.md) |
| agent needs persistent shell session | [middlewares/provider-agnostic/shell-tool.md](./resources/middlewares/provider-agnostic/shell-tool.md) |
| agent needs to search files (glob/grep) | [middlewares/provider-agnostic/file-search.md](./resources/middlewares/provider-agnostic/file-search.md) |
| agent needs task planning/tracking | [middlewares/provider-agnostic/to-do-list.md](./resources/middlewares/provider-agnostic/to-do-list.md) |

### Middleware - Context

| Use when | Resource |
|-------------|----------|
| modifying/removing messages at runtime | [middlewares/provider-agnostic/context-editing.md](./resources/middlewares/provider-agnostic/context-editing.md) |
| auto-summarizing near token limits | [middlewares/provider-agnostic/summarization.md](./resources/middlewares/provider-agnostic/summarization.md) |

### Middleware - Provider-Specific

| Use when | Resource |
|-------------|----------|
| using OpenAI moderation API | [middlewares/provider-specific/openai.md](./resources/middlewares/provider-specific/openai.md) |
| using Claude caching/bash/text-editor | [middlewares/provider-specific/anthropic.md](./resources/middlewares/provider-specific/anthropic.md) |
| building custom before/after/wrap hooks | [middlewares/custom.md](./resources/middlewares/custom.md) |

### Integrations

| Use when | Resource |
|-------------|----------|
| converting text to embedding vectors | [integrations/embedding.md](./resources/integrations/embedding.md) |
| using FAISS/Pinecone/Chroma stores | [integrations/vector-stores.md](./resources/integrations/vector-stores.md) |
| splitting long documents into chunks | [integrations/text-splitter.md](./resources/integrations/text-splitter.md) |

---

## Verification

- [ ] CLAUDE.md checked (root + cast-specific if exists, skipped if not)
- [ ] Implementation order: state → deps(option) → nodes → conditions(option) → graph
- [ ] Nodes match CLAUDE.md specs
- [ ] Dependencies installed, env vars configured
- [ ] Graph compiles