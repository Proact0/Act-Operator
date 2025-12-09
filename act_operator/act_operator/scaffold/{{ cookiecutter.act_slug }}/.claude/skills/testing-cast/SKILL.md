---
name: testing-cast
description: Use when writing pytest for cast nodes or casts(graphs), need mocking strategies for LLM/API/Store calls, setting up test fixtures, or organizing sync/async test suites - provides comprehensive patterns for effective cast verification
---

# Testing Cast Skill

Write effective pytest tests for {{ cookiecutter.act_name }} Act's casts.

## When NOT to Use

- Writing implementation → `developing-cast`
- Designing architectures → `architecting-act`
- Project setup → `engineering-act`

## Quick Reference

```bash
# Run tests
uv run pytest                              # All tests
uv run pytest tests/test_nodes.py          # Specific file
uv run pytest -k "test_my_function"        # Match name
uv run pytest -v                           # Verbose
uv run pytest -x                           # Stop on first failure
uv run pytest --lf                         # Last failed only

# With coverage
uv run pytest --cov=casts --cov-report=html
```

## Resources

| Task | Resource |
|------|----------|
| Test nodes (sync/async) | `resources/testing-nodes.md` |
| Test graphs | `resources/testing-graphs.md` |
| Mock LLMs, APIs, Store | `resources/mocking.md` |
| Reusable fixtures | `resources/fixtures.md` |
| Coverage strategies | `resources/coverage.md` |

## Test Patterns

### Node Test
```python
class TestMyNode:
    def test_execute(self):
        node = MyNode()
        result = node.execute({"input": "test"})
        assert "output" in result
```

### Async Node Test
```python
@pytest.mark.asyncio
async def test_async_node():
    node = AsyncNode()
    result = await node.execute({"query": "test"})
    assert "data" in result
```

### Graph Test
```python
def test_graph_invoke(graph):
    result = graph.invoke({"input": "test"})
    assert result is not None
```

### Mock LLM
```python
def test_with_mock(monkeypatch):
    class MockLLM:
        def invoke(self, messages):
            return {"content": "mocked"}
    
    node = LLMNode()
    monkeypatch.setattr(node, "llm", MockLLM())
    result = node.execute({"messages": []})
```

## Test Organization

```
casts/{cast_name}/
└── tests/
    ├── conftest.py      # Fixtures
    ├── test_nodes.py    # Node tests
    └── test_graph.py    # Graph tests
```

## Best Practices

**DO:**
- Test behavior, not implementation
- Use descriptive names
- Arrange-Act-Assert pattern
- Mock external dependencies
- Test error paths

**DON'T:**
- Test private methods
- Order-dependent tests
- Use `sleep()` for timing
- Aim for 100% coverage
