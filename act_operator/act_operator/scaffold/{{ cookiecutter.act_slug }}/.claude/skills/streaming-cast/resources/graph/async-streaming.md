# Async Event Streaming

Consume graph output asynchronously using `graph.astream_events(..., version="v3")`. `casts/{cast_name}/modules/` and `casts/{cast_name}/graph.py` are reserved for graph definition; **stream consumer code lives anywhere else** — pick the entry point that fits the project (an additional cast module such as `runtime.py`, an external API endpoint module, or an async script).

## Contents

- Basic Pattern
- Parameters
- Python < 3.11 Workaround

## Basic Pattern

```python
# stream consumer — location flexible
from casts.{{ cookiecutter.cast_snake }}.graph import {{ cookiecutter.cast_snake }}_graph

graph = {{ cookiecutter.cast_snake }}_graph()

config = {
    "configurable": {
        "actor_id": user_id,
        "thread_id": session_id,
    },
    "recursion_limit": 2000,
}

stream = await graph.astream_events(inputs, config=config, version="v3")

async for message in stream.messages:
    async for token in message.text:
        await send_token(token)

final_state = await stream.output
```

For projection-specific patterns, multi-projection concurrent consumption (`asyncio.gather`), and transport (SSE/WebSocket) integration, see the projections, multiple-modes, and integration resources linked from SKILL.md.

---

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input` | dict \| Command \| None | — | Input state (or `Command` for resume) |
| `config` | dict \| None | `None` | Execution config (thread_id, actor_id, recursion_limit) |
| `version` | `"v3"` | required | Always pass `"v3"` for the typed-projection event stream |
| `transformers` | list | `[]` | Custom `StreamTransformer` classes for `stream.extensions` projections |
| `context` | ContextT \| None | `None` | Static context for the run |
| `durability` | `"sync"` \| `"async"` \| `"exit"` \| None | `None` | Checkpoint persistence timing. Requires checkpointer |
| `interrupt_before` | list \| `"*"` \| None | `None` | Nodes to interrupt before execution |
| `interrupt_after` | list \| `"*"` \| None | `None` | Nodes to interrupt after execution |
| `control` | `RunControl` \| None | `None` | Graceful shutdown handle (langgraph v1.2+) |

---

## Python < 3.11 Workaround

Python < 3.11 asyncio doesn't propagate context automatically. Pass `config` explicitly to `astream_events()` **and** to LLM calls inside async nodes:

```python
from casts.base_node import AsyncBaseNode

class LLMNode(AsyncBaseNode):
    async def execute(self, state, config):
        # Explicit config propagation ensures streaming callbacks work
        response = await self.model.ainvoke(state["messages"], config)
        return {"response": response}
```

**Recommendation:** Upgrade to Python 3.11+.
