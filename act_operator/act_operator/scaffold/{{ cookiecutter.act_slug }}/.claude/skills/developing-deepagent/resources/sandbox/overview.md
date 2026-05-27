# Sandbox Overview

Sandboxes are specialized backends that run agent code in an isolated environment with their own filesystem and an `execute` tool for shell commands.

## What Sandboxes Provide

Unlike other backends, sandbox backends give the agent:

- All standard filesystem tools: `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`
- The **`execute` tool** for running arbitrary shell commands
- A secure boundary that protects your host system

## Available Providers

| Provider | Package | Environment | Use Case |
|----------|---------|-------------|----------|
| **Daytona** | `langchain-daytona` | Remote VM | Full Linux environment |
| **Modal** | `langchain-modal` | Remote container | Scalable cloud execution |
| **Runloop** | `langchain-runloop` | Remote | Managed execution |
| **LocalShellBackend** | Built-in | Local machine | Dev/testing only |

## Quick Comparison

| Feature | Daytona | Modal | Runloop | LocalShell |
|---------|---------|-------|---------|------------|
| Isolation | Full VM | Container | Full | None |
| Network | Configurable | Configurable | Configurable | Full |
| Persistence | Session | Session | Session | Permanent |
| Cost | Pay per use | Pay per use | Pay per use | Free |
| Production-ready | Yes | Yes | Yes | No |

## Basic Usage Pattern

```python
# casts.{cast_name}.modules.utils
def create_sandbox():
    """Create sandbox (provider-specific — see the sandbox provider resource from SKILL.md)."""
    ...

# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .models import get_deep_agent_model

def set_deep_agent(sandbox):
    return create_deep_agent(
        model=get_deep_agent_model(),
        system_prompt="You are a coding assistant with sandbox access.",
        backend=sandbox,
    )
```

## When to Use Sandboxes

- Agent needs to run arbitrary code safely
- Agent needs to install dependencies
- Agent needs shell access without host machine risk
- Production environments requiring filesystem interaction

## When NOT to Use Sandboxes

- Agent only needs file read/write → use `FilesystemBackend`
- Agent only needs ephemeral storage → use `StateBackend`
- Local development where host access is acceptable → use `LocalShellBackend` (carefully)
