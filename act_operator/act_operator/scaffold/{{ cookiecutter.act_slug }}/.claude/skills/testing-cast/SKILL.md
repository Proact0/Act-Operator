---
name: testing-cast
description: Pytest-based testing framework for LangGraph casts - patterns, fixtures, and test generation for nodes, graphs, and integrated systems
---

# Testing Cast Skill

You are a pytest expert specializing in LangGraph testing. Your role is to help developers write effective, maintainable tests for their Act Operator casts.

## Quick Start

### Generate Tests Automatically

```bash
# Generate node tests
python .claude/skills/testing-cast/scripts/generate_node_tests.py casts/my_cast/nodes.py

# Generate graph tests
python .claude/skills/testing-cast/scripts/generate_graph_tests.py my_cast

# Run tests
python .claude/skills/testing-cast/scripts/run_tests.py
```

### Manual Testing

**Test a node:**
```python
def test_my_node():
    from casts.my_cast.nodes import MyNode

    node = MyNode()
    result = node.execute({"input": "test"})

    assert "output" in result
```

**Test a graph:**
```python
def test_my_graph():
    from casts.my_cast.graph import MyGraph

    graph = MyGraph().build()
    result = graph.invoke({"input": "test"})

    assert result is not None
```

## Resource Map

### Core Testing (< 2k tokens each - read these first)

```
resources/core/
├── testing-nodes.md       # Unit tests for BaseNode/AsyncBaseNode classes
├── testing-graphs.md      # Integration tests for graphs
└── testing-state.md       # Testing state schemas and flow
```

**When to read:**
- **testing-nodes.md:** Testing individual node classes
- **testing-graphs.md:** Testing graph execution and routing
- **testing-state.md:** Testing state schemas, reducers, updates

### Advanced Testing (< 4k tokens each)

```
resources/advanced/
├── async-testing.md             # pytest-asyncio patterns
├── mocking-strategies.md        # Mock LLMs, tools, APIs, Store
├── fixtures-guide.md            # Reusable pytest fixtures
├── integration-testing.md       # End-to-end workflow tests
└── coverage-best-practices.md   # Coverage goals and strategies
```

**When to read:**
- **async-testing.md:** Testing AsyncBaseNode classes
- **mocking-strategies.md:** Need to mock LLMs, APIs, or dependencies
- **fixtures-guide.md:** Creating reusable test fixtures
- **integration-testing.md:** Testing complete workflows
- **coverage-best-practices.md:** Improving test coverage

## Common Testing Patterns

### Pattern 1: Test Node Execution
```python
class TestMyNode:
    def test_execute(self):
        node = MyNode()
        state = {"input": "test"}

        result = node.execute(state)

        assert "processed" in result
```

### Pattern 2: Test with Mocks
```python
def test_with_mock_llm(monkeypatch):
    class MockLLM:
        def invoke(self, messages):
            return {"content": "mocked"}

    node = LLMNode()
    monkeypatch.setattr(node, "llm", MockLLM())

    result = node.execute({"messages": []})
    assert result["response"]["content"] == "mocked"
```

### Pattern 3: Test Graph Flow
```python
def test_graph_routing():
    graph = MyGraph().build()

    result = graph.invoke({"input": "test", "condition": True})

    assert result["path_taken"] == "expected_path"
```

### Pattern 4: Test Async Nodes
```python
@pytest.mark.asyncio
async def test_async_node():
    node = AsyncNode()

    result = await node.execute({"query": "test"})

    assert "data" in result
```

## Quick Workflows

### Workflow 1: Test New Node

1. Write test first (TDD):
   ```python
   def test_new_node():
       node = NewNode()
       result = node.execute({"input": "test"})
       assert result["expected_field"] == "expected_value"
   ```

2. Run test (should fail):
   ```bash
   pytest tests/test_nodes.py::test_new_node -v
   ```

3. Implement node
4. Run test (should pass)

### Workflow 2: Test Existing Cast

1. Generate tests:
   ```bash
   python .claude/skills/testing-cast/scripts/generate_node_tests.py casts/my_cast/nodes.py
   python .claude/skills/testing-cast/scripts/generate_graph_tests.py my_cast
   ```

2. Customize generated tests with specifics
3. Run tests:
   ```bash
   pytest casts/my_cast/tests/ -v
   ```

### Workflow 3: Add Integration Tests

1. Create `tests/integration/test_my_workflow.py`
2. Use `integration-testing.md` patterns
3. Mark as integration:
   ```python
   @pytest.mark.integration
   def test_complete_workflow():
       ...
   ```

## Fixtures

Copy `fixtures/conftest.py` to your cast's `tests/` directory for reusable fixtures:

- `empty_state` - Empty state dict
- `populated_state` - Pre-filled state
- `mock_llm` - Mock LLM responses
- `mock_store` - Mock Store for memory tests
- `mock_runtime` - Mock Runtime with Store
- `memory_saver` - MemorySaver checkpointer

## Test Organization

```
casts/my_cast/
├── nodes.py
├── graph.py
├── state.py
└── tests/
    ├── conftest.py          # Cast-specific fixtures
    ├── test_nodes.py        # Node unit tests
    ├── test_graph.py        # Graph integration tests
    └── test_state.py        # State tests

tests/integration/           # Cross-cast integration tests
└── test_my_workflow.py
```

## Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/test_nodes.py

# Specific test
pytest tests/test_nodes.py::TestMyNode::test_execute

# With coverage
pytest --cov=casts --cov-report=html

# Only failed tests
pytest --lf

# Verbose
pytest -v

# Stop on first failure
pytest -x

# Using enhanced runner
python .claude/skills/testing-cast/scripts/run_tests.py -v
```

## pytest.ini Configuration

```ini
[tool.pytest.ini_options]
testpaths = ["tests", "casts/*/tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=casts --cov-report=term-missing"
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
asyncio_mode = "auto"
```

## Troubleshooting

**Tests not found:**
- Check test file names start with `test_`
- Check test functions start with `test_`
- Check test classes start with `Test`

**Import errors:**
- Ensure you're in project root
- Check Python path includes project
- Verify cast imports are correct

**Async tests fail:**
- Add `@pytest.mark.asyncio` decorator
- Install `pytest-asyncio`
- Set `asyncio_mode = "auto"` in pytest.ini

**Coverage too low:**
- See `coverage-best-practices.md`
- Focus on critical paths first
- Don't aim for 100%

## Best Practices

✅ **Do:**
- Test behavior, not implementation
- Use descriptive test names
- Arrange-Act-Assert pattern
- Mock external dependencies
- Test error paths
- Use fixtures for reusability

❌ **Don't:**
- Test private methods
- Depend on test execution order
- Use sleep() for timing
- Test library code
- Aim for 100% coverage blindly

## Integration with Other Skills

**From developing-cast:**
- Implementation is complete
- Tests validate behavior matches design

**To production:**
- Tests pass before deployment
- Coverage meets minimum threshold
- Integration tests validate workflows

---

**Remember:** Good tests document behavior, catch regressions, and enable confident refactoring. Make testing easy and valuable, not a chore.
