---
name: developing-cast
description: Use when implementing LangGraph components (state, nodes, edges, graph) with or without CLAUDE.md specs, stuck on workflow order (what order to implement), or need patterns for agents/models/tools/memory/middlewares/prompts (conversation memory, retry/fallback, guardrails, vector stores, tool management, etc.) - provides systematic workflow (state → deps → nodes → conditions → graph)
---
# Developing {{ cookiecutter.act_name }}'s Cast

Implement LangGraph casts following {{ cookiecutter.act_name }} Act patterns.

## When to Use

- Building nodes, agents, tools, or graphs
- Need LangGraph implementation patterns
- Have architecture specs to implement

## When NOT to Use

- Architecture design → `architecting-act`
- Project setup → `engineering-act`
- Testing → `testing-cast`

---

## Implementation Workflow

### Step 1: Understand CLAUDE.md

**If CLAUDE.md exists (distributed structure):**
- **Root `/CLAUDE.md`** contains:
  - **Act Overview**: {{ cookiecutter.act_name }} Act purpose and domain
  - **Casts Table**: All available casts in the project with links
- **Cast `/casts/{cast_slug}/CLAUDE.md`** contains:
  - **Cast Overview**: Purpose, Pattern, Latency
  - **Architecture Diagram**: Mermaid diagram with nodes and edges
  - **State Schema**: InputState, OutputState, OverallState
  - **Node Specifications**: Detailed node descriptions
  - **Technology Stack**: Additional dependencies and environment variables
- Identify which Cast to implement (check root Casts table)
- Read the cast's CLAUDE.md: `/casts/{cast_slug}/CLAUDE.md`
- Proceed to Step 2

**If CLAUDE.md not found:**
- Skip architecture analysis
- Proceed to Step 2

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

### Option Step 3: Create required environment variables (if needed)

Update to `.env.example` (project root)

```bash
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
```

### Option Step 4: Install dpendency packages (if needed)

Use `engineering-act`

---

## Component Reference

### Core Components

| Use when... | Resource |
|-------------|----------|
| defining graph state with TypedDict | [core/state.md](usage/core/state.md) |
| implementing sync/async node classes | [core/node.md](usage/core/node.md) |
| setting up edges or conditional routing | [core/edge.md](usage/core/edge.md) |
| assembling StateGraph and compiling | [core/graph.md](usage/core/graph.md) |
| reusing graphs as subgraphs | [core/subgraph.md](usage/core/subgraph.md) |

### Prompts & Messages

| Use when... | Resource |
|-------------|----------|
| creating System/Human/AI/Tool messages | [prompts/message-types.md](usage/prompts/message-types.md) |
| handling image/audio/PDF inputs | [prompts/multimodal.md](usage/prompts/multimodal.md) |

### Models & Agents

| Use when... | Resource |
|-------------|----------|
| choosing between OpenAI/Anthropic/Google | [models/select-chat-models.md](usage/models/select-chat-models.md) |
| configuring model (temperature, tokens) | [models/standalone-model.md](usage/models/standalone-model.md) |
| need model to return structured output(Pydantic schema) | [models/structured-output.md](usage/models/structured-output.md) |
| creating agent with tools | [agents/configuration.md](usage/agents/configuration.md) |
| need agent to return structured output(Pydantic schema) | [agents/structured-output.md](usage/agents/structured-output.md) |

### Tools

| Use when... | Resource |
|-------------|----------|
| creating simple tool with @tool | [tools/basic-tool.md](usage/tools/basic-tool.md) |
| tool needs complex Pydantic inputs | [tools/tool-with-complex-inputs.md](usage/tools/tool-with-complex-inputs.md) |
| tool needs to read/write state or store | [tools/access-context.md](usage/tools/access-context.md) |

### Memory

| Use when... | Resource |
|-------------|----------|
| adding conversation memory to agent | [memory/short-term/add-to-agent.md](usage/memory/short-term/add-to-agent.md) |
| customizing agent memory storage | [memory/short-term/customize-agent-memory.md](usage/memory/short-term/customize-agent-memory.md) |
| trimming/deleting/summarizing history | [memory/short-term/manage-conversations.md](usage/memory/short-term/manage-conversations.md) |
| accessing memory from middleware/tools | [memory/short-term/access-and-modify-memory.md](usage/memory/short-term/access-and-modify-memory.md) |
| persisting data across sessions (Store) | [memory/long-term/memory-storage.md](usage/memory/long-term/memory-storage.md) |
| accessing Store from within tools | [memory/long-term/in-tools.md](usage/memory/long-term/in-tools.md) |

