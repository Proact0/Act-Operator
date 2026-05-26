# CodeInterpreterMiddleware (Interpreters)

Lightweight code-execution layer for Deep Agents using a scoped QuickJS runtime. Lets the agent compose tools, orchestrate subagents, and transform structured data without round-tripping every step through the model. Available in deepagents v0.6+ (experimental).

> Interpreters require `langchain-quickjs>=0.1.0` and Python `>=3.11`. APIs are experimental and may change between releases.

## Contents

- When to Use
- Installation
- Basic Usage
- Programmatic Tool Calling (PTC)
- Snapshots Across Turns
- Middleware Options
- Security & Capability Boundary

## When to Use

| Need | Use |
|------|-----|
| One or two simple external calls | Normal tool calling |
| Small program with loops, branching, retries, aggregation | Interpreter |
| Many tool calls that should run from code | Interpreter + PTC |
| Reusable code helpers across threads | Interpreter + interpreter skills |
| Shell commands, package installs, OS filesystem access | Sandbox backend |

The interpreter is a code-first way to act **inside the agent loop** (composing tools, preserving state). Sandboxes are a code-first way to act on **an environment** (running commands, editing files).

---

## Installation

```bash
uv add --package {{ cookiecutter.act_slug }} "deepagents[quickjs]"
```

---

## Basic Usage

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware
from .models import get_deep_agent_model


def set_interpreter_agent():
    return create_deep_agent(
        model=get_deep_agent_model(),
        middleware=[CodeInterpreterMiddleware()],
    )
```

The middleware adds an `eval` tool. The agent writes TypeScript that runs in a persistent context, with `console.log` capture and last-expression return:

```typescript
const rows = [
  { team: "alpha", score: 8 },
  { team: "beta", score: 13 },
  { team: "alpha", score: 21 },
];

const totals = rows.reduce((acc, row) => {
  acc[row.team] = (acc[row.team] ?? 0) + row.score;
  return acc;
}, {});

totals;
```

---

## Programmatic Tool Calling (PTC)

PTC exposes selected agent tools inside the interpreter under a `tools` namespace, letting the agent write code that calls tools in loops, branches, retries, or parallel batches. Intermediate results stay in the interpreter — only the final synthesis returns to the model.

Tool names are converted to camelCase. For example, `web_search` becomes `tools.webSearch(...)`.

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware
from .models import get_deep_agent_model


def set_ptc_agent():
    return create_deep_agent(
        model=get_deep_agent_model(),
        middleware=[CodeInterpreterMiddleware(ptc=["task", "web_search"])],
    )
```

Interpreter code can then call allowlisted tools:

```typescript
const topics = ["retrieval", "memory", "evaluation"];

const reports = await Promise.all(
  topics.map((topic) =>
    tools.task({
      description: `Research ${topic} in Deep Agents and return three concise findings.`,
      subagent_type: "general-purpose",
    }),
  ),
);

reports.join("\n\n");
```

| Pattern | What the interpreter can do |
|---------|-----------------------------|
| Batch processing | Loop over many inputs and call a tool for each |
| Parallel work | Use `Promise.all` for independent calls |
| Conditional logic | Branch on earlier results |
| Early termination | Stop calling tools once a success condition is met |
| Data filtering | Return only relevant rows/snippets/errors/summaries to the model |
| Recursive orchestration | Call `task` repeatedly and combine subagent results in code |

> **HITL note:** PTC calls execute through the interpreter bridge and do **not** go through the normal tool-calling path. `interrupt_on` approval workflows are **not enforced per PTC-invoked tool call**. Treat the PTC allowlist as the permission boundary.

---

## Snapshots Across Turns

By default, `CodeInterpreterMiddleware` snapshots interpreter state after each agent run and restores it before the next run — giving the next turn the same globals, variables, functions, and modules.

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware
from langgraph.checkpoint.memory import MemorySaver
from .models import get_deep_agent_model


def set_interpreter_agent_with_checkpoint():
    return create_deep_agent(
        model=get_deep_agent_model(),
        checkpointer=MemorySaver(),
        middleware=[
            CodeInterpreterMiddleware(snapshot_between_turns=True),  # Default
        ],
    )
```

### Snapshot rules

- Within a single agent run, repeated `eval` calls share the live interpreter context (no snapshot between calls).
- Between turns, only serializable values survive. Functions, classes, and other in-process handles are restored as inaccessible artifacts — accessing one raises an error.
- Snapshots preserve **interpreter memory**, not outside-world effects. Replaying a checkpoint does not undo side effects from PTC-invoked tool calls.
- With a checkpointer, snapshots are stored in graph state and participate in LangGraph time travel.

Disable cross-turn snapshots with `snapshot_between_turns=False` when you want each turn to start from a clean interpreter.

---

## Middleware Options

| Kwarg | Default | Purpose |
|-------|---------|---------|
| `memory_limit` | `64 * 1024 * 1024` (64 MB) | QuickJS heap memory limit (bytes) |
| `timeout` | `5.0` | Per-`eval` timeout (seconds) |
| `max_ptc_calls` | `256` | Maximum `tools.*` calls per `eval`. Use `None` only in trusted environments |
| `tool_name` | `"eval"` | Name of the interpreter tool exposed to the model |
| `max_result_chars` | `4000` | Maximum characters returned from result and stdout blocks |
| `capture_console` | `True` | Capture `console.log`/`warn`/`error` output |
| `ptc` | `None` | PTC allowlist: list of tool names or `BaseTool` instances |
| `skills_backend` | `None` | Backend used to resolve interpreter skill modules |
| `snapshot_between_turns` | `True` | Whether interpreter state snapshots persist across agent turns |
| `max_snapshot_bytes` | `None` | Maximum serialized snapshot size (defaults to `memory_limit`) |

---

## Security & Capability Boundary

Interpreters use QuickJS for **scoped JavaScript execution**, not a full process sandbox. Treat it as a capability boundary, not a host-isolation boundary.

| Capability | Available by default | How to expose it |
|-----------|----------------------|------------------|
| JavaScript execution | Yes | Add the middleware |
| Top-level await | Yes | Use promises in interpreter code |
| `console.log` capture | Yes | Disable with `capture_console=False` |
| Agent tools | No | Add a PTC allowlist |
| Interpreter skill modules | No | Add a module entry, configure `skills_backend` |
| Filesystem access | No | Add built-in filesystem tools via the PTC allowlist |
| Network access | No | Expose a specific network tool via PTC |
| Wall-clock / datetime | No | Expose an explicit time tool if needed |
| Shell / package installs / OS-level execution | No | Use a sandbox backend instead |

**Operational guidance:**
- Treat the PTC allowlist as the permission surface — only expose tools the agent needs.
- For untrusted or semi-trusted code, run agents in isolated worker processes or containers and keep the allowlist narrow.
- QuickJS is single-process and same-memory — it does not provide host-memory isolation by itself.

---

## Interpreter vs Sandbox

| Use interpreter when… | Use sandbox when… |
|-----------------------|-------------------|
| Composing tool calls, branching, aggregating | Running shell commands or installing packages |
| Keeping intermediate values out of model context | Building and testing code, executing CLIs |
| Deterministic data transformation | Operating on a real OS filesystem |
| Coordinating subagents through `task` PTC | Network calls beyond an allowlisted tool |
