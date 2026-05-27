---
name: testing-cast
description: Guides pytest test writing for LangGraph casts with mocking patterns for LLM/API/Store calls. Use when writing tests, need mock strategies, setting up fixtures, testing nodes/graphs (v3 event streaming, timeouts, error handlers, graceful shutdown), or ask "write tests", "mock LLM", "test coverage".
version: "2026.05.26"
author: Proact0
allowed-tools:
  - Bash(uv run pytest *)
  - Read
  - Write
  - Edit
  - AskUserQuestion
---

# Testing Cast Skill

Write effective pytest tests for {{ cookiecutter.act_name }} Act's casts.

## When NOT to Use

- Writing implementation → `developing-cast`
- Designing architectures → `architecting-act`
- Project / cast scaffolding → run `uv run act new` (project) or `uv run act cast` (new cast) directly

## Quick Reference

```bash
# Run tests
uv run pytest                              # All tests
uv run pytest tests/node_tests/            # All node tests
uv run pytest tests/cast_tests/            # All cast (graph) tests
uv run pytest -k "test_my_function"        # Match name
uv run pytest -v                           # Verbose
uv run pytest -x                           # Stop on first failure
uv run pytest --lf                         # Last failed only

# With coverage
uv run pytest --cov=casts --cov-report=html
```

## Test Organization

The scaffold places tests at the **project root** under `tests/`, organized by scope:

```
{{ cookiecutter.act_slug }}/
├── casts/
│   └── {{ cookiecutter.cast_snake }}/        # cast implementation
└── tests/
    ├── conftest.py                            # shared fixtures (create as needed)
    ├── cast_tests/
    │   └── {{ cookiecutter.cast_snake }}_test.py    # graph-level tests (suffix: *_test.py)
    └── node_tests/
        └── test_node.py                       # node tests for the initial cast (prefix: test_*.py)
```

| Location | Naming | Scope |
|----------|--------|-------|
| `tests/cast_tests/{cast_snake}_test.py` | `<cast_snake>_test.py` **suffix** | Whole-graph invocation tests; `act cast` auto-creates one per cast |
| `tests/node_tests/test_<something>.py` | `test_*.py` **prefix** | Per-node behavior tests |
| `tests/conftest.py` | fixed | Shared fixtures across `cast_tests/` and `node_tests/` |

> The `{cast_snake}_test.py` suffix naming for cast tests is what `act cast` generates — do not rename to `test_<cast>.py`.

## Resources

| Use when | Resource |
|----------|----------|
| testing sync/async nodes, drain-aware nodes | [testing-nodes.md](./resources/testing-nodes.md) |
| testing graphs (invoke, routing, streaming v3, timeouts, error handlers, graceful shutdown) | [testing-graphs.md](./resources/testing-graphs.md) |
| mocking LLM / API / Store calls | [mocking.md](./resources/mocking.md) |
| reusable fixtures (graph, mock model, mock store) | [fixtures.md](./resources/fixtures.md) |
| coverage targeting and reporting | [coverage.md](./resources/coverage.md) |

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
