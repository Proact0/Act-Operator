# Shell Tool

Expose a persistent shell session to agents for command execution.

**Warning:** Use appropriate execution policies for your security requirements.

## Basic Usage

```python
# casts.{cast_name}.modules.middlewares
from langchain.agents.middleware import ShellToolMiddleware, HostExecutionPolicy

def get_shell_middleware():
    return ShellToolMiddleware(
        workspace_root="/workspace",
        execution_policy=HostExecutionPolicy(),
    )
```

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from .middlewares import get_shell_middleware

def set_shell_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[],  # Middleware adds shell tool
        middleware=[get_shell_middleware()],
    )
```

## Execution Policies

| Policy | Description |
|--------|-------------|
| `HostExecutionPolicy` | Full host access (default) |
| `DockerExecutionPolicy` | Isolated Docker container |
| `CodexSandboxExecutionPolicy` | Codex CLI sandbox |

## Docker Isolation Example

```python
# casts.{cast_name}.modules.middlewares
from langchain.agents.middleware import ShellToolMiddleware, DockerExecutionPolicy

def get_isolated_shell_middleware():
    return ShellToolMiddleware(
        workspace_root="/workspace",
        startup_commands=["pip install requests"],
        execution_policy=DockerExecutionPolicy(
            image="python:3.11-slim",
            command_timeout=60.0,
        ),
    )
```

## Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `workspace_root` | Temp dir | Base directory for shell |
| `startup_commands` | None | Commands on session start |
| `shutdown_commands` | None | Commands before shutdown |
| `execution_policy` | HostExecutionPolicy | Security policy |
| `redaction_rules` | None | Output sanitization rules |
| `env` | None | Environment variables |

**Note:** Persistent sessions do not work with HITL interrupts.
