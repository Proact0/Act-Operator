---
name: testing-debugging
description: Test and debug LangGraph applications. Use when writing tests, debugging graphs, troubleshooting issues, or validating Cast structure in Act projects.
---

# Testing & Debugging

## Overview

Testing and debugging in Act projects uses pytest for testing and LangGraph dev server for debugging. This skill provides workflows for effective testing and debugging strategies.

## When to Use This Skill

- Writing unit tests for nodes
- Writing integration tests for graphs
- Debugging graph execution
- Using LangGraph Studio
- Troubleshooting issues

## Testing Checklist

Before deploying:

- [ ] Unit tests for all nodes
- [ ] Integration tests for graph flows
- [ ] Edge case testing
- [ ] Error handling tested
- [ ] Tests pass with `uv run pytest -q`

## Testing Workflow

### 1. Write Unit Tests

```python
# tests/unit_tests/test_nodes.py
from casts.my_cast.modules.nodes import ProcessNode
from casts.my_cast.modules.state import State

def test_process_node():
    node = ProcessNode()
    state = State(query="test")
    result = node(state)
    assert "result" in result
```

### 2. Write Integration Tests

```python
# tests/integration_tests/test_graph.py
from casts.my_cast.graph import my_cast_graph

def test_graph_execution():
    graph = my_cast_graph()
    result = graph.invoke({"query": "test"})
    assert "messages" in result
```

### 3. Run Tests

```bash
# All tests
uv run pytest -q

# Specific test file
uv run pytest tests/unit_tests/test_nodes.py

# With coverage
uv run pytest --cov
```

## Debugging Workflow

### 1. Start Dev Server

```bash
uv run langgraph dev
```

### 2. Open LangGraph Studio

Navigate to: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

### 3. Step Through Execution

- Select graph from dropdown
- Enter input
- Step through nodes
- Inspect state at each step

## Common Issues

**Issue**: Tests fail with import errors
- **Fix**: Run `uv sync --all-packages --dev`

**Issue**: Graph hangs during test
- **Fix**: Check for infinite loops in routing functions

**Issue**: State not updating
- **Fix**: Ensure nodes return dict, not modified state

## Quick Reference

```bash
# Run tests
uv run pytest -q                  # All tests
uv run pytest -v                  # Verbose
uv run pytest -k "test_node"      # Match name
uv run pytest --cov               # With coverage

# Dev server
uv run langgraph dev              # Start server

# Validate Cast
uv run python scripts/validate_cast.py casts/my_cast
```

## Resources

### References
- `references/pytest_patterns.md` - Pytest patterns and best practices
- `references/studio_debugging.md` - LangGraph Studio debugging guide
- `references/logging_guide.md` - Logging best practices

### Templates
- `templates/unit_test.py` - Unit test template
- `templates/integration_test.py` - Integration test template
- `templates/test_fixtures.py` - Common test fixtures

### Scripts
- `scripts/run_tests.py` - Test runner with reporting

### Official Documentation
- Pytest: https://docs.pytest.org/
- LangGraph Testing: https://docs.langchain.com/oss/python/langgraph/testing
- LangGraph CLI: https://docs.langchain.com/oss/python/langgraph/cli
