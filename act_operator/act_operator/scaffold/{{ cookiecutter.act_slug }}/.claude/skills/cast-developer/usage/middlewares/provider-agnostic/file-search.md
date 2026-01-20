# File Search

Provide Glob and Grep search tools over filesystem files.

## Basic Usage

```python
# casts.{cast_name}.modules.middlewares
from langchain.agents.middleware import FilesystemFileSearchMiddleware

def get_file_search_middleware():
    return FilesystemFileSearchMiddleware(
        root_path="/workspace",
        use_ripgrep=True,
        max_file_size_mb=10,
    )
```

```python
# casts.{cast_name}.modules.agents
from langchain.agents import create_agent
from .middlewares import get_file_search_middleware

def set_file_search_agent():
    return create_agent(
        model=get_sample_model(),
        tools=[],  # Middleware adds glob_search and grep_search
        middleware=[get_file_search_middleware()],
    )
```

## Provided Tools

| Tool | Description |
|------|-------------|
| `glob_search` | File pattern matching (`**/*.py`, `src/**/*.ts`) |
| `grep_search` | Content search with regex, supports `include` filter and output modes |

## Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `root_path` | Required | Root directory for searches |
| `use_ripgrep` | True | Use ripgrep (falls back to Python regex) |
| `max_file_size_mb` | 10 | Skip files larger than this |
