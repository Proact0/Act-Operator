---
name: testing-cast
description: Use when testing LangGraph casts after implementation - provides pytest patterns, fixtures, mocking strategies, and test generation scripts for unit tests (nodes), integration tests (graphs), and async testing with comprehensive coverage guidance
---

# Testing Cast

## Overview

Comprehensive pytest-based testing framework for LangGraph casts. Provides patterns, fixtures, mocking strategies, and executable scripts for testing nodes, graphs, state management, tools, and integrated systems.

**When to use:** After developing-cast has implemented components. Use this skill to write tests that validate behavior and catch regressions.

## Quick Start

**New to testing LangGraph?** → Read `resources/testing-philosophy.md` first

**Have implementation ready?** →
1. Use `scripts/generate_tests.py` to create test boilerplate
2. Add assertions using patterns from resources
3. Run tests with `pytest` or `scripts/run_tests.py`

**Debugging test failures?** → See Quick Troubleshooting below

## Resource Navigation

### 🧪 Core Testing Patterns (Frequently Accessed)

| Resource | When to Read | Tokens |
|----------|--------------|--------|
| `resources/node-testing.md` | Testing individual nodes (unit tests) | < 2k |
| `resources/graph-testing.md` | Testing complete graphs (integration) | < 2k |
| `resources/async-testing.md` | Testing async nodes and graphs | < 2k |
| `resources/mocking.md` | Mocking LLMs, APIs, Store, tools | < 2k |

### 📚 Advanced Testing

| Resource | When to Read | Tokens |
|----------|--------------|--------|
| `resources/state-testing.md` | Testing state updates and reducers | < 3k |
| `resources/fixtures-guide.md` | Creating and using fixtures | < 3k |
| `resources/coverage.md` | Coverage targets and meaningful tests | < 3k |

### 🛠️ Utilities

| Resource | When to Use |
|----------|-------------|
| `scripts/generate_tests.py` | Generate test boilerplate for nodes/graphs |
| `scripts/run_tests.py` | Enhanced test runner with markers |
| `fixtures/conftest.py` | Import reusable fixtures |
| `templates/*.j2` | Cookiecutter templates for tests |

## Testing Philosophy

**Test behavior, not implementation** - Tests should verify what code does, not how it does it.

**Fast tests encourage frequent running** - Use mocks to keep unit tests fast (< 1s each).

**Coverage is a means, not an end** - Aim for meaningful tests, not arbitrary percentages.

**Tests are documentation** - Well-written tests explain how code should behave.

## Test Organization

### Act Project Structure

```
casts/
  my_agent/
    tests/
      __init__.py
      conftest.py           # Cast-specific fixtures
      test_nodes.py         # Node unit tests
      test_graph.py         # Graph integration tests
      test_state.py         # State update tests
      test_integration.py   # E2E tests (optional)

tests/                      # Project-level tests
  integration/              # Cross-cast integration tests
  conftest.py               # Project-wide fixtures
```

### Test File Naming

- `test_*.py` or `*_test.py` - pytest discovers both
- One test file per component (e.g., `test_nodes.py` for all nodes)
- Group related tests in classes: `class TestProcessNode:`

## Quick Workflows

### Workflow 1: Testing New Node

```bash
# 1. Generate test boilerplate
python scripts/generate_tests.py --node ProcessNode --cast my_agent

# 2. Add assertions (see resources/node-testing.md)
# Edit casts/my_agent/tests/test_nodes.py

# 3. Run tests
pytest casts/my_agent/tests/test_nodes.py -v

# 4. Check coverage
pytest casts/my_agent/tests/test_nodes.py --cov=casts.my_agent.nodes
```

### Workflow 2: Testing Complete Graph

```bash
# 1. Generate test boilerplate
python scripts/generate_tests.py --graph MyAgentGraph --cast my_agent

# 2. Add test cases (see resources/graph-testing.md)
# Edit casts/my_agent/tests/test_graph.py

# 3. Run integration tests
pytest casts/my_agent/tests/test_graph.py -v

# 4. Test with markers
pytest -m "not slow" -v  # Skip slow tests
```

### Workflow 3: Debugging Test Failures

1. **Read error message** - pytest shows clear assertion failures
2. **Use -v flag** - See detailed test names
3. **Use --pdb** - Drop into debugger on failure: `pytest --pdb`
4. **Check mocks** - Verify mock setup in conftest.py
5. **See resources/troubleshooting.md** for common issues

## Quick Decision Flowchart

