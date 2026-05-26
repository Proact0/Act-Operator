# StateBackend

Ephemeral in-state filesystem backend. This is the **default** backend when no backend is specified.

## Overview

- Files are stored in LangGraph graph state
- Only persists for a **single thread** — files are lost when the conversation ends
- No disk access, no persistence across threads
- Ideal for stateless tasks and prototyping

## Implicit Usage (Default)

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .models import get_deep_agent_model

def set_deep_agent():
    """StateBackend is the default — no need to specify."""
    return create_deep_agent(
        model=get_deep_agent_model(),
    )
```

## Explicit Usage (deepagents v0.5+)

`StateBackend()` is instantiated directly — no factory required.

```python
# casts.{cast_name}.modules.utils
from deepagents.backends import StateBackend

def get_state_backend():
    """Direct StateBackend instance."""
    return StateBackend()
```

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .utils import get_state_backend

def set_deep_agent():
    return create_deep_agent(
        model=get_deep_agent_model(),
        backend=get_state_backend(),
    )
```

## Seeding Files

With StateBackend, seed initial files via the `files` key using `create_file_data()`:

```python
# casts.{cast_name}.modules.utils
from deepagents.backends.utils import create_file_data

def create_seed_files():
    """Prepare seed files for StateBackend."""
    return {
        "/config.json": create_file_data('{"key": "value"}'),
        "/skills/my-skill/SKILL.md": create_file_data("---\nname: my-skill\n---\n# My Skill"),
    }
```

### Binary Files (v0.5+)

StateBackend now supports binary file storage for PDFs, images, audio, and video:

```python
# casts.{cast_name}.modules.utils
from deepagents.backends.utils import create_file_data

def create_seed_files_with_binary():
    """Prepare seed files including binary content."""
    with open("logo.png", "rb") as f:
        logo_bytes = f.read()
    return {
        "/config.json": create_file_data('{"key": "value"}'),
        "/assets/logo.png": create_file_data(logo_bytes),
    }
```

> **Important**: Raw strings are not supported for `files`. Always use `create_file_data()`. Binary content (bytes) is supported as of v0.5.

## Factory Pattern (deprecated)

> Direct instantiation of `StateBackend()` is the supported form since deepagents v0.5.0. The factory form `backend=(lambda rt: StateBackend(rt))` is **deprecated** — keep only for code that still targets pre-0.5 releases.

## When to Use

- Prototyping and development
- Stateless single-turn tasks
- When no filesystem persistence is needed
- As the default backend in a CompositeBackend

## When NOT to Use

- Need files to persist across threads → use `StoreBackend`
- Need real disk access → use `FilesystemBackend`
- Need code execution → use a sandbox backend
- Need hybrid storage → use `CompositeBackend`
