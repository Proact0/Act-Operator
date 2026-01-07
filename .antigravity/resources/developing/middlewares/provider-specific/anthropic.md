# Anthropic Middleware

Middleware designed for Claude models.

## Contents

- Prompt Caching
- Bash Tool
- Text Editor (State-based, Filesystem-based)
- Memory (State-based, Filesystem-based)
- File Search (State-based)

## Prompt Caching

Reduce costs and latency by caching static prompt content.

```python
# casts.{cast_name}.modules.middlewares
from langchain_anthropic.middleware import AnthropicPromptCachingMiddleware

def get_prompt_caching_middleware():
    return AnthropicPromptCachingMiddleware(ttl="5m")
```

```python
# casts.{cast_name}.modules.agents
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from .middlewares import get_prompt_caching_middleware

def set_cached_agent():
    return create_agent(
        model=ChatAnthropic(model="claude-sonnet-4-5-20250929"),
        system_prompt="<Your long system prompt>",
        middleware=[get_prompt_caching_middleware()],
    )
```

### Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `type` | "ephemeral" | Cache type |
| `ttl` | "5m" | Time to live: `'5m'` or `'1h'` |
| `min_messages_to_cache` | 0 | Min messages before caching |
| `unsupported_model_behavior` | "warn" | `'ignore'`, `'warn'`, `'raise'` |

---

## Bash Tool

Execute Claude's native `bash_20250124` tool with local execution.

```python
# casts.{cast_name}.modules.middlewares
from langchain_anthropic.middleware import ClaudeBashToolMiddleware

def get_claude_bash_middleware():
    return ClaudeBashToolMiddleware(workspace_root="/workspace")
```

```python
# casts.{cast_name}.modules.agents
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from .middlewares import get_claude_bash_middleware

def set_bash_agent():
    return create_agent(
        model=ChatAnthropic(model="claude-sonnet-4-5-20250929"),
        tools=[],
        middleware=[get_claude_bash_middleware()],
    )
```

Accepts all `ShellToolMiddleware` parameters: `workspace_root`, `startup_commands`, `execution_policy`, `redaction_rules`.

---

## Text Editor

Provide Claude's `text_editor_20250728` tool for file operations.

### State-based (files in LangGraph state)

```python
# casts.{cast_name}.modules.middlewares
from langchain_anthropic.middleware import StateClaudeTextEditorMiddleware

def get_state_text_editor_middleware():
    return StateClaudeTextEditorMiddleware(
        allowed_path_prefixes=["/project"],
    )
```

### Filesystem-based (files on disk)

```python
# casts.{cast_name}.modules.middlewares
from langchain_anthropic.middleware import FilesystemClaudeTextEditorMiddleware

def get_fs_text_editor_middleware():
    return FilesystemClaudeTextEditorMiddleware(
        root_path="/workspace",
        allowed_prefixes=["/src"],
        max_file_size_mb=10,
    )
```

**Commands:** `view`, `create`, `str_replace`, `insert`, `delete`, `rename`

---

## Memory

Provide Claude's `memory_20250818` tool for persistent agent memory.

### State-based

```python
# casts.{cast_name}.modules.middlewares
from langchain_anthropic.middleware import StateClaudeMemoryMiddleware

def get_state_memory_middleware():
    return StateClaudeMemoryMiddleware()  # Uses /memories directory
```

### Filesystem-based

```python
# casts.{cast_name}.modules.middlewares
from langchain_anthropic.middleware import FilesystemClaudeMemoryMiddleware

def get_fs_memory_middleware():
    return FilesystemClaudeMemoryMiddleware(root_path="/workspace")
```

---

## File Search (State-based)

Provide Glob and Grep tools for state-based files.

```python
# casts.{cast_name}.modules.middlewares
from langchain_anthropic.middleware import (
    StateClaudeTextEditorMiddleware,
    StateFileSearchMiddleware,
)

def get_editor_with_search_middlewares():
    return [
        StateClaudeTextEditorMiddleware(),
        StateFileSearchMiddleware(state_key="text_editor_files"),
    ]

def get_memory_with_search_middlewares():
    return [
        StateClaudeMemoryMiddleware(),
        StateFileSearchMiddleware(state_key="memory_files"),
    ]
```

```python
# casts.{cast_name}.modules.agents
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from .middlewares import get_editor_with_search_middlewares

def set_editor_agent():
    return create_agent(
        model=ChatAnthropic(model="claude-sonnet-4-5-20250929"),
        tools=[],
        middleware=get_editor_with_search_middlewares(),
    )
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `state_key` | "text_editor_files" | `"text_editor_files"` or `"memory_files"` |