```
What are you testing?

├─ Individual node
│  → resources/node-testing.md
│  → Use mock LLM, mock dependencies
│  → Fast unit tests (< 1s each)
│
├─ Complete graph
│  → resources/graph-testing.md
│  → Use MemorySaver for checkpointer
│  → Integration tests (can be slower)
│
├─ Async node/graph
│  → resources/async-testing.md
│  → Use @pytest.mark.asyncio
│  → Use @pytest_asyncio.fixture
│
├─ State updates
│  → resources/state-testing.md
│  → Test reducers directly
│  → Test state flow through graph
│
├─ Tools
│  → resources/node-testing.md (tools section)
│  → Test tool functions directly
│  → Mock external APIs in tools
│
└─ Need to mock something?
   → resources/mocking.md
   → LLM, API, Store, database, file I/O
```

## pytest Essentials

### Running Tests

```bash
# All tests
pytest

# Specific file
pytest casts/my_agent/tests/test_nodes.py

# Specific test
pytest casts/my_agent/tests/test_nodes.py::test_process_node

# With coverage
pytest --cov=casts.my_agent --cov-report=term-missing

# Parallel execution
pytest -n auto  # Requires pytest-xdist

# Stop on first failure
pytest -x

# Failed tests only
pytest --lf  # Last failed

# Verbose output
pytest -v

# Quiet output
pytest -q
```

### pytest Markers

```python
# Mark slow tests
@pytest.mark.slow
def test_expensive_operation():
    pass

# Mark integration tests
@pytest.mark.integration
def test_full_workflow():
    pass

# Mark async tests
@pytest.mark.asyncio
async def test_async_node():
    pass

# Parametrize tests
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
])
def test_uppercase(input, expected):
    assert input.upper() == expected
```

**Run by marker:**
```bash
pytest -m "not slow"           # Skip slow tests
pytest -m integration          # Only integration tests
pytest -m "not integration"    # Only unit tests
```

## Common Testing Patterns

### Pattern: Test Node with Mock LLM

```python
from casts.my_agent.nodes import ProcessNode

def test_process_node(mock_llm):
    """Test ProcessNode with mocked LLM."""
    node = ProcessNode(mock_llm)
    state = {"messages": [], "task": "test"}

    result = node.execute(state)

    assert "messages" in result
    assert len(result["messages"]) == 1
```

### Pattern: Test Graph Execution

```python
from casts.my_agent.graph import MyAgentGraph
from langgraph.checkpoint.memory import MemorySaver

def test_graph_execution():
    """Test complete graph workflow."""
    graph = MyAgentGraph(checkpointer=MemorySaver()).build()

    result = graph.invoke({"messages": [], "task": "test"})

    assert result["status"] == "completed"
```

### Pattern: Test Async Node

```python
import pytest
from casts.my_agent.nodes import AsyncFetchNode

@pytest.mark.asyncio
async def test_async_fetch():
    """Test async node."""
    node = AsyncFetchNode()
    state = {"query": "test"}

    result = await node.execute(state)

    assert "data" in result
```

### Pattern: Test State Updates

```python
def test_state_reducer():
    """Test state reducer behavior."""
    from casts.my_agent.state import MyAgentState
    from operator import add

    # Test message accumulation
    state: MyAgentState = {"messages": [msg1]}
    update = {"messages": [msg2]}

    # Reducer should append
    result = add(state["messages"], update["messages"])
    assert len(result) == 2
```

## Fixtures Reference

### Built-in Fixtures (from fixtures/conftest.py)

```python
# Mock LLM
def test_with_mock_llm(mock_llm):
    # mock_llm returns AIMessage("Mock response")
    pass

# Mock LLM with tools
def test_with_tools(mock_llm_with_tools):
    # mock_llm_with_tools returns AIMessage with tool_calls
    pass

# Test graph
def test_with_graph(test_graph):
    # test_graph is compiled graph with MemorySaver
    pass

# Test config
def test_with_config(test_config):
    # test_config has thread_id="test-123"
    pass

# Mock Store
def test_with_store(mock_store):
    # mock_store is in-memory Store implementation
    pass
```

**See `resources/fixtures-guide.md` for creating custom fixtures**

## Quick Troubleshooting

### Issue: "TypeError: object dict can't be used in 'await' expression"

**Cause:** Async test without @pytest.mark.asyncio

**Fix:**
```python
@pytest.mark.asyncio  # Add this
async def test_async_function():
    result = await some_async_func()
```

### Issue: "fixture 'mock_llm' not found"

**Cause:** conftest.py not in correct location

**Fix:**
```bash
# Ensure conftest.py exists:
casts/my_agent/tests/conftest.py

# Or import from project-level:
# In your conftest.py:
pytest_plugins = ["fixtures.conftest"]
```

### Issue: Tests pass individually but fail together

**Cause:** Shared state between tests (fixture scope issue)

**Fix:**
```python
# Use function scope for isolation
@pytest.fixture(scope="function")  # Not "module" or "session"
def my_fixture():
    return clean_state()
```

### Issue: "State not updating in tests"

