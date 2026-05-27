# Human-in-the-Loop (HITL)

Configure human approval for sensitive tool operations using the `interrupt_on` parameter.

## Contents

- Flow
- Configuration
- Interrupt Policies
- Decision Types
- With Built-in Filesystem Tools
- Requirements

## Flow

```
Agent ──> Check: Interrupt? ──> No ──> Execute ──> Agent
                │
                └──> Yes ──> Human Decision
                              ├── approve ──> Execute ──> Agent
                              ├── edit ──> Execute (modified) ──> Agent
                              └── reject ──> Cancel ──> Agent
```

## Configuration

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .models import get_deep_agent_model
from .tools import delete_file, read_file, send_email
from .utils import create_checkpointer

def set_deep_agent():
    return create_deep_agent(
        model=get_deep_agent_model(),
        tools=[delete_file, read_file, send_email],
        interrupt_on={
            "delete_file": True,                                         # All decisions allowed
            "read_file": False,                                          # No interrupts
            "send_email": {"allowed_decisions": ["approve", "reject"]},  # No editing
        },
        checkpointer=create_checkpointer(),  # Required!
    )
```

## Interrupt Policies

| Value | Behavior |
|-------|----------|
| `True` | Interrupt with all decisions: approve, edit, reject |
| `False` | No interrupt (tool executes immediately) |
| `{"allowed_decisions": [...]}` | Interrupt with only specified decisions |

## Decision Types

| Decision | Effect |
|----------|--------|
| `approve` | Execute the tool call as-is |
| `edit` | Execute with modified arguments |
| `reject` | Cancel the tool call, agent receives rejection feedback |

## With Built-in Filesystem Tools

```python
# casts.{cast_name}.modules.agents
from .utils import create_filesystem_backend, create_checkpointer

def set_deep_agent_with_hitl():
    return create_deep_agent(
        backend=create_filesystem_backend("/path/to/project"),
        interrupt_on={
            "write_file": True,    # Approve before writing
            "edit_file": True,     # Approve before editing
            "read_file": False,    # No approval needed for reads
            "execute": True,       # Approve shell commands (sandbox only)
        },
        checkpointer=create_checkpointer(),
    )
```

## Requirements

- **Checkpointer is mandatory**: HITL uses LangGraph's interrupt mechanism, which requires state persistence
- Without a checkpointer, `interrupt_on` will raise an error

```python
# casts.{cast_name}.modules.utils
from langgraph.checkpoint.memory import MemorySaver

def create_checkpointer():
    """Create checkpointer for HITL. Use PostgresSaver in production."""
    return MemorySaver()
```

## Handling Interrupts

```python
# casts.{cast_name}.modules.utils
from langgraph.types import Command

def check_for_interrupts(agent, config: dict):
    """Check agent state for pending interrupts."""
    state = agent.get_state(config)
    interrupts = []
    for task in state.tasks:
        if task.interrupts:
            for interrupt in task.interrupts:
                interrupts.append(interrupt)
    return interrupts

def resume_with_approve(agent, config: dict):
    """Resume interrupted agent with approval."""
    return agent.invoke(Command(resume=True), config=config)

def resume_with_reject(agent, config: dict):
    """Resume interrupted agent with rejection."""
    return agent.invoke(Command(resume=False), config=config)
```

For advanced resume patterns (multiple interrupts, edit/reject payloads), see the resume resource linked from SKILL.md.
