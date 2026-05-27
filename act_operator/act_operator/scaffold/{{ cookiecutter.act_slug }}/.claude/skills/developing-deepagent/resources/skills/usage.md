# Adding Skills to Deep Agent

Skills provide specialized workflows and domain knowledge to your deep agent via progressive disclosure.

## Contents

- What Are Skills
- How Skills Work
- With FilesystemBackend
- With StateBackend
- With StoreBackend
- SKILL.md Format
- Skill Path Rules

## What Are Skills

Skills are directories containing:

- **SKILL.md**: Instructions and metadata (required)
- **Scripts**: Supporting code (optional)
- **References**: Documentation (optional)
- **Assets**: Templates and other resources (optional)

## How Skills Work

1. At startup, the agent reads frontmatter (name, description) from each SKILL.md
2. During conversation, the agent determines which skills are relevant
3. Only relevant skills are loaded into context (**progressive disclosure**)

## With FilesystemBackend

```python
# casts.{cast_name}.modules.utils
from deepagents.backends import FilesystemBackend

def create_skill_backend(root_dir: str = "."):
    return FilesystemBackend(root_dir=root_dir, virtual_mode=True)
```

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .utils import create_skill_backend, create_checkpointer

def set_deep_agent():
    return create_deep_agent(
        backend=create_skill_backend("/path/to/project"),
        skills=["./skills/"],
        checkpointer=create_checkpointer(),
    )
```

Directory structure:

```
/path/to/project/
├── skills/
│   ├── web-research/
│   │   ├── SKILL.md
│   │   └── scripts/
│   └── data-analysis/
│       ├── SKILL.md
│       └── references/
└── ...
```

## With StateBackend

Provide skill files via `invoke(files={...})`:

```python
# casts.{cast_name}.modules.utils
from deepagents.backends.utils import create_file_data

def create_skill_files():
    """Prepare skill files for StateBackend seeding."""
    skill_content = """---
name: my-skill
description: Does something useful
---
# My Skill
Instructions here...
"""
    return {
        "/skills/my-skill/SKILL.md": create_file_data(skill_content),
    }
```

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent
from .utils import create_checkpointer

def set_deep_agent():
    return create_deep_agent(
        skills=["./skills/"],
        checkpointer=create_checkpointer(),
    )
```

> **Important**: Use `create_file_data()` from `deepagents.backends.utils`. Raw strings are not supported.

## With StoreBackend

Pre-seed skills into the store for persistent access:

```python
# casts.{cast_name}.modules.utils
from deepagents.backends import StoreBackend
from deepagents.backends.utils import create_file_data
from langgraph.store.memory import InMemoryStore

def create_skill_store():
    """Create store with pre-seeded skill files."""
    store = InMemoryStore()
    store.put(
        namespace=("filesystem",),
        key="/skills/my-skill/SKILL.md",
        value=create_file_data("---\nname: my-skill\n---\n# Instructions"),
    )
    return store
```

```python
# casts.{cast_name}.modules.utils
from deepagents.backends import StoreBackend


def get_store_backend():
    return StoreBackend()
```

```python
# casts.{cast_name}.modules.agents
from deepagents import create_deep_agent

from .utils import create_skill_store, get_store_backend


def set_deep_agent():
    return create_deep_agent(
        backend=get_store_backend(),
        store=create_skill_store(),
        skills=["/skills/"],
    )
```

## SKILL.md Format

```markdown
---
name: my-skill
description: Short description for progressive disclosure matching
version: "1.0.0"
---

# My Skill

Detailed instructions that the agent follows when this skill is activated.

## When to Use
- Scenario 1
- Scenario 2

## Steps
1. Step one
2. Step two
```

## Skill Path Rules

- Paths use forward slashes (`/`)
- Paths are relative to the backend's root
- Later sources override earlier ones for skills with the same name (last one wins)
- Multiple skill directories can be specified: `skills=["./skills/", "./extra-skills/"]`