**Cause:** Forgetting reducers or not returning dict from execute()

**Fix:**
```python
# Ensure state has reducer
messages: Annotated[list, add]  # Will accumulate

# Ensure execute returns dict
def execute(self, state) -> dict:
    return {"messages": [new_msg]}  # Not None!
```

### Issue: Slow tests

**Cause:** Not using mocks, real API calls

**Fix:**
```python
# Mock expensive operations
@pytest.fixture
def mock_api(monkeypatch):
    def fake_api_call(*args, **kwargs):
        return {"data": "mock"}

    monkeypatch.setattr("module.api_call", fake_api_call)
    return fake_api_call

# Use in test
def test_fast(mock_api):
    # Uses fake_api_call, not real API
    pass
```

## Coverage Guidelines

### Target Coverage

- **Nodes:** 90%+ coverage (unit tests)
- **Graphs:** 80%+ coverage (integration tests)
- **Tools:** 90%+ coverage (unit tests)
- **Conditions:** 100% coverage (all branches)

**But:** Don't chase coverage - focus on meaningful tests.

### What to Test

✅ **DO test:**
- Business logic in nodes
- Edge routing conditions
- State update behavior
- Error handling paths
- Tool execution

❌ **DON'T test:**
- Framework code (LangGraph internals)
- Third-party libraries
- Trivial getters/setters
- Generated code

### Coverage Commands

```bash
# Generate coverage report
pytest --cov=casts.my_agent --cov-report=html

# View in browser
open htmlcov/index.html

# Terminal report with missing lines
pytest --cov=casts.my_agent --cov-report=term-missing

# Fail if coverage below threshold
pytest --cov=casts.my_agent --cov-fail-under=80
```

## Integration with Other Skills

### Before This Skill

1. **architecting-act** - Created CLAUDE.md with architecture
2. **engineering-act** - Set up project structure
3. **developing-cast** - Implemented nodes, graphs, tools

### During This Skill

- Reference CLAUDE.md for expected behavior
- Use implementation from developing-cast
- Validate architecture decisions with tests

### Testing validates:

- State schema works as designed
- Nodes behave as specified in CLAUDE.md
- Edges route correctly based on architecture
- Tools integrate properly
- Error handling works

## Common Mistakes

### ❌ Not Using Mocks

```python
# BAD: Real API calls in unit tests
def test_node():
    node = ProcessNode(ChatAnthropic())  # Real LLM!
    result = node.execute(state)
```

**Fix:** Use mock_llm fixture

### ❌ Testing Implementation Details

```python
# BAD: Testing internal variable names
def test_node():
    node = ProcessNode()
    node.execute(state)
    assert node._internal_counter == 5  # Implementation detail
```

**Fix:** Test behavior, not internals

### ❌ No Assertions

```python
# BAD: Test runs but doesn't verify anything
def test_node():
    node = ProcessNode()
    node.execute(state)  # No assert!
```

**Fix:** Always assert expected behavior

### ❌ Forgetting Async Marker

```python
# BAD: Async test without marker
async def test_async():  # Will fail
    await async_func()
```

**Fix:** Add @pytest.mark.asyncio

### ❌ Hardcoded Values

```python
# BAD: Hardcoded test data
def test_node():
    result = node.execute({"messages": [HumanMessage("test")]})
    assert result["messages"][0].content == "Specific LLM response"  # Fragile!
```

**Fix:** Test structure, not exact content

## Act Project Conventions

⚠️ **Test organization:**
- Tests in: `casts/[cast_name]/tests/`
- One conftest.py per cast
- Import project fixtures: `pytest_plugins = ["fixtures.conftest"]`

⚠️ **Naming:**
- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`

⚠️ **Fixtures:**
- Cast-specific: `casts/[cast_name]/tests/conftest.py`
- Project-wide: `fixtures/conftest.py`
- Always use function scope unless performance critical

## Resources Index

**Core patterns:**
- `resources/node-testing.md` - Node unit tests
- `resources/graph-testing.md` - Graph integration tests
- `resources/async-testing.md` - Async testing
- `resources/mocking.md` - Mocking strategies

**Advanced:**
- `resources/state-testing.md` - State and reducers
- `resources/fixtures-guide.md` - Fixture patterns
- `resources/coverage.md` - Coverage and quality

**Utilities:**
- `scripts/generate_tests.py` - Generate test boilerplate
- `scripts/run_tests.py` - Enhanced test runner
- `fixtures/conftest.py` - Reusable fixtures
- `templates/*.j2` - Test templates

**Philosophy:**
- `resources/testing-philosophy.md` - Testing principles

---

**Remember:** Good tests make refactoring safe. Write tests that verify behavior, not implementation. Use mocks to keep tests fast. Aim for meaningful coverage, not arbitrary percentages.