### Middleware - Reliability

| Use when... | Resource |
|-------------|----------|
| LLM calls fail intermittently | [middlewares/provider-agnostic/model-retry.md](usage/middlewares/provider-agnostic/model-retry.md) |
| tool execution fails intermittently | [middlewares/provider-agnostic/tool-retry.md](usage/middlewares/provider-agnostic/tool-retry.md) |
| need backup model when primary fails | [middlewares/provider-agnostic/model-fallback.md](usage/middlewares/provider-agnostic/model-fallback.md) |

### Middleware - Safety & Control

| Use when... | Resource |
|-------------|----------|
| validating/blocking inappropriate content | [middlewares/provider-agnostic/guardrails.md](usage/middlewares/provider-agnostic/guardrails.md) |
| preventing infinite LLM call loops | [middlewares/provider-agnostic/model-call-limit.md](usage/middlewares/provider-agnostic/model-call-limit.md) |
| limiting tool calls to control costs | [middlewares/provider-agnostic/tool-call-limit.md](usage/middlewares/provider-agnostic/tool-call-limit.md) |
| requiring human approval at checkpoints | [middlewares/provider-agnostic/human-in-the-loop.md](usage/middlewares/provider-agnostic/human-in-the-loop.md) |

### Middleware - Tool Management

| Use when... | Resource |
|-------------|----------|
| dynamically selecting relevant tools | [middlewares/provider-agnostic/llm-tool-selector.md](usage/middlewares/provider-agnostic/llm-tool-selector.md) |
| emulating tools with LLM for testing | [middlewares/provider-agnostic/llm-tool-emulator.md](usage/middlewares/provider-agnostic/llm-tool-emulator.md) |
| agent needs persistent shell session | [middlewares/provider-agnostic/shell-tool.md](usage/middlewares/provider-agnostic/shell-tool.md) |
| agent needs to search files (glob/grep) | [middlewares/provider-agnostic/file-search.md](usage/middlewares/provider-agnostic/file-search.md) |
| agent needs task planning/tracking | [middlewares/provider-agnostic/to-do-list.md](usage/middlewares/provider-agnostic/to-do-list.md) |

### Middleware - Context

| Use when... | Resource |
|-------------|----------|
| modifying/removing messages at runtime | [middlewares/provider-agnostic/context-editing.md](usage/middlewares/provider-agnostic/context-editing.md) |
| auto-summarizing near token limits | [middlewares/provider-agnostic/summarization.md](usage/middlewares/provider-agnostic/summarization.md) |

### Middleware - Provider-Specific

| Use when... | Resource |
|-------------|----------|
| using OpenAI moderation API | [middlewares/provider-specific/openai.md](usage/middlewares/provider-specific/openai.md) |
| using Claude caching/bash/text-editor | [middlewares/provider-specific/anthropic.md](usage/middlewares/provider-specific/anthropic.md) |
| building custom before/after/wrap hooks | [middlewares/custom.md](usage/middlewares/custom.md) |

### Integrations

| Use when... | Resource |
|-------------|----------|
| converting text to embedding vectors | [integrations/embedding.md](usage/integrations/embedding.md) |
| using FAISS/Pinecone/Chroma stores | [integrations/vector-stores.md](usage/integrations/vector-stores.md) |
| splitting long documents into chunks | [integrations/text-spliter.md](usage/integrations/text-spliter.md) |

---

## Verification

- [ ] CLAUDE.md checked (root + cast-specific if exists, skipped if not)
  - [ ] Root `/CLAUDE.md` reviewed for Act context
  - [ ] Cast `/casts/{cast_slug}/CLAUDE.md` reviewed for specifications
- [ ] Files in order: state → dependency modules → nodes → conditions → graph
- [ ] Node names lowercase in graph.py
- [ ] START/END imported from `langgraph.graph`
- [ ] Nodes added as instances
- [ ] Graph compiles

---

## Next Steps

1. **Test:** `testing-cast` skill
2. **Debug:** `uv run langgraph dev`